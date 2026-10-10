#!/usr/bin/env python3
"""Генератор схемы KiCad для ПР №5 «Отображение информации в системах с МК».

Вариант 1:
  Задание 1: VAL=0FFh (255), порт P1, трёхразрядный индикатор (HG1-HG3).
  Задание 2: a=23, b=52 (BCD), сумма 75, порт P1, двухразрядный индикатор (HG4-HG5).

Метод: программный (таблица кодов, рис.44/46 ТЗ) + динамическая индикация
для нескольких разрядов на одном порту (сегментная шина общая, общие аноды
коммутируются ключами VT1-VT5 с линий P3). Индикаторы SA39-11EWA (общий анод,
одиночный, аналог рис.41-42). МК — P8051AH (MCU_Intel, аналог МК-51).
Соединения — именованными цепями (labels), как в ПР2: эквивалент проводов,
читаемость выше, пересечений нет.
Обозначения — по ГОСТ 2.710-81: DD (МК), HG (индикаторы), R, C, VT, Y.
Формат KiCad 10, лист A3.
"""
import importlib.util
import json
import re
import sys
import uuid
from datetime import date
from pathlib import Path
sys.path.insert(0, "/Users/d.d.lyapunov/MCP/KiCAD-MCP-Server/python")

GRID = 1.27
ROOT = Path(__file__).resolve().parent
SCH = ROOT / "PR5_SevenSeg.kicad_sch"
PRO = ROOT / "PR5_SevenSeg.kicad_pro"
SYMDIR = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
ROOT_UUID = "55555555-5555-5555-5555-555555555555"

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
    return round(round(float(v) / GRID) * GRID, 2)


def fmt(v):
    f = float(v)
    return str(int(f)) if f.is_integer() else str(round(f, 4))


def parse_pins(lib, sym):
    s = (SYMDIR / f"{lib}.kicad_sym").read_text(encoding="utf-8")
    i = s.find(f'(symbol "{sym}"')
    assert i != -1, (lib, sym)
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


class B:
    def __init__(self, sch_path):
        self.sch = sch_path
        self.wires = []
        self.junctions = []
        self.labels = []
        self.nocos = []
        self.texts = []

    def wire(self, pts):
        pts = [(snap(a), snap(b)) for a, b in pts]
        for p, q in zip(pts, pts[1:]):
            self.wires.append((p, q))

    def junction(self, x, y):
        self.junctions.append((snap(x), snap(y)))

    def label(self, name, x, y, justify="left"):
        self.labels.append((name, snap(x), snap(y), justify))

    def no_connect(self, x, y):
        self.nocos.append((snap(x), snap(y)))

    def text(self, s, x, y, size=1.7):
        self.texts.append((s, snap(x), snap(y), size))

    def flush(self):
        content = self.sch.read_text(encoding="utf-8")
        out = []
        for x, y in self.junctions:
            out.append(f'\t(junction\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(diameter 0)\n\t\t(uuid "{u()}")\n\t)\n')
        for x, y in self.nocos:
            out.append(f'\t(no_connect\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(uuid "{u()}")\n\t)\n')
        for (x1, y1), (x2, y2) in self.wires:
            out.append(
                f'\t(wire\n\t\t(pts\n\t\t\t(xy {fmt(x1)} {fmt(y1)})\n'
                f'\t\t\t(xy {fmt(x2)} {fmt(y2)})\n\t)'
                f'\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t)\n\t\t(uuid "{u()}")\n\t)\n')
        for name, x, y, justify in self.labels:
            safe = name.replace('"', "'")
            j = justify if justify in ("left", "right") else "left"
            out.append(
                f'\t(label "{safe}"\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n\t\t\t(font\n'
                f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {j} bottom)\n\t)\n\t\t(uuid "{u()}")\n\t)\n')
        for s, x, y, size in self.texts:
            safe = s.replace('"', "'")
            out.append(
                f'\t(text "{safe}"\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n\t\t\t(font\n'
                f'\t\t\t\t(size {fmt(size)} {fmt(size)}))\n\t\t\t(justify left bottom)\n\t)\n'
                f'\t\t(uuid "{u()}")\n\t)\n')
        idx = content.find("(sheet_instances")
        assert idx != -1
        content = content[:idx] + "".join(out) + content[idx:]
        self.sch.write_text(content, encoding="utf-8")


