# -*- coding: utf-8 -*-
"""Генератор схемы kicad/pr15-16.kicad_sch (KiCad v10).

Схема практической работы 15-16: микроконтроллер МК-52 (8052) с обвязкой
(кварц, сброс, подтяжка EA) и выходом ШИМ P1.0 на разъём пробника
осциллографа. Стандартные символы (Device:Crystal, Device:C, Device:R,
Switch:SW_Push, Connector_Generic:Conn_01x02, power:+5V, power:GND)
извлекаются из системных библиотек KiCad и встраиваются в файл, символ
МК-52 (PEPiS:MK52, корпус DIP-40) описан в этом скрипте. Все координаты
кратны 1,27 мм.

Запуск:  python3 tools/make_sch.py
"""

from pathlib import Path

KICAD_SYM_DIR = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "kicad" / "pr15-16.kicad_sch"

SCH_UUID = "3a1f15c6-2b48-4e7a-9c3d-7f2a9b4d6e01"
PROJ_NAME = "pr15-16"
SHEET_PATH = "/" + SCH_UUID

# ---------------------------------------------------------------------------
# Утилиты S-expression
# ---------------------------------------------------------------------------


def extract_symbol(lib_file, name, lib_prefix):
    """Извлечь определение символа name из системной библиотеки KiCad
    и переименовать в «lib_prefix:name» для встраивания в lib_symbols."""
    text = (KICAD_SYM_DIR / lib_file).read_text(encoding="utf-8")
    needle = f'\n\t(symbol "{name}"'
    start = text.index(needle) + len(needle) - len(f'(symbol "{name}"')
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                block = text[start : i + 1]
                break
    else:
        raise RuntimeError(f"symbol {name} not closed")
    head = f'(symbol "{lib_prefix}:{name}"'
    return head + block[len(f'(symbol "{name}"') :]


def pin_offsets(symbol_block):
    """Прочитать (pin ...) символа: номер -> ((x, y), поворот, длина)."""
    pins = {}
    for m in re_pin.finditer(symbol_block):
        pass
    return pins


import re

RE_PIN = re.compile(
    r"\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)"
    r"\s+\(length\s+([-\d.]+)\)(?:.*?)\(name\s+\"([^\"]*)\".*?"
    r"\(number\s+\"([^\"]*)\"",
    re.S,
)


def parse_pins(symbol_block):
    """{номер пина: (x, y, поворот)} из определения символа."""
    pins = {}
    for m in RE_PIN.finditer(symbol_block):
        pins[m.group(7)] = (float(m.group(2)), float(m.group(3)), int(m.group(4)))
    return pins


def rot_point(x, y, rot):
    # преобразование локальной точки символа в смещение на листе:
    # eeschema переворачивает ось Y, затем поворачивает на -rot (по часовой)
    if rot == 0:
        return (x, -y)
    if rot == 90:
        return (-y, -x)
    if rot == 180:
        return (-x, y)
    if rot == 270:
        return (y, x)
    raise ValueError(rot)


def pin_world(inst_at, inst_rot, pin_at, pin_rot_unused=None):
    x, y = rot_point(pin_at[0], pin_at[1], inst_rot)
    return (round(inst_at[0] + x, 2), round(inst_at[1] + y, 2))


def uuid():
    import uuid as _uuid

    return str(_uuid.uuid4())


# ---------------------------------------------------------------------------
# Встраиваемые определения символов
# ---------------------------------------------------------------------------

EMBEDDED = [
    extract_symbol("Device.kicad_sym", "Crystal", "Device"),
    extract_symbol("Device.kicad_sym", "C", "Device"),
    extract_symbol("Device.kicad_sym", "R", "Device"),
    extract_symbol("Switch.kicad_sym", "SW_Push", "Switch"),
    extract_symbol("Connector_Generic.kicad_sym", "Conn_01x02", "Connector_Generic"),
    extract_symbol("power.kicad_sym", "+5V", "power"),
    extract_symbol("power.kicad_sym", "GND", "power"),
    extract_symbol("power.kicad_sym", "PWR_FLAG", "power"),
]

