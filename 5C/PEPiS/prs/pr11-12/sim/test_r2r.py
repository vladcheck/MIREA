# -*- coding: utf-8 -*-
"""Тесты и расчёты модели R-2R для ПР 11-12 (вариант 4).

Сценарии (по пунктам 7-9 методички):
  1. Общая часть: коды 0, 64, 128, 192, 255; UH, q, расчёт по формуле
     Uвых = UH*D/256 и расчёт узловой моделью лестницы.
  2. Индивидуальная часть: коды 76, 133, 207; пила 0..255 с шагом 10 мс,
     пять расчётных периодов.
  3. Диагностика: отключение завершающего 2R, расчёт передадочной
     характеристики 0..255 до и после изменения.

Результаты: out/r2r_results.json, out/r2r_ramp_waveform.csv.

Запуск:
    python3 sim/test_r2r.py
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from r2r_ladder import (  # noqa: E402
    R2_OHM, R_METER_OHM, R_OHM, R_OUT_OHM, T_STEP_MS, UH_V,
    bit_string, measure_periods, q_step, ramp_waveform,
    solve_ladder, u_calc,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")
os.makedirs(OUT_DIR, exist_ok=True)

GENERAL_CODES = [0, 64, 128, 192, 255]
VARIANT_CODES = [76, 133, 207]  # вариант 4, таблица 9.35
T_CALC_MS = 256.0 * T_STEP_MS  # 2560 мс

CHECKS = []


def check(name, ok, detail=""):
    """Фиксирует результат одной проверки и печатает строку отчёта."""
    CHECKS.append((name, ok, detail))
    print(f"[{'OK' if ok else 'FAIL'}] {name} {detail}")
    return ok


# ---------------------------------------------------------------------------
# Сценарии модели
# ---------------------------------------------------------------------------
def run_scenarios():
    """Все расчёты модели. Возвращает словарь с данными сценариев."""
    data = {
        "params": {
            "uh_v": UH_V,
            "q_mv": q_step() * 1e3,
            "r_ohm": R_OHM,
            "r2_ohm": R2_OHM,
            "r_out_ohm": R_OUT_OHM,
            "r_meter_ohm": R_METER_OHM,
            "t_step_ms": T_STEP_MS,
            "t_calc_ms": T_CALC_MS,
            "supply_v": 3.3,
        },
        "general": [],
        "variant": [],
        "ramp": {},
        "diagnostic": {},
    }

    for code in GENERAL_CODES:
        u_c = u_calc(code)
        u_m = solve_ladder(code)
        data["general"].append({
            "code": code,
            "bits": bit_string(code),
            "u_calc_v": u_c,
            "u_meas_v": u_m,
            "abs_delta_v": abs(u_c - u_m),
        })

    for code in VARIANT_CODES:
        u_c = u_calc(code)
        u_m = solve_ladder(code)
        data["variant"].append({
            "code": code,
            "bits": bit_string(code),
            "u_calc_v": u_c,
            "u_meas_v": u_m,
            "abs_delta_v": abs(u_c - u_m),
        })

    samples, wrap_times = ramp_waveform(periods=6)
    periods, avg = measure_periods(wrap_times[:6])
    data["ramp"] = {
        "wrap_times_ms": wrap_times[:6],
        "periods_ms": periods[:5],
        "t_avg_ms": avg,
        "t_calc_ms": T_CALC_MS,
        "deviation_pct": (avg - T_CALC_MS) / T_CALC_MS * 100.0,
        "samples": samples,
    }

    nominal = [solve_ladder(d) for d in range(256)]
    opened = [solve_ladder(d, terminated=False) for d in range(256)]
    data["diagnostic"] = {
        "nominal_curve": nominal,
        "opened_curve": opened,
        "points": [],
    }
    for code in VARIANT_CODES + [255, 128, 1]:
        n = nominal[code]
        o = opened[code]
        data["diagnostic"]["points"].append({
            "code": code,
            "u_nominal_v": n,
            "u_open_v": o,
            "delta_v": o - n,
            "rel_delta_pct": (o - n) / n * 100.0 if n > 0 else None,
        })
    # Проверка монотонности обеих характеристик.
    data["diagnostic"]["nominal_monotonic"] = all(
        nominal[d + 1] > nominal[d] for d in range(255))
    drops = [d for d in range(255) if opened[d + 1] < opened[d]]
    data["diagnostic"]["opened_drops"] = drops
    # Максимальное отклонение от прямой через ноль и точку 255.
    full = opened[255]
    max_inl = max(abs(opened[d] - full * d / 255.0) for d in range(256))
    data["diagnostic"]["opened_max_inl_v"] = max_inl
    return data


# ---------------------------------------------------------------------------
# Проверки
# ---------------------------------------------------------------------------
def test_model_checks():
    """Все проверки модели под pytest."""
    data = run_scenarios()
    assert run_checks(data)


def run_checks(data):
    g = {e["code"]: e for e in data["general"]}
    check("Uвых(0) = 0", g[0]["u_meas_v"] < 1e-9,
          f"{g[0]['u_meas_v']:.6f} В")
    # Максимум ниже UH на один шаг и ещё на падение на нагрузке
    # вольтметра (вход 10 МОм против выходного сопротивления R матрицы).
    u255_exp = UH_V * 255 / 256 - UH_V / R_METER_OHM * R_OHM
    check("Uвых(255) ниже UH на шаг с учётом нагрузки вольтметра",
          abs(g[255]["u_meas_v"] - u255_exp) < 0.5e-3,
          f"{g[255]['u_meas_v']:.6f} В (ожидание {u255_exp:.6f} В)")
    check("Монотонность общей части",
          all(g[c1]["u_meas_v"] < g[c2]["u_meas_v"]
              for c1, c2 in zip(GENERAL_CODES, GENERAL_CODES[1:])),
          "")
    for e in data["general"] + data["variant"]:
        check(f"|Uформулы-Uмодели| < 5 мВ при D = {e['code']}",
              e["abs_delta_v"] < 5e-3, f"{e['abs_delta_v'] * 1e3:.3f} мВ")
    periods = data["ramp"]["periods_ms"]
    check("Получено пять полных расчётных периодов", len(periods) == 5, "")
    check("Все периоды равны расчётным 2560 мс с точностью 1 мс",
          all(abs(p - T_CALC_MS) <= 1.0 for p in periods),
          ", ".join(f"{p:.1f}" for p in periods))
    check("Средний период отличается от расчёта менее чем на 0.1 %",
          abs(data["ramp"]["deviation_pct"]) < 0.1,
          f"{data['ramp']['deviation_pct']:.4f} %")
    diag = data["diagnostic"]
    check("Исправная характеристика монотонна", diag["nominal_monotonic"], "")
    check("Без завершающего 2R U(255) приближается к UH",
          abs(diag["opened_curve"][255] - UH_V) < 5e-3,
          f"{diag['opened_curve'][255]:.6f} В")
    check("Без завершающего 2R U(255) выше номинального более чем на 5 мВ",
          diag["opened_curve"][255] - diag["nominal_curve"][255] > 5e-3,
          f"на {(diag['opened_curve'][255] - diag['nominal_curve'][255]) * 1e3:.1f} мВ")
    check("Без завершающего 2R есть отклонения от прямой более 10 мВ",
          diag["opened_max_inl_v"] > 10e-3,
          f"max {diag['opened_max_inl_v'] * 1e3:.1f} мВ")
    return all(ok for _, ok, _ in CHECKS)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    data = run_scenarios()
    all_pass = run_checks(data)

    # CSV осциллограммы пилы (первые 2.5 периода, шаг 0.5 мс).
    csv_path = os.path.join(OUT_DIR, "r2r_ramp_waveform.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["t_ms", "code", "u_out_v"])
        for t_ms, code, u_v in data["ramp"]["samples"]:
            if t_ms <= 2.6 * T_CALC_MS:
                wr.writerow([f"{t_ms:.1f}", code, f"{u_v:.6f}"])

    json_data = {
        "params": data["params"],
        "general": data["general"],
        "variant": data["variant"],
        "ramp": {k: v for k, v in data["ramp"].items() if k != "samples"},
        "diagnostic": {
            k: v for k, v in data["diagnostic"].items()
            if k not in ("nominal_curve", "opened_curve")
        },
    }
    json_path = os.path.join(OUT_DIR, "r2r_results.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(json_data, fh, ensure_ascii=False, indent=2)

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
