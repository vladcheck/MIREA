#!/usr/bin/env python3
"""
Генератор схемы KiCad для ЛР №8 «ШИМ на МК-52 (8052), таймер Т/С2».
Аналог рис.64 методички (Multisim Circuit 8) в KiCad:
  U1  P8052AH (MCU_Intel) — МК-52 (Intel 8052AH, MCS-51, DIP-40)
  XSC1 Conn_01x02 — эквивалент осциллографа XSC-1 из Multisim:
       1 -> P1.0 (ШИМ), 2 -> GND
  Y1 11MHz + C1/C2 — задание Fосц (вариант 1: 11 МГц)
  R2/C3 — цепь сброса RST, EA=+5V
Связи — именованными цепями (label+stub), ERC-чисто.
Формат KiCad 10. Вариант 1: T=0.07c, Q=50%, F=11МГц.
  R = 1369 (0x0559): RCAP2H=0x05, RCAP2L=0x59, tmpCnt=32084 (0x7D54).
"""
import re
import sys
import uuid
from datetime import date
from pathlib import Path

sys.path.insert(0, "/Users/d.d.lyapunov/MCP/KiCAD-MCP-Server/python")

GRID = 1.27
ROOT = Path(__file__).resolve().parent
SCH = ROOT / "Circuit8_PWM_MK52.kicad_sch"
PRO = ROOT / "Circuit8_PWM_MK52.kicad_pro"
SYMDIR = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
ROOT_UUID = "88888888-1111-4444-5555-666666666666"

