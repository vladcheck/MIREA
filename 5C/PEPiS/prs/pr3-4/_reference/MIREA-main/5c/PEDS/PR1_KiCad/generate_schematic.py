#!/usr/bin/env python3
"""
Генератор принципиальной схемы для практической работы №1 (ПЭПС).
Стенд «Учтех-Профи» на микроконтроллере STM32F100C8Tx.

ВНИМАНИЕ: эталоном является PR1_KiCad.kicad_sch. После генерации в схему
вручную внесён пост-пасс (читаемость + электрика), который повторный запуск
ЗАТРЁТ: разнос Reference/Value, маркеры N01-N25 и таблица цепей, сдвиг C3 на
166.37 и флагов, шахматка питания SB1/SB3=93.98 vs SB2/SB4=88.9, раздельные
вертикали SB (111.76/114.30/116.84/119.38), жгут POT_ADC в обход SB,
джоги G/DP у стоек CC, R11-R18 270 Ом в сегментах, VDD-стабы, no_connect,
удалён лишний PWR_FLAG LED-рейки. Перед регенерацией сверяйтесь с OTCHET.md.
Обозначения — по ГОСТ 2.710-81: DD1 (МК), HG1 (индикатор), HL1-HL8,
SB1-SB4 (кнопки), RP1 (потенциометр), R/C без изменений.

Периферийные модули (обозначения по ГОСТ 2.710-81):
  1. Светодиоды HL1..HL8 на PA0..PA7 с токоограничивающими резисторами R1..R8 (270 Ом)
  2. Семисегментный индикатор HG1 (KCSC02-105, общий катод) на PB8..PB15
  3. Генераторы логических уровней SB1..SB4 (SPDT) на PC13, PC14, PC15, PD0
  4. Потенциометр RP1 (ADC12_IN8) на PB0 с фильтрующим конденсатором C1 (100 нФ)
Обвязка: NRST (R9 10к + C4 100нФ), BOOT0 (R10 10к), развязка C2/C3 (100 нФ), PWR_FLAG.

Все соединения с микроконтроллером выполнены зелёным цветом (0 132 0).
Формат: KiCad 10 (20260101).
"""

import importlib.util
import json
import re
import uuid
from datetime import date
from pathlib import Path

GRID = 1.27
GREEN = "0 132 0 1"
ROOT_UUID = "11111111-2222-3333-4444-555555555555"

ROOT = Path(__file__).resolve().parent
SCH = ROOT / "PR1_KiCad.kicad_sch"
PRO = ROOT / "PR1_KiCad.kicad_pro"

_spec = importlib.util.spec_from_file_location(
    "dynamic_symbol_loader",
    "/Users/d.d.lyapunov/MCP/KiCAD-MCP-Server/python/commands/dynamic_symbol_loader.py",
)
_dsl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dsl)
DynamicSymbolLoader = _dsl.DynamicSymbolLoader


def u():
    return str(uuid.uuid4())


def snap(v):
    return round(round(v / GRID) * GRID, 2)


def fmt(v):
    f = float(v)
    return str(int(f)) if f.is_integer() else str(round(v, 4))


def pin_tf(px, py, angle):
    if angle == 0:
        return (px, -py)
    if angle == 90:
        return (-py, -px)
    if angle == 180:
        return (-px, py)
    if angle == 270:
        return (py, px)
    raise ValueError(angle)


def pin_abs(ox, oy, angle, px, py):
    dx, dy = pin_tf(px, py, angle)
    return snap(ox + dx), snap(oy + dy)


def mcu_pin_table():
    lib = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/MCU_ST_STM32F1.kicad_sym"
    s = Path(lib).read_text(encoding="utf-8")
    i = s.find('(symbol "STM32F100C_8-B_Tx"')
    depth, end = 0, None
    for k in range(i, len(s)):
        if s[k] == "(":
            depth += 1
        elif s[k] == ")":
            depth -= 1
            if depth == 0:
                end = k + 1
                break
    block = s[i:end]
    pins = {}
    for m in re.finditer(
        r'\(pin\s+\w+\s+\w+\s*\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)\s*\(length\s+[\d.]+\)'
        r'[\s\S]*?\(name\s+"([^"]*)"[\s\S]*?\(number\s+"([^"]*)"',
        block,
    ):
        x, y, rot, name, num = m.groups()
        pins.setdefault(name, []).append((float(x), float(y), num))
    return pins


