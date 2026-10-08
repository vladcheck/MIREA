"""Bit-level I2C bus simulator (100 kHz) с моделями 24LC64 и DS1307.

Чистый Python stdlib. Моделирует открытый сток, подтяжки, тайм-ауты
ведущего, внутренний цикл записи EEPROM и ACK polling — в точности те
транзакции, которые выполняет pr3-4/src/main_variant4.c (вариант 4).

Время в микросекундах, период SCL = 10 мкс (fSCL = 100 кГц).
"""

# ---------------------------------------------------------------------------
# Константы варианта 4 (табл. 9.9) и настройки I2C1 STM32F103C8
# ---------------------------------------------------------------------------
EEPROM_CELL = 0x003F
EEPROM_TEST_VALUE = 0x67
DS1307_TEST_REG = 0x00

EEPROM_ADDR_7BIT = 0x50  # A2:A0 = 000
DS1307_ADDR_7BIT = 0x68

T_HALF_PERIOD_US = 5.0  # 100 кГц: полупериод 5 мкс
T_CLOCK_LOW_US = 5.0
T_CLOCK_HIGH_US = 5.0
MASTER_TIMEOUT_BITS = 2000  # тайм-аут ведущего (~20 мс)
EEPROM_T_WRITE_US = 5000.0  # внутренний цикл записи 24LC64 (до 5 мс)

ACK, NACK = True, False


class I2CTimeout(Exception):
    """Ведущий не дождался условия на шине (нет ACK / линия застряла)."""


class I2CShortPullup(Exception):
    """Линия SDA не поднялась — подтяжка отключена."""


