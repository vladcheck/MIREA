#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор схемы lab4-atmega32.kicad_sch (ЛР №4, стенд MPSU-SH-MN, ATmega32 DIP-40, 5 В).

Состав:
  U1  — ATmega32, КАСТОМНЫЙ символ (встроен в lib_symbols):
        слева PA0-PA7, PB0-PB7; справа PD0-PD7, PC0-PC7;
        сверху Vcc/GND/AVCC/GND/AREF; снизу RESET/XTAL1/XTAL2.
        Номера выводов — по корпусу DIP-40.
  SA1-SA8 — тумблеры SW_SPST на PA0-PA7 (замыкают вход на GND, pull-up в МК);
  SB1-SB4 — кнопки SW_Push на PB0-PB3 (на GND);
  SB5/SB6 — кнопки SW_Push на PD1/PD2 (на GND, порт D двунаправленный);
  SB7     — кнопка сброса на RESET (на GND);
  R1-R8   — 1 кОм в линиях PC0-PC7 -> VD1-VD8 (на GND, активная 1);
  R9-R16  — 1 кОм в линиях PD0-PD7 -> VD9-VD16 (на GND);
  R17     — 10 кОм подтяжка RESET к +5V;
  C1/C2   — 100 нФ развязка Vcc/AVCC; C3/C4 — 22 пФ кварца;
  X1      — кварц 8 МГц на XTAL1/XTAL2;
  шина +5V с PWR_FLAG, PWR_FLAG на GND, AREF на +5V;
  no-connect на PB4-PB7.

