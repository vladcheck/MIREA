#!/usr/bin/env python3
"""Расчёт Uвых идеального 8-бит ЦАП для ЛР №6, Вар.1. Uвых = D*Uref/255."""
import csv, json
UREF = 5.0
CODES = [8, 36, 107]
rows = []
for d in CODES:
    u = d * UREF / 255.0
    rows.append({"code_dec": d, "code_hex": f"0x{d:02X}",
                 "code_bin": f"{d:08b}", "u_v": round(u, 4)})
    print(f"D={d:3d} 0x{d:02X} {d:08b} -> {u:.4f} В")
zmr = UREF / 255.0
print(f"ЗМР = {zmr*1000:.1f} мВ; Umax(255) = {255*UREF/255:.3f} В")
with open("out/results.json", "w", encoding="utf-8") as f:
    json.dump({"uref": UREF, "zmr_v": round(zmr, 6), "rows": rows},
              f, ensure_ascii=False, indent=2)
with open("out/results.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["code_dec", "code_hex", "code_bin", "u_v"])
    w.writeheader(); w.writerows(rows)
print("OK: out/results.json, out/results.csv")
