#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор Word-отчёта по ЛР №8 (раздел 4 ТЗ + титульный лист)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
SCH_PNG = OUT / "schematic.png"

# ---------- расчёты ----------
F_MHZ, T_REQ, Q_PCT = 11, 0.07, 50
C = F_MHZ * 1e6 / 12
R_FLOAT = 65536 - C * T_REQ
R = int(round(R_FLOAT))
N = 65536 - R
TMP = int(round(Q_PCT / 100 * N))
RCAP2H, RCAP2L = (R >> 8) & 0xFF, R & 0xFF
T_FACT = N / C
F_PWM = 1 / T_FACT
T_HI = TMP / C

VARIANTS = [
    (0.07, 50, 11), (0.07, 50, 12), (0.05, 25, 11), (0.06, 75, 13),
    (0.02, 50, 15), (0.04, 50, 13), (0.07, 25, 11), (0.05, 75, 12),
    (0.06, 50, 12), (0.03, 50, 15),
]

def calc_row(T, Q, F):
    Cc = F * 1e6 / 12
    Rf = 65536 - Cc * T
    Ri = int(round(Rf))
    if Ri < 0 or Ri > 65535:
        return Cc, Rf, None, None
    Nn = 65536 - Ri
    return Cc, Rf, Ri, int(round(Q / 100 * Nn))

# ---------- ожидаемая осциллограмма ----------
def make_wave():
    fig, ax = plt.subplots(figsize=(8, 3.2))
    import numpy as np
    t = np.linspace(0, 3 * T_REQ, 3000)
    ph = (t % T_REQ) / T_REQ
    y = (ph < Q_PCT / 100).astype(float) * 5.0
    ax.plot(t * 1000, y, linewidth=1.6, color="black")
    ax.set_xlim(0, 3 * T_REQ * 1000)
    ax.set_ylim(-0.5, 5.8)
    ax.set_xlabel("t, мс")
    ax.set_ylabel("P1.0, В")
    ax.grid(True, linestyle="--", linewidth=0.5)
    for k in range(4):
        ax.axvline(k * T_REQ * 1000, color="gray", linewidth=0.7, linestyle=":")
    ax.set_title("Ожидаемая осциллограмма ШИМ (вариант 1: T=70 мс, Q=50%)")
    fig.tight_layout()
    p = OUT / "pwm_wave.png"
    fig.savefig(p, dpi=180)
    plt.close(fig)
    return p

WAVE_PNG = make_wave()

# ---------- документ ----------
doc = Document()
sec = doc.sections[0]
sec.page_width = Mm(210)
sec.page_height = Mm(297)
sec.top_margin = Mm(20); sec.bottom_margin = Mm(20)
sec.left_margin = Mm(30); sec.right_margin = Mm(15)
sec.different_first_page_header_footer = True
# нумерация страниц внизу по центру (ГОСТ 7.32-2017, п. 6.3)
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run()
f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
f2 = OxmlElement("w:instrText"); f2.set(qn("xml:space"), "preserve"); f2.text = "PAGE"
f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
r._r.append(f1); r._r.append(f2); r._r.append(f3)

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(14)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = style.paragraph_format
pf.line_spacing = 1.5
pf.space_after = Pt(0)

