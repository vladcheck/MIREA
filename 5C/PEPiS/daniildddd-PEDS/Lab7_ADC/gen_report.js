const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, HeadingLevel, AlignmentType, ImageRun, PageBreak,
  Footer, PageNumber, LineRuleType } = require('docx');

const F = 'Times New Roman';
const BLACK = '000000';
const SZ = 28; // 14pt in half-points
const SZs = 28; // 14pt tables
const SZxs = 28; // 14pt wide tables
const DXA_FULL = 9360; // ~163mm usable
const BODY_SPACING = { after: 120, line: 360, lineRule: LineRuleType.AUTO }; // 1.5 интервал
const INDENT_125 = { firstLine: 708 }; // абзацный отступ 1,25 см

function p(text, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    heading: opts.heading,
    indent: INDENT_125,
    children: [new TextRun({ text, font: F, size: opts.size || SZ, bold: !!opts.bold, italics: !!opts.italic, color: BLACK })],
    spacing: BODY_SPACING,
  });
}
function pc(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text, font: F, size: opts.size || SZ, bold: !!opts.bold, color: BLACK })],
    spacing: { after: 120 },
  });
}
function code(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    children: [new TextRun({ text: text === '' ? ' ' : text, font: 'Courier New', size: 22, color: BLACK })],
    spacing: { after: 0, line: 276 },
  });
}
function pright(text, opts = {}) {  return new Paragraph({
    alignment: AlignmentType.RIGHT,
    children: [new TextRun({ text, font: F, size: opts.size || SZ, bold: !!opts.bold, color: BLACK })],
    spacing: { after: 120 },
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, font: F, size: 32, bold: true, color: BLACK })],
    spacing: { after: 120 },
    pageBreakBefore: true,
  });
}
// Подпись таблицы, слева НАД таблицей (ГОСТ 7.32)
function tcap(text) {
  return new Paragraph({
    alignment: AlignmentType.LEFT,
    children: [new TextRun({ text, font: F, size: SZ, color: BLACK })],
    spacing: { after: 120 },
  });
}
// Выключная формула по центру с номером справа
function formula(text, num) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `${text}                                          (${num})`, font: F, size: SZ, color: BLACK })],
    spacing: { after: 120 },
  });
}
// widths: array of DXA summing to DXA_FULL; size: half-points
function tblW(headers, rows, widths, size = SZs) {
  const mk = (r, bold) => new TableRow({
    children: r.map((t, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: String(t), font: F, size, bold, color: BLACK })] })],
    })),
  });
  return new Table({
    width: { size: DXA_FULL, type: WidthType.DXA },
    columnWidths: widths,
    rows: [mk(headers, true), ...rows.map(r => mk(r, false))],
  });
}
function tbl(headers, rows) {
  const n = headers.length;
  const cw = Math.floor(DXA_FULL / n);
  const widths = headers.map((_, i) => (i === n - 1 ? DXA_FULL - cw * (n - 1) : cw));
  return tblW(headers, rows, widths, SZs);
}
function imgPara(path, w, h, caption) {
  const data = fs.readFileSync(path);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: 'png', data, transformation: { width: w, height: h } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: caption, font: F, size: SZ, italics: true, color: BLACK })], spacing: { after: 120 } }),
  ];
}

const C = [];
const push = (...xs) => C.push(...xs);

// ---------- Титульный лист (после regen: python3 ../tmp/shift_titles.py, центровка титула: поля 30/15 уводят центр вправо) (единый для всех работ: отличается только тема/вариант) ----------
push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: 'jpg', data: fs.readFileSync('logo.jpg'), transformation: { width: 151, height: 171 } })] }));
push(pc('МИНОБРНАУКИ РОССИИ', { size: 24 }));
push(pc('Федеральное государственное бюджетное образовательное учреждение высшего образования', { size: 24 }));
push(pc('«МИРЭА – Российский технологический университет»', { bold: true }));
push(pc('РТУ МИРЭА', { bold: true }));
push(pc('Институт перспективных технологий и индустриального программирования', { size: 24 }));
push(pc('Кафедра индустриального программирования', { size: 24 }));
push(p('', {}));
push(pc('ОТЧЁТ ПО ЛАБОРАТОРНОЙ РАБОТЕ № 7', { bold: true }));
push(pc('по дисциплине «Программирование электронных приборов и систем»', { size: 24 }));
push(pc('НАПРАВЛЕНИЕ ПОДГОТОВКИ', { bold: true, size: 24 }));
push(pc('09.03.02 «Информационные системы и технологии»', { size: 24 }));
push(p('', {}));
push(pc('Тема: Изучение принципов работы аналого-цифровых преобразователей', { bold: true }));
push(pc('Вариант 1: АЦП 8 разрядов, Eref1 = +2,5 В, Eref2 = −2,5 В'));
push(p('', {}));
push(pright('Выполнил: студент группы ЭФБО-04-24 Ляпунов Д.Д.'));
push(pright('Принял: Клёсов Д.Н.'));
push(p('', {}));
push(pc('Москва 2026', { size: 24 }));
push(new Paragraph({ children: [new PageBreak()] }));

