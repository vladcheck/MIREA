"""Реестровая модель таймера TIM2 микроконтроллера STM32F103C8 (ПР №5-6).

Модель повторяет конфигурацию и последовательность pr5-6/src/main_variant4.c
(индивидуальный вариант 4, Timing values из PLAN.md):
  1. базовая часть 250 мс   — PSC = 7999, ARR = 249;
  2. T1 = 80 мс             — ARR = 79  (меняется только ARR);
  3. T2 = 40 мс             — ARR = 39  (меняется только ARR);
  4. диагностика ARR+100    — ARR = 139 -> интервал 140 мс (×3,5 от T2,
     отклонение 250 %), после возврата ARR = 39 интервал 40 мс подтверждается;
  5. возврат T2             — ARR = 39.

Тактирование: HSI 8 МГц, APB1 делитель 1 -> PCLK1 = TIM2CLK = 8 МГц.
PSC = 7999 -> fCNT = 1 кГц: один отсчёт CNT = 1 мс, ARR = Tмс - 1.
PA1 — обычный двухтактный выход GPIO: в TIM2_IRQHandler состояние
инвертируется, поэтому расстояние между соседними фронтами равно интервалу
таймера, а полный период меандра — двум интервалам.

Семантика регистров (RM0008):
  * PSC и ARR пишутся в регистры предзагрузки; рабочие регистры обновляются
    только при событии обновления (запись EGR.UG или переполнение CNT) —
    запись ARR посреди интервала не меняет текущий интервал;
  * EGR.UG формирует событие обновления немедленно: загрузка PSC/ARR,
    CNT = 0, UIF = 1;
  * SR.UIF — семантика rc_w0: очищается записью 0, запись 1 не меняет бит;
  * прерывание берётся только при DIER.UIE = 1 И разрешённой линии TIM2_IRQn
    в NVIC; иначе UIF просто остаётся установленным, а PA1 не переключается
    (диагностика «нет фронтов»).

Время в модели — целое число тактов TIM2CLK, событийная дискретизация по
отсчётам CNT (без wall-clock циклов и без искусственного дрожания): при
PSC = 7999 один отсчёт = ровно 1 мс, поэтому измеренные интервалы точны,
а δT = |Tзам - Tзад| / Tзад * 100 % равен ровно 0.
"""

# ---------------------------------------------------------------------------
# Константы: тактирование и базовые настройки временной базы
# ---------------------------------------------------------------------------
TIM2CLK_HZ = 8_000_000  # HSI 8 МГц, делитель APB1 = 1 -> PCLK1 = TIM2CLK
PSC_DEFAULT = 7999  # 8 МГц / 8000 = 1 кГц: один отсчёт CNT = 1 мс

# Индивидуальный вариант 4 (табл. 9.9)
BASE_MS = 250  # обязательная базовая часть
T1_MS = 80  # первый интервал варианта
T2_MS = 40  # второй интервал варианта
DIAG_ARR_OFFSET = 100  # диагностическое изменение: ARR + 100
EVENTS_PER_PHASE = 8  # событий обновления на фазу -> 7-8 фронт-фронт интервалов

# Биты регистров
CEN = 0x0001  # CR1.CEN — запуск счётчика
UIE = 0x0001  # DIER.UIE — разрешение прерывания обновления
UIF = 0x0001  # SR.UIF — флаг обновления (rc_w0)
UG = 0x0001  # EGR.UG — программное событие обновления
TIM2_IRQn = 28  # номер линии прерывания TIM2 в NVIC (STM32F103)

GPIO_ODR1 = 0x0002  # ODR бит PA1
MAX_TICKS = 5_000_000  # защита от зацикливания в помощниках прогона


class NVIC:
    """Контроллер прерываний: разрешённые линии (здесь — только TIM2_IRQn)."""

    def __init__(self):
        self.enabled = set()

    def enable(self, line):
        self.enabled.add(line)

    def disable(self, line):
        self.enabled.discard(line)

    def is_enabled(self, line):
        return line in self.enabled


