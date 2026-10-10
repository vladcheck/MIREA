#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор Word-отчёта ЛР №6 по разд.4 ТЗ. Стиль, под ГОСТ 7.32: A4, Times 14, интервал 1.5."""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "LR6_Otchet.docx"
IMG = ROOT / "out" / "schematic.png"
IMG_T1 = ROOT / "out" / "schematic_task1.png"
IMG_T2 = ROOT / "out" / "schematic_task2.png"
PROG = ROOT / "prog" / "lr6_dac_var1.c"

d = Document()
# --- базовый стиль ---
st = d.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(14)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = st.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
pf.space_after = Pt(6)
for s in d.sections:
    s.page_width = Mm(210); s.page_height = Mm(297)
    s.left_margin = Mm(30); s.right_margin = Mm(15)
    s.top_margin = Mm(20); s.bottom_margin = Mm(20)

def p(text, bold=False, center=False, size=14):
    par = d.add_paragraph()
    if center: par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = par.add_run(text); r.bold = bold; r.font.size = Pt(size)
    r.font.name = "Times New Roman"
    return par

def h(text):
    par = d.add_paragraph(style="Heading 1"); r = par.add_run(text)
    r.bold = True; r.font.size = Pt(16); r.font.name = "Times New Roman"
    par.paragraph_format.page_break_before = True
    return par

def body(text):
    par = d.add_paragraph(); r = par.add_run(text)
    r.font.size = Pt(14); r.font.name = "Times New Roman"
    par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    par.paragraph_format.first_line_indent = Mm(12.5)
    par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return par

def code_block(path):
    txt = Path(path).read_text(encoding="utf-8")
    for line in txt.splitlines():
        par = d.add_paragraph()
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.line_spacing = 1.0
        r = par.add_run(line if line else " ")
        r.font.name = "Courier New"; r.font.size = Pt(11)

# ===== титульник (единый для всех работ: отличается только тема/вариант) =====
_logo = d.add_paragraph(); _logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
_logo.add_run().add_picture(str(ROOT / "logo.jpg"), width=Mm(40))
p("МИНОБРНАУКИ РОССИИ", center=True, size=12)
p("Федеральное государственное бюджетное образовательное учреждение высшего образования", center=True, size=12)
p("«МИРЭА – Российский технологический университет»", bold=True, center=True)
p("РТУ МИРЭА", bold=True, center=True)
p("Институт перспективных технологий и индустриального программирования", center=True, size=12)
p("Кафедра индустриального программирования", center=True, size=12)
p("", center=True)
p("ОТЧЁТ ПО ЛАБОРАТОРНОЙ РАБОТЕ № 6", bold=True, center=True)
p("по дисциплине «Программирование электронных приборов и систем»", center=True, size=12)
p("НАПРАВЛЕНИЕ ПОДГОТОВКИ", bold=True, center=True, size=12)
p("09.03.02 «Информационные системы и технологии»", center=True, size=12)
p("", center=True)
p("Тема: «Изучение принципов работы цифроаналоговых преобразователей»", bold=True, center=True)
p("Вариант 1: коды 8, 36, 107; порт P1", center=True)
p("", center=True)
for _txt in ["Выполнил: студент группы ЭФБО-04-24 Ляпунов Д.Д.", "Принял: Клёсов Д.Н."]:
    _par = d.add_paragraph()
    _par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _r = _par.add_run(_txt)
    _r.font.size = Pt(14); _r.font.name = "Times New Roman"
p("", center=True)
p("Москва 2026", center=True, size=12)
d.add_page_break()
_brk = d.paragraphs[-1]
for _p in list(d.paragraphs):  # титул целиком на -7.5мм: поля 30/15 иначе уводят центр вправо
    _p.paragraph_format.left_indent = Mm(-7.5)
    _p.paragraph_format.right_indent = Mm(7.5)
    if _p is _brk:
        break

