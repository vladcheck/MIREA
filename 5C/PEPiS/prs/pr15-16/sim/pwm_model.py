# -*- coding: utf-8 -*-
"""Реестровая модель ШИМ на таймере Т/С2 микроконтроллера МК-52
(8052-совместимый, Intel MCS-51), практическая работа 15-16.

Модель исполняет ту же последовательность действий, что и программы
src/main_example.c и src/main_variant4.c, на уровне машинных циклов:

  - таймер 2 работает в режиме 16-разрядного автоперезагрузки
    (CP/RL2 = 0, C/T2 = 0), период переполнения равен
    (65536 - RCAP2H:RCAP2L) машинных циклов, один машинный цикл
    равен 12 периодам кварца (формула (3) методички);
  - при переполнении устанавливается TF2 и вызывается обработчик
    прерывания (вектор 002Bh, разрешение IE.5 = ET2 и EA);
  - обработчик повторяет тело t2_isr(): сброс TF2, загрузка cnt из
    tmpCnt, фронт P1.0 = 1, программная задержка tmpCnt машинных
    циклов, спад P1.0 = 0. Скорость задержки соответствует формуле
    (4) методички: Q = tmpCnt/(65536 - R) (один отсчёт cnt за один
    машинный цикл). Команды обработчика до цикла и после него
    моделируются честно (2 + 1 + 1 машинных цикла), поэтому
    измеренная скважность чуть отличается от расчётной.

Модель накапливает фронты на выводе P1.0, измеряет период следования
импульсов и длительность высокого уровня, сравнивает их с расчётными
значениями по формулам (3) и (4) и сохраняет результаты в JSON и CSV.

Запуск:  python sim/pwm_model.py        (из каталога pr15-16)
Тесты:  python -m pytest sim/test_pwm.py
"""

import csv
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Константы: конфигурации учебного примера и варианта 4 (таблица 19 методички)
# ---------------------------------------------------------------------------

EXAMPLE = {
    "name": "example",
    "title": "Учебный пример",
    "fosc_hz": 11_059_200,   # кварц учебного примера
    "rcap2h": 0x00,          # R = 0x0000
    "rcap2l": 0x00,
    "tmp_cnt": 4000,         # скважность по формуле (4)
}

VARIANT4 = {
    "name": "variant4",
    "title": "Индивидуальный вариант 4",
    "fosc_hz": 13_000_000,   # кварц варианта 4
    "rcap2h": 0x02,          # R = 0x0218 = 536
    "rcap2l": 0x18,
    "tmp_cnt": 48750,        # Q*(65536 - R) = 0,75*65 000
}

MC_PER_CLOCK = 12          # один машинный цикл МК-51/52
MAX_TICKS = 500_000_000    # защита от зацикливания

# Биты регистра T2CON
T2CON_CP_RL2 = 0x01
T2CON_C_T2 = 0x02
T2CON_EXEN2 = 0x04
T2CON_TR2 = 0x08
T2CON_TF2 = 0x80

IE_ET2 = 0x20   # IE.5
IE_EA = 0x80    # IE.7


def machine_cycle_hz(fosc_hz):
    """Частота машинного цикла C = Fosc/12 (формула (3) методички)."""
    return fosc_hz / MC_PER_CLOCK


def calc_reload(fosc_hz, period_s):
    """Величина перезагрузки R по формуле (3): R = 65536 - C*T."""
    r = 65536 - machine_cycle_hz(fosc_hz) * period_s
    return int(round(r))


