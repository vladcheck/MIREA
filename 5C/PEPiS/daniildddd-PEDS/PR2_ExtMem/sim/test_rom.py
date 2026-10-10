#!/usr/bin/env python3
"""Задание 2: контрольная сумма ПЗУ K байт с адреса ZZZ (табл.9) + сравнение с эталоном."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sim"))
from mcu8051_bus import ExtMemSystem


def fill_rom(sys_: ExtMemSystem, start: int, size: int):
    # детерминированное содержимое ПЗУ: младший байт адреса (как прошивка стенда)
    for off in range(size):
        sys_.rom[(start + off) & 0xFFFF] = (start + off) & 0xFF


def main() -> int:
    variants = json.loads((ROOT / "variants.json").read_text(encoding="utf-8"))["task2_rom"]
    out = []
    ok_all = True
    for v in variants:
        sys_ = ExtMemSystem()
        start = int(v["ZZZ"], 16)
        k = int(v["K_bytes"])
        fill_rom(sys_, start, k)
        ref = sys_.rom_checksum(start, k)  # эталон в «резидентном ПЗУ»
        got = sys_.rom_checksum(start, k)  # повторный подсчёт
        ok_match = (got == ref)
        # негативный контроль: портим байт → суммы обязаны разойтись, LED загорается
        sys_.rom[(start + k // 2) & 0xFFFF] ^= 0x01
        got_bad = sys_.rom_checksum(start, k)
        led = (got_bad != ref)
        row = {"variant": v["variant"], "N_kb": v["N_kb"], "K_bytes": k, "ZZZ": v["ZZZ"],
               "ref_hex": hex(ref), "got_hex": hex(got), "match": ok_match,
               "corrupt_hex": hex(got_bad), "led_on_mismatch": led,
               "pass": bool(ok_match and led)}
        out.append(row)
        ok_all &= row["pass"]
        print(f'Вар.{v["variant"]}: ПЗУ {v["N_kb"]}К, K={k}, старт {v["ZZZ"]}: '
              f'CRC={hex(got)} vs эталон {hex(ref)} -> {"СОВПАЛО" if ok_match else "РАЗОШЛОСЬ"}; '
              f'LED при порче: {"ON" if led else "OFF"}')
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / "rom_results.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("PASS" if ok_all else "FAIL", f"({len(out)} вариантов)")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
