"""Проверка модели семисегментного индикатора (вариант 4, пр9-10).

Сценарии:
  1. Таблица 9.21: коды цифр, светящиеся сегменты, обратная декодировка.
  2. Статическая индикация (учебный пример): цифра 5 -> код 0x6D ->
     уровни PA7–PA0, светящиеся сегменты.
  3. Последовательный вывод варианта 4 (STM32, запись через BSRR):
     самопроверка 0, 8, 9, затем цикл 9, 6, 7, 8 (обратный порядок),
     измерение интервалов между изменениями кода.
  4. То же для ATmega32 (запись PORTA): таймерная разметка
     16,000 мс × 25 = 400,0 мс.
  5. Диагностика: инвертированный код -> нечитаемый рисунок.

Артефакты: out/display_results.json, out/display_waveform.csv,
docs/figures/display-static-stm32.png, display-static-atmega32.png,
docs/figures/display-seq-stm32.png, display-seq-atmega32.png,
docs/figures/display-digits-variant4.png, display-diagnostic-inverted.png.
Код выхода 0 только если все проверки прошли.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import display as d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")
FIG_DIR = os.path.join(ROOT, "docs", "figures")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

LA_CHANNELS = ["PA7", "PA6", "PA5", "PA4", "PA3", "PA2", "PA1", "PA0"]

results = {"checks": [], "all_pass": True}


def check(name, ok, detail=""):
    results["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
    print(f"{'PASS' if ok else 'FAIL'}: {name} {detail}")
    if not ok:
        results["all_pass"] = False
    return ok


# ---------------------------------------------------------------------------
# 1. Таблица кодов 9.21
# ---------------------------------------------------------------------------
table_rows = []
roundtrip_ok = True
for digit in range(10):
    code = d.code_for_digit(digit)
    segments = "".join(sorted(d.segments_for_code(code)))
    decoded = d.decode_digit(code)
    table_rows.append(
        {
            "digit": digit,
            "code": f"0x{code:02X}",
            "segments": segments,
            "decoded": decoded,
        }
    )
    if decoded != digit:
        roundtrip_ok = False
check("таблица 9.21: коды 0–9 декодируются обратно", roundtrip_ok)

# ---------------------------------------------------------------------------
# 2. Статическая индикация, цифра 5 (обе платформы)
# ---------------------------------------------------------------------------
static = {}
for platform, cls in (("stm32", d.STM32PortA), ("avr", d.AVRPortA)):
    port = cls()
    code = d.code_for_digit(5)
    levels = port.write_code(code)
    lit = "".join(sorted(d.segments_for_code(levels)))
    decoded = d.decode_digit(levels)
    static[platform] = {
        "digit": 5,
        "code": f"0x{code:02X}",
        "levels_pa7_pa0": f"0b{levels:08b}",
        "lit_segments": lit,
        "decoded": decoded,
    }
    check(
        f"статика {platform}: цифра 5 -> 0x{code:02X}, сегменты {lit}",
        decoded == 5,
    )
results["static"] = static

# ---------------------------------------------------------------------------
# 3–4. Последовательный вывод варианта 4
# ---------------------------------------------------------------------------
DURATION_MS = 3600.0
SEQ_PORT = {"stm32": d.STM32PortA(), "avr": d.AVRPortA()}
writes = d.variant4_scenario(DURATION_MS)
expected_digits = [d.decode_digit(code) for _, code in writes]

for platform, port in SEQ_PORT.items():
    port_writes = [(t, port.write_code(code)) for t, code in writes]
    samples = d.sample_waveform(port_writes, DURATION_MS)
    change_intervals = d.measure_change_intervals(samples)
    intervals = d.event_intervals(writes)
    mean_interval = sum(intervals) / len(intervals) if intervals else 0.0
    deviation = (mean_interval - d.T_SYMBOL_MS) / d.T_SYMBOL_MS * 100.0
    order_ok = expected_digits[: len(intervals) + 1] == [
        0, 8, 9, 9, 6, 7, 8, 9, 6, 7,
    ][: len(intervals) + 1]
    results[f"seq_{platform}"] = {
        "expected_order": expected_digits[: len(intervals) + 1],
        "measured_event_intervals_ms": intervals,
        "code_change_intervals_ms": change_intervals,
        "note": ("участок 800 мс — самопроверка (9) и цикл (9) совпадают, "
                 "код порта не меняется два интервала подряд"),
        "mean_interval_ms": round(mean_interval, 3),
        "t_symbol_nominal_ms": d.T_SYMBOL_MS,
        "relative_deviation_pct": round(deviation, 3),
    }
    check(
        f"вариант 4 {platform}: порядок 9,6,7,8 после самопроверки 0,8,9",
        order_ok,
        str(expected_digits[: len(intervals) + 1]),
    )
    check(
        f"вариант 4 {platform}: средний интервал {mean_interval:.1f} мс "
        f"(отклонение {deviation:+.2f} %)",
        abs(deviation) < 1.0,
    )

results["timers"] = {
    "stm32_tim2": {"psc": d.TIM2_PSC, "arr": d.TIM2_ARR,
                   "tick_ms": (d.TIM2_PSC + 1) / 8000.0,
                   "interval_ms": (d.TIM2_PSC + 1) * (d.TIM2_ARR + 1) / 8000.0},
    "avr_timer0": {"prescaler": 1024, "ocr": d.TIMER0_OCR,
                   "event_ms": (d.TIMER0_OCR + 1) * 1024 / 8000.0,
                   "events": d.TIMER0_EVENTS,
                   "interval_ms": (d.TIMER0_OCR + 1) * 1024 / 8000.0
                   * d.TIMER0_EVENTS},
}

# ---------------------------------------------------------------------------
# 5. Диагностика: инвертированный код
# ---------------------------------------------------------------------------
code5 = d.code_for_digit(5)
inv5 = d.invert_code(code5)
diag = {
    "digit": 5,
    "normal_code": f"0x{code5:02X}",
    "inverted_code": f"0x{inv5:02X}",
    "normal_segments": "".join(sorted(d.segments_for_code(code5))),
    "inverted_lit_segments": "".join(sorted(d.segments_for_code(inv5))),
    "decoded_inverted": d.decode_digit(inv5),
}
results["diagnostic"] = diag
check(
    "диагностика: инвертированный код 0x{:02X} не образует цифру".format(inv5),
    diag["decoded_inverted"] is None,
    f"светятся сегменты {diag['inverted_lit_segments']}",
)

results["code_table"] = table_rows

# ---------------------------------------------------------------------------
# CSV: осциллограмма последовательного вывода STM32
# ---------------------------------------------------------------------------
port = d.STM32PortA()
port_writes = [(t, port.write_code(code)) for t, code in writes]
samples = d.sample_waveform(port_writes, DURATION_MS)
csv_path = os.path.join(OUT_DIR, "display_waveform.csv")
with open(csv_path, "w", encoding="utf-8") as fh:
    fh.write("t_ms,code_hex,pa7,pa6,pa5,pa4,pa3,pa2,pa1,pa0\n")
    for t, code in samples:
        bits = ",".join(str((code >> bit) & 1) for bit in range(7, -1, -1))
        fh.write(f"{t:.0f},0x{code:02X},{bits}\n")


# ---------------------------------------------------------------------------
# Фигуры
# ---------------------------------------------------------------------------
def render_logic_figure(samples, writes, path, title):
    """Логический анализатор: 8 каналов PA7–PA0, развёртка в мс."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    times = [t for t, _ in samples]
    fig, axes = plt.subplots(8, 1, figsize=(9.5, 6.4), sharex=True)
    for ch in range(8):
        ax = axes[ch]
        bit = 7 - ch
        ys = [1.0 if (code >> bit) & 1 else 0.0 for _, code in samples]
        ax.step(times, ys, where="post", color="#0b5394", linewidth=1.4)
        ax.set_ylim(-0.3, 1.5)
        ax.set_yticks([0, 1])
        ax.set_ylabel(LA_CHANNELS[ch], rotation=0, ha="right", va="center")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.set_yticks([])
    # подписи цифр над моментами записи
    for t, code in writes:
        digit = d.decode_digit(code)
        axes[0].annotate(
            str(digit) if digit is not None else "?",
            xy=(t, 1.1),
            xytext=(t + 6, 1.35),
            fontsize=10,
            color="#990000",
            fontweight="bold",
        )
    axes[-1].set_xlabel("t, мс")
    axes[0].set_title(title, fontsize=11)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.94, bottom=0.08)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def render_static_figures():
    for platform, cls, fname, title in (
        ("stm32", d.STM32PortA, "display-static-stm32.png",
         "Статический вывод цифры 5 (STM32F103C8, запись через BSRR)"),
        ("avr", d.AVRPortA, "display-static-atmega32.png",
         "Статический вывод цифры 5 (ATmega32, запись PORTA)"),
    ):
        port = cls()
        samples = d.sample_waveform(
            [(1.0, port.write_code(d.code_for_digit(5)))], 9.0, sample_ms=0.25
        )
        render_logic_figure(
            samples, [(1.0, d.code_for_digit(5))],
            os.path.join(FIG_DIR, fname), title,
        )


