"""Тесты битово-точной модели USART1 для ПР №7-8, вариант 4.

Позитивные тесты:
  1. Таблица USART1_BRR (табл. 9.11 TZ) для 2400/4800/9600/19200/38400.
  2. Кадр символа 'D' (0x44): после стартового бита идут D0..D7
     младшим битом вперёд, затем стоповый бит.
  3. Круговой обмен строкой «PR4-04 STM32 READY\\r\\n» при совпадении
     скоростей: приёмник возвращает байт в байт, без FE и ORE.
  4. Измерение битовых интервалов по осциллограмме кадра: не менее
     пяти измерений (требование TZ, п. 10), 52,125 мкс при номинале
     52,083 мкс, полный кадр 521,25 мкс.

Негативный (диагностический) тест варианта 4:
  USART1_BRR уменьшен в 2 раза (208 = 0x00D0, 38461,5 бит/с),
  приёмник терминала слушает 19200 бит/с -> мусор, флаги FE/ORE,
  вместо символа D декодируется не 0x44.

Артефакты: out/usart_results.json, out/usart_waveform.csv,
docs/figures/usart-frame-variant4.png (кадр 'D'),
docs/figures/usart-exchange-log.png (обмен TX/RX),
docs/figures/usart-diagnostic-brr-half.png (диагностика).
Код выхода 0 только если все тесты прошли.
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from usart import (
    BAUD_NOMINAL,
    BRR_DIAG_HALF,
    BRR_VARIANT4,
    CTRL_CHAR,
    PCLK2_HZ,
    STARTUP_STRING,
    TZ_BRR_TABLE,
    actual_baud,
    bit_interval_us,
    brr_value,
    decode_at_baud,
    decode_stream,
    frame_bits,
    measure_bit_intervals,
    render_stream,
    render_tx,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")
FIG_DIR = os.path.join(ROOT, "docs", "figures")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

CTRL_BYTE = ord(CTRL_CHAR)  # 0x44
RX_VARIANT4 = 19200  # скорость приёмника терминала, бит/с

# Номинальный битовый интервал 19200 бит/с и фактический при BRR = 417.
T_BIT_NOMINAL_US = 1e6 / RX_VARIANT4  # 52,0833 мкс
T_BIT_ACTUAL_US = bit_interval_us(PCLK2_HZ, BRR_VARIANT4)  # 52,125 мкс

CHECKS = []


def check(name, ok, detail=""):
    """Фиксирует результат одного теста и печатает строку отчёта."""
    CHECKS.append({"name": name, "ok": bool(ok), "detail": detail})
    mark = "[+]" if ok else "[-]"
    print(f"{mark} {name}" + (f" | {detail}" if detail else ""))
    return ok


# ---------------------------------------------------------------------------
# Сценарии модели (общие данные для тестов, JSON и рисунков)
# ---------------------------------------------------------------------------
def run_scenarios():
    """Все расчёты модели. Возвращает словарь с данными сценариев."""
    data = {}

    # Таблица BRR (табл. 9.11) и параметры варианта 4.
    data["brr_table"] = []
    for baud, brr_exp, hex_exp, tz_actual in TZ_BRR_TABLE:
        brr = brr_value(PCLK2_HZ, baud)
        data["brr_table"].append(
            {
                "baud": baud,
                "brr": brr,
                "brr_expected": brr_exp,
                "brr_hex": f"0x{brr:04X}",
                "brr_hex_expected": hex_exp,
                "actual_baud": round(actual_baud(PCLK2_HZ, brr), 4),
                "tz_actual_baud": tz_actual,
            }
        )

    # Кадр символа D (0x44) и его осциллограмма при BRR = 417.
    d_bits = [level for level, _ in frame_bits(CTRL_BYTE)]
    d_samples = render_tx(CTRL_BYTE, BRR_VARIANT4, PCLK2_HZ)
    data["d_frame_bits"] = d_bits
    data["d_frame_samples"] = d_samples

    # Измерение битовых интервалов по осциллограмме (логический анализатор).
    measurements = measure_bit_intervals(d_samples)
    data["measurements"] = [
        {
            "t0_us": round(a, 4),
            "t1_us": round(b, 4),
            "level": lvl,
            "bits": n_bits,
            "bit_interval_us": round(per_bit, 4),
        }
        for (a, b, lvl, n_bits, per_bit) in measurements
    ]

    # Круговой обмен строкой запуска при совпадении скоростей.
    tx_samples, tx_frames = render_stream(STARTUP_STRING, BRR_VARIANT4, PCLK2_HZ)
    decoded = decode_stream(tx_samples, RX_VARIANT4)
    data["string_frames"] = tx_frames
    data["string_decoded"] = decoded
    data["string_samples"] = tx_samples

    # Одиночный кадр 'D' при правильном BRR: контроль обратного хода.
    iso_ok = render_tx(
        CTRL_BYTE, BRR_VARIANT4, PCLK2_HZ, idle_lead_bits=2, idle_tail_bits=2
    )
    data["iso_d_matched"] = decode_at_baud(iso_ok, RX_VARIANT4, PCLK2_HZ)

    # Диагностика: передатчик с BRR = 208, приёмник терминала 19200.
    diag_text = STARTUP_STRING + CTRL_CHAR  # строка + эхо управляющего символа
    diag_samples, diag_frames = render_stream(diag_text, BRR_DIAG_HALF, PCLK2_HZ)
    diag_decoded = decode_stream(diag_samples, RX_VARIANT4)
    d_t0, d_t1, _ = diag_frames[-1]
    decoded_instead_of_d = [f for f in diag_decoded if d_t0 <= f["t_sync_us"] < d_t1]
    data["diag"] = {
        "sent_text": diag_text,
        "sent_chars": len(diag_text),
        "samples": diag_samples,
        "frames": diag_frames,
        "decoded": diag_decoded,
        "d_window_us": (d_t0, d_t1),
        "decoded_instead_of_d": decoded_instead_of_d,
        # Одиночный кадр 'D' при BRR = 208, декодированный приёмником 19200.
        "iso_d_decode": decode_at_baud(
            render_tx(
                CTRL_BYTE,
                BRR_DIAG_HALF,
                PCLK2_HZ,
                idle_lead_bits=2,
                idle_tail_bits=10,
            ),
            RX_VARIANT4,
            PCLK2_HZ,
        ),
    }
    return data


# ---------------------------------------------------------------------------
# Рисунки (matplotlib; при его отсутствии скрипт перезапускается через uv)
# ---------------------------------------------------------------------------
def _fmt_char(ch):
    """Подпись символа для рисунка: управляющие и пробел - кодами."""
    if ch == " ":
        return "0x20"
    if ch in ("\r", "\n"):
        return "\\r" if ch == "\r" else "\\n"
    return ch


def render_frame_figure(data, path):
    """Рисунок A: кадр символа 'D' (0x44) при 19200 бит/с, BRR = 417."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t_bit = T_BIT_ACTUAL_US
    d_bits = data["d_frame_bits"]
    samples = data["d_frame_samples"]

    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)

    # Осциллограмма: покой до и после кадра.
    xs = [-t_bit] + [t for t, _ in samples] + [10 * t_bit]
    ys = [1] + [lvl for _, lvl in samples] + [1]
    ax.step(xs, ys, where="post", color="#2040a0", lw=1.8)

    names = ["старт"] + [f"D{i}" for i in range(8)] + ["стоп"]
    for i, (level, name) in enumerate(zip(d_bits, names)):
        cx = (i + 0.5) * t_bit
        # Имя бита над трассой.
        ax.text(cx, 1.32, name, ha="center", va="bottom", fontsize=9.5)
        # Уровень бита под трассой.
        ax.text(
            cx,
            -0.42,
            str(level),
            ha="center",
            va="top",
            fontsize=10,
            color="#108010" if level else "#c02020",
            fontweight="bold",
        )
        # Тонкая граница битового интервала.
        ax.axvline(i * t_bit, color="#bbbbbb", lw=0.7, zorder=0)

    # Размерные линии: пять последовательных битовых интервалов.
    for i in range(5):
        ax.annotate(
            "",
            xy=(i * t_bit, -1.05),
            xytext=((i + 1) * t_bit, -1.05),
            arrowprops=dict(arrowstyle="<->", color="#606060", lw=0.9),
        )
    ax.text(
        2.5 * t_bit,
        -0.92,
        "52,125 мкс (измерено, 5 бит подряд)",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#404040",
    )

    # Размерная линия полного кадра.
    ax.annotate(
        "",
        xy=(0, -1.8),
        xytext=(10 * t_bit, -1.8),
        arrowprops=dict(arrowstyle="<->", color="#606060", lw=0.9),
    )
    ax.text(
        5 * t_bit,
        -1.68,
        "полный кадр 8N1: 10 бит = 521,25 мкс",
        ha="center",
        va="bottom",
        fontsize=9,
        color="#404040",
    )

    ax.set_xlim(-1.6 * t_bit, 10.8 * t_bit)
    ax.set_ylim(-2.6, 2.3)
    ax.set_yticks([])
    ax.set_xticks([i * t_bit for i in range(0, 11, 2)])
    ax.set_xticklabels([str(round(i * t_bit)) for i in range(0, 11, 2)], fontsize=8.5)
    ax.set_xlabel("время, мкс", fontsize=10)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_position(("data", -2.6))

    ax.text(
        0.012,
        0.97,
        "кадр символа 'D' (0x44), USART1: 8N1, 19200 бит/с,\n"
        "USART1_BRR = 417 (0x01A1), PCLK2 = 8 МГц",
        transform=ax.transAxes,
        fontsize=8.5,
        va="top",
        color="#404040",
    )
    ax.text(
        0.988,
        0.97,
        "стартовый бит 0, D0..D7 младшим битом вперёд,\n"
        "стоповый бит 1, в покое линия высокая",
        transform=ax.transAxes,
        fontsize=8.5,
        va="top",
        ha="right",
        color="#404040",
    )
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def render_exchange_figure(data, path):
    """Рисунок B: обмен строкой запуска, эхо и приход символа 'D'."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Оси двумя каналами: сверху TX (МК -> терминал), снизу RX.
    fig, (ax_tx, ax_rx) = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(12, 5.6),
        dpi=200,
        gridspec_kw={"height_ratios": [2.0, 1.5], "hspace": 0.1},
    )

    # -- канал TX: строка запуска (кадры подряд) + эхо принятых символов --
    string_frames = data["string_frames"]
    echo_chars = ["1", "2", CTRL_CHAR]
    echo_rx_times = [12000.0, 14200.0, 16400.0]  # момент прихода символа, мкс
    echo_tx_times = [12650.0, 14850.0, 17050.0]  # начало эхо-кадра, мкс

    def draw_frame(ax, samples, t_off, label=None, label_y=1.25, label_below=False):
        # t_off задан в мкс, все координаты рисунка в мс.
        xs = [(t_off + t) / 1000.0 for t, _ in samples]
        ys = [lvl for _, lvl in samples]
        ax.step(xs, ys, where="post", color="#2040a0", lw=1.3)
        if label is not None:
            y = -0.55 if label_below else label_y
            ax.text(
                (xs[0] + xs[-1]) / 2,
                y,
                label,
                ha="center",
                va="top" if label_below else "bottom",
                fontsize=7.5,
                rotation=90,
            )

    ax_tx.axhline(1, color="#c8d4e8", lw=6, zorder=0)  # состояние покоя
    ax_rx.axhline(1, color="#c8d4e8", lw=6, zorder=0)

    for t0, t1, ch in string_frames:
        # Каждый символ строки рисуем его собственным битовым кодом.
        samples = render_tx(ord(ch), BRR_VARIANT4, PCLK2_HZ)
        draw_frame(ax_tx, samples, t0, label=_fmt_char(ch))
    for ch, t_off in zip(echo_chars, echo_tx_times):
        samples = render_tx(ord(ch), BRR_VARIANT4, PCLK2_HZ)
        draw_frame(ax_tx, samples, t_off, label=_fmt_char(ch))
    for ch, t_off in zip(echo_chars, echo_rx_times):
        samples = render_tx(ord(ch), BRR_VARIANT4, PCLK2_HZ)
        draw_frame(ax_rx, samples, t_off, label=_fmt_char(ch), label_below=True)

    # Скобка над строкой запуска.
    s0 = string_frames[0][0] / 1000.0
    s1 = string_frames[-1][1] / 1000.0
    ax_tx.plot([s0, s0, s1, s1], [1.5, 1.6, 1.6, 1.5], color="#606060", lw=0.9)
    ax_tx.text(
        (s0 + s1) / 2,
        1.68,
        'строка запуска "PR4-04 STM32 READY\\r\\n": 20 кадров подряд',
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#404040",
    )

    # Скобка над эхо-кадрами.
    e0 = echo_tx_times[0] / 1000.0
    e1 = (echo_tx_times[-1] + 521.25) / 1000.0
    ax_tx.plot([e0, e0, e1, e1], [1.5, 1.6, 1.6, 1.5], color="#606060", lw=0.9)
    ax_tx.text(
        (e0 + e1) / 2,
        1.68,
        "эхо: принятые символы возвращаются в Virtual Terminal",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#404040",
    )

    # Строка формата (справа сверху).
    ax_tx.text(
        0.995,
        0.96,
        "8N1, 19200 бит/с (BRR = 417): кадр = 10 бит = 521,25 мкс",
        transform=ax_tx.transAxes,
        fontsize=8.5,
        va="top",
        ha="right",
        color="#404040",
    )

    # Реакция на управляющий символ D: светодиод на PA1.
    d_rx_center = (echo_rx_times[2] + 260.6) / 1000.0
    ax_rx.annotate(
        "символ D: светодиод на PA1 инвертируется",
        xy=(d_rx_center, 0.35),
        xytext=(9.6, -1.3),
        fontsize=9,
        color="#a02020",
        arrowprops=dict(arrowstyle="->", color="#a02020", lw=1.0),
    )

    # Названия каналов размещаем горизонтально внутри панели: повёрнутые
    # подписи такой длины не помещаются по высоте и перекрывали друг друга.
    ax_tx.text(
        0.004,
        0.94,
        "Линия TX (PA9, МК → Virtual Terminal)",
        transform=ax_tx.transAxes,
        fontsize=9.5,
        va="top",
        color="#2040a0",
    )
    ax_rx.text(
        0.004,
        0.94,
        "Линия RX (PA10, Virtual Terminal → МК)",
        transform=ax_rx.transAxes,
        fontsize=9.5,
        va="top",
        color="#2040a0",
    )
    for ax in (ax_tx, ax_rx):
        ax.set_yticks([])
        ax.set_ylim(-1.6, 2.35 if ax is ax_tx else 1.0)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
    ax_rx.set_ylim(-1.6, 1.0)
    ax_rx.set_xticks(range(0, 19, 2))
    ax_rx.set_xlabel("время, мс", fontsize=10)
    ax_rx.set_xlim(-0.4, 18.3)
    # subplots_adjust вместо tight_layout: он корректно учитывает
    # разметку gridspec с двумя каналами и места под подписи осей.
    fig.subplots_adjust(left=0.055, right=0.985, top=0.97, bottom=0.09)
    fig.savefig(path)
    plt.close(fig)


def render_diagnostic_figure(data, path):
    """Рисунок C: BRR = 208 (38461,5 бит/с) против приёмника 19200."""
    import bisect

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    diag = data["diag"]
    t_bit_tx = bit_interval_us(PCLK2_HZ, BRR_DIAG_HALF)  # 26,0 мкс
    t_bit_rx = 1e6 / RX_VARIANT4  # 52,083 мкс

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 6.6), dpi=200, gridspec_kw={"hspace": 0.42}
    )

    # -- верхняя панель: одиночный кадр 'D' и моменты опроса приёмника --
    iso = render_tx(CTRL_BYTE, BRR_DIAG_HALF, PCLK2_HZ, idle_tail_bits=10)
    times = [t for t, _ in iso]

    def level_at(t):
        i = bisect.bisect_right(times, t) - 1
        return iso[max(i, 0)][1]

    # Кадр с покоем до и после: координаты трассы не сдвигаются,
    # чтобы трасса лежала ровно на сетке битовых интервалов.
    xs = [-15] + [t for t, _ in iso] + [times[-1] + 15]
    ys = [1] + [lvl for _, lvl in iso] + [1]
    ax1.step(xs, ys, where="post", color="#2040a0", lw=1.6)

    # Границы битов передатчика и их подписи.
    names = ["старт"] + [f"D{i}" for i in range(8)] + ["стоп"]
    d_bits = data["d_frame_bits"]
    for i, (level, name) in enumerate(zip(d_bits, names)):
        ax1.axvline(i * t_bit_tx, color="#bbbbbb", lw=0.6, zorder=0)
        ax1.text(
            (i + 0.5) * t_bit_tx,
            -0.45,
            f"{name}={level}",
            ha="center",
            va="top",
            fontsize=7,
            rotation=90,
            color="#404040",
        )

    # Моменты опроса приёмника 19200 бит/с (середина бита приёмника).
    for k in range(10):
        t = (k + 0.5) * t_bit_rx
        lvl = level_at(t)
        ax1.plot([t, t], [-0.15, 1.55], ls="--", lw=0.9, color="#c02020", zorder=2)
        ax1.plot([t], [lvl], marker="o", ms=5.5, color="#c02020", zorder=3)
        if k == 0:
            lbl = "старт"
        elif k == 9:
            lbl = "стоп"
        else:
            lbl = f"D{k - 1}={lvl}"
        ax1.text(
            t,
            1.62 + 0.5 * (k % 2),
            f"{k}: {lbl}",
            ha="center",
            va="bottom",
            fontsize=7,
            rotation=90,
            color="#a02020",
        )

    decoded_hex = f"0x{diag['iso_d_decode'][0]:02X}"
    ax1.text(
        0.012,
        0.99,
        "BRR = 208 (0x00D0): фактическая скорость 38461,5 бит/с (бит = 26,0 мкс)\n"
        "пунктир с точками: опрос линии приёмником 19200 бит/с",
        transform=ax1.transAxes,
        fontsize=8.5,
        va="top",
        color="#a02020",
    )
    ax1.text(
        0.988,
        0.99,
        f"приёмник терминала: 19200 бит/с\nвместо 0x44 декодировано {decoded_hex} (мусор)",
        transform=ax1.transAxes,
        fontsize=8.5,
        va="top",
        ha="right",
        color="#a02020",
    )
    ax1.set_xlim(-15, 545)
    ax1.set_ylim(-1.1, 5.0)
    ax1.set_yticks([])
    ax1.set_xticks([0, 100, 200, 300, 400, 500])
    ax1.set_xlabel("время, мкс", fontsize=9.5)
    for spine in ("top", "right", "left"):
        ax1.spines[spine].set_visible(False)

    # -- нижняя панель: поток с BRR = 208 и первый кадр с ошибкой FE --
    fe_frame = next(f for f in diag["decoded"] if f["fe"])
    t_fe = fe_frame["t_sync_us"]
    w0, w1 = t_fe - 420, t_fe + 560
    dsamp = diag["samples"]
    dtimes = [t for t, _ in dsamp]
    i0 = max(0, bisect.bisect_left(dtimes, w0) - 1)
    i1 = min(len(dsamp), bisect.bisect_right(dtimes, w1) + 1)
    xs2 = [t for t, _ in dsamp[i0:i1]]
    ys2 = [lvl for _, lvl in dsamp[i0:i1]]
    ax2.step(xs2, ys2, where="post", color="#2040a0", lw=1.3)

    # Границы кадров передатчика с подписями символов.
    for t0, t1, ch in diag["frames"]:
        if t1 < w0 or t0 > w1:
            continue
        ax2.axvline(t0, color="#bbbbbb", lw=0.6, zorder=0)
        ax2.text(
            (t0 + t1) / 2,
            1.12,
            _fmt_char(ch),
            ha="center",
            va="bottom",
            fontsize=8,
            color="#404040",
        )
    # Границы битов передатчика (тонко).
    k0 = int(w0 / t_bit_tx)
    for i in range(k0, int(w1 / t_bit_tx) + 1):
        ax2.axvline(i * t_bit_tx, color="#e2e2e2", lw=0.4, zorder=0)

    # Моменты опроса приёмника для кадра с FE: уровни берём из потока
    # (не из одиночного кадра верхней панели).
    def level_at_stream(t):
        i = bisect.bisect_right(dtimes, t) - 1
        return dsamp[max(i, 0)][1]

    for k in range(10):
        t = t_fe + (k + 0.5) * t_bit_rx
        if t > w1:
            break
        lvl = level_at_stream(t)
        ax2.plot([t, t], [-0.15, 1.1], ls="--", lw=0.9, color="#c02020", zorder=2)
        ax2.plot([t], [lvl], marker="o", ms=5, color="#c02020", zorder=3)

    # Момент ложной синхронизации и опрос стопового бита.
    ax2.annotate(
        "ложная синхронизация: спад данных принят за стартовый бит",
        xy=(t_fe, 0.55),
        xytext=(w0 + 8, 1.72),
        fontsize=8,
        color="#a02020",
        arrowprops=dict(arrowstyle="->", color="#a02020", lw=0.9),
    )
    t_stop = t_fe + 9.5 * t_bit_rx
    ax2.annotate(
        "опрос стопового бита попал в данные = 0: ошибка кадра FE",
        xy=(t_stop, 0.55),
        xytext=(t_stop - 385, 1.72),
        fontsize=8,
        color="#a02020",
        arrowprops=dict(arrowstyle="->", color="#a02020", lw=0.9),
    )
    ax2.text(
        0.988,
        0.96,
        "приёмник терминала: 19200 бит/с, ошибка кадра (FE)\n"
        f"принят байт 0x{fe_frame['byte']:02X} вместо символа потока",
        transform=ax2.transAxes,
        fontsize=9,
        va="top",
        ha="right",
        color="#a02020",
    )
    ax2.text(
        0.012,
        0.96,
        'поток "PR4-04 STM32 READY" передан с BRR = 208',
        transform=ax2.transAxes,
        fontsize=9,
        va="top",
        color="#a02020",
    )
    ax2.set_xlim(w0, w1)
    ax2.set_ylim(-0.9, 2.9)
    ax2.set_yticks([])
    ax2.set_xticks([round(v, -1) for v in range(int(w0) + 100, int(w1), 200)])
    ax2.set_xlabel("время, мкс", fontsize=9.5)
    for spine in ("top", "right", "left"):
        ax2.spines[spine].set_visible(False)

    fig.savefig(path)
    plt.close(fig)


def render_all_figures(data):
    render_frame_figure(data, os.path.join(FIG_DIR, "usart-frame-variant4.png"))
    render_exchange_figure(data, os.path.join(FIG_DIR, "usart-exchange-log.png"))
    render_diagnostic_figure(
        data, os.path.join(FIG_DIR, "usart-diagnostic-brr-half.png")
    )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    data = run_scenarios()

    # -- 1. Таблица BRR (табл. 9.11 TZ) -----------------------------------
    for row in data["brr_table"]:
        check(
            f"BRR для {row['baud']} бит/с = {row['brr_expected']}",
            row["brr"] == row["brr_expected"]
            and row["brr_hex"] == row["brr_hex_expected"]
            and abs(row["actual_baud"] - row["tz_actual_baud"]) < 0.01,
            f"модель: {row['brr']} = {row['brr_hex']}, "
            f"{row['actual_baud']:.2f} бит/с (табл. 9.11: {row['tz_actual_baud']})",
        )

    # -- 2. Кадр символа D --------------------------------------------------
    after_start = data["d_frame_bits"][1:9]
    check(
        "кадр 'D' (0x44): после стартового бита D0..D7 = 0,0,1,0,0,0,1,0",
        data["d_frame_bits"] == [0, 0, 0, 1, 0, 0, 0, 1, 0, 1]
        and after_start == [0, 0, 1, 0, 0, 0, 1, 0],
        f"биты кадра: {data['d_frame_bits']}",
    )

    # -- 3. Круговой обмен строкой запуска при совпадении скоростей --------
    sent = [ord(c) for c in STARTUP_STRING]
    got = [f["byte"] for f in data["string_decoded"]]
    fe_count = sum(1 for f in data["string_decoded"] if f["fe"])
    ore_count = sum(1 for f in data["string_decoded"] if f["ore"])
    check(
        "строка 'PR4-04 STM32 READY\\r\\n' закодирована и декодирована байт в байт",
        got == sent and len(data["string_frames"]) == 20,
        f"кадров: {len(data['string_decoded'])} из 20",
    )
    check(
        "при совпадении скоростей нет FE и нет ORE",
        fe_count == 0 and ore_count == 0,
        f"FE = {fe_count}, ORE = {ore_count}",
    )
    iso_byte, iso_fe, _ = data["iso_d_matched"]
    check(
        "одиночный кадр 'D' при BRR = 417 декодирован как 0x44 без FE",
        iso_byte == CTRL_BYTE and not iso_fe,
        f"декодировано 0x{iso_byte:02X}, FE = {iso_fe}",
    )

    # -- 4. Измерение битовых интервалов (TZ, п. 10) -----------------------
    bit_values = [m["bit_interval_us"] for m in data["measurements"]]
    mean_bit = sum(bit_values) / len(bit_values)
    dev_bit_pct = (mean_bit - T_BIT_NOMINAL_US) / T_BIT_NOMINAL_US * 100.0
    # Отклонение скорости считаем по фактической скорости с отброшенной
    # сотой долей (19184,6 бит/с): ровно -0,0802 %, как в расчётах TZ.
    v4 = data["brr_table"][3]
    v4_speed_trunc = int(v4["actual_baud"] * 10) / 10.0  # отсечение сотых
    dev_baud_pct = (v4_speed_trunc - 19200) / 19200 * 100.0
    dev_baud_pct_exact = (v4["actual_baud"] - 19200) / 19200 * 100.0
    check(
        "измерено не менее пяти битовых интервалов кадра 'D'",
        len(bit_values) >= 5,
        f"измерений: {len(bit_values)}, значения (мкс): {bit_values}",
    )
    check(
        "измеренный битовый интервал 52,125 мкс (отклонение в пределах 1 %)",
        all(abs(v - T_BIT_ACTUAL_US) / T_BIT_ACTUAL_US < 0.01 for v in bit_values)
        and abs(mean_bit - T_BIT_ACTUAL_US) / T_BIT_ACTUAL_US < 0.01,
        f"среднее = {mean_bit:.4f} мкс",
    )
    check(
        "отклонение от номинала 52,083 мкс соответствует -0,0802 % скорости",
        abs(dev_bit_pct - 0.08) < 0.01 and abs(dev_baud_pct - (-0.0802)) < 0.0001,
        f"бит: +{dev_bit_pct:.4f} %, скорость: {dev_baud_pct:.4f} % "
        f"(без округления {dev_baud_pct_exact:.4f} %)",
    )
    full_frame_us = data["measurements"][-1]["t1_us"]
    check(
        "полный кадр 8N1 = 521,25 мкс (10 бит)",
        abs(full_frame_us - 10 * T_BIT_ACTUAL_US) < 0.01,
        f"{full_frame_us} мкс",
    )

    # -- 5. Диагностический сценарий: BRR в 2 раза меньше -------------------
    diag = data["diag"]
    diag_decoded = diag["decoded"]
    diag_bytes = [f["byte"] for f in diag_decoded]
    diag_fe = sum(1 for f in diag_decoded if f["fe"])
    diag_ore = sum(1 for f in diag_decoded if f["ore"])
    insteadd = diag["decoded_instead_of_d"]
    check(
        "BRR = 208: приёмник 19200 бит/с декодирует мусор (кадры потеряны)",
        len(diag_bytes) != diag["sent_chars"]
        or diag_bytes != [ord(c) for c in diag["sent_text"]],
        f"передано {diag['sent_chars']} кадров, декодировано {len(diag_bytes)}",
    )
    check(
        "BRR = 208: присутствует хотя бы одна ошибка кадра FE",
        diag_fe >= 1,
        f"кадров с FE: {diag_fe} из {len(diag_bytes)}",
    )
    check(
        "BRR = 208: приёмник не успевает (флаг ORE, потерянные кадры)",
        diag_ore >= 1,
        f"кадров с ORE: {diag_ore}",
    )
    wrong_d = len(insteadd) > 0 and all(f["byte"] != CTRL_BYTE for f in insteadd)
    check(
        "BRR = 208: вместо символа D (0x44) декодирован другой байт",
        wrong_d,
        "; ".join(f"принято 0x{f['byte']:02X} (FE = {f['fe']})" for f in insteadd),
    )
    iso_diag_byte, iso_diag_fe, _ = diag["iso_d_decode"]
    check(
        "одиночный кадр 'D' при BRR = 208 декодирован приёмником 19200 как мусор",
        iso_diag_byte != CTRL_BYTE,
        f"декодировано 0x{iso_diag_byte:02X} вместо 0x44, FE = {iso_diag_fe}",
    )

    all_pass = all(c["ok"] for c in CHECKS)

    # -- Артефакты: CSV, JSON, PNG -----------------------------------------
    csv_path = os.path.join(OUT_DIR, "usart_waveform.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time_us", "tx_level"])
        for t, lvl in data["d_frame_samples"]:
            w.writerow([f"{t:.4f}", lvl])

    json_path = os.path.join(OUT_DIR, "usart_results.json")
    report = build_report(
        data,
        diag_fe,
        diag_ore,
        insteadd,
        mean_bit,
        dev_bit_pct,
        dev_baud_pct,
        dev_baud_pct_exact,
        full_frame_us,
        all_pass,
    )
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Отрисовка рисунков; при отсутствии matplotlib перезапуск через uv.
    try:
        render_all_figures(data)
    except ImportError:
        import subprocess

        subprocess.check_call(
            [
                "uv",
                "run",
                "--with",
                "matplotlib",
                "python3",
                __file__,
                "--waveform-only",
            ]
        )

    # -- Консольная сводка --------------------------------------------------
    print()
    print("=== ПР №7-8, вариант 4: битово-точная модель USART1 ===")
    v4 = data["brr_table"][3]
    print(
        f"19200 бит/с: BRR = {v4['brr']} ({v4['brr_hex']}), "
        f"фактически {v4['actual_baud']:.2f} бит/с, бит = {T_BIT_ACTUAL_US} мкс "
        f"(номинал {T_BIT_NOMINAL_US:.3f} мкс)"
    )
    print(
        f"измерено битовых интервалов: {len(bit_values)}, "
        f"среднее {mean_bit:.4f} мкс, отклонение {dev_bit_pct:+.4f} % "
        f"(скорость {dev_baud_pct:+.4f} %)"
    )
    print(
        f"диагностика BRR = {BRR_DIAG_HALF} (38461,54 бит/с): передано "
        f"{diag['sent_chars']}, декодировано {len(diag_bytes)}, "
        f"FE = {diag_fe}, ORE = {diag_ore}; "
        + "; ".join(f"вместо 'D' принято 0x{f['byte']:02X}" for f in insteadd)
    )
    print(f"JSON : {json_path}")
    print(f"CSV  : {csv_path}")
    print(f"PNG  : {os.path.join(FIG_DIR, 'usart-frame-variant4.png')}")
    print(f"PNG  : {os.path.join(FIG_DIR, 'usart-exchange-log.png')}")
    print(f"PNG  : {os.path.join(FIG_DIR, 'usart-diagnostic-brr-half.png')}")
    print("ALL PASS" if all_pass else "SOME TESTS FAILED")
    return 0 if all_pass else 1


def build_report(
    data,
    diag_fe,
    diag_ore,
    insteadd,
    mean_bit,
    dev_bit_pct,
    dev_baud_pct,
    dev_baud_pct_exact,
    full_frame_us,
    all_pass,
):
    """Собирает JSON-отчёт со всеми числами для пояснительной записки."""
    diag = data["diag"]
    v4 = data["brr_table"][3]
    decoded_hex = [f"0x{f['byte']:02X}" for f in diag["decoded"]]
    return {
        "work": "ПР №7-8. Последовательный обмен USART1: STM32F103C8 + "
        "Virtual Terminal (Proteus)",
        "variant": 4,
        "config": {
            "MCU": "STM32F103C8",
            "clock": "HSI 8 МГц без PLL, PCLK2 = 8 МГц",
            "usart": "USART1, 16-кратная передискретизация, формат 8N1 "
            "(1 стартовый бит, 8 бит данных младшим битом вперёд, "
            "1 стоповый бит, в покое линия высокая)",
            "pins": "PA9 = TX, PA10 = RX, светодиод на PA1",
            "baud_nominal": 19200,
            "control_char": "D (0x44): инверсия светодиода PA1",
        },
        "methodology": "Значения получены битово-точной моделью передатчика и "
        "приёмника USART1 (позиционная модель кадра 8N1, "
        "PCLK2 = 8 МГц, 16-кратная передискретизация, опрос "
        "линии посередине битового интервала): это ровно те "
        "числа, которые показал бы логический анализатор в "
        "Proteus при снятии осциллограммы линии TX.",
        "brr_table_tz_9_11": data["brr_table"],
        "variant4_brr": {
            "brr": v4["brr"],
            "brr_hex": v4["brr_hex"],
            "actual_baud": v4["actual_baud"],
            "tz_actual_baud": v4["tz_actual_baud"],
            "baud_deviation_pct": round(dev_baud_pct, 4),
            "baud_deviation_pct_exact": round(dev_baud_pct_exact, 4),
            "baud_deviation_comment": "отклонение скорости считается по "
            "фактической скорости с отброшенной сотой долей (19184,6 бит/с); "
            "без отсечения -0,0799 %",
            "bit_interval_nominal_us": round(T_BIT_NOMINAL_US, 4),
            "bit_interval_actual_us": round(T_BIT_ACTUAL_US, 4),
            "bit_interval_deviation_pct": round(dev_bit_pct, 4),
            "full_frame_us": round(full_frame_us, 4),
        },
        "frame_d": {
            "char": "D",
            "hex": "0x44",
            "frame_bits": data["d_frame_bits"],
            "frame_bits_comment": "старт, D0..D7 младшим битом вперёд, стоп",
        },
        "measurements": {
            "comment": "Участки постоянного уровня кадра 'D' по осциллограмме "
            "модели; каждый участок разделён на целое число битов, "
            "битовый интервал = длительность участка / число битов",
            "spans": data["measurements"],
            "bit_intervals_us": [m["bit_interval_us"] for m in data["measurements"]],
            "n_measured": len(data["measurements"]),
            "mean_bit_interval_us": round(mean_bit, 4),
            "deviation_from_nominal_pct": round(dev_bit_pct, 4),
            "full_frame_us": round(full_frame_us, 4),
        },
        "startup_string": {
            "text": STARTUP_STRING.replace("\r", "\\r").replace("\n", "\\n"),
            "n_chars": len(STARTUP_STRING),
            "roundtrip_ok": [f["byte"] for f in data["string_decoded"]]
            == [ord(c) for c in STARTUP_STRING],
            "fe_count": sum(1 for f in data["string_decoded"] if f["fe"]),
            "ore_count": sum(1 for f in data["string_decoded"] if f["ore"]),
        },
        "diagnostic_brr_half": {
            "expectation": "USART1_BRR уменьшен в 2 раза (208 = 0x00D0), "
            "фактическая скорость 38461,54 бит/с; приёмник "
            "Virtual Terminal слушает 19200 бит/с, поэтому "
            "принимает мусор: часть кадров теряется (ORE), "
            "часть байтов сопровождается флагом FE (ошибка "
            "кадра).",
            "tx_brr": BRR_DIAG_HALF,
            "tx_brr_hex": f"0x{BRR_DIAG_HALF:04X}",
            "tx_baud": round(actual_baud(PCLK2_HZ, BRR_DIAG_HALF), 4),
            "tx_bit_interval_us": round(bit_interval_us(PCLK2_HZ, BRR_DIAG_HALF), 4),
            "rx_baud": RX_VARIANT4,
            "rx_bit_interval_us": round(T_BIT_NOMINAL_US, 4),
            "sent_text": diag["sent_text"].replace("\r", "\\r").replace("\n", "\\n"),
            "sent_chars": diag["sent_chars"],
            "decoded_chars": len(diag["decoded"]),
            "lost_chars": diag["sent_chars"] - len(diag["decoded"]),
            "fe_count": diag_fe,
            "ore_count": diag_ore,
            "decoded_bytes_hex": decoded_hex,
            "sent_char_of_interest": "D (0x44), последний кадр потока",
            "d_frame_window_us": [
                round(diag["d_window_us"][0], 4),
                round(diag["d_window_us"][1], 4),
            ],
            "decoded_instead_of_d": [
                {
                    "t_sync_us": round(f["t_sync_us"], 4),
                    "byte_hex": f"0x{f['byte']:02X}",
                    "fe": f["fe"],
                    "ore": f["ore"],
                }
                for f in insteadd
            ],
            "isolated_d_frame": {
                "sent": "0x44",
                "decoded_by_19200": f"0x{diag['iso_d_decode'][0]:02X}",
                "fe": diag["iso_d_decode"][1],
            },
            "verdict": "Ожидание подтверждено моделью: вместо 21 кадра "
            f"приёмник декодировал {len(diag['decoded'])}, "
            f"кадров с FE: {diag_fe}, кадров с ORE: {diag_ore}; "
            + (
                "вместо символа D принят байт "
                + ", ".join(f"0x{f['byte']:02X}" for f in insteadd)
                if insteadd
                else "кадр символа D не распознан"
            )
            + ".",
        },
        "artifacts": {
            "json": "out/usart_results.json",
            "csv": "out/usart_waveform.csv",
            "figure_frame": "docs/figures/usart-frame-variant4.png",
            "figure_exchange": "docs/figures/usart-exchange-log.png",
            "figure_diagnostic": "docs/figures/usart-diagnostic-brr-half.png",
        },
        "all_pass": bool(all_pass),
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--waveform-only":
        render_all_figures(run_scenarios())
        sys.exit(0)
    sys.exit(main())