class Bus:
    """Двухпроводная шина с открытым стоком и опциональной подтяжкой."""

    def __init__(self, pullups=True):
        self.pullups = pullups
        self.t = 0.0
        # Линии: уровень вычисляется из драйверов (открытый сток).
        self._sda_master_low = False
        self._sda_dev_low = False  # ведомое тянет SDA вниз
        self.scl = 1
        self.devices = []
        # Журнал образцов для осциллограммы: (t_us, sda, scl).
        self.samples = []
        # Границы байт для подписей: (t_start, t_end, метка, ack).
        self.byte_spans = []
        # Журнал ACK/NACK: (t_us, метка, ack).
        self.ack_log = []
        # Маркеры условий START/STOP для осциллограммы: (t_us, вид).
        self.markers = []
        # Текущая транзакция (для JSON-отчёта).
        self.current = None
        self.transactions = []
        # Состояние протокола: ожидаем адресный байт / активное ведомое.
        self._in_addr = True
        self._active = None

    # -- уровни линий -------------------------------------------------------
    def sda_level(self):
        if self._sda_master_low or self._sda_dev_low:
            return 0
        if not self.pullups:
            return 0  # без подтяжки линия не поднимается (застревает)
        return 1

    def _sample(self):
        self.samples.append((self.t, self.sda_level(), self.scl))

    def _set_sda_master(self, low):
        self._sda_master_low = low
        self._sample()

    def _set_scl(self, level):
        self.scl = level
        self._sample()

    def _delay(self, us):
        self.t += us

    # -- низкоуровневые примитивы (только ведущий двигает SCL) --------------
    def start_condition(self, marker="START"):
        """START: SDA 1->0 при SCL=1. Проверяет, что подтяжка работает."""
        # После любого START следующий байт — адресный.
        self._in_addr = True
        self._active = None
        # Проверка отпускания линии (диагностика отключённой подтяжки).
        self._sda_master_low = False
        self._delay(T_HALF_PERIOD_US)
        self._sample()
        if self.sda_level() != 1:
            # Линия застряла в 0 — подтяжка отключена, START невозможен.
            raise I2CShortPullup("SDA не поднялась: подтяжка отключена")
        self._sda_master_low = True
        self._delay(T_HALF_PERIOD_US)
        self._sample()
        self.markers.append((self.t, marker))
        self._set_scl(0)

    def repeated_start_condition(self):
        self._sda_master_low = False
        self._delay(T_HALF_PERIOD_US)
        self._sample()
        self._set_scl(1)
        self._delay(T_HALF_PERIOD_US)
        self.start_condition(marker="REP START")

    def stop_condition(self):
        self._sda_master_low = True
        self._delay(T_HALF_PERIOD_US)
        self._sample()
        self._set_scl(1)
        self._delay(T_HALF_PERIOD_US)
        self._sda_master_low = False
        self._delay(T_HALF_PERIOD_US)
        self._sample()
        self.markers.append((self.t, "STOP"))
        self._idle_bus()

    def _idle_bus(self):
        self._active = None
        self._in_addr = True
        for dev in self.devices:
            dev.on_stop(self)

    # -- передача/приём байтов ----------------------------------------------
    def write_byte(self, value, label=""):
        """Мастер передаёт байт; возвращает ACK (True) или NACK (False)."""
        value &= 0xFF
        t0 = self.t
        for bit in range(7, -1, -1):
            # Данные выставляются при SCL=0.
            self._sda_master_low = not ((value >> bit) & 1)
            self._delay(T_CLOCK_LOW_US / 2)
            self._sample()
            self._set_scl(1)
            self._delay(T_CLOCK_HIGH_US)
            self._set_scl(0)
            self._delay(T_CLOCK_LOW_US / 2)
        # Девятый такт: чтение ACK от ведомого.
        self._sda_master_low = False  # мастер отпускает SDA
        self._delay(T_CLOCK_LOW_US / 2)
        self._sample()
        if self._in_addr:
            addr7 = value >> 1
            rw = value & 1
            dev = self._find_device(addr7)
            if dev is not None:
                self._sda_dev_low = True  # ведомое тянет SDA (ACK)
                ack = True
                self._active = dev
                dev.on_addressed(rw, self)
            else:
                ack = False
            self._in_addr = False
        elif self._active is not None:
            ack = self._active.write_byte(value, self)
            self._sda_dev_low = ack  # ACK = низкий уровень девятого такта
        else:
            ack = False
        self._set_scl(1)
        self._delay(T_CLOCK_HIGH_US)
        self._set_scl(0)
        self._delay(T_CLOCK_LOW_US / 2)
        self._sda_dev_low = False  # ведомое отпускает линию
        self._sample()
        self.ack_log.append((t0, label or f"0x{value:02X}", ack))
        self.byte_spans.append((t0, self.t, label or f"0x{value:02X}", ack))
        return ack

    def read_byte(self, master_ack, label=""):
        """Мастер принимает байт; master_ack=True -> мастер отвечает ACK."""
        t0 = self.t
        value = 0
        for bit in range(7, -1, -1):
            self._sda_master_low = False
            # Ведомое выставляет очередной бит данных на SDA.
            if self._active is not None and self._active.reading:
                self._sda_dev_low = not self._active.serve_bit(self)
            self._delay(T_CLOCK_LOW_US)
            self._sample()
            self._set_scl(1)
            self._delay(T_CLOCK_HIGH_US / 2)
            level = self.sda_level()
            value |= (level & 1) << bit
            self._delay(T_CLOCK_HIGH_US / 2)
            self._set_scl(0)
        self._sda_dev_low = False
        self._sda_master_low = not master_ack
        self._delay(T_CLOCK_LOW_US / 2)
        self._sample()
        self._set_scl(1)
        self._delay(T_CLOCK_HIGH_US)
        self._set_scl(0)
        self._delay(T_CLOCK_LOW_US / 2)
        self._sda_master_low = False
        self._sample()
        self.ack_log.append((t0, label or f"read 0x{value:02X}", master_ack))
        self.byte_spans.append((t0, self.t, label or f"0x{value:02X}", master_ack))
        return value

    def _find_device(self, addr7):
        for dev in self.devices:
            if dev.address_7bit == addr7 and dev.responsive(self.t):
                return dev
        return None

    def idle(self, us, label=""):
        """Пауза на шине (например, внутренний цикл записи EEPROM)."""
        self.t += us
        self._sample()