class MCU52:
    """МК-52: таймер 2 в режиме автоперезагрузки, порт P1.0, прерывания."""

    def __init__(self, fosc_hz, rcap2h, rcap2l, tmp_cnt):
        self.clock_hz = fosc_hz
        self.mc_hz = machine_cycle_hz(fosc_hz)
        self.t2con = 0
        self.th2 = rcap2h
        self.tl2 = rcap2l
        self.rcap2h = rcap2h
        self.rcap2l = rcap2l
        self.ie = 0
        self.p1 = 0
        self.tmp_cnt = tmp_cnt
        self.cnt = 0
        self.time_mc = 0          # модельное время, машинные циклы
        self.edges = []           # (t_mc, уровень P1.0) на каждый фронт
        self.isr_ticks_left = 0   # оставшиеся машинные циклы обработчика
        self.isr_stage = None     # этап исполнения обработчика
        self.overflows = 0

    # --- порт P1 ------------------------------------------------------
    def _set_p1_0(self, level):
        new = (self.p1 | 0x01) if level else (self.p1 & ~0x01)
        if new != self.p1:
            self.p1 = new
            self.edges.append((self.time_mc, level))

    # --- прерывания ----------------------------------------------------
    def _irq_pending(self):
        return (self.ie & IE_EA) and (self.ie & IE_ET2) and \
            (self.t2con & T2CON_TF2)

    # --- обработчик прерывания t2_isr (тело из main_*.c) ---------------
    def _isr_step(self):
        """Один машинный цикл обработчика. Этапы повторяют t2_isr()."""
        if self.isr_stage == "tf2":
            self.t2con &= ~T2CON_TF2          # TF2 = 0
            self.cnt = self.tmp_cnt           # cnt = tmpCnt
            self.isr_stage = "front"
        elif self.isr_stage == "front":
            self._set_p1_0(1)                 # P1_0 = 1 (2 маш. цикла)
            self.isr_ticks_left = 1
            self.isr_stage = "front2"
        elif self.isr_stage == "front2":
            self.isr_stage = "delay"
        elif self.isr_stage == "delay":
            if self.cnt != 0:
                self.cnt -= 1                 # while (cnt != 0) cnt--;
            if self.cnt == 0:
                self.isr_stage = "fall"
        elif self.isr_stage == "fall":
            self._set_p1_0(0)                 # P1_0 = 0 (2 маш. цикла)
            self.isr_ticks_left = 1
            self.isr_stage = "fall2"
        elif self.isr_stage == "fall2":
            self.isr_stage = None

    # --- таймер 2 ------------------------------------------------------
    def _timer2_step(self):
        """Один машинный цикл счётчика таймера 2 (TR2 = 1)."""
        if not (self.t2con & T2CON_TR2):
            return
        value = (self.th2 << 8) | self.tl2
        value = (value + 1) & 0xFFFF
        if value == 0:
            # переполнение: автоперезагрузка из RCAP2 (CP/RL2 = 0)
            value = (self.rcap2h << 8) | self.rcap2l
            self.t2con |= T2CON_TF2
            self.overflows += 1
        self.th2 = (value >> 8) & 0xFF
        self.tl2 = value & 0xFF

    # --- шаг модели ----------------------------------------------------
    def step(self):
        # Таймер 2 считает аппаратно и не останавливается на время
        # исполнения обработчика: следующее переполнение наступает
        # ровно через (65536 - RCAP2) машинных циклов после предыдущего,
        # поэтому период ШИМ не зависит от длительности t2_isr().
        self._timer2_step()
        if self.isr_stage is not None:
            self._isr_step()
        elif self._irq_pending():
            self.isr_stage = "tf2"  # векторирование прерывания
        self.time_mc += 1
        if self.time_mc > MAX_TICKS:
            raise RuntimeError("превышен лимит тактов модели")

    # --- программная инициализация, как в main() -----------------------
    def init_from_main(self):
        """Повторяет инициализацию из main_example.c / main_variant4.c."""
        self._set_p1_0(0)
        self.th2 = self.rcap2h
        self.tl2 = self.rcap2l
        self.t2con &= ~(T2CON_CP_RL2 | T2CON_C_T2 | T2CON_EXEN2)
        self.ie |= IE_ET2 | IE_EA
        self.t2con |= T2CON_TR2


def run_until_edges(mcu, n_edges):
    """Прогнать модель, пока на P1.0 не наберётся n_edges фронтов."""
    target = len(mcu.edges) + n_edges
    while len(mcu.edges) < target:
        mcu.step()


