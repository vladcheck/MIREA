#!/usr/bin/env python3
"""
Генератор схемы KiCad для ПР №2 «Подключение внешней памяти к МК-51».
Аналог рис.25 методички (Multisim) в KiCad:
  U1  P8051AH (MCU_Intel) — МК-51
  U3  74LS373 (74xx) — регистр-защелка адреса (фиксация A0-A7 по спаду ALE)
  U2  HY6264AxP (Memory_RAM 8Kx8) — внешнее ОЗУ, функц. аналог HM1-65642-883 / 6116 (2K) / 6264 (8K)
  U4  27C64 (Memory_EPROM 8Kx8) — внешнее ПЗУ, аналог 27C64E350-883 (8K) / 27C128 (16K) / 27C256 (32K)
  D1+R1 — светодиод ошибки на P1.0, Y1 12МГц + обвязка, RST-цепь, пробник ALE (XSC1).
Связи выполнены именованными цепями (labels) — эквивалент шин Bus1/Bus2 из Multisim.
Формат KiCad 10.
Использование: python3 generate_schematic.py [--variant1 N] [--variant2 M]
"""
import argparse
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
SCH = ROOT / "PR2_extmem.kicad_sch"
PRO = ROOT / "PR2_extmem.kicad_pro"
SYMDIR = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols")
ROOT_UUID = "22222222-3333-4444-5555-666666666666"

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
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant1", type=int, default=1)
    ap.add_argument("--variant2", type=int, default=7)
    a = ap.parse_args()
    variants = json.loads((ROOT / "variants.json").read_text(encoding="utf-8"))
    v1 = next(v for v in variants["task1_ram"] if v["variant"] == a.variant1)
    v2 = next(v for v in variants["task2_rom"] if v["variant"] == a.variant2)

    SCH.write_text(
        f'''(kicad_sch
\t(version 20260101)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A3")
\t(title_block
\t\t(title "ПР №2. Подключение внешней памяти к МК-51 (аналог рис.25)")
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
    inject("74xx", "74LS138")

    P_MCU = parse_pins("MCU_Intel", "P8051AH")
    P_RAM = parse_pins("Memory_RAM", "HY6264AxP")
    P_ROM = parse_pins("Memory_EPROM", "27C64")
    P_LATCH = parse_pins("74xx", "74LS373")
    P_DEC = parse_pins("74xx", "74LS138")
    P_CONN = parse_pins("Connector", "Conn_01x02_Pin")
    # Device:R/C/LED/Crystal — универсально берём по number
    P_R = parse_pins("Device", "R")
    P_C = parse_pins("Device", "C")
    P_LED = parse_pins("Device", "LED")
    P_XT = parse_pins("Device", "Crystal")

    def pin_pos(ox, oy, angle, dx, dy):
        # только angle=0 используется.
        # ВНИМАНИЕ: у KiCad ордината пина в библиотеке (y-up) при
        # установке на схему инвертируется (схема y-down):
        # факт ERC = (inst_x + dx, inst_y - dy). Без минуса все стабы
        # уходили в зеркальные координаты и висели в воздухе.
        return snap(ox + dx), snap(oy - dy)

    def stub_label(ox, oy, dx, dy, net, length=5.08):
        """Короткий вывод от пина наружу + метка цепи.

        Якорь метки ставится ТОЧНО на конец провода (требование ERC,
        иначе label_dangling/unconnected_wire_endpoint). Чтобы текст не
        ложился поверх провода, justify разворачиваем от компонента:
        стаб влево (side=-1) -> текст влево (right), стаб вправо -> right.
        """
        px, py = pin_pos(ox, oy, 0, dx, dy)
        side = -1 if dx < 0 else (1 if dx > 0 else (-1 if dy < 0 else 1))
        # для DIP корпуса выводы слева/справа — отводим по X; иначе по X тоже (упрощённо)
        ex = snap(px + side * length)
        b.wire([(px, py), (ex, py)])
        b.label(net, ex, py, "left" if side > 0 else "right")
        return (ex, py)

    # ---------- размещение ----------
    MCU_X, MCU_Y = 130, 150
    LAT_X, LAT_Y = 215, 150
    RAM_X, RAM_Y = 300, 125
    ROM_X, ROM_Y = 300, 195
    DEC_X, DEC_Y = 250, 110
    XSC_X, XSC_Y = 210, 95
    place("MCU_Intel", "P8051AH", "U1", "P8051AH (МК-51)", MCU_X, MCU_Y, fp="Package_DIP:DIP-40_W15.24mm")
    place("74xx", "74LS373", "U3", "74LS373 (защелка A0-A7)", LAT_X, LAT_Y, fp="Package_DIP:DIP-20_W7.62mm")
    place("Memory_RAM", "HY6264AxP", "U2", f'HY6264 (ОЗУ {v1["N_kb"]}Кx8, Вар.{v1["variant"]})', RAM_X, RAM_Y, fp="Package_DIP:DIP-28_W15.24mm")
    place("Memory_EPROM", "27C64", "U4", f'27C64 (ПЗУ {v2["N_kb"]}Кx8, Вар.{v2["variant"]})', ROM_X, ROM_Y, fp="Package_DIP:DIP-28_W15.24mm")
    place("74xx", "74LS138", "U5", "74LS138", DEC_X, DEC_Y, fp="Package_DIP:DIP-16_W7.62mm")
    place("Connector", "Conn_01x02_Pin", "XSC1", "XSC1", XSC_X, XSC_Y, fp="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")

    def pin_by_number(pins_dict, number):
        for _name, lst in pins_dict.items():
            for (dx, dy, num) in lst:
                if str(num) == str(number):
                    return dx, dy
        raise KeyError(number)

    C_FOOT = "Capacitor_THT:C_Disc_D4.3mm_W1.9mm_P5.00mm"

    # ---------- мультиплексированная шина AD0-AD7: P0 <-> latch.D <-> RAM.I/O <-> ROM.D ----------
    p0_names = ["P0.0/AD0", "P0.1/AD1", "P0.2/AD2", "P0.3/AD3", "P0.4/AD4", "P0.5/AD5", "P0.6/AD6", "P0.7/AD7"]
    latch_d = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"]
    ram_io = ["I/O0", "I/O1", "I/O2", "I/O3", "I/O4", "I/O5", "I/O6", "I/O7"]
    rom_d = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"]
    for k in range(8):
        net = f"AD{k}"
        dx, dy, _ = P_MCU[p0_names[k]][0]
        stub_label(MCU_X, MCU_Y, dx, dy, net)
        dx, dy, _ = P_LATCH[latch_d[k]][0]
        stub_label(LAT_X, LAT_Y, dx, dy, net)
        dx, dy, _ = P_RAM[ram_io[k]][0]
        stub_label(RAM_X, RAM_Y, dx, dy, net)
        dx, dy, _ = P_ROM[rom_d[k]][0]
        stub_label(ROM_X, ROM_Y, dx, dy, net)

    # ---------- фиксированный младший адрес A0-A7: latch.Q <-> RAM.A <-> ROM.A ----------
    latch_q = ["O0", "O1", "O2", "O3", "O4", "O5", "O6", "O7"]
    for k in range(8):
        net = f"A{k}"
        dx, dy, _ = P_LATCH[latch_q[k]][0]
        stub_label(LAT_X, LAT_Y, dx, dy, net)
        # RAM A0..A7
        key = f"A{k}"
        dx, dy, _ = P_RAM[key][0]
        stub_label(RAM_X, RAM_Y, dx, dy, net)
        dx, dy, _ = P_ROM[key][0]
        stub_label(ROM_X, ROM_Y, dx, dy, net)

    # ---------- старший адрес A8-A15 с порта P2 ----------
    p2_names = ["P2.0/A8", "P2.1/A9", "P2.2/A10", "P2.3/A11", "P2.4/A12", "P2.5/A13", "P2.6/A14", "P2.7/A15"]
    for k in range(8):
        net = f"A{k+8}"
        dx, dy, _ = P_MCU[p2_names[k]][0]
        stub_label(MCU_X, MCU_Y, dx, dy, net)
        if k <= 4:  # A8-A12 есть и у ОЗУ 8К, и у ПЗУ 8К
            dx, dy, _ = P_RAM[f"A{k+8}"][0]
            stub_label(RAM_X, RAM_Y, dx, dy, net)
            dx, dy, _ = P_ROM[f"A{k+8}"][0]
            stub_label(ROM_X, ROM_Y, dx, dy, net)
    # A13-A15: у 8К-кристаллов отсутствуют — идут на дешифратор U5 (реальные стабы ниже)

    # ---------- управление ----------
    def single(lib_pins, ox, oy, key, net):
        dx, dy, _ = lib_pins[key][0]
        stub_label(ox, oy, dx, dy, net)

    single(P_MCU, MCU_X, MCU_Y, "ALE", "ALE")
    single(P_LATCH, LAT_X, LAT_Y, "LE", "ALE")          # защелка фиксирует по ALE
    single(P_LATCH, LAT_X, LAT_Y, "OE", "GND")      # OE защелки на землю (реальная цепь)
    single(P_MCU, MCU_X, MCU_Y, "P3.6/~{WR}", "/WR")
    single(P_RAM, RAM_X, RAM_Y, "~{WE}", "/WR")
    single(P_MCU, MCU_X, MCU_Y, "P3.7/~{RD}", "/RD")
    single(P_RAM, RAM_X, RAM_Y, "~{OE}", "/RD")
    single(P_MCU, MCU_X, MCU_Y, "~{PSEN}", "/PSEN")
    single(P_ROM, ROM_X, ROM_Y, "~{OE}", "/PSEN")       # ПЗУ читается стробом /PSEN
    single(P_ROM, ROM_X, ROM_Y, "~{CE}", "ROM_CS")
    single(P_RAM, RAM_X, RAM_Y, "~{CS1}", "RAM_CS")
    single(P_RAM, RAM_X, RAM_Y, "CS2", "+5V")
    single(P_ROM, ROM_X, ROM_Y, "VPP", "+5V")
    single(P_ROM, ROM_X, ROM_Y, "~{PGM}", "+5V")
    single(P_MCU, MCU_X, MCU_Y, "~{EA}", "+5V")
    single(P_MCU, MCU_X, MCU_Y, "P1.0", "LED_ERR")
    single(P_MCU, MCU_X, MCU_Y, "RST", "RST")
    single(P_MCU, MCU_X, MCU_Y, "XTAL1", "XTAL1")
    single(P_MCU, MCU_X, MCU_Y, "XTAL2", "XTAL2")
    single(P_MCU, MCU_X, MCU_Y, "VCC", "+5V")
    single(P_MCU, MCU_X, MCU_Y, "VSS", "GND")
    single(P_RAM, RAM_X, RAM_Y, "VCC", "+5V")
    single(P_RAM, RAM_X, RAM_Y, "GND", "GND")
    single(P_ROM, ROM_X, ROM_Y, "VCC", "+5V")
    single(P_ROM, ROM_X, ROM_Y, "GND", "GND")
    single(P_LATCH, LAT_X, LAT_Y, "VCC", "+5V")
    single(P_LATCH, LAT_X, LAT_Y, "GND", "GND")
    # NC у HY6264/27C64 — тип no_connect внутри корпуса: ничего не подключаем
    # (провода+метки сюда запрещены, маркеры внутри корпуса тоже убраны)
    # ---------- дешифратор U5 74LS138 ----------
    # A13->A0, A14->A1, A15->A2; E1,E2->GND; E3->+5V; O0->RAM_CS; O4->ROM_CS
    single(P_DEC, DEC_X, DEC_Y, "A0", "A13")
    single(P_DEC, DEC_X, DEC_Y, "A1", "A14")
    single(P_DEC, DEC_X, DEC_Y, "A2", "A15")
    single(P_DEC, DEC_X, DEC_Y, "E1", "GND")
    single(P_DEC, DEC_X, DEC_Y, "E2", "GND")
    single(P_DEC, DEC_X, DEC_Y, "E3", "+5V")
    single(P_DEC, DEC_X, DEC_Y, "O0", "RAM_CS")
    single(P_DEC, DEC_X, DEC_Y, "O4", "ROM_CS")
    single(P_DEC, DEC_X, DEC_Y, "VCC", "+5V")
    single(P_DEC, DEC_X, DEC_Y, "GND", "GND")
    for _key in ["O1", "O2", "O3", "O5", "O6", "O7"]:
        dx, dy, _ = P_DEC[_key][0]
        b.no_connect(*pin_pos(DEC_X, DEC_Y, 0, dx, dy))
    # ---------- осциллограф XSC1 как компонент ----------
    dx, dy = pin_by_number(P_CONN, "1")
    stub_label(XSC_X, XSC_Y, dx, dy, "ALE")
    dx, dy = pin_by_number(P_CONN, "2")
    stub_label(XSC_X, XSC_Y, dx, dy, "GND")

    # неиспользованные P1/P3 — no_connect чтобы не было висячих
    for key in ["P1.1", "P1.2", "P1.3", "P1.4", "P1.5", "P1.6", "P1.7",
                "P3.0/RXD", "P3.1/TXD", "P3.2/~{INT0}", "P3.3/~{INT1}",
                "P3.4/T0", "P3.5/T1"]:
        dx, dy, _ = P_MCU[key][0]
        px, py = pin_pos(MCU_X, MCU_Y, 0, dx, dy)
        b.no_connect(px, py)

    # ---------- LED ошибки D1+R1 на P1.0 (реальные стабы к тем же цепям) ----------
    R1_X, R1_Y = 100, 195
    D1_X, D1_Y = 100, 212
    place("Device", "R", "R1", "330", R1_X, R1_Y, fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "LED", "D1", "LED-RED:ERROR", D1_X, D1_Y, fp="LED_THT:LED_D5.0mm")
    dx, dy = pin_by_number(P_R, "1")
    stub_label(R1_X, R1_Y, dx, dy, "LED_ERR")
    dx, dy = pin_by_number(P_R, "2")
    stub_label(R1_X, R1_Y, dx, dy, "LED_A")
    stub_label(D1_X, D1_Y, *P_LED["A"][0][:2], "LED_A")
    stub_label(D1_X, D1_Y, *P_LED["K"][0][:2], "GND")
    b.text("R1 330 Ом: P1.0 -> D1 (ERROR). Горит при несовпадении write/read.", 130, 225, 1.5)

    # ---------- кварц 12 МГц + сброс (реальные стабы) ----------
    # Y1 сдвинут влево от стаба /WR (иначе XTAL2 ложится на /WR на одной высоте y=165)
    Y1_X, Y1_Y = 80, 165
    C1_X, C1_Y = 85, 175
    C2_X, C2_Y = 95, 183
    R2_X, R2_Y = 90, 130
    C3_X, C3_Y = 105, 143
    place("Device", "Crystal", "Y1", "12MHz", Y1_X, Y1_Y, fp="Crystal:Crystal_HC49-U_Vertical")
    place("Device", "C", "C1", "33pF", C1_X, C1_Y, fp=C_FOOT)
    place("Device", "C", "C2", "33pF", C2_X, C2_Y, fp=C_FOOT)
    stub_label(Y1_X, Y1_Y, *P_XT["1"][0][:2] if "1" in P_XT else (P_XT[""][0][:2]), "XTAL1")
    _xt_keys = list(P_XT.keys())
    _xt_all = [t for _lst in P_XT.values() for t in _lst]
    _xt2 = [t for t in _xt_all if str(t[2]) == "2"][0] if any(str(t[2]) == "2" for t in _xt_all) else _xt_all[1]
    stub_label(Y1_X, Y1_Y, _xt2[0], _xt2[1], "XTAL2")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C1_X, C1_Y, dx, dy, "XTAL1")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C1_X, C1_Y, dx, dy, "GND")
    dx, dy = pin_by_number(P_C, "1")
    # Укороченный стаб: иначе ярлык XTAL2 залезает на ярлык +5V от EA (та же высота)
    stub_label(C2_X, C2_Y, dx, dy, "XTAL2", length=3.0)
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C2_X, C2_Y, dx, dy, "GND")
    place("Device", "R", "R2", "10k", R2_X, R2_Y, fp="Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal")
    place("Device", "C", "C3", "10uF", C3_X, C3_Y, fp=C_FOOT)
    dx, dy = pin_by_number(P_R, "1")
    stub_label(R2_X, R2_Y, dx, dy, "+5V")
    dx, dy = pin_by_number(P_R, "2")
    stub_label(R2_X, R2_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "1")
    stub_label(C3_X, C3_Y, dx, dy, "RST")
    dx, dy = pin_by_number(P_C, "2")
    stub_label(C3_X, C3_Y, dx, dy, "GND")
    b.text("Сброс: RC 10к/10мкФ. EA=+5В (резидентное ПЗУ разрешено).", 40, 76, 1.5)

    # ---------- питание (реальные провода к флагам) ----------
    place("power", "+5V", "#PWR01", "+5V", 60, 90)
    place("power", "GND", "#PWR02", "GND", 60, 250)
    place("power", "PWR_FLAG", "#FLG01", "PWR_FLAG", 70, 90)
    place("power", "PWR_FLAG", "#FLG02", "PWR_FLAG", 70, 250)
    b.wire([(60, 90), (70, 90)])
    b.label("+5V", 70, 90, "left")
    b.wire([(60, 250), (70, 250)])
    b.label("GND", 70, 250, "left")
    b.text("+5V/GND: питание U1-U5, pull-up CS2/VPP/PGM/EA/E3 через метку +5V.", 80, 95, 1.5)

    # ---------- дешифратор / карта памяти / осциллограф ----------
    b.text(f"Карта памяти (Вар.1={v1['variant']}, Вар.2={v2['variant']}): ОЗУ {v1['N_kb']}К в 0000h..; тест 1Кбайт с {v1['ZZZ']} паттерн {v1['XX']}; ПЗУ {v2['N_kb']}К; CRC {v2['K_bytes']} байт с {v2['ZZZ']}.", 40, 40, 1.7)
    b.text("Дешифратор U5 74LS138: RAM_CS=O0 (0000h-1FFFh = !A15&!A14&!A13); ROM_CS=O4 (окно 8000h-9FFFh, полное ПЗУ — ИЛИ O4-O7). Для 2К A11-A12 к GND.", 40, 46, 1.5)
    b.text("ALE: 2 импульса за машинный цикл (1 мкс при 12 МГц). Осциллограф XSC1: 1-Ch.A -> ALE, 2-Ch.B -> GND; 1 мкс/дел, 5 В/дел.", 40, 52, 1.5)
    b.text("XSC1-ALE-PROBE (корпус XSC1 рядом с U3).", 225, 87, 1.5)
    b.text("P0: AD0-AD7 мультиплекс (адрес при ALE=1, данные при ALE=0). U3 фиксирует A0-A7 по спаду ALE. P2: A8-A15. /RD P3.7, /WR P3.6, /PSEN к ПЗУ.", 40, 58, 1.5)
    b.text("Соответствие Multisim рис.25: Bus1=AD0-AD7, Bus2=A0-A7 (Merge), U3=74LS373N (~4037BP), U2=RAM 6116/6264.", 40, 64, 1.5)

    b.flush()
    # Пост-проход: значение U4 перекрывается стабом +5V у VCC — уносим под корпус.
    # (Reference/Value ставит лоадер по дефолту; якорь Value middle, ширина ~25мм.)
    content = SCH.read_text(encoding="utf-8")
    iref = content.find('(property "Reference" "U4"')
    assert iref != -1
    ival = content.find('(property "Value"', iref)
    iat = content.find("(at ", ival)
    iend = content.find(")", iat)
    content = content[:iat] + f"(at {fmt(ROM_X)} {fmt(ROM_Y + 33)} 0" + content[iend:]
    SCH.write_text(content, encoding="utf-8")
    print(f"OK: {SCH} (Вар.1={v1['variant']}, Вар.2={v2['variant']})")


if __name__ == "__main__":
    main()