# ---------------------------------------------------------------------------
# Ведомые устройства
# ---------------------------------------------------------------------------
class EEPROM24LC64:
    """24LC64: 8192 байта, страница 32 байта, цикл записи до 5 мс (NACK)."""

    def __init__(self, a012=0, wp=False, t_write_us=EEPROM_T_WRITE_US):
        assert 0 <= a012 <= 7
        self.address_7bit = 0x50 | a012
        self.wp = wp
        self.t_write = t_write_us
        self.mem = bytearray(0x2000)
        self.ptr = 0
        self.state = "idle"
        self.reading = False
        self._pending = None
        self._busy_until = 0.0

    def responsive(self, t):
        self._commit(t)
        return t >= self._busy_until

    def _commit(self, t):
        if self._pending is not None and t >= self._busy_until:
            addr, data = self._pending
            if not self.wp:
                self.mem[addr] = data
            self._pending = None

    def on_addressed(self, rw, bus):
        self.state = "addr_hi"
        self.reading = rw == 1
        self._tx = None
        self._tx_bits = 0

    def serve_bit(self, bus):
        """Ведомое выдаёт очередной бит текущего байта чтения."""
        if self._tx is None or self._tx_bits >= 8:
            self._tx = self.read_byte(bus)
            self._tx_bits = 0
        bit = (self._tx >> (7 - self._tx_bits)) & 1
        self._tx_bits += 1
        return bit

    def write_byte(self, value, bus):
        if self.state == "addr_hi":
            self.ptr = (value & 0x1F) << 8
            self.state = "addr_lo"
        elif self.state == "addr_lo":
            self.ptr = (self.ptr | value) & 0x1FFF
            self.state = "data"
        elif self.state == "data":
            if self._pending is None:
                self._pending = (self.ptr, value)
            self.ptr = (self.ptr + 1) & 0x1FFF
        return True

    def read_byte(self, bus):
        self._commit(bus.t)
        value = self.mem[self.ptr]
        self.ptr = (self.ptr + 1) & 0x1FFF
        return value

    def on_stop(self, bus):
        if self._pending is not None and self.state != "idle":
            self._busy_until = bus.t + self.t_write
        self.state = "idle"
        self.reading = False


class DS1307:
    """DS1307: 64 регистра, время в BCD, бит CH в регистре 0x00."""

    def __init__(self):
        self.address_7bit = DS1307_ADDR_7BIT
        self.regs = bytearray(0x40)
        self.regs[0x00] = 0x80  # CH=1 — генератор остановлен при подаче питания
        self.reg = 0
        self.state = "idle"
        self.reading = False

    def responsive(self, t):
        return True

    def on_addressed(self, rw, bus):
        self.state = "reg"
        self.reading = rw == 1
        self._tx = None
        self._tx_bits = 0

    def serve_bit(self, bus):
        if self._tx is None or self._tx_bits >= 8:
            self._tx = self.read_byte(bus)
            self._tx_bits = 0
        bit = (self._tx >> (7 - self._tx_bits)) & 1
        self._tx_bits += 1
        return bit

    def write_byte(self, value, bus):
        if self.state == "reg":
            self.reg = value & 0x3F
            self.state = "data"
        else:
            self.regs[self.reg] = value
            self.reg = (self.reg + 1) & 0x3F
        return True

    def read_byte(self, bus):
        value = self.regs[self.reg]
        self.reg = (self.reg + 1) & 0x3F
        return value

    def on_stop(self, bus):
        self.state = "idle"
        self.reading = False