def measure(mcu, n_rising=8):
    """Измерить период (по передним фронтам) и скважность."""
    rising = [t for t, lvl in mcu.edges if lvl == 1]
    falling = [t for t, lvl in mcu.edges if lvl == 0]
    if len(rising) < n_rising + 1 or len(falling) < n_rising:
        raise RuntimeError("недостаточно фронтов для измерения")
    periods = [rising[i + 1] - rising[i] for i in range(n_rising)]
    highs = [falling[i] - rising[i] for i in range(n_rising)]
    period_mc = sum(periods) / len(periods)
    high_mc = sum(highs) / len(highs)
    return {
        "period_mc": period_mc,
        "period_s": period_mc / mcu.mc_hz,
        "high_mc": high_mc,
        "high_s": high_mc / mcu.mc_hz,
        "duty_pct": high_mc / period_mc * 100.0,
    }


def expected(config):
    """Расчётные значения по формулам (3) и (4) методички."""
    reload_value = (config["rcap2h"] << 8) | config["rcap2l"]
    span = 65536 - reload_value
    c = machine_cycle_hz(config["fosc_hz"])
    period_s = span / c
    duty = config["tmp_cnt"] / span
    return {
        "reload_dec": reload_value,
        "reload_hex": "0x%04X" % reload_value,
        "span_mc": span,
        "period_s": period_s,
        "high_s": config["tmp_cnt"] / c,
        "duty_pct": duty * 100.0,
    }


def run_experiment(config, n_rising=8):
    mcu = MCU52(config["fosc_hz"], config["rcap2h"], config["rcap2l"],
                config["tmp_cnt"])
    mcu.init_from_main()
    run_until_edges(mcu, 2 * n_rising + 2)
    meas = measure(mcu, n_rising)
    exp = expected(config)
    return mcu, meas, exp


def export_waveform_csv(mcu, path, t_max_s):
    """Сохранить осциллограмму P1.0 (ступенчатая форма) в CSV."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["t_s", "p1_0"])
        level = 0
        for t_mc, lvl in mcu.edges:
            if t_mc / mcu.mc_hz > t_max_s:
                break
            writer.writerow(["%.9f" % (t_mc / mcu.mc_hz), level])
            level = lvl
            writer.writerow(["%.9f" % (t_mc / mcu.mc_hz), level])
        writer.writerow(["%.9f" % t_max_s, level])


def main():
    base = Path(__file__).resolve().parent.parent
    out = base / "out"
    out.mkdir(exist_ok=True)

    results = []
    for config in (EXAMPLE, VARIANT4):
        mcu, meas, exp = run_experiment(config)
        row = {
            "name": config["name"],
            "title": config["title"],
            "fosc_hz": config["fosc_hz"],
            "rcap2h": "0x%02X" % config["rcap2h"],
            "rcap2l": "0x%02X" % config["rcap2l"],
            "tmp_cnt": config["tmp_cnt"],
            "expected": exp,
            "measured": meas,
            "period_deviation_pct": (
                (meas["period_s"] - exp["period_s"]) / exp["period_s"] * 100.0
            ),
            "duty_deviation_pct": (
                (meas["duty_pct"] - exp["duty_pct"]) / exp["duty_pct"] * 100.0
            ),
        }
        results.append(row)
        export_waveform_csv(mcu, out / ("pwm_waveform_%s.csv" % config["name"]),
                            meas["period_s"] * 3)

    (out / "pwm_results.json").write_text(
        json.dumps({"results": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    for row in results:
        print("%s: T расч %.4f мс, T изм %.4f мс, Q расч %.2f %%, "
              "Q изм %.2f %%" % (
                  row["name"], row["expected"]["period_s"] * 1e3,
                  row["measured"]["period_s"] * 1e3,
                  row["expected"]["duty_pct"], row["measured"]["duty_pct"]))


if __name__ == "__main__":
    main()
