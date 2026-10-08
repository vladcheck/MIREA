#!/bin/bash
# ПР №2 — сквозной прогон: генерация схемы + симуляция + отчёт о файлах.
set -e
cd "$(dirname "$0")"
echo "== [1/4] Генерация схемы KiCad =="
KICAD_PY="/Users/d.d.lyapunov/MCP/KiCAD-MCP-Server/venv-kicad/bin/python"
if [ ! -x "$KICAD_PY" ]; then KICAD_PY="python3"; fi
"$KICAD_PY" generate_schematic.py --variant1 1 --variant2 7
echo "== [2/4] Симуляция ОЗУ (6 вариантов) =="
python3 sim/test_ram.py
echo "== [3/4] Симуляция ПЗУ (6 вариантов) =="
python3 sim/test_rom.py
echo "== [4/4] Осциллограмма ALE =="
python3 sim/test_ale.py
echo "== Файлы =="
ls -la PR2_extmem.kicad_sch prog/ out/ docs/
echo "DONE: ALL PASS если выше везде PASS"
