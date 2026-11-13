# -*- coding: utf-8 -*-
"""Тесты и построение диаграмм модели R-2R для ПР 11-12 (вариант 4).

Сценарии (по пунктам 7-9 методички):
  1. Общая часть: коды 0, 64, 128, 192, 255; UH, q, расчёт и измерение
     Uвых; диаграммы Logic Analyzer (D7..D0) и ступенчатая осциллограмма.
  2. Индивидуальная часть: коды 76, 133, 207; пила 0..255 с шагом 10 мс,
     пять измеренных периодов.
  3. Диагностика: отключение завершающего 2R, передадочная
     характеристика 0..255 до и после изменения.

Результаты: out/r2r_results.json, out/r2r_ramp_waveform.csv,
docs/figures/r2r-*.png.

Запуск:
    uv run --with matplotlib python sim/test_r2r.py
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from r2r_ladder import (  # noqa: E402
    N_BITS, R2_OHM, R_METER_OHM, R_OHM, R_OUT_OHM, T_STEP_MS, UH_V,
    bit_string, dwell_waveform, measure_periods, q_step, ramp_waveform,
    solve_ladder, u_calc,
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")
FIG_DIR = os.path.join(ROOT, "docs", "figures")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

GENERAL_CODES = [0, 64, 128, 192, 255]
VARIANT_CODES = [76, 133, 207]  # вариант 4, таблица 9.35
DWELL_MS = 2000
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
# Рисунки
# ---------------------------------------------------------------------------
def render_general_logic_figure(data, path):
    """Рисунок 1: Logic Analyzer, коды 0, 64, 128, 192, 255 (общая часть)."""
    samples = dwell_waveform(GENERAL_CODES, DWELL_MS, dt_ms=5.0, lead_ms=500.0)
    t = [s[0] / 1000.0 for s in samples]
    fig, axes = plt.subplots(N_BITS + 1, 1, figsize=(11, 7.5),
                             sharex=True,
                             gridspec_kw={"height_ratios": [2] + [1] * N_BITS})
    ax = axes[0]
    u = [solve_ladder(s[1]) for s in samples]
    ax.plot(t, u, color="#009E73", lw=1.4)
    ax.set_ylabel("Uвых, В")
    ax.set_ylim(-0.15, UH_V + 0.25)
    ax.grid(alpha=0.3)
    for k, code in enumerate(GENERAL_CODES):
        x = (500.0 + DWELL_MS * k + DWELL_MS / 2) / 1000.0
        ax.annotate(f"D = {code}", (x, u_calc(code)), fontsize=9,
                    ha="center", va="bottom", color="#00563f")
    ax.set_title("Ступенчатая последовательность кодов 0, 64, 128, 192, 255 "
                 "(осциллограф, канал VOUT)")
    for bit in range(N_BITS):
        ax = axes[N_BITS - bit]
        lvl = [((s[1] >> bit) & 1) * 0.9 for s in samples]
        ax.fill_between(t, 0, lvl, step="post", color="#0072B2", alpha=0.85)
        ax.set_ylabel(f"D{bit}", rotation=0, ha="right", va="center")
        ax.set_yticks([])
        ax.set_ylim(0, 1.2)
    axes[-1].set_xlabel("t, с")
    axes[-1].set_xlim(0, t[-1])
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_general_table_figure(data, path):
    """Рисунок 2: измеренные уровни общей части против расчётных."""
    codes = [g["code"] for g in data["general"]]
    u_c = [g["u_calc_v"] for g in data["general"]]
    u_m = [g["u_meas_v"] for g in data["general"]]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    w = 8
    ax.bar([c - w for c in codes], u_c, width=w * 1.7, label="Uрасч = UH*D/256",
           color="#999999")
    ax.bar([c + w for c in codes], u_m, width=w * 1.7, label="Uизм (модель)",
           color="#0072B2")
    for c, uc, um in zip(codes, u_c, u_m):
        ax.annotate(f"{um:.4f}", (c + w, um), fontsize=8, ha="center",
                    va="bottom", color="#00527a")
    ax.set_xlabel("Код D")
    ax.set_ylabel("Uвых, В")
    ax.set_xticks(codes)
    ax.set_ylim(0, UH_V + 0.3)
    ax.grid(alpha=0.3, axis="y")
    ax.legend()
    ax.set_title("Общая часть: расчётные и измеренные выходные напряжения")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_variant_codes_figure(data, path):
    """Рисунок 3: удержание кодов 76, 133, 207 (индивидуальная часть)."""
    samples = dwell_waveform(VARIANT_CODES, DWELL_MS, dt_ms=2.0, lead_ms=200.0)
    t = [s[0] / 1000.0 for s in samples]
    u = [solve_ladder(s[1]) for s in samples]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t, u, color="#D55E00", lw=1.6)
    ax.grid(alpha=0.3)
    ax.set_xlabel("t, с")
    ax.set_ylabel("Uвых, В")
    ax.set_ylim(0, UH_V + 0.15)
    for k, g in enumerate(data["variant"]):
        x = (200.0 + DWELL_MS * k + DWELL_MS / 2) / 1000.0
        ax.annotate(
            f"D = {g['code']}\nUрасч = {g['u_calc_v']:.4f} В\n"
            f"Uизм = {g['u_meas_v']:.4f} В",
            (x, g["u_meas_v"]), fontsize=9, ha="center", va="bottom",
            color="#7a3200")
    ax.set_title("Индивидуальный вариант 4: коды 76, 133, 207")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_ramp_figure(data, path):
    """Рисунок 4: пила 0..255, шаг 10 мс, пять измеренных периодов."""
    samples = data["ramp"]["samples"]
    t = [s[0] / 1000.0 for s in samples]
    u = [s[2] for s in samples]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.5))
    ax1.plot(t, u, color="#0072B2", lw=0.8)
    ax1.grid(alpha=0.3)
    ax1.set_ylabel("Uвых, В")
    ax1.set_title("Пилообразный сигнал 0..255, Tш = 10 мс "
                  "(не менее двух полных периодов)")
    ax1.set_ylim(0, UH_V + 0.15)
    wraps = [w / 1000.0 for w in data["ramp"]["wrap_times_ms"][:6]]
    for i, w in enumerate(wraps[1:6], start=1):
        ax1.annotate(f"T{i}", (w - 1.28, UH_V * 0.93), fontsize=9,
                     ha="center", color="#b3001f")
        ax1.axvline(w, color="#b3001f", ls=":", lw=0.9)
    ax1.annotate(f"Umax = {solve_ladder(255):.4f} В",
                 (wraps[0] + 0.2, UH_V * 0.9),
                 fontsize=9, color="#00527a")
    # Нижняя панель: один период крупно.
    t0, t1 = wraps[0], wraps[1]
    seg = [(tt, uu) for tt, uu in zip(t, u) if t0 - 0.1 <= tt <= t1 + 0.1]
    ax2.plot([tt - t0 for tt, _ in seg], [uu for _, uu in seg],
             color="#0072B2", lw=1.0)
    ax2.set_xlabel("t, с (от начала периода)")
    ax2.set_ylabel("Uвых, В")
    ax2.set_title("Один период: 256 ступеней, код 255 переходит в код 0")
    ax2.grid(alpha=0.3)
    ax2.set_xlim(0, t1 - t0)
    ax2.set_ylim(0, UH_V + 0.15)
    ax2.annotate("переход 255 -> 0", (t1 - t0, 0.02), fontsize=9, ha="right",
                 color="#b3001f")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_diagnostic_figure(data, path):
    """Рисунок 5: передадочная характеристика до и после отключения 2R."""
    nominal = data["diagnostic"]["nominal_curve"]
    opened = data["diagnostic"]["opened_curve"]
    d = list(range(256))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5))
    ax1.plot(d, nominal, color="#0072B2", lw=1.2, label="исправная матрица")
    ax1.plot(d, opened, color="#D55E00", lw=1.2,
             label="завершающий 2R отключён")
    ax1.set_xlabel("Код D")
    ax1.set_ylabel("Uвых, В")
    ax1.grid(alpha=0.3)
    ax1.legend()
    ax1.set_title("Передадочная характеристика ЦАП 0..255")
    err = [(opened[k] - UH_V * k / 255.0) * 1e3 for k in d]
    ax2.plot(d, err, color="#D55E00", lw=1.0)
    ax2.axhline(0, color="#555555", lw=0.8)
    ax2.set_xlabel("Код D")
    ax2.set_ylabel("Отклонение от прямой, мВ")
    ax2.grid(alpha=0.3)
    ax2.set_title("Нелинейность характеристики без завершающего 2R")
    for g in data["diagnostic"]["points"]:
        if g["code"] in (76, 133, 207):
            ax1.annotate(str(g["code"]), (g["code"], g["u_open_v"]),
                         fontsize=9, color="#7a3200", ha="center")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_all_figures(data):
    render_general_logic_figure(
        data, os.path.join(FIG_DIR, "r2r-general-logic.png"))
    render_general_table_figure(
        data, os.path.join(FIG_DIR, "r2r-general-table.png"))
    render_variant_codes_figure(
        data, os.path.join(FIG_DIR, "r2r-variant-codes.png"))
    render_ramp_figure(data, os.path.join(FIG_DIR, "r2r-ramp-variant4.png"))
    render_diagnostic_figure(
        data, os.path.join(FIG_DIR, "r2r-diagnostic-open2r.png"))


# ---------------------------------------------------------------------------
# Проверки
# ---------------------------------------------------------------------------
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
        check(f"|Uрасч-Uизм| < 5 мВ при D = {e['code']}",
              e["abs_delta_v"] < 5e-3, f"{e['abs_delta_v'] * 1e3:.3f} мВ")
    periods = data["ramp"]["periods_ms"]
    check("Измерено пять полных периодов", len(periods) == 5, "")
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

    render_all_figures(data)
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