class GPIOA:
    """Порт A: PA1 — двухтактный выход, инвертируется в TIM2_IRQHandler.

    edges — журнал фронтов: dict(t_ms, level, arr), где arr — рабочий ARR,
    управлявший интервалом, закончившимся данным фронтом.
    """

    def __init__(self):
        self.odr = 0  # BSRR = BR1 при инициализации: PA1 = 0
        self.edges = []

    def toggle(self):
        self.odr ^= GPIO_ODR1
        return 1 if self.odr & GPIO_ODR1 else 0


class TIM2:
    """Таймер TIM2 с предзагрузкой PSC/ARR и семантикой rc_w0 у SR."""

    def __init__(self, mcu):
        self.mcu = mcu
        self.CR1 = 0  # CEN
        self.DIER = 0  # UIE
        self.CNT = 0
        self._psc = 0  # регистр предзагрузки PSC
        self._arr = 0  # регистр предзагрузки ARR
        self._psc_active = 0  # рабочий (загруженный) PSC
        self._arr_active = 0  # рабочий (загруженный) ARR
        self._sr = 0
        self._egr = 0

    # -- регистры с описанной семантикой ----------------------------------
    @property
    def PSC(self):
        return self._psc

    @PSC.setter
    def PSC(self, value):
        self._psc = value & 0xFFFF  # только предзагрузка

    @property
    def ARR(self):
        return self._arr

    @ARR.setter
    def ARR(self, value):
        self._arr = value & 0xFFFF  # только предзагрузка

    @property
    def arr_active(self):
        """Рабочий ARR, по которому сейчас сравнивается CNT."""
        return self._arr_active

    @property
    def psc_active(self):
        """Рабочий PSC, делющий частоту таймера."""
        return self._psc_active

    @property
    def SR(self):
        return self._sr

    @SR.setter
    def SR(self, value):
        self._sr &= value & 0xFFFF  # rc_w0: запись 0 очищает, запись 1 не меняет

    @property
    def EGR(self):
        return self._egr

    @EGR.setter
    def EGR(self, value):
        self._egr = value & 0xFF
        if value & UG:
            self.update_event()  # UG формирует событие обновления немедленно

    # -- командные записи --------------------------------------------------
    # write_* — алиасы для соответствия вызовам прошивки (семантика — в свойствах выше).
    def write_psc(self, value):
        self.PSC = value

    def write_arr(self, value):
        self.ARR = value

    def write_cr1(self, value):
        self.CR1 = value & 0xFFFF

    def write_dier(self, value):
        self.DIER = value & 0xFFFF

    def write_egr(self, value):
        self.EGR = value

    def write_sr(self, value):
        self.SR = value

    # -- событие обновления ------------------------------------------------
    def update_event(self):
        """Событие обновления: загрузка PSC/ARR, CNT = 0, UIF = 1, IRQ."""
        governed_arr = self._arr_active  # ARR, управлявший закончившимся интервалом
        self._psc_active = self._psc  # предзагрузка -> рабочий регистр
        self._arr_active = self._arr
        self.CNT = 0
        self._sr |= UIF
        self.mcu.on_update(governed_arr)

    def tick(self):
        """Один отсчёт CNT: время растёт на (PSC_active + 1) тактов TIM2CLK."""
        self.mcu.now_cycles += self._psc_active + 1
        if not (self.CR1 & CEN):
            return  # счётчик остановлен (CEN = 0)
        self.CNT += 1
        if self.CNT > self._arr_active:
            self.update_event()  # переполнение: 0..ARR -> ARR+1 отсчётов


class MCU:
    """Микроконтроллер: TIM2 + NVIC + GPIOA + диспетчер модельного времени."""

    def __init__(self):
        self.now_cycles = 0  # модельное время в тактах TIM2CLK
        self.nvic = NVIC()
        self.gpioa = GPIOA()
        self.tim2 = TIM2(self)
        self.update_events = 0  # всего событий обновления (включая UG)
        self.update_count = 0  # выполненные обработчики (g_update_count)

    @property
    def t_ms(self):
        """Текущее модельное время, мс (точно: целые такты / 8000)."""
        return self.now_cycles * 1000.0 / TIM2CLK_HZ

    def step(self):
        """Один шаг симуляции — один отсчёт CNT (или пауза, если CEN = 0)."""
        self.tim2.tick()

    def on_update(self, governed_arr):
        """Событие обновления: диспетчеризация прерывания TIM2_IRQn."""
        self.update_events += 1
        tim = self.tim2
        # Прерывание берётся только при UIE = 1 И разрешённой линии NVIC.
        if not (tim.DIER & UIE):
            return
        if not self.nvic.is_enabled(TIM2_IRQn):
            return
        if not (tim.SR & UIF):
            return
        # TIM2_IRQHandler: очистка UIF (rc_w0), инверсия PA1, счётчик событий.
        tim.SR = ~UIF & 0xFFFF
        level = self.gpioa.toggle()
        self.gpioa.edges.append(
            {"t_ms": self.t_ms, "level": level, "arr": governed_arr}
        )
        self.update_count += 1