Все библиотечные символы (кроме U1) встраиваются из штатных библиотек KiCad
без изменений. Все координаты — на сетке 1.27 мм, единицы — мм.
"""

import re
import uuid

STOCK_DEV = "/Applications/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym"
STOCK_SW = "/Applications/KiCad.app/Contents/SharedSupport/symbols/Switch.kicad_sym"
STOCK_PW = "/Applications/KiCad.app/Contents/SharedSupport/symbols/power.kicad_sym"
OUT = "schematic/lab4-atmega32.kicad_sch"
PROJECT = "lab4-atmega32"

MX, MY = 152.4, 152.4  # центр U1

# Левые выводы: PA0-PA7 (ряды 0-7), PB0-PB7 (ряды 8-15). Шаг 2.54.
Y0 = 129.54
LEFT_NAMES = ["PA%d" % i for i in range(8)] + ["PB%d" % i for i in range(8)]
RIGHT_NAMES = ["PD%d" % i for i in range(8)] + ["PC%d" % i for i in range(8)]
PIN_NUM = {  # имя -> номер вывода DIP-40
    "PB0": "1",
    "PB1": "2",
    "PB2": "3",
    "PB3": "4",
    "PB4": "5",
    "PB5": "6",
    "PB6": "7",
    "PB7": "8",
    "RESET": "9",
    "VCC": "10",
    "GND11": "11",
    "XTAL2": "12",
    "XTAL1": "13",
    "PD0": "14",
    "PD1": "15",
    "PD2": "16",
    "PD3": "17",
    "PD4": "18",
    "PD5": "19",
    "PD6": "20",
    "PD7": "21",
    "PC1": "22",
    "PC0": "23",
    "PC2": "24",
    "PC3": "25",
    "PC4": "26",
    "PC5": "27",
    "PC6": "28",
    "PC7": "29",
    "AVCC": "30",
    "GND31": "31",
    "AREF": "32",
    "PA7": "33",
    "PA6": "34",
    "PA5": "35",
    "PA4": "36",
    "PA3": "37",
    "PA2": "38",
    "PA1": "39",
    "PA0": "40",
}
LX_TIP, RX_TIP = 137.16, 167.64  # кончики левых/правых выводов U1
TOP_TIP, BOT_TIP = 124.46, 180.34  # кончики верхних/нижних выводов U1
TOP_XS = [139.7, 144.78, 149.86, 154.94, 160.02]  # Vcc GND AVCC GND AREF
TOP_IDS = ["VCC", "GND11", "AVCC", "GND31", "AREF"]
BOT_XS = [144.78, 152.4, 160.02]  # RESET XTAL1 XTAL2
BOT_IDS = ["RESET", "XTAL1", "XTAL2"]

ROW_Y = [round(Y0 + 2.54 * i, 2) for i in range(16)]


def U():
    return str(uuid.uuid4())


def extract_symbol(src, name):
    key = '(symbol "%s"' % name
    i = src.find(key)
    assert i > 0, name
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "(":
            depth += 1
        elif src[j] == ")":
            depth -= 1
            if depth == 0:
                return src[i : j + 1]
    raise AssertionError(name)


def mcu_lib():
    """Кастомный символ ATmega32: прямоугольник + 40 выводов."""
    L = []
    A = L.append
    A('\t\t(symbol "lab4:ATmega32"')
    A("\t\t\t(pin_names\n\t\t\t\t(offset 1.016)\n\t\t\t)")
    A("\t\t\t(pin_numbers\n\t\t\t\t(hide yes)\n\t\t\t)")
    A("\t\t\t(exclude_from_sim no)")
    A("\t\t\t(in_bom yes)")
    A("\t\t\t(on_board yes)")
    A("\t\t\t(in_pos_files yes)")
    A("\t\t\t(duplicate_pin_numbers_are_jumpers no)")
    for prop, val, hx, hy in (
        ("Reference", "U", 0, 27.94),
        ("Value", "ATmega32", 0, -27.94),
        ("Footprint", "Package_DIP:DIP-40_W15.24mm", 0, 0),
        ("Datasheet", "https://www.microchip.com/en-us/product/ATmega32", 0, 0),
        ("Description", "ATmega32 8-bit AVR, DIP-40", 0, 0),
    ):
        hide = "" if prop in ("Reference", "Value") else "\n\t\t\t\t(hide yes)"
        A(
            '\t\t\t(property "%s" "%s"\n\t\t\t\t(at %g %g 0)%s\n'
            "\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n"
            "\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n"
            "\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)" % (prop, val, hx, hy, hide)
        )
    A('\t\t\t(symbol "ATmega32_0_1"')
    A(
        "\t\t\t\t(rectangle\n\t\t\t\t\t(start -12.7 25.4)\n\t\t\t\t\t(end 12.7 -25.4)"
        "\n\t\t\t\t\t(stroke\n\t\t\t\t\t\t(width 0.254)\n\t\t\t\t\t\t(type default)"
        "\n\t\t\t\t\t)\n\t\t\t\t\t(fill\n\t\t\t\t\t\t(type background)\n\t\t\t\t\t)"
        "\n\t\t\t\t)"
    )
    A("\t\t\t)")
    A('\t\t\t(symbol "ATmega32_1_1"')
    for r in range(16):
        wy = ROW_Y[r]
        ly = round(MY - wy, 2)
        for name, lx, ang in ((LEFT_NAMES[r], -15.24, 0), (RIGHT_NAMES[r], 15.24, 180)):
            A(pin_line(name, PIN_NUM[name], lx, ly, ang, "bidirectional"))
    for xid, idx in zip(TOP_XS, TOP_IDS):
        lx = round(xid - MX, 2)
        et = "power_in" if idx in ("VCC", "AVCC", "GND11", "GND31") else "input"
        A(
            pin_line(
                idx if idx.startswith("GND") else idx, PIN_NUM[idx], lx, 27.94, 270, et
            )
        )
    for xid, idx in zip(BOT_XS, BOT_IDS):
        lx = round(xid - MX, 2)
        A(pin_line(idx, PIN_NUM[idx], lx, -27.94, 90, "input"))
    A("\t\t\t)")
    A("\t\t\t(embedded_fonts no)")
    A("\t\t)")
    return "\n".join(L)


def pin_line(name, num, x, y, ang, etype):
    return (
        "\t\t\t\t(pin %s line\n\t\t\t\t\t(at %g %g %d)\n\t\t\t\t\t(length 2.54)\n"
        '\t\t\t\t\t(name "%s"\n\t\t\t\t\t\t(effects\n\t\t\t\t\t\t\t(font\n'
        "\t\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t\t)\n\t\t\t\t\t\t)\n"
        '\t\t\t\t\t)\n\t\t\t\t\t(number "%s"\n\t\t\t\t\t\t(effects\n'
        "\t\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t\t\t\t)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)"
        % (etype, x, y, ang, name, num)
    )


def inst(
    lib_id, ref, value, footprint, x, y, rot, root_uuid, pins, ref_hide=False, pang=None
):
    L = []
    A = L.append
    pa = rot if pang is None else pang
    A(
        '\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %g %g %d)\n\t\t(unit 1)\n'
        "\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n"
        '\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)\n\t\t(uuid "%s")'
        % (lib_id, x, y, rot, U())
    )
    for prop, val, px, py, show in (
        ("Reference", ref, x, round(y - 3.81, 2), not ref_hide),
        ("Value", value, x, round(y + 3.81, 2), True),
        ("Footprint", footprint, x, y, False),
        ("Datasheet", "", x, y, False),
    ):
        A(
            '\t\t(property "%s" "%s"\n\t\t\t(at %g %g %d)%s\n\t\t\t(show_name no)\n'
            "\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n"
            "\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)"
            % (prop, val, px, py, pa, "" if show else "\n\t\t\t(hide yes)")
        )
    for p in pins:
        A('\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)' % (p, U()))
    A(
        '\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n'
        '\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'
        % (PROJECT, root_uuid, ref)
    )
    return "\n".join(L)


def wire(pts):
    return (
        "\t(wire\n\t\t(pts\n\t\t\t%s\n\t\t)"
        "\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)"
        '\n\t\t(uuid "%s")\n\t)' % ("\n\t\t\t".join("(xy %g %g)" % p for p in pts), U())
    )


def junction(x, y):
    return (
        "\t(junction\n\t\t(at %g %g)\n\t\t(diameter 0)\n"
        '\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)' % (x, y, U())
    )


def no_connect(x, y):
    return '\t(no_connect\n\t\t(at %g %g)\n\t\t(uuid "%s")\n\t)' % (x, y, U())


def label(name, x, y, angle, side):
    just = "right bottom" if side == "right" else "left bottom"
    return (
        '\t(label "%s"\n\t\t(at %g %g %d)\n\t\t(effects\n\t\t\t(font\n'
        "\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)"
        '\n\t\t(uuid "%s")\n\t)' % (name, x, y, angle, just, U())
    )


def text(s, x, y, size, bold=False):
    b = "\n\t\t\t(bold yes)" if bold else ""
    return (
        '\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %g %g 0)\n'
        "\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %g %g)%s\n\t\t\t)"
        '\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "%s")\n\t)'
        % (s, x, y, size, size, b, U())
    )


THT_R = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"
THT_C = "Capacitor_THT:C_Disc_D3.8mm_W2.6mm_P2.50mm"
DIP40 = "Package_DIP:DIP-40_W15.24mm"
HC49 = "Crystal:Crystal_HC49-U_Vertical"
LED5 = "LED_THT:LED_D5.0mm"
BTN = "Button_Switch_THT:SW_PUSH_6mm"
TOG = "Button_Switch_THT:SW_DIP_SPSTx01_Slide_9.78x4.72mm_W7.62mm_P2.54mm"


def main():
    dev = open(STOCK_DEV, encoding="utf-8").read()
    sw = open(STOCK_SW, encoding="utf-8").read()
    pw = open(STOCK_PW, encoding="utf-8").read()
    root_uuid = U()
    libs = [
        extract_symbol(dev, "R").replace('(symbol "R"', '(symbol "Device:R"', 1),
        extract_symbol(dev, "C").replace('(symbol "C"', '(symbol "Device:C"', 1),
        extract_symbol(dev, "Crystal").replace(
            '(symbol "Crystal"', '(symbol "Device:Crystal"', 1
        ),
        extract_symbol(dev, "LED").replace('(symbol "LED"', '(symbol "Device:LED"', 1),
        extract_symbol(sw, "SW_SPST").replace(
            '(symbol "SW_SPST"', '(symbol "Switch:SW_SPST"', 1
        ),
        extract_symbol(sw, "SW_Push").replace(
            '(symbol "SW_Push"', '(symbol "Switch:SW_Push"', 1
        ),
        extract_symbol(pw, "+5V").replace('(symbol "+5V"', '(symbol "power:+5V"', 1),
        extract_symbol(pw, "GND").replace('(symbol "GND"', '(symbol "power:GND"', 1),
        extract_symbol(pw, "PWR_FLAG").replace(
            '(symbol "PWR_FLAG"', '(symbol "power:PWR_FLAG"', 1
        ),
        mcu_lib(),
    ]

    out = []
    A = out.append
    A("(kicad_sch")
    A("\t(version 20260306)")
    A('\t(generator "eeschema")')
    A('\t(generator_version "10.0")')
    A('\t(uuid "%s")' % root_uuid)
    A('\t(paper "A3")')
    A("\t(lib_symbols")
    A("\n".join(libs))
    A("\t)")

    gnd_n = [0]
    p5_n = [0]

    def gnd(x, y, rot=0):
        gnd_n[0] += 1
        A(
            inst(
                "power:GND",
                "GND%d" % gnd_n[0],
                "GND",
                "",
                x,
                y,
                rot,
                root_uuid,
                ["1"],
                ref_hide=True,
            )
        )

    def p5(x, y, rot=0):
        p5_n[0] += 1
        A(
            inst(
                "power:+5V",
                "+5V%d" % p5_n[0],
                "+5V",
                "",
                x,
                y,
                rot,
                root_uuid,
                ["1"],
                ref_hide=True,
            )
        )

    # ---------- U1 ----------
    mcu_pins = (
        [PIN_NUM[n] for n in LEFT_NAMES + RIGHT_NAMES]
        + [PIN_NUM[i] for i in TOP_IDS]
        + [PIN_NUM[i] for i in BOT_IDS]
    )
    A(inst("lab4:ATmega32", "U1", "ATmega32", DIP40, MX, MY, 0, root_uuid, mcu_pins))

    # ---------- входные стабы + метки слева (PA/PB) ----------
    for r, name in enumerate(LEFT_NAMES):
        y = ROW_Y[r]
        A(wire([(132.08, y), (LX_TIP, y)]))
        A(label(name, 132.08, y, 0, "left"))
    # ---------- выходные стабы + метки справа (PD/PC) ----------
    for r, name in enumerate(RIGHT_NAMES):
        y = ROW_Y[r]
        A(wire([(RX_TIP, y), (172.72, y)]))
        A(label(name, 172.72, y, 180, "right"))
    # ---------- no-connect PB4-PB7 ----------
    for r in range(12, 16):
        A(no_connect(LX_TIP, ROW_Y[r]))

    # ---------- питание верхних выводов ----------
    for xid, idx in zip(TOP_XS, TOP_IDS):
        A(wire([(xid, 121.92), (xid, TOP_TIP)]))
        if idx in ("VCC", "AVCC", "AREF"):
            p5(xid, 121.92)
        else:
            gnd(xid, 121.92)

    # ---------- шина +5V с PWR_FLAG ----------
    A(wire([(50.8, 60.96), (60.96, 60.96)]))
    A(wire([(60.96, 60.96), (88.9, 60.96)]))
    p5(50.8, 60.96)
    p5(88.9, 60.96)
    A(
        inst(
            "power:PWR_FLAG",
            "PWR_FLAG1",
            "PWR_FLAG",
            "",
            60.96,
            60.96,
            0,
            root_uuid,
            ["1"],
            ref_hide=True,
        )
    )

    # ---------- развязка Vcc / AVCC ----------
    for n, cx, val in ((1, 118.11, "100n"), (2, 128.27, "100n")):
        A(inst("Device:C", "C%d" % n, val, THT_C, cx, 104.14, 0, root_uuid, ["1", "2"]))
        A(wire([(cx, 95.25), (cx, 100.33)]))
        p5(cx, 95.25)
        A(wire([(cx, 107.95), (cx, 114.3)]))
        gnd(cx, 114.3)

    # ---------- кварц X1 + 22 пФ ----------
    A(
        inst(
            "Device:Crystal",
            "X1",
            "8MHz",
            HC49,
            156.21,
            195.58,
            0,
            root_uuid,
            ["1", "2"],
        )
    )
    A(wire([(152.4, BOT_TIP), (152.4, 195.58)]))

    A(wire([(160.02, BOT_TIP), (160.02, 195.58)]))

    A(junction(152.4, 195.58))
    A(junction(160.02, 195.58))
    for n, cx in ((3, 152.4), (4, 160.02)):
        A(
            inst(
                "Device:C",
                "C%d" % n,
                "22p",
                THT_C,
                cx,
                208.28,
                0,
                root_uuid,
                ["1", "2"],
            )
        )
        A(wire([(cx, 195.58), (cx, 204.47)]))
        A(wire([(cx, 212.09), (cx, 220.98)]))
        gnd(cx, 220.98)

    # ---------- RESET: подтяжка 10k + кнопка ----------
    A(inst("Device:R", "R17", "10k", THT_R, 144.78, 193.04, 0, root_uuid, ["1", "2"]))
    A(wire([(144.78, BOT_TIP), (144.78, 189.23)]))
    A(wire([(144.78, 196.85), (144.78, 200.66)]))
    p5(144.78, 200.66)
    A(
        inst(
            "Switch:SW_Push",
            "SB7",
            "RESET",
            BTN,
            114.3,
            187.96,
            0,
            root_uuid,
            ["1", "2"],
        )
    )
    A(wire([(119.38, 187.96), (144.78, 187.96)]))
    A(junction(144.78, 187.96))
    A(wire([(104.14, 187.96), (109.22, 187.96)]))
    gnd(104.14, 187.96, 90)

    # ---------- SA1-SA8 (тумблеры на PA) ----------
    SA_Y = [round(69.85 + 12.7 * i, 2) for i in range(8)]
    for i, y in enumerate(SA_Y):
        A(
            inst(
                "Switch:SW_SPST",
                "SA%d" % (i + 1),
                "ON-OFF",
                TOG,
                44.45,
                y,
                0,
                root_uuid,
                ["1", "2"],
            )
        )
        A(wire([(34.29, y), (39.37, y)]))
        A(label("PA%d" % i, 34.29, y, 0, "left"))
        A(wire([(49.53, y), (55.88, y)]))
        gnd(55.88, y, 90)

    # ---------- SB1-SB4 (кнопки на PB0-PB3) ----------
    SB_Y = [139.7, 152.4, 165.1, 177.8]
    for i, y in enumerate(SB_Y):
        A(
            inst(
                "Switch:SW_Push",
                "SB%d" % (i + 1),
                "PUSH",
                BTN,
                88.9,
                y,
                0,
                root_uuid,
                ["1", "2"],
            )
        )
        A(wire([(78.74, y), (83.82, y)]))
        A(label("PB%d" % i, 78.74, y, 0, "left"))
        A(wire([(93.98, y), (100.33, y)]))
        gnd(100.33, y, 90)

    # ---------- SB5/SB6 (кнопки на PD1/PD2) ----------
    for i, y in ((5, 190.5), (6, 203.2)):
        A(
            inst(
                "Switch:SW_Push",
                "SB%d" % i,
                "PUSH",
                BTN,
                88.9,
                y,
                0,
                root_uuid,
                ["1", "2"],
            )
        )
        A(wire([(78.74, y), (83.82, y)]))
        A(label("PD%d" % (i - 4), 78.74, y, 0, "left"))
        A(wire([(93.98, y), (100.33, y)]))
        gnd(100.33, y, 90)

    # ---------- светодиоды PC (VD1-VD8) и PD (VD9-VD16) ----------
    for i, y in enumerate(SA_Y):
        # PCi -> Ri -> VDi -> GND
        A(
            inst(
                "Device:R",
                "R%d" % (i + 1),
                "1k",
                THT_R,
                200.66,
                y,
                90,
                root_uuid,
                ["1", "2"],
            )
        )
        A(
            inst(
                "Device:LED",
                "VD%d" % (i + 1),
                "red",
                LED5,
                220.98,
                y,
                180,
                root_uuid,
                ["1", "2"],
                pang=0,
            )
        )
        A(wire([(190.5, y), (196.85, y)]))
        A(label("PC%d" % i, 190.5, y, 0, "left"))
        A(wire([(204.47, y), (217.17, y)]))
        A(wire([(224.79, y), (233.68, y)]))
        gnd(233.68, y, 90)
        # PDi -> R(i+8) -> VD(i+8) -> GND
        A(
            inst(
                "Device:R",
                "R%d" % (i + 9),
                "1k",
                THT_R,
                259.08,
                y,
                90,
                root_uuid,
                ["1", "2"],
            )
        )
        A(
            inst(
                "Device:LED",
                "VD%d" % (i + 9),
                "red",
                LED5,
                279.4,
                y,
                180,
                root_uuid,
                ["1", "2"],
                pang=0,
            )
        )
        A(wire([(248.92, y), (255.27, y)]))
        A(label("PD%d" % i, 248.92, y, 0, "left"))
        A(wire([(262.89, y), (275.59, y)]))
        A(wire([(283.21, y), (292.1, y)]))
        gnd(292.1, y, 90)

    # ---------- PWR_FLAG на GND ----------
    A(wire([(139.7, 250.19), (149.86, 250.19)]))
    gnd(139.7, 250.19, 90)
    A(
        inst(
            "power:PWR_FLAG",
            "PWR_FLAG2",
            "PWR_FLAG",
            "",
            149.86,
            250.19,
            0,
            root_uuid,
            ["1"],
            ref_hide=True,
        )
    )

    # ---------- надписи ----------
    A(
        text(
            "Лабораторная работа #4: стенд ATmega32 (вариант 4)",
            20.32,
            30.48,
            3.0,
            bold=True,
        )
    )
    A(
        text(
            "lab4 ATmega32 stand connections: PA->SA, PB->SB, PC->VD1-VD8, PD->VD9-VD16",
            20.32,
            38.1,
            1.7,
        )
    )
    notes = [
        "SA1-SA8 (PA0-PA7): тумблер замкнут — лог. 0, разомкнут — лог. 1 (pull-up в МК);",
        "SB1-SB4 (PB0-PB3): кнопка нажата — лог. 0 (pull-up в МК);",
        "VD1-VD8 (PC0-PC7) и VD9-VD16 (PD0-PD7) через 1 кОм на GND: лог. 1 зажигает;",
        "SB5/SB6 подключены к PD1/PD2 параллельно VD10/VD11: порт D двунаправленный,",
        "  при выводе проверять, что кнопки отпущены; SB7 — сброс (RESET, 10 кОм к +5V);",
        "Тактирование: X1 8 МГц, C3/C4 22 пФ; развязка Vcc/AVCC — C1/C2 100 нФ; AREF на +5V;",
        "PB4-PB7 не используются (no-connect).",
    ]
    for n, line in enumerate(notes):
        A(text(line, 100, round(46.0 + 4.5 * n, 2), 1.5))

    A('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)')
    A("\t(embedded_fonts no)")
    A(")")

    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("saved %s (%d bytes)" % (OUT, len("\n".join(out))))
    print(
        "nets: PA0-7->SA1-8, PB0-3->SB1-4, PB4-7 NC, PC0-7->R1-8->VD1-8, "
        "PD0-7->R9-16->VD9-16, PD1/PD2->SB5/SB6, RESET->R17/SB7"
    )


if __name__ == "__main__":
    main()
