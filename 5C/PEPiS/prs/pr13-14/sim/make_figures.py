# -*- coding: utf-8 -*-
"""Генерация иллюстраций отчёта (практика 13-14).

Запуск из корня pr13-14:
    ~/.local/share/agentpipe/gost-report/venv/bin/python sim/make_figures.py

Фигуры сохраняются в docs/figures/:
  adc-timing.png           — диаграмма синхронизации АЦП (V4, SOC, OE, EOC);
  adc-transfer-variant4.png— статическая характеристика и погрешность квантования
                             16-разрядного АЦП варианта 4;
  adc-probes-variant4.png  — показания пробников Х0…Х15 для трёх точек задания 2.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from adc import (
    T_CONV_US,
    T_SETTLE_US,
    V4_FREQ_HZ,
    V4_HIGH,
    V4_LOW,
    VARIANT4_BITS,
    VARIANT4_INPUTS_V,
    VARIANT4_MCU_INPUTS_V,
    VARIANT4_VREF_M,
    VARIANT4_VREF_P,
    dac_voltage,
    investigation_table,
    lsb_voltage,
    mcu_read_code,
    quantize,
)

BASE = Path(__file__).resolve().parent.parent
FIG = BASE / "docs" / "figures"

LSB = lsb_voltage(VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS)
PERIOD_US = 1e6 / V4_FREQ_HZ


def _stairs(ax, segments):
    """Отрисовка цифрового сигнала по участкам [(t0, t1, уровень), ...]."""
    for t0, t1, lvl in segments:
        ax.plot([t0, t1, t1], [lvl, lvl, None], color="C0", lw=1.6,
                solid_capstyle="butt")
        ax.plot([t1, t1], [lvl, None], color="C0", lw=0)  # заглушка
    # корректные вертикальные перепады
    for (t0a, t1a, la), (t0b, t1b, lb) in zip(segments, segments[1:]):
        ax.plot([t1a, t0b], [la, lb], color="C0", lw=1.6)


def _draw_signal(ax, segments, y_hi, y_lo, label):
    for i, (t0, t1, lvl) in enumerate(segments):
        ax.plot([t0, t1], [lvl, lvl], color="C0", lw=1.6,
                solid_capstyle="butt")
        if i + 1 < len(segments):
            t_next, _lvl_next = segments[i + 1][0], segments[i + 1][2]
            ax.plot([t1, t_next], [lvl, segments[i + 1][2]], color="C0", lw=1.6)
    ax.set_ylim(y_lo - 0.7, y_hi + 0.9)
    ax.set_yticks([y_lo, y_hi])
    ax.set_ylabel(label, rotation=0, ha="right", va="center")
    ax.grid(True, axis="x", ls=":", alpha=0.5)
    ax.set_yticklabels(["0", "5 В"])


def fig_timing():
    """Диаграмма синхронизации виртуального АЦП (рис. 58 методички)."""
    t_conv = T_CONV_US
    t_valid = T_CONV_US + T_SETTLE_US
    fig, axes = plt.subplots(
        5, 2, figsize=(7.2, 5.2),
        gridspec_kw={"hspace": 0.6},
    )

    columns = [
        (2 * PERIOD_US, "а — общий вид, 2 периода (t, мкс)", 2 * PERIOD_US),
        (4 * (T_CONV_US + T_SETTLE_US), "б — фрагмент запуска (t, мкс)",
         PERIOD_US / 2),
    ]
    for col, (t_end, title, t_fall) in enumerate(columns):
        v4 = [(0.0, t_fall, V4_HIGH), (t_fall, t_end, V4_LOW)]
        soc = list(v4)
        oe = [(0.0, t_fall, V4_LOW), (t_fall, t_end, V4_HIGH)]
        eoc = [(0.0, t_conv, V4_LOW), (t_conv, t_end, V4_HIGH)]
        valid_to = min(t_fall, t_end)
        data = [(0.0, t_valid, V4_LOW), (t_valid, valid_to, V4_HIGH),
                (valid_to, t_end, V4_LOW)]
        for row, (segs, label) in enumerate(
            [(v4, "V4"), (soc, "SOC"), (oe, "OE"), (eoc, "EOC"),
             (data, "D0…D15")]
        ):
            ax = axes[row][col]
            _draw_signal(ax, segs, 5, 0, label)
            if row == 0:
                ax.set_title(title, fontsize=9)
            if row == 4:
                ax.set_xlabel("t, мкс", fontsize=9)
        axes[4][col].annotate(
            "код достоверен",
            xy=((t_valid + valid_to) / 2, 2.5),
            ha="center", fontsize=8, color="C2",
        )

    fig.suptitle(
        "Временная диаграмма синхронизации виртуального АЦП "
        "(V4 = 1 кГц, tпр = 10 мкс)", fontsize=10
    )
    fig.align_ylabels(axes)
    fig.savefig(FIG / "adc-timing.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_transfer():
    """Статическая характеристика 16-разрядного АЦП варианта 4."""
    fig, axes = plt.subplots(
        1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.3}
    )

    # (а) характеристика преобразования uвых(ЦАП) = f(uвх)
    ax = axes[0]
    u = [i * 5.0 / 4000 for i in range(4001)]
    code = [quantize(x, VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS) for x in u]
    u_dac = [dac_voltage(c, VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS)
             for c in code]
    ax.plot(u, u_dac, color="C0", lw=1.0)
    meas = investigation_table(
        VARIANT4_INPUTS_V, VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS
    )
    ax.plot([m["u_in"] for m in meas], [m["u_dac"] for m in meas],
            "o", color="C3", ms=4, label="точки измерений")
    ax.plot([0, 5], [0, 5], "--", color="0.5", lw=0.8, label="идеальная прямая")
    ax.set_xlabel("uвх, В")
    ax.set_ylabel("uвых(ЦАП), В")
    ax.set_title("а — характеристика преобразования", fontsize=9)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, ls=":", alpha=0.5)

    # (б) погрешность квантования (пилообразная, ±1 МЗР)
    ax = axes[1]
    u_fine = [0.001 + i * (4.999 - 0.001) / 5000 for i in range(5001)]
    err = [
        dac_voltage(
            quantize(x, VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS),
            VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS,
        )
        - x
        for x in u_fine
    ]
    ax.plot(u_fine, [e / LSB for e in err], color="C0", lw=0.7)
    ax.axhline(1.0, color="C3", ls="--", lw=0.8)
    ax.axhline(0.0, color="0.5", ls=":", lw=0.8)
    ax.axhline(-1.0, color="C3", ls="--", lw=0.8)
    ax.set_xlabel("uвх, В")
    ax.set_ylabel("погрешность, МЗР")
    ax.set_title("б — погрешность квантования", fontsize=9)
    ax.grid(True, ls=":", alpha=0.5)

    fig.savefig(FIG / "adc-transfer-variant4.png", dpi=200,
                bbox_inches="tight")
    plt.close(fig)


def fig_probes():
    """Показания пробников Х0…Х15 для трёх точек задания 2 (вариант 4)."""
    rows = [
        mcu_read_code(u, VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS)
        for u in VARIANT4_MCU_INPUTS_V
    ]
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    ax.set_aspect("equal")
    ax.axis("off")
    for r, res in enumerate(rows):
        y = len(rows) - 1 - r
        code = res["code"]
        ax.text(-5.0, y, f"uвх = {res['u_in']:.1f} В", ha="right", va="center",
                fontsize=9)
        ax.text(-2.6, y, f"D = {code} (0x{code:04X})", ha="right",
                va="center", fontsize=8, family="monospace")
        for i in range(16):
            lit = res["probes"][i]
            ax.add_patch(
                Circle((i, y), 0.36,
                       facecolor="#2ca02c" if lit else "#f2f2f2",
                       edgecolor="0.3", lw=0.8)
            )
            ax.text(i, y, str(i) if lit else "", ha="center", va="center",
                    fontsize=7, color="white")
    for i in range(16):
        ax.text(i, -0.9, f"X{i}", ha="center", va="center", fontsize=7)
    ax.set_xlim(-5.4, 15.6)
    ax.set_ylim(-1.3, len(rows) - 0.4)
    ax.set_title(
        "Показания пробников: зелёный — пробник светится (бит равен 1)", fontsize=9
    )
    fig.savefig(FIG / "adc-probes-variant4.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    fig_timing()
    fig_transfer()
    fig_probes()
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
