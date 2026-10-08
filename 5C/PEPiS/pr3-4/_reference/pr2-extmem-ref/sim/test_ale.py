#!/usr/bin/env python3
"""Осциллограмма ALE: 2 импульса за машинный цикл, 1 мкс/дел, 5 В/дел (рис.28)."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sim"))
from mcu8051_bus import ExtMemSystem


def main() -> int:
    s = ExtMemSystem()
    pts = s.gen_ale(machine_cycles=4, f_osc_mhz=12.0)
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    with open(out / "ale_waveform.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_us", "ALE_V"])
        for t, lvl in pts:
            w.writerow([t, 5 if lvl else 0])
    # проверки по ТЗ: длительность 4 мкс, 8 импульсов (2 на цикл), уровни 0/5В
    dur = pts[-1][0] - pts[0][0]
    # число высоких плато = число импульсов (первое плато в t=0 тоже считается)
    rising = sum(1 for i, (t, l) in enumerate(pts) if l == 1 and (i == 0 or pts[i - 1][1] == 0))
    levels = {v for _, v in pts}
    ok = abs(dur - 4.0) < 1e-9 and rising == 8 and levels == {0, 1}
    print(f"ALE: машинных циклов=4, длительность={dur} мкс, фронтов вверх={rising} (ожидалось 8), уровни={sorted(levels)}")
    # PNG через matplotlib (если есть), иначе ASCII
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ts = [t for t, _ in pts]
        vs = [5 * v for _, v in pts]
        plt.figure(figsize=(8, 3))
        plt.step(ts, vs, where="post")
        plt.ylim(-1, 6)
        plt.xlim(0, 4)
        plt.xlabel("t, мкс (1 мкс/дел = 1 машинный цикл)")
        plt.ylabel("ALE, В (5 В/дел)")
        plt.title("ALE МК-51: 2 импульса за машинный цикл (12 МГц)")
        plt.grid(True)
        plt.savefig(out / "ale_oscillogram.png", dpi=120)
        print(f"PNG: {out / 'ale_oscillogram.png'}")
    except Exception as e:  # noqa: BLE001
        print(f"matplotlib недоступен ({e}), PNG пропущен — CSV достаточно для отчёта")
    # ASCII-превью для отчёта
    asc = []
    for t, lvl in pts:
        asc.append(f"{t:5.2f} мкс | {'████' if lvl else '    '} ({5 if lvl else 0}В)")
    (out / "ale_ascii.txt").write_text("\n".join(asc), encoding="utf-8")
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
