# ПР №2. Подключение внешней памяти к МК-51 и её тестирование

Отдельная папка (по требованию): `PR2_ExtMem/` — всё задание живёт здесь,
ничего вне папки не создаётся (кроме чтения KiCad-библиотек и MCP-лоадера).

## Выбор варианта (важно)

В тексте ТЗ (табл. 8, табл. 9) **правило выбора варианта не указано**
(нет фраз «по журналу» / «по последней цифре»). Обычно вариант задаёт
преподаватель. Поэтому решение **параметрическое**:

- `variants.json` — все 12 вариантов (1–6 ОЗУ, 7–12 ПЗУ);
- прошивки (`prog/*.asm`, `prog/*.c`) — вариант меняется 2–3 строками `EQU`/`define`
  (таблица замен в шапке каждого файла);
- симулятор (`sim/`) прогоняет **все 12 вариантов**, а не только демо;
- демо по умолчанию: **Вар.1 (ОЗУ 8К, 0AAh, 0800h) + Вар.7 (ПЗУ 8К, K=100, 0800h)**.

## Состав

| Путь | Что это (пункт отчёта 2.2.4) |
|---|---|
| `generate_schematic.py` → `PR2_extmem.kicad_sch` | п.3 — схема (аналог рис.25: U1 МК-51, U3 74LS373, U2 ОЗУ, U4 ПЗУ, U5 74LS138 дешифратор, D1 LED, XSC1-корпус на ALE; ERC 0) |
| `prog/prog2_ram_test.asm`, `prog/prog2_ram_test.c` | п.4 — Задание 1 (ОЗУ, 1 Кбайт с ZZZ, паттерн XX, LED на P1.0) |
| `prog/prog2_rom_checksum.asm`, `prog/prog2_rom_checksum.c` | п.4 — Задание 2 (ПЗУ, CRC K байт с ZZZ, сравнение с эталоном) |
| `sim/mcu8051_bus.py`, `sim/test_ram.py`, `sim/test_rom.py`, `sim/test_ale.py` | п.5 — моделирование вместо Multisim (macOS): шина ALE/P0/P2//RD//WR, тесты, осциллограмма |
| `out/ram_results.json`, `out/rom_results.json`, `out/ale_waveform.csv`, `out/ale_oscillogram.png` | п.5 — результаты |
| `docs/OTCHET.md` | отчёт целиком (п.1–5 + ответы на 10 вопросов самоконтроля) |

## Запуск (проверено на macOS, Python 3.9, KiCad 10)

```bash
cd PR2_ExtMem
bash run.sh
# или по шагам:
python3 generate_schematic.py --variant1 1 --variant2 7
python3 sim/run_all.py
```

Ожидается `ALL PASS`. Схему открыть в KiCad: `PR2_extmem.kicad_sch`.
Осциллограмма: `out/ale_oscillogram.png` (1 мкс/дел, 5 В/дел, 2 импульса ALE за машинный цикл).

## Соответствие Multisim-оригиналу

| Multisim (рис.25–28) | Здесь |
|---|---|
| U1 8051, U3 74LS373N/4037BP, U2 RAM 2K/8K, Bus1/Bus2 Merge | U1 P8051AH, U3 74LS373, U2 HY6264 (8Kx8, аналог 6264/6116), метки AD0-AD7/A0-A7 вместо шин |
| Built-in External RAM = N Кбайт | подпись на схеме + `variants.json` |
| prog2.asm / prog2.c, MCU→Build, F5/F11, Memory view | `prog/*` + `sim/*` (пошаговость = итерации цикла, Memory view = `xram`/`rom` массивы) |
| XSC1 Ch.A→ALE, Ch.B→GND, 1 мкс/дел, 5 В/дел | `sim/test_ale.py` → CSV+PNG+ASCII, метка XSC1-ALE-PROBE на схеме |
| Светодиод при несовпадении | P1.0 → R1 → D1 (ERROR), `led_error` в симуляторе + негативные тесты |
