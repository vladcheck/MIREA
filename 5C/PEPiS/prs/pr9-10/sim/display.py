"""Битово-точная модель семисегментного индикатора с общим катодом,
подключённого к младшим восьми разрядам порта (PA0–PA7 STM32F103C8 /
PORTA ATmega32) — практическая работа № 5 (пр9-10).

Моделируется:
  - таблица кодов цифр 0–9 (табл. 9.21 методички, индикатор с общим
    катодом: единица включает сегмент, бит 0 — сегмент a, бит 6 — g,
    бит 7 — десятичная точка dp);
  - запись кода в порт: STM32 — через BSRR (младшие 16 бит устанавливают,
    старшие 16 бит сбрасывают линии), ATmega32 — прямая запись PORTA;
  - статический вывод (учебный пример, цифра 5);
  - последовательная смена цифр по событию таймера (вариант 4:
    цифры 9-8-7-6, обратный порядок, T_симв = 400 мс);
  - измерение интервалов между изменениями кода порта в духе
    логического анализатора (дискретизация 1 мс);
  - диагностическое изменение варианта 4 — инвертированный код.

Это модель сигналов портов, а не подмена схемы: она проверяет таблицу
кодов, порядок следования цифр и временные параметры программ из src/.
"""

# ---------------------------------------------------------------------------
# Таблица 9.21: коды цифр для индикатора с общим катодом
# ---------------------------------------------------------------------------
# Младший бит — сегмент a, бит 6 — сегмент g, бит 7 — dp.
SEGMENT_CODE_CC = (
    0x3F, 0x06, 0x5B, 0x4F, 0x66,
    0x6D, 0x7D, 0x07, 0x7F, 0x6F,
)

# Геометрия цифр: множество сегментов, образующих изображение.
DIGIT_SEGMENTS = {
    0: frozenset("abcdef"),
    1: frozenset("bc"),
    2: frozenset("abged"),
    3: frozenset("abgcd"),
    4: frozenset("fgbc"),
    5: frozenset("afgcd"),
    6: frozenset("afgedc"),
    7: frozenset("abc"),
    8: frozenset("abcdefg"),
    9: frozenset("abcfgd"),
}

SEGMENT_BIT = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "dp": 7}

# Параметры варианта 4 (табл. 9.26).
SEQUENCE_VARIANT4 = (9, 8, 7, 6)   # цифры
T_SYMBOL_MS = 400                  # T_симв, мс
SELFTEST_DIGITS = (0, 8, 9)        # методика: 0, 8 и цифра варианта

# Таймеры (методика работы 9.3).
TIM2_PSC = 7999            # STM32: 8 МГц / 8000 = 1 кГц, отсчёт 1 мс
TIM2_ARR = 399             # STM32: 400 отсчётов -> ровно 400,0 мс
TIMER0_OCR = 124           # ATmega32: предделитель 1024 -> 128 мкс,
TIMER0_EVENTS = 25         # 125 отсчётов = 16,000 мс; 25 событий = 400,0 мс

# Дискретизация логического анализатора в модели, мс.
LA_SAMPLE_MS = 1.0


# ---------------------------------------------------------------------------
# Коды и сегменты
# ---------------------------------------------------------------------------
def code_for_digit(digit):
    """Код цифры для общего катода (табл. 9.21)."""
    if not 0 <= digit <= 9:
        raise ValueError(f"цифра вне диапазона 0–9: {digit}")
    return SEGMENT_CODE_CC[digit]


def segments_for_code(code):
    """Множество светящихся сегментов для кода (общий катод)."""
    return frozenset(
        name for name, bit in SEGMENT_BIT.items() if code & (1 << bit)
    )


def decode_digit(code):
    """Цифра по коду или None, если рисунок не является цифрой 0–9."""
    for digit, segments in DIGIT_SEGMENTS.items():
        if segments == segments_for_code(code):
            return digit
    return None


def invert_code(code):
    """Инверсия кода в пределах восьми младших битов (общий анод)."""
    return (~code) & 0xFF


# ---------------------------------------------------------------------------
# Модель портов
# ---------------------------------------------------------------------------
class STM32PortA:
    """GPIOA STM32F103C8: запись через BSRR, чтение уровней из ODR."""

    def __init__(self):
        self.odr = 0x0000

    def write_code(self, code):
        """Display_WriteCode: BSRR = reset_mask | set_mask."""
        set_mask = code & 0xFF
        reset_mask = ((~code) & 0xFF) << 16
        bsrr = reset_mask | set_mask
        self.odr |= bsrr & 0xFFFF          # младшие 16 бит — установка
        self.odr &= ~(bsrr >> 16) & 0xFFFF  # старшие 16 бит — сброс
        return self.odr & 0xFF

    def levels(self):
        """Уровни PA7..PA0 — по младшим восьми битам ODR."""
        return self.odr & 0xFF


class AVRPortA:
    """PORTA ATmega32: прямая запись восьмиразрядного кода."""

    def __init__(self):
        self.porta = 0x00

    def write_code(self, code):
        self.porta = code & 0xFF
        return self.porta

    def levels(self):
        return self.porta


# ---------------------------------------------------------------------------
# Сценарии вывода
# ---------------------------------------------------------------------------
def static_scenario(digit):
    """Статический вывод: одна запись кода в начале моделирования."""
    return [(0.0, code_for_digit(digit))]


def variant4_scenario(duration_ms):
    """Сценарий варианта 4: самопроверка 0, 8, 9, затем цикл
    9, 6, 7, 8 (обратный порядок) с интервалом T_симв = 400 мс."""
    writes = []
    t = 0.0
    for digit in SELFTEST_DIGITS:
        writes.append((t, code_for_digit(digit)))
        t += T_SYMBOL_MS
    index = 0  # начальный индекс массива {9,8,7,6}
    while t < duration_ms:
        writes.append((t, code_for_digit(SEQUENCE_VARIANT4[index])))
        index = 3 if index == 0 else index - 1
        t += T_SYMBOL_MS
    return writes


def diagnostic_scenario():
    """Диагностика варианта 4: инвертированный код цифры 5."""
    return [(0.0, invert_code(code_for_digit(5)))]


# ---------------------------------------------------------------------------
# Логический анализатор (дискретизация 1 мс)
# ---------------------------------------------------------------------------
def sample_waveform(writes, duration_ms, sample_ms=LA_SAMPLE_MS):
    """Осциллограмма уровней порта: [(t_мс, уровни), ...]."""
    samples = []
    code = 0
    wi = 0
    t = 0.0
    while t <= duration_ms:
        while wi < len(writes) and writes[wi][0] <= t:
            code = writes[wi][1]
            wi += 1
        samples.append((t, code))
        t += sample_ms
    return samples


def measure_change_intervals(samples):
    """Измерение интервалов между изменениями кода порта, мс.

    Примечание: если соседние выводимые цифры совпадают (у варианта 4
    самопроверка заканчивается цифрой 9, и цикл тоже начинается с 9),
    код порта не меняется два интервала подряд — такие участки дают
    удвоенный интервал. Это свойство последовательности, а не ошибка
    таймера; интервал событий таймера измеряется отдельно."""
    intervals = []
    prev_t, prev_code = samples[0]
    for t, code in samples[1:]:
        if code != prev_code:
            intervals.append(round(t - prev_t, 3))
            prev_t, prev_code = t, code
    return intervals


def event_intervals(writes):
    """Интервалы между событиями записи в порт (событиями таймера), мс."""
    return [round(writes[i + 1][0] - writes[i][0], 3)
            for i in range(len(writes) - 1)]