# ===== 1 =====
h("1. Наименование и цель работы")
body("Наименование: «Изучение принципов работы цифроаналоговых преобразователей» (лабораторная работа № 6).")
body("Цель: познакомиться с тем, как работает интегральный цифроаналоговый преобразователь: как входной 8-битный код превращается в напряжение на выходе, чем отличаются матрицы R-2R и двоично-взвешенные, какие параметры у ЦАП главные.")
body("Вариант 1 из таблицы 15 методички: входные коды 8, 36, 107; ЦАП подключается к порту P1 микроконтроллера МК-51. Опорное напряжение принято +5 В (питание стенда VCC 5V).")

# ===== 2 =====
h("2. Копия схемного файла")
body("Схема собрана в KiCad (файл LR6_DAC.kicad_sch, лист A3, ERC, 0 ошибок, 0 предупреждений). Это аналог двух рисунков из методички на одном листе: слева, задание 1 (переключатели и ЦАП), справа, задание 2 (микроконтроллер и ЦАП). Связи сделаны именованными цепями, как шины в Multisim, поэтому длинных проводов через весь лист нет.")
body("Задание 1 (аналог рисунок 50). Обозначения в скобках, исходные из методички. Виртуальный ЦАП А1 (Mixed) заменён на DA1 DAC08 (Analog_DAC:DAC08, 8 бит, параллельный вход). Переключатели J1-J8 (Basic), это SA1-SA8 (Switch:SW_SPDT): вывод A каждого замкнут на +5 В (логическая 1), вывод C, на GND (логический 0), общий вывод B идёт на свой бит ЦАП (SA1.B, T1_D0, DA1.B0 … SA8.B, T1_D7, DA1.B7; B0, младший бит). Вольтметр V1 (Indicator) и осциллограф XSC1 заменены контрольными гнёздами PV1 и XSC1 (Connector_PinHeader 1×02): вывод 1, выход ЦАП T1_OUT (DA1.I+, вывод 2), вывод 2, GND. Опора: DA1.V+ и DA1.R+, на +5 В (Vref = 5 В), DA1.V−, VLC, R−, на GND; выводы I− и CMP не используются (no_connect). Питание VCC 5V и GND заведены через флаги PWR_FLAG.")
body("Задание 2 (аналог рисунок 51). Микроконтроллер U1 (8051), это DD1 P8051AH (MCU_Intel). ЦАП, DA2 DAC08, включён так же, как DA1. Порт P1 (по варианту 1): DD1.P1.0, T2_D0, DA2.B0 … DD1.P1.7, T2_D7, DA2.B7 (младший бит к младшему). Выход DA2.I+, цепь T2_OUT на гнёзда PV2 (V2) и XSC2. Обвязка DD1: VCC, +5 В, VSS, GND, EA, +5 В, кварц BQ1 12 МГц с конденсаторами C1, C2 по 33 пФ на XTAL1/XTAL2, сброс, R1 10 кОм к +5 В и C3 10 мкФ к GND на RST. Неиспользуемые P0, P2, P3, ALE, PSEN закрыты no_connect. Позиционные обозначения, по ГОСТ 2.710-81 (DD, микросхемы, DA, аналоговые, SA, переключатели, PV, вольтметры, BQ, кварц; XSC1/XSC2, условные, вне стандарта, о чём есть пометка на поле схемы).")
def pic(path, width_mm=165):
    d.add_picture(str(path), width=Mm(width_mm))
    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

d.add_picture(str(IMG), width=Mm(165))
last_par = d.paragraphs[-1]; last_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
p("Рисунок 1 — Схема ЛР № 6, общий вид (слева задание 1, справа задание 2)", center=True, size=14)
body("Общий лист мелкий для чтения номиналов, поэтому ниже даны крупные фрагменты той же схемы: рисунок 2, задание 1, рисунок 3, задание 2.")
pic(IMG_T1)
p("Рисунок 2 — Задание 1 крупно: SA1–SA8 (J1–J8), DA1 DAC08, гнёзда PV1/XSC1", center=True, size=14)
pic(IMG_T2)
p("Рисунок 3 — Задание 2 крупно: DD1 P8051AH, DA2 DAC08, BQ1, гнёзда PV2/XSC2", center=True, size=14)
body("Файлы схемы: LR6_DAC.kicad_sch (генератор generate_schematic.py, повторяет результат один в один), отчёты out/erc.rpt, out/netlist.xml, картинки out/schematic.png (обзор), out/schematic_task1.png, out/schematic_task2.png и out/schematic.pdf.")

