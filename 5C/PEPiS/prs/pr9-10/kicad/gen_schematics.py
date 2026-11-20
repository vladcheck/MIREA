#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор схемы пр9-10 (KiCad 10): STM32F103C8 + ATmega32 с
семисегментными индикаторами HDSP-7503 (общий катод), вариант 4.

Составляет pr9-10.kicad_sch из символов системных библиотек KiCad
(определения встраиваются в lib_symbols, файл самодостаточен).
Все координаты — на сетке 1,27 мм (проверяется assert'ами).

Запуск: python3 kicad/gen_schematics.py
"""

import re
import uuid

SYM_DIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
GRID = 1.27
OUT = "pr9-10.kicad_sch"
ROOT_UUID = "9d5f2a10-7c1e-4b9a-9e3d-2f8a6b4c1d2e"


def uid():
    return str(uuid.uuid4())


def grid_ok(*vals):
    for v in vals:
        assert abs(v / GRID - round(v / GRID)) < 1e-6, f"вне сетки 1,27: {v}"


def r2(v):
    """Округление координат до сотых (убирает шум float у границ сетки)."""
    return round(v + 0.0, 2)


def rot_pt(x, y, rot):
    """Поворот локальной точки вывода на rot градусов против часовой."""
    if rot == 0:
        return x, y
    if rot == 90:
        return -y, x
    if rot == 180:
        return -x, -y
    if rot == 270:
        return y, -x
    raise ValueError(rot)


# ---------------------------------------------------------------------------
# Чтение символов из библиотек (с развёртыванием extends)
# ---------------------------------------------------------------------------
class Symbol:
    def __init__(self, lib, name):
        self.lib = lib
        self.name = name
        txt = open(SYM_DIR + lib + ".kicad_sym", encoding="utf-8").read()

        def block(nm):
            i = txt.index(f'(symbol "{nm}"')
            depth, j = 0, i
            while True:
                if txt[j] == "(":
                    depth += 1
                elif txt[j] == ")":
                    depth -= 1
                if depth == 0:
                    break
                j += 1
            return txt[i : j + 1]

        derived = block(name)
        m = re.search(r'\(extends "([^"]+)"\)', derived)
        base_name, base = (m.group(1), block(m.group(1))) if m else (name, derived)

        # свойства производного символа (без extends, без sub-символов,
        # без обёртки и финального embedded_fonts)
        dprops = re.sub(r'\(extends "[^"]+"\)\n', "", derived)
        dprops = dprops[dprops.index("\n") + 1 :].rstrip()
        m_cut = re.search(r"^\t+\(symbol ", dprops, re.M)
        if m_cut:
            dprops = dprops[: m_cut.start()].rstrip()
        dprops = re.sub(r"\t+\(embedded_fonts no\)\s*\n?\t*\)?\s*$", "", dprops)
        lines = [l for l in dprops.splitlines() if l.strip()]
        indents = [len(l) - len(l.lstrip("\t")) for l in lines]
        base_ind = min(indents)
        dprops = "\n".join(
            "\t\t" + l[base_ind:] if l.strip() else l for l in lines
        )

        # sub-символы базы, переименованные под производное имя
        subs = []
        for sm in re.finditer(r'\(symbol "%s(_\d+_\d+)"' % re.escape(base_name), base):
            i, depth, j = sm.start(), 0, sm.start()
            while True:
                if base[j] == "(":
                    depth += 1
                elif base[j] == ")":
                    depth -= 1
                if depth == 0:
                    break
                j += 1
            subs.append(
                '(symbol "%s%s"' % (name, sm.group(1)) + base[sm.end() : j + 1]
            )

        self.embedded = (
            '\t\t(symbol "%s:%s"\n%s\n%s\n\t\t\t(embedded_fonts no)\n\t\t)'
            % (lib, name, dprops, "\n".join(subs))
        )

        # выводы unit 1 из базы; ключ — номер вывода
        u1 = None
        for sm in re.finditer(r'\(symbol "%s_1_1"' % re.escape(base_name), base):
            depth, j = 0, sm.start()
            while True:
                if base[j] == "(":
                    depth += 1
                elif base[j] == ")":
                    depth -= 1
                if depth == 0:
                    break
                j += 1
            u1 = base[sm.start() : j + 1]
            break
        src = u1 if u1 else base
        self.pins = {}  # num -> (name, x, y, rot)
        for pm in re.finditer(
            r'\(pin (\S+) (\S+)\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)(.*?)(?=\(pin |\Z)',
            src,
            re.S,
        ):
            pbody = pm.group(6)
            nm = re.search(r'\(name "([^"]*)"', pbody)
            num = re.search(r'\(number "([^"]+)"', pbody)
            if num:
                self.pins[num.group(1)] = (
                    nm.group(1) if nm else "",
                    float(pm.group(3)),
                    float(pm.group(4)),
                    int(pm.group(5)),
                )

    def by_name(self, name):
        """Все выводы с данным именем: [(num, x, y, rot), ...]."""
        return [v for v in self.pins.values() if v[0] == name]


# ---------------------------------------------------------------------------
# Лист
# ---------------------------------------------------------------------------
class Sheet:
    def __init__(self):
        self.libs = {}
        self.items = []
        self._wires = set()

    def use(self, sym):
        self.libs.setdefault(f"{sym.lib}:{sym.name}", sym.embedded)

    def wire(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = r2(x1), r2(y1), r2(x2), r2(y2)
        grid_ok(x1, y1, x2, y2)
        key = tuple(sorted(((x1, y1), (x2, y2))))
        if key in self._wires:
            return  # наложенные выводы (VSS×3): один сегмент вместо стека
        self._wires.add(key)
        self.items.append(
            f'\t(wire\n\t\t(pts\n\t\t\t(xy {x1} {y1}) (xy {x2} {y2})\n\t\t)\n'
            f'\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n'
            f'\t\t(uuid "{uid()}")\n\t)'
        )

    def junction(self, x, y):
        x, y = r2(x), r2(y)
        grid_ok(x, y)
        self.items.append(
            f'\t(junction\n\t\t(at {x} {y})\n\t\t(diameter 0)\n'
            f'\t\t(color 0 0 0 0)\n\t\t(uuid "{uid()}")\n\t)'
        )

    def no_connect(self, x, y):
        x, y = r2(x), r2(y)
        grid_ok(x, y)
        self.items.append(
            f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uid()}")\n\t)'
        )

    def text(self, x, y, s, size=2.54):
        grid_ok(x, y)
        self.items.append(
            f'\t(text "{s}"\n\t\t(at {x} {y} 0)\n\t\t(effects\n'
            f'\t\t\t(font\n\t\t\t\t(size {size} {size})\n\t\t\t)\n'
            f'\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uid()}")\n\t)'
        )

    def symbol(self, sym, x, y, ref, value, pwr=False, rot=0,
               ref_at=None, val_at=None):
        """Экземпляр символа. Возвращает {номер вывода: (abs x, abs y)}.

        ref_at/val_at — (px, py, угол, выравнивание left|right) для
        свойств Reference/Value; по умолчанию — в точке (x, y).
        У силовых символов (pwr) Reference скрыт: иначе «#PWR0x»
        печатается поверх графики символа.
        """
        x, y = r2(x), r2(y)
        grid_ok(x, y)
        self.use(sym)
        # значения свойств с учётом экранированных кавычек \" внутри
        props_def = dict(
            re.findall(
                r'\(property "([^"]+)" "((?:[^"\\]|\\.)*)"',
                sym.embedded,
            )
        )
        pins = {}
        pin_block = []
        for pnum, (pname, px, py, _rot) in sym.pins.items():
            pin_block.append(f'\t\t(pin "{pnum}"\n\t\t\t(uuid "{uid()}")\n\t\t)')
            # локальные координаты библиотеки: +y вверх; на листе +y вниз,
            # поэтому y инвертируется (как в pr7-8: совпадение выводов R1/PA1)
            rx, ry = rot_pt(px, py, rot)
            ax, ay = r2(x + rx), r2(y - ry)
            grid_ok(ax, ay)
            pins[pnum] = (ax, ay)
        extra = "" if pwr else "\t\t(in_pos_files yes)\n"
        rp = ref_at or (x, y, 0, "left")
        vp = val_at or (x, y, 0, "left")
        grid_ok(rp[0], rp[1], vp[0], vp[1])
        hide_ref = "\t\t\t(hide yes)\n" if pwr else ""

        def prop_block(name, val, pos, hide=""):
            return (
                f'\t\t(property "{name}" "{val}"\n'
                f'\t\t\t(at {pos[0]} {pos[1]} {pos[2]})\n'
                f'{hide}'
                f'\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n'
                f'\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n'
                f'\t\t\t\t)\n'
                f'\t\t\t\t(justify {pos[3]} bottom)\n'
                f'\t\t\t)\n\t\t)\n'
            )

        self.items.append(
            f'\t(symbol\n'
            f'\t\t(lib_id "{sym.lib}:{sym.name}")\n'
            f'\t\t(at {x} {y} {rot})\n'
            f'\t\t(unit 1)\n'
            f'\t\t(body_style 1)\n'
            f'\t\t(exclude_from_sim no)\n'
            f'\t\t(in_bom yes)\n'
            f'\t\t(on_board yes)\n'
            f'{extra}'
            f'\t\t(dnp no)\n'
            f'\t\t(uuid "{uid()}")\n'
            + prop_block("Reference", ref, rp, hide_ref)
            + prop_block("Value", value, vp)
            + "".join(
                prop_block(k, v, (x, y, 0, "left"), "\t\t\t(hide yes)\n")
                for k, v in props_def.items()
                if k not in ("Reference", "Value")
            )
            + "\n".join(pin_block)
            + f'\n\t\t(instances\n\t\t\t(project "pr9-10"\n'
              f'\t\t\t\t(path "/{ROOT_UUID}"\n'
              f'\t\t\t\t\t(reference "{ref}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n'
              f'\t\t\t)\n\t\t)\n\t)'
        )
        return pins

    def save(self, path, title):
        doc = (
            "(kicad_sch\n"
            "\t(version 20260306)\n"
            '\t(generator "eeschema")\n'
            '\t(generator_version "10.0")\n'
            f'\t(uuid "{ROOT_UUID}")\n'
            '\t(paper "A3")\n'
            "\t(title_block\n"
            f'\t\t(title "{title}")\n'
            "\t)\n"
            "\t(lib_symbols\n"
            + "\n".join(self.libs.values())
            + "\n\t)\n"
            + "\n".join(self.items)
            + '\n\t(embedded_fonts no)\n)\n'
        )
        open(path, "w", encoding="utf-8").write(doc)
        print(f"wrote {path}: {len(self.items)} элементов, {len(self.libs)} символов")


# ---------------------------------------------------------------------------
# Символы
# ---------------------------------------------------------------------------
STM32 = Symbol("MCU_ST_STM32F1", "STM32F103C8Tx")
AVR = Symbol("MCU_Microchip_ATmega", "ATmega32-16P")
DISP = Symbol("Display_Character", "HDSP-7503")
R = Symbol("Device", "R")
GND = Symbol("power", "GND")
PWR_FLAG = Symbol("power", "PWR_FLAG")
V33 = Symbol("power", "+3.3V")
V5 = Symbol("power", "+5V")

NUM = {"pwr": 0, "r": 0, "u": 0}


def ref_next(kind):
    NUM[kind] += 1
    return {"pwr": "#PWR", "r": "R", "u": "U"}[kind] + str(NUM[kind])


def pin_by_name(placed, sym, name, which=0):
    """Абсолютные координаты which-го вывода с именем name."""
    nums = [n for n, v in sym.pins.items() if v[0] == name]
    nums.sort(key=int)
    return placed[nums[which]]


SEG_FROM_PA = ["A", "B", "C", "D", "E", "F", "G", "DP"]

sh = Sheet()

# Лист A3 (420x297): оба стенда размещены в середине листа,
# свободные поля — по краям (см. канонический pr7-8).
HDR_Y = 60.96          # строка-заголовок над каждым стендом
UY = 160.02            # центр МК STM32 (вертикальная центровка листа)
AY = 160.02            # центр МК ATmega

# ===========================================================================
# Блок 1: STM32F103C8, индикатор общего катода, резисторы 330 Ом (3,3 В)
# ===========================================================================
sh.text(48.26, HDR_Y, "STM32F103C8T6, питание 3,3 В, индикатор с общим катодом")
UX = 78.74
p = sh.symbol(STM32, UX, UY, ref_next("u"), "STM32F103C8Tx",
              ref_at=(UX - 17.78, UY + 50.8, 0, "left"),
              val_at=(UX + 17.78, UY + 50.8, 0, "right"))

# --- индикатор HDSP-7503: вывод A совмещён по вертикали с PA0 ----------
pa0 = pin_by_name(p, STM32, "PA0")
DX, DY = 140.97, pa0[1] + 7.62
dp = sh.symbol(DISP, DX, DY, ref_next("u"), "HDSP-7503",
               ref_at=(DX - 5.08, DY - 15.24, 0, "left"),
               val_at=(DX + 10.16, DY - 15.24, 0, "right"))

for i, seg in enumerate(SEG_FROM_PA):
    pa = pin_by_name(p, STM32, f"PA{i}")
    dsp = pin_by_name(dp, DISP, seg)
    grid_ok(pa[1], dsp[1])
    assert abs(pa[1] - dsp[1]) < 1e-9, f"PA{i} (y={pa[1]}) не совпадает с {seg} (y={dsp[1]})"
    y = pa[1]
    # резистор вертикально повёрнут (выводы 1/2 слева/справа); позиция и
    # номинал — снаружи корпуса, чтобы не наезжали на соседние резисторы
    # угол 90: надпись поворачивается вместе с символом, поэтому в файле
    # указывается 90, чтобы на листе текст был горизонтальным; позиции —
    # по бокам от колонки корпусов (между ними на шаге 2,54 не помещаются)
    sh.symbol(R, 107.95, y, ref_next("r"), "330", rot=90,
              ref_at=(104.14, y - 2.54, 90, "left"),
              val_at=(111.76, y - 2.54, 90, "right"))
    sh.wire(pa[0], y, 104.14, y)      # PA -> резистор (pin 1)
    sh.wire(111.76, y, dsp[0], y)     # резистор (pin 2) -> сегмент

# оба вывода общего катода на общий GND
cc_a = pin_by_name(dp, DISP, "CC", 0)
cc_b = pin_by_name(dp, DISP, "CC", 1)
rail = DX + 11.43
mid_y = (cc_a[1] + cc_b[1]) / 2
sh.wire(cc_a[0], cc_a[1], rail, cc_a[1])
sh.wire(cc_b[0], cc_b[1], rail, cc_b[1])
sh.wire(rail, cc_a[1], rail, cc_b[1])
sh.junction(rail, mid_y)
sh.symbol(GND, rail, mid_y, ref_next("pwr"), "GND", pwr=True)

# --- питание: VBAT/VDD×3/VDDA -> шина +3,3 В; VSS×3/VSSA -> шина GND ---
def power_rail(pts, sym, value, center_y, pwr_flag=None):
    """Горизонтальная шина от группы одноимённых выводов питания.

    Шина — со стороны, свободной от корпуса МК; отвод PWR_FLAG —
    за правым краем шины, подальше от символа питания (иначе их
    надписи наезжают друг на друга).
    """
    xs = sorted(x for x, _y in pts)
    ys = [y for _x, y in pts]
    below = min(ys) > center_y  # выводы ниже центра МК -> шина под ними
    rail_y = (max(ys) + 1.27) if below else (min(ys) - 1.27)
    for x, y in pts:
        sh.wire(x, y, x, rail_y)
        sh.junction(x, rail_y)
    fx = r2(xs[-1] + 7.62)  # отвод PWR_FLAG за правым выводом
    sh.wire(xs[0], rail_y, fx, rail_y)
    # точка отвода: на сетке, но не совпадающая с отводом вывода (иначе
    # получится четырёхстороннее соединение)
    mid_x = r2((xs[0] + xs[-1]) / 2)
    while mid_x in xs:
        mid_x = r2(mid_x + 1.27)
    if mid_x > xs[-1] or mid_x < xs[0]:
        mid_x = r2((xs[0] + xs[-1]) / 2)
        while mid_x in xs:
            mid_x = r2(mid_x - 1.27)
    dy = 3.81 if below else -3.81
    sh.junction(mid_x, rail_y)
    sh.wire(mid_x, rail_y, mid_x, rail_y + dy)
    sh.symbol(sym, mid_x, rail_y + dy, ref_next("pwr"), value, pwr=True)
    if pwr_flag is not None:
        sh.wire(fx, rail_y, fx, rail_y + dy)
        sh.symbol(pwr_flag, fx, rail_y + dy, ref_next("pwr"), "PWR_FLAG",
                  pwr=True)

top = []
for nm in ("VBAT", "VDD", "VDDA"):
    top += [pin_by_name(p, STM32, nm, w) for w in range(len(STM32.by_name(nm)))]
power_rail(top, V33, "+3.3V", UY, pwr_flag=PWR_FLAG)

bot = []
for nm in ("VSS", "VSSA"):
    bot += [pin_by_name(p, STM32, nm, w) for w in range(len(STM32.by_name(nm)))]
power_rail(bot, GND, "GND", UY, pwr_flag=PWR_FLAG)

# --- NRST: подтяжка 10к к +3,3 В; BOOT0 -> GND ---------------------------
# Цепочки разнесены по горизонтали (53,34 и 58,42), чтобы надписи
# резисторов и символов питания не наезжали друг на друга.
nrst = pin_by_name(p, STM32, "NRST")
sh.wire(nrst[0], nrst[1], 53.34, nrst[1])
sh.wire(53.34, nrst[1], 53.34, nrst[1] - 1.27)
sh.symbol(R, 53.34, nrst[1] - 5.08, ref_next("r"), "10k",
          ref_at=(53.34 - 2.54, nrst[1] - 5.08, 0, "right"),
          val_at=(53.34 + 2.54, nrst[1] - 5.08, 0, "left"))
sh.wire(53.34, nrst[1] - 8.89, 53.34, nrst[1] - 12.7)
sh.symbol(V33, 53.34, nrst[1] - 12.7, ref_next("pwr"), "+3.3V", pwr=True)

boot0 = pin_by_name(p, STM32, "BOOT0")
sh.wire(boot0[0], boot0[1], 58.42, boot0[1])
sh.wire(58.42, boot0[1], 58.42, boot0[1] + 3.81)
sh.symbol(GND, 58.42, boot0[1] + 3.81, ref_next("pwr"), "GND", pwr=True)

# --- неиспользуемые выводы ----------------------------------------------
used = {"PA%d" % i for i in range(8)} | {"VBAT", "VDD", "VDDA", "VSS", "VSSA", "NRST", "BOOT0"}
for num, (nm, rx, ry, _rt) in STM32.pins.items():
    if nm not in used:
        sh.no_connect(UX + rx, UY - ry)

# ===========================================================================
# Блок 2: ATmega32, индикатор общего катода, резисторы 470 Ом (5 В)
# ===========================================================================
sh.text(200.66, HDR_Y, "ATmega32, питание 5 В (VCC и AVCC), индикатор с общим катодом")
AX = 229.87
a = sh.symbol(AVR, AX, AY, ref_next("u"), "ATmega32-16P",
              ref_at=(AX - 15.24, AY + 59.69, 0, "left"),
              val_at=(AX + 15.24, AY + 59.69, 0, "right"))

pa0 = pin_by_name(a, AVR, "PA0")
DX2, DY2 = 285.75, pa0[1] + 7.62
dp2 = sh.symbol(DISP, DX2, DY2, ref_next("u"), "HDSP-7503",
                ref_at=(DX2 - 5.08, DY2 - 15.24, 0, "left"),
                val_at=(DX2 + 10.16, DY2 - 15.24, 0, "right"))

for i, seg in enumerate(SEG_FROM_PA):
    pa = pin_by_name(a, AVR, f"PA{i}")
    dsp = pin_by_name(dp2, DISP, seg)
    grid_ok(pa[1], dsp[1])
    assert abs(pa[1] - dsp[1]) < 1e-9, f"ATmega PA{i} не совпадает с {seg}"
    y = pa[1]
    sh.symbol(R, 256.54, y, ref_next("r"), "470", rot=90,
              ref_at=(252.73, y - 2.54, 90, "left"),
              val_at=(260.35, y - 2.54, 90, "right"))
    sh.wire(pa[0], y, 252.73, y)
    sh.wire(260.35, y, dsp[0], y)

cc_a = pin_by_name(dp2, DISP, "CC", 0)
cc_b = pin_by_name(dp2, DISP, "CC", 1)
rail2 = DX2 + 11.43
mid_y2 = (cc_a[1] + cc_b[1]) / 2
sh.wire(cc_a[0], cc_a[1], rail2, cc_a[1])
sh.wire(cc_b[0], cc_b[1], rail2, cc_b[1])
sh.wire(rail2, cc_a[1], rail2, cc_b[1])
sh.junction(rail2, mid_y2)
sh.symbol(GND, rail2, mid_y2, ref_next("pwr"), "GND", pwr=True)

# --- питание: VCC и AVCC -> шина +5 В; оба GND (одна точка) -------------
vcc = pin_by_name(a, AVR, "VCC")
avcc = pin_by_name(a, AVR, "AVCC")
power_rail([vcc, avcc], V5, "+5V", AY, pwr_flag=PWR_FLAG)

g = pin_by_name(a, AVR, "GND")  # оба вывода GND совпадают по координатам
sh.wire(g[0], g[1], g[0], g[1] + 3.81)
sh.symbol(GND, g[0], g[1] + 3.81, ref_next("pwr"), "GND", pwr=True)

# --- RESET: подтяжка 10к к +5 В (цепочка уходит вверх, как у NRST) ------
rst = pin_by_name(a, AVR, "~{RESET}")
sh.wire(rst[0], rst[1], 207.01, rst[1])
sh.wire(207.01, rst[1], 207.01, rst[1] - 1.27)
sh.symbol(R, 207.01, rst[1] - 5.08, ref_next("r"), "10k",
          ref_at=(207.01 - 2.54, rst[1] - 5.08, 0, "right"),
          val_at=(207.01 + 2.54, rst[1] - 5.08, 0, "left"))
sh.wire(207.01, rst[1] - 8.89, 207.01, rst[1] - 12.7)
sh.symbol(V5, 207.01, rst[1] - 12.7, ref_next("pwr"), "+5V", pwr=True)

# --- неиспользуемые выводы (тактирование — свойство модели 8 МГц) -------
used_avr = {f"PA{i}" for i in range(8)} | {"VCC", "AVCC", "GND", "~{RESET}"}
for num, (nm, rx, ry, _rt) in AVR.pins.items():
    if nm not in used_avr:
        sh.no_connect(AX + rx, AY - ry)

# «№» в шрифтах KiCad превращается в тофу — только «#»
sh.save(OUT, "Практическая работа # 5. Семисегментный индикатор, вариант 4 (пр9-10)")
