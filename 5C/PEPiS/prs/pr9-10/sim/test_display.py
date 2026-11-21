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

Артефакты: out/display_results.json, out/display_waveform.csv.
Код выхода 0 только если все проверки прошли.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import display as d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")
os.makedirs(OUT_DIR, exist_ok=True)

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
# Сохранение результатов
# ---------------------------------------------------------------------------
def test_all_checks_passed():
    """Все проверки модуля (выполняются при импорте) завершились успехом."""
    assert results["all_pass"], results["checks"]


def main():
    results["artifacts"] = {
        "json": "out/display_results.json",
        "csv": "out/display_waveform.csv",
    }
    with open(os.path.join(OUT_DIR, "display_results.json"), "w",
              encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"\nall_pass = {results['all_pass']}")
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