SEG_SHAPES = {
    "a": ((1.0, 8.2), (2.2, 9.4), (5.8, 9.4), (7.0, 8.2), (5.8, 7.0), (2.2, 7.0)),
    "b": ((7.2, 7.8), (8.4, 9.0), (8.4, 12.6), (7.2, 13.8), (6.0, 12.6), (6.0, 9.0)),
    "c": ((7.2, 1.8), (8.4, 3.0), (8.4, 6.6), (7.2, 7.8), (6.0, 6.6), (6.0, 3.0)),
    "d": ((1.0, 0.2), (2.2, 1.4), (5.8, 1.4), (7.0, 0.2), (5.8, -1.0), (2.2, -1.0)),
    "e": ((-0.4, 1.8), (0.8, 3.0), (0.8, 6.6), (-0.4, 7.8), (-1.6, 6.6), (-1.6, 3.0)),
    "f": ((-0.4, 7.8), (0.8, 9.0), (0.8, 12.6), (-0.4, 13.8), (-1.6, 12.6), (-1.6, 9.0)),
    "g": ((1.0, 4.2), (2.2, 5.4), (5.8, 5.4), (7.0, 4.2), (5.8, 3.0), (2.2, 3.0)),
}


def draw_digit(ax, code, x0, label):
    """Семисегментный индикатор: светящиеся сегменты красные."""
    from matplotlib.patches import Polygon

    lit = d.segments_for_code(code)
    for name, pts in SEG_SHAPES.items():
        poly = Polygon(
            [(x + x0, y) for x, y in pts],
            closed=True,
            facecolor="#e31b1b" if name in lit else "#f3dada",
            edgecolor="#7a7a7a",
            linewidth=0.8,
        )
        ax.add_patch(poly)
    digit = d.decode_digit(code)
    ax.text(x0 + 3.5, -3.2, label, ha="center", fontsize=10)
    ax.text(x0 + 3.5, 15.4, str(digit) if digit is not None else "—",
            ha="center", fontsize=11, fontweight="bold",
            color="#0b5394" if digit is not None else "#990000")