// ---------- 1. Название и цель ----------
push(h1('1. Название и цель работы'));
push(p('Название: Лабораторная работа № 7 «Изучение принципов работы аналого-цифровых преобразователей».'));
push(p('Цель: снять коды 8-битного АЦП (±2,5 В) по рисунку 58 и рисунок 60 ТЗ и рассчитать погрешность по формулам (1)-(3). Задачи: собрать схему измерения точности АЦП с обратным ЦАП (рисунок 58 ТЗ), снять коды для 10 значений Uвх, рассчитать погрешности, собрать схему подключения МК-51 к АЦП (рисунок 60 ТЗ) и снять коды для трех значений Uвх.'));
push(p('Вариант задания (таблица 18 ТЗ, № 1): разрядность 8, Eref1 = +2,5 В, Eref2 = −2,5 В. Полный размах опорного напряжения 5,0 В.'));
push(formula('Dрасч = 256·Uвх / (V1 + |V2|)', 1));
push(formula('D = Dинв − 128', 2));
push(formula('ΔU% = 100·(Uвых(ЦАП) − Uвх) / Uвх', 3));
push(p('Формула (2), для разнополярной опоры (код с пробников инверсный; больше 128, положительный, меньше, отрицательный).'));

// ---------- 2. Перечень элементов ----------
push(h1('2. Перечень элементов схемы'));
push(p('Задание 1 выполнено в KiCad (проект Lab7_ADC): виртуальные модели АЦП/ЦАП повторяют УГО рисунка 59 ТЗ (прямоугольники, выводы Vin, Vref+, Vref−, D0-D7, SOC, EOC, OE). Источники, идеальные VDC/VPULSE. Пробы X1-X10, однопиновые соединители (эквивалент пробников Multisim). Инвертор, одиночный КМОП 74LVC1G04 (функциональный аналог TTL-инвертора U2A из ТЗ).'));
push(tcap('Таблица 1 — Перечень элементов схемы'));
push(tbl(
  ['Поз.', 'Тип / номинал', 'Назначение'],
  [
    ['A1', 'Virtual_ADC8, 8 бит', 'Исследуемый АЦП: Vin, Vref±, D0-D7, SOC, EOC, OE'],
    ['A2', 'Virtual_DAC8, 8 бит', 'Обратный ЦАП: D0-D7, Vref±, OUT (Uвых)'],
    ['V1', 'VDC 2,5 В', 'Опорное Vref+ = +2,5 В (пин 1 → VREF_P, пин 2 → GND)'],
    ['V2', 'VDC 2,5 В', 'Опорное Vref− = −2,5 В (пин 1 → GND, пин 2 → VREF_M, инверсное включение)'],
    ['V3', 'VDC, перем.', 'Входное Uвх (10 значений 0,1…2,4 и −0,5…−2,0 В)'],
    ['V4', 'VPULSE 1 кГц', 'Синхронизация: фронт SOC'],
    ['V5', 'VDC 5 В', 'Питание инвертора U2 (VCC)'],
    ['U2', '74LVC1G04', 'Инвертор: SOC → OE_N (противофаза, разрешает D0-D7)'],
    ['U1', 'VOLTMETER_DIFF', 'Вольтметр Uвых с выхода ЦАП'],
    ['X1-X8', 'Conn_01x01', 'Пробы D0-D7'],
    ['X9', 'Conn_01x01', 'Проба EOC'],
    ['X10', 'Conn_01x01', 'Проба Uвых (OUT ЦАП)'],
  ]
));
push(p('Задание 2 (файл Lab7_ADC_MCU.kicad_sch): A1, тот же Virtual_ADC8; DD1, AT89C51 (MCS-51, DIP-40); V1, Vin (пример 1 В); V2, +2,5 В (Vref+); V3, −2,5 В (Vref−); V4, +5 В (питание МК); X1-X8, пробы на P2.0-P2.7; X9, EOC. Связи: P1.0-P1.7 ← AD0-AD7 (D0-D7 АЦП), P2.0-P2.7 → X1-X8, P3.6 → SOC, OE АЦП → GND (выход постоянно разрешен). Неиспользуемые выводы DD1 (P0, P3.0-P3.5, P3.7, XTAL, PSEN, ALE) закрыты маркерами No-Connect.'));

