"""Битово-точная модель передатчика и приёмника USART1 (STM32F103C8).

Позиционная модель на чистом stdlib повторяет формат кадра 8N1
(1 стартовый бит, 8 информационных битов младшим битом вперёд,
1 стоповый бит; в состоянии покоя линия высокая) и делитель скорости
USART1_BRR при 16-кратной передискретизации: BRR = round(PCLK2 / Baud),
фактическая скорость = PCLK2 / BRR (табл. 9.11 TZ).

Базовая конфигурация работы: HSI 8 МГц, PCLK2 = 8 МГц, USART1,
PA9 = TX, PA10 = RX. Индивидуальный вариант 4: 19200 бит/с,
управляющий символ 'D' (0x44), диагностическое изменение: USART1_BRR
уменьшен в 2 раза (208 = 0x00D0), приёмник терминала слушает 19200.

Время во всех функциях измеряется в микросекундах.
"""

import bisect

# ---------------------------------------------------------------------------
# Константы базовой конфигурации и варианта 4
# ---------------------------------------------------------------------------
PCLK2_HZ = 8_000_000  # HSI 8 МГц без PLL, шина APB2 без делителя
BAUD_NOMINAL = 19200  # скорость индивидуального варианта 4, бит/с
BRR_VARIANT4 = 417  # round(8000000 / 19200) = 0x01A1
BRR_DIAG_HALF = 208  # диагностика: BRR в 2 раза меньше нормы, 0x00D0
STARTUP_STRING = "PR4-04 STM32 READY\r\n"  # строка запуска варианта 4
CTRL_CHAR = "D"  # управляющий символ, 0x44, инвертирует светодиод PA1

# Табл. 9.11 TZ: скорость, BRR и фактическая скорость при PCLK2 = 8 МГц.
TZ_BRR_TABLE = (
    (2400, 3333, "0x0D05", 2400.24),
    (4800, 1667, "0x0683", 4799.04),
    (9600, 833, "0x0341", 9603.84),
    (19200, 417, "0x01A1", 19184.65),
    (38400, 208, "0x00D0", 38461.54),
)


# ---------------------------------------------------------------------------
# Делитель скорости и временные параметры кадра
# ---------------------------------------------------------------------------
def brr_value(pclk_hz, baud):
    """Значение USART1_BRR при 16-кратной передискретизации.

    В STM32F103BRR численно равен округлённому отношению PCLK2 / Baud,
    что совпадает с формулой из прошивки:
    ((PCLK2_HZ + BAUD / 2) / BAUD) с целочисленным делением.
    """
    return int(round(pclk_hz / baud))


def actual_baud(pclk_hz, brr):
    """Фактическая скорость передачи, бит/с (PCLK2 / BRR)."""
    return pclk_hz / brr


def bit_interval_us(pclk_hz, brr):
    """Длительность битового интервала, мкс (BRR / PCLK2)."""
    return brr / pclk_hz * 1e6


# ---------------------------------------------------------------------------
# Кадр 8N1: последовательность битов и осциллограмма TX
# ---------------------------------------------------------------------------
def frame_bits(byte):
    """Сегменты кадра 8N1: [(уровень, длительность в битах), ...].

    Стартовый бит 0, восемь информационных битов младшим битом вперёд
    (D0..D7), стоповый бит 1. Всего 10 битовых интервалов.
    """
    segments = [(0, 1.0)]  # стартовый бит
    for i in range(8):
        segments.append(((byte >> i) & 1, 1.0))  # D0..D7, LSB вперёд
    segments.append((1, 1.0))  # стоповый бит
    return segments


def render_tx(
    byte, brr, pclk, samples_per_bit=20, idle_lead_bits=0.0, idle_tail_bits=0.0
):
    """Осциллограмма TX одного кадра: [(t_мкс, уровень), ...].

    Один битовый интервал разбит на samples_per_bit равномерных
    выборок (по умолчанию 20, то есть 20 выборок на бит). Покой
    до/после кадра задаётся числом битовых интервалов.
    """
    t_bit = bit_interval_us(pclk, brr)
    dt = t_bit / samples_per_bit
    samples = []
    t = 0.0
    for _ in range(int(round(idle_lead_bits * samples_per_bit))):
        samples.append((round(t, 6), 1))
        t += dt
    for level, dur_bits in frame_bits(byte):
        for _ in range(int(round(dur_bits * samples_per_bit))):
            samples.append((round(t, 6), level))
            t += dt
    for _ in range(int(round(idle_tail_bits * samples_per_bit))):
        samples.append((round(t, 6), 1))
        t += dt
    return samples


def render_stream(text, brr, pclk, samples_per_bit=20, lead_us=50.0, tail_us=50.0):
    """Осциллограмма строки: кадры идут подряд, покой до и после.

    Возвращает (образцы, кадры), где образцы: [(t_мкс, уровень)],
    кадры: [(t_нач_мкс, t_кон_мкс, символ)] для подписей на рисунках.
    """
    t_bit = bit_interval_us(pclk, brr)
    dt = t_bit / samples_per_bit
    samples = []
    frames = []
    t = 0.0
    for _ in range(int(round(lead_us / dt))):
        samples.append((round(t, 6), 1))
        t += dt
    for ch in text:
        t0 = t
        for level, dur_bits in frame_bits(ord(ch)):
            for _ in range(int(round(dur_bits * samples_per_bit))):
                samples.append((round(t, 6), level))
                t += dt
        frames.append((round(t0, 6), round(t, 6), ch))
    for _ in range(int(round(tail_us / dt))):
        samples.append((round(t, 6), 1))
        t += dt
    return samples, frames