import importlib.util
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
\t\t(title "ЛР8. ШИМ на МК-52, Т/С2 (вар.1)")
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
    import json
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
                     ("Device", "R"), ("Device", "C"),
                     ("Device", "Crystal"), ("Connector", "Conn_01x02_Pin")]:
        inject(lib, sym)

    P_MCU = parse_pins("MCU_Intel", "P8052AH")
    P_CONN = parse_pins("Connector", "Conn_01x02_Pin")
    P_R = parse_pins("Device", "R")
    P_C = parse_pins("Device", "C")
    P_XT = parse_pins("Device", "Crystal")

    def pin_pos(ox, oy, angle, dx, dy):
        return snap(ox + dx), snap(oy - dy)

    def stub_label(ox, oy, dx, dy, net, length=5.08):
        px, py = pin_pos(ox, oy, 0, dx, dy)
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

    MCU_X, MCU_Y = 140, 150
    XSC_X, XSC_Y = 215, 132
    place("MCU_Intel", "P8052AH", "U1", "P8052AH (МК-52)", MCU_X, MCU_Y,
          fp="Package_DIP:DIP-40_W15.24mm")
    place("Connector", "Conn_01x02_Pin", "XSC1", "XSC1 (осциллограф)",
          XSC_X, XSC_Y, fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")

    def single(lib_pins, ox, oy, key, net, length=5.08):
        dx, dy, _ = lib_pins[key][0]
        stub_label(ox, oy, dx, dy, net, length=length)

    # --- ключевые цепи ЛР №8 ---
    single(P_MCU, MCU_X, MCU_Y, "P1.0/T2", "PWM_P1_0")
    single(P_MCU, MCU_X, MCU_Y, "VCC", "+5V")
    single(P_MCU, MCU_X, MCU_Y, "VSS", "GND")
    single(P_MCU, MCU_X, MCU_Y, "~{EA}", "+5V")
    single(P_MCU, MCU_X, MCU_Y, "RST", "RST")
    single(P_MCU, MCU_X, MCU_Y, "XTAL1", "XTAL1")
    single(P_MCU, MCU_X, MCU_Y, "XTAL2", "XTAL2")
    # T2EX не используется в данной работе (режим автоперезагрузки без захвата)
    # остальные порты не задействованы
    for key in ["P1.1/T2EX", "P1.2", "P1.3", "P1.4", "P1.5", "P1.6", "P1.7",
                "P0.0/AD0", "P0.1/AD1", "P0.2/AD2", "P0.3/AD3",
                "P0.4/AD4", "P0.5/AD5", "P0.6/AD6", "P0.7/AD7",
                "P2.0/A8", "P2.1/A9", "P2.2/A10", "P2.3/A11",
                "P2.4/A12", "P2.5/A13", "P2.6/A14", "P2.7/A15",
                "P3.0/RXD", "P3.1/TXD", "P3.2/~{INT0}", "P3.3/~{INT1}",
                "P3.4/T0", "P3.5/T1", "P3.6/~{WR}", "P3.7/~{RD}",
                "ALE", "~{PSEN}"]:
        try:
            dx, dy, _ = P_MCU[key][0]
        except KeyError:
            continue
        px, py = pin_pos(MCU_X, MCU_Y, 0, dx, dy)
        b.no_connect(px, py)

    # --- осциллограф XSC1 ---
    dx, dy = pin_by_number(P_CONN, "1")
    stub_label(XSC_X, XSC_Y, dx, dy, "PWM_P1_0")
    dx, dy = pin_by_number(P_CONN, "2")
    stub_label(XSC_X, XSC_Y, dx, dy, "GND")

    # --- кварц 11 МГц (Fосц варианта 1) + нагрузка ---
    Y1_X, Y1_Y = 85, 165
    C1_X, C1_Y = 90, 178
    C2_X, C2_Y = 100, 186
    place("Device", "Crystal", "Y1", "11MHz", Y1_X, Y1_Y,
          fp="Crystal:Crystal_HC49-U_Vertical")
    C_FOOT = "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm"
    place("Device", "C", "C1", "33pF", C1_X, C1_Y, fp=C_FOOT)
    place("Device", "C", "C2", "33pF", C2_X, C2_Y, fp=C_FOOT)
    _xt_all = [t for _lst in P_XT.values() for t in _lst]
    # у Crystal обычно пины 1/2
    stub_label(Y1_X, Y1_Y, *[_t for _t in _xt_all if str(_t[2]) == "1"][0][:2], "XTAL1")
    _xt2 = [_t for _t in _xt_all if str(_t[2]) == "2"]
    _xt2 = _xt2[0] if _xt2 else _xt_all[1]
    stub_label(Y1_X, Y1_Y, _xt2[0], _xt2[1], "XTAL2")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C1_X, C1_Y, dx, dy, "XTAL1")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C1_X, C1_Y, dx, dy, "GND")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C2_X, C2_Y, dx, dy, "XTAL2", length=3.0)
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C2_X, C2_Y, dx, dy, "GND")

    # --- сброс ---
    R2_X, R2_Y = 95, 130
    C3_X, C3_Y = 110, 143
    place("Device", "R", "R1", "10k", R2_X, R2_Y,
          fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "C", "C3", "10uF", C3_X, C3_Y, fp=C_FOOT)
    dx, dy = pin_by_number(P_R, "1")
    stub_label(R2_X, R2_Y, dx, dy, "+5V")
    dx, dy = pin_by_number(P_R, "2")
    stub_label(R2_X, R2_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C3_X, C3_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C3_X, C3_Y, dx, dy, "GND")

    # --- питание ---
    place("power", "+5V", "#PWR01", "+5V", 60, 90)
    place("power", "GND", "#PWR02", "GND", 60, 250)
    place("power", "PWR_FLAG", "#FLG01", "PWR_FLAG", 70, 90)
    place("power", "PWR_FLAG", "#FLG02", "PWR_FLAG", 70, 250)
    b.wire([(60, 90), (70, 90)])
    b.label("+5V", 70, 90, "left")
    b.wire([(60, 250), (70, 250)])
    b.label("GND", 70, 250, "left")

    # --- аннотации (вне корпусов и стабов) ---
    b.text("ЛР №8, Circuit 8: ШИМ на МК-52 (P8052AH), таймер Т/С2, автоперезагрузка.", 40, 40, 1.7)
    b.text("Вариант 1: T=0.07с, Q=50%, F=11МГц; RCAP2H=0x05, RCAP2L=0x59 (R=0559h), tmpCnt=32084 (7D54h).", 40, 46, 1.5)
    b.text("ШИМ-выход: P1.0/T2 (выв.1) -> цепь PWM_P1_0 -> XSC1:1; XSC1:2 -> GND. XSC1 — эквивалент осциллографа XSC-1.", 40, 52, 1.5)
    b.text("Питание: VCC (выв.40) -> +5В, VSS (выв.20) -> GND; EA=1 (+5В, внутр. ПЗУ разрешено). T2CON=автозагрузка, TR2=1.", 40, 58, 1.5)
    b.text("Fосц: Y1 11МГц, C1/C2 33пФ. Сброс: R1 10к / C3 10мкФ (электролит, + к RST). Неиспользуемые пины — NC.", 40, 64, 1.5)
    b.text("Соответствие рис.64: U1=8052, XSC1=осциллограф, VCC=+5V, GND=общий.", 40, 70, 1.5)
    b.text("XSC1-PROBE рядом с U1 (канал A -> PWM_P1_0).", 228, 124, 1.5)
    b.text("Перечень элементов: U1 МК-52 (P8052AH, DIP-40); XSC1 — эквивалент осциллографа XSC-1 (контр. гнездо); Y1 11МГц; C1,C2 33пФ; C3 10мкФ электролит (+ к RST); R1 10к. Полный перечень — в отчёте.", 40, 76, 1.5)
    b.text("Примечание: обозначения U1/XSC1/Y1 — по рис.64 ТЗ (Multisim) для трассируемости; строгий ЕСКД-код (DD1/XS1/ZQ1) в учебной схеме не применён. Рамка/штамп ф.1 — title_block листа А3.", 40, 82, 1.5)

    b.flush()
    # Пост-проход: уносим Reference/Value из зоны корпусов (иначе inspect collisions).
    content = SCH.read_text(encoding="utf-8")
    content = content.replace('(property "Reference" "U1"\n      (at 128.016 184.912 0)', '(property "Reference" "U1"\n      (at 128.016 195 0)')
    content = content.replace('(property "Value" "P8052AH (МК-52)"\n      (at 147.828 184.912 0)', '(property "Value" "P8052AH (МК-52)"\n      (at 148 195 0)')
    content = content.replace('(property "Reference" "XSC1"\n      (at 214.63 134.62 0)', '(property "Reference" "XSC1"\n      (at 214.63 140 0)')
    content = content.replace('(property "Value" "XSC1 (осциллограф)"\n      (at 214.63 127 0)', '(property "Value" "XSC1 (осциллограф)"\n      (at 214.63 122 0)')
    SCH.write_text(content, encoding="utf-8")
    print(f"OK: {SCH}")


if __name__ == "__main__":
    main()
