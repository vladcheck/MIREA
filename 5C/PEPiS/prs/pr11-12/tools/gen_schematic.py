# -*- coding: utf-8 -*-
"""Генератор схемы ПР 11-12 (ЦАП на матрице R-2R, STM32F103C8, вариант 4).

Создаёт kicad/pr11-12.kicad_sch в формате KiCad 10 (s-expression).
Символы берутся из стандартных библиотек KiCad (разрешаются при
открытии/экспорте через kicad-cli), поэтому секция lib_symbols не
включается. Все координаты кратны 1,27 мм (сетка 1,27 мм), единицы
измерения: мм.

Топология матрицы (таблица 9.30 методички):
  Di (PAi) -- 2R=20 кОм -- узел Ni; между узлами Ni и N(i+1): R=10 кОм;
  завершающий 2R=20 кОм от узла N0 (младший разряд) на GND;
  выход VOUT снимается с узла N7 (старший разряд).

Запуск:
    python3 tools/gen_schematic.py
"""

from pathlib import Path
from uuid import uuid5, NAMESPACE_URL
import re

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "kicad" / "pr11-12.kicad_sch"

SHEET_UUID = "3f2a1c9e-7b4d-4e8a-9c15-2d6f0a48b3e7"

KICAD_SYM_DIR = Path(
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
)
# Символы, встраиваемые в lib_symbols (глобальная таблица библиотек на
# машине не настроена, поэтому схема несёт копии определений, как в пр7-8).
EMBED_LIBS = {
    "MCU_ST_STM32F1": ("MCU_ST_STM32F1.kicad_sym",
                       ["STM32F103C8Tx", "STM32F103C_8-B_Tx"]),
    "Device": ("Device.kicad_sym", ["R"]),
    "power": ("power.kicad_sym", ["PWR_FLAG"]),
    "Connector_Generic": ("Connector_Generic.kicad_sym", ["Conn_01x02"]),
}
# Символы-родители: нужны только для раскрытия extends, в файл не пишутся.
PARENT_ONLY = {"STM32F103C_8-B_Tx"}


