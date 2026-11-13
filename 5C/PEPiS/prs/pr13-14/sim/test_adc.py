# -*- coding: utf-8 -*-
"""Проверочные тесты модели АЦП и генерация результатов (практика 13-14).

Запуск из корня pr13-14:
    ~/.local/share/agentpipe/gost-report/venv/bin/python sim/test_adc.py

Проверяет битовую точность квантователя против контрольных точек
методички, собирает таблицы исследования для учебного примера и
варианта 4, эмулирует чтение кода МК-51 и пишет сводку в
out/adc_results.json.
"""

import json
from pathlib import Path

from adc import (
    EXAMPLE_BITS,
    EXAMPLE_EXPECTED_CODE,
    EXAMPLE_UIN,
    EXAMPLE_VREF_M,
    EXAMPLE_VREF_P,
    TZ_TABLE17,
    VARIANT4_BITS,
    VARIANT4_INPUTS_V,
    VARIANT4_MCU_INPUTS_V,
    VARIANT4_VREF_M,
    VARIANT4_VREF_P,
    code_direct,
    dac_voltage,
    investigation_table,
    lsb_voltage,
    mcu_read_code,
    quantize,
    variant4_summary,
)

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "out" / "adc_results.json"


def test_example_probe_code():
    """Учебный пример: uвх = 1 В, 8 бит, Vref+ = 5 В -> код 51 (методичка)."""
    code = quantize(EXAMPLE_UIN, EXAMPLE_VREF_P, EXAMPLE_VREF_M, EXAMPLE_BITS)
    assert code == EXAMPLE_EXPECTED_CODE, (code, EXAMPLE_EXPECTED_CODE)


def test_variant4_control_points():
    """Вариант 4: контрольные коды D = trunc(65536 * u / 5)."""
    assert quantize(1.0, 5.0, 0.0, 16) == 13107
    assert quantize(2.5, 5.0, 0.0, 16) == 32768
    assert quantize(4.0, 5.0, 0.0, 16) == 52428


def test_quantizer_edges():
    """Границы шкалы: ниже Vref- -> 0, выше Vref+ -> 2**n - 1."""
    assert quantize(-0.001, 5.0, 0.0, 16) == 0
    assert quantize(0.0, 5.0, 0.0, 16) == 0
    assert quantize(5.0, 5.0, 0.0, 16) == 65535
    assert quantize(9.9, 5.0, 0.0, 16) == 65535


def test_formula1():
    """Формула (1): Dрасч = 2**k * uвх / (Vref+ + |Vref-|)."""
    assert abs(code_direct(1.0, 5.0, 0.0, 16) - 13107.2) < 1e-9
    assert abs(code_direct(0.1, 2.5, -2.5, 8) - 5.12) < 1e-9


def test_dac_inverse_within_lsb():
    """ЦАП восстанавливает напряжение с погрешностью меньше 1 МЗР."""
    lsb = lsb_voltage(5.0, 0.0, 16)
    for u in (0.1, 1.0, 2.5, 4.9):
        code = quantize(u, 5.0, 0.0, 16)
        assert abs(dac_voltage(code, 5.0, 0.0, 16) - u) < lsb


def test_tz_table17_internal_consistency():
    """Эталонная таблица 17 методички согласована с формулой (2):
    прямой код D равен разности инверсного кода и 128."""
    for row in TZ_TABLE17:
        assert row[5] == row[4] - 128, row
    positive = [r[0] for r in TZ_TABLE17 if r[0] > 0]
    assert positive == sorted(positive)


def test_variant4_monotonic():
    """Код варианта 4 монотонно неубывает по uвх."""
    codes = [quantize(u, 5.0, 0.0, 16) for u in VARIANT4_INPUTS_V]
    assert codes == sorted(codes)
    assert len(set(codes)) == len(codes)


def test_mcu_probe_consistency():
    """Пробники X0..X7 (P2) и X8..X15 (выходы АЦП) дают один код."""
    for u in VARIANT4_MCU_INPUTS_V:
        res = mcu_read_code(u, 5.0, 0.0, 16)
        probe_code = sum(bit << i for i, bit in enumerate(res["probes"]))
        assert probe_code == res["code"]
        assert res["p2_low"] == res["p1_in"]
        assert res["p0_in"] == res["code"] >> 8


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"{len(tests)} tests passed")

    example_row = mcu_read_code(
        EXAMPLE_UIN, EXAMPLE_VREF_P, EXAMPLE_VREF_M, EXAMPLE_BITS
    )
    results = {
        "example": {
            "bits": EXAMPLE_BITS,
            "vref_p": EXAMPLE_VREF_P,
            "vref_m": EXAMPLE_VREF_M,
            "u_in": EXAMPLE_UIN,
            "expected_probe_code": EXAMPLE_EXPECTED_CODE,
            "model_code": example_row["code"],
            "p2_probe_code": example_row["p2_low"],
        },
        "variant4": variant4_summary(),
        "tz_table17": [
            {
                "u_in": r[0],
                "u_dac": r[1],
                "code_bin": r[2],
                "code_hex": r[3],
                "code_probe": r[4],
                "code_dec": r[5],
                "d_calc": r[6],
                "d_u_pct": r[7],
            }
            for r in TZ_TABLE17
        ],
        "variant4_table17": investigation_table(
            VARIANT4_INPUTS_V,
            VARIANT4_VREF_P,
            VARIANT4_VREF_M,
            VARIANT4_BITS,
        ),
        "variant4_mcu": [
            mcu_read_code(u, VARIANT4_VREF_P, VARIANT4_VREF_M, VARIANT4_BITS)
            for u in VARIANT4_MCU_INPUTS_V
        ],
    }
    OUT.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
