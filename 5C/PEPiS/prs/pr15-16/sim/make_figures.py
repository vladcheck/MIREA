# -*- coding: utf-8 -*-
"""Построение осциллограмм ШИМ на выводе P1.0 по результатам модели.

Читает out/pwm_waveform_<name>.csv (из pwm_model.py) и строит
«экран осциллографа» в стиле стендовых снимков: ступенчатая форма
сигнала, разметка периода и длительности высокого уровня, таблица
измеренных значений. Файлы сохраняются в docs/figures/.

Запуск:  python sim/make_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
FIGURES = BASE / "docs" / "figures"
RESULTS = BASE / "out" / "pwm_results.json"

import json


def load_waveform(name):
    import csv
    t, v = [], []
    with open(BASE / "out" / ("pwm_waveform_%s.csv" % name),
              encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            t.append(float(row["t_s"]))
            v.append(int(row["p1_0"]))
    return t, v


def draw(name, fig_name):
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    row = next(r for r in data["results"] if r["name"] == name)
    t, v = load_waveform(name)
    meas = row["measured"]

    fig, ax = plt.subplots(figsize=(8.6, 4.2), dpi=150)
    ax.plot([x * 1e3 for x in t], v, drawstyle="steps-post",
            color="#0b3d91", linewidth=1.6)

    # разметка периода (между первым и вторым передним фронтами)
    rising = [i for i in range(1, len(v)) if v[i] == 1 and v[i - 1] == 0]
    t1, t2 = t[rising[0]] * 1e3, t[rising[1]] * 1e3
    y = 1.13
    ax.annotate("", xy=(t1, y), xytext=(t2, y),
                arrowprops=dict(arrowstyle="<->", color="#b00000", lw=1.2))
    ax.text((t1 + t2) / 2, y + 0.035,
            "T = %.3f мс" % (meas["period_s"] * 1e3),
            ha="center", fontsize=10, color="#b00000")

    # разметка длительности высокого уровня первого импульса
    i_fall = next(i for i in range(rising[0] + 1, len(v)) if v[i] == 0)
    tf = t[i_fall] * 1e3
    ylow = -0.16
    ax.annotate("", xy=(t1, ylow), xytext=(tf, ylow),
                arrowprops=dict(arrowstyle="<->", color="#008000", lw=1.2))
    ax.text((t1 + tf) / 2, ylow - 0.11,
            "t = %.3f мс" % (meas["high_s"] * 1e3),
            ha="center", fontsize=10, color="#008000")

    ax.set_ylim(-0.35, 1.32)
    ax.set_yticks([0, 1])
    ax.set_ylabel("P1.0, В")
    ax.set_xlabel("t, мс")
    ax.set_xlim(0, max(x * 1e3 for x in t))
    ax.grid(True, linestyle=":", linewidth=0.6, alpha=0.7)
    ax.set_title("%s: Fosc = %.3f МГц, RCAP2 = %s, tmpCnt = %d; "
                 "измерено Q = %.2f %%" % (
                     row["title"], row["fosc_hz"] / 1e6,
                     row["expected"]["reload_hex"], row["tmp_cnt"],
                     meas["duty_pct"]),
                 fontsize=10.5)
    fig.tight_layout()
    fig.savefig(FIGURES / fig_name)
    plt.close(fig)
    print("wrote %s" % fig_name)


if __name__ == "__main__":
    FIGURES.mkdir(parents=True, exist_ok=True)
    draw("example", "pwm-example.png")
    draw("variant4", "pwm-variant4.png")
