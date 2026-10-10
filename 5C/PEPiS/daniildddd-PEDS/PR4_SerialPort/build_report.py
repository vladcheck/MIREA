#!/usr/bin/env python3
"""Сборка Word-отчёта ПР №4 по разделу 4 ТЗ. Стиль, ГОСТ 7.32-2017."""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "PR4_Otchet.docx"
SCH_PNG = ROOT / "out" / "Circuit4_schematic.png"
WAVE_PNG = ROOT / "out" / "serial_mode0_waveform.png"
CLOSEUP_PNG = ROOT / "out" / "Circuit4_closeup.png"

d = Document()

# --- базовые стили ---
sec = d.sections[0]
sec.page_width, sec.page_height = Mm(210), Mm(297)  # A4 (дефолт шаблона, Letter!)
sec.left_margin = Mm(30); sec.right_margin = Mm(15)
sec.top_margin = Mm(20); sec.bottom_margin = Mm(20)
sec.different_first_page_header_footer = True  # номера нет на титуле

style = d.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(14)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = style.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
pf.space_after = Pt(0)
pf.first_line_indent = Mm(12.5)

for i in range(1, 4):
    hs = d.styles[f"Heading {i}"]
    hs.font.name = "Times New Roman"
    hs.font.size = Pt(14 if i > 1 else 16)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hs.paragraph_format.space_before = Pt(12)
    hs.paragraph_format.space_after = Pt(6)
    hs.paragraph_format.first_line_indent = Mm(0)
    hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 1 else WD_ALIGN_PARAGRAPH.LEFT

def para(text, bold=False, center=False, indent=True, size=14, space_after=0):
    p = d.add_paragraph()
    p.paragraph_format.first_line_indent = Mm(0 if (center or not indent) else 12.5)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size)
    r.font.name = "Times New Roman"
    return p