// ---------- 3. Схемы ----------
push(h1('3. Схемы при моделировании'));
push(p('Схемы Заданий 1 и 2 набраны в KiCad (каталог Lab7_ADC). Multisim недоступен; вместо моделирования, проверка ERC (0 ошибок на обоих листах) и сверка netlist.'));
push(p('D0-D7: A1-A2-X1-X8, 8 линий. Остальные цепи, метками по рисунку 58.'));
push(...imgPara('render_task1.png', 590, 476, 'Рисунок 1 — Задание 1. Схема исследования 8-разрядного АЦП (аналог рисунок 58 ТЗ).'));
push(...imgPara('render_task2.png', 590, 335, 'Рисунок 2 — Задание 2. Подключение МК-51 к АЦП (аналог рисунок 60 ТЗ).'));
push(p('Листинг main.c (Задание 2, Keil/SDCC-синтаксис, файл main.c в каталоге проекта): P1, вход (0xFF), P2, выход (0x00), строб P3.6 0/1 (SOC), чтение val = P1, вывод P2 = val, бесконечный цикл. При Uвх = 1,0 В код равен 51, что совпадает с расчетом таблица 2 (D = 51, Dинв = 179).'));
push(...fs.readFileSync('main.c', 'utf-8').replace(/\s+$/, '').split('\n').map(code));

// ---------- 4. Таблица 17 ----------
push(h1('4. Результаты моделирования по схеме рисунок 58 (таблица типа 17)'));
push(p('Расчет по формулам ТЗ при V1 + |V2| = 5,0 В: Dрасч = 51,2·Uвх; D = floor(Dрасч) (для отрицательных, округление вниз, как в примере ТЗ: −42,67 → −43); Dинв = D + 128; Uвых = D·5/256; ΔU% по (3). Коды D2/D16, двоичное/шестнадцатеричное представление Dинв (то, что показывают пробники).'));
push(p('Таблица 17 ТЗ посчитана при 6 В. Ниже, пересчет для варианта 1: 5,0 В, Dрасч = 51,2·Uвх.'));
push(tcap('Таблица 2 — Исследование АЦП, вариант 1 (8 бит, ±2,5 В)'));
push(tblW(
  ['Uвх, В', 'Uвых, В', 'D2', 'D16', 'Dинв', 'D', 'Dрасч', 'ΔU, %'],
  [
    ['0,1', '0,09766', '10000101', '85', '133', '5', '5,12', '−2,34'],
    ['0,2', '0,19531', '10001010', '8A', '138', '10', '10,24', '−2,34'],
    ['0,5', '0,48828', '10011001', '99', '153', '25', '25,60', '−2,34'],
    ['1,0', '0,99609', '10110011', 'B3', '179', '51', '51,20', '−0,39'],
    ['1,5', '1,48438', '11001100', 'CC', '204', '76', '76,80', '−1,04'],
    ['2,0', '1,99219', '11100110', 'E6', '230', '102', '102,40', '−0,39'],
    ['2,4', '2,38281', '11111010', 'FA', '250', '122', '122,88', '−0,72'],
    ['−0,5', '−0,50781', '01100110', '66', '102', '−26', '−25,60', '1,56'],
    ['−1,0', '−1,01562', '01001100', '4C', '76', '−52', '−51,20', '1,56'],
    ['−2,0', '−2,01172', '00011001', '19', '25', '−103', '−102,40', '0,59'],
  ],
  [900, 1100, 2700, 800, 800, 800, 1100, 1160],
  SZxs
));
push(p('Наибольшая погрешность, на малых сигналах (0,1-0,5 В, −2,34 %: цена кванта 5/256 ≈ 0,0195 В сопоставима с сигналом); на 1,0-2,0 В погрешность менее 1 %.'));

