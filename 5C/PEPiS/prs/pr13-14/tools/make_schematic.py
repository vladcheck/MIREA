#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор схемы KiCad 10 для практики 13-14 (АЦП, вариант 4).

Создаёт проект kicad/pr13-14.kicad_pro и три листа:
  pr13-14.kicad_sch            — корневой лист с двумя листами-заданиями;
  adc_investigation.kicad_sch  — задание 1 (аналог рис. 58 методички):
                                 исследование 16-разрядного виртуального АЦП;
  mcu_connection.kicad_sch     — задание 2 (аналог рис. 60 методички):
                                 подключение МК-51 к 16-разрядному АЦП.

Схема пишется напрямую в S-expression (альтернативный путь авторинга
согласно AGENTS.md, когда MCP недоступен). Все координаты — на сетке
1,27 мм (проверяется assert-ами).

Запуск: python3 tools/make_schematic.py
"""

import uuid
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "kicad"

GRID = 1.27
ROOT_UUID = "9d1c2f74-3a6b-4c1e-9f02-7b8e5d1a2c34"
SHEET1_UUID = "1a7b3c5d-9e2f-4a6b-8c1d-2e4f6a8b0c1d"
SHEET2_UUID = "2b8c4d6e-0f3a-5b7c-9d2e-3f5a7c9e1b2d"
PATH_SHEET1 = f"/{ROOT_UUID}/{SHEET1_UUID}"
PATH_SHEET2 = f"/{ROOT_UUID}/{SHEET2_UUID}"


def uid():
    return str(uuid.uuid4())


def g(*vals):
    """Проверка попадания координат на сетку 1,27 мм."""
    for v in vals:
        assert abs(v / GRID - round(v / GRID)) < 1e-6, f"вне сетки 1.27: {v}"


def num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s else "0"


class Sheet:
    def __init__(self, paper, title, path):
        self.paper = paper
        self.title = title
        self.path = path
        self.libs = []      # определения символов (текстовые блоки)
        self.items = []     # провода, символы, метки, ...

    def add(self, s):
        self.items.append(s)

    def render(self, root_uuid):
        parts = [
            "(kicad_sch",
            "\t(version 20260306)",
            '\t(generator "eeschema")',
            '\t(generator_version "10.0")',
            f'\t(uuid "{root_uuid}")',
            f'\t(paper "{self.paper}")',
            "\t(title_block",
            f'\t\t(title "{self.title}")',
            '\t\t(date "2026-11-13")',
            '\t\t(rev "1.0")',
            "\t)",
        ]
        if self.libs:
            parts.append("\t(lib_symbols")
            parts.extend(self.libs)
            parts.append("\t)")
        parts.extend(self.items)
        parts.append("\t(sheet_instances")
        parts.append(f'\t\t(path "{self.path}" (page "1"))')
        parts.append("\t)")
        parts.append(")")
        return "\n".join(parts) + "\n"


def wire(x1, y1, x2, y2):
    g(x1, y1, x2, y2)
    return (
        "\t(wire\n"
        "\t\t(pts\n"
        f"\t\t\t(xy {num(x1)} {num(y1)})\n"
        f"\t\t\t(xy {num(x2)} {num(y2)})\n"
        "\t\t)\n"
        "\t\t(stroke (width 0) (type default))\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def junction(x, y):
    g(x, y)
    return (
        f"\t(junction (at {num(x)} {num(y)}) (diameter 0) (color 0 0 0 0)\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def net_label(name, x, y, rot=0, justify="left"):
    g(x, y)
    return (
        f'\t(label "{name}"\n'
        f"\t\t(at {num(x)} {num(y)} {rot})\n"
        "\t\t(effects (font (size 1.27 1.27)) (justify "
        + ("right" if justify == "right" else "left")
        + "))\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def text(s, x, y, size=1.27):
    g(x, y)
    return (
        f'\t(text "{s}"\n'
        f"\t\t(at {num(x)} {num(y)} 0)\n"
        "\t\t(effects (font (size "
        f"{num(size)} {num(size)}"
        ")) (justify left bottom))\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def no_connect(x, y):
    g(x, y)
    return (
        f"\t(no_connect (at {num(x)} {num(y)})\n"
        f'\t\t(uuid "{uid()}")\n'
        "\t)"
    )


def _prop(name, value, x, y, hide=False, size=1.27):
    h = "\n\t\t(hide yes)" if hide else ""
    return (
        f'\t(property "{name}" "{value}"\n'
        f"\t\t(at {num(x)} {num(y)} 0){h}\n"
        "\t\t(show_name no)\n"
        "\t\t(do_not_autoplace no)\n"
        "\t\t(effects (font (size "
        f"{num(size)} {num(size)}"
        ")))\n"
        "\t)"
    )


def instance(lib_id, ref, value, x, y, path, rot=0, unit=1, pins=(),
             val_size=1.27, extra_props=None):
    """Экземпляр символа на листе."""
    g(x, y)
    parts = [
        "\t(symbol",
        f'\t\t(lib_id "{lib_id}")',
        f"\t\t(at {num(x)} {num(y)} {rot})",
        f"\t\t(unit {unit})",
        "\t\t(body_style 1)",
        "\t\t(exclude_from_sim no)",
        "\t\t(in_bom yes)",
        "\t\t(on_board yes)",
        "\t\t(dnp no)",
        f'\t\t(uuid "{uid()}")',
    ]
    parts.append(_prop("Reference", ref, x, y - 2.54, size=1.27))
    parts.append(_prop("Value", value, x, y + 2.54, size=val_size))
    parts.append(_prop("Footprint", "", x, y, hide=True))
    parts.append(_prop("Datasheet", "", x, y, hide=True))
    parts.append(_prop("Description", "", x, y, hide=True))
    for p in extra_props or []:
        parts.append(_prop(p[0], p[1], x, y, hide=True))
    for p in pins:
        parts.append(f'\t\t(pin "{p}"\n\t\t\t(uuid "{uid()}")\n\t\t)')
    parts.append(
        "\t\t(instances\n"
        '\t\t\t(project "pr13-14"\n'
        f'\t\t\t\t(path "{path}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f"\t\t\t\t\t(unit {unit})\n"
        "\t\t\t\t)\n"
        "\t\t\t)\n"
        "\t\t)"
    )
    parts.append("\t)")
    return "\n".join(parts)


def power(lib, value, ref, x, y, path, rot=0):
    g(x, y)
    return instance(lib, ref, value, x, y, path, rot=rot, pins=("1",),
                    val_size=1.27)


# ---------------------------------------------------------------------------
# Определения собственных символов (встраиваются в lib_symbols листа)
# ---------------------------------------------------------------------------

def _pin(ptype, x, y, rot, length, name, number):
    g(x, y)
    return (
        f"\t\t\t(pin {ptype} line\n"
        f"\t\t\t\t(at {num(x)} {num(y)} {rot})\n"
        f"\t\t\t\t(length {num(length)})\n"
        f'\t\t\t\t(name "{name}"\n'
        "\t\t\t\t\t(effects (font (size 1.27 1.27)))\n"
        "\t\t\t\t)\n"
        f'\t\t\t\t(number "{number}"\n'
        "\t\t\t\t\t(effects (font (size 1.27 1.27)))\n"
        "\t\t\t\t)\n"
        "\t\t\t)"
    )


def _sym_header(lib_name, ref_letter, value, desc, ref_y, val_y):
    return [
        f'\t(symbol "pr1314:{lib_name}"',
        "\t\t(pin_names (offset 1.016))",
        "\t\t(exclude_from_sim no)",
        "\t\t(in_bom yes)",
        "\t\t(on_board yes)",
        f'\t\t(property "Reference" "{ref_letter}"',
        f"\t\t\t(at 0 {num(ref_y)} 0)",
        "\t\t\t(effects (font (size 1.27 1.27))))",
        f'\t\t(property "Value" "{value}"',
        f"\t\t\t(at 0 {num(val_y)} 0)",
        "\t\t\t(effects (font (size 1.27 1.27))))",
        '\t\t(property "Footprint" "" (at 0 0 0) (hide yes)',
        "\t\t\t(effects (font (size 1.27 1.27))))",
        '\t\t(property "Datasheet" "" (at 0 0 0) (hide yes)',
        "\t\t\t(effects (font (size 1.27 1.27))))",
        f'\t\t(property "Description" "{desc}" (at 0 0 0) (hide yes)',
        "\t\t\t(effects (font (size 1.27 1.27))))",
    ]


def sym_adc16():
    """Виртуальный 16-разрядный АЦП (аналог элемента Mixed Multisim)."""
    L = _sym_header("VIRT_ADC16", "A", "VIRT_ADC16",
                    "Виртуальный АЦП, 16 разрядов", 33.02, -29.21)
    L.append(f'\t\t(symbol "VIRT_ADC16_0_1"')
    L.append(
        "\t\t\t(rectangle (start -22.86 30.48) (end 22.86 -25.4)"
        "\n\t\t\t\t(stroke (width 0.254) (type default))"
        "\n\t\t\t\t(fill (type background))\n\t\t\t)"
    )
    L.append('\t\t\t(text "АЦП 16 бит" (at 0 27.94 0)')
    L.append("\t\t\t\t(effects (font (size 2.54 2.54))))")
    L.append("\t\t)")
    L.append('\t\t(symbol "VIRT_ADC16_1_1"')
    L.append(_pin("input", -26.67, 27.94, 0, 3.81, "Vin", "1"))
    L.append(_pin("input", -26.67, 20.32, 0, 3.81, "Vref+", "2"))
    L.append(_pin("input", -26.67, 12.7, 0, 3.81, "Vref-", "3"))
    L.append(_pin("input", -26.67, -12.7, 0, 3.81, "SOC", "4"))
    L.append(_pin("input", -26.67, -20.32, 0, 3.81, "OE", "5"))
    L.append(_pin("output", 26.67, 27.94, 180, 3.81, "EOC", "6"))
    for i in range(16):
        L.append(_pin("output", 26.67, 20.32 - 2.54 * i, 180, 3.81,
                      f"D{15 - i}", str(7 + i)))
    L.append("\t\t)")
    L.append("\t\t(embedded_fonts no)")
    L.append("\t)")
    return "\n".join(L)


def sym_dac16():
    """Виртуальный ЦАП (аналог элемента Mixed Multisim)."""
    L = _sym_header("VIRT_DAC16", "A", "VIRT_DAC16",
                    "Виртуальный ЦАП, 16 разрядов", 33.02, -29.21)
    L.append('\t\t(symbol "VIRT_DAC16_0_1"')
    L.append(
        "\t\t\t(rectangle (start -22.86 30.48) (end 22.86 -25.4)"
        "\n\t\t\t\t(stroke (width 0.254) (type default))"
        "\n\t\t\t\t(fill (type background))\n\t\t\t)"
    )
    L.append('\t\t\t(text "ЦАП 16 бит" (at 0 27.94 0)')
    L.append("\t\t\t\t(effects (font (size 2.54 2.54))))")
    L.append("\t\t)")
    L.append('\t\t(symbol "VIRT_DAC16_1_1"')
    for i in range(16):
        L.append(_pin("input", -26.67, 20.32 - 2.54 * i, 0, 3.81,
                      f"D{15 - i}", str(1 + i)))
    L.append(_pin("output", 26.67, 0, 180, 3.81, "Vout", "17"))
    L.append("\t\t)")
    L.append("\t\t(embedded_fonts no)")
    L.append("\t)")
    return "\n".join(L)


def sym_probe():
    """Пробник (индикатор логического уровня)."""
    L = _sym_header("PROBE", "X", "PROBE", "Логический пробник", 3.81, -3.81)
    L.append('\t\t(symbol "PROBE_0_1"')
    L.append("\t\t\t(circle (center 0 0) (radius 1.27)")
    L.append("\t\t\t\t(stroke (width 0.254) (type default))")
    L.append("\t\t\t\t(fill (type outline))\n\t\t\t)")
    L.append("\t\t)")
    L.append('\t\t(symbol "PROBE_1_1"')
    L.append(_pin("passive", -5.08, 0, 0, 3.81, "X", "1"))
    L.append("\t\t)")
    L.append("\t\t(embedded_fonts no)")
    L.append("\t)")
    return "\n".join(L)


def _balanced(src, start):
    """Индекс конца s-expr блока, начинающегося в start (на '(')."""
    depth = 0
    for i in range(start, len(src)):
        ch = src[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError("unbalanced")


def hoist_pins(def_text):
    """Переносит (pin ...) из вложенных подсимволов в корень определения.

    Формат встраиваемых определений символов в .kicad_sch отличается от
    формата .kicad_sym: выводы хранятся в корне определения, а вложенные
    блоки NAME_x_y содержат только графику. Без переноса eeschema
    неверно интерпретирует геометрию выводов (переворот по оси Y).
    """
    pins = []
    out = []
    i = 0
    while i < len(def_text):
        j = def_text.find("(pin ", i)
        if j < 0:
            out.append(def_text[i:])
            break
        out.append(def_text[i:j])
        end = _balanced(def_text, j)
        pins.append(def_text[j:end])
        i = end
    text = "".join(out)
    anchor = text.rfind("(embedded_fonts no)")
    if anchor < 0:
        anchor = text.rfind("\n\t)")
    insert_at = text.rfind("\n", 0, anchor)
    block = "".join("\t" + p.strip() + "\n" for p in pins)
    return text[:insert_at + 1] + block + text[insert_at + 1:]


def sym_inv1():
    """Инвертор (элемент U2A типа 74LS04) — одноэлементный символ."""
    L = _sym_header("INV1", "U", "74LS04", "Инвертор (74LS04), элемент A",
                    5.08, -5.08)
    L.append('\t\t(symbol "INV1_0_1"')
    L.append("\t\t\t(polyline")
    L.append("\t\t\t\t(pts")
    L.append("\t\t\t\t\t(xy -3.81 3.81) (xy -3.81 -3.81) (xy 3.81 0)")
    L.append("\t\t\t\t\t(xy -3.81 3.81)")
    L.append("\t\t\t\t)")
    L.append("\t\t\t\t(stroke (width 0.254) (type default))")
    L.append("\t\t\t\t(fill (type background))\n\t\t\t)")
    L.append("\t\t\t(circle (center 4.953 0) (radius 0.508)")
    L.append("\t\t\t\t(stroke (width 0.254) (type default))")
    L.append("\t\t\t\t(fill (type none))\n\t\t\t)")
    L.append("\t\t)")
    L.append('\t\t(symbol "INV1_1_1"')
    L.append(_pin("input", -7.62, 0, 0, 3.81, "A", "1"))
    L.append(_pin("output", 7.62, 0, 180, 3.81, "Y", "2"))
    L.append("\t\t)")
    L.append("\t\t(embedded_fonts no)")
    L.append("\t)")
    return "\n".join(L)


CUSTOM_LIBS = [sym_adc16(), sym_dac16(), sym_probe(), sym_inv1()]
CUSTOM_LIBS_EMBEDDED = [hoist_pins(d) for d in CUSTOM_LIBS]
ADC_PINS = [str(n) for n in range(1, 23)]
DAC_PINS = [str(n) for n in range(1, 18)]
PROBE_PINS = ["1"]

# ---------------------------------------------------------------------------
# Встраивание системных символов: на машине нет глобальной таблицы
# библиотек (~/.config/kicad отсутствует), поэтому kicad-cli разрешает
# символы только из lib_symbols самого листа (как в pr7-8).
# ---------------------------------------------------------------------------

KICAD_SYMS = Path(
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
)


def extract_symbol(libfile, name):
    """Вырезает блок (symbol "NAME" ...) из библиотеки .kicad_sym."""
    src = (KICAD_SYMS / libfile).read_text(encoding="utf-8")
    start = src.index(f'(symbol "{name}"')
    depth = 0
    for i in range(start, len(src)):
        ch = src[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    raise ValueError(f"unbalanced block for {name}")


def embed(nickname, libfile, name):
    """Определение символа с никнеймом библиотеки для lib_symbols листа."""
    block = extract_symbol(libfile, name)
    return block.replace(f'(symbol "{name}"', f'(symbol "{nickname}:{name}"', 1)


def system_embeds(libspecs):
    return [embed(nick, fn, nm) for nick, fn, nm in libspecs]


EMBEDS_SHEET1 = [hoist_pins(d) for d in system_embeds([
    ("Simulation_SPICE", "Simulation_SPICE.kicad_sym", "VDC"),
    ("Simulation_SPICE", "Simulation_SPICE.kicad_sym", "VPULSE"),
    ("Simulation_SPICE", "Simulation_SPICE.kicad_sym", "VOLTMETER_DIFF"),
    ("power", "power.kicad_sym", "GND"),
    ("power", "power.kicad_sym", "+5V"),
    ("power", "power.kicad_sym", "PWR_FLAG"),
])]

EMBEDS_SHEET2 = [hoist_pins(d) for d in system_embeds([
    ("Simulation_SPICE", "Simulation_SPICE.kicad_sym", "VDC"),
    ("MCU_Microchip_8051", "MCU_Microchip_8051.kicad_sym", "AT89x51xxP"),
    ("power", "power.kicad_sym", "GND"),
    ("power", "power.kicad_sym", "+5V"),
    ("power", "power.kicad_sym", "PWR_FLAG"),
])]


# ---------------------------------------------------------------------------
# Лист 1: исследование АЦП (аналог рис. 58 методички).
# Соединения — метками цепей на выводах и контактами вывод-вывод (стиль
# pr7-8). ВАЖНО: kicad-cli 10.0.8 (macOS, headless) размещает выводы
# символов зеркально по оси Y относительно точки привязки, поэтому все
# привязки (метки, земля, пробники) ставятся в «истинные для ERC»
# координаты: anchor = (x + dx, y - dy) для вывода с локальным (dx, dy).
# Нетлиста это не касается: связи (ref, pin) корректны.
# ---------------------------------------------------------------------------

def build_sheet1():
    s = Sheet("A3", "ПР 13-14, задание 1. Исследование 16-разрядного АЦП",
              PATH_SHEET1)
    s.libs = EMBEDS_SHEET1 + CUSTOM_LIBS_EMBEDDED
    p = PATH_SHEET1
    # A1 — АЦП в (160.02, 140.97); ERC-истинные выводы:
    ax, ay = 160.02, 140.97
    s.add(instance("pr1314:VIRT_ADC16", "A1", "VIRT_ADC16", ax, ay, p,
                   pins=ADC_PINS))
    vin_e = (133.35, 113.03)    # Vin  (+27.94 -> зеркально)
    vrp_e = (133.35, 120.65)    # Vref+
    vrm_e = (133.35, 128.27)    # Vref-
    soc_e = (133.35, 153.67)    # SOC  (-12.7)
    oe_e = (133.35, 161.29)     # OE   (-20.32)
    eoc_e = (186.69, 113.03)    # EOC
    data_e = [(186.69, 120.65 + 2.54 * i) for i in range(16)]  # D15..D0

    # V1 (+5 В): '+' ERC (105.41, 151.13), '-' ERC (105.41, 161.29)
    v1 = (105.41, 156.21)
    s.add(instance("Simulation_SPICE:VDC", "V1", "+5 В", *v1, p, pins=("1", "2")))
    s.add(net_label("VREF+", 105.41, 151.13, justify="right"))
    s.add(power("power:GND", "GND", "GND1", 105.41, 161.29, p))
    # V3 (uвх): '+' ERC (76.2, 154.94), '-' ERC (76.2, 165.1)
    v3 = (76.2, 160.02)
    s.add(instance("Simulation_SPICE:VDC", "V3", "Uвх", *v3, p, pins=("1", "2")))
    s.add(net_label("VIN", 76.2, 154.94, justify="right"))
    s.add(power("power:GND", "GND", "GND2", 76.2, 165.1, p))
    # Vref+, Vin АЦП — метки; Vref- — земля
    s.add(net_label("VREF+", vrp_e[0], vrp_e[1], justify="right"))
    s.add(net_label("VIN", vin_e[0], vin_e[1], justify="right"))
    s.add(power("power:GND", "GND", "GND3", vrm_e[0], vrm_e[1], p))
    # V4 (VPULSE 1 кГц): '+' ERC (105.41, 118.11), '-' ERC (105.41, 128.27)
    v4 = (105.41, 123.19)
    s.add(instance("Simulation_SPICE:VPULSE", "V4", "1 кГц", *v4, p,
                   pins=("1", "2")))
    s.add(net_label("SOC", 105.41, 118.11, justify="right"))
    s.add(power("power:GND", "GND", "GND4", 105.41, 128.27, p))
    s.add(net_label("SOC", soc_e[0], soc_e[1], justify="right"))
    # U2 — инвертор (74LS04), выводы на оси Y (инвариантны)
    u2 = (128.27, 139.7)
    s.add(instance("pr1314:INV1", "U2", "74LS04", *u2, p, pins=("1", "2")))
    s.add(net_label("SOC", 120.65, 139.7, justify="right"))
    s.add(net_label("OE", 135.89, 139.7))
    s.add(net_label("OE", oe_e[0], oe_e[1], justify="right"))
    # A2 — ЦАП в (247.65, 140.97); ERC-выводы данных:
    dx, dy = 247.65, 140.97
    s.add(instance("pr1314:VIRT_DAC16", "A2", "VIRT_DAC16", dx, dy, p,
                   pins=DAC_PINS))
    # строка y = 120.65 + 2.54*k — это разряд D(15-k) (зеркальная ось Y)
    for k in range(16):
        b = 15 - k
        ye = 120.65 + 2.54 * k
        s.add(net_label(f"D{b}", 186.69, ye, justify="right"))
        # пробник Xb: контакт вывод-вывод с выходом АЦП
        s.add(instance("pr1314:PROBE", f"X{b}", "PROBE", 191.77,
                       ye, p, pins=PROBE_PINS))
        s.add(text(f"X{b}", 193.04, ye))
        s.add(net_label(f"D{b}", 220.98, ye, justify="right"))
    # EOC -> пробник X16 (контакт)
    s.add(instance("pr1314:PROBE", "X16", "PROBE", eoc_e[0] + 5.08, eoc_e[1],
                   p, pins=PROBE_PINS))
    s.add(text("EOC", eoc_e[0] + 7.62, eoc_e[1]))
    # U1 — вольтметр: '+' ERC должен совпасть с Vout (274.32, 140.97)
    # '+' local (0, +5.08) -> ERC (x, y - 5.08) = (274.32, 140.97) => y = 146.05
    u1 = (274.32, 146.05)
    s.add(instance("Simulation_SPICE:VOLTMETER_DIFF", "U1", "В", *u1, p,
                   pins=("1", "2", "3")))
    s.add(power("power:GND", "GND", "GND6", 274.32, 151.13, p))  # '-' ERC
    s.add(no_connect(279.4, 146.05))                             # out ERC
    # флаги питания (источник для ERC по сети GND)
    s.add(instance("power:PWR_FLAG", "PWR1", "PWR_FLAG", 85.09, 176.53, p,
                   pins=("1",)))
    s.add(net_label("GND", 85.09, 176.53, justify="right"))
    # подписи
    s.add(text("Задание 1. Схема исследования точности 16-разрядного "
               "виртуального АЦП (вариант 4, аналог рис. 58 методички)",
               63.5, 185.42, size=2.54))
    s.add(text("Vref+ = +5 В (V1), Vref- = 0 В (GND); uвх — источник V3; "
               "V4 — синхронизация 1 кГц; U2 — 74LS04 (OE в противофазе SOC); "
               "U1 — вольтметр на выходе ЦАП; связи — метками цепей",
               63.5, 29.21))
    return s


# ---------------------------------------------------------------------------
# Лист 2: подключение МК-51 к АЦП (аналог рис. 60 методички)
# ---------------------------------------------------------------------------

def build_sheet2():
    s = Sheet("A3", "ПР 13-14, задание 2. Подключение МК-51 к 16-разрядному АЦП",
              PATH_SHEET2)
    s.libs = EMBEDS_SHEET2 + CUSTOM_LIBS_EMBEDDED
    p = PATH_SHEET2
    # A1 — АЦП в (118.11, 135.89); ERC-истинные выводы:
    ax, ay = 118.11, 135.89
    s.add(instance("pr1314:VIRT_ADC16", "A1", "VIRT_ADC16", ax, ay, p,
                   pins=ADC_PINS))
    vin_e = (91.44, 107.95)
    vrp_e = (91.44, 115.57)
    vrm_e = (91.44, 123.19)
    soc_e = (91.44, 148.59)
    oe_e = (91.44, 156.21)
    eoc_e = (144.78, 107.95)
    data_e = [(144.78, 115.57 + 2.54 * i) for i in range(16)]  # D15..D0
    # U1 — AT89C51 в (222.25, 95.25); ERC-истинные выводы (зеркально):
    mx, my = 222.25, 95.25
    mcu_pins = [str(n) for n in range(1, 41)]
    s.add(instance("MCU_Microchip_8051:AT89x51xxP", "U1", "AT89C51",
                   mx, my, p, pins=mcu_pins))
    # левый край (local y -> ERC -y): P1.i local +22.86-2.54i -> ERC 72.39+2.54i
    p1_e = {i: (207.01, 72.39 + 2.54 * i) for i in range(8)}
    # P3.k local -2.54-2.54k -> ERC 97.79+2.54k; RST +27.94 -> 67.31;
    # XTAL1/2 -25.4/-27.94 -> 120.65/123.19; EA -33.02 -> 128.27
    p3_6_e = (207.01, 113.03)
    p3_7_e = (207.01, 115.57)
    # правый край: P0.i +22.86-2.54i -> 72.39+2.54i; P2.i -2.54-2.54i -> 97.79+2.54i
    p0_e = {i: (237.49, 72.39 + 2.54 * i) for i in range(8)}
    p2_e = {i: (237.49, 97.79 + 2.54 * i) for i in range(8)}
    vcc_e = (222.25, 54.61)    # VCC local +40.64 -> ERC -
    gnd_e = (222.25, 135.89)   # GND local -40.64 -> ERC +
    # D0..D7 -> P1.0..P1.7 (метки)
    for i in range(8):
        s.add(net_label(f"D{i}", data_e[15 - i][0], data_e[15 - i][1],
                        justify="right"))
        s.add(net_label(f"D{i}", p1_e[i][0], p1_e[i][1], justify="right"))
    # D8..D15 -> P0.0..P0.7 (метки)
    for k in range(8):
        bit = 15 - k
        s.add(net_label(f"D{bit}", data_e[k][0], data_e[k][1], justify="right"))
        s.add(net_label(f"D{bit}", p0_e[k][0], p0_e[k][1]))
    # EOC -> P3.7 (метки)
    s.add(net_label("EOC", eoc_e[0], eoc_e[1], justify="right"))
    s.add(net_label("EOC", p3_7_e[0], p3_7_e[1], justify="right"))
    # P3.6 -> SOC (метки)
    s.add(net_label("SOC", p3_6_e[0], p3_6_e[1], justify="right"))
    s.add(net_label("SOC", soc_e[0], soc_e[1], justify="right"))
    # OE -> земля, Vin/Vref+ — метки, Vref- — земля
    s.add(power("power:GND", "GND", "GND1", oe_e[0], oe_e[1], p))
    s.add(net_label("VIN", vin_e[0], vin_e[1], justify="right"))
    s.add(net_label("VREF+", vrp_e[0], vrp_e[1], justify="right"))
    s.add(power("power:GND", "GND", "GND4", vrm_e[0], vrm_e[1], p))
    # V2 (+5 В): '+' ERC (48.26, 146.05), '-' ERC (48.26, 156.21)
    v2 = (48.26, 151.13)
    s.add(instance("Simulation_SPICE:VDC", "V2", "+5 В", *v2, p, pins=("1", "2")))
    s.add(net_label("VREF+", 48.26, 146.05, justify="right"))
    s.add(power("power:GND", "GND", "GND2", 48.26, 156.21, p))
    # V1 (uвх): '+' ERC (76.2, 154.94), '-' ERC (76.2, 165.1)
    v1 = (76.2, 160.02)
    s.add(instance("Simulation_SPICE:VDC", "V1", "Uвх", *v1, p, pins=("1", "2")))
    s.add(net_label("VIN", 76.2, 154.94, justify="right"))
    s.add(power("power:GND", "GND", "GND3", 76.2, 165.1, p))
    # питание МК (ERC-истинные позиции)
    s.add(power("power:+5V", "+5V", "+5V1", vcc_e[0], vcc_e[1], p))
    s.add(power("power:GND", "GND", "GND5", gnd_e[0], gnd_e[1], p))
    # P2 -> пробники X0..X7 (контакт вывод-вывод)
    for i in range(8):
        s.add(instance("pr1314:PROBE", f"X{i}", "PROBE",
                       p2_e[i][0] + 5.08, p2_e[i][1], p, pins=PROBE_PINS))
        s.add(text(f"X{i}", p2_e[i][0] + 7.62, p2_e[i][1]))
    # флаг питания сети +5V (GND-флаг — на листе 1, сеть глобальная)
    s.add(instance("power:PWR_FLAG", "PWR2", "PWR_FLAG", 245.11, 60.96, p,
                   pins=("1",)))
    s.add(net_label("+5V", 245.11, 60.96, justify="right"))
    # неиспользуемые выводы МК (ERC-истинные позиции)
    nc_left = [
        (207.01, 67.31),    # RST
        (207.01, 120.65),   # XTAL1
        (207.01, 123.19),   # XTAL2
        (207.01, 128.27),   # EA/Vpp
    ] + [(207.01, 97.79 + 2.54 * k) for k in range(6)]  # P3.0..P3.5
    nc_right = [
        (237.49, 120.65),   # PSEN
        (237.49, 123.19),   # ALE
    ]
    for x, y in nc_left + nc_right:
        s.add(no_connect(x, y))
    # подписи
    s.add(text("Задание 2. Подключение МК-51 (AT89C51) к 16-разрядному АЦП "
               "(вариант 4, аналог рис. 60 методички)",
               48.26, 180.34, size=2.54))
    s.add(text("P1 <- D0…D7, P0 <- D8…D15 (метки цепей); P2 -> пробники "
               "X0…X7; P3.6 -> SOC; P3.7 <- EOC; OE = 0 (GND) — выходы АЦП "
               "разрешены постоянно; связи — метками цепей",
               48.26, 38.1))
    return s


# ---------------------------------------------------------------------------
# Корневой лист
# ---------------------------------------------------------------------------

def build_root():
    s = Sheet("A3", "Практическое занятие 13-14. АЦП, вариант 4", "/")
    s.add(
        f"\t(sheet\n"
        f"\t\t(at 25.4 152.4)\n"
        f"\t\t(size 165.1 63.5)\n"
        f"\t\t(fields_autoplaced yes)\n"
        f"\t\t(stroke (width 0.1524) (type solid))\n"
        f"\t\t(fill (color 0 0 0 0.0))\n"
        f'\t\t(uuid "{SHEET1_UUID}")\n'
        + _prop("Sheetname", "Задание 1. Исследование АЦП", 27.94, 217.17,
                size=2.54)
        + _prop("Sheetfile", "adc_investigation.kicad_sch", 27.94, 151.13,
                size=1.27)
        + "\t\t(instances\n"
          '\t\t\t(project "pr13-14"\n'
        f'\t\t\t\t(path "/{ROOT_UUID}" (page "2"))\n'
          "\t\t\t)\n"
          "\t\t)\n"
          "\t)"
    )
    s.add(
        f"\t(sheet\n"
        f"\t\t(at 212.09 152.4)\n"
        f"\t\t(size 165.1 63.5)\n"
        f"\t\t(fields_autoplaced yes)\n"
        f"\t\t(stroke (width 0.1524) (type solid))\n"
        f"\t\t(fill (color 0 0 0 0.0))\n"
        f'\t\t(uuid "{SHEET2_UUID}")\n'
        + _prop("Sheetname", "Задание 2. МК-51 + АЦП", 214.63, 217.17,
                size=2.54)
        + _prop("Sheetfile", "mcu_connection.kicad_sch", 214.63, 151.13,
                size=1.27)
        + "\t\t(instances\n"
          '\t\t\t(project "pr13-14"\n'
        f'\t\t\t\t(path "/{ROOT_UUID}" (page "3"))\n'
          "\t\t\t)\n"
          "\t\t)\n"
          "\t)"
    )
    s.add(text("Практическое занятие 13-14 «Изучение принципов работы "
               "аналого-цифровых преобразователей»", 63.5, 234.95, size=2.54))
    s.add(text("Вариант 4 (табл. 18 методички): 16-разрядный АЦП, "
               "Vref+ = +5 В, Vref- = 0 В", 63.5, 228.6, size=1.27))
    return s


PROJ = """{
  "meta": {
    "filename": "pr13-14.kicad_pro",
    "version": 3
  },
  "schematic": {
    "annotate_start_num": 0,
    "bom_export_filename": "",
    "bom_fmt_presets": [],
    "bom_fmt_settings": {
      "field_delimiter": ",",
      "keep_line_breaks": false,
      "keep_tabs": false,
      "name_only": false,
      "output_file_name": "",
      "ref_delimiter": ",",
      "ref_range_delimiter": "",
      "string_delimiter": "\\""
    },
    "bom_presets": [],
    "bom_settings": {
      "exclude_dnp": false,
      "fields_ordered": [
        {
          "group_by": false,
          "label": "Reference",
          "name": "Reference",
          "show": true
        },
        {
          "group_by": true,
          "label": "Value",
          "name": "Value",
          "show": true
        },
        {
          "group_by": false,
          "label": "Datasheet",
          "name": "Datasheet",
          "show": true
        },
        {
          "group_by": false,
          "label": "Footprint",
          "name": "Footprint",
          "show": true
        },
        {
          "group_by": false,
          "label": "Qty",
          "name": "${QUANTITY}",
          "show": true
        },
        {
          "group_by": true,
          "label": "DNP",
          "name": "${DNP}",
          "show": true
        }
      ],
      "group_symbols": true,
      "name_only": false,
      "sort_asc": true,
      "sort_field": "Reference"
    },
    "connection_grid_size": 1270,
    "drawing": {
      "dashed_lines_dash_length_ratio": 12.0,
      "dashed_lines_gap_length_ratio": 3.0,
      "default_line_thickness": 6.0,
      "default_text_size": 50.0,
      "field_names": [],
      "intersheets_ref_own_page_extension": "({SUPER_PAGE_ID})",
      "intersheets_ref_prefix": "",
      "intersheets_ref_short": false,
      "intersheets_ref_show": false,
      "intersheets_ref_suffix": "",
      "junction_size_choice": 3,
      "label_size_ratio": 0.375,
      "operating_point_overlay_i_precision": 3,
      "operating_point_overlay_i_suffix": "A",
      "operating_point_overlay_v_precision": 3,
      "operating_point_overlay_v_suffix": "V",
      "overbar_offset_ratio": 1.23,
      "pin_symbol_size": 25.0,
      "text_offset_ratio": 0.15
    },
    "legacy_lib_dir": "",
    "legacy_lib_list": [],
    "meta": {
      "version 2": 1
    },
    "net_format_name": "",
    "ngspice": {
      "fix_include_paths": true,
      "meta": {
        "version 0": 1
      },
      "model_mode": 0,
      "workbook_filename": ""
    },
    "page_layout_descr_file": "",
    "plot_directory": "",
    "spice_adjust_passive_values": false,
    "spice_current_sheet_as_root": false,
    "spice_external_command": "spice \"%I\"",
    "spice_model_current_sheet_as_root": true,
    "spice_save_all_currents": false,
    "spice_save_all_dissipations": false,
    "spice_save_all_voltages": false,
    "subpart_first_matching": false,
    "subpart_keep_annotation": true
  }
}
"""


SYS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
SYM_LIB_TABLE = f'''(sym_lib_table
  (lib (name "pr1314") (type "KiCad") (uri "${{KIPRJMOD}}/pr1314.kicad_sym") (options "") (descr "Виртуальные модели АЦП/ЦАП и пробники ПР 13-14"))
  (lib (name "power") (type "KiCad") (uri "{SYS}/power.kicad_sym") (options "") (descr "Power symbols"))
  (lib (name "Simulation_SPICE") (type "KiCad") (uri "{SYS}/Simulation_SPICE.kicad_sym") (options "") (descr "SPICE sources"))
  (lib (name "MCU_Microchip_8051") (type "KiCad") (uri "{SYS}/MCU_Microchip_8051.kicad_sym") (options "") (descr "8051 MCUs"))
)
'''


def write_sym_lib():
    """Отдельная библиотека символов проекта (имена без никнейма)."""
    defs = "\n".join(
        d.replace('(symbol "pr1314:', '(symbol "')
        for d in CUSTOM_LIBS
    )
    return (
        "(kicad_symbol_lib\n"
        "\t(version 20251024)\n"
        '\t(generator "kicad_symbol_editor")\n'
        '\t(generator_version "10.0")\n'
        f"{defs}"
        ")\n"
    )


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "pr13-14.kicad_pro").write_text(PROJ, encoding="utf-8")
    (BASE / "sym-lib-table").write_text(SYM_LIB_TABLE, encoding="utf-8")
    (BASE / "pr1314.kicad_sym").write_text(write_sym_lib(), encoding="utf-8")
    (BASE / "pr13-14.kicad_sch").write_text(build_root().render(ROOT_UUID),
                                            encoding="utf-8")
    (BASE / "adc_investigation.kicad_sch").write_text(
        build_sheet1().render(SHEET1_UUID), encoding="utf-8")
    (BASE / "mcu_connection.kicad_sch").write_text(
        build_sheet2().render(SHEET2_UUID), encoding="utf-8")
    print("schematics written to", BASE)


if __name__ == "__main__":
    main()
