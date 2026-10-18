#!/usr/bin/env python3
"""Сквозной прогон ПР №2: ОЗУ + ПЗУ + ALE. Код возврата 0 = всё PASS."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(name: str) -> int:
    p = subprocess.run([sys.executable, str(ROOT / "sim" / name)], capture_output=True, text=True)
    print(f"===== {name} =====")
    print(p.stdout, end="")
    if p.stderr:
        print(p.stderr, end="")
    return p.returncode


def main() -> int:
    rc = 0
    for t in ["test_ram.py", "test_rom.py", "test_ale.py"]:
        rc |= run(t)
    print("ИТОГ:", "ALL PASS" if rc == 0 else "FAILURES PRESENT")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