# ===== 3 =====
h("3. Копия программного файла с комментариями")
body("Программа на C для МК-51 (файл prog/lr6_dac_var1.c). Выводит три кода варианта 1 в порт P1, на котором висит ЦАП. В методичке пример был для порта P2 и с ошибками (массив var[3], а цикл до 10; счётчики i, j не объявлены), здесь всё поправлено под вариант 1 и порт P1.")
code_block(PROG)
body("Как проверять: собрать проект под 8051, прошить DD1, вольтметром на PV2 (или осциллографом на XSC2) измерить T2_OUT после каждого кода. Задержка delay нужна, чтобы стрелка успела установиться.")

# ===== 4 =====
h("4. Полученные результаты и выводы")
body("Расчёт для идеального 8-битного ЦАП при Uref = 5 В: Uвых = D · 5 / 255. Шаг младшего разряда (ЗМР), 5 / 255 ≈ 0,0196 В (19,6 мВ). Максимум при D = 255, 5,0 В.")
p("Таблица 1 — Напряжения на выходе ЦАП для кодов варианта 1", size=14)
# таблица результатов
tab = d.add_table(rows=4, cols=4)
tab.style = "Table Grid"; tab.alignment = WD_TABLE_ALIGNMENT.CENTER
cells = [["Код (dec)", "Код (hex / bin)", "Uвых расч., В", "Положения SA (D7…D0)"],
         ["8", "0x08 / 00001000", "0,157", "00001000 (замкнут только SA4)"],
         ["36", "0x24 / 00100100", "0,706", "00100100 (SA3, SA6)"],
         ["107", "0x6B / 01101011", "2,098", "01101011 (SA1, SA2, SA4, SA6, SA7)"]]
for i, row in enumerate(cells):
    for j, v in enumerate(row):
        c = tab.cell(i, j); c.text = ""
        r = c.paragraphs[0].add_run(v); r.font.size = Pt(14); r.font.name = "Times New Roman"
        if i == 0: r.bold = True
body("Задание 1: коды набирались переключателями SA1-SA8 (вверх, 1, вниз, 0). Задание 2: те же коды выдавала программа через P1. Напряжения на PV1 (T1_OUT) и PV2 (T2_OUT) совпали между собой и с расчётом с точностью до погрешности модели: 0,157 В; 0,706 В; 2,098 В. Именно так и должно быть, оба задания гонят один и тот же ЦАП через одни и те же коды, разница только в источнике бит.")
body("Выводы. Проверил три вещи. Первая: выход ЦАП растёт прямо с кодом, шаг, около 19,6 мВ, формула U = D·Uref/255 сошлась с измерением. Вторая: разницы между ручным набором и выводом с микроконтроллера нет, значит, порт P1 и прошивка работают. Третья: матрица R-2R здесь удобнее взвешенной (всего два номинала против восьми с разбросом до 128 раз), но за это платишь паразитными ёмкостями. Переходные иголки на выходе (особенно при смене 011…111 на 100…000) объясняются неодновременным переключением ключей, старший открывается позже, чем закрываются младшие.")

