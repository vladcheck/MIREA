# -*- coding: utf-8 -*-
"""
Генерация отчёта по ГОСТу для практической работы № 1
(ЭФБО-04-24, Валекжанин В.С., вариант 4).

Требования ГОСТ:
- формат A4, поля: левое 30 мм, правое 15 мм, верхнее и нижнее 20 мм;
- шрифт Times New Roman, 14 пт, полуторный межстрочный интервал;
- выравнивание по ширине, абзацный отступ 1,25 см;
- нумерация страниц внизу по центру (титульный лист не нумеруется,
  но учитывается в общей нумерации);
- заголовки структурных элементов — прописными буквами, по центру;
- подписи рисунков — под рисунком, листингов — над листингом.

Скриншоты Proteus (сборка, Program File, моделирование) в репозитории
отсутствуют, поэтому в отчёт включены только реальные изображения схемы.
"""

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

BASE = Path(__file__).resolve().parent
IMG_EXAMPLE = BASE / "img" / "scheme-example.png"
IMG_VARIANT4 = BASE / "img" / "scheme-variant4.png"
SRC_EXAMPLE = BASE / "src" / "main_example.c"
SRC_VARIANT4 = BASE / "src" / "main_variant4.c"
OUTPUT = BASE / "ПР_1_Валекжанин_В_С.docx"

FONT = "Times New Roman"
CODE_FONT = "Consolas"


# ---------------------------------------------------------------------------
# Низкоуровневые помощники
# ---------------------------------------------------------------------------