// ---------- 5. Пробы по схеме 60 ----------
push(h1('5. Показания пробников по схеме рисунок 60 (Задание 2)'));
push(p('Сняты для трех значений Uвх из таблицы 2. Пробники X1-X8 (P2.0-P2.7) показывают Dинв в двоичном виде; P2 = P1 (код с АЦП без изменений).'));
push(tcap('Таблица 3 — Коды на порту P2'));
push(tbl(
  ['Uвх, В', 'D', 'Dинв', 'Пробы X8…X1 (D7…D0)', 'D16', 'P2'],
  [
    ['1,0', '51', '179', '10110011', 'B3', '10110011'],
    ['2,0', '102', '230', '11100110', 'E6', '11100110'],
    ['−1,0', '−52', '76', '01001100', '4C', '01001100'],
  ]
));
push(p('При Uвх = 1,0 В: D = 51, Dинв = 179 = 0xB3 = 10110011 (таблица 2, таблица 3). EOC (X9) после строба P3.6, лог. 1 (конец преобразования).'));

// ---------- 6. Выводы ----------
push(h1('6. Выводы по работе'));
push(p('1. Собраны обе схемы варианта 1 (8 бит, ±2,5 В). ERC: 0 ошибок; по 2 предупреждения на лист, библиотека/сетка, на цепи не влияют. Netlist полон: D0-D7 (A1-A2-X, по 3 пина), VIN, VREF_P, VREF_M, SOC, EOC, OE_N, UOUT; в Задании 2, AD0-AD7 (P1), P2_0-P2_7 (X1-X8), SOC (P3.6).'));
push(p('2. По таблице 2 погрешность квантования падает с ростом сигнала: −2,34 % на 0,1-0,5 В до −0,39 % на 1,0 и 2,0 В; на отрицательных входах 0,6-1,6 %. Это соответствует цене кванта 19,5 мВ. Инверсия кода при разнополярной опоре подтверждена: D = Dинв − 128, граница 128 отделяет знак.'));
push(p('3. Связка МК-51-АЦП работает по программе main.c: строб P3.6 запускает преобразование, код считывается с P1 и выводится на P2 без изменений (таблица 3). EOC после строба P3.6 = 0→1, лог. 1. Временные диаграммы не снимались.'));
push(p('Примечания: УГО и обозначения A/DD/V/X, по ЕСКД 2.710/2.743; U2 оставлено по тексту ТЗ «U2A». Рамка/штамп не оформлялись.'));
push(h1('Список использованных источников'));
[
  'Практическое занятие 13-14. Лабораторная работа № 7 «Изучение принципов работы аналого-цифровых преобразователей» (таблица 17, 18, рисунок 58-60).',
  'ГОСТ 2.710-81. Обозначения буквенно-цифровые в электрических схемах.',
  'ГОСТ 7.32-2017. Отчёт о научно-исследовательской работе. Структура и правила оформления.',
  'Файлы проекта: Lab7_ADC.kicad_sch, Lab7_ADC_MCU.kicad_sch, main.c.',
].forEach((src, i) => push(new Paragraph({
  children: [new TextRun({ text: `${i + 1}. ${src}`, font: F, size: SZ, color: BLACK })],
  spacing: BODY_SPACING,
})));

const footerNum = new Footer({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ font: F, size: 24, color: BLACK, children: [PageNumber.CURRENT] })],
  })],
});
const footerFirst = new Footer({
  children: [new Paragraph({ children: [new TextRun({ text: '', font: F, size: 24 })] })],
});
const doc = new Document({
  styles: { default: { document: { run: { font: F, size: SZ, color: BLACK } } } },
  sections: [{
    properties: { titlePage: true, page: { margin: { top: 1134, bottom: 1134, left: 1701, right: 851 } } },
    footers: { default: footerNum, first: footerFirst },
    children: C,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync('Lab7_Otchet.docx', b); console.log('OK Lab7_Otchet.docx', b.length); });