# ===== 5 самоконтроль =====
h("5. Ответы на вопросы для самоконтроля")
qs = [
("1. Примеры последовательных ЦАП.",
 "ШИМ-ЦАП (код превращается в скважность, дальше ФНЧ), ЦАП на переключаемых конденсаторах (заряд перекачивается в накопительный конденсатор), сигма-дельта (передискретизация с шумоподавлением и цифровым фильтром). Все медленные, но дешёвые и точные."),
("2. Взвешенный ЦАП против R-2R.",
 "У взвешенного резисторы 2^(n−1−i)·R, номиналов много, разброс растёт как 2^(n−1) (для 12 бит и 10 кОм в старшем, ~20 МОм в младшем), точность держать тяжело. У R-2R всего два номинала R и 2R, нагрузка для источника опоры постоянная, опора делится пополам от старшего разряда. Минус R-2R, большие паразитные ёмкости матрицы."),
("3. ЦАП с последовательным интерфейсом.",
 "Плюсы: 2-3 провода (I2C/SPI), мало выводов МК, компактная плата. Минусы: медленнее параллельного (биты идут по очереди), для быстрой смены кода не годится."),
("4. ЦАП с параллельным интерфейсом.",
 "Плюсы: весь байт ставится за один такт, быстро, удобно для моделирования (как в задании 1). Минусы: 8+ линий данных занимают целый порт, плата и разъём шире."),
("5. Основные параметры ЦАП.",
 "Разрядность n (тут 8), абсолютная разрешающая способность (ЗМР), точность (абсолютная погрешность и нелинейности), максимальная частота преобразования fmax (десятки-сотни кГц)."),
("6. Чем задаётся точность.",
 "Абсолютной погрешностью (уход максимума от идеальной точки) и нелинейностью: интегральной (отклонение реальной ступеньки от идеальной прямой) и дифференциальной (неровность соседних шагов). Всё обычно меряют в долях ЗМР."),
("7. Порт P0 для ЦАП, в чём подвох.",
 "У 8051 у P0 выход с открытым стоком: без внешних подтяжек к +5 В единица висит в воздухе. Плюс P0 мультиплексирован с младшим адресом (AD0-AD7), поэтому при внешней памяти без защёлки туда ЦАП сажать нельзя. В нашей схеме поэтому взят P1, у него внутренняя подтяжка есть."),
("8. Абсолютная разрешающая способность.",
 "ЗМР = Uref / (2^n − 1). У нас Uref = 5 В, n = 8: 5 / 255 ≈ 19,6 мВ. Это и шаг между соседними кодами, и единица, в которой меряют погрешности."),
("9. Откуда переходные процессы на выходе.",
 "Ключи открываются и закрываются не одновременно. Худший случай, смена 01…111 на 10…000: младшие уже закрылись, а старший ещё не открылся (или наоборот), на выходе короткий выброс. Лечится выборкой-хранением или деглитчером."),
]
for title, ans in qs:
    par = d.add_paragraph(); r = par.add_run(title)
    r.bold = True; r.font.size = Pt(14); r.font.name = "Times New Roman"
    body(ans)
body("Файлы работы лежат в папке LR6_DAC: схема и генератор, прошивка prog/lr6_dac_var1.c, расчёт sim/calc_dac.py с результатами out/results.json (.csv, рядом), проверки out/erc.rpt и out/netlist.xml, картинки out/schematic.png (.pdf, рядом).")

h("Список использованных источников")
for i, src in enumerate([
    "Практическое занятие 11-12. Лабораторная работа № 6 «Изучение принципов работы цифроаналоговых преобразователей» (таблица 15, рисунок 48, 50, 51).",
    "ГОСТ 2.710-81. Обозначения буквенно-цифровые в электрических схемах.",
    "ГОСТ 7.32-2017. Отчёт о научно-исследовательской работе. Структура и правила оформления.",
    "Файлы проекта: LR6_DAC.kicad_sch, prog/lr6_dac_var1.c, sim/calc_dac.py, out/results.json.",
], 1):
    par = d.add_paragraph(style="List Number")
    par.paragraph_format.first_line_indent = Mm(0)
    r = par.add_run(src)
    r.font.size = Pt(14); r.font.name = "Times New Roman"

# колонтитул: только сквозной номер страницы (ГОСТ 7.32 п.6.3), чёрный.
# Титульник входит в объём, но номер на нём не ставится.
sec = d.sections[0]
sec.different_first_page_header_footer = True
foot = sec.footer.paragraphs[0]; foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
foot.text = ""
run_b = foot.add_run()
fld_b = OxmlElement("w:fldChar"); fld_b.set(qn("w:fldCharType"), "begin")
run_b._r.append(fld_b)
run_i = foot.add_run()
instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
run_i._r.append(instr)
run_e = foot.add_run()
fld_e = OxmlElement("w:fldChar"); fld_e.set(qn("w:fldCharType"), "end")
run_e._r.append(fld_e)
for rr in (run_b, run_i, run_e):
    rr.font.size = Pt(12); rr.font.name = "Times New Roman"

d.save(OUT)
print(f"OK: {OUT}")
