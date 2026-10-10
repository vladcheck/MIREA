# ПР №2. Подключение внешней памяти к МК-51 (аналог рис.25)

Вариант: ОЗУ — Вар.1, ПЗУ — Вар.7 (см. `variants.json`).

## Состав

- `PR2_extmem.kicad_sch` — схема KiCad 10 (лист A3): U1 P8051AH (МК-51),
  U3 74LS373 (защёлка A0–A7 по ALE), U2 HY6264 (ОЗУ), U4 27C64 (ПЗУ),
  U5 74LS138 (дешифратор RAM_CS/ROM_CS), D1+R1 (LED ошибки на P1.0),
  Y1 12 МГц, RST-цепь, пробник ALE (XSC1).
- `generate_schematic.py` — генератор схемы:
  `python3 generate_schematic.py [--variant1 N] [--variant2 M]`.
- `prog/` — `prog2_ram_test.asm/.c` (тест ОЗУ), `prog2_rom_checksum.asm/.c`
  (контрольная сумма ПЗУ).
- `sim/` — `test_ram.py`, `test_rom.py`, `test_ale.py` (симуляция шины),
  `mcu8051_bus.py`, `run_all.py`.
- `out/` — результаты симуляций и осциллограмма ALE.
- `PR2_Otchet.docx` — отчёт.

## Сквозной прогон

```bash
bash run.sh
```

Ждать `ALL PASS` в секциях ОЗУ, ПЗУ и ALE.
