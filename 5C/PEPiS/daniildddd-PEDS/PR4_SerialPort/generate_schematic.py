#!/usr/bin/env python3
"""
Генератор схемы KiCad для ПР №4 «Основы организации последовательного порта».
Вариант 1 (табл.12 ТЗ): T (передача), K=0 (режим 0, синхронный), S=1000 Кбит/с,
XX=50h (начало данных в резидентной памяти), N=10 байт.
Аналог рис.40 методички: U1 P8051AH (МК-51) + осциллограф-пробник XSC1 на P3.0.

Режим 0: синхронный, 8 бит данных, скорость f0 = fosc/12.
При fosc=12 МГц -> 1 МГц = 1000 Кбит/с. Таймер Т/С1 не используется.
SCON = 0x00 (SM0=0,SM1=0,SM2=0,REN=0,TB8=0,RB8=0,TI=0,RI=0).
Передача стартует записью в SBUF, конец — флаг TI.

Примечание о нумерации: в методичке перепутаны TxD/RxD
(написано TxD(P3.0), реально у 8051: P3.0=RXD данные, P3.1=TXD синхроимпульсы
в режиме 0). Следуем ТЗ: пробник на P3.0, второй канал описан текстом.

Формат KiCad 10. Стиль — как в ПР2: стаб+метка на каждый пин, PWR_FLAG,
сетка 1.27 мм, якорь метки точно на конце провода.
"""
import importlib.util
import json
import re
import uuid
from datetime import date
from pathlib import Path
import sys
sys.path.insert(0, "/Users/d.d.lyapunov/MCP/KiCAD-MCP-Server/python")

