# -*- coding: utf-8 -*-
"""Модель восьмиразрядной матрицы R-2R для ПР 11-12 (вариант 4).

Воспроизводит электрическую часть стенда методички (учебная работа № 6):
выходы PA0..PA7 STM32F103C8 управляют лестницей R-2R (R = 10 кОм,
2R = 20 кОм, завершающий 2R от младшего узла на GND), выход VOUT
снимается со старшего узла и измеряется высокоомным входом
(модель DC Voltmeter / Oscilloscope из Proteus).

Напряжение считается методом узловых потенциалов: каждый разряд - это
тевениновский источник (UH при единице, 0 В при нуле) с выходным
сопротивлением вывода GPIO r_out, последовательно с резистором 2R.

Параметры модели (UH, r_out) соответствуют модели STM32F103C8 в
Proteus 8.17 при питании 3,3 В: высокий уровень 3,30 В, выходное
сопротивление вывода 50 Ом.
"""

# ---------------------------------------------------------------------------
# Параметры стенда и модели
# ---------------------------------------------------------------------------
UH_V = 3.30          # высокий уровень GPIO, В (измеряется на PAx)
R_OHM = 10_000.0     # R матрицы, Ом
R2_OHM = 20_000.0    # 2R матрицы, Ом
R_OUT_OHM = 50.0     # выходное сопротивление вывода GPIO, Ом
R_METER_OHM = 10e6   # входное сопротивление вольтметра/осциллографа, Ом

T_STEP_MS = 10       # шаг пилы варианта 4, мс
N_BITS = 8


def q_step(uh_v=UH_V):
    """Шаг квантования идеальной матрицы, В."""
    return uh_v / 256.0


def solve_ladder(code, uh_v=UH_V, r_ohm=R_OHM, r2_ohm=R2_OHM,
                 r_out_ohm=R_OUT_OHM, r_meter_ohm=R_METER_OHM,
                 terminated=True):
    """Напряжение выхода VOUT (старший узел) для кода 0..255, В.

    Метод узловых потенциалов: 8 узлов, линейная система 8x8 решается
    методом Гаусса без выбора главного элемента (матрица диагонально
    преобладающая). terminated=False воспроизводит диагностическое
    изменение варианта 4 (отключённый завершающий 2R).
    """
    if not 0 <= code <= 255:
        raise ValueError("code must be 0..255")
    n = N_BITS
    g_bit = 1.0 / (r_out_ohm + r2_ohm)   # проводимость ветви разряда
    g_r = 1.0 / r_ohm                    # проводимость связующего R
    g_meter = 1.0 / r_meter_ohm

    a = [[0.0] * n for _ in range(n)]
    b = [0.0] * n
    for i in range(n):
        src = uh_v if (code >> i) & 1 else 0.0
        a[i][i] += g_bit
        b[i] += g_bit * src
        if i > 0:
            a[i][i] += g_r
            a[i][i - 1] -= g_r
        if i < n - 1:
            a[i][i] += g_r
            a[i][i + 1] -= g_r
    if terminated:
        a[0][0] += 1.0 / r2_ohm
    a[n - 1][n - 1] += g_meter

    # Прямой ход и обратная подстановка (Гаусс).
    for col in range(n):
        piv = a[col][col]
        for row in range(col + 1, n):
            f = a[row][col] / piv
            for k in range(col, n):
                a[row][k] -= f * a[col][k]
            b[row] -= f * b[col]
    x = [0.0] * n
    for row in range(n - 1, -1, -1):
        s = b[row] - sum(a[row][k] * x[k] for k in range(row + 1, n))
        x[row] = s / a[row][row]
    return x[n - 1]


def u_calc(code, uh_v=UH_V):
    """Расчётное напряжение идеальной матрицы: UH * D / 256."""
    return uh_v * code / 256.0


def bit_string(code):
    """Двоичная запись кода старшим разрядом вперёд: D7..D0."""
    return format(code, "08b")


# ---------------------------------------------------------------------------
# Временная диаграмма пилы (расчёт периода)
# ---------------------------------------------------------------------------
def ramp_waveform(periods, t_step_ms=T_STEP_MS, dt_ms=0.5):
    """Пилообразный сигнал 0..255 с шагом t_step_ms, periods полных
    периодов (256 ступеней на период). Возвращает (samples, wrap_times):
    образцы (t_ms, code, u_v) и моменты перехода 255 -> 0, мс.
    """
    total_ms = periods * 256.0 * t_step_ms
    samples = []
    wrap_times = []
    t = 0.0
    prev_code = 0
    while t <= total_ms:
        step_idx = int(t // t_step_ms)
        code = step_idx % 256
        if prev_code == 255 and code == 0 and t > 0:
            wrap_times.append(t)
        u = solve_ladder(code)
        samples.append((t, code, u))
        prev_code = code
        t += dt_ms
    return samples, wrap_times


def measure_periods(wrap_times):
    """Пять расчётных периодов по моментам перехода 255 -> 0, мс."""
    periods = [wrap_times[i + 1] - wrap_times[i]
               for i in range(len(wrap_times) - 1)]
    avg = sum(periods) / len(periods)
    return periods, avg
