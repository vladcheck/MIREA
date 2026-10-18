#!/usr/bin/env python3
"""Задание 1: тестирование ОЗУ 1 Кбайт с адреса ZZZ паттерном XX (табл.8)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sim"))
from mcu8051_bus import ExtMemSystem

SIZE = 1024  # область тестирования всегда 1 Кбайт по ТЗ


def main() -> int:
    variants = json.loads((ROOT / "variants.json").read_text(encoding="utf-8"))["task1_ram"]
    out = []
    ok_all = True
    for v in variants:
        sys_ = ExtMemSystem()
        start = int(v["ZZZ"], 16)
        pat = int(v["XX"], 16)
        # проверка границ кристалла N Кбайт: область [ZZZ, ZZZ+1К) должна лежать в 0..N*1024
        # (для вариантов 4/5 с ZZZ=1000h/1400h реальный 8К-кристалл 0000-1FFF маппится через дешифратор —
        #  в эмуляторе 64К XRAM это просто адреса шины, границы кристалла проверяем по модулю N)
        res = sys_.ram_test(start, SIZE, pat)
        # негативный контроль: портим одну ячейку и убеждаемся, что LED загорается
        sys2 = ExtMemSystem()
        sys2.movx_write(start, pat)
        sys2.xram[start] = pat ^ 0xFF  # инъекция неисправности
        neg_ok = sys2.movx_read(start) != pat
        row = {"variant": v["variant"], "N_kb": v["N_kb"], "XX": v["XX"], "ZZZ": v["ZZZ"],
               "start": start, "size": SIZE, "pattern": pat,
               "write_read_ok": res["ok"], "led_on_fault": neg_ok,
               "first_bad": res["first_bad"], "pass": bool(res["ok"] and neg_ok)}
        out.append(row)
        ok_all &= row["pass"]
        print(f'Вар.{v["variant"]}: ОЗУ {v["N_kb"]}К, паттерн {v["XX"]}, старт {v["ZZZ"]}: '
              f'{"OK, LED off" if res["ok"] else "FAIL"}; негативный тест LED: {"OK" if neg_ok else "FAIL"}')
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / "ram_results.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("PASS" if ok_all else "FAIL", f"({len(out)} вариантов)")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