GRID = 1.27
ROOT = Path(__file__).resolve().parent
SCH = ROOT / "Circuit4.kicad_sch"
PRO = ROOT / "Circuit4.kicad_pro"
SYMDIR = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
ROOT_UUID = "44444444-5555-6666-7777-888888888888"

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
\t\t(title "ПР4. Порт МК-51, Circuit4 (вар.1)")
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
                     ("Device", "R"), ("Device", "C"), ("Device", "LED"),
                     ("Device", "Crystal"), ("Connector", "Conn_01x02_Pin")]:
        inject(lib, sym)

    P_MCU = parse_pins("MCU_Intel", "P8051AH")
    P_CONN = parse_pins("Connector", "Conn_01x02_Pin")
    P_R = parse_pins("Device", "R")
    P_C = parse_pins("Device", "C")
    P_LED = parse_pins("Device", "LED")
    P_XT = parse_pins("Device", "Crystal")

    def pin_pos(ox, oy, dx, dy):
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

    # ---------- размещение ----------
    MCU_X, MCU_Y = 150, 150
    XSC_X, XSC_Y = 230, 120
    place("MCU_Intel", "P8051AH", "U1", "P8051AH (МК-51)", MCU_X, MCU_Y,
          fp="Package_DIP:DIP-40_W15.24mm")
    place("Connector", "Conn_01x02_Pin", "XSC1", "XSC1 (осциллограф)",
          XSC_X, XSC_Y, fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
    place("Connector", "Conn_01x02_Pin", "XSC2", "XSC2 (синхро)",
          XSC_X, snap(XSC_Y + 15.24), fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")

    def single(pins, ox, oy, key, net):
        dx, dy, _ = pins[key][0]
        stub_label(ox, oy, dx, dy, net)

    # --- последовательный порт: P3.0 данные + P3.1 синхро (режим 0) ---
    single(P_MCU, MCU_X, MCU_Y, "P3.0/RXD", "P30_TXDATA")
    single(P_MCU, MCU_X, MCU_Y, "P3.1/TXD", "P31_TXCLK")
    # --- питание/земля/кварц/сброс/EA ---
    single(P_MCU, MCU_X, MCU_Y, "VCC", "+5V")
    single(P_MCU, MCU_X, MCU_Y, "VSS", "GND")
    single(P_MCU, MCU_X, MCU_Y, "XTAL1", "XTAL1")
    single(P_MCU, MCU_X, MCU_Y, "XTAL2", "XTAL2")
    single(P_MCU, MCU_X, MCU_Y, "RST", "RST")
    single(P_MCU, MCU_X, MCU_Y, "~{EA}", "+5V")
    # ALE и /PSEN в задаче последовательного порта не используются —
    # висячих меток не ставим (иначе isolated_pin_label), помечаем no_connect
    for _k in ("ALE", "~{PSEN}"):
        dx, dy, _ = P_MCU[_k][0]
        b.no_connect(*pin_pos(MCU_X, MCU_Y, dx, dy))
    single(P_MCU, MCU_X, MCU_Y, "P1.0", "TX_DONE")
    # неиспользуемые порты — no_connect
    for key in ["P1.1", "P1.2", "P1.3", "P1.4", "P1.5", "P1.6", "P1.7",
                "P3.2/~{INT0}", "P3.3/~{INT1}", "P3.4/T0", "P3.5/T1",
                "P3.6/~{WR}", "P3.7/~{RD}",
                "P0.0/AD0", "P0.1/AD1", "P0.2/AD2", "P0.3/AD3",
                "P0.4/AD4", "P0.5/AD5", "P0.6/AD6", "P0.7/AD7",
                "P2.0/A8", "P2.1/A9", "P2.2/A10", "P2.3/A11",
                "P2.4/A12", "P2.5/A13", "P2.6/A14", "P2.7/A15"]:
        dx, dy, _ = P_MCU[key][0]
        b.no_connect(*pin_pos(MCU_X, MCU_Y, dx, dy))

    # --- осциллограф XSC1: Ch.A -> P3.0, Ch.B -> GND (по ТЗ) ---
    dx, dy = pin_by_number(P_CONN, "1")
    stub_label(XSC_X, XSC_Y, dx, dy, "P30_TXDATA")
    dx, dy = pin_by_number(P_CONN, "2")
    stub_label(XSC_X, XSC_Y, dx, dy, "GND")
    # --- осциллограф XSC2: синхроимпульсы P3.1 (режим 0), второй пин -> GND ---
    XSC2_Y = snap(XSC_Y + 15.24)
    dx, dy = pin_by_number(P_CONN, "1")
    stub_label(XSC_X, XSC2_Y, dx, dy, "P31_TXCLK")
    dx, dy = pin_by_number(P_CONN, "2")
    stub_label(XSC_X, XSC2_Y, dx, dy, "GND")

    # --- LED готовности TX_DONE (P1.0) ---
    R1_X, R1_Y = 110, 195
    D1_X, D1_Y = 110, 212
    place("Device", "R", "R1", "330", R1_X, R1_Y,
          fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "LED", "D1", "LED-RED:TX_DONE", D1_X, D1_Y, fp="LED_THT:LED_D5.0mm")
    dx, dy = pin_by_number(P_R, "1")
    stub_label(R1_X, R1_Y, dx, dy, "TX_DONE")
    dx, dy = pin_by_number(P_R, "2")
    stub_label(R1_X, R1_Y, dx, dy, "LED_A")
    stub_label(D1_X, D1_Y, *P_LED["A"][0][:2], "LED_A")
    stub_label(D1_X, D1_Y, *P_LED["K"][0][:2], "GND")

    # --- кварц 12 МГц ---
    Y1_X, Y1_Y = 95, 165
    C1_X, C1_Y = 100, 175
    C2_X, C2_Y = 110, 183
    R2_X, R2_Y = 100, 130
    C3_X, C3_Y = 115, 143
    place("Device", "Crystal", "Y1", "12MHz", Y1_X, Y1_Y, fp="Crystal:Crystal_HC49-U_Vertical")
    place("Device", "C", "C1", "33pF", C1_X, C1_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
    place("Device", "C", "C2", "33pF", C2_X, C2_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
    _xt_all = [t for _lst in P_XT.values() for t in _lst]
    _xt1 = [t for t in _xt_all if str(t[2]) == "1"]
    _k1 = _xt1[0] if _xt1 else _xt_all[0]
    _xt2 = [t for t in _xt_all if str(t[2]) == "2"]
    _k2 = _xt2[0] if _xt2 else _xt_all[1]
    stub_label(Y1_X, Y1_Y, _k1[0], _k1[1], "XTAL1")
    stub_label(Y1_X, Y1_Y, _k2[0], _k2[1], "XTAL2", length=3.0)
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C1_X, C1_Y, dx, dy, "XTAL1")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C1_X, C1_Y, dx, dy, "GND")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C2_X, C2_Y, dx, dy, "XTAL2", length=3.0)
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C2_X, C2_Y, dx, dy, "GND")
    place("Device", "R", "R2", "10k", R2_X, R2_Y,
          fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "C", "C3", "10uF", C3_X, C3_Y,
          fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
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

    # --- поясняющие надписи (свободные зоны, не на проводах) ---
    b.text("ПР4 Вар.1: T / K=0 (синхронный) / 1000 Кбит/с / XX=50h / N=10 байт.", 40, 40, 1.7)
    b.text("Режим 0: f0=fosc/12; при 12 МГц -> 1 МГц. SCON=00h, TMOD/T1 не используются.", 40, 46, 1.5)
    b.text("XSC1: Ch.A -> P3.0 (данные), Ch.B -> GND (по рис.40 ТЗ). P3.1 — синхроимпульсы.", 40, 52, 1.5)
    b.text("TX_DONE (P1.0) -> R1 330 Ом -> D1 (горит по окончании передачи 10 байт).", 130, 225, 1.5)
    b.text("Сброс: RC 10к/10мкФ. EA=+5В. Y1 12 МГц + 33пФ.", 40, 76, 1.5)
    b.text("Данные для передачи: резидентная память 50h..59h (10 байт).", 40, 58, 1.5)
    b.text("XSC1-PROBE (корпус XSC1 рядом с U1).", 240, 112, 1.5)

    b.flush()
    print(f"OK: {SCH} (Вар.1 T/K0/1000/50h/10)")


if __name__ == "__main__":
    main()