def main():
    SCH.write_text(
        f'''(kicad_sch
\t	(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A3")
\t(title_block
\t\t(title "ПР5. Семисегментные индикаторы (вар.1)")
\t\t(date "{date.today().isoformat()}")
\t\t(rev "1.0")
\t\t(company "РТУ МИРЭА, ПЭПС, 5 семестр")
\t)
\t(lib_symbols
\t)
\t(sheet_instances
\t\t(path "/" (page "1"))
\t)
)
''', encoding="utf-8")
    PRO.write_text(json.dumps({
        "board": {}, "meta": {"filename": PRO.name, "version": 1},
        "schematic": {}, "sheets": [], "text_variables": {},
    }, indent=2), encoding="utf-8")

    loader = DynamicSymbolLoader(project_path=ROOT)
    b = B(SCH)

    def place(lib, sym, ref, val, x, y, angle=0, fp=""):
        loader.inject_symbol_into_schematic(SCH, lib, sym)
        ok = loader.create_component_instance(
            SCH, lib, sym, reference=ref, value=val,
            x=snap(x), y=snap(y), angle=angle, footprint=fp)
        assert ok, (lib, sym, ref)

    def inject(lib, sym):
        loader.inject_symbol_into_schematic(SCH, lib, sym)

    for lib, sym in [("power", "+5V"), ("power", "GND"), ("power", "PWR_FLAG"),
                     ("Device", "R"), ("Device", "C"), ("Device", "Crystal"),
                     ("Device", "Q_PNP")]:
        inject(lib, sym)

    P_MCU = parse_pins("MCU_Intel", "P8051AH")
    P_DISP = parse_pins("Display_Character", "SA39-11EWA")
    P_R = parse_pins("Device", "R")
    P_C = parse_pins("Device", "C")
    P_Q = parse_pins("Device", "Q_PNP")
    P_XT = parse_pins("Device", "Crystal")

    def pin_by_number(pins_dict, number):
        for _name, lst in pins_dict.items():
            for (dx, dy, num) in lst:
                if str(num) == str(number):
                    return dx, dy
        raise KeyError(number)

    def pin_pos(ox, oy, dx, dy):
        return snap(ox + dx), snap(oy - dy)

    def stub_label(ox, oy, dx, dy, net, length=5.08):
        px, py = pin_pos(ox, oy, dx, dy)
        side = -1 if dx < 0 else (1 if dx > 0 else (-1 if dy < 0 else 1))
        ex = snap(px + side * length)
        b.wire([(px, py), (ex, py)])
        b.label(net, ex, py, "left" if side > 0 else "right")
        return (ex, py)

    def mcu_pin(ox, oy, number, net, length=5.08):
        dx, dy = pin_by_number(P_MCU, number)
        # P8051AH имеет дублирующиеся имена (P1.0 и P1.0/T2) — берём первые координаты по номеру
        return stub_label(ox, oy, dx, dy, net, length)

    # ---------- размещение ----------
    DD1_X, DD1_Y = 115, 150
    DD2_X, DD2_Y = 285, 150

    place("MCU_Intel", "P8051AH", "DD1", "P8051AH (МК-51, Задание 1)", DD1_X, DD1_Y,
          fp="Package_DIP:DIP-40_W15.24mm")
    place("MCU_Intel", "P8051AH", "DD2", "P8051AH (МК-51, Задание 2)", DD2_X, DD2_Y,
          fp="Package_DIP:DIP-40_W15.24mm")

    # Дисплеи: Задание 1 — три разряда (сотни/десятки/единицы VAL=255 -> 2,5,5)
    # цифра разряда закодирована в Value (видно под корпусом), отдельные
    # текстовые подписи убраны — они ложились поверх меток сегментов.
    # Дисплеи сдвинуты влево (x=40/210), ключи вправо (x=66/236): иначе короткий
    # стаб базы VT и его подпись ложатся на корпус дисплея.
    HG1 = (40, 110, "HG1", "[2 сотни]")
    HG2 = (40, 150, "HG2", "[5 десятки]")
    HG3 = (40, 190, "HG3", "[5 единицы]")
    # Задание 2 — два разряда (десятки/единицы 23+52=75 -> 7,5)
    HG4 = (210, 130, "HG4", "[7 десятки]")
    HG5 = (210, 170, "HG5", "[5 единицы]")
    HG_DIGIT = {"HG1": "2", "HG2": "5", "HG3": "5", "HG4": "7", "HG5": "5"}
    for (hx, hy, ref, _note) in (HG1, HG2, HG3, HG4, HG5):
        # Value — чистый тип по ГОСТ 2.702 (без суффиксов); ожидаемая цифра
        # показана отдельной подписью слева от разрядов (см. тексты ниже).
        place("Display_Character", "SA39-11EWA", ref, "SA39-11EWA", hx, hy,
              fp="Display_7Segment:Sx39-1xxxxx")

    # Сегментные резисторы 270 Ом (по ТЗ рис.44: R1..R8 — 270).
    # Шаг 12.7 мм: при шаге 7.62 соседние выводы (пин2 Rk и пин1 Rk+1)
    # попадали в одну точку и закорачивали соседние цепи (ERC multiple_net_names).
    # Z1: R1..R8 горизонтально между DD1 и дисплеями
    SEG_NAMES = ["A", "B", "C", "D", "E", "F", "G", "H"]  # H = DP (рис.44: сегменты A-H)
    SEG_PINS = {"A": "10", "B": "9", "C": "7", "D": "5", "E": "4", "F": "2", "G": "1", "H": "6"}
    SEG_RY = [snap(100 + k * 12.7) for k in range(8)]
    for k, seg in enumerate(SEG_NAMES):
        ry = SEG_RY[k]
        # Z1
        place("Device", "R", f"R{k+1}", "270", 80, ry, 0,
              fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
        # Z2 (нумерация сквозная R13-R20 — без пропусков по ГОСТ 2.710)
        place("Device", "R", f"R{k+13}", "270", 250, ry, 0,
              fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")

    # Базовые резисторы ключей 4.7k — вынесены в свободную верхнюю зону,
    # чтобы подписи SEL/SELB не ложились на VT и дисплеи.
    for ref, bx, by in (("R9", 100, 70), ("R10", 130, 70), ("R11", 160, 70),
                        ("R21", 250, 70), ("R22", 280, 70)):
        place("Device", "R", ref, "4.7k", bx, by, 0,
              fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")

    # Ключи общих анодов (PNP) — отнесены от базовых резисторов на 10 мм,
    # иначе корпуса и подписи VT/R налезают друг на друга.
    # VT3 поднят на 184.15 (был 190): иначе подпись коллектора 1D3 ложится на
    # подпись 1P7 вывода R8 (одна строка y). Остальные VT соосны своим HG.
    for ref, qx, qy in (("VT1", 66, 110), ("VT2", 66, 150), ("VT3", 66, 184.15),
                        ("VT4", 236, 130), ("VT5", 236, 170)):
        place("Device", "Q_PNP", ref, "KT361", qx, qy,
              fp="Package_TO_SOT_THT:TO-92_Inline")

    # Кварцы 12 МГц + конденсаторы 33п + RST-цепь + питание для каждого МК.
    # Кварц отнесён на +58.42 (низ корпуса +20 зазора, был +45.72 — налезал на R8),
    # RST вынесена ВПРАВО от МК (была слева поверх R1/R12 — корпуса пересекались).
    # Иначе корпуса C5/C6 и их стабы лежат внутри bbox DD и дают symbol_wire_conflict.
    RST_POS = {"Z1": (150, 100, 162, 100), "Z2": (330, 100, 342, 100)}  # R(x,y), C(x,y)
    for tag, mcu_x, mcu_y in (("Z1", DD1_X, DD1_Y), ("Z2", DD2_X, DD2_Y)):
        qx = snap(mcu_x - 25.4)
        qy = snap(mcu_y + 58.42)
        place("Device", "Crystal", f"Y{1 if tag == 'Z1' else 2}", "12MHz", qx, qy,
              fp="Crystal:Crystal_HC49-U_Horizontal")
        place("Device", "C", f"C{1 if tag == 'Z1' else 3}", "33p", snap(qx - 12.7), qy,
              fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
        place("Device", "C", f"C{2 if tag == 'Z1' else 4}", "33p", snap(qx + 12.7), qy,
              fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
        rrx, rry, ccx, ccy = RST_POS[tag][0], RST_POS[tag][1], RST_POS[tag][2], RST_POS[tag][3]
        place("Device", "R", f"R{12 if tag == 'Z1' else 23}", "10k", rrx, rry,
              fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
        place("Device", "C", f"C{5 if tag == 'Z1' else 6}", "10u", ccx, ccy,
              fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
        place("power", "+5V", f"#PWR_{tag}_VCC", "+5V", mcu_x, snap(mcu_y - 45.72)) if tag == "Z1" else None
        place("power", "GND", f"#GND_{tag}_VSS", "GND", mcu_x, snap(mcu_y + 45.72)) if tag == "Z1" else None

    # ---------- цепи ----------
    # Питание/земля/опорные пины МК (короткие имена: nX1/nX2=кварц, nRST=сброс)
    for (mx, my, tag) in ((DD1_X, DD1_Y, "Z1"), (DD2_X, DD2_Y, "Z2")):
        n = "1" if tag == "Z1" else "2"
        mcu_pin(mx, my, "40", "+5V")   # VCC
        mcu_pin(mx, my, "20", "GND")   # VSS
        mcu_pin(mx, my, "31", "+5V")   # EA=+5V (внутреннее ПЗУ)
        # XTAL
        dx1, dy1 = pin_by_number(P_MCU, "19")
        stub_label(mx, my, dx1, dy1, f"{n}X1", 3.81)
        dx2, dy2 = pin_by_number(P_MCU, "18")
        stub_label(mx, my, dx2, dy2, f"{n}X2", 3.81)
        # RST
        mcu_pin(mx, my, "9", f"{n}RST")
        # PSEN/ALE не используются в программном варианте -> no_connect
        for nc_num in ("29", "30"):
            dx, dy = pin_by_number(P_MCU, nc_num)
            b.no_connect(*pin_pos(mx, my, dx, dy))
        # Неиспользуемые порты -> no_connect (P0 целиком, P2 целиком, остатки P3)
        for nc_num in ("39", "38", "37", "36", "35", "34", "33", "32",
                       "21", "22", "23", "24", "25", "26", "27", "28"):
            dx, dy = pin_by_number(P_MCU, nc_num)
            b.no_connect(*pin_pos(mx, my, dx, dy))

    # P1 -> сегментные резисторы -> общая сегментная шина -> все HG блока
    # порядок бит: P1.0->A, P1.1->B, P1.2->C, P1.3->D, P1.4->E, P1.5->F, P1.6->G, P1.7->DP
    # Стабы МК чередуются 5.08/10.16 (пины P1 через 2.54 — иначе подписи сливаются).
    # Стабы дисплеев чередуются 3.81/7.62 по той же причине.
    # У сегментных R стабы разведены в разные стороны (pin1 влево, pin2 вправо),
    # чтобы подписи Zx_P1_k и Zx_SEG_x не встречались в одном зазоре с подписями МК.
    # Короткие имена цепей (читаемость: длинные Z1_SEG_A налезали друг на друга,
    # пины P1 стоят через 2.54 мм). Легенда — в подписях листа и в отчёте:
    #   1P0-1P7 = биты P1 Задания 1; 1A-1H = сегменты (H=DP); 1S0-1S2 = выбор
    #   разряда с P3; 1S0B-1S2B = базы ключей; 1D1-1D3 = общие аноды;
    #   1X1/1X2 = кварц; 1RST = сброс. Префикс 2 = то же для Задания 2.
    P1_NUMS = ["1", "2", "3", "4", "5", "6", "7", "8"]
    for k, seg in enumerate(SEG_NAMES):
        ry = SEG_RY[k]
        mlen = 5.08  # uniform: короткие имена (3 символа) в ровный столбец, зазор до R-меток ~1.6 мм
        dlen = 5.08
        # --- блок Z1 ---
        mcu_pin(DD1_X, DD1_Y, P1_NUMS[k], f"1P{k}", mlen)
        dx1, dy1 = pin_by_number(P_R, "1")
        p1x, p1y = pin_pos(80, ry, dx1, dy1)
        b.wire([(p1x, p1y), (snap(p1x - 6.35), p1y)])
        b.label(f"1P{k}", snap(p1x - 6.35), p1y, "right")
        dx2, dy2 = pin_by_number(P_R, "2")
        p2x, p2y = pin_pos(80, ry, dx2, dy2)
        b.wire([(p2x, p2y), (snap(p2x + 6.35), p2y)])
        b.label(f"1{seg}", snap(p2x + 6.35), p2y, "left")
        for (hx, hy, _ref, _n) in (HG1, HG2, HG3):
            dx, dy = pin_by_number(P_DISP, SEG_PINS[seg])
            stub_label(hx, hy, dx, dy, f"1{seg}", dlen)
        # --- блок Z2 ---
        mcu_pin(DD2_X, DD2_Y, P1_NUMS[k], f"2P{k}", mlen)
        p1x, p1y = pin_pos(250, ry, dx1, dy1)
        b.wire([(p1x, p1y), (snap(p1x - 6.35), p1y)])
        b.label(f"2P{k}", snap(p1x - 6.35), p1y, "right")
        p2x, p2y = pin_pos(250, ry, dx2, dy2)
        b.wire([(p2x, p2y), (snap(p2x + 6.35), p2y)])
        b.label(f"2{seg}", snap(p2x + 6.35), p2y, "left")
        for (hx, hy, _ref, _n) in (HG4, HG5):
            dx, dy = pin_by_number(P_DISP, SEG_PINS[seg])
            stub_label(hx, hy, dx, dy, f"2{seg}", dlen)

    # Выбор разряда: P3.0..P3.2 (Z1) и P3.0..P3.1 (Z2) через 4.7k на базы PNP,
    # эмиттеры на +5V, коллекторы на общие аноды CA (пины 3 и 8 каждого HG)
    SEL_Z1 = [("10", "R9", "VT1", "1S0", "1D1", (HG1,)), ("11", "R10", "VT2", "1S1", "1D2", (HG2,)),
              ("12", "R11", "VT3", "1S2", "1D3", (HG3,))]
    SEL_Z2 = [("10", "R21", "VT4", "2S0", "2D1", (HG4,)), ("11", "R22", "VT5", "2S1", "2D2", (HG5,))]
    qpos = {"VT1": (66, 110), "VT2": (66, 150), "VT3": (66, 184.15),
            "VT4": (236, 130), "VT5": (236, 170)}
    rpos = {"R9": (100, 70), "R10": (130, 70), "R11": (160, 70),
            "R21": (250, 70), "R22": (280, 70)}
    for (mcu_x, mcu_y, items) in ((DD1_X, DD1_Y, SEL_Z1), (DD2_X, DD2_Y, SEL_Z2)):
        for (pnum, rref, vtref, selnet, dignet, hgs) in items:
            mcu_pin(mcu_x, mcu_y, pnum, selnet)
            rx, ry = rpos[rref]
            stub_label(rx, ry, *pin_by_number(P_R, "1"), selnet, 3.81)
            stub_label(rx, ry, *pin_by_number(P_R, "2"), f"{selnet}B", 3.81)
            qx, qy = qpos[vtref]
            dxb, dyb = pin_by_number(P_Q, "B")
            stub_label(qx, qy, dxb, dyb, f"{selnet}B", 3.81)
            dxe, dye = pin_by_number(P_Q, "E")
            stub_label(qx, qy, dxe, dye, "+5V", 3.81)
            dxc, dyc = pin_by_number(P_Q, "C")
            stub_label(qx, qy, dxc, dyc, dignet, 3.81)
            for (hx, hy, _ref, _n) in hgs:
                for canum in ("3", "8"):
                    dx, dy = pin_by_number(P_DISP, canum)
                    stub_label(hx, hy, dx, dy, dignet, 3.81)

    # Остатки P3 -> no_connect
    for (mx, my, used) in ((DD1_X, DD1_Y, {"10", "11", "12"}), (DD2_X, DD2_Y, {"10", "11"})):
        for pnum, pname in (("13", "P3.2"), ("14", "P3.4"), ("15", "P3.5"),
                            ("16", "P3.6"), ("17", "P3.7")):
            if pnum in used:
                continue
            # номера 13..17 соответствуют P3.3..P3.7
            dx, dy = pin_by_number(P_MCU, pnum)
            b.no_connect(*pin_pos(mx, my, dx, dy))
        # P3.2 у DD2 не используется (только 2 разряда)
        if used == {"10", "11"}:
            dx, dy = pin_by_number(P_MCU, "12")
            b.no_connect(*pin_pos(mx, my, dx, dy))

    # Кварцевая обвязка и RST (именованные цепи, без длинных проводов).
    # RST-цепь лежит справа от МК (см. RST_POS выше), кварц внизу на +58.42.
    for tag, mx, my in (("Z1", DD1_X, DD1_Y), ("Z2", DD2_X, DD2_Y)):
        n = "1" if tag == "Z1" else "2"
        qx = snap(mx - 25.4)
        qy = snap(my + 58.42)
        dx1, dy1 = pin_by_number(P_XT, "1")
        stub_label(qx, qy, dx1, dy1, f"{n}X1", 3.81)
        dx2, dy2 = pin_by_number(P_XT, "2")
        stub_label(qx, qy, dx2, dy2, f"{n}X2", 3.81)
        c1x = snap(qx - 12.7)
        stub_label(c1x, qy, *pin_by_number(P_C, "1"), f"{n}X1", 3.81)
        stub_label(c1x, qy, *pin_by_number(P_C, "2"), "GND", 3.81)
        c2x = snap(qx + 12.7)
        stub_label(c2x, qy, *pin_by_number(P_C, "1"), f"{n}X2", 3.81)
        stub_label(c2x, qy, *pin_by_number(P_C, "2"), "GND", 3.81)
        # RST: R к GND, C к +5V (позиции из RST_POS)
        rrx, rry, ccx, ccy = RST_POS[tag][0], RST_POS[tag][1], RST_POS[tag][2], RST_POS[tag][3]
        stub_label(rrx, rry, *pin_by_number(P_R, "1"), f"{n}RST", 3.81)
        stub_label(rrx, rry, *pin_by_number(P_R, "2"), "GND", 3.81)
        stub_label(ccx, ccy, *pin_by_number(P_C, "1"), f"{n}RST", 3.81)
        stub_label(ccx, ccy, *pin_by_number(P_C, "2"), "+5V", 3.81)

    # PWR_FLAG на +5V/GND (один на каждую цепь питания — цепи глобальные,
    # второй флаг на той же цепи даёт ошибку pin_to_pin Power-output-to-Power-output)
    place("power", "PWR_FLAG", "#FLG_5V", "PWR_FLAG", snap(DD1_X - 12.7), snap(DD1_Y - 45.72))
    b.wire([(snap(DD1_X - 12.7), snap(DD1_Y - 45.72)), (DD1_X, snap(DD1_Y - 45.72))])
    place("power", "PWR_FLAG", "#FLG_GND", "PWR_FLAG", snap(DD1_X - 12.7), snap(DD1_Y + 45.72))
    b.wire([(snap(DD1_X - 12.7), snap(DD1_Y + 45.72)), (DD1_X, snap(DD1_Y + 45.72))])

    # ---------- подписи (в свободных зонах, не на проводах) ----------
    b.text("ПР №5. Отображение информации на семисегментных индикаторах. Вариант 1.", 20, 15, 2.0)
    b.text("Задание 1 (слева): VAL=0FFh (255) -> P1 -> HG1..HG3 (2, 5, 5). Динамическая индикация, выбор разряда P3.0-P3.2.", 20, 22, 1.5)
    b.text("Задание 2 (справа): a=23, b=52 (BCD), сумма 75 -> P1 -> HG4,HG5 (7, 5). Выбор разряда P3.0-P3.1.", 20, 29, 1.5)
    b.text("Программный вариант (рис.44/46 ТЗ): 8 линий порта + таблица кодов, R=270 Ом, индикаторы с общим анодом.", 20, 36, 1.5)
    b.text("Соединения — именованными цепями (эквивалент проводов). Легенда: 1P0-1P7 биты P1; 1A-1H сегменты (H=DP);", 20, 43, 1.5)
    b.text("1S0-1S2 выбор разряда с P3; 1S0B-1S2B базы ключей; 1D1-1D3 общие аноды; 1X1/1X2 кварц; 1RST сброс. Префикс 2 — Задание 2.", 20, 50, 1.5)
    # Ожидаемые цифры разрядов — подписью ПОД своим разрядом (в свободной зоне,
    # строго внутри рамки листа x>=15: прежнее x=6 ложилось на рамку и её зоновые метки).
    # Z1: под HG1..HG3 (низ корпуса ~120/162/202 + стабы на строках пинов — y=126/168/208 свободны).
    # Z2: под HG4/HG5 (низ ~142/182 — y=148/188 свободны).
    b.text("2 (сотни)", 30, 126, 1.5)
    b.text("5 (дес.)", 30, 168, 1.5)
    b.text("5 (ед.)", 30, 208, 1.5)
    b.text("7 (дес.)", 198, 148, 1.5)
    b.text("5 (ед.)", 198, 188, 1.5)

    b.flush()
    print("OK:", SCH)


if __name__ == "__main__":
    main()