MCU_PINS = {}


class B:
    def __init__(self, sch_path):
        self.sch = sch_path
        self.wires = []
        self.junctions = []
        self.labels = []
        self.nocos = []
        self.texts = []

    def wire(self, pts, color=GREEN):
        pts = [(snap(a), snap(b)) for a, b in pts]
        for p, q in zip(pts, pts[1:]):
            self.wires.append((p, q, color))

    def junction(self, x, y):
        self.junctions.append((snap(x), snap(y)))

    def label(self, name, x, y):
        self.labels.append((name, snap(x), snap(y)))

    def no_connect(self, x, y):
        self.nocos.append((snap(x), snap(y)))

    def text(self, s, x, y, size=1.5):
        self.texts.append((s, snap(x), snap(y), size))

    def flush(self):
        content = self.sch.read_text(encoding="utf-8")
        out = []
        for x, y in self.junctions:
            out.append(
                f'\t(junction\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(diameter 0)\n'
                f'\t\t(color {GREEN})\n\t\t(uuid "{u()}")\n\t)\n'
            )
        for x, y in self.nocos:
            out.append(
                f'\t(no_connect\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(uuid "{u()}")\n\t)\n'
            )
        for (x1, y1), (x2, y2), color in self.wires:
            out.append(
                f'\t(wire\n\t\t(pts\n\t\t\t(xy {fmt(x1)} {fmt(y1)})\n'
                f'\t\t\t(xy {fmt(x2)} {fmt(y2)})\n\t\t)\n'
                f'\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n'
                f'\t\t\t(color {color})\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n'
            )
        for name, x, y in self.labels:
            out.append(
                f'\t(label "{name}"\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n'
                f'\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
                f'\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n'
            )
        for s, x, y, size in self.texts:
            out.append(
                f'\t(text "{s}"\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n'
                f'\t\t\t(font\n\t\t\t\t(size {fmt(size)} {fmt(size)}))\n\t\t)\n'
                f'\t\t(uuid "{u()}")\n\t)\n'
            )
        idx = content.find("(sheet_instances")
        assert idx != -1, "sheet_instances not found"
        content = content[:idx] + "".join(out) + content[idx:]
        self.sch.write_text(content, encoding="utf-8")