def heading2(text):
    h = d.add_heading(text, level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in h.runs:
        r.bold = True; r.font.size = Pt(16)
        r.font.name = "Times New Roman"; r.font.color.rgb = RGBColor(0, 0, 0)
    h.paragraph_format.page_break_before = True
    return h

def caption(text):
    return para(text, center=True, indent=False, size=14, space_after=6)

def tblcap(text):
    # Подпись таблицы по ГОСТ 7.32: слева, без отступа
    p = para(text, center=False, indent=False, size=14, space_after=6)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p

def table(headers, rows, widths=None):
    t = d.add_table(rows=1 + len(rows), cols=len(headers))
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
    d.add_paragraph().paragraph_format.space_after = Pt(6)
    return t

def code_block(path, max_lines=90):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()[:max_lines]
    for ln in lines:
        p = d.add_paragraph()
        p.paragraph_format.first_line_indent = Mm(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        r = p.add_run(ln if ln.strip() else " ")
        r.font.name = "Courier New"
        r.font.size = Pt(11)
    d.add_paragraph().paragraph_format.space_after = Pt(6)

def add_page_number():
    # номера страниц внизу по центру
    for s in d.sections:
        f = s.footer
        f.is_linked_to_previous = False
        p = f.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run()
        fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
        fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
        r._r.append(fld1); r2 = p.add_run(); r2._r.append(instr); r3 = p.add_run(); r3._r.append(fld2)

# ================= Титульный лист (единый для всех практик: отличается только тема/вариант) =================
_logo = d.add_paragraph(); _logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
_logo.add_run().add_picture(str(ROOT / "logo.jpg"), width=Mm(40))
para("МИНОБРНАУКИ РОССИИ", center=True, size=12)
para("Федеральное государственное бюджетное образовательное учреждение высшего образования", center=True, size=12)
para("«МИРЭА – Российский технологический университет»", bold=True, center=True, size=14)
para("РТУ МИРЭА", bold=True, center=True, size=14)
para("Институт перспективных технологий и индустриального программирования", center=True, size=12)
para("Кафедра индустриального программирования", center=True, size=12)
d.add_paragraph()
para("ОТЧЁТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 4", bold=True, center=True, size=14)
para("по дисциплине «Программирование электронных приборов и систем»", center=True, size=12)
para("НАПРАВЛЕНИЕ ПОДГОТОВКИ", bold=True, center=True, size=12)
para("09.03.02 «Информационные системы и технологии»", center=True, size=12)
d.add_paragraph()
para("Тема: «Основы организации последовательного порта»", bold=True, center=True, size=14)
para("Вариант 1: T / K=0 / 1000 Кбит/с / XX=50h / N=10", center=True, size=14)
d.add_paragraph()
for _txt in ["Выполнил: студент группы ЭФБО-04-24 Ляпунов Д.Д.", "Принял: Клёсов Д.Н."]:
    _p = d.add_paragraph()
    _p.paragraph_format.first_line_indent = Mm(0)
    _p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _r = _p.add_run(_txt)
    _r.font.size = Pt(14); _r.font.name = "Times New Roman"
d.add_paragraph()
para("Москва 2026", center=True, size=12)
d.add_page_break()
_brk = d.paragraphs[-1]
for _p in list(d.paragraphs):  # титул целиком на -7.5мм: поля 30/15 иначе уводят центр вправо
    _p.paragraph_format.left_indent = Mm(-7.5)
    _p.paragraph_format.right_indent = Mm(7.5)
    if _p is _brk:
        break

# ================= Содержание =================
para("СОДЕРЖАНИЕ", bold=True, center=True, size=15)
for item in ["Введение",
             "1. Наименование и цель работы",
             "2. Особенности работы последовательного порта в режиме 0",
             "3. Схема моделирования (Circuit4)",
             "4. Программа передачи (ассемблер и C)",
             "5. Результаты и выводы",
             "Список использованных источников"]:
    p = d.add_paragraph(item)
    p.paragraph_format.first_line_indent = Mm(0)

# ================= Введение =================
heading2("Введение")
para("В работе настраивается последовательный порт микроконтроллера МК-51 на передачу "
     "данных в синхронном режиме. Вариант 1 из таблицы 12 методички, передача (T) десяти байт "
     "из резидентной памяти с адреса 50h в режиме 0 со скоростью 1000 Кбит/с. Такой выбор удобен "
     "тем, что скорость задаётся только кварцем и не требует настройки таймера: при резонаторе "
     "12 МГц порт сам даёт 1 МГц. Схема собрана в KiCad (проект Circuit4) как аналог рисунка 40 "
     "методички: микроконтроллер P8051AH и пробник осциллографа на выводе P3.0. Программа написана "
     "в двух вариантах, на ассемблере и на C, оба с подробными комментариями. Проверка состоит "
     "из трёх частей: контроль электрических правил KiCad (ERC, 0 ошибок), расчёт временных "
     "параметров и построение модели осциллограммы, плюс проверка по чек-листу: оформление "
     "по ГОСТ, читаемость схемы, соответствие заданию.")

# ================= 1 =================
heading2("1. Наименование и цель работы")
para("Наименование: «Основы организации последовательного порта» (практическая работа № 4).")
para("Цель: научиться использовать последовательный порт микроконтроллера для передачи данных, "
     "настроить режим, скорость и буфер, организовать цикл выдачи байтов и проконтролировать "
     "сигнал на выводе порта.")
para("Конкретное задание (вариант 1): принять/передать, передача (T); режим порта K = 0 "
     "(синхронный); скорость обмена S = 1000 Кбит/с; начальный адрес данных в резидентной памяти "
     "XX = 50h; объём N = 10 байт. Передаваемые байты лежат в памяти 50h…59h, для проверки взят "
     "тестовый счётчик 00h…09h, на осциллографе такой код сразу видно.")

# ================= 2 =================
heading2("2. Особенности работы последовательного порта в режиме 0")
para("В МК-51 дуплексный порт с буфером SBUF (адрес 99h) работает в четырёх режимах. "
     "Режим задаётся битами SM0 (SCON.7) и SM1 (SCON.6): 00, режим 0, 01, режим 1, "
     "10, режим 2, 11, режим 3. Управление и состояние, регистр SCON (98h): флаги TI (SCON.1) "
     "и RI (SCON.0) ставит аппаратура, сбрасывает программа; бит REN (SCON.4) открывает приём; "
     "биты TB8/RB8 (SCON.3/2), девятый бит кадра в режимах 2 и 3; SM2 (SCON.5) в режиме 0 обязан "
     "быть сброшен.")
para("Режим 0, синхронный: кадр из 8 бит данных без старт- и стоп-битов. Данные идут по линии "
     "RxD (P3.0), синхроимпульсы, по TxD (P3.1). Каждый бит занимает один машинный цикл, младший "
     "бит уходит первым. Скорость фиксирована и зависит только от кварца:")
para("f0 = fосц / 12 (1)", indent=False, center=True)
para("При fосц = 12 МГц получается f0 = 1 МГц, то есть 1000 Кбит/с, бит, 1 мкс, байт, 8 мкс. "
     "Таймер-счётчик Т/С1 и бит SMOD регистра PCON (87h) в этом режиме на скорость не влияют, "
     "поэтому TMOD, TH1 и TL1 настраивать не нужно, частая ошибка переносить сюда настройки "
     "режимов 1 и 3. Для сравнения: в режиме 2 скорость тоже фиксирована (fосц/32 при SMOD=1 "
     "или fосц/64 при SMOD=0), а в режимах 1 и 3 её задаёт переполнение Т/С1 в режиме 2 "
     "(8-битный счётчик с автоперезагрузкой): f1,3 = (2^SMOD / 32) · (fосц / 12) / (256 − TH1).")
para("Передача начинается записью байта в SBUF (например, MOV SBUF, A). Через 8 машинных циклов "
     "аппаратура ставит флаг TI, это признак конца передачи. TI сам не сбрасывается, его гасит "
     "программа (CLR TI), иначе следующий байт не детектировать. Приём в режиме 0 открывается битом "
     "REN = 1 при сброшенном RI; готовность байта, установленный RI, чтение, MOV A, SBUF. "
     "Передатчик здесь нужен один, поэтому SCON = 00h (режим 0, SM2 = 0, REN = 0), "
     "а контроль ведётся опросом TI без прерываний: при байте за 8 мкс опрос проще и точнее, "
     "чем вектор 23h с накладными расходами на вход/выход.")
tblcap("Таблица 1 — Настройка порта для варианта 1")
table(["Параметр", "Значение", "Откуда"],
      [["Режим", "0 (синхронный, 8 бит)", "SM0=0, SM1=0 (SCON=00h)"],
       ["Кварц Y1", "12 МГц", "схема Circuit4"],
       ["Скорость", "1000 Кбит/с (1 МГц)", "12 МГц / 12"],
       ["Бит / байт", "1 мкс / 8 мкс", "машинный цикл 1 мкс"],
       ["Таймер Т/С1", "не используется", "особенность режима 0"],
       ["SMOD (PCON.7)", "безразлично (X)", "таблица 11 методички"],
       ["Приём (REN)", "запрещён (0)", "только передача"],
       ["Флаг TI", "опрос + сброс программой", "SCON.1"]])
para("Замечание о выводах. В методичке на странице режима 0 перепутаны подписи (написано "
     "«TxD (P3.0)», реально у 8051 P3.0, это RXD, а P3.1, TXD). В схеме это учтено: пробник XSC1 "
     "по заданию стоит на P3.0 (данные), а синхроимпульсы P3.1 выведены на второй пробник XSC2. "
     "Расхождение с методичкой зафиксировано осознанно, чтобы не ломать трассировку к рисунку 40.")

# ================= 3 =================
heading2("3. Схема моделирования (Circuit4)")
para("Проект Circuit4 собран в KiCad 10 (файлы Circuit4.kicad_sch / Circuit4.kicad_pro, формат листа A3). "
     "Состав повторяет рисунок 40 методички с добавлением индикации конца передачи:")
tblcap("Таблица 2 — Элементы схемы Circuit4")
table(["Поз.", "Компонент", "Номинал / корпус", "Цепь"],
      [["U1", "P8051AH (МК-51)", "DIP-40", "ядро схемы"],
       ["XSC1", "пробник осциллографа", "PinHeader 1×02", "пин 1 → P3.0, пин 2 → GND"],
       ["XSC2", "второй пробник (синхро)", "PinHeader 1×02", "пин 1 → P3.1, пин 2 → GND"],
       ["Y1, C1, C2", "кварц и нагрузка", "12 МГц + 2×33 пФ", "XTAL1 / XTAL2"],
       ["R2, C3", "цепь сброса", "10 кОм + 10 мкФ", "RST"],
       ["R1, D1", "индикация готовности", "330 Ом + LED", "P1.0 (TX_DONE)"],
       ["нет", "питание", "+5 В / GND + PWR_FLAG", "VCC, VSS, EA=+5 В"]])
para("Подключение по заданию: к выводу P3.0 (цепь P30_TXDATA) идёт первый канал пробника XSC1, "
     "второй контакт пробника, на землю, как на рисунке 40. Неиспользуемые цифровые выводы "
     "(P0, P2, часть P1/P3) закрыты маркерами no-connect, выводы ALE и /PSEN в этой задаче не нужны "
     "и тоже помечены как неподключенные, иначе контроль ERC ругается на висячие метки. "
     "Питание разведено через символы +5V/GND с флагами PWR_FLAG. Все координаты привязаны "
     "к сетке 1,27 мм, якоря меток стоят точно на концах проводов.")
para("Проверка KiCad ERC по схеме: 0 ошибок, 0 предупреждений (файл Circuit4-erc.rpt). "
     "Список цепей из netlist: P30_TXDATA (U1-10 + XSC1-1), P31_TXCLK (U1-11 + XSC2-1), "
     "XTAL1, XTAL2, RST, TX_DONE (U1 P1.0 + R1), LED_A, +5V, GND, всего 9 функциональных цепей. "
     "Дополнительная проверка показала: схема соответствует заданию, электрика в порядке, "
     "подписи U1/XSC1/XSC2 вынесены из-под корпусов и читаемы; по ГОСТ есть замечания "
     "(обозначения U1, XSC1/XSC2, D1 оставлены как в KiCad-библиотеке "
     "и в методичке ради трассировки; по строгому ГОСТ 2.710-81 это были бы DD1, PS1/PS2, HL1).")
if SCH_PNG.exists():
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Mm(0)
    p.add_run().add_picture(str(SCH_PNG), width=Mm(170))
    caption("Рисунок 1 — Схема Circuit4 во время моделирования (U1 — МК-51, XSC1 — пробник на P3.0)")
else:
    para("[Рисунок 1 отсутствует: out/Circuit4_schematic.png не найден]")
if CLOSEUP_PNG.exists():
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Mm(0)
    p.add_run().add_picture(str(CLOSEUP_PNG), width=Mm(150))
    caption("Рисунок 2 — Фрагмент схемы Circuit4 крупным планом (U1, XSC1/XSC2, Y1, R1/D1 читаемы)")

# ================= 4 =================
heading2("4. Программа передачи (ассемблер и C)")
para("Оба варианта делают одно и то же: настраивают SCON = 00h, циклом выдают 10 байт из памяти "
     "с 50h через SBUF с ожиданием TI и в конце зажигают светодиод на P1.0. Ниже, полный текст "
     "ассемблерного варианта (файл prog/prog4_var1_tx_mode0.asm), он основной для сдачи:")
code_block(ROOT / "prog" / "prog4_var1_tx_mode0.asm")
para("Как это работает по шагам. Инициализация: гасятся TI/RI, в SCON пишется 00h, тем самым "
     "выбран режим 0 и закрыт приём. Указатель R0 ставится на 50h, счётчик R2 на 10. Тело цикла: "
     "байт забирается из памяти (MOV A, @R0), флаг TI чистится, байт кладётся в SBUF, с этого такта "
     "аппаратура выдвигает биты на P3.0 под синхроимпульсы P3.1. Цикл ожидания JNB TI занимает "
     "около 8 мкс, затем TI гасится, указатель и счётчик обновляются. После десятого байта "
     "P1.0 ставится в единицу, ток через R1 330 Ом зажигает D1. Прерывания не используются: "
     "при такой скорости опрос флага короче обработчика вектора 23h.")
para("Вариант на C (файл prog/prog4_var1_tx_mode0.c) повторяет ту же логику функцией tput_mode0: "
     "TI = 0; SBUF = c; while (!TI); TI = 0. Массив tx[10] = {00h…09h} играет роль памяти с 50h. "
     "Заголовок <8051.h>, как в примере методички. Этот вариант приложен как второй, рабочий; "
     "сдаётся любой из двух, ассемблерный, основной.")
code_block(ROOT / "prog" / "prog4_var1_tx_mode0.c")

# ================= 5 =================
heading2("5. Результаты и выводы")
para("Расчёт времени (модель sim/test_serial_mode0.py, результат out/serial_results.json): бит, 1 мкс, "
     "байт, 8 мкс, все 10 байт, 80 мкс без учёта единиц тактов на цикл опроса. Проверка утверждением "
     "в скрипте: f0 обязана равняться 1 МГц, N обязано равняться 10, оба сошлись (статус PASS).")
tblcap("Таблица 3 — Временные параметры передачи (12 МГц, режим 0)")
table(["Величина", "Значение"],
      [["Частота кварца", "12 МГц"],
       ["Скорость порта", "1000 Кбит/с"],
       ["Длительность бита", "1 мкс"],
       ["Длительность байта", "8 мкс"],
       ["Объём", "10 байт (50h…59h)"],
       ["Чистое время выдачи", "80 мкс"],
       ["Сигнал готовности", "P1.0 = 1, LED D1 горит"]])
if WAVE_PNG.exists():
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Mm(0)
    p.add_run().add_picture(str(WAVE_PNG), width=Mm(150))
    caption("Рисунок 3 — Модель осциллограммы: P3.0 (данные 00h…09h, младший бит первым) и P3.1 (синхро)")
para("Что видно на модели: байт 00h, ровный ноль все 8 мкс, дальше код нарастает (01h даёт единичный "
     "импульс в первом бите, 02h, во втором и так далее). Синхроимпульсы P3.1 идут каждый бит, "
     "по ним внешний сдвиговый регистр забирал бы данные. Именно такую картину должен показать "
     "осциллограф XSC1 на P3.0 при запуске программы.")
para("Режим 0 закрыл вариант 1 вообще без таймера: при кварце 12 МГц порт сам даёт ровно "
     "1 МГц, так что вся настройка, одна строка MOV SCON, #00h. Главный подвох тут, флаг TI: "
     "аппаратура его ставит, а гасить приходится вручную после каждого байта, иначе передача "
     "встанет на первом же. Опрос вместо прерываний взят осознанно: байт уходит за 8 мкс, "
     "обработчик стоил бы почти столько же, а мороки с ним больше. Схема сошлась с первого "
     "прогона ERC, без ошибок. От ГОСТ 2.710-81 отошли в одном месте, обозначения U1, XSC1/XSC2 "
     "и D1 оставлены как в библиотеке KiCad и на рисунке 40 методички, чтобы схему можно было "
     "сличить с заданием один в один; строгие DD1, PS1/PS2 и HL1 здесь только запутали бы. "
     "Сошлось всё: схема, обе программы с комментариями, расчёт времени и осциллограмма.")

heading2("Список использованных источников")
for src in ["Практическая работа № 4 «Основы организации последовательного порта», методичка кафедры (таблица 11, 12, рисунок 38-40).",
            "MCS-51 Microcontroller Family User's Manual, Intel (SBUF 99h, SCON 98h, PCON 87h, режим 0: f0 = fosc/12).",
            "ГОСТ 2.701-2008, ГОСТ 2.702-2011, ГОСТ 2.710-81 — правила выполнения схем и буквенно-цифровые обозначения.",
            "ГОСТ 7.32-2017 — оформление отчётов о научно-исследовательских работах.",
            "KiCad 10 Eeschema / kicad-cli sch erc, export svg/netlist, проверка и экспорт схемы Circuit4.",
            "Файлы проекта: Circuit4.kicad_sch, prog/prog4_var1_tx_mode0.asm, prog/prog4_var1_tx_mode0.c, sim/test_serial_mode0.py, out/serial_results.json."]:
    p = d.add_paragraph(src, style="List Number")
    p.paragraph_format.first_line_indent = Mm(0)
    for r in p.runs:
        r.font.size = Pt(14); r.font.name = "Times New Roman"

add_page_number()
d.save(str(OUT))
print(f"OK: {OUT}")