# --- МК-52 (8052, DIP-40): левые выводы 1-20, правые 21-40 ----------------
LEFT_PINS = [
    ("P1.0", "bidirectional"),
    ("P1.1", "bidirectional"),
    ("P1.2", "bidirectional"),
    ("P1.3", "bidirectional"),
    ("P1.4", "bidirectional"),
    ("P1.5", "bidirectional"),
    ("P1.6", "bidirectional"),
    ("P1.7", "bidirectional"),
    ("RST", "input"),
    ("P3.0", "bidirectional"),
    ("P3.1", "bidirectional"),
    ("P3.2", "bidirectional"),
    ("P3.3", "bidirectional"),
    ("P3.4", "bidirectional"),
    ("P3.5", "bidirectional"),
    ("P3.6", "bidirectional"),
    ("P3.7", "bidirectional"),
    ("XTAL2", "output"),
    ("XTAL1", "input"),
    ("GND", "power_in"),
]
RIGHT_PINS = [
    ("P2.0", "bidirectional"),
    ("P2.1", "bidirectional"),
    ("P2.2", "bidirectional"),
    ("P2.3", "bidirectional"),
    ("P2.4", "bidirectional"),
    ("P2.5", "bidirectional"),
    ("P2.6", "bidirectional"),
    ("P2.7", "bidirectional"),
    ("PSEN", "output"),
    ("ALE", "output"),
    ("EA", "input"),
    ("P0.7", "bidirectional"),
    ("P0.6", "bidirectional"),
    ("P0.5", "bidirectional"),
    ("P0.4", "bidirectional"),
    ("P0.3", "bidirectional"),
    ("P0.2", "bidirectional"),
    ("P0.1", "bidirectional"),
    ("P0.0", "bidirectional"),
    ("VCC", "power_in"),
]

PIN_LEN = 5.08
STEP = 2.54
BODY_W = 30.48
BODY_H = 48.26


def mk52_symbol():
    lines = []
    ap = lines.append
    ap('\t\t(symbol "PEPiS:MK52"')
    ap("\t\t\t(pin_numbers")
    ap("\t\t\t\t(hide yes)")
    ap("\t\t\t)")
    ap("\t\t\t(exclude_from_sim no)")
    ap("\t\t\t(in_bom yes)")
    ap("\t\t\t(on_board yes)")
    ap("\t\t\t(in_pos_files yes)")
    ap("\t\t\t(duplicate_pin_numbers_are_jumpers no)")
    ap('\t\t\t(property "Reference" "U"')
    ap("\t\t\t\t(at 0 2.54 0)")
    ap("\t\t\t\t(show_name no)")
    ap("\t\t\t\t(do_not_autoplace no)")
    ap("\t\t\t\t(effects (font (size 1.27 1.27))))")
    ap('\t\t\t(property "Value" "MK52"')
    ap("\t\t\t\t(at 0 -50.8 0)")
    ap("\t\t\t\t(show_name no)")
    ap("\t\t\t\t(do_not_autoplace no)")
    ap("\t\t\t\t(effects (font (size 1.27 1.27))))")
    ap('\t\t\t(property "Footprint" ""')
    ap("\t\t\t\t(at 0 0 0) (show_name no) (do_not_autoplace no)")
    ap("\t\t\t\t(hide yes) (effects (font (size 1.27 1.27))))")
    ap('\t\t\t(property "Datasheet" ""')
    ap("\t\t\t\t(at 0 0 0) (show_name no) (do_not_autoplace no)")
    ap("\t\t\t\t(hide yes) (effects (font (size 1.27 1.27))))")
    ap('\t\t\t(property "Description" "МК-52 (Intel 8052), 8-битный микроконтроллер MCS-51, таймер Т/С2"')
    ap("\t\t\t\t(at 0 0 0) (show_name no) (do_not_autoplace no)")
    ap("\t\t\t\t(hide yes) (effects (font (size 1.27 1.27))))")
    ap('\t\t\t(symbol "MK52_0_1"')
    ap("\t\t\t\t(rectangle")
    ap("\t\t\t\t\t(start 0 0)")
    ap(f"\t\t\t\t\t(end {BODY_W} {-BODY_H})")
    ap("\t\t\t\t\t(stroke (width 0.254) (type default))")
    ap("\t\t\t\t\t(fill (type background))")
    ap("\t\t\t\t)")
    ap("\t\t\t)")
    ap('\t\t\t(symbol "MK52_1_1"')
    for i, (name, ptype) in enumerate(LEFT_PINS):
        y = -i * STEP
        ap(f'\t\t\t\t(pin {ptype} line (at {-PIN_LEN} {y} 0) (length {PIN_LEN})')
        ap(f'\t\t\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))')
        ap(f'\t\t\t\t\t(number "{i + 1}" (effects (font (size 1.27 1.27))))')
        ap("\t\t\t\t)")
    for i, (name, ptype) in enumerate(RIGHT_PINS):
        y = -i * STEP
        ap(f'\t\t\t\t(pin {ptype} line (at {BODY_W + PIN_LEN} {y} 180) (length {PIN_LEN})')
        ap(f'\t\t\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))')
        ap(f'\t\t\t\t\t(number "{i + 21}" (effects (font (size 1.27 1.27))))')
        ap("\t\t\t\t)")
    ap("\t\t\t)")
    ap("\t\t\t(embedded_fonts no)")
    ap("\t\t)")
    # убрать один уровень отступа: блок встаёт в lib_symbols как и прочие
    return "\n".join(line[1:] if line.startswith("\t") else line
                     for line in lines)