def extract_symbol_block(lib_text: str, name: str) -> str:
    """Вырезает сбалансированный блок (symbol \"NAME\" ...) из текста библиотеки."""
    needle = f'(symbol "{name}"'
    i = lib_text.find(needle)
    if i < 0:
        raise KeyError(f"symbol {name} not found")
    depth = 0
    for j in range(i, len(lib_text)):
        c = lib_text[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return lib_text[i:j + 1]
    raise ValueError(f"unbalanced block for {name}")


def embedded_lib_symbols() -> str:
    """Секция lib_symbols: блоки символов с переименованием в Lib:Name.

    Для символов с наследованием (extends), которое kicad-cli не
    разрешает из встроенных lib_symbols, наследование раскрывается:
    графические блоки родителя копируются внутрь дочернего символа
    с заменой имени (как делает eeschema при сохранении).
    """
    blocks = []
    for lib, (fname, names) in EMBED_LIBS.items():
        text = (KICAD_SYM_DIR / fname).read_text(encoding="utf-8")
        lib_blocks = {}
        for name in names:
            lib_blocks[name] = extract_symbol_block(text, name)
        for name in names:
            if name in PARENT_ONLY:
                continue
            blk = lib_blocks[name]
            m_ext = re.search(r'^\s*\(extends "([^"]+)"\)\n', blk,
                              re.MULTILINE)
            if m_ext:
                parent_name = m_ext.group(1)
                parent = lib_blocks.get(parent_name) or \
                    extract_symbol_block(text, parent_name)
                units = re.findall(
                    r'\(symbol "' + re.escape(parent_name) +
                    r'_([^"]+)"', parent)
                inserts = []
                for suffix in units:
                    unit_blk = extract_symbol_block(
                        parent, f"{parent_name}_{suffix}")
                    unit_blk = unit_blk.replace(
                        f'(symbol "{parent_name}_{suffix}"',
                        f'(symbol "{name}_{suffix}"', 1)
                    inserts.append(unit_blk)
                blk = blk.replace(m_ext.group(0), "")
                marker = "\t(embedded_fonts no)"
                if marker in blk:
                    pos = blk.find(marker)
                    blk = blk[:pos] + "".join(
                        i + "\n" for i in inserts) + blk[pos:]
                else:
                    blk = blk.rstrip(")\n ") + "\n" + "".join(
                        i + "\n" for i in inserts) + ")"
            blk = blk.replace(f'(symbol "{name}"',
                              f'(symbol "{lib}:{name}"', 1)
            blocks.append(blk)
    lines = ["(lib_symbols"]
    for blk in blocks:
        lines.extend("\t" + ln for ln in blk.splitlines())
    lines.append(")")
    return "\n".join(lines)


def u(tag: str) -> str:
    """Детерминированный UUID по метке объекта."""
    return str(uuid5(NAMESPACE_URL, f"pr11-12/{SHEET_UUID}/{tag}"))


L = []  # строки выходного файла


def emit(s: str = "") -> None:
    # Защита от «тофу»: KiCad не рисует «№», заменяем на «#».
    L.append(s.replace("№", "#"))


def prop(name: str, value: str, at, hide=False, justify=None, rot=None) -> None:
    x, y = at[0], at[1]
    r = at[2] if len(at) > 2 else 0
    if rot is not None:
        r = rot
    emit(f'\t\t(property "{name}" "{value}"')
    emit(f"\t\t\t(at {x} {y} {r})")
    if hide:
        emit("\t\t\t(hide yes)")
    emit("\t\t\t(show_name no)")
    emit("\t\t\t(do_not_autoplace no)")
    emit("\t\t\t(effects")
    emit("\t\t\t\t(font")
    emit("\t\t\t\t\t(size 1.27 1.27)")
    emit("\t\t\t\t)")
    if justify:
        emit(f"\t\t\t\t(justify {justify})")
    emit("\t\t\t)")
    emit("\t\t)")


def symbol(lib_id, ref, value, at, pins, ref_at=None, val_at=None,
           footprint="", datasheet="", description="", pin_uuids=None,
           hide_value=False, hide_ref=False, val_rot=None, project="pr11-12",
           extra_props=None, ref_justify=None, val_justify=None):
    x, y, rot = at
    emit("\t(symbol")
    emit(f'\t\t(lib_id "{lib_id}")')
    emit(f"\t\t(at {x} {y} {rot})")
    emit("\t\t(unit 1)")
    emit("\t\t(body_style 1)")
    emit("\t\t(exclude_from_sim no)")
    emit("\t\t(in_bom yes)")
    emit("\t\t(on_board yes)")
    emit("\t\t(in_pos_files yes)")
    emit("\t\t(dnp no)")
    emit(f'\t\t(uuid "{u("sym:" + ref)}")')
    prop("Reference", ref, ref_at or (x, y - 2.54, 0), hide=hide_ref,
         justify=ref_justify)
    prop("Value", value, val_at or (x, y + 2.54, 0),
         hide=hide_value, rot=val_rot, justify=val_justify)
    if footprint:
        prop("Footprint", footprint, (x, y, 0), hide=True)
    if datasheet:
        prop("Datasheet", datasheet, (x, y, 0), hide=True)
    if description:
        prop("Description", description, (x, y, 0), hide=True)
    for extra in (extra_props or []):
        prop(extra[0], extra[1], extra[2], hide=True)
    for pin in pins:
        emit(f'\t\t(pin "{pin}"')
        emit(f'\t\t\t(uuid "{u(f"pin:{ref}:{pin}")}")')
        emit("\t\t)")
    emit("\t\t(instances")
    emit(f'\t\t\t(project "{project}"')
    emit(f'\t\t\t\t(path "/{SHEET_UUID}"')
    emit(f'\t\t\t\t\t(reference "{ref}")')
    emit("\t\t\t\t\t(unit 1)")
    emit("\t\t\t\t)")
    emit("\t\t\t)")
    emit("\t\t)")
    emit("\t)")


def wire(x1, y1, x2, y2) -> None:
    emit("\t(wire")
    emit("\t\t(pts")
    emit(f"\t\t\t(xy {x1} {y1}) (xy {x2} {y2})")
    emit("\t\t)")
    emit("\t\t(stroke")
    emit("\t\t\t(width 0)")
    emit("\t\t\t(type default)")
    emit("\t\t)")
    emit(f'\t\t(uuid "{u(f"wire:{x1},{y1}-{x2},{y2}")}")')
    emit("\t)")


def junction(x, y) -> None:
    emit("\t(junction")
    emit(f"\t\t(at {x} {y})")
    emit("\t\t(diameter 0)")
    emit("\t\t(color 0 0 0 0)")
    emit(f'\t\t(uuid "{u(f"junc:{x},{y}")}")')
    emit("\t)")


def label(text, x, y, rot=0, justify="left bottom") -> None:
    emit(f'\t(label "{text}"')
    emit(f"\t\t(at {x} {y} {rot})")
    emit("\t\t(effects")
    emit("\t\t\t(font")
    emit("\t\t\t\t(size 1.27 1.27)")
    emit("\t\t\t)")
    emit(f"\t\t\t(justify {justify})")
    emit("\t\t)")
    emit(f'\t\t(uuid "{u(f"label:{text}:{x},{y}")}")')
    emit("\t)")


def global_label(text, x, y, rot=0, justify="left bottom") -> None:
    emit(f'\t(global_label "{text}"')
    emit("\t\t(shape bidirectional)")
    emit(f"\t\t(at {x} {y} {rot})")
    emit("\t\t(effects")
    emit("\t\t\t(font")
    emit("\t\t\t\t(size 1.27 1.27)")
    emit("\t\t\t)")
    emit(f"\t\t\t(justify {justify})")
    emit("\t\t)")
    emit(f'\t\t(uuid "{u(f"glabel:{text}:{x},{y}")}")')
    emit("\t)")


def no_connect(x, y) -> None:
    emit("\t(no_connect")
    emit(f"\t\t(at {x} {y})")
    emit(f'\t\t(uuid "{u(f"nc:{x},{y}")}")')
    emit("\t)")


def text(body, x, y, size=1.27, bold=False) -> None:
    emit(f'\t(text "{body}"')
    emit("\t\t(exclude_from_sim no)")
    emit(f"\t\t(at {x} {y} 0)")
    emit("\t\t(effects")
    emit("\t\t\t(font")
    emit(f"\t\t\t\t(size {size} {size})")
    if bold:
        emit("\t\t\t\t(bold yes)")
    emit("\t\t\t)")
    emit("\t\t\t(justify left bottom)")
    emit("\t\t)")
    emit(f'\t\t(uuid "{u(f"text:{body[:24]}:{x},{y}")}")')
    emit("\t)")


R_FP = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
DS_STM32 = "https://www.st.com/resource/en/datasheet/stm32f103c8.pdf"
DESC_STM32 = ("STMicroelectronics Arm Cortex-M3 MCU, 64KB flash, 20KB "
              "RAM, 72 MHz, 2.0-3.6V, 37 GPIO, LQFP48")

# ---------------------------------------------------------------- header
emit("(kicad_sch")
emit("\t(version 20260306)")
emit('\t(generator "eeschema")')
emit('\t(generator_version "10.0")')
emit(f'\t(uuid "{SHEET_UUID}")')
emit('\t(paper "A4")')
emit("\t(title_block")
emit('\t\t(title "Практическая работа #11-12. ЦАП R-2R, вариант 4")')
emit("\t)")
for ln in embedded_lib_symbols().splitlines():
    emit("\t" + ln)

# ------------------------------------------------------------------ U1
mcu_pins = [str(n) for n in range(1, 49)]
symbol(
    "MCU_ST_STM32F1:STM32F103C8Tx", "U1", "STM32F103C8Tx",
    (78.74, 100.33, 0), mcu_pins,
    ref_at=(63.5, 139.7, 0), val_at=(86.36, 139.7, 0),
    ref_justify="left", val_justify="left",
    footprint="Package_QFP:LQFP-48_7x7mm_P0.5mm",
    datasheet=DS_STM32, description=DESC_STM32,
)

# ------------------------------------------------- подключение питания U1
# Верхние выводы (связка = pos + (x, -y)): VBAT 1, VDD 24, VDDA 9, VDD 36,
# VDD 48. Нижние: VSS 23/35/47, VSSA 8. Выводы соединены короткими
# перемычками с шинами (y = 57.15 сверху, y = 143.51 снизу), чтобы
# избежать наложения меток. Слева на шине 3V3 — символ PWR_FLAG на
# видимой перемычке 2,54 мм. Горизонтальные метки 3V3 закреплены на
# концах шины: левая смотрит влево от начала шины (рядом с флагом),
# правая — вправо от конца шины; ни одна не перекрывает символы и провода.
for px in (73.66, 76.2, 78.74, 81.28, 83.82):
    wire(px, 59.69, px, 57.15)
    junction(px, 57.15)
wire(73.66, 57.15, 83.82, 57.15)
wire(73.66, 57.15, 73.66, 54.61)
symbol("power:PWR_FLAG", "PWR1", "PWR_FLAG", (73.66, 54.61, 0), ["1"],
       hide_value=True, hide_ref=True)
global_label("3V3", 73.66, 57.15, rot=0, justify="right bottom")
global_label("3V3", 83.82, 57.15, rot=0)
for px in (78.74, 81.28):
    wire(px, 140.97, px, 143.51)
    junction(px, 143.51)
wire(78.74, 143.51, 83.82, 143.51)
global_label("GND", 83.82, 143.51, rot=0)

# Флаг питания GND стоит на отводе J1.2 (см. раздел разъёма J1 ниже).

# -------------------------------------------------- линии разрядов D0..D7
# Выводы PA0..PA7 (выводы 10..17) справа, x = 96.52, шаг 2.54, PA0 снизу.
for i in range(8):
    py = 67.31 + 2.54 * i
    wire(96.52, py, 99.06, py)
    label(f"D{i}", 99.06, py)

# ------------------------------------------------------------ матрица R-2R
# Узлы Ni на x = 139.7, шаг 10.16, N0 (младший разряд) внизу.
NODE_X = 139.7
Y = {i: 72.39 + 10.16 * i for i in range(8)}

# Входные 2R = 20 кОм (R8..R15), горизонтально; точки подключения
# выводов на (130.81 +- 3.81, Y) - см. ERC.
for i in range(8):
    y = Y[i]
    wire(123.19, y, 127.0, y)
    label(f"D{i}", 123.19, y)
    symbol(
        "Device:R", f"R{8 + i}", "20k", (130.81, y, 90), ["1", "2"],
        ref_at=(130.81, y - 2.54, 0), val_at=(130.81, y + 2.54, 90),
        footprint=R_FP,
    )
    wire(134.62, y, NODE_X, y)
    junction(NODE_X, y)

# Связующие R = 10 кОм (R1..R7), вертикально между узлами; точки
# подключения на расстоянии 3.81 от центра, поэтому узлы соединяются
# короткими перемычками 1.27 мм.
for i in range(1, 8):
    symbol(
        "Device:R", f"R{i}", "10k", (NODE_X, Y[i] - 5.08, 0), ["1", "2"],
        ref_at=(NODE_X - 2.54, Y[i] - 5.08, 90),
        val_at=(NODE_X + 2.54, Y[i] - 5.08, 90),
        footprint=R_FP,
    )
    wire(NODE_X, Y[i - 1], NODE_X, Y[i - 1] + 1.27)
    wire(NODE_X, Y[i] - 1.27, NODE_X, Y[i])

# Завершающий 2R = 20 кОм (R16) от узла N0 на GND.
symbol(
    "Device:R", "R16", "20k", (NODE_X, Y[0] - 5.08, 0), ["1", "2"],
    ref_at=(NODE_X - 2.54, Y[0] - 5.08, 90),
    val_at=(NODE_X + 2.54, Y[0] - 5.08, 90),
    footprint=R_FP,
)
wire(NODE_X, Y[0], NODE_X, Y[0] - 1.27)
wire(NODE_X, Y[0] - 8.89, NODE_X, 59.69)
global_label("GND", NODE_X, 59.69, rot=0)

# Выход VOUT с узла N7 (старший разряд) на разъём приборов J1.
# Точки подключения Conn_01x02 на (-5.08, 0) и (-5.08, -2.54) от центра.
# Позиции Reference/Value — у корпуса символа (как в пр7-8).
VOUT_Y = Y[7]
wire(NODE_X, VOUT_Y, 147.32, VOUT_Y)
label("VOUT", 141.24, VOUT_Y)
symbol(
    "Connector_Generic:Conn_01x02", "J1", "VOUT + GND",
    (152.4, VOUT_Y, 0), ["1", "2"],
    ref_at=(152.4, VOUT_Y - 3.81, 0),
    val_at=(161.29, VOUT_Y, 0),
    footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
    description="Generic connector, single row, 01x02",
)
# J1.1 (вывод 1) сидит на конце провода VOUT; J1.2 (вывод 2) на GND.
# Отвод уходит вниз, затем вправо на флаг питания PWR2; горизонтальная
# метка GND закреплена на углу провода — провод виден от вывода до метки
# и от метки до символа, ничего не перекрывает корпус J1.
wire(147.32, VOUT_Y + 2.54, 147.32, VOUT_Y + 10.16)
wire(147.32, VOUT_Y + 10.16, 152.4, VOUT_Y + 10.16)
global_label("GND", 147.32, VOUT_Y + 10.16, rot=0, justify="right bottom")
# флажок продолжает линию: провод подходит слева -> ромб вправо (rot 270)
symbol("power:PWR_FLAG", "PWR2", "PWR_FLAG", (152.4, VOUT_Y + 10.16, 270),
       ["1"], hide_value=True, hide_ref=True)

# -------------------------------------------------- неиспользуемые выводы
# Левый ряд: PC13..PC15 (2..4), PD0/PD1 (5..6), NRST (7), PB0..PB2 (18..20),
# PB10..PB11 (21..22), PB12..PB15 (25..28), PB3..PB9 (39..46), BOOT0 (44).
left_nc = {
    2: 85.09, 3: 87.63, 4: 90.17,          # PC13..PC15
    5: 77.47, 6: 80.01,                     # PD0, PD1
    7: 67.31,                               # NRST
    18: 95.25, 19: 97.79, 20: 100.33,       # PB0..PB2
    21: 120.65, 22: 123.19,                 # PB10, PB11
    25: 125.73, 26: 128.27, 27: 130.81, 28: 133.35,  # PB12..PB15
    39: 102.87, 40: 105.41, 41: 107.95, 42: 110.49,
    43: 113.03, 44: 72.39, 45: 115.57, 46: 118.11,   # BOOT0 = 44
}
for pin, y in sorted(left_nc.items()):
    no_connect(60.96, y)
# Правый ряд: PA8..PA15 (29..38, кроме 10..17).
right_nc = {29: 87.63, 30: 90.17, 31: 92.71, 32: 95.25,
            33: 97.79, 34: 100.33, 37: 102.87, 38: 105.41}
for pin, y in sorted(right_nc.items()):
    no_connect(96.52, y)

# ------------------------------------------------------------- пояснения
text("Практическая работа # 11-12 (учебная # 6). "
     "ЦАП на матрице R-2R, STM32F103C8, вариант 4",
     55.88, 43.18, size=2, bold=True)
text("Матрица R-2R: R1-R7 = 10 кОм, R8-R15 = 2R = 20 кОм, "
     "R16 = завершающий 2R = 20 кОм.", 160.02, 60.96)
text("Разряды: D7 (PA7, вес 128) ... D0 (PA0, вес 1); выход VOUT с узла D7.",
     160.02, 68.58)
text("Приборы Proteus: DC Voltmeter и Oscilloscope к J1.1 (VOUT), "
     "общий провод J1.2; входы приборов высокоомные.",
     160.02, 76.2)
text("Logic Analyzer подключается к линиям D7..D0 до резисторов. "
     "Все приборы и контроллер имеют общий GND.",
     160.02, 83.82)
text("Питание 3,3 В: выводы VDD, VDDA, VBAT; общий провод: VSS, VSSA.",
     160.02, 91.44)

# ---------------------------------------------------------------- footer
emit("\t(sheet_instances")
emit('\t\t(path "/"')
emit('\t\t\t(page "1")')
emit("\t\t)")
emit("\t)")
emit("\t(embedded_fonts no)")
emit(")")

OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"Wrote {OUT} ({len(L)} lines)")
