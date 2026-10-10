#!/usr/bin/env python3
"""Модель передачи Вар.1 (режим 0, 1 МГц): проверка скорости и осциллограмма."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"

FOSC = 12e6
F0 = FOSC / 12          # 1 МГц
TBIT = 1 / F0           # 1 мкс
DATA = list(range(10))  # 00h..09h с 50h
TBYTE = 8 * TBIT        # 8 мкс
TTOTAL = len(DATA) * TBYTE

print(f"fosc=12 МГц, f0={F0/1e3:.0f} Кбит/с, Tbit={TBIT*1e6:.1f} мкс, "
      f"Tbyte={TBYTE*1e6:.0f} мкс, N=10 -> {TTOTAL*1e6:.0f} мкс")
assert abs(F0 - 1e6) < 1, "скорость обязана быть 1000 Кбит/с"
assert len(DATA) == 10

# Осциллограмма: P3.0 данные (LSB first) + P3.1 синхроимпульсы
t, d, c = [], [], []
tt = 0.0
for byte in DATA:
    for k in range(8):
        bit = (byte >> k) & 1
        t += [tt, tt + TBIT * 0.999]
        d += [bit, bit]
        c += [0, 0]  # фронт синхро в начале бита
        c[-2:] = [1, 1]
        c[-1] = 0
        tt += TBIT
        t.append(tt); d.append(bit); c.append(0)

fig, ax = plt.subplots(2, 1, figsize=(12, 4), sharex=True)
ax[0].step([x * 1e6 for x in t], d, where="post")
ax[0].set_ylabel("P3.0\nданные"); ax[0].set_ylim(-0.2, 1.2); ax[0].grid(True, alpha=0.3)
ax[0].set_title("ПР4 Вар.1: режим 0, 1 МГц — P3.0 (данные) и P3.1 (синхро), 10 байт 00h..09h (50h..59h)")
ax[1].step([x * 1e6 for x in t], c, where="post", color="tab:orange")
ax[1].set_ylabel("P3.1\nсинхро"); ax[1].set_xlabel("мкс"); ax[1].set_ylim(-0.2, 1.2); ax[1].grid(True, alpha=0.3)
fig.tight_layout()
OUT.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT / "serial_mode0_waveform.png", dpi=150)
print("WAVEFORM: out/serial_mode0_waveform.png")

res = {"variant": 1, "mode": 0, "fosc_MHz": 12, "f0_kbps": 1000,
       "Tbit_us": 1.0, "Tbyte_us": 8.0, "N": 10, "Ttotal_us": 80.0,
       "XX": "50h", "SCON": "0x00", "status": "PASS"}
(OUT / "serial_results.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
print("RESULTS: out/serial_results.json PASS")