EMBEDDED.append(mk52_symbol())


# ---------------------------------------------------------------------------
# Размещение компонентов (все координаты кратны 1,27 мм)
# ---------------------------------------------------------------------------

U1_AT = (81.28, 60.96)  # левый верхний угол корпуса МК-52


def u1_pin_world(number):
    """Мировая координата конца вывода U1 (ось Y листа направлена вверх)."""
    if number <= 20:
        i = number - 1
        return (U1_AT[0] - PIN_LEN, round(U1_AT[1] + i * STEP, 2))
    i = number - 21
    return (U1_AT[0] + BODY_W + PIN_LEN, round(U1_AT[1] + i * STEP, 2))


SYMBOL_DEFS = {  # lib_id -> определение (для списка пинов экземпляра)
    "Device:Crystal": EMBEDDED[0],
    "Device:C": EMBEDDED[1],
    "Device:R": EMBEDDED[2],
    "Switch:SW_Push": EMBEDDED[3],
    "Connector_Generic:Conn_01x02": EMBEDDED[4],
    "power:+5V": EMBEDDED[5],
    "power:GND": EMBEDDED[6],
    "power:PWR_FLAG": EMBEDDED[7],
    "PEPiS:MK52": EMBEDDED[8],
}

# (lib_id, обозначение, значение, пин, куда поставить этот пин, поворот)
# Лист: ось Y вверх. Корпус U1 занимает y 12.7..60.96 (P1.0 сверху,
# GND/VCC снизу). Кварцевая обвязка под МК, цепь сброса слева.
PLACEMENTS = [
    ("Device:Crystal", "Y1", "11,0592 МГц", "1", (60.96, 101.6), 0),
    ("Device:C", "C1", "22 пФ", "2", (60.96, 99.06), 0),
    ("Device:C", "C2", "22 пФ", "2", (68.58, 99.06), 0),
    # пин 2 C3 сверху (к +5V), пин 1 снизу на магистрали RST
    ("Device:C", "C3", "10 мкФ", "2", (68.58, 88.9), 0),
    ("Device:R", "R1", "10 кОм", "2", (63.5, 78.74), 0),
    ("Device:R", "R2", "10 кОм", "1", (120.65, 86.36), 90),
    ("Switch:SW_Push", "SW1", "RESET", "1", (73.66, 81.28), 90),
    # J1: выводы смотрят влево, корпус левее конца провода P1.0
    ("Connector_Generic:Conn_01x02", "J1", "Пробник осциллографа", "1",
     (63.5, 60.96), 180),
    ("power:+5V", "PWR1", "+5V", "1", (68.58, 88.9), 0),
    ("power:+5V", "PWR2", "+5V", "1", (73.66, 71.12), 0),
    ("power:+5V", "PWR3", "+5V", "1", (121.92, 109.22), 0),
    ("power:+5V", "PWR4", "+5V", "1", (128.27, 88.9), 0),
    ("power:GND", "GND1", "GND", "1", (60.96, 91.44), 0),
    ("power:GND", "GND2", "GND", "1", (68.58, 91.44), 0),
    ("power:GND", "GND3", "GND", "1", (63.5, 68.58), 0),
    ("power:GND", "GND4", "GND", "1", (71.12, 109.22), 0),
    ("power:GND", "GND5", "GND", "1", (63.5, 58.42), 0),
    ("power:PWR_FLAG", "PWR5", "PWR_FLAG", "1", (71.12, 88.9), 0),
    ("power:PWR_FLAG", "PWR6", "PWR_FLAG", "1", (57.15, 91.44), 0),
]

# Позиции подписей (смещение от точки размещения, поворот текста):
# (ref_dx, ref_dy, ref_rot, val_dx, val_dy, val_rot)
LABEL_OVERRIDES = {
    "U1": (0, 2.54, 0, 15.24, 2.54, 0),
    "Y1": (0, 2.54, 0, -12.07, 0, 0),
    "C1": (3.81, 1.27, 0, 3.81, -1.27, 0),
    "C2": (3.81, 1.27, 0, 3.81, -1.27, 0),
    "C3": (-3.81, 1.27, 0, -3.81, -1.27, 0),
    "R1": (3.81, 0, 90, -3.81, 0, 90),
    "R2": (0, 2.54, 0, 0, -2.54, 0),
    "SW1": (3.81, 0, 90, 3.81, -3.81, 0),
    "J1": (0, 2.54, 0, -10.16, 0, 0),
}