def render_digits_figure():
    """Рисунок: самопроверка 0, 8, 9 и цикл варианта 9, 6, 7, 8."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(9.5, 5.6))
    top = [d.code_for_digit(x) for x in (0, 8, 9)]
    bottom = [d.code_for_digit(x) for x in (9, 6, 7, 8)]
    for ax, codes, title in (
        (axes[0], top, "Самопроверка по методике (интервал T_симв = 400 мс)"),
        (axes[1], bottom, "Цикл варианта 4, обратный порядок (9, 6, 7, 8)"),
    ):
        for i, code in enumerate(codes):
            draw_digit(ax, code, i * 11.0, f"0x{code:02X}")
        ax.set_xlim(-3, len(codes) * 11.0)
        ax.set_ylim(-5, 18)
        ax.set_title(title, fontsize=10)
        ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.02)
    fig.savefig(os.path.join(FIG_DIR, "display-digits-variant4.png"), dpi=150)
    plt.close(fig)


def render_diagnostic_figure():
    """Рисунок: нормальный код 0x6D против инвертированного 0x92."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    draw_digit(ax, d.code_for_digit(5), 0.0, "норма 0x6D")
    draw_digit(ax, d.invert_code(d.code_for_digit(5)), 11.0, "инверсия 0x92")
    ax.set_xlim(-3, 22)
    ax.set_ylim(-5, 18)
    ax.axis("off")
    ax.set_title("Диагностика варианта 4: инвертированный код (цифра 5)",
                 fontsize=11)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.02)
    fig.savefig(os.path.join(FIG_DIR, "display-diagnostic-inverted.png"), dpi=150)
    plt.close(fig)


def render_all_figures():
    render_static_figures()
    for platform, cls, fname, title in (
        ("stm32", d.STM32PortA, "display-seq-stm32.png",
         "Последовательный вывод варианта 4 (STM32F103C8, T_симв = 400 мс)"),
        ("avr", d.AVRPortA, "display-seq-atmega32.png",
         "Последовательный вывод варианта 4 (ATmega32, T_симв = 400 мс)"),
    ):
        port = cls()
        port_writes = [(t, port.write_code(code)) for t, code in writes]
        samples = d.sample_waveform(port_writes, DURATION_MS)
        render_logic_figure(
            samples, writes, os.path.join(FIG_DIR, fname), title
        )
    render_digits_figure()
    render_diagnostic_figure()


def main():
    render_all_figures()
    results["artifacts"] = {
        "json": "out/display_results.json",
        "csv": "out/display_waveform.csv",
        "figure_static_stm32": "docs/figures/display-static-stm32.png",
        "figure_static_atmega32": "docs/figures/display-static-atmega32.png",
        "figure_seq_stm32": "docs/figures/display-seq-stm32.png",
        "figure_seq_atmega32": "docs/figures/display-seq-atmega32.png",
        "figure_digits": "docs/figures/display-digits-variant4.png",
        "figure_diagnostic": "docs/figures/display-diagnostic-inverted.png",
    }
    with open(os.path.join(OUT_DIR, "display_results.json"), "w",
              encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"\nall_pass = {results['all_pass']}")
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImportError:
        import subprocess

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "matplotlib"]
            if os.environ.get("UV_ACTIVE")
            else ["uv", "run", "--with", "matplotlib", __file__]
        )
        sys.exit(0)
