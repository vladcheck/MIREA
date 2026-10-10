#!/usr/bin/env python3
"""
Генератор схемы KiCad для ПР №3 «Организация заданных интервалов времени»
Вариант 1: P1.3, S=2с (ON), K=1с (OFF), T=3мин.
Состав (аналог рис.31 методички, но 1 канал):
  DD1 P8051AH (MCU_Intel) — МК-51, кварц 12 МГц
  R1 270 Ом + HL1 LED — нагрузка на P1.3
  BQ1 12MHz + C1/C2 33пФ — тактирование
  R2 10к + C3 10мкФ — сброс
  XMM1 Conn_01x02 — мультиметр (вольтметр параллельно HL1; для тока переставляется в разрыв)
Связи — именованными метками (как Bus1 в Multisim), без длинных проводов.
Формат KiCad 10, лист A3.
"""
import importlib.util
import re
import sys
import uuid
sys.path.insert(0, "/Users/d.d.lyapunov/MCP/KiCAD-MCP-Server/python")
from datetime import date
from pathlib import Path

GRID = 1.27
ROOT = Path(__file__).resolve().parent
SCH = ROOT / "PR3_Timer.kicad_sch"
PRO = ROOT / "PR3_Timer.kicad_pro"
SYMDIR = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
ROOT_UUID = "33333333-4444-5555-6666-777777777777"

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
\t\t(title "ПР3. Таймер МК-51, HL1 на P1.3 (вар.1)")
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
        "meta": {"filename": PRO.name, "version": 1},
        "schematic": {"page_layout_descr_file": ""},
        "sheets": [], "text_variables": {},
    }, indent=2, ensure_ascii=False), encoding="utf-8")

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
    P_R = parse_pins("Device", "R")
    P_C = parse_pins("Device", "C")
    P_LED = parse_pins("Device", "LED")
    P_XT = parse_pins("Device", "Crystal")
    P_CONN = parse_pins("Connector", "Conn_01x02_Pin")

    def pin_pos(ox, oy, angle, dx, dy):
        # только angle=0
        return snap(ox + dx), snap(oy - dy)

    def pin_by_number(pins_dict, number):
        for _name, lst in pins_dict.items():
            for (dx, dy, num) in lst:
                if str(num) == str(number):
                    return dx, dy
        raise KeyError(number)

    def stub_label(ox, oy, dx, dy, net, length=5.08):
        px, py = pin_pos(ox, oy, 0, dx, dy)
        # Горизонтальные выводы (dx!=0) — стаб по X; вертикальные (dx==0) — по Y.
        # Иначе вертикальный стаб уходит горизонтально внутрь соседнего корпуса.
        if abs(dx) > 0.01:
            side = -1 if dx < 0 else 1
            ex = snap(px + side * length)
            ey = py
            b.wire([(px, py), (ex, ey)])
            b.label(net, ex, ey, "left" if side > 0 else "right")
            return (ex, ey)
        else:
            # dy>0 — пин сверху (py меньше oy), тянем вверх; dy<0 — вниз
            up = dy > 0
            ey = snap(py - length if up else py + length)
            b.wire([(px, py), (px, ey)])
            # justify для вертикального стаба не критичен, оставляем left
            b.label(net, px, ey, "left")
            return (px, ey)

    # ---------- размещение (разнесено для читаемости) ----------
    MCU_X, MCU_Y = 140, 150
    R1_X, R1_Y = 95, 165      # вертикальный
    HL1_X, HL1_Y = 95, 188    # горизонтальный
    XMM1_X, XMM1_Y = 60, 188  # мультиметр слева
    BQ1_X, BQ1_Y = 90, 130    # кварц
    C1_X, C1_Y = 80, 145
    C2_X, C2_Y = 100, 145
    R2_X, R2_Y = 105, 108
    C3_X, C3_Y = 120, 120

    place("MCU_Intel", "P8051AH", "DD1", "P8051AH (МК-51)", MCU_X, MCU_Y,
          fp="Package_DIP:DIP-40_W15.24mm")
    place("Device", "R", "R1", "270", R1_X, R1_Y,
          fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "LED", "HL1", "LED-RED 2V 10mA", HL1_X, HL1_Y,
          fp="LED_THT:LED_D5.0mm")
    place("Connector", "Conn_01x02_Pin", "XMM1", "MULTIMETER", XMM1_X, XMM1_Y,
          fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
    place("Device", "Crystal", "BQ1", "12MHz", BQ1_X, BQ1_Y,
          fp="Crystal:Crystal_HC49-U_Vertical")
    place("Device", "C", "C1", "33pF", C1_X, C1_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
    place("Device", "C", "C2", "33pF", C2_X, C2_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")
    place("Device", "R", "R2", "10k", R2_X, R2_Y, fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "C", "C3", "10uF", C3_X, C3_Y, fp="Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm")

    def single(pins, ox, oy, key, net, length=5.08):
        dx, dy, _ = pins[key][0]
        stub_label(ox, oy, dx, dy, net, length)

    # ---------- цепь светодиода P1.3 -> R1 -> HL1 -> GND ----------
    single(P_MCU, MCU_X, MCU_Y, "P1.3", "P1_3")
    dx, dy = pin_by_number(P_R, "1")
    stub_label(R1_X, R1_Y, dx, dy, "P1_3")
    dx, dy = pin_by_number(P_R, "2")
    stub_label(R1_X, R1_Y, dx, dy, "LED_A")
    # HL1: A(2) к R1, K(1) к GND
    dx, dy, _ = P_LED["A"][0]
    stub_label(HL1_X, HL1_Y, dx, dy, "LED_A")
    dx, dy, _ = P_LED["K"][0]
    stub_label(HL1_X, HL1_Y, dx, dy, "GND")

    # ---------- мультиметр XMM1 параллельно HL1 (режим V) ----------
    # Pin_1 -> LED_A, Pin_2 -> GND. Для режима A щупы переставляются в разрыв HL1.
    dx, dy = pin_by_number(P_CONN, "1")
    stub_label(XMM1_X, XMM1_Y, dx, dy, "LED_A")
    dx, dy = pin_by_number(P_CONN, "2")
    stub_label(XMM1_X, XMM1_Y, dx, dy, "GND")

    # ---------- тактирование ----------
    single(P_MCU, MCU_X, MCU_Y, "XTAL1", "XTAL1")
    single(P_MCU, MCU_X, MCU_Y, "XTAL2", "XTAL2")
    # BQ1: вывод 1 -> XTAL1, вывод 2 -> XTAL2
    _all_xt = [t for lst in P_XT.values() for t in lst]
    _xt1 = [t for t in _all_xt if str(t[2]) == "1"][0]
    _xt2 = [t for t in _all_xt if str(t[2]) == "2"][0]
    stub_label(BQ1_X, BQ1_Y, _xt1[0], _xt1[1], "XTAL1")
    stub_label(BQ1_X, BQ1_Y, _xt2[0], _xt2[1], "XTAL2")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C1_X, C1_Y, dx, dy, "XTAL1")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C1_X, C1_Y, dx, dy, "GND")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C2_X, C2_Y, dx, dy, "XTAL2", length=3.0)
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C2_X, C2_Y, dx, dy, "GND")

    # ---------- сброс + питание ----------
    single(P_MCU, MCU_X, MCU_Y, "RST", "RST")
    dx, dy = pin_by_number(P_R, "1")
    stub_label(R2_X, R2_Y, dx, dy, "+5V")
    dx, dy = pin_by_number(P_R, "2")
    stub_label(R2_X, R2_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C3_X, C3_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C3_X, C3_Y, dx, dy, "GND")

    single(P_MCU, MCU_X, MCU_Y, "VCC", "+5V")
    single(P_MCU, MCU_X, MCU_Y, "VSS", "GND")
    single(P_MCU, MCU_X, MCU_Y, "~{EA}", "+5V")

    # неиспользуемые порты — no_connect (чтобы ERC не ругался на висячие)
    for key in ["P0.0/AD0", "P0.1/AD1", "P0.2/AD2", "P0.3/AD3", "P0.4/AD4",
                "P0.5/AD5", "P0.6/AD6", "P0.7/AD7",
                "P1.0", "P1.1", "P1.2", "P1.4", "P1.5", "P1.6", "P1.7",
                "P2.0/A8", "P2.1/A9", "P2.2/A10", "P2.3/A11", "P2.4/A12",
                "P2.5/A13", "P2.6/A14", "P2.7/A15",
                "P3.0/RXD", "P3.1/TXD", "P3.2/~{INT0}", "P3.3/~{INT1}",
                "P3.4/T0", "P3.5/T1", "P3.6/~{WR}", "P3.7/~{RD}",
                "ALE", "~{PSEN}"]:
        dx, dy, _ = P_MCU[key][0]
        b.no_connect(*pin_pos(MCU_X, MCU_Y, 0, dx, dy))

    # ---------- питание ----------
    place("power", "+5V", "#PWR01", "+5V", 60, 90)
    place("power", "GND", "#PWR02", "GND", 60, 250)
    place("power", "PWR_FLAG", "#FLG01", "PWR_FLAG", 70, 90)
    place("power", "PWR_FLAG", "#FLG02", "PWR_FLAG", 70, 250)
    b.wire([(60, 90), (70, 90)])
    b.label("+5V", 70, 90, "left")
    b.wire([(60, 250), (70, 250)])
    b.label("GND", 70, 250, "left")

    # ---------- текстовые примечания (свободные зоны, не на проводах) ----------
    b.text("Вар.1: P1.3, S=2с ON / K=1с OFF, T=3мин (60 циклов по 3с). Fosc=12МГц, Tмаш=1мкс.", 40, 40, 1.7)
    b.text("Таймер T/C0, режим 1 (16 бит), база 50мс: TH0=3Ch, TL0=0B0h (65536-50000). S:40x50мс, K:20x50мс.", 40, 46, 1.5)
    b.text("HL1: P1.3=1 -> R1 270 Ом -> HL1 (Vf~2В, If~11мА) -> GND. P1.3=0 -> HL1 погашен.", 40, 52, 1.5)
    b.text("XMM1: V — параллельно HL1 (1-LED_A, 2-GND, Rin=1ГОм). A — в разрыв цепи HL1 (Rin=1нОм).", 40, 58, 1.5)
    b.text("BQ1 12МГц + C1/C2 33пФ; сброс R2 10к/C3 10мкФ; EA=+5В (внутр. ПЗУ). Свободные порты — NC.", 40, 64, 1.5)
    b.text("Обозначения по ГОСТ 2.710-81: DD1, HL1, R1/R2, C1-C3, BQ1, XMM1.", 40, 70, 1.5)
    b.text("XMM1-MULTIMETER: 1(+) LED_A, 2(-) GND.", 40, 180, 1.5)

    b.flush()
    # Пост-пасс: поле Reference C3 ложилось на провод RST (y=121.92, wire_hits=1) — уносим влево от корпуса.
    content = SCH.read_text(encoding="utf-8")
    iref = content.find('(property "Reference" "C3"')
    assert iref != -1
    iat = content.find("(at ", iref)
    iend = content.find(")", iat)
    content = content[:iat] + "(at 109 119.5 0" + content[iend:]
    SCH.write_text(content, encoding="utf-8")
    print(f"OK: {SCH}")


if __name__ == "__main__":
    main()