instances = []  # (lib_id, ref, value, at, rot, {pin: world})
for lib_id, ref, value, pin_no, target, rot in PLACEMENTS:
    block = SYMBOL_DEFS[lib_id]
    pins = parse_pins(block)
    if pin_no not in pins:
        raise RuntimeError(f"{lib_id}: pin {pin_no} not found")
    off = pins[pin_no]
    rx, ry = rot_point(off[0], off[1], rot)
    at = (round(target[0] - rx, 2), round(target[1] - ry, 2))
    world = {n: pin_world(at, rot, p) for n, p in pins.items()}
    instances.append((lib_id, ref, value, at, rot, world))

world_of = {ref: w for _, ref, _, _, _, w in instances}


def pxy(ref, pin):
    x, y = world_of[ref][pin]
    return (round(x, 2), round(y, 2))


# --- провода ---------------------------------------------------------------
W = [
    ((76.2, 60.96), (63.5, 60.96)),        # P1.0 -> J1.1
    ((63.5, 81.28), (76.2, 81.28)),        # магистраль RST
    ((63.5, 78.74), (63.5, 81.28)),        # R1 -> RST (T-стык)
    ((63.5, 71.12), (63.5, 68.58)),        # R1 -> GND3
    ((68.58, 88.9), (71.12, 88.9)),        # +5V -> PWR_FLAG
    ((116.84, 86.36), (120.65, 86.36)),    # EA -> R2
    ((128.27, 86.36), (128.27, 88.9)),     # R2 -> +5V
    ((116.84, 109.22), (121.92, 109.22)),  # VCC -> +5V
    ((76.2, 109.22), (71.12, 109.22)),     # GND вывод 20
    ((76.2, 106.68), (60.96, 106.68)),     # XTAL1 влево
    ((60.96, 106.68), (60.96, 101.6)),     # XTAL1 -> кварц
    ((76.2, 104.14), (73.66, 104.14)),     # XTAL2
    ((73.66, 104.14), (73.66, 101.6)),
    ((73.66, 101.6), (68.58, 101.6)),      # к выводу 2 кварца
    ((60.96, 101.6), (60.96, 99.06)),      # кварц -> C1
    ((68.58, 101.6), (68.58, 99.06)),      # кварц -> C2
    ((57.15, 91.44), (60.96, 91.44)),      # PWR_FLAG -> GND1
]

JUNCTIONS = [(63.5, 81.28), (68.58, 81.28), (73.66, 81.28)]

LABELS = [("PWM_P1.0", (69.85, 60.96), 0)]

# no_connect на неиспользуемых выводах U1
NO_CONNECT_PINS = [2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17,
                   21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 33, 34, 35,
                   36, 37, 38, 39]
NO_CONNECTS = [u1_pin_world(n) for n in NO_CONNECT_PINS]

TEXTS = [
    ("Осциллограф XSC-1: канал A на P1.0 (J1.1), общий на GND (J1.2)",
     (20.32, 69.85), 0),
    ("Кварц 11,0592 МГц (учебный пример); для варианта 4: 13 МГц",
     (20.32, 88.9), 0),
    ("ШИМ на таймере Т/С2, выход P1.0",
     (20.32, 57.15), 0),
    ("Сброс: R1 на GND, C3 и SW1 на +5V",
     (20.32, 81.28), 0),
]

# ---------------------------------------------------------------------------
# Сборка файла
# ---------------------------------------------------------------------------


def fmt(n):
    s = f"{n:.2f}".rstrip("0").rstrip(".")
    return s if s else "0"


