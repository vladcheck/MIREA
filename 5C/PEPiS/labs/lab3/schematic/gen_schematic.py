#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор схемы lab3-sw-7seg.kicad_sch.

Состав (ЛР №3, STM32F407VGT6, индикатор с общим катодом):
  U1  — MCU STM32F407VGTx (символ дословно из lab1-gpio);
  R1-R8 — 270 Ом в линиях сегментов PA0-PA7 (Device:R из lab1);
  HG1 — 4-разрядный индикатор CC56-12GWA, общий катод
        (символ дословно из штатной библиотеки KiCad Display_Character);
  S1-S4 — свитчи генераторов логических уровней на PB0-PB3
        (символ дословно из штатной библиотеки KiCad Switch:SW_Push),
        каждый замыкает свой вход на GND (активный низкий, pull-up в МК);
  цепи питания +3V3/GND — дословно из lab1-gpio.

Все библиотечные символы встраиваются в файл (внешние библиотеки не нужны),
определения совпадают со штатными — ERC без замечаний.
Подключение: PA0-PA7 -> R -> сегменты a-g,DPX; PC0-PC3 -> CC1-CC4 (активный 0);
PB0-PB3 -> S1-S4 -> GND.
Опыты со светодиодом (PA0) выполняются без индикатора: D1 подключается
к PA0 через 270 Ом на GND вместо HG1 (общая линия PA0).

Преобразование координат символа в лист (проверено по lab1):
    world = inst_pos + Rot(inst_rot) * (x_lib, -y_lib)