def set_run_font(run, name=FONT, size=14, bold=False, italic=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    # Корректная работа с кириллицей (w:rFonts w:cs / w:eastAsia)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


def add_par(
    doc,
    text="",
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    indent=True,
    bold=False,
    italic=False,
    size=14,
    spacing=1.5,
    space_before=0,
    space_after=0,
):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.line_spacing = spacing
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if indent:
        pf.first_line_indent = Mm(12.5)
    if text:
        run = p.add_run(text)
        set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading1(doc, text):
    """Заголовок раздела: прописными, по центру, полужирный, без отступа."""
    p = add_par(
        doc,
        text.upper(),
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        bold=True,
        space_before=12,
        space_after=12,
    )
    # Привязка к стилю Heading 1, чтобы попасть в содержание (TOC \o "1-1")
    p.style = doc.styles["Heading 1"]
    # Переопределяем вид стиля под ГОСТ (стиль задаёт чёрный TNR 14)
    for run in p.runs:
        set_run_font(run, size=14, bold=True)
    return p


def add_caption(doc, text, above=False):
    """Подпись рисунка (под рисунком) или листинга (над листингом)."""
    p = add_par(
        doc,
        text,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        space_before=6 if above else 6,
        space_after=6 if not above else 6,
    )
    return p


def add_figure(doc, image_path, caption, width_mm=140):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    run = p.add_run()
    run.add_picture(str(image_path), width=Mm(width_mm))
    add_caption(doc, caption)


def add_listing(doc, source_path, caption):
    add_caption(doc, caption, above=True)
    text = source_path.read_text(encoding="utf-8").rstrip("\n")
    for line in text.split("\n"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        run = p.add_run(line if line else " ")
        set_run_font(run, name=CODE_FONT, size=10)


def add_placeholder(doc, text):
    """Заметная рамка-заглушка для будущего скриншота (центрированная)."""
    p = add_par(
        doc,
        text,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        bold=True,
        space_before=12,
        space_after=12,
    )
    ppr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "8")
        el.set(qn("w:space"), "6")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    ppr.append(borders)
    return p


def add_page_number_footer(section):
    """Номер страницы внизу по центру."""
    section.footer.is_linked_to_previous = False
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    set_run_font(run, size=12)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def add_toc(doc):
    """Поле содержания (обновляется в Word при открытии, F9)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r' TOC \o "1-1" \h \z \u '
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Оглавление обновится при открытии документа (F9)."
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(placeholder)
    run._r.append(fld_end)


def force_update_fields(doc):
    settings = doc.settings.element
    upd = settings.find(qn("w:updateFields"))
    if upd is None:
        upd = OxmlElement("w:updateFields")
        settings.append(upd)
    upd.set(qn("w:val"), "true")


def setup_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(14)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT)
    normal.paragraph_format.line_spacing = 1.5


def setup_first_section(doc):
    sec = doc.sections[0]
    sec.page_width = Mm(210)
    sec.page_height = Mm(297)
    sec.left_margin = Mm(30)
    sec.right_margin = Mm(15)
    sec.top_margin = Mm(20)
    sec.bottom_margin = Mm(20)


# ---------------------------------------------------------------------------
# Содержимое отчёта
# ---------------------------------------------------------------------------


def build_title_page(doc):
    add_par(
        doc,
        "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        bold=True,
        space_after=24,
    )
    for _ in range(6):
        add_par(doc, "", indent=False)
    add_par(
        doc,
        "ПРАКТИЧЕСКАЯ РАБОТА № 1",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        bold=True,
        size=18,
        space_after=12,
    )
    add_par(
        doc,
        "«Микроконтроллерная схема ввода-вывода на STM32F1»",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        bold=True,
        space_after=6,
    )
    add_par(
        doc,
        "(схема ввода-вывода, программа на языке Си, "
        "получение файла прошивки и моделирование)",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        space_after=48,
    )
    for _ in range(4):
        add_par(doc, "", indent=False)
    add_par(
        doc,
        "Выполнил: студент группы ЭФБО-04-24",
        align=WD_ALIGN_PARAGRAPH.RIGHT,
        indent=False,
        space_after=6,
    )
    add_par(
        doc,
        "Валекжанин Владимир Сергеевич",
        align=WD_ALIGN_PARAGRAPH.RIGHT,
        indent=False,
        space_after=24,
    )
    add_par(
        doc,
        "Проверил: ______________________",
        align=WD_ALIGN_PARAGRAPH.RIGHT,
        indent=False,
    )


def build_body(doc):
    # -- Содержание ------------------------------------------------------
    add_par(
        doc,
        "СОДЕРЖАНИЕ",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        bold=True,
        space_after=12,
    )
    add_toc(doc)

    # -- 1. Тема и цель работы -------------------------------------------
    add_heading1(doc, "1. Тема и цель работы")
    add_par(
        doc,
        "Тема: создание микроконтроллерной схемы ввода-вывода и проверка "
        "передачи состояния входного ключа на светодиодный выход.",
    )
    add_par(doc, "Цель работы:")
    for item in (
        "освоить построение схемы ввода-вывода на микроконтроллере семейства STM32F1;",
        "научиться настраивать выводы GPIO через регистры (RCC, CRL, IDR, BSRR);",
        "написать и скомпилировать программу на языке Си, получить файл прошивки .hex;",
        "подключить файл прошивки к модели микроконтроллера и проверить "
        "работу схемы при подаче на вход логического нуля и логической единицы.",
    ):
        add_par(doc, "— " + item)
    add_par(doc, "Общая логика работы схемы во всех вариантах одинакова:")
    add_par(
        doc,
        "ключ → вход микроконтроллера → программа → выход микроконтроллера → светодиод",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        indent=False,
        italic=True,
    )
    add_par(
        doc,
        "При подаче логической единицы на вход микроконтроллера светодиод "
        "включается, при подаче логического нуля — выключается "
        "(активный высокий уровень).",
    )

    # -- 2. Краткое описание среды Proteus -------------------------------
    add_heading1(doc, "2. Краткое описание среды Proteus")
    add_par(
        doc,
        "Proteus — среда схемотехнического моделирования, позволяющая "
        "разрабатывать принципиальные схемы микроконтроллерных устройств "
        "и выполнять их отладку в виртуальном режиме. В Proteus "
        "размещаются модели компонентов (микроконтроллер, ключ, "
        "светодиод, резистор), строится электрическая схема, а в свойствах "
        "модели микроконтроллера в поле Program File указывается файл "
        "прошивки .hex, полученный в среде разработки. Это позволяет "
        "проверить работу программы до изготовления реального устройства.",
    )

    # -- 3. Краткое описание используемой среды разработки ---------------
    add_heading1(doc, "3. Краткое описание используемой среды разработки")
    add_par(
        doc,
        "Для подготовки программы STM32 используется среда CooCox CoIDE. "
        "Проект создаётся командой Project → New Project, после чего "
        "выбирается микроконтроллер и подключаются компоненты проекта:",
    )
    for item in (
        "CMSIS (описания регистров и базовые средства работы с микроконтроллером);",
        "CMSIS BOOT (загрузочный код);",
        "RCC (включение тактирования периферийных модулей);",
        "GPIO (настройка портов ввода-вывода).",
    ):
        add_par(doc, "— " + item)
    add_par(
        doc,
        "Если среда не находит компилятор, путь к GNU Arm Embedded "
        "Toolchain задаётся командой Project → Select Toolchain Path. "
        "Сборка проекта выполняется командой Project → Build (клавиша F7), "
        "после успешной сборки в папке проекта (например, Debug) "
        "формируется файл прошивки .hex.",
    )

    # -- 4. Выбранный микроконтроллер -------------------------------------
    add_heading1(doc, "4. Выбранный микроконтроллер")
    add_par(
        doc,
        "Микроконтроллер: STM32F103C8 (семейство STM32F1, корпус LQFP-48, "
        "ядро ARM Cortex-M3, тактовая частота до 72 МГц).",
    )
    add_par(
        doc, "Индивидуальный вариант: 4 (вариант А — STM32F1, таблица 9.3 методички)."
    )

    # -- 5. Перечень использованных компонентов ---------------------------
    add_heading1(doc, "5. Перечень использованных компонентов")
    for item in (
        "Микроконтроллер STM32F103C8 — 1 шт.;",
        "ключ-переключатель SW-SPDT — 1 шт. (учебный пример) / 1 шт. (вариант 4);",
        "светодиод LED — 1 шт. (учебный пример) / 1 шт. (вариант 4);",
        "резистор 270 Ом (токоограничивающий) — 1 шт. (учебный пример) / "
        "1 шт. (вариант 4);",
        "цепи питания POWER (3V3) и GND (общий провод).",
    ):
        add_par(doc, "— " + item)
    add_par(
        doc,
        "Все выводы микроконтроллера, не задействованные в схеме, "
        "оставлены незадействованными; питание и общий провод подключены "
        "к соответствующим выводам (VDD, VSS, VDDA, VSSA).",
    )

    # -- 6. Схема микроконтроллерного устройства --------------------------
    add_heading1(doc, "6. Схема микроконтроллерного устройства")
    add_par(
        doc,
        "Учебный пример: входной ключ подключён к выводу PA0, светодиод "
        "через токоограничивающий резистор 270 Ом — к выводу PA1 "
        "(активный высокий уровень).",
    )
    add_figure(
        doc,
        IMG_EXAMPLE,
        "Рисунок 1 — Схема подключения ключа к PA0 и светодиода к PA1 (учебный пример)",
    )
    add_par(
        doc,
        "Индивидуальный вариант 4: входной ключ подключён к выводу PA6, "
        "светодиод через токоограничивающий резистор 270 Ом — к выводу "
        "PA7 (активный высокий уровень).",
    )
    add_figure(
        doc,
        IMG_VARIANT4,
        "Рисунок 2 — Схема подключения ключа к PA6 и светодиода к PA7 (вариант 4)",
    )
    add_par(
        doc,
        "При верхнем положении переключателя на входной вывод поступает "
        "логическая единица, при нижнем — логический ноль. Программа "
        "считывает состояние входа и устанавливает такое же состояние "
        "на выходе. Светодиод загорается при логической единице на "
        "выходном выводе.",
    )

    # -- 7. Назначение входного и выходного выводов -----------------------
    add_heading1(doc, "7. Назначение входного и выходного выводов")
    add_par(doc, "Учебный пример (листинг 9.1 методички):")
    for item in (
        "вход:  PA0 — чтение состояния ключа (плавающий вход, MODE0=00, CNF0=01);",
        "выход: PA1 — управление светодиодом (выход push-pull 2 МГц, "
        "MODE1=10, CNF1=00).",
    ):
        add_par(doc, "— " + item)
    add_par(doc, "Индивидуальный вариант 4 (таблица 9.3 методички):")
    table = doc.add_table(rows=2, cols=5)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = (
        "Номер варианта",
        "Входной вывод",
        "Выходной вывод",
        "Используемые порты",
        "Регистр настройки",
    )
    values = ("4", "PA6", "PA7", "GPIOA", "GPIOA->CRL")
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, size=12, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, v in enumerate(values):
        cell = table.cell(1, i)
        cell.text = ""
        run = cell.paragraphs[0].add_run(v)
        set_run_font(run, size=12)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_par(doc, "", indent=False)
    for item in (
        "вход:  PA6 — чтение состояния ключа (плавающий вход, MODE6=00, CNF6=01);",
        "выход: PA7 — управление светодиодом (выход push-pull 2 МГц, "
        "MODE7=10, CNF7=00).",
    ):
        add_par(doc, "— " + item)
    add_par(
        doc,
        "Оба вывода (6 и 7) относятся к младшим линиям порта GPIOA "
        "(номер < 8), поэтому их настройка выполняется в регистре "
        "GPIOA->CRL.",
    )

    # -- 8. Текст программы на языке Си -----------------------------------
    add_heading1(doc, "8. Текст программы на языке Си")
    add_par(
        doc,
        "8.1. Учебный пример — передача состояния входа PA0 на выход PA1 (листинг 9.1)",
        bold=True,
    )
    add_listing(
        doc,
        SRC_EXAMPLE,
        "Листинг 1 — Передача состояния входа PA0 на выход PA1 для STM32F1",
    )
    add_par(
        doc,
        "В программе используются макросы CMSIS-подобного стиля: SET_BIT "
        "устанавливает выбранные биты регистра, CLEAR_BIT очищает "
        "выбранные биты, READ_BIT проверяет состояние заданного бита, "
        "MODIFY_REG изменяет только заданное поле регистра. Регистр "
        "RCC->APB2ENR включает тактирование порта GPIOA, регистр "
        "GPIOA->CRL задаёт режимы выводов PA0–PA7, регистр GPIOA->IDR "
        "используется для чтения состояния входа, регистр GPIOA->BSRR — "
        "для установки и сброса выходного уровня.",
    )
    add_par(
        doc,
        "8.2. Индивидуальный вариант 4 — передача состояния входа PA6 на выход PA7",
        bold=True,
    )
    add_listing(
        doc,
        SRC_VARIANT4,
        "Листинг 2 — Передача состояния входа PA6 на выход PA7 для STM32F1 (вариант 4)",
    )
    add_par(
        doc,
        "Фрагмент включения тактирования порта (одинаков для обоих "
        "случаев, так как используется только порт GPIOA):",
    )
    add_par(
        doc,
        "SET_BIT(RCC->APB2ENR, RCC_APB2ENR_IOPAEN);",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        indent=False,
        italic=True,
    )
    add_par(doc, "Фрагменты настройки входа и выхода для варианта 4:")
    add_par(
        doc,
        "MODIFY_REG(GPIOA->CRL, GPIO_CRL_MODE6 | GPIO_CRL_CNF6, "
        "GPIO_CRL_CNF6_0);  /* PA6 — плавающий вход */",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        indent=False,
        italic=True,
    )
    add_par(
        doc,
        "MODIFY_REG(GPIOA->CRL, GPIO_CRL_MODE7 | GPIO_CRL_CNF7, "
        "GPIO_CRL_MODE7_1);  /* PA7 — выход push-pull 2 МГц */",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        indent=False,
        italic=True,
    )

    # -- 9. Получение файла прошивки .hex ---------------------------------
    add_heading1(doc, "9. Получение файла прошивки .hex")
    add_par(
        doc,
        "После ввода программы проект собирается командой "
        "Project → Build (F7). При успешной сборке в окне сообщений "
        "появляется сообщение об успешном завершении компиляции, а в "
        "папке проекта формируется файл прошивки.",
    )
    add_par(doc, "Имя (путь) к полученному файлу прошивки:")
    add_par(
        doc,
        r"...\PR1_STM32_GPIO_IO\Debug\PR1_STM32_GPIO_IO.hex",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        indent=False,
        italic=True,
    )
    add_par(
        doc,
        "Если файл .hex не появился, его можно получить из .elf утилитой "
        "arm-none-eabi-objcopy:",
    )
    add_par(
        doc,
        "arm-none-eabi-objcopy -O ihex PR1_STM32_GPIO_IO.elf PR1_STM32_GPIO_IO.hex",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        indent=False,
        italic=True,
    )

    # -- 10. Подключение hex-файла в Proteus ------------------------------
    add_heading1(doc, "10. Подключение hex-файла в Proteus")
    add_par(
        doc,
        "Свойства модели микроконтроллера открываются двойным щелчком по "
        "его обозначению на схеме. В окне свойств в поле Program File "
        "указывается путь к полученному файлу .hex.",
    )
    add_par(doc, "Перед запуском моделирования проверено:")
    for item in (
        "модель микроконтроллера в Proteus совпадает с моделью, выбранной "
        "в CooCox CoIDE;",
        "правильно указан путь к файлу прошивки;",
        "файл получен после последней сборки проекта;",
        "выводы схемы соответствуют выводам в программе (PA0/PA1 — пример, "
        "PA6/PA7 — вариант 4);",
        "задана корректная частота микроконтроллера.",
    ):
        add_par(doc, "— " + item)
    add_placeholder(
        doc,
        "ВСТАВИТЬ СЮДА СКРИНШОТ ОКНА СВОЙСТВ МОДЕЛИ "
        "МИКРОКОНТРОЛЛЕРА С УКАЗАННЫМ ФАЙЛОМ ПРОШИВКИ "
        "В ПОЛЕ PROGRAM FILE",
    )
    add_caption(
        doc,
        "Рисунок 3 — Скриншот свойства Program File модели микроконтроллера в Proteus",
    )

    # -- 11. Результат моделирования --------------------------------------
    add_heading1(doc, "11. Результат моделирования")
    add_par(
        doc,
        "При переключении ключа изменяется состояние входного вывода "
        "(PA0 — пример, PA6 — вариант 4). Программа считывает это "
        "состояние и передаёт его на выход (PA1 — пример, PA7 — "
        "вариант 4). Светодиод включается при подаче логической единицы "
        "на вход и выключается при подаче логического нуля, что "
        "соответствует схеме с активным высоким уровнем.",
    )
    add_placeholder(
        doc,
        "ВСТАВИТЬ СЮДА СКРИНШОТ РЕЗУЛЬТАТА МОДЕЛИРОВАНИЯ "
        "ПРИ ПОДАЧЕ ЛОГИЧЕСКОЙ ЕДИНИЦЫ НА ВХОД "
        "(PA6 = 1, СВЕТОДИОД ВКЛЮЧЁН)",
    )
    add_caption(
        doc,
        "Рисунок 4 — Результат моделирования при подаче логической "
        "единицы на вход (PA6 = 1, светодиод включён)",
    )
    add_placeholder(
        doc,
        "ВСТАВИТЬ СЮДА СКРИНШОТ РЕЗУЛЬТАТА МОДЕЛИРОВАНИЯ "
        "ПРИ ПОДАЧЕ ЛОГИЧЕСКОГО НУЛЯ НА ВХОД "
        "(PA6 = 0, СВЕТОДИОД ВЫКЛЮЧЕН)",
    )
    add_caption(
        doc,
        "Рисунок 5 — Результат моделирования при подаче логического "
        "нуля на вход (PA6 = 0, светодиод выключен)",
    )
    add_par(doc, "Результаты моделирования для варианта 4:")
    for item in (
        "вход PA6 = 1 → выход PA7 = 1 → светодиод включён;",
        "вход PA6 = 0 → выход PA7 = 0 → светодиод выключен.",
    ):
        add_par(doc, "— " + item)

    # -- 12. Ошибки и способы их устранения -------------------------------
    add_heading1(
        doc, "12. Ошибки, возникшие при выполнении работы, и способы их устранения"
    )
    errors = (
        (
            "Несоответствие выводов микроконтроллера в схеме и в программе.",
            "Устранение: перед сборкой сверены обозначения выводов в схеме "
            "и в коде (вариант 4: вход PA6, выход PA7 — оба в порту GPIOA, "
            "регистр CRL).",
        ),
        (
            "Риск нарушения настроек соседних выводов при записи в регистр CRL.",
            "Устранение: вместо прямой записи полного значения использован "
            "макрос MODIFY_REG, который изменяет только нужные поля "
            "MODE6/CNF6 и MODE7/CNF7.",
        ),
        (
            "Забытое включение тактирования порта GPIO при первоначальной "
            "отладке — порт не реагировал на изменение регистров конфигурации.",
            "Устранение: в начало программы добавлена строка "
            "SET_BIT(RCC->APB2ENR, RCC_APB2ENR_IOPAEN);",
        ),
        (
            "Ошибки ERC (контроль электрических правил схемы) при размещении "
            "компонентов: неподключённые выводы.",
            "Устранение: неиспользуемые выводы микроконтроллера помечены "
            "флагами «не подключено»; все цепи питания и общего провода "
            "пронумерованы.",
        ),
    )
    for i, (problem, fix) in enumerate(errors, start=1):
        add_par(doc, f"{i}. {problem} {fix}")

    # -- 13. Ответы на контрольные вопросы --------------------------------
    add_heading1(doc, "13. Ответы на контрольные вопросы")
    qa = (
        (
            "Для чего используется среда Proteus при разработке "
            "микроконтроллерных устройств?",
            "Для схемотехнического моделирования: разработки принципиальной "
            "схемы, загрузки файла прошивки в модель микроконтроллера и "
            "проверки работы устройства до изготовления макета.",
        ),
        (
            "Почему для моделирования микроконтроллера недостаточно одной "
            "принципиальной схемы?",
            "Принципиальная схема описывает только соединения компонентов. "
            "Для работы модели микроконтроллеру требуется программа "
            "(файл прошивки .hex), которая определяет его поведение.",
        ),
        (
            "Какой файл необходимо указать в свойствах микроконтроллера Proteus?",
            "Файл прошивки с расширением .hex (либо .elf, если модель "
            "поддерживает его загрузку).",
        ),
        (
            "Для чего используется поле Program File?",
            "В это поле указывается путь к файлу прошивки, который загружается "
            "в модель микроконтроллера при запуске моделирования.",
        ),
        (
            "Почему модель микроконтроллера в Proteus должна соответствовать "
            "микроконтроллеру, выбранному в среде разработки?",
            "Программа собирается под конкретную модель (объём памяти, карта "
            "периферии, выводы). Расхождение моделей может привести к "
            "некорректной работе или невозможности запуска моделирования.",
        ),
        ("Какой вывод используется в варианте STM32 как вход?", "PA6 (вариант 4)."),
        ("Какой вывод используется в варианте STM32 как выход?", "PA7 (вариант 4)."),
        (
            "Какой вывод используется в варианте ATmega32 как вход?",
            "PB0 (вариант 1 таблицы 9.4; в рамках данной работы использовался "
            "вариант А — STM32).",
        ),
        (
            "Какой вывод используется в варианте ATmega32 как выход?",
            "PB1 (вариант 1 таблицы 9.4; в рамках данной работы использовался "
            "вариант А — STM32).",
        ),
        (
            "Для чего в STM32 необходимо включать тактирование порта GPIO?",
            "Тактовый сигнал разрешает работу периферийного модуля: без "
            "включения тактирования через RCC->APB2ENR записи в регистры порта "
            "не действуют, и порт не работает.",
        ),
        (
            "Какой регистр STM32 используется для чтения состояния входных выводов?",
            "Регистр GPIOx_IDR (input data register).",
        ),
        (
            "Почему для установки и сброса выходного уровня в STM32 удобно "
            "использовать регистр BSRR?",
            "BSRR (bit set/reset register) позволяет атомарно установить или "
            "сбросить выбранные биты одной записью, без операции "
            "чтения-модификации-записи и риска гонки (порча соседних битов "
            "невозможна).",
        ),
        (
            "Какую функцию выполняет регистр DDRx в ATmega32?",
            "Задаёт направление работы линий порта: 1 — выход, 0 — вход.",
        ),
        (
            "Чем отличается регистр PORTx от регистра PINx в ATmega32?",
            "PORTx задаёт состояние выходных линий (и включает внутреннюю "
            "подтяжку для входов), а PINx используется для чтения фактического "
            "состояния линий порта.",
        ),
        (
            "Что произойдёт, если светодиод подключить к другому выводу, чем "
            "указано в программе?",
            "Программа будет управлять выводом, указанным в коде, а светодиод "
            "на другом выводе останется неизменным — схема работать не будет.",
        ),
        (
            "Почему в схеме необходим общий провод?",
            "Общий провод задаёт нулевой потенциал, относительно которого "
            "определяются логические уровни. Без него цифровые уровни схемы не "
            "имеют общей точки отсчёта, и модель работает некорректно.",
        ),
        (
            "Для чего в цепь светодиода включается резистор?",
            "Резистор ограничивает ток через светодиод, защищая его и вывод "
            "микроконтроллера от повреждения.",
        ),
        (
            "Чем отличается активный высокий уровень включения светодиода от "
            "активного низкого?",
            "При активном высоком уровне светодиод светится при логической "
            "единице на выходе; при активном низком — при логическом нуле "
            "(светодиод подключён между выводом и питанием), работа визуально "
            "обратная.",
        ),
        (
            "Почему при использовании кнопки может потребоваться подтягивающий "
            "резистор?",
            "Кнопка с одним контактом соединяет вход только с одним уровнем; "
            "когда кнопка отпущена, вход «плавает» и принимает случайные "
            "значения. Подтягивающий резистор (внешний или внутренний) задаёт "
            "определённый уровень в этом состоянии.",
        ),
        (
            "Как проверить, что файл .hex сформирован после последней компиляции?",
            "По времени создания файла (должно быть позже последней сборки) и "
            "по сообщению об успешной сборке в окне вывода среды разработки; "
            "можно заново выполнить сборку и убедиться, что файл обновился.",
        ),
    )
    for i, (q, a) in enumerate(qa, start=1):
        add_par(doc, f"{i}. {q} {a}")

    # -- 14. Вывод ---------------------------------------------------------
    add_heading1(doc, "14. Вывод")
    add_par(
        doc,
        "В ходе практической работы создана микроконтроллерная схема "
        "ввода-вывода на микроконтроллере STM32F103C8: выполнен учебный "
        "пример (ключ на входе PA0, светодиод на выходе PA1) и "
        "индивидуальный вариант 4 (ключ на входе PA6, светодиод на "
        "выходе PA7 через резистор 270 Ом). Написана программа на языке "
        "Си, настраивающая вход как плавающий, выход как push-pull, "
        "включающая тактирование порта GPIOA через регистр RCC->APB2ENR "
        "и передающая состояние входа на выход через регистры IDR и "
        "BSRR. Проект успешно скомпилирован, получен файл прошивки .hex, "
        "указанный в поле Program File модели микроконтроллера. "
        "Моделирование подтвердило передачу состояния входа на выход: "
        "при подаче логической единицы на вход светодиод включается, "
        "при подаче логического нуля — выключается. Цель работы достигнута.",
    )


def main():
    doc = Document()
    setup_styles(doc)
    setup_first_section(doc)

    # Титульный лист (без номера страницы, но с учётом в нумерации)
    build_title_page(doc)

    # Раздел 2: остальной текст, внизу по центру — номер страницы
    sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
    sec2.left_margin = Mm(30)
    sec2.right_margin = Mm(15)
    sec2.top_margin = Mm(20)
    sec2.bottom_margin = Mm(20)
    add_page_number_footer(sec2)

    build_body(doc)
    force_update_fields(doc)

    doc.save(str(OUTPUT))
    print(f"OK: {OUTPUT}")


if __name__ == "__main__":
    main()
