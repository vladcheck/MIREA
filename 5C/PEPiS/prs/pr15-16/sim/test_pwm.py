# -*- coding: utf-8 -*-
"""Проверки реестровой модели ШИМ (sim/pwm_model.py), ПР 15-16."""

import pytest

from pwm_model import (
    VARIANT4,
    calc_reload,
    expected,
    machine_cycle_hz,
    run_experiment,
)

# Допуски: период должен совпадать с расчётом точно (события таймера
# детерминированы), скважность допускает накладные расходы обработчика
# (несколько машинных циклов до цикла задержки).
PERIOD_TOL_PCT = 0.1
DUTY_TOL_PCT = 1.0


@pytest.mark.parametrize("fosc_hz,period_s,want", [
    (11_059_200, 0.0711111, 0x0000),   # учебный пример: R = 0
    (13_000_000, 0.06, 0x0218),        # вариант 4: R = 536
])
def test_calc_reload(fosc_hz, period_s, want):
    assert calc_reload(fosc_hz, period_s) == want


def test_machine_cycle_variant4():
    assert machine_cycle_hz(13_000_000) == pytest.approx(1_083_333.333, rel=1e-6)


def test_variant4_expected():
    exp = expected(VARIANT4)
    assert exp["reload_hex"] == "0x0218"
    assert exp["period_s"] == pytest.approx(0.0600, abs=1e-4)
    assert exp["duty_pct"] == pytest.approx(75.0, abs=0.1)


def test_example_period_and_duty():
    _, meas, exp = run_experiment(
        {
            "name": "example",
            "title": "Учебный пример",
            "fosc_hz": 11_059_200,
            "rcap2h": 0x00,
            "rcap2l": 0x00,
            "tmp_cnt": 4000,
        }
    )
    assert meas["period_s"] == pytest.approx(
        exp["period_s"], rel=PERIOD_TOL_PCT / 100.0)
    assert meas["duty_pct"] == pytest.approx(
        exp["duty_pct"], rel=DUTY_TOL_PCT / 100.0)
    # период учебного примера по методичке: около 71 мс
    assert meas["period_s"] == pytest.approx(0.0711, abs=1e-3)


def test_variant4_period_and_duty():
    _, meas, exp = run_experiment(VARIANT4)
    assert meas["period_s"] == pytest.approx(0.06, abs=1e-4)
    assert meas["duty_pct"] == pytest.approx(75.0, abs=0.8)