# ---------------------------------------------------------------------------
# Приёмник 8N1
# ---------------------------------------------------------------------------
def _level_at(samples, times, t):
    """Уровень линии в момент t (последний образец не позже t)."""
    i = bisect.bisect_right(times, t) - 1
    if i < 0:
        i = 0
    return samples[i][1]


def _find_falling_edge(samples, times, search_from):
    """Момент первого стартового бита (спад) не раньше search_from."""
    i = bisect.bisect_left(times, search_from)
    for j in range(max(i, 1), len(samples)):
        if samples[j][1] == 0 and samples[j - 1][1] == 1:
            return times[j]
    return None


def _decode_frame_at(samples, times, t_sync, t_bit_rx):
    """Декодировка одного кадра от момента стартового бита t_sync.

    Приёмник опрашивает линию посередине каждого битового интервала
    собственной скорости (реальный USART1 голосует 3 из 16 подвыборок,
    для модели середина бита достаточно). Возвращает (байт, FE):
    FE ( framing error ) = в момент стопового бита линия низкая.
    """
    value = 0
    for k in range(1, 9):  # D0..D7, опрос в середине бита
        level = _level_at(samples, times, t_sync + (k + 0.5) * t_bit_rx)
        value |= (level & 1) << (k - 1)
    stop = _level_at(samples, times, t_sync + 9.5 * t_bit_rx)
    return value, stop == 0


def decode_at_baud(samples, sample_baud, pclk=None):
    """Приёмник 8N1 со собственной скоростью sample_baud, бит/с.

    Ищет первый стартовый бит (спад линии) и декодирует один кадр.
    Возвращает (байт, fe_flag, ore_flag); байт None, если стартового
    бита в образцах нет. Параметр pclk сохранён для совместимости
    API: приёмник работает по своей шкале времени, делитель ему не
    нужен. ORE в одиночном кадре не возникает (см. decode_stream).
    """
    t_bit_rx = 1e6 / sample_baud
    times = [s[0] for s in samples]
    t_sync = _find_falling_edge(samples, times, times[0])
    if t_sync is None:
        return (None, False, False)
    value, fe = _decode_frame_at(samples, times, t_sync, t_bit_rx)
    return (value, fe, False)


def decode_stream(samples, sample_baud, start_us=0.0):
    """Сквозная декодировка потока приёмником скоростью sample_baud.

    Кадры ищутся по стартовым битам; после оценки стопового бита
    поиск возобновляется с конца кадра (10 битовых интервалов
    приёмника). ORE ( overrun ) ставится, если приёмник не успевает
    за передатчиком: между концом текущего кадра и стартовым битом
    следующего проходит более одного битового интервала приёмника,
    то есть как минимум один полный кадр передатчика потерян.
    Такая трактовка соответствует наблюдаемому на Virtual Terminal
    эффекту при несовпадении скоростей (мусор и флаги ORE/FE).
    Возвращает список словарей: t_sync_us (момент стартового бита),
    byte, fe, ore.
    """
    t_bit_rx = 1e6 / sample_baud
    times = [s[0] for s in samples]
    frames = []
    search = start_us
    while True:
        t_sync = _find_falling_edge(samples, times, search)
        if t_sync is None:
            break
        value, fe = _decode_frame_at(samples, times, t_sync, t_bit_rx)
        frames.append({"t_sync_us": t_sync, "byte": value, "fe": fe, "ore": False})
        search = t_sync + 10.0 * t_bit_rx
    # ORE: пропущен хотя бы один полный кадр между двумя кадрами.
    for i, frame in enumerate(frames):
        if i + 1 < len(frames):
            gap = frames[i + 1]["t_sync_us"] - frame["t_sync_us"] - 10.0 * t_bit_rx
        else:
            gap = times[-1] - frame["t_sync_us"] - 10.0 * t_bit_rx
        frame["ore"] = gap > t_bit_rx
    return frames


# ---------------------------------------------------------------------------
# Измерения по осциллограмме (в духе логического анализатора)
# ---------------------------------------------------------------------------
def measure_spans(samples, dt=None):
    """Участки постоянного уровня: [(t0_мкс, t1_мкс, уровень), ...].

    Граница участка: момент смены уровня (равен началу следующего
    образца). Если dt не задан, он вычисляется как шаг равномерной
    выборки. Длительность участка = t1 - t0.
    """
    if dt is None and len(samples) > 1:
        dt = samples[1][0] - samples[0][0]
    spans = []
    for t, level in samples:
        if spans and spans[-1][2] == level:
            spans[-1][1] = t
        else:
            spans.append([t, t, level])
    for i in range(len(spans) - 1):
        spans[i][1] = spans[i + 1][0]
    spans[-1][1] = samples[-1][0] + dt
    return [(a, b, lvl) for (a, b, lvl) in spans]


def measure_bit_intervals(samples, dt=None):
    """Измерение битовых интервалов по участкам уровня.

    Каждый участок разбивается на целое число битов; длительность
    одного бита на участке = (t1 - t0) / n. Возвращает список
    [(t0, t1, уровень, n_битов, бит_мкс), ...]. Как минимум пять
    измерений: в кадре 8N1 всегда не меньше шести участков.
    """
    spans = measure_spans(samples, dt)
    if dt is None and len(samples) > 1:
        dt = samples[1][0] - samples[0][0]
    shortest = min(b - a for (a, b, _) in spans)
    result = []
    for a, b, level in spans:
        n_bits = max(1, round((b - a) / shortest))
        result.append((a, b, level, n_bits, (b - a) / n_bits))
    return result
