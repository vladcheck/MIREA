# Происхождение символов схемы pr15-16.kicad_sch

## Пользовательский символ (обязателен по ТЗ ЛР8)

| Символ | Обозначение | Происхождение |
|---|---|---|
| `PEPiS:MK52` | U1 (МК-52) | **Пользовательский**, описан в генераторе `tools/make_sch.py` (функция `mk52_symbol`), корпус DIP-40, 40 выводов. В системных библиотеках KiCad символа МК-52 (советский учебный МК на базе Intel 8052) **не существует**, поэтому по методичке ЛР8 требуется собственный символ. Определение встроено в файл схемы (lib_symbols), отдельная библиотека `.kicad_sym` не используется (предупреждение ERC `lib_symbol_issues` о библиотеке PEPiS — следствие этого, некритично). |

## Встроенные копии системных символов KiCad 10

Извлечены из системных библиотек KiCad
(`/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols`) и встроены
в `lib_symbols` файла схемы (файл схемы остаётся самодостаточным):

| Символ | Библиотека | Экземпляры |
|---|---|---|
| `Device:Crystal` | Device.kicad_sym | Y1 (кварц 11,0592 МГц) |
| `Device:C` | Device.kicad_sym | C1, C2 (22 пФ), C3 (10 мкФ) |
| `Device:R` | Device.kicad_sym | R1, R2 (10 кОм) |
| `Switch:SW_Push` | Switch.kicad_sym | SW1 (RESET) |
| `Connector_Generic:Conn_01x02` | Connector_Generic.kicad_sym | J1 (пробник осциллографа) |
| `power:+5V` | power.kicad_sym | PWR1–PWR4 |
| `power:GND` | power.kicad_sym | GND1–GND5 |
| `power:PWR_FLAG` | power.kicad_sym | PWR5 (+5V), PWR6 (GND) |

Все координаты — в миллиметрах, на сетке 1,27 мм.
