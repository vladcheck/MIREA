#!/usr/bin/env python3
"""GOST-финал для ПР1: правит PR1_KiCad.kicad_sch поверх эталона (пост-пасс не трогает).

Что делает (см. OTCHET.md § про ГОСТ 2.702/2.709/2.104):
  1. Бэкап PR1_KiCad.kicad_sch.bak_gost_fix (старые .bak_* не трогает).
  2. Цепи N01–N25 -> 1–25 (ГОСТ 2.709-89 п.5.9, последовательные числа) в label/text.
     Заголовок таблицы цепей -> ссылка на 2.709 п.5.9.
  3. Номиналы по ГОСТ 2.702-2011 п.5.3.20: Value "10k" -> "10 к", "100nF" -> "0,1 мк".
     ("270" уже соответствует: омы без единиц.)
  4. Перечень элементов на поле схемы (п.5.3.18, форма по ГОСТ 2.701):
     тексты + сетка gr_rect/gr_line, зона x240..412, y20..108 (свободна: контент x<=228.6).
  5. Пометки: SB в отключённом положении (п.5.3.3); цвет<->цепи (2.709 п.3.2);
     способ нумерации цепей (2.709 п.5.9).
Проверки в конце: баланс скобок, ERC ожидает 0/0 (запускается отдельно kicad-cli).
Идемпотентность: повторный запуск без эффекта (маркеры уже заменены/таблица уже есть).
"""
import re
import shutil
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCH = ROOT / "PR1_KiCad.kicad_sch"
BAK = ROOT / "PR1_KiCad.kicad_sch.bak_gost_fix"
MARK = "Перечень элементов (ГОСТ 2.701"


def u():
    return str(uuid.uuid4())


def main() -> int:
    if not SCH.exists():
        print("ERR: schematic not found", SCH)
        return 1
    s = SCH.read_text(encoding="utf-8")
    if MARK in s:
        print("SKIP: GOST-правки уже внесены (маркер найден).")
        return 0
    shutil.copy2(SCH, BAK)
    print("backup:", BAK)

    # --- 2. цепи Nxx -> xx в label/text строках ---
    lines = s.split("\n")
    n_ren = 0
    for i, ln in enumerate(lines):
        if ('(label "' in ln or '(text "' in ln) and re.search(r"\bN\d\d\b", ln):
            lines[i], n = re.subn(r"\bN(\d\d)\b", r"\1", ln)
            n_ren += n
    s = "\n".join(lines)
    print("net labels renamed:", n_ren)
    assert n_ren > 0, "no Nxx labels found"
    assert not re.search(r'\((label|text) "N\d\d\b', s), "leftover Nxx in label/text"
    s = s.replace(
        "Таблица цепей (нумерация по ГОСТ 2.710-81):",
        "Таблица цепей (участки цепей, ГОСТ 2.709-89 п.5.9):",
    )

    # --- 3. номиналы ---
    c1 = s.count('"Value" "10k"')
    s = s.replace('"Value" "10k"', '"Value" "10 к"')
    c2 = s.count('"Value" "100nF"')
    s = s.replace('"Value" "100nF"', '"Value" "0,1 мк"')
    print(f"values: 10k->{c1}, 100nF->{c2}")
    assert c1 == 3 and c2 == 4, (c1, c2)

    # --- 4-5. новые тексты и сетка перечня ---
    def text(x, y, val, size=1.27):
        v = val.replace('"', "'")
        return (
            f'\t(text "{v}"\n\t\t(at {x} {y} 0)\n\t\t(effects\n'
            f'\t\t\t(font\n\t\t\t\t(size {size} {size})\n\t\t\t)\n'
            f'\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{u()}")\n\t)\n'
        )

    def grline(x1, y1, x2, y2, w=0.15):
        # KiCad 10: линии таблицы — polyline (токенов gr_* в .kicad_sch нет)
        return (
            f'\t(polyline\n\t\t(pts\n\t\t\t(xy {x1} {y1})\n\t\t\t(xy {x2} {y2})\n'
            f'\t\t)\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type default)\n'
            f'\t\t)\n\t\t(fill\n\t\t\t(type none)\n\t\t)\n'
            f'\t\t(uuid "{u()}")\n\t)\n'
        )

    out = []
    # пометка о способе нумерации под таблицей цепей (таблица y34..134) 
    out.append(text(20, 140, "Участки цепей 1–25 — последовательные числа (ГОСТ 2.709-89 п.5.9).", 1.5))
    # легенда цвета: усилить ссылкой на стандарт
    out.append(text(20, 27, "Зелёный — условный цвет цепей МК (ГОСТ 2.709-89 п.3.2; связь с обозначениями — таблица цепей).", 1.5))
    # SB по п.5.3.3 (кнопки x96..119, y124..151; кладем в свободную правую зону)
    out.append(text(240, 150, "SB1–SB4 показаны в отключённом положении (ГОСТ 2.702-2011 п.5.3.3).", 1.5))

    # перечень: шапка + 10 строк; cols x: 240/268/363/380; rows y=34 step 7
    out.append(text(240, 20, MARK + ", п.5.3.18 ГОСТ 2.702-2011).", 1.5))
    cols = [240, 268, 363, 380]
    rows = [
        ("Поз. обозначение", "Наименование", "Кол.", "Примечание"),
        ("DD1", "Микроконтроллер STM32F100C8Tx", "1", "LQFP-48"),
        ("HG1", "Индикатор KCSC02-105", "1", "общий катод"),
        ("HL1–HL8", "Светодиод зелёный 0603", "8", "LED-GREEN"),
        ("R1–R8", "Резистор 270 Ом 0603", "8", "HL1–HL8"),
        ("R9", "Резистор 10 кОм", "1", "подтяжка NRST"),
        ("R10", "Резистор 10 кОм", "1", "стяжка BOOT0"),
        ("R11–R18", "Резистор 270 Ом 0603", "8", "сегменты HG1"),
        ("RP1", "Потенциометр 10 кОм", "1", "Bourns 3296W"),
        ("SB1–SB4", "Переключатель SPDT", "4", "генераторы уровней"),
        ("C1–C4", "Конденсатор 0,1 мкФ", "4", "C1-АЦП, C2-C3-развязка, C4-сброс"),
    ]
    y0, step = 30, 7
    for r, row in enumerate(rows):
        y = y0 + r * step
        for c, val in zip(cols, row):
            out.append(text(c, y, val))
    y1 = y0 + len(rows) * step - 2  # низ таблицы
    out.append(grline(238, y0 - 6, 412, y0 - 6, 0.3))
    out.append(grline(238, y1, 412, y1, 0.3))
    out.append(grline(238, y0 - 6, 238, y1, 0.3))
    out.append(grline(412, y0 - 6, 412, y1, 0.3))
    for cx in (266, 361, 378):
        out.append(grline(cx, y0 - 6, cx, y1))
    for r in range(1, len(rows)):
        out.append(grline(238, y0 + r * step - 3.5, 412, y0 + r * step - 3.5))

    idx = s.find("(sheet_instances")
    assert idx != -1
    s = s[:idx] + "".join(out) + s[idx:]
    assert s.count("(") == s.count(")"), "paren imbalance"
    SCH.write_text(s, encoding="utf-8")
    print("OK: texts+grid added:", len(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
