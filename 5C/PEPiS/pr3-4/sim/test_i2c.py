"""Тесты симулятора шины I2C для ПР №3-4, вариант 4.

Позитивные тесты повторяют точную последовательность транзакций
pr3-4/src/main_variant4.c:
  1. EEPROM_WriteByte(0x003F, 0x67):  START 0xA0 ACK 0x00 ACK 0x3F ACK 0x67 ACK STOP
  2. внутренний цикл записи ~5 мс + ACK polling: NACK, затем ACK
  3. EEPROM_ReadByte (random read):   START 0xA0 ACK 0x00 ACK 0x3F ACK
                                      repeated START 0xA1 ACK 0x67 NACK STOP
  4. DS1307_SetTime(12,34,00):        START 0xD0 ACK 0x00 ACK 0x00 ACK
                                      0x34 ACK 0x12 ACK STOP
  5. DS1307_ReadReg(0x00):            START 0xD0 ACK 0x00 ACK
                                      repeated START 0xD1 ACK 0x00 NACK STOP

Негативные тесты (п. 9 задания TZ):
  a. отключена подтяжка -> SDA застряла, тайм-аут мастера, светодиод OFF
  b. EEPROM с адресом 0x51 (A0=1) -> NACK на SLA+W, светодиод OFF

Артефакты: out/i2c_results.json, out/i2c_waveform.csv, img/i2c-waveform.png
Код выхода 0 только если все тесты прошли.
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i2c_bus import (
    Bus,
    I2CMaster,
    EEPROM24LC64,
    DS1307,
    I2CTimeout,
    I2CShortPullup,
    EEPROM_CELL,
    EEPROM_TEST_VALUE,
    DS1307_TEST_REG,
    EEPROM_T_WRITE_US,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")
IMG_DIR = os.path.join(ROOT, "img")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Позитивный сценарий — точная копия main() из main_variant4.c
# ---------------------------------------------------------------------------
def run_positive():
    bus = Bus(pullups=True)
    eeprom = EEPROM24LC64(a012=0b000, wp=False)
    rtc = DS1307()
    bus.devices = [eeprom, rtc]
    master = I2CMaster(bus)

    result = {"phases": [], "pass": False}

    def phase(name):
        result["phases"].append({"name": name, "t_start_us": round(bus.t, 1)})

    # 1. Запись байта варианта в ячейку EEPROM -------------------------
    phase("EEPROM write 0x67 -> 0x003F")
    ok = master.eeprom_write_byte(EEPROM_CELL, EEPROM_TEST_VALUE)
    result["write_ack_polling_ok"] = ok

    # 2. Внутренний цикл записи уже прошёл внутри eeprom_write_byte
    #    (ACK polling). Фиксируем его на временной оси подписью.
    result["write_cycle_us"] = EEPROM_T_WRITE_US

    # 3. Случайное чтение той же ячейки --------------------------------
    phase("EEPROM random read 0x003F")
    value = master.eeprom_read_byte(EEPROM_CELL)
    result["eeprom_read"] = f"0x{value:02X}"
    result["eeprom_match"] = value == EEPROM_TEST_VALUE

    # 4. Установка времени DS1307 12:34:00 -----------------------------
    phase("DS1307 SetTime(12,34,00)")
    result["ds1307_set_ok"] = master.ds1307_set_time(12, 34, 0)

    # 5. Чтение регистра 0x00 (секунды) --------------------------------
    phase("DS1307 read reg 0x00")
    raw = master.ds1307_read_reg(DS1307_TEST_REG)
    result["ds1307_raw"] = f"0x{raw:02X}"
    result["ds1307_dec"] = master.decode_reg(DS1307_TEST_REG, raw)

    # Итог по прошивке: светодиод PA1 (1 = успех) ----------------------
    success = (
        result["write_ack_polling_ok"]
        and result["eeprom_match"]
        and result["ds1307_set_ok"]
        and result["ds1307_raw"] == "0x00"
    )
    master.led = 1 if success else 0
    result["led"] = master.led
    result["pass"] = bool(success)

    # Журнал ACK/NACK и границы байт для осциллограммы
    result["ack_log"] = [
        {"t_us": round(t, 1), "label": lbl, "ack": bool(ack)}
        for (t, lbl, ack) in bus.ack_log
    ]
    result["transactions"] = [
        {
            "t_start_us": round(a, 1),
            "t_end_us": round(b, 1),
            "label": lbl,
            "ack": bool(ack),
        }
        for (a, b, lbl, ack) in bus.byte_spans
    ]
    result["total_time_us"] = round(bus.t, 1)
    return result, bus


# ---------------------------------------------------------------------------
# Негативные тесты
# ---------------------------------------------------------------------------
def run_negative_no_pullup():
    """Подтяжка отключена: SDA не поднимается, мастер тайм-аутится."""
    bus = Bus(pullups=False)
    bus.devices = [EEPROM24LC64(), DS1307()]
    master = I2CMaster(bus)
    outcome = {"pass": False, "led": 0, "timeout": False, "acks": 0}
    try:
        master.eeprom_write_byte(EEPROM_CELL, EEPROM_TEST_VALUE)
    except (I2CTimeout, I2CShortPullup) as exc:
        outcome["timeout"] = True
        outcome["reason"] = str(exc)
    outcome["acks"] = sum(1 for (_, _, ack) in bus.ack_log if ack)
    outcome["led"] = 0  # error: ветка goto error -> ResultLED_Set(0)
    outcome["pass"] = (
        outcome["timeout"] and outcome["acks"] == 0 and outcome["led"] == 0
    )
    return outcome


def run_negative_wrong_address():
    """A0 подключен к VCC -> адрес 0x51; мастер шлёт 0xA0 -> NACK."""
    bus = Bus(pullups=True)
    eeprom_wrong = EEPROM24LC64(a012=0b001, wp=False)  # адрес 0x51
    bus.devices = [eeprom_wrong, DS1307()]
    master = I2CMaster(bus)
    outcome = {"pass": False, "led": 0, "sla_w": "0xA0", "ack": None}
    try:
        master.eeprom_write_byte(EEPROM_CELL, EEPROM_TEST_VALUE)
    except I2CTimeout:
        pass
    sla_w_entry = next((e for e in bus.ack_log if e[1].startswith("SLA+W")), None)
    outcome["ack"] = bool(sla_w_entry[2]) if sla_w_entry else None
    outcome["led"] = 0  # goto error -> ResultLED_Set(0)
    outcome["pass"] = (outcome["ack"] is False) and outcome["led"] == 0
    return outcome


# ---------------------------------------------------------------------------
# Осциллограмма
# ---------------------------------------------------------------------------
# Ширина слота отображения: байт — его реальная длительность + поля,
# паузы короче 300 мкс — 30 усл. единиц, длинные (цикл записи) — 110.
LEAD_US, TRAIL_US = 35.0, 35.0
SMALL_GAP_W, BIG_GAP_W, BIG_GAP_T = 30.0, 110.0, 300.0


def _build_segments(bus):
    """Разбивает временную ось на слоты: каждый байт — свой слот,
    паузы (START/STOP, цикл записи) — сжатые разрывы шкалы.
    Длинные серии одинаковых слотов (ACK polling) схлопываются в один
    разрыв, внутри которого реальные посылки показаны в сжатом виде."""
    spans = list(bus.byte_spans)
    collapsed = []
    i = 0
    while i < len(spans):
        a, b, lbl, ack = spans[i]
        k = i
        while k + 1 < len(spans) and spans[k + 1][2] == lbl and spans[k + 1][3] == ack:
            k += 1
        run = k - i + 1
        if run > 3:
            collapsed.append((a, b, lbl, ack))
            collapsed.append(("COLLAPSE", b, spans[k][0], lbl, run - 2))
            collapsed.append((spans[k][0], spans[k][1], lbl, ack))
        else:
            collapsed.extend(spans[i : k + 1])
        i = k + 1

    segments = []
    x = 0.0
    prev_end = None
    for idx, item in enumerate(collapsed):
        if item[0] == "COLLAPSE":
            _t0, _t1, lbl, count = item[1], item[2], item[3], item[4]
            gw = BIG_GAP_W * 1.6
            segments.append(
                {
                    "gap": True,
                    "collapse": True,
                    "t0": _t0,
                    "t1": _t1,
                    "x0": x,
                    "x1": x + gw,
                    "dur": _t1 - _t0,
                    "label": lbl,
                    "count": count,
                }
            )
            x += gw
            continue
        (a, b, lbl, ack) = item
        if prev_end is not None and a - prev_end > 0.5:
            dur = a - prev_end
            gw = BIG_GAP_W if dur > BIG_GAP_T else SMALL_GAP_W
            segments.append(
                {
                    "gap": True,
                    "t0": prev_end,
                    "t1": a,
                    "x0": x,
                    "x1": x + gw,
                    "dur": dur,
                }
            )
            x += gw
        w = (b - a) + LEAD_US + TRAIL_US
        segments.append(
            {
                "gap": False,
                "t0": a - LEAD_US,
                "t1": b + TRAIL_US,
                "x0": x,
                "x1": x + w,
                "label": lbl,
                "ack": ack,
            }
        )
        x += w
        prev_end = b

    def t2x(t):
        for seg in segments:
            if seg["t0"] - 1e-9 <= t <= seg["t1"] + 1e-9:
                frac = (t - seg["t0"]) / max(seg["t1"] - seg["t0"], 1e-9)
                return seg["x0"] + frac * (seg["x1"] - seg["x0"])
        return None

    return segments, x, t2x


def export_waveform_csv(bus, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time_us", "sda", "scl", "note"])
        for t, sda, scl in bus.samples:
            w.writerow([f"{t:.2f}", sda, scl, ""])


def render_waveform_png(bus, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    segments, total_x, t2x = _build_segments(bus)

    fig, ax = plt.subplots(figsize=(17, 6.6), dpi=150)

    # Разрывы шкалы — серые штрихованные полосы с подписями пауз.
    for seg in segments:
        if not seg["gap"]:
            continue
        ax.axvspan(seg["x0"], seg["x1"], color="#dddddd", alpha=0.55, hatch="//")
        if seg.get("collapse"):
            ax.text(
                (seg["x0"] + seg["x1"]) / 2,
                6.9,
                f"цикл записи EEPROM = {seg['dur'] / 1000:.1f} мс\n"
                f"ACK polling x{seg['count']} (NACK)",
                ha="center",
                va="bottom",
                fontsize=7.5,
                color="#555555",
            )
        elif seg["dur"] > BIG_GAP_T:
            ax.text(
                (seg["x0"] + seg["x1"]) / 2,
                2.0,
                f"внутренний цикл записи\nEEPROM = {seg['dur'] / 1000:.1f} мс",
                ha="center",
                va="center",
                fontsize=7,
                color="#555555",
                rotation=90,
            )

    # Диапазоны схлопнутых серий (для скрытия маркеров и рисования тиков).
    collapse_ranges = [
        (seg["t0"], seg["t1"]) for seg in segments if seg["gap"] and seg.get("collapse")
    ]

    # Сигналы: каждый байт — в своём слоте (внутри слота масштаб сохранён).
    for seg in segments:
        if seg["gap"]:
            # В схлопнутой полосе рисуем «лесенку» сжатых посылок-тиков.
            if seg.get("collapse"):
                for a, b, lbl, ack in bus.byte_spans:
                    if seg["t0"] - 1e-9 <= a <= seg["t1"] + 1e-9:
                        xm = t2x(a)
                        if xm is not None:
                            ax.plot(
                                [xm, xm],
                                [0.55, 4.05],
                                color="#909090",
                                lw=0.8,
                                alpha=0.85,
                            )
            continue
        pts = [
            (t2x(t), sda, scl)
            for (t, sda, scl) in bus.samples
            if seg["t0"] - 1e-9 <= t <= seg["t1"] + 1e-9
        ]
        if not pts:
            continue
        xs = [p[0] for p in pts]
        ax.step(xs, [p[2] + 2.6 for p in pts], where="post", color="#b03030", lw=1.3)
        ax.step(xs, [p[1] + 0.6 for p in pts], where="post", color="#2040a0", lw=1.3)

    # Маркеры START / repeated START / STOP: компактные глифы,
    # полные слова — только при первом появлении.
    seen = set()
    for t, kind in bus.markers:
        if any(r0 - 1e-9 <= t <= r1 + 1e-9 for r0, r1 in collapse_ranges):
            continue  # маркеры схлопнутых посылок не подписываем
        x = t2x(t)
        if x is None:
            continue
        first = kind not in seen
        seen.add(kind)
        if kind == "STOP":
            txt = "STOP" if first else "P"
            ax.annotate(
                txt,
                (x, 1.12),
                xytext=(x, 0.30 if first else 0.55),
                fontsize=6.5,
                color="#a02020",
                ha="center",
                arrowprops=dict(arrowstyle="-", color="#a02020", lw=0.9),
            )
        else:
            txt = (
                ("Sr  REP START" if first else "Sr")
                if kind == "REP START"
                else ("START" if first else "S")
            )
            ax.annotate(
                txt,
                (x, 4.15),
                xytext=(x, 4.95),
                fontsize=6.5,
                color="#208020",
                ha="center",
                arrowprops=dict(arrowstyle="-", color="#208020", lw=0.9),
            )

    # Подписи байтов — вертикально над слотом (стиль логического анализатора).
    for seg in segments:
        if seg["gap"]:
            continue
        color = "#208020" if seg["ack"] else "#c02020"
        marker = "ACK" if seg["ack"] else "NACK"
        cx = (seg["x0"] + seg["x1"]) / 2
        ax.text(
            cx,
            6.35,
            f"{seg['label']} {marker}",
            ha="center",
            va="bottom",
            fontsize=6.8,
            color=color,
            rotation=90,
        )

    # Легенда сигналов.
    ax.text(
        -total_x * 0.035,
        3.6,
        "SCL",
        color="#b03030",
        fontsize=12,
        fontweight="bold",
        ha="right",
    )
    ax.text(
        -total_x * 0.035,
        1.6,
        "SDA",
        color="#2040a0",
        fontsize=12,
        fontweight="bold",
        ha="right",
    )

    ax.set_yticks([])
    ax.set_xlim(-total_x * 0.04, total_x)
    ax.set_ylim(0.0, 9.4)
    ax.set_xticks([])
    ax.set_xlabel(
        "условная ось: каждый байт — в своём временном слоте, "
        "серые полосы — сжатые паузы (шкала разорвана)",
        fontsize=10,
    )
    ax.set_title(
        "Временная диаграмма обмена по I2C, вариант 4 (fSCL = 100 кГц): "
        "запись 0x67 -> 24LC64@0x003F, ACK polling, случайное чтение, "
        "DS1307 SetTime(12:34:00) и чтение регистра 0x00",
        fontsize=11.5,
    )
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    positive, bus = run_positive()

    # Осциллограмма позитивного сценария.
    csv_path = os.path.join(OUT_DIR, "i2c_waveform.csv")
    png_path = os.path.join(IMG_DIR, "i2c-waveform.png")
    export_waveform_csv(bus, csv_path)
    try:
        render_waveform_png(bus, png_path)
        waveform_ok = True
    except ImportError:
        import subprocess

        subprocess.check_call(
            [
                "uv",
                "run",
                "--with",
                "matplotlib",
                sys.executable,
                __file__,
                "--waveform-only",
            ]
        )
        waveform_ok = True

    neg_a = run_negative_no_pullup()
    neg_b = run_negative_wrong_address()

    report = {
        "work": "ПР №3-4. Шина I2C: STM32F103C8 + 24LC64 + DS1307",
        "variant": 4,
        "i2c_settings": {
            "fSCL_Hz": 100000,
            "STM32": {
                "FREQ": 8,
                "CCR": 40,
                "TRISE": 9,
                "pins": "PB6=SCL, PB7=SDA (open-drain, 2 MHz)",
                "clock": "HSI 8 MHz, PCLK1 = 8 MHz",
            },
            "ATmega32": {
                "TWBR": 32,
                "TWPS": "00",
                "pins": "PC0=SCL, PC1=SDA (сравнительная часть)",
                "led": "PB1",
            },
        },
        "positive": positive,
        "negative_no_pullup": neg_a,
        "negative_wrong_eeprom_address": neg_b,
        "waveform_csv": "out/i2c_waveform.csv",
        "waveform_png": "img/i2c-waveform.png",
        "all_pass": bool(positive["pass"] and neg_a["pass"] and neg_b["pass"]),
    }
    json_path = os.path.join(OUT_DIR, "i2c_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Консольная сводка.
    print("=== ПР №3-4, вариант 4: результаты симуляции I2C ===")
    p = positive
    print(
        f"[+] EEPROM write 0x{EEPROM_TEST_VALUE:02X} @0x{EEPROM_CELL:04X} | ACK polling "
        f"{'OK' if p['write_ack_polling_ok'] else 'FAIL'} | "
        f"read back {p['eeprom_read']} (match={p['eeprom_match']}) | "
        f"DS1307 raw {p['ds1307_raw']} -> dec {p['ds1307_dec']} | LED={p['led']}"
    )
    print(
        f"[-] без подтяжки: timeout={neg_a['timeout']}, ACK={neg_a['acks']}, "
        f"LED={neg_a['led']}, pass={neg_a['pass']}"
    )
    print(
        f"[-] неверный адрес EEPROM (0x51): ACK на 0xA0={neg_b['ack']}, "
        f"LED={neg_b['led']}, pass={neg_b['pass']}"
    )
    print(f"JSON : {json_path}")
    print(f"CSV  : {csv_path}")
    print(f"PNG  : {png_path}")
    print("ALL PASS" if report["all_pass"] else "SOME TESTS FAILED")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--waveform-only":
        _pos, _bus = run_positive()
        render_waveform_png(_bus, os.path.join(IMG_DIR, "i2c-waveform.png"))
        sys.exit(0)
    sys.exit(main())