def emit_symbol_instance(lib_id, ref, value, at, rot, world):
    lines = []
    ap = lines.append
    ap("\t(symbol")
    ap(f'\t\t(lib_id "{lib_id}")')
    ap(f"\t\t(at {fmt(at[0])} {fmt(at[1])} {rot})")
    ap("\t\t(unit 1)")
    ap("\t\t(body_style 1)")
    ap("\t\t(exclude_from_sim no)")
    ap("\t\t(in_bom yes)")
    ap("\t\t(on_board yes)")
    ap("\t\t(in_pos_files yes)")
    ap("\t\t(dnp no)")
    ap(f'\t\t(uuid "{uuid()}")')
    hidden_power = lib_id.startswith("power:")
    if hidden_power:
        # у силовых символов Value это текст «GND»/«+5V» внутри графики,
        # Reference скрыт
        ref_dx, ref_dy, ref_rot = 0, 2.54, 0
        val_dx, val_dy, val_rot = 0, 0, 0
    else:
        ref_dx, ref_dy, ref_rot, val_dx, val_dy, val_rot = LABEL_OVERRIDES.get(
            ref, (0, 2.54, 0, 0, -2.54, 0))
    for prop, val, vis, dx, dy, prot in (
        ("Reference", ref, not hidden_power, ref_dx, ref_dy, ref_rot),
        ("Value", value, True, val_dx, val_dy, val_rot),
        ("Footprint", "", False, val_dx, val_dy, 0),
        ("Datasheet", "", False, val_dx, val_dy, 0),
    ):
        vx, vy = at[0] + dx, at[1] + dy
        hide = "" if vis else "\n\t\t\t(hide yes)"
        ap(f'\t\t(property "{prop}" "{val}"')
        ap(f"\t\t\t(at {fmt(vx)} {fmt(vy)} {prot}){hide}")
        ap("\t\t\t(show_name no)")
        ap("\t\t\t(do_not_autoplace no)")
        ap("\t\t\t(effects (font (size 1.1 1.1))))")
    for pin in sorted(world, key=lambda p: int(p)):
        ap(f'\t\t(pin "{pin}"')
        ap(f'\t\t\t(uuid "{uuid()}")')
        ap("\t\t)")
    ap("\t\t(instances")
    ap(f'\t\t\t(project "{PROJ_NAME}"')
    ap(f'\t\t\t\t(path "{SHEET_PATH}"')
    ap(f'\t\t\t\t\t(reference "{ref}")')
    ap("\t\t\t\t\t(unit 1)")
    ap("\t\t\t\t)")
    ap("\t\t\t)")
    ap("\t\t)")
    ap("\t)")
    return "\n".join(lines)


def main():
    out = []
    ap = out.append
    ap("(kicad_sch")
    ap("\t(version 20260306)")
    ap('\t(generator "eeschema")')
    ap('\t(generator_version "10.0")')
    ap(f'\t(uuid "{SCH_UUID}")')
    ap('\t(paper "A4")')
    ap("\t(title_block")
    ap('\t\t(title "Практическая работа № 15-16. ШИМ на МК-52 (8052), вариант 4")')
    ap("\t)")
    ap("\t(lib_symbols")
    for block in EMBEDDED:
        ap("\n".join("\t\t" + line for line in block.splitlines()))
    ap("\t)")

    # U1 МК-52
    mk_world = {
        str(i + 1): u1_pin_world(i + 1) for i in range(40)
    }
    ap(emit_symbol_instance("PEPiS:MK52", "U1", "МК-52 (8052)", U1_AT, 0,
                            mk_world))
    for inst in instances:
        ap(emit_symbol_instance(*inst))

    for (a, b) in W:
        ap("\t(wire")
        ap("\t\t(pts")
        ap(f"\t\t\t(xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])})")
        ap("\t\t)")
        ap("\t\t(stroke (width 0) (type default))")
        ap("\t\t(uuid \"%s\")" % uuid())
        ap("\t)")

    for (x, y) in JUNCTIONS:
        ap("\t(junction")
        ap(f"\t\t(at {fmt(x)} {fmt(y)})")
        ap("\t\t(diameter 0)")
        ap("\t\t(color 0 0 0 0)")
        ap(f"\t\t(uuid \"{uuid()}\")")
        ap("\t)")

    for (text, (x, y), rot) in LABELS:
        ap(f'\t(label "{text}"')
        ap(f"\t\t(at {fmt(x)} {fmt(y)} {rot})")
        ap("\t\t(effects (font (size 1.27 1.27)) (justify left bottom))")
        ap(f"\t\t(uuid \"{uuid()}\")")
        ap("\t)")

    for (x, y) in NO_CONNECTS:
        ap("\t(no_connect")
        ap(f"\t\t(at {fmt(x)} {fmt(y)})")
        ap(f"\t\t(uuid \"{uuid()}\")")
        ap("\t)")

    for (text, (x, y), rot) in TEXTS:
        ap(f'\t(text "{text}"')
        ap("\t\t(exclude_from_sim no)")
        ap(f"\t\t(at {fmt(x)} {fmt(y)} {rot})")
        ap("\t\t(effects (font (size 1.27 1.27)) (justify left bottom))")
        ap(f"\t\t(uuid \"{uuid()}\")")
        ap("\t)")

    ap("\t(sheet_instances")
    ap(f'\t\t(path "/"\n\t\t\t(page "1")\n\t\t)')
    ap("\t)")
    ap("\t(embedded_fonts no)")
    ap(")")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