def main():
    SCH.parent.mkdir(parents=True, exist_ok=True)
    SCH.write_text(f'''(kicad_sch
\t(version 20260101)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A3")
\t(title_block
\t\t(title "Практическая работа №1. Схема ввода-вывода на STM32F100")
\t\t(date "{date.today().isoformat()}")
\t\t(rev "1.0")
\t\t(company "РТУ МИРЭА, 09.03.02, ЭФБО-04-24, Ляпунов Д.Д.")
\t)
\t(lib_symbols
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)
''', encoding="utf-8")
    PRO.write_text(json.dumps({
        "board": {},
        "meta": {"filename": PRO.name, "version": 1},
        "schematic": {},
        "sheets": [],
        "text_variables": {},
    }, indent=2), encoding="utf-8")

    loader = DynamicSymbolLoader(project_path=SCH.parent)
    b = B(SCH)

    def place(lib, sym, ref, val, x, y, angle=0, fp=None):
        loader.inject_symbol_into_schematic(SCH, lib, sym)
        ok = loader.create_component_instance(
            SCH, lib, sym, reference=ref, value=val,
            x=snap(x), y=snap(y), angle=angle, footprint=fp or "",
        )
        assert ok, (lib, sym, ref)

    def inject(lib, sym):
        loader.inject_symbol_into_schematic(SCH, lib, sym)

    def mp(name):
        return pin_abs(MCU_X, MCU_Y, 0, *MCU_PINS[name][0][:2])

    inject("power", "+3V3")
    inject("power", "GND")
    inject("power", "PWR_FLAG")
    inject("Device", "C")
    inject("Device", "R")
    inject("Device", "LED")
    inject("Device", "R_Potentiometer")
    inject("Switch", "SW_SPDT")
    inject("Display_Character", "KCSC02-105")

    # ============================== MCU ============================== #
    MCU_X, MCU_Y = 139.7, 148.59
    MCU_PINS.update(mcu_pin_table())
    place("MCU_ST_STM32F1", "STM32F100C8Tx", "DD1", "STM32F100C8Tx", MCU_X, MCU_Y)

    PA = {f"PA{m}": mp(f"PA{m}") for m in range(16)}
    PB = {f"PB{m}": mp(f"PB{m}") for m in range(16)}
    PC = {f"PC{m}": mp(f"PC{m}") for m in (13, 14, 15)}
    PD = {f"PD{m}": mp(f"PD{m}") for m in (0, 1)}

    # ======================= питание MCU ============================= #
    # +3V3 сверху (y=105.41), GND снизу (y=194.31)
    rail_top_y, rail_bot_y = 105.41, 194.31
    vdd = [mp("VBAT"), mp("VDD"), mp("VDD"), mp("VDD"), mp("VDDA")]
    for px, py in vdd:
        b.wire([(px, py), (px, rail_top_y)])
    xs = sorted(p[0] for p in vdd)
    b.wire([(min(xs), rail_top_y), (max(xs), rail_top_y)])
    cx = snap((min(xs) + max(xs)) / 2)   # 139.7
    b.wire([(cx, rail_top_y), (cx, 100.33)])
    b.junction(cx, rail_top_y)
    place("power", "+3V3", "#PWR01", "+3V3", cx, 100.33)
    # PWR_FLAG отнесён на 7.62 влево (было cx-2.54 — тексты +3V3/PWR_FLAG сливались)
    place("power", "PWR_FLAG", "#FLG01", "PWR_FLAG", 132.08, 100.33)
    b.wire([(132.08, 100.33), (cx, 100.33)])

    vss = [mp("VSS"), mp("VSSA")]        # VSS: 3 шт. в одной точке
    for px, py in vss:
        b.wire([(px, py), (px, rail_bot_y)])
    vxs = sorted(p[0] for p in vss)
    b.wire([(min(vxs), rail_bot_y), (max(vxs), rail_bot_y)])
    bx = snap((min(vxs) + max(vxs)) / 2)  # 140.97
    b.wire([(bx, rail_bot_y), (bx, 198.12)])
    b.junction(bx, rail_bot_y)
    place("power", "GND", "#PWR02", "GND", bx, 198.12)
    # PWR_FLAG отнесён вправо до сетки (было +2.54 — сливался с GND)
    place("power", "PWR_FLAG", "#FLG02", "PWR_FLAG", 151.13, 198.12)
    b.wire([(bx, 198.12), (151.13, 198.12)])

    # развязка C2/C3 над шиной +3V3 (C3 отнесён на +12.7 по сетке — было 3.81, корпуса и порты сливались)
    for ref, cx in (("C2", 149.86), ("C3", 166.37)):
        place("Device", "C", ref, "100nF", cx, 100.33,
              fp="Capacitor_SMD:C_0603_1608Metric")
        place("power", "+3V3", f"#PWR{ref}", "+3V3", cx, 96.52)
        place("power", "GND", f"#GND{ref}", "GND", cx, 104.14)
        b.wire([(cx, 96.52), (cx, 96.52)])
        b.wire([(cx, 104.14), (cx, 104.14)])

    # =================== LED-блок (PA0..PA7) ========================= #
    rail_x = 228.6
    for k in range(8):
        ypin = PA[f"PA{k}"][1]
        yrow = snap(25.4 + 10.16 * k)
        xk = snap(160.02 + 2.54 * k)
        place("Device", "R", f"R{k+1}", "270", 200.66, yrow, 90,
              fp="Resistor_SMD:R_0603_1608Metric")
        place("Device", "LED", f"HL{k+1}", "LED-GREEN", 215.9, yrow, 180,
              fp="LED_SMD:LED_0603_1608Metric")
        b.wire([(157.48, ypin), (xk, ypin)])
        b.wire([(xk, ypin), (xk, yrow)])
        b.wire([(xk, yrow), (196.85, yrow)])
        b.wire([(204.47, yrow), (212.09, yrow)])
        b.wire([(219.71, yrow), (rail_x, yrow)])
        b.label(f"HL{k+1}", 193.04, yrow)
        if k > 0:
            b.junction(rail_x, yrow)
    b.wire([(rail_x, 25.4), (rail_x, 109.22)])
    place("power", "GND", "#PWRLED", "GND", rail_x, 109.22)
    # флаг отнесён вправо до сетки (было +5.08 — тексты налезали)
    place("power", "PWR_FLAG", "#FLGLED", "PWR_FLAG", 240.03, 109.22)
    b.wire([(rail_x, 109.22), (240.03, 109.22)])

    # ================= 7-сегментный индикатор ======================== #
    HG1_Y = 171.45
    place("Display_Character", "KCSC02-105", "HG1", "KCSC02-105", 76.2, HG1_Y,
          fp="Display_7Segment:KCSC02-105")
    seg_names = ["A", "B", "C", "D", "E", "F", "G", "DP"]
    seg_pb = ["PB8", "PB9", "PB10", "PB11", "PB12", "PB13", "PB14", "PB15"]
    seg_off = {"A": 7.62, "B": 5.08, "C": 2.54, "D": 0.0,
               "E": -2.54, "F": -5.08, "G": -7.62, "DP": -10.16}
    for name, pb in zip(seg_names, seg_pb):
        py = snap(HG1_Y - seg_off[name])
        my = PB[pb][1]
        assert abs(my - py) < 0.01, (name, my, py)
        b.wire([(PB[pb][0], my), (68.58, my)])
    cc1, cc2 = (83.82, HG1_Y + 7.62), (83.82, HG1_Y + 10.16)
    b.wire([cc1, (88.9, cc1[1])])
    b.wire([(88.9, cc1[1]), (88.9, 193.04)])
    b.wire([cc2, (88.9, cc2[1])])
    b.junction(88.9, cc2[1])
    place("power", "GND", "#PWR03", "GND", 88.9, 193.04)

    # ============= генераторы уровней SB1..SB4 (SPDT) =================== #
    sw = [("SB1", "PC13", 124.46), ("SB2", "PC14", 133.35),
          ("SB3", "PC15", 142.24), ("SB4", "PD0", 151.13)]
    n = 10
    for ref, pinname, sy in sw:
        place("Switch", "SW_SPDT", ref, "SW-SPDT", 101.6, sy, 180)
        Bx, By = 106.68, sy
        Ax, Ay = 96.52, sy - 2.54
        Cx, Cy = 96.52, sy + 2.54
        # SB2/SB4 отнесены по X на 88.9 (шахматка): иначе порты +3V3/GND соседних
        # кнопок стоят через 3.81 мм друг над другом и их стрелки/подписи сливаются
        jog = ref in ("SB2", "SB4")
        px = 88.9 if jog else Ax
        place("power", "+3V3", f"#PWR{n}", "+3V3", px, snap(Ay - 3.81))
        place("power", "GND", f"#PWR{n+1}", "GND", px, snap(Cy + 3.81))
        if jog:
            b.wire([(Ax, Ay), (px, Ay)])
            b.wire([(px, Ay), (px, snap(Ay - 3.81))])
            b.wire([(Cx, Cy), (px, Cy)])
            b.wire([(px, Cy), (px, snap(Cy + 3.81))])
        else:
            b.wire([(Ax, Ay), (Ax, snap(Ay - 3.81))])
            b.wire([(Cx, Cy), (Cx, snap(Cy + 3.81))])
        mx, my = (PB.get(pinname) or PC.get(pinname) or PD.get(pinname))
        b.wire([(Bx, By), (116.84, By)])
        b.wire([(116.84, By), (116.84, my)])
        b.wire([(116.84, my), (mx, my)])
        b.label(ref, 111.76, By)  # середина провода Bx->116.84 (было 118.11 — висело в воздухе)
        n += 2

    # ================= потенциометр RP1 (PB0, АЦП) ==================== #
    place("Device", "R_Potentiometer", "RP1", "10k", 78.74, 143.51,
          fp="Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical")
    place("power", "+3V3", "#PWR20", "+3V3", 78.74, 139.7)
    place("power", "GND", "#PWR21", "GND", 78.74, 147.32)
    b.wire([(78.74, 143.51 - 3.81), (78.74, 139.7)])
    b.wire([(78.74, 143.51 + 3.81), (78.74, 147.32)])
    b.wire([(82.55, 143.51), (PB["PB0"][0], 143.51)])
    b.label("POT_ADC", 105.41, 143.51)
    # C1 — фильтр на входе АЦП: от цепи POT_ADC к GND
    place("Device", "C", "C1", "100nF", 86.36, 147.32,
          fp="Capacitor_SMD:C_0603_1608Metric")
    b.junction(86.36, 143.51)
    place("power", "GND", "#PWR22", "GND", 86.36, 158.75)
    b.wire([(86.36, 151.13), (86.36, 158.75)])  # верх C1 (пин 151.13) к GND; низ (143.51) уже на POT_ADC

    # ===================== цепь сброса NRST =========================== #
    place("Device", "R", "R9", "10k", 113.03, 115.57, 90,
          fp="Resistor_SMD:R_0603_1608Metric")
    b.wire([(121.92, 115.57), (116.84, 115.57)])
    b.wire([(109.22, 115.57), (106.68, 115.57)])
    place("power", "+3V3", "#PWR23", "+3V3", 106.68, 110.49)
    b.wire([(106.68, 115.57), (106.68, 110.49)])
    place("Device", "C", "C4", "100nF", 119.38, 111.76)
    b.wire([(116.84, 115.57), (119.38, 115.57)])  # верх C4 к NRST (без сквозной закоротки на GND)
    b.junction(119.38, 115.57)
    place("power", "GND", "#PWR24", "GND", 119.38, 107.95)

    # ======================= BOOT0 -> R10 ============================= #
    place("Device", "R", "R10", "10k", 113.03, 120.65, 90,
          fp="Resistor_SMD:R_0603_1608Metric")
    b.wire([(121.92, 120.65), (116.84, 120.65)])
    b.wire([(109.22, 120.65), (106.68, 120.65)])
    place("power", "GND", "#PWR25", "GND", 106.68, 120.65)

    # ============= неиспользуемые выводы -> no_connect ================ #
    used = set(PA) | set(PB) | set(PC) | set(PD) | {
        "NRST", "BOOT0", "VBAT", "VDD", "VDDA", "VSS", "VSSA"}
    for name, plist in MCU_PINS.items():
        if name in used:
            continue
        for px, py, num in plist:
            b.no_connect(*pin_abs(MCU_X, MCU_Y, 0, px, py))

    # ============================ подписи ============================= #
    # Тексты — в свободной зоне ВВЕРХУ-влево внутри рамки (20,15/20,22):
    # низ листа (250/258) оказался зоной штампа — текст «выплывал за рамки».
    # Пост-обработка Reference/Value в .kicad_sch: R — вынос ±7 по Y,
    # SB — Ref влево-вниз/Val вправо-вверх, C — в стороны ±6 (C2/C3 со сдвигом
    # ∓3 по Y), HG1/RP1/DD1 — разнесены; Value портов питания — наружу от символов
    # (+3V3 вверх, GND вниз), иначе соседние +3V3/GND сливаются (см. коммит).
    b.text("Соединения с МК - зелёным (0 132 0)", 20, 15, 1.5)
    b.text("Стенд «Учтех-Профи», МК STM32F100C8Tx", 20, 22, 1.5)

    b.flush()
    print("OK:", SCH)


if __name__ == "__main__":
    main()