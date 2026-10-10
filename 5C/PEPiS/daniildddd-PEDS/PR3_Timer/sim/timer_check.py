#!/usr/bin/env python3
"""Проверка расчёта таймера ПР №3, Вариант 1 (и всех вариантов табл.10).
Без железа: арифметика перезагрузки + счётчики циклов + электрика LED.
Выход: PASS/FAIL + out/timer_results.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

FOSC = 12_000_000
T_MACH = 12 / FOSC  # 1мкс
BASE_MS = 50
COUNTS = int(BASE_MS * 1000 / (T_MACH * 1e6))  # 50000
RELOAD = 65536 - COUNTS
TH0, TL0 = (RELOAD >> 8) & 0xFF, RELOAD & 0xFF

print(f"Fosc=12МГц, Tмаш=1мкс, база={BASE_MS}мс -> счетов={COUNTS}, reload={RELOAD}=0x{RELOAD:04X}")
assert COUNTS == 50000, COUNTS
assert (TH0, TL0) == (0x3C, 0xB0), (hex(TH0), hex(TL0))
print(f"TH0=0x{TH0:02X}, TL0=0x{TL0:02X} OK")

variants = json.loads((ROOT / "variants.json").read_text(encoding="utf-8"))["variants"]
results = {"th0": f"0x{TH0:02X}", "tl0": f"0x{TL0:02X}", "base_ms": BASE_MS, "variants": []}
all_ok = True
for v in variants:
    s_ms = int(v["S_s"] * 1000)
    k_ms = int(v["K_s"] * 1000)
    n_on, n_off = v["N_on"], v["N_off"]
    ok_on = (n_on * BASE_MS == s_ms)
    ok_off = (n_off * BASE_MS == k_ms)
    period_ms = s_ms + k_ms
    total_ms = v["cycles"] * period_ms
    target_ms = int(v["T_min"] * 60 * 1000)
    # для вариантов с остатком (8,9,10) cycles усечены — фиксируем остаток
    rem = target_ms - total_ms
    ok = ok_on and ok_off and (0 <= rem < period_ms)
    all_ok &= ok
    results["variants"].append({
        "variant": v["variant"], "pxy": v["pxy"],
        "S_ms": s_ms, "K_ms": k_ms, "N_on": n_on, "N_off": n_off,
        "cycles": v["cycles"], "total_ms": total_ms, "target_ms": target_ms,
        "remainder_ms": rem, "ok": ok,
    })
    print(f"Вар.{v['variant']:2d} {v['pxy']:5s} S={v['S_s']}с({n_on}x50мс) K={v['K_s']}с({n_off}x50мс) "
          f"T={v['T_min']}мин cycles={v['cycles']} total={total_ms/1000:.1f}с rem={rem}мс -> {'PASS' if ok else 'FAIL'}")

# Электрика цепи HL1 (Вар.1): P1.3=1 (5В) -> R1 270 Ом -> HL1 (Vf~2В) -> GND
VCC, VF, R = 5.0, 2.0, 270.0
I = (VCC - VF) / R  # А
P_R = I * I * R
print(f"\nLED: I=({VCC}-{VF})/{R}={I*1000:.1f}мА, P_R={P_R*1000:.1f}мВт")
print(f"Ожидания мультиметра: V_HL1~{VF}В (1.66..2.2В по типу), I~{I*1000:.1f}мА (10..12мА)")
assert 0.008 <= I <= 0.015, I  # 8..15мА — рабочий диапазон красного LED через 270 Ом
results["led"] = {"Vcc": VCC, "Vf": VF, "R": R, "I_mA": round(I*1000, 2), "P_R_mW": round(P_R*1000, 1)}

(OUT / "timer_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n{'ALL PASS' if all_ok else 'FAILURES PRESENT'} -> {OUT/'timer_results.json'}")
raise SystemExit(0 if all_ok else 1)
