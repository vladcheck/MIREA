#!/usr/bin/env python3
"""
ЛР №6 «Изучение принципов работы ЦАП».
Генератор схемы KiCad — аналог рис.50 (переключатели+ЦАП) и рис.51 (МК-51+ЦАП) методички.

Вариант 1 (ТЗ табл.15): коды 8, 36, 107; порт P1.

Соответствие Multisim -> KiCad:
  A1 (виртуальный 8-бит ЦАП, Mixed) -> DA1/DA2 Analog_DAC:DAC08 (8-бит, параллельный)
  J1..J8 (Basic SPDT)               -> SA1..SA8 Switch:SW_SPDT (A=+5V лог.1, C=GND лог.0, B=общий к ЦАП)
  V1 (Indicator вольтметр)          -> PV1/PV2 Connector:Conn_01x02_Pin (пробник: 1=выход ЦАП, 2=GND)
  XSC1 (осциллограф)                -> XSC1/XSC2 Connector:Conn_01x02_Pin (пробник ALE/выхода)
  U1 8051 (МК-51)                   -> DD1 MCU_Intel:P8051AH
  VCC 5V                            -> power:+5V / GND + PWR_FLAG

Обозначения — по ГОСТ 2.710-81: DD1 (МК), DA1/DA2 (ЦАП), SA1-SA8 (переключатели),
PV1/PV2 (вольтметры-пробники), Y1 (кварц), R/C по ЕСКД.

Топология: все связи — именованными цепями (короткий стаб от пина + метка).
Физических длинных проводов между блоками нет — аналог шин из Multisim,
читаемость не страдает, пересечений текстов с линиями нет.

Сети:
  Задание 1: T1_D0..T1_D7 (SAk.B <-> DA1.Bk), T1_OUT (DA1.I+ <-> PV1.1/XSC1.1)
  Задание 2: T2_D0..T2_D7 (DD1.P1.k <-> DA2.Bk), T2_OUT (DA2.I+ <-> PV2.1/XSC2.1)
Блоки независимы (как два отдельных схемных проекта рис.50/рис.51).

DAC08: B0=LSB(D0) ... B7=MSB(D7); V+=+5V, V-=GND (однополярная учебная модель),
VLC=GND, R+=+5V (Vref=5В), R-=GND, I+=выход, I-=GND, CMP=no_connect.
Uвых идеального 8-бит ЦАП: U = D * Uref / 255 (ЗМР=19.6мВ при Uref=5В, см. ТЗ п.1.2).

Формат KiCad 10. Использование: python3 generate_schematic.py
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
SCH = ROOT / "LR6_DAC.kicad_sch"
PRO = ROOT / "LR6_DAC.kicad_pro"
SYMDIR = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
ROOT_UUID = "66666666-7777-8888-9999-aaaaaaaaaaaa"

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
                f'\t(wire\n\t\t(pts\n\t\t\t(xy {fmt(x1)} {fmt(y1)})\n\t\t\t(xy {fmt(x2)} {fmt(y2)})\n\t\t)'
                f'\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n')
        for name, x, y, justify in self.labels:
            safe = name.replace('"', "'")
            j = justify if justify in ("left", "right") else "left"
            out.append(
                f'\t(label "{safe}"\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {j} bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n')
        for s, x, y, size in self.texts:
            safe = s.replace('"', "'")
            out.append(
                f'\t(text "{safe}"\n\t\t(at {fmt(x)} {fmt(y)} 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size {fmt(size)} {fmt(size)}))\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n')
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
\t\t		(title "ЛР6. ЦАП (вар.1)")
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
                     ("Connector", "Conn_01x02_Pin")]:
        inject(lib, sym)

    P_MCU = parse_pins("MCU_Intel", "P8051AH")
    P_DAC = parse_pins("Analog_DAC", "DAC08")
    P_SW = parse_pins("Switch", "SW_SPDT")
    P_CONN = parse_pins("Connector", "Conn_01x02_Pin")
    P_R = parse_pins("Device", "R")
    P_C = parse_pins("Device", "C")
    P_XT = parse_pins("Device", "Crystal")

    def pin_pos(ox, oy, dx, dy):
        # KiCad lib y-up -> схема y-down
        return snap(ox + dx), snap(oy - dy)

    def stub_label(ox, oy, dx, dy, net, length=5.08):
        px, py = pin_pos(ox, oy, dx, dy)
        side = -1 if dx < 0 else (1 if dx > 0 else (-1 if dy < 0 else 1))
        ex = snap(px + side * length)
        b.wire([(px, py), (ex, py)])
        b.label(net, ex, py, "left" if side > 0 else "right")
        return (ex, py)

    def pin_by_number(pins_dict, number):
        for _name, lst in pins_dict.items():
            for (dx, dy, num) in lst:
                if str(num) == str(number):
                    return dx, dy
        raise KeyError(number)

    def single(pins_dict, ox, oy, key, net, length=5.08):
        dx, dy, _ = pins_dict[key][0]
        stub_label(ox, oy, dx, dy, net, length)

    # ================= ЗАДАНИЕ 1 (аналог рис.50), слева =================
    DA1_X, DA1_Y = 115, 140
    place("Analog_DAC", "DAC08", "DA1", "DAC08 (ЦАП Зад.1, 8 бит)", DA1_X, DA1_Y,
          fp="Package_DIP:DIP-16_W7.62mm")
    # Переключатели SA1..SA8: столбец слева, шаг 12.7
    SA_X = 55
    SA_Y0, SA_STEP = 88, 12.7
    dac_b_names = ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]  # B0=LSB(D0)
    for k in range(8):
        say = snap(SA_Y0 + k * SA_STEP)
        ref = f"SA{k+1}"
        place("Switch", "SW_SPDT", ref, f"J{k+1} (бит D{k})", SA_X, say,
              fp="Button_Switch_THT:SW_E-Switch_EG1271_SPDT")
        net = f"T1_D{k}"
        # B (общий, пин 2 слева) -> сеть данных
        dx, dy, _ = P_SW["B"][0]
        stub_label(SA_X, say, dx, dy, net)
        # A (пин 1 справа сверху) -> +5V (лог.1)
        dx, dy, _ = P_SW["A"][0]
        stub_label(SA_X, say, dx, dy, "+5V", length=3.81)
        # C (пин 3 справа снизу) -> GND (лог.0)
        dx, dy, _ = P_SW["C"][0]
        stub_label(SA_X, say, dx, dy, "GND", length=3.81)
        # ЦАП: Bk -> та же сеть
        dx, dy, _ = P_DAC[dac_b_names[k]][0]
        stub_label(DA1_X, DA1_Y, dx, dy, net)
    # Питание/опора DA1
    single(P_DAC, DA1_X, DA1_Y, "V+", "+5V")
    single(P_DAC, DA1_X, DA1_Y, "V-", "GND")
    single(P_DAC, DA1_X, DA1_Y, "VLC", "GND")
    single(P_DAC, DA1_X, DA1_Y, "R+", "+5V")
    single(P_DAC, DA1_X, DA1_Y, "R-", "GND")
    single(P_DAC, DA1_X, DA1_Y, "I+", "T1_OUT")
    dx, dy, _ = P_DAC["I-"][0]
    b.no_connect(*pin_pos(DA1_X, DA1_Y, dx, dy))
    dx, dy, _ = P_DAC["CMP"][0]
    b.no_connect(*pin_pos(DA1_X, DA1_Y, dx, dy))
    # Пробники Зад.1: PV1 (вольтметр V1) + XSC1 (осциллограф)
    place("Connector", "Conn_01x02_Pin", "PV1", "V1 (вольтметр)", 155, 118,
          fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
    place("Connector", "Conn_01x02_Pin", "XSC1", "XSC1 (осциллограф)", 155, 138,
          fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
    for ref, ox, oy in [("PV1", 155, 118), ("XSC1", 155, 138)]:
        dx, dy = pin_by_number(P_CONN, "1")
        stub_label(ox, oy, dx, dy, "T1_OUT", length=3.81)
        dx, dy = pin_by_number(P_CONN, "2")
        stub_label(ox, oy, dx, dy, "GND", length=3.81)

    # ================= ЗАДАНИЕ 2 (аналог рис.51), справа =================
    DD_X, DD_Y = 245, 150
    DA2_X, DA2_Y = 325, 150
    place("MCU_Intel", "P8051AH", "DD1", "P8051AH (МК-51)", DD_X, DD_Y,
          fp="Package_DIP:DIP-40_W15.24mm")
    place("Analog_DAC", "DAC08", "DA2", "DAC08 (ЦАП Зад.2, 8 бит)", DA2_X, DA2_Y,
          fp="Package_DIP:DIP-16_W7.62mm")
    # Порт P1 -> ЦАП (Вар.1: P1; P1.0=LSB D0 ... P1.7=MSB D7)
    for k in range(8):
        net = f"T2_D{k}"
        dx, dy, _ = P_MCU[f"P1.{k}"][0]
        stub_label(DD_X, DD_Y, dx, dy, net)
        dx, dy, _ = P_DAC[dac_b_names[k]][0]
        stub_label(DA2_X, DA2_Y, dx, dy, net)
    single(P_DAC, DA2_X, DA2_Y, "V+", "+5V")
    single(P_DAC, DA2_X, DA2_Y, "V-", "GND")
    single(P_DAC, DA2_X, DA2_Y, "VLC", "GND")
    single(P_DAC, DA2_X, DA2_Y, "R+", "+5V")
    single(P_DAC, DA2_X, DA2_Y, "R-", "GND")
    single(P_DAC, DA2_X, DA2_Y, "I+", "T2_OUT")
    dx, dy, _ = P_DAC["I-"][0]
    b.no_connect(*pin_pos(DA2_X, DA2_Y, dx, dy))
    dx, dy, _ = P_DAC["CMP"][0]
    b.no_connect(*pin_pos(DA2_X, DA2_Y, dx, dy))
    # Пробники Зад.2
    place("Connector", "Conn_01x02_Pin", "PV2", "V2 (вольтметр)", 372, 128,
          fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
    place("Connector", "Conn_01x02_Pin", "XSC2", "XSC2 (осциллограф)", 372, 148,
          fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
    for ref, ox, oy in [("PV2", 372, 128), ("XSC2", 372, 148)]:
        dx, dy = pin_by_number(P_CONN, "1")
        stub_label(ox, oy, dx, dy, "T2_OUT", length=3.81)
        dx, dy = pin_by_number(P_CONN, "2")
        stub_label(ox, oy, dx, dy, "GND", length=3.81)
    # МК: питание, EA, кварц, сброс
    single(P_MCU, DD_X, DD_Y, "VCC", "+5V")
    single(P_MCU, DD_X, DD_Y, "VSS", "GND")
    single(P_MCU, DD_X, DD_Y, "~{EA}", "+5V")
    single(P_MCU, DD_X, DD_Y, "RST", "RST")
    single(P_MCU, DD_X, DD_Y, "XTAL1", "XTAL1")
    single(P_MCU, DD_X, DD_Y, "XTAL2", "XTAL2")
    # Неиспользуемые P0/P2/P3/ALE/PSEN — no_connect
    for key in ["P0.0/AD0", "P0.1/AD1", "P0.2/AD2", "P0.3/AD3", "P0.4/AD4",
                "P0.5/AD5", "P0.6/AD6", "P0.7/AD7",
                "P2.0/A8", "P2.1/A9", "P2.2/A10", "P2.3/A11",
                "P2.4/A12", "P2.5/A13", "P2.6/A14", "P2.7/A15",
                "P3.0/RXD", "P3.1/TXD", "P3.2/~{INT0}", "P3.3/~{INT1}",
                "P3.4/T0", "P3.5/T1", "P3.6/~{WR}", "P3.7/~{RD}",
                "ALE", "~{PSEN}"]:
        dx, dy, _ = P_MCU[key][0]
        b.no_connect(*pin_pos(DD_X, DD_Y, dx, dy))
    # Кварц 12 МГц + сброс
    Y_X, Y_Y = 197, 175
    C1_X, C1_Y = 204, 188
    C2_X, C2_Y = 225, 188
    R1_X, R1_Y = 210, 120
    C3_X, C3_Y = 230, 105
    place("Device", "Crystal", "BQ1", "12 МГц", Y_X, Y_Y, fp="Crystal:Crystal_HC49-U_Vertical")
    place("Device", "C", "C1", "33 пФ", C1_X, C1_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
    place("Device", "C", "C2", "33 пФ", C2_X, C2_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
    xt_keys = list(P_XT.keys())
    xt_all = [t for lst in P_XT.values() for t in lst]
    xt1 = [t for t in xt_all if str(t[2]) == "1"][0] if any(str(t[2]) == "1" for t in xt_all) else xt_all[0]
    xt2 = [t for t in xt_all if str(t[2]) == "2"][0] if any(str(t[2]) == "2" for t in xt_all) else xt_all[1]
    stub_label(Y_X, Y_Y, xt1[0], xt1[1], "XTAL1")
    stub_label(Y_X, Y_Y, xt2[0], xt2[1], "XTAL2")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C1_X, C1_Y, dx, dy, "XTAL1")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C1_X, C1_Y, dx, dy, "GND")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C2_X, C2_Y, dx, dy, "XTAL2", length=3.0)
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C2_X, C2_Y, dx, dy, "GND")
    place("Device", "R", "R1", "10 кОм", R1_X, R1_Y, fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "C", "C3", "10 мкФ", C3_X, C3_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
    dx, dy = pin_by_number(P_R, "1")
    stub_label(R1_X, R1_Y, dx, dy, "+5V")
    dx, dy = pin_by_number(P_R, "2")
    stub_label(R1_X, R1_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C3_X, C3_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C3_X, C3_Y, dx, dy, "GND")

    # ================= питание =================
    place("power", "+5V", "#PWR01", "+5V", 40, 72)
    place("power", "GND", "#PWR02", "GND", 40, 250)
    place("power", "PWR_FLAG", "#FLG01", "PWR_FLAG", 52, 72)
    place("power", "PWR_FLAG", "#FLG02", "PWR_FLAG", 52, 250)
    b.wire([(40, 72), (52, 72)])
    b.label("+5V", 52, 72, "left")
    b.wire([(40, 250), (52, 250)])
    b.label("GND", 52, 250, "left")

    # ================= подписи (строки разнесены по Y, наложений нет) =================
    b.text("Зад.1 (рис.50): SA1-SA8 -> DA1. SA.A=+5V(1), SA.C=GND(0), SA.B->T1_D. PV1/XSC1: T1_OUT.", 30, 30, 1.5)
    b.text("Зад.2 (рис.51, Вар.1 P1): DD1.P1.0-P1.7 -> DA2.B0-B7 (T2_D). PV2/XSC2: T2_OUT. BQ1/R1/C.", 30, 36, 1.5)
    b.text("Вар.1: 8 (00001000), 36 (00100100), 107 (01101011). Uref=5V. U=D*5/255: 0.157, 0.706, 2.098 В.", 30, 42, 1.5)
    b.text("DA DAC08: B0=LSB...B7=MSB; V+/R+=+5V; V-/VLC/R-=GND; I+=OUT; I-/CMP=NC.", 30, 48, 1.5)
    b.text("Mixed A1->DA1/DA2; Basic J->SA; Indicator V1->PV; XSC1->XSC; VCC 5V; GND.", 30, 54, 1.5)
    b.text("Связи — именованными цепями (шины Multisim). Длинных проводов нет.", 30, 60, 1.5)
    b.text("XSC1/XSC2 — обозначения условные, вне ГОСТ 2.710-81 (контрольные гнезда).", 30, 66, 1.5)

    b.flush()
    print(f"OK: {SCH}")

if __name__ == "__main__":
    main()