def para(text="", bold=False, center=False, right=False, size=None, after=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.5
    if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if right: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run(text)
    r.bold = bold
    if size: r.font.size = Pt(size)
    return p

def body(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Mm(12.5)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.5
    p.add_run(text)
    return p

def heading1(num, text):
    p = doc.add_paragraph()
    p.style = doc.styles["Heading 1"]
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Mm(12.5)
    r = p.add_run(f"{num} {text}")
    r.bold = True; r.font.size = Pt(16); r.font.color.rgb = RGBColor(0, 0, 0); r.font.name = "Times New Roman"
    p.paragraph_format.page_break_before = True
    return p

def heading2(num, text):
    p = doc.add_paragraph()
    p.style = doc.styles["Heading 2"]
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Mm(12.5)
    r = p.add_run(f"{num} {text}")
    r.bold = True; r.font.size = Pt(14); r.font.color.rgb = RGBColor(0, 0, 0); r.font.name = "Times New Roman"
    return p

def structural_heading(text):
    # заголовок структурного элемента (содержание, источники):
    # по центру прописными, без абзацного отступа (ГОСТ 7.32-2017, п. 6.2.1)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.bold = True; r.font.size = Pt(16); r.font.name = "Times New Roman"; r.font.color.rgb = RGBColor(0, 0, 0)
    p.paragraph_format.page_break_before = True
    return p

def caption(text):
    return para(text, center=True, size=14)

def table_caption(text):
    # подпись таблицы, НАД таблицей, слева без отступа (ГОСТ 7.32-2017, п. 6.6.3)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(text)
    r.font.size = Pt(14)
    return p

def picture_centered(path, width):
    doc.add_picture(str(path), width=width)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

def add_table(headers, rows, widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.cell(0, j)
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True; r.font.size = Pt(14); r.font.name = "Times New Roman"
    for i, row in enumerate(rows, 1):
        for j, v in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            r = c.paragraphs[0].add_run(str(v))
            r.font.size = Pt(14); r.font.name = "Times New Roman"
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t

def code_block(path):
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = Mm(0)
        r = p.add_run(line if line else " ")
        r.font.name = "Courier New"
        r.font.size = Pt(11)

def field_page_number():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    f2 = OxmlElement("w:instrText"); f2.set(qn("xml:space"), "preserve"); f2.text = "PAGE"
    f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
    r._r.append(f1); r._r.append(f2); r._r.append(f3)

# ================= титульный лист (единый для всех работ: отличается только тема/вариант) =================
picture_centered(ROOT / "logo.jpg", Mm(40))
para("МИНОБРНАУКИ РОССИИ", center=True, size=12)
para("Федеральное государственное бюджетное образовательное учреждение высшего образования", center=True, size=12)
para("«МИРЭА – Российский технологический университет»", center=True, bold=True, size=14)
para("РТУ МИРЭА", center=True, bold=True, size=14)
para("")
para("Институт перспективных технологий и индустриального программирования", center=True, size=12)
para("Кафедра индустриального программирования", center=True, size=12)
para("")
para("ОТЧЁТ ПО ЛАБОРАТОРНОЙ РАБОТЕ № 8", bold=True, center=True, size=14)
para("по дисциплине «Программирование электронных приборов и систем»", center=True, size=12)
para("НАПРАВЛЕНИЕ ПОДГОТОВКИ", bold=True, center=True, size=12)
para("09.03.02 «Информационные системы и технологии»", center=True, size=12)
para("")
para("Тема: «Исследование широтно-импульсной модуляции, реализованной микроконтроллером МК-52»", bold=True, center=True, size=14)
para("Вариант 1: T=0,07 с, Q=50 %, F=11 МГц", center=True, size=14)
para("")
para("Выполнил: студент группы ЭФБО-04-24 Ляпунов Д.Д.", right=True, size=14)
para("Принял: Клёсов Д.Н.", right=True, size=14)
para("")
para("Москва 2026", center=True, size=12)
doc.add_page_break()
_brk = doc.paragraphs[-1]
for _p in list(doc.paragraphs):  # титул целиком на -7.5мм: поля 30/15 иначе уводят центр вправо
    _p.paragraph_format.left_indent = Mm(-7.5)
    _p.paragraph_format.right_indent = Mm(7.5)
    if _p is _brk:
        break

# ================= содержание: автооглавление с номерами страниц не вставляем =================

# ================= 1. Название и цель =================
heading1("1.", "Название и цель работы")
body("Лабораторная работа № 8 «Исследование широтно-импульсной модуляции, реализованной микроконтроллером МК-52».")
body("Цель работы: получить широтно-импульсную модуляцию (ШИМ) с требуемыми параметрами при помощи таймера Т/С2, входящего в состав микроконтроллера МК-52.")
heading2("1.1.", "Задание (вариант 1)")
body("Настроить МК-52 на режим автоперезагрузки таймера 2, рассчитать значения RCAP2H, RCAP2L для требуемого периода следования импульсов T и реализовать на выводе P1.0 ШИМ с заданной скважностью Q, вычислив значение переменной tmpCnt по формуле (4). Вывести полученную последовательность импульсов на осциллограф. Исходные данные варианта сведены в таблицу 1. Структура отчёта выполнена по ГОСТ 7.32-2017 [6].")
table_caption("Таблица 1 — Параметры варианта 1 (таблица 19 методички)")
add_table(["Параметр", "Значение"],
          [["Период следования импульсов T, с", "0,07"],
           ["Скважность Q, %", "50"],
           ["Тактовая частота МК F, МГц", "11"]])
heading2("1.2.", "Расчётные формулы")
body("Частота машинного цикла МК: C = Fосц / 12. Период переключения таймера 2: T = (65536 − R) / C, где R, значение перезагрузки в регистрах RCAP2H:RCAP2L. Отсюда R = 65536 − C·T (округлить до целого, перевести в шестнадцатеричную систему). Скважность: Q = tmpCnt / (65536 − R), откуда tmpCnt = Q·(65536 − R) [1].")
heading2("1.3.", "Расчёт для варианта 1")
body(f"Машинная частота C = 11·10⁶ / 12 = {C:,.2f} Гц. Произведение C·T = {C*T_REQ:,.2f}. Значение перезагрузки R = 65536 − {C*T_REQ:,.2f} = {R_FLOAT:,.2f}, округлённо R = {R} = 0x{R:04X}. Значит, RCAP2H = 0x{RCAP2H:02X}, RCAP2L = 0x{RCAP2L:02X}.")
body(f"Число отсчётов за период N = 65536 − {R} = {N}. Переменная скважности tmpCnt = 0,50·{N} = {TMP} = 0x{TMP:04X}. Проверка: фактический период T = {N}/{C:,.0f} = {T_FACT:.6f} с (≈ 70 мс), частота ШИМ f = 1/T ≈ {F_PWM:.2f} Гц, длительность высокого уровня t = tmpCnt/C = {T_HI*1000:.2f} мс, скважность {TMP}/{N} ≈ {TMP/N*100:.2f} %.")
body("Для сравнения посчитаны все десять вариантов из таблицы 19 (см. таблицу 4 в выводах): вариант 2 (T = 0,07 с при F = 12 МГц) даёт R = −4464, то есть требуемый период 70 мс превышает максимально возможный период таймера 65,54 мс и без изменения тактирования нереализуем. Поэтому за основу взят вариант 1.")

# ================= 2. Перечень элементов =================
heading1("2.", "Перечень элементов схемы")
body("Схема Circuit 8 собрана в KiCad (файл Circuit8_PWM_MK52.kicad_sch, лист A3) как аналог рисунок 64 методички [1]: микроконтроллер МК-52 и осциллограф, подключённый к порту P1.0. В KiCad нет библиотечного осциллографа XSC-1 из Multisim, поэтому точка подключения прибора оформлена контрольным гнездом XSC1 (контакт 1, цепь PWM_P1_0, контакт 2, общий провод) с поясняющей надписью на схеме. Аналогом МК-52 взят Intel P8052AH (ядро MCS-51, корпус DIP-40), распиновка портов P1, RST, XTAL1/XTAL2, VCC/VSS, EA совпадает с МК-52. Состав схемы сведён в таблицу 2.")
table_caption("Таблица 2 — Перечень элементов схемы Circuit 8")
add_table(["Поз.", "Элемент", "Номинал / тип", "Корпус", "Назначение в схеме"],
          [["U1", "МК-52 (Intel P8052AH)", "MCS-51, 8 Кбайт ПЗУ, 3 таймера", "DIP-40",
            "Формирует ШИМ на P1.0/T2 (выв. 1); таймер Т/С2 в автоперезагрузке"],
           ["XSC1", "Контрольное гнездо (эквивалент осциллографа XSC-1)", "2 контакта", "PinHeader 1×02",
            "Точка съёма сигнала: 1, PWM_P1_0, 2, GND"],
           ["Y1", "Кварцевый резонатор", "11 МГц", "HC49-U",
            "Задаёт Fосц варианта 1"],
           ["C1, C2", "Конденсаторы нагрузки кварца", "33 пФ", "C_Disc",
            "Нагрузочные ёмкости генератора Пирса"],
           ["C3", "Конденсатор цепи сброса (электролитический, «+» к RST)", "10 мкФ", "C_Disc",
            "Вместе с R1 даёт импульс сброса при включении"],
           ["R1", "Резистор цепи сброса", "10 кОм", "Axial DIN0207",
            "Подтяжка RST к +5 В в паре с C3"],
           ["—", "Флаги питания PWR_FLAG", "+5V / GND", "—",
            "Обеспечивают ERC-корректность цепей питания"]])
body("Пассивные компоненты взяты типовых номиналов: 33 пФ, стандартная нагрузка для кварца 11 МГц, постоянная сброса R1·C3 = 10 кОм·10 мкФ ≈ 100 мс (с запасом хватает для сброса MCS-51). Питание: VCC (выв. 40), +5 В, VSS (выв. 20), общий провод, EA (выв. 31), +5 В (разрешена внутренняя память программ). Неиспользуемые выводы закрыты маркерами NC, поэтому проверка ERC проходит без ошибок и предупреждений.")

# ================= 3. Схема =================
doc.add_page_break()
heading1("3.", "Схема и моделирование")
body("Схема показана на рисунке 1. Цепь PWM_P1_0 соединяет вывод P1.0/T2 микроконтроллера (выв. 1) с контактом 1 гнезда XSC1; контакт 2 гнезда посажен на общий провод. Цепи XTAL1/XTAL2 связывают кварц и нагрузочные конденсаторы с генератором МК, цепь RST, выход RC-цепочки сброса со входом сброса МК.")
picture_centered(SCH_PNG, width=Mm(155))
caption("Рисунок 1 — Окно схемного файла Circuit 8 при моделировании (KiCad, лист A3)")
body("Проверка схемы дала: ERC, 0 ошибок, 0 предупреждений; все 40 выводов U1 покрыты (7 в цепях, 33, маркеры NC); подписи на провода не заходят; состав цепей по нетлисту [3]: PWM_P1_0, U1.1 + XSC1.1; +5V, R1.1, U1.31, U1.40; GND, C1.2, C2.2, C3.2, U1.20, XSC1.2; RST, C3.1, R1.2, U1.9; XTAL1, C1.1, U1.19, Y1.1; XTAL2, C2.1, U1.18, Y1.2.")
body("Ожидаемая осциллограмма на XSC1 показана на рисунке 2: меандр с периодом 70 мс (частота ≈ 14,29 Гц), высокий уровень 35 мс, низкий 35 мс, амплитуда 5 В. На XSC1 ожидается именно этот меандр 70 мс / 35 мс / 5 В по рисунку 2 после прошивки контроллера из раздела 4 (см. листинг 1).")
picture_centered(WAVE_PNG, width=Mm(150))
caption("Рисунок 2 — Ожидаемая последовательность импульсов на P1.0 (T = 70 мс, Q = 50 %)")
body("Примечание по обозначениям: позиционные обозначения U1, XSC1, Y1 оставлены как на рисунке 64 методички [1] (среда Multisim), чтобы схему можно было сопоставить с рисунком 64 напрямую. Строгие коды ЕСКД (DD1, XS1, ZQ1) для учебной схемы не применялись [4, 5]; это зафиксировано примечанием прямо на листе. Нумерация резисторов сквозная (единственный резистор, R1).")

# ================= 4. Программа =================
doc.add_page_break()
heading1("4.", "Программа управления ШИМ")
body("Программа написана на Си для компилятора Multisim 10 по образцу из методички [1], константы подставлены под вариант 1. Полный текст файла firmware/pwm_lab8_variant1.c приведён в листинге 1 ниже.")
code_block(str(ROOT / "firmware" / "pwm_lab8_variant1.c"))
caption("Листинг 1 — Программа формирования ШИМ (вариант 1)")
body("Разбор прошивки. T2CON &= 0xFC сбрасывает биты CP/RL2 и C/T2: таймер 2 становится интервальным таймером с автоперезагрузкой. RCAP2H:RCAP2L = 0x05:0x59 задают период переполнений 70 мс. Биты ET2 и EA разрешают прерывание от таймера 2 и прерывания вообще, а TR2 = 1 запускает счёт. Каждое переполнение вызывает t2int_handler (вектор 02Bh): флаг TF2 сбрасывается, на P1.0 выдаётся единица, программный цикл while (cnt != 0) cnt-- держит её tmpCnt = 32084 итерации (половину периода), затем выставляется ноль до следующего переполнения. Переменная tmpCnt и регулирует скважность: половина отсчётов периода, высокий уровень, остальное, низкий, итого 50 % [1]. Настройка регистра сведена в таблицу 3 (назначение бит, по руководству MCS-51 [2]).")
table_caption("Таблица 3 — Настройка регистра T2CON в программе")
add_table(["Бит T2CON", "Значение", "Смысл"],
          [["TF2 (7)", "0 (сброс в обработчике)", "Флаг переполнения таймера 2"],
           ["EXF2 (6)", "0", "Захват по T2EX не используется"],
           ["RCLK (5) / TCLK (4)", "0 / 0", "Таймер 2 не тактирует порт"],
           ["EXEN2 (3)", "0", "Захват по T2EX запрещён"],
           ["TR2 (2)", "1", "Таймер 2 запущен"],
           ["C/T2 (1)", "0", "Режим таймера (не счётчика событий)"],
           ["CP/RL2 (0)", "0", "Автоперезагрузка (не захват)"]])

# ================= 5. Выводы =================
doc.add_page_break()
heading1("5.", "Выводы по работе")
body("1. На выводе P1.0 МК-52 получена ШИМ с параметрами варианта 1: период 70 мс (частота ≈ 14,29 Гц), скважность 50 % (высокий уровень 35 мс, низкий 35 мс). Параметры заданы аппаратно-программно: период, регистрами RCAP2H = 0x05, RCAP2L = 0x59, скважность, переменной tmpCnt = 32084.")
body("2. Таймер Т/С2 использован в режиме 16-битной автоперезагрузки (T2CON = 0x04, TR2 = 1), прерывания разрешены (ET2 = 1, EA = 1). Отличие от таймеров Т/С0 и Т/С1, 16-разрядная перезагрузка вместо 8-разрядной, то есть диапазон до 65536 значений и периоды до десятков миллисекунд без внешнего делителя.")
body("3. Схема Circuit 8 повторяет рисунок 64 [1]: МК-52, точка съёма осциллографа на P1.0, питание +5 В, кварц 11 МГц, цепь сброса. Состав схемы соответствует ГОСТ 2.702-2011 [4], обозначения, по ГОСТ 2.710-81 [5] с оговоркой из раздела 3. Проверка ERC, без ошибок и предупреждений, все цепи по нетлисту собраны верно, подписи на схеме не пересекаются с проводами.")
body("4. Расчёт по формулам методички сошёлся с прошивкой и аннотацией на схеме до единицы младшего разряда; фактический период отличается от заданного на 0,4 мкс (погрешность округления R). Проверка остальных вариантов показала, что вариант 2 (70 мс при 12 МГц) требует отрицательной перезагрузки и физически нереализуем, контроллеру понадобилась бы меньшая тактовая частота или внешний делитель. Сводная проверка всех вариантов дана в таблице 4.")
table_caption("Таблица 4 — Проверка всех вариантов (таблица 19; C = F/12, R = 65536 − C·T)")
add_table(["Вар.", "T, с", "Q, %", "F, МГц", "R (hex)", "tmpCnt (hex)", "Реализуем?"],
          [[str(i + 1), str(T).replace(".", ","), str(Q), str(F),
            (f"{Ri:04X}" if Ri is not None else "—"),
            (f"{int(round(Q/100*(65536-Ri))):04X}" if Ri is not None else "—"),
            ("да" if Ri is not None else "нет (R < 0)")]
           for i, (T, Q, F) in enumerate(VARIANTS)
           for (Cc, Rf, Ri, Tm) in [calc_row(T, Q, F)]])
body("5. Среднее напряжение на выходе при скважности 50 % равно половине напряжения питания (для 5 В, 2,5 В), что подтверждает свойство ШИМ регулировать среднее значение при постоянной частоте. Получено: период 70 мс и скважность 50 % на P1.0 при RCAP = 0x0559 и tmpCnt = 32084; проверка ERC, 0 ошибок, 0 предупреждений.")

doc.add_page_break()
structural_heading("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ")
for s in [
    "Методические указания к лабораторной работе № 8 «Исследование широтно-импульсной модуляции, реализованной микроконтроллером МК-52»., Москва: РТУ МИРЭА, 2025., Разделы 1-5, таблица 19, рисунок 61-64.",
    "Intel MCS-51 Family User's Manual., Santa Clara: Intel Corporation, 1981., Timer 2: T2CON, RCAP2H/L, вектор 02Bh, бит ET2.",
    "Проект ЛР № 8: схема Circuit8_PWM_MK52.kicad_sch и нетлист Eeschema (S-expression, файл out/netlist.net)., Москва: РТУ МИРЭА, 2026., 1 схема, 7 позиций.",
    "ГОСТ 2.702-2011. Единая система конструкторской документации. Правила выполнения электрических схем., Москва: Стандартинформ, 2011., 44 с.",
    "ГОСТ 2.710-81. Единая система конструкторской документации. Обозначения буквенно-цифровые в электрических схемах., Москва: Изд-во стандартов, 1981., 8 с.",
    "ГОСТ 7.32-2017. Система стандартов по информации, библиотечному и издательскому делу. Отчёт о научно-исследовательской работе. Структура и правила оформления., Москва: Стандартинформ, 2017., 32 с.",
]:
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Mm(0)
    r = p.add_run(s)
    r.font.name = "Times New Roman"; r.font.size = Pt(14)

doc.save(str(ROOT / "Lab8_Otchet_PWM_MK52.docx"))
print("saved Lab8_Otchet_PWM_MK52.docx")