Все координаты на сетке 1.27 мм.
"""

import re
import uuid

LAB1 = "../lab1-gpio/schematic/lab1-gpio.kicad_sch"
STOCK_DISP = (
    "/Applications/KiCad.app/Contents/SharedSupport/symbols/Display_Character.kicad_sym"
)
STOCK_SW = "/Applications/KiCad.app/Contents/SharedSupport/symbols/Switch.kicad_sym"
OUT = "schematic/lab3-sw-7seg.kicad_sch"
PROJECT = "lab3-sw-7seg"

MX, MY = 60.96, 106.68  # позиция U1 (как в lab1)

PA_ROWS = [43.18 + 2.54 * i for i in range(8)]  # PA0..PA7 (совпадает с U1)
PC_ROWS = [129.54 + 2.54 * i for i in range(4)]  # PC0..PC3

PA_NAMES = ["PA%d" % i for i in range(8)]
PC_NAMES = ["PC%d" % i for i in range(4)]

RX_BASE = 106.68
RX_STEP = 5.08
# Лесенка: R1-R4 уходят вправо, R5-R8 начинаются заново с базы.
RXS = [RX_BASE + RX_STEP * (i % 4) for i in range(8)]

# HG1 CC56-12GWA в (170, 50.8): сдвинут вправо под лесенку резисторов.
HG_X, HG_Y = 170, 50.8
HG_SEGX = HG_X - 27.94  # 116.84
HG_CCX = HG_X + 27.94  # 172.72
# соответствие строк R (PA0..PA7 = a..g,DPX) строкам выводов HG1
HG_SEGS = ["a", "b", "c", "d", "e", "f", "g", "DPX"]
# номера выводов CC56-12GWA: имя -> номер
HG_PINNUM = {
    "e": "1",
    "d": "2",
    "DPX": "3",
    "c": "4",
    "g": "5",
    "CC4": "6",
    "b": "7",
    "CC3": "8",
    "CC2": "9",
    "f": "10",
    "a": "11",
    "CC1": "12",
}
HG_CCS = ["CC1", "CC2", "CC3", "CC4"]  # CC1=DIG1(тысячи) .. CC4=DIG4(единицы)


def U():
    return str(uuid.uuid4())


def extract_symbol(src, name):
    """Извлечь блок (symbol "name" ...) по балансу скобок."""
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


def extract_instances(src, y_keep):
    """Инстансы символов питания на заданных Y: целиком дословно из lab1."""
    blocks = []
    for m in re.finditer(
        r'\t\(symbol\s+\(lib_id "(power:[^"]+)"\)\s+'
        r"\(at ([\d\.\-]+) ([\d\.\-]+) (\d+)\)(.*?)\n\t\)\n",
        src,
        re.S,
    ):
        if float(m.group(3)) in y_keep:
            blocks.append(m.group(0))
    return blocks


def retarget_power(block, root_uuid):
    """Новый uuid + проект lab2-7seg в дословно перенесённом инстансе."""
    block = re.sub(r'\(uuid "[0-9a-f\-]+"\)', '(uuid "%s")' % U(), block, count=1)
    block = block.replace('(project "lab1-gpio"', '(project "%s"' % PROJECT)
    block = re.sub(r'\(path "/[0-9a-f\-]+"', '(path "/%s"' % root_uuid, block)
    return block


def main():
    src = open(LAB1, encoding="utf-8").read()
    stock_disp = open(STOCK_DISP, encoding="utf-8").read()
    stock_sw = open(STOCK_SW, encoding="utf-8").read()
    root_uuid = U()

    lib_R = extract_symbol(src, "Device:R")
    lib_MCU = extract_symbol(src, "MCU_ST_STM32F4:STM32F407VGTx")
    lib_3V3 = extract_symbol(src, "power:+3V3")
    lib_GND = extract_symbol(src, "power:GND")
    lib_FLAG = extract_symbol(src, "power:PWR_FLAG")
    lib_HG = extract_symbol(stock_disp, "CC56-12GWA")
    lib_SW = extract_symbol(stock_sw, "SW_Push")

    # --- пины MCU ---
    pins = re.findall(
        r"\(pin (\S+) \S+\s+\(at ([\d\.\-]+) ([\d\.\-]+) (\d+)\)\s+"
        r'\(length ([\d\.]+)\)\s+\(name "([^"]+)"',
        lib_MCU,
    )

    def world(px, py):
        return (round(MX + px, 2), round(MY - py, 2))

    pin_world = {}
    for etype, xs, ys, ang, ln, name in pins:
        pin_world.setdefault(name, []).append((etype, world(float(xs), float(ys))))

    used = set(PA_NAMES) | set(PC_NAMES) | {"PB0", "PB1", "PB2", "PB3"}
    rail_xy = set()
    for name, lst in pin_world.items():
        for etype, (wx, wy) in lst:
            if wy in (33.02, 177.8) and etype in ("power_in", "power_out"):
                rail_xy.add((wx, wy))

    out = []
    A = out.append

    A("(kicad_sch")
    A("\t(version 20260306)")
    A('\t(generator "eeschema")')
    A('\t(generator_version "10.0")')
    A('\t(uuid "%s")' % root_uuid)
    A('\t(paper "A4")')
    A("\t(lib_symbols")
    for lib in (lib_R, lib_MCU, lib_3V3, lib_GND, lib_FLAG):
        # переименовать ключи lib_symbols под имена из штатных библиотек
        A(lib)
    A(
        lib_HG.replace(
            '(symbol "CC56-12GWA"', '(symbol "Display_Character:CC56-12GWA"', 1
        )
    )
    A(lib_SW.replace('(symbol "SW_Push"', '(symbol "Switch:SW_Push"', 1))
    A("\t)")

    # ---------- U1 ----------
    A(mcu_instance(root_uuid))

    # ---------- шины питания из lab1 ----------
    for block in extract_instances(src, {33.02, 177.8}):
        A(retarget_power(block, root_uuid))

    # ---------- провода/перемычки шин питания lab1 ----------
    body = src[src.find("\t(wire") :]
    for m in re.finditer(
        r"\t\(wire\s+\(pts\s+(.*?)\)\s+\(stroke\s+\(width 0\)\s+"
        r'\(type default\)\s+\)\s+\(uuid "[0-9a-f\-]+"\)\s+\)',
        body,
        re.S,
    ):
        pts = re.findall(r"\(xy ([\d\.\-]+) ([\d\.\-]+)\)", m.group(1))
        ys = {float(p[1]) for p in pts}
        if ys <= {33.02, 177.8}:
            A(
                "\t(wire\n\t\t(pts\n\t\t\t%s\n\t\t)"
                % "\n\t\t\t".join("(xy %s %s)" % p for p in pts)
                + "\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)"
                '\n\t\t(uuid "%s")\n\t)' % U()
            )
    for m in re.finditer(
        r"\t\(junction\s+\(at ([\d\.\-]+) ([\d\.\-]+)\)\s+"
        r"\(diameter 0\)\s+\(color 0 0 0 0\)\s+"
        r'\(uuid "[0-9a-f\-]+"\)\s+\)',
        body,
    ):
        if float(m.group(2)) in (33.02, 177.8):
            A(
                "\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n"
                '\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)'
                % (m.group(1), m.group(2), U())
            )

    # ---------- R1-R8 + провода PAx + метки (лесенка 4+4) ----------
    for i in range(8):
        y = PA_ROWS[i]
        rx = RXS[i]
        r_l, r_r = round(rx - 3.81, 2), round(rx + 3.81, 2)
        A(resistor_instance("R%d" % (i + 1), rx, y, root_uuid))
        A(wire([(86.36, y), (r_l, y)]))
        A(label(PA_NAMES[i], 86.36, y, 0, "left"))
        A(label(PA_NAMES[i], r_l, y, 180, "right"))
        # правый вывод R — проводом напрямую на сегмент HG1
        A(wire([(r_r, y), (HG_SEGX, y)]))

    # ---------- HG1 ----------
    A(hg_instance("HG1", HG_X, HG_Y, root_uuid))
    for d in range(4):
        cc_lib = {"CC1": -2.54, "CC2": -5.08, "CC3": -7.62, "CC4": -10.16}[HG_CCS[d]]
        A(label(PC_NAMES[d], HG_CCX, round(HG_Y - cc_lib, 2), 0, "left"))
        A(label(PC_NAMES[d], 86.36, PC_ROWS[d], 0, "left"))

    # ---------- S1-S4 + GND ----------
    # Выводы PB0-PB3 U1 короткие stubs с метками. Сами свитчи стоят
    # свободным рядом на Y=110 с шагом 30 мм и цепляются к тем же
    # цепям через одноимённые метки (длинных проводов через всё поле нет).
    # Свитч Sn: вывод 1 к PB(n-1), вывод 2 напрямую на GND (как в lab2).
    for n in range(1, 5):
        y_pin = round(86.36 + 2.54 * (n - 1), 2)
        A(wire([(86.36, y_pin), (93.98, y_pin)]))
        A(label("PB%d" % (n - 1), 93.98, y_pin, 180, "right"))
    SW_Y = 122
    for n in range(1, 5):
        x = 100 + 30 * (n - 1)
        A(sw_instance("S%d" % n, x, SW_Y, root_uuid))
        A(wire([(round(x - 12.7, 2), SW_Y), (round(x - 5.08, 2), SW_Y)]))
        A(label("PB%d" % (n - 1), round(x - 12.7, 2), SW_Y, 0, "left"))
        A(wire([(round(x + 5.08, 2), SW_Y), (round(x + 10.16, 2), SW_Y)]))
        A(gnd_instance("GND%d" % (n + 1), round(x + 10.16, 2), SW_Y, root_uuid))

    # ---------- no-connect на неиспользуемые выводы U1 ----------
    done = set()
    for name, lst in pin_world.items():
        for etype, (wx, wy) in lst:
            if (wx, wy) in done:
                continue
            if name in used:
                continue
            if (wx, wy) in rail_xy:
                continue
            A('\t(no_connect\n\t\t(at %g %g)\n\t\t(uuid "%s")\n\t)' % (wx, wy, U()))
            done.add((wx, wy))

    # ---------- аннотации ----------
    A(
        text(
            "Лабораторная работа #3: генератор логических уровней "
            "на STM32F407VGT6 (STM32F4DISCOVERY)",
            22.86,
            24.13,
            2.54,
            bold=True,
        )
    )
    notes = [
        "HG1 CC56-12GWA (общий катод): сегменты a-g,DPX -> PA0-PA7 "
        "через резисторы 270 Ом;",
        "катоды CC1-CC4 -> PC0-PC3 (активный низкий уровень): "
        "CC1 = DIG1 (левый) ... CC4 = DIG4 (правый).",
        "S1-S4 (PB0-PB3, pull-up): разомкнут — лог. 1, замкнут на GND — лог. 0;",
        "вариант 4: разряды DIG1-DIG4 показывают биты S4 S3 S2 S1.",
        "Опыты со светодиодом: D1 (PA0 через 270 Ом на GND) вместо HG1, S1 на PB0.",
        "R = (3,3 - 2,0) / 0,005 ~= 260 Ом -> ближайший номинал 270 Ом.",
    ]
    # Примечания в свободной зоне под рядом свитчей.
    for n, line in enumerate(notes):
        A(text(line, 100, 145 + 3.81 * n, 1.27, bold=False))

    A('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)')
    A("\t(embedded_fonts no)")
    A(")")

    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("saved %s (%d bytes)" % (OUT, len("\n".join(out))))


# ---------------- шаблоны элементов ----------------


def wire(pts):
    return (
        "\t(wire\n\t\t(pts\n\t\t\t%s\n\t\t)"
        "\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)"
        '\n\t\t(uuid "%s")\n\t)' % ("\n\t\t\t".join("(xy %g %g)" % p for p in pts), U())
    )


def label(name, x, y, angle, side):
    just = "right bottom" if side == "right" else "left bottom"
    return (
        '\t(label "%s"\n\t\t(at %g %g %d)\n\t\t(effects\n\t\t\t(font\n'
        "\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)"
        '\n\t\t(uuid "%s")\n\t)' % (name, x, y, angle, just, U())
    )


def text(s, x, y, size, bold):
    b = "\n\t\t\t(bold yes)" if bold else ""
    return (
        '\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %g %g 0)\n'
        "\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %g %g)%s\n\t\t\t)"
        '\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "%s")\n\t)'
        % (s, x, y, size, size, b, U())
    )


def mcu_instance(root_uuid):
    return (
        '\t(symbol\n\t\t(lib_id "MCU_ST_STM32F4:STM32F407VGTx")\n'
        "\t\t(at 60.96 106.68 0)\n\t\t(unit 1)\n"
        "\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n"
        '\t\t(dnp no)\n\t\t(uuid "%s")\n'
        '\t\t(property "Reference" "U1"\n'
        "\t\t\t(at 40.64 36.83 0)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Value" "STM32F407VGT6"\n'
        "\t\t\t(at 73.66 36.83 0)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Footprint" "Package_QFP:LQFP-100_14x14mm_P0.5mm"\n'
        "\t\t\t(at 60.96 172.72 0)\n\t\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Datasheet" '
        '"https://www.st.com/resource/en/datasheet/stm32f407vg.pdf"\n'
        "\t\t\t(at 60.96 106.68 0)\n\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Description" "STMicroelectronics Arm Cortex-M4 '
        'MCU, 1024KB flash, 192KB RAM, 168 MHz, 1.8-3.6V, 82 GPIO, LQFP100"\n'
        "\t\t\t(at 60.96 106.68 0)\n\t\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(instances\n\t\t\t(project "%s"\n'
        '\t\t\t\t(path "/%s"\n\t\t\t\t\t(reference "U1")\n'
        "\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)" % (U(), PROJECT, root_uuid)
    )


def resistor_instance(ref, x, y, root_uuid):
    return (
        '\t(symbol\n\t\t(lib_id "Device:R")\n\t\t(at %g %g 90)\n'
        "\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n"
        '\t\t(dnp no)\n\t\t(uuid "%s")\n'
        '\t\t(property "Reference" "%s"\n\t\t\t(at %g %g 90)\n'
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Value" "270"\n\t\t\t(at %g %g 90)\n'
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Footprint" "Resistor_SMD:R_0805_2012Metric"\n'
        "\t\t\t(at %g %g 90)\n\t\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Datasheet" ""\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(hide yes)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Description" "Resistor"\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(hide yes)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(pin "1"\n\t\t\t(uuid "%s")\n\t\t)\n'
        '\t\t(pin "2"\n\t\t\t(uuid "%s")\n\t\t)\n'
        '\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n'
        '\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n'
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)"
        % (
            x,
            y,
            U(),
            ref,
            x,
            round(y - 2.54, 2),
            x,
            round(y + 2.54, 2),
            x,
            round(y + 1.778, 2),
            x,
            y,
            x,
            y,
            U(),
            U(),
            PROJECT,
            root_uuid,
            ref,
        )
    )


def hg_instance(ref, x, y, root_uuid):
    pins = "\n".join(
        '\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)' % (HG_PINNUM[n], U())
        for n in (["a", "b", "c", "d", "e", "f", "g", "DPX"] + HG_CCS)
    )
    return (
        '\t(symbol\n\t\t(lib_id "Display_Character:CC56-12GWA")\n'
        "\t\t(at %g %g 0)\n"
        "\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n"
        '\t\t(dnp no)\n\t\t(uuid "%s")\n'
        '\t\t(property "Reference" "%s"\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Value" "CC56-12GWA"\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Footprint" "Display_7Segment:CC56-12GWA"\n'
        "\t\t\t(at %g %g 0)\n\t\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Datasheet" '
        '"http://www.kingbrightusa.com/images/catalog/SPEC/CC56-12GWA.pdf"\n'
        "\t\t\t(at %g %g 0)\n\t\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Description" "4 digit 7 segment high efficiency '
        'red LED, common cathode"\n'
        "\t\t\t(at %g %g 0)\n\t\t\t(hide yes)\n"
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        "%s\n"
        '\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n'
        '\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n'
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)"
        % (
            x,
            y,
            U(),
            ref,
            x,
            round(y - 17.78, 2),
            x,
            round(y + 17.78, 2),
            x,
            y,
            x,
            y,
            x,
            y,
            pins,
            PROJECT,
            root_uuid,
            ref,
        )
    )


def sw_instance(ref, x, y, root_uuid):
    return (
        '\t(symbol\n\t\t(lib_id "Switch:SW_Push")\n\t\t(at %g %g 0)\n'
        "\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n"
        '\t\t(dnp no)\n\t\t(uuid "%s")\n'
        '\t\t(property "Reference" "%s"\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Value" "SW_Push"\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(pin "1"\n\t\t\t(uuid "%s")\n\t\t)\n'
        '\t\t(pin "2"\n\t\t\t(uuid "%s")\n\t\t)\n'
        '\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n'
        '\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n'
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)"
        % (
            x,
            y,
            U(),
            ref,
            x,
            round(y - 3.81, 2),
            x,
            round(y + 3.81, 2),
            U(),
            U(),
            PROJECT,
            root_uuid,
            ref,
        )
    )


def gnd_instance(ref, x, y, root_uuid):
    """Инстанс GND на выводе свитча: поза дословно как GND2 в lab2 (rot 90)."""
    return (
        '\t(symbol\n\t\t(lib_id "power:GND")\n\t\t(at %g %g 90)\n'
        "\t\t(unit 1)\n\t\t(body_style 1)\n\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n"
        '\t\t(dnp no)\n\t\t(uuid "%s")\n'
        '\t\t(property "Reference" "%s"\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(hide yes)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Value" "GND"\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Footprint" ""\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(hide yes)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Datasheet" ""\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(hide yes)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(property "Description" "Power symbol creates a global label '
        'with name \\"GND\\""\n\t\t\t(at %g %g 0)\n'
        "\t\t\t(hide yes)\n\t\t\t(show_name no)\n"
        "\t\t\t(do_not_autoplace no)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        '\t\t(pin "1"\n\t\t\t(uuid "%s")\n\t\t)\n'
        '\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n'
        '\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n'
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)"
        % (
            x,
            y,
            U(),
            ref,
            x,
            round(y - 2.54, 2),
            x,
            round(y + 2.54, 2),
            x,
            y,
            x,
            y,
            x,
            y,
            U(),
            PROJECT,
            root_uuid,
            ref,
        )
    )


if __name__ == "__main__":
    main()