def interval_init(mcu, interval_ms, psc=PSC_DEFAULT, ui=True, nvic=True):
    """Повторяет TIM2_IntervalInit() из src/main_variant4.c.

    Порядок как в прошивке: CR1/DIER в 0, запись PSC и ARR (предзагрузка),
    CNT = 0, событие обновления EGR.UG (загрузка рабочих регистров, CNT = 0,
    UIF = 1), очистка UIF, разрешение UIE и линии NVIC, запуск CEN.
    """
    if interval_ms <= 0 or interval_ms > 65536:
        raise ValueError(f"интервал {interval_ms} мс вне диапазона 1..65536")
    tim = mcu.tim2
    tim.write_cr1(0)
    tim.write_dier(0)
    tim.write_psc(psc)
    tim.write_arr(interval_ms - 1)
    tim.CNT = 0
    tim.write_egr(UG)  # событие обновления немедленно
    tim.write_sr(0x0000)  # очистка UIF после UG (rc_w0)
    if ui:
        tim.write_dier(UIE)
    if nvic:
        mcu.nvic.enable(TIM2_IRQn)
    else:
        mcu.nvic.disable(TIM2_IRQn)
    # Сбрасываем и журналы/счётчики: повторная инициализация используемого
    # MCU не должна смешивать фазы в журнале фронтов и в счётчиках событий.
    mcu.gpioa.odr = 0  # BSRR = BR1: PA1 = 0 до первого события
    mcu.gpioa.edges = []
    mcu.update_events = 0
    mcu.update_count = 0
    tim.write_cr1(CEN)
    return tim


def run_ms(mcu, ms):
    """Прогнать модельное время на ms миллисекунд."""
    target = mcu.now_cycles + int(round(ms * TIM2CLK_HZ / 1000.0))
    ticks = 0
    while mcu.now_cycles < target:
        mcu.step()
        ticks += 1
        if ticks > MAX_TICKS:
            raise RuntimeError("run_ms: превышен лимит тактов (проверьте PSC/CEN)")


def run_until_edges(mcu, n_edges):
    """Пока на PA1 меньше n_edges фронтов — шагать модель."""
    ticks = 0
    while len(mcu.gpioa.edges) < n_edges:
        mcu.step()
        ticks += 1
        if ticks > MAX_TICKS:
            raise RuntimeError(
                "run_until_edges: фронты не приходят (проверьте DIER.UIE, NVIC, CR1.CEN)"
            )


def run_until_updates(mcu, n_updates):
    """Пока g_update_count (выполненные обработчики) меньше n_updates."""
    ticks = 0
    while mcu.update_count < n_updates:
        mcu.step()
        ticks += 1
        if ticks > MAX_TICKS:
            raise RuntimeError(
                "run_until_updates: обработчики не выполняются (проверьте UIE/NVIC/CEN)"
            )


def run_experiment(interval_ms, n_update_events, psc=PSC_DEFAULT, ui=True, nvic=True):
    """Настроить TIM2 как в TIM2_IntervalInit и собрать фронты PA1.

    Возвращает список времен фронтов в мс (len == n_update_events):
    каждый фронт — одно событие обновления, обработанное по прерыванию.
    """
    mcu = MCU()
    interval_init(mcu, interval_ms, psc=psc, ui=ui, nvic=nvic)
    run_until_edges(mcu, n_update_events)
    return [e["t_ms"] for e in mcu.gpioa.edges]
