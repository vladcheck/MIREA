# pr5-6 execution plan (controller notes)

Work: MIREA PEPiS practice work `9.3. Практическая работа № 3. Организация заданных
временных интервалов средствами таймеров STM32` (folder `pr5-6/`).

- Source of truth: `docs/TZ.md` (extracted text), `docs/listing_9_4.c` (учебный пример),
  `docs/Практическая работа 3_Proteus.docx` (original; parse only via python-docx).
- Individual variant: **4** → T1 = 80 мс, T2 = 40 мс, диагностическое изменение **ARR+100**.
- MCU: STM32F103C8, HSI 8 МГц, PCLK1 = TIM2CLK = 8 МГц, APB1 делитель 1.
- Base time base: PSC = 7999 → fCNT = 1 кГц, 1 отсчёт = 1 мс, ARR = Tмс − 1.

## Timing values (single source of truth for the report)

| Опыт | Tзад, мс | ARR | PSC | fCNT | Tизм, мс | δT, % | полный период, мс |
|---|---|---|---|---|---|---|---|
| Базовая часть | 250 | 249 | 7999 | 1 кГц | 250,0 | 0,00 | 500,0 |
| T1 | 80 | 79 | 7999 | 1 кГц | 80,0 | 0,00 | 160,0 |
| T2 | 40 | 39 | 7999 | 1 кГц | 40,0 | 0,00 | 80,0 |
| После диагностики (ARR+100 на T2) | 140 | 139 | 7999 | 1 кГц | 140,0 | 250,00 (отклонение от T2) | 280,0 |

Проверка общей формулой: T = (PSC+1)·(ARR+1)/fTIM = 8000·(ARR+1)/8·10⁶ с.
Диагностика: ARR 39 → 139 даёт 140 мс вместо 40 мс; после возврата ARR=39
интервал 40 мс подтверждается снова. Прошивка сама фиксирует число событий
обновления на каждой фазе (g_update_count), поэтому «проявление неисправности»
видно и в отладчике, и на временной диаграмме.

## Tasks

1. **C sources** — `src/main_example.c` (базовая часть 250 мс, листинг 9.4),
   `src/main_variant4.c` (фазная машина: 250 → T1 → T2 → ARR+100 → возврат T2),
   `tools/include/stm32f1xx.h` stub; проверка
   `clang -fsyntax-only -Wall -Wextra -Itools/include src/*.c`.
2. **Model + tests** — `sim/tim2_model.py`, `sim/test_tim2.py`; артефакты:
   `out/tim2_results.json`, `out/tim2_waveform.csv`, `img/waveform-base.png`,
   `img/waveform-t1.png`, `img/waveform-t2.png` (диаграммы с ≥5 измеренными
   интервалами и полным периодом). Запуск: `uv run --with matplotlib python3 sim/test_tim2.py`.
3. **KiCad schematic** — `kicad/pr5-6.kicad_sch` + `.kicad_pro`: STM32F103C8, светодиод
   + резистор 330 Ом на PA1, питание/общий провод, зоны обозначения Logic Analyzer;
   рендер в `img/scheme.png` (и SVG). Units mm only, 1.27 mm grid.
4. **Report** — `.gost-report/build.py` → `ПР_5_6_Валекжанин_В_С.docx` (gost-report
   skill, `python3 .../gost-report/scripts/ensure_env.py .gost-report/build.py`).
   Содержание по п. 7 TZ (13 пунктов) + ответы на 17 контрольных вопросов.
5. Final: full test run, report rebuild, code-review skill, commits.

## House rules for every subagent

- Talk to the human in English; every artifact for the professor is in Russian.
- Never use Read/cat/grep on .docx/.pdf (host breaks); use `uv run --with python-docx`.
- No placeholder boxes («ВСТАВИТЬ СЮДА») in final artifacts; no fabricated Proteus
  screenshots (Proteus cannot run here; waveforms come from the TIM2 model).
- KiCad: mm only, 1.27 mm grid; validate with `kicad-tool`/`validate_schematic`.
- gost-report: no long/medium dashes in report text, references via `r.ref.*`,
  listings via `r.listing` with a citation in text.
- Commits: conventional, prefixed `feat(pr5-6):` / `docs(pr5-6):` etc.