# ---------------------------------------------------------------------------
# Ведущий: те же вызовы, что и в pr3-4/src/main_variant4.c
# ---------------------------------------------------------------------------
class I2CMaster:
    """Повторяет логику main_variant4.c: EEPROM_WriteByte (с ACK polling),
    EEPROM_ReadByte (random read), DS1307_SetTime, DS1307_ReadReg."""

    def __init__(self, bus, eeprom_addr=EEPROM_ADDR_7BIT, ds1307_addr=DS1307_ADDR_7BIT):
        self.bus = bus
        self.eeprom_addr = eeprom_addr
        self.ds1307_addr = ds1307_addr
        self.led = 0

    # -- примитивы из main_variant4.c ---------------------------------------
    def start_write(self, address):
        """I2C1_StartWrite: START + SLA+W, ожидание ADDR (иначе тайм-аут)."""
        self.bus.start_condition()
        return self.bus.write_byte(
            (address << 1) & 0xFE, f"SLA+W 0x{(address << 1) & 0xFE:02X}"
        )

    def read_one_byte(self, address):
        """I2C1_ReadOneByte: START + SLA+R, чтение одного байта с NACK."""
        self.bus.start_condition()
        ack = self.bus.write_byte(
            (address << 1) | 1, f"SLA+R 0x{((address << 1) | 1):02X}"
        )
        if not ack:
            raise I2CTimeout("Нет ACK на SLA+R")
        data = self.bus.read_byte(master_ack=False, label="DATA")
        return data

    # -- EEPROM --------------------------------------------------------------
    def eeprom_wait_ready(self, max_attempts=1000):
        """EEPROM_WaitReady: ACK polling — повторные START+0xA0 до ACK."""
        for attempt in range(max_attempts):
            self.bus.start_condition()
            ack = self.bus.write_byte(
                self.eeprom_addr << 1, f"ACK poll 0x{self.eeprom_addr << 1:02X}"
            )
            self.bus.stop_condition()
            if ack:
                return True
            # EEPROM занята внутренним циклом записи — NACK.
        return False

    def eeprom_write_byte(self, mem, data):
        """EEPROM_WriteByte: запись байта + ACK polling (как в main_variant4.c)."""
        if not self.start_write(self.eeprom_addr):
            raise I2CTimeout("Нет ACK на SLA+W при записи EEPROM")
        self.bus.write_byte((mem >> 8) & 0xFF, "addr hi")
        self.bus.write_byte(mem & 0xFF, "addr lo")
        self.bus.write_byte(data, f"data 0x{data:02X}")
        self.bus.stop_condition()  # здесь начинается внутренний цикл записи
        return self.eeprom_wait_ready()  # ACK polling

    def eeprom_read_byte(self, mem):
        """EEPROM_ReadByte: установка адреса (фаза записи), затем random read."""
        if not self.start_write(self.eeprom_addr):
            raise I2CTimeout("Нет ACK на SLA+W при чтении EEPROM")
        self.bus.write_byte((mem >> 8) & 0xFF, "addr hi")
        self.bus.write_byte(mem & 0xFF, "addr lo")
        self.bus.repeated_start_condition()
        data = self.read_one_byte(self.eeprom_addr)
        self.bus.stop_condition()
        return data

    # -- DS1307 ---------------------------------------------------------------
    def ds1307_write_bytes(self, reg, data):
        """DS1307_WriteBytes: START 0xD0, регистр, данные, STOP."""
        if not self.start_write(self.ds1307_addr):
            raise I2CTimeout("Нет ACK на SLA+W (DS1307)")
        self.bus.write_byte(reg, "reg 0x00")
        for b in data:
            self.bus.write_byte(b, f"0x{b:02X}")
        self.bus.stop_condition()
        return True

    def ds1307_set_time(self, h, m, s):
        """DS1307_SetTime(12,34,00): BCD, CH=0, 24-часовой режим."""
        raw = [
            self._dec_to_bcd(s) & 0x7F,
            self._dec_to_bcd(m),
            self._dec_to_bcd(h) & 0x3F,
        ]
        return self.ds1307_write_bytes(0x00, raw)

    def ds1307_read_reg(self, reg):
        """DS1307_ReadReg: фаза записи адреса регистра, repeated START, чтение."""
        if not self.start_write(self.ds1307_addr):
            raise I2CTimeout("Нет ACK на SLA+W (DS1307)")
        self.bus.write_byte(reg, "reg 0x00")
        self.bus.repeated_start_condition()
        data = self.read_one_byte(self.ds1307_addr)
        self.bus.stop_condition()
        return data

    @staticmethod
    def _dec_to_bcd(v):
        return ((v // 10) << 4) | (v % 10)

    @staticmethod
    def decode_reg(reg, raw):
        """DS1307_DecodeReg: маскирование служебных битов + BCD->dec."""
        if reg in (0x00, 0x01):
            raw &= 0x7F
        if reg == 0x02:
            raw &= 0x3F
        return 10 * ((raw >> 4) & 0x0F) + (raw & 0x0F)
