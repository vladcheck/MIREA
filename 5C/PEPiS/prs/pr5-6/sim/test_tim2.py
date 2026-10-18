"""Тесты модели таймера TIM2 (STM32F103C8) для ПР №5-6, вариант 4.

Позитивные тесты повторяют точную последовательность фаз
pr5-6/src/main_variant4.c (измерения сняты с реестровой модели, поскольку
Proteus 8.17 недоступен на этой машине; все артефакты — результат
моделирования):
  1. базовая часть 250 мс: PSC = 7999, ARR = 249 -> фронты строго через
     250 мс, полный период меандра 500 мс;
  2. T1 = 80 мс (ARR = 79) и T2 = 40 мс (ARR = 39): меняется только ARR;
  3. диагностика ARR+100: ARR = 39 -> 139 даёт 140 мс (в 3,5 раза больше
     T2, отклонение 250 %), после возврата ARR = 39 интервал 40 мс
     подтверждается снова;
  4. полная последовательность варианта 4: 250 -> T1 -> T2 -> ARR+100 ->
     возврат, по EVENTS_PER_PHASE событий обновления на фазу (в каждой
     фазе не менее пяти измеренных фронт-фронт интервалов).

Негативные тесты (диагностика «нет фронтов», п. 5 TZ):
  a. DIER.UIE = 0   -> прерывание не берётся: PA1 не переключается,
     но UIF устанавливается при каждом событии обновления;
  b. TIM2_IRQn выкл. в NVIC -> тот же результат (фронтов нет, UIF = 1).

Семантика регистров (RM0008):
  * PSC/ARR предзагружены: записанное значение попадает в рабочий регистр
    только при событии обновления (EGR.UG или переполнение CNT), поэтому
    запись ARR посреди интервала не меняет текущий интервал;
  * SR.UIF — семантика rc_w0: очищается записью 0, запись 1 не влияет;
  * событие обновления: загрузка PSC/ARR, CNT = 0, UIF = 1; прерывание
    берётся только при DIER.UIE = 1 И разрешённой линии NVIC.

Времена в модели — дискретные отсчёты CNT (1 отсчёт = 1 мс при PSC = 7999),
без искусственного дрожания: относительное отклонение δT = |Tзам-Tзад|/Tзад
* 100 % равно ровно 0 для всех штатных опытов.

Артефакты: out/tim2_results.json, out/tim2_waveform.csv,
img/waveform-base.png, img/waveform-t1.png, img/waveform-t2.png.
Код выхода 0 только если все тесты прошли.
"""

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tim2_model import (  # noqa: E402
    BASE_MS,
    DIAG_ARR_OFFSET,
    EVENTS_PER_PHASE,
    PSC_DEFAULT,
    T1_MS,
    T2_MS,
    TIM2_IRQn,
    TIM2CLK_HZ,
    UIF,
    UG,
    MCU,
    interval_init,
    run_experiment,
    run_ms,
    run_until_edges,
    run_until_updates,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")
IMG_DIR = os.path.join(ROOT, "img")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

JSON_PATH = os.path.join(OUT_DIR, "tim2_results.json")
CSV_PATH = os.path.join(OUT_DIR, "tim2_waveform.csv")
PNG_PATHS = {
    "base": os.path.join(IMG_DIR, "waveform-base.png"),
    "t1": os.path.join(IMG_DIR, "waveform-t1.png"),
    "t2": os.path.join(IMG_DIR, "waveform-t2.png"),
}

# Ожидаемые фазы последовательности варианта 4: (рабочий ARR, имя, Tзад, мс).
EXPECTED_PHASES = [
    (BASE_MS - 1, "Базовая часть", BASE_MS),
    (T1_MS - 1, "T1", T1_MS),
    (T2_MS - 1, "T2", T2_MS),
    (T2_MS - 1 + DIAG_ARR_OFFSET, "Диагностика ARR+100", T2_MS + DIAG_ARR_OFFSET),
    (T2_MS - 1, "Возврат T2", T2_MS),
]

# Результат прогона последовательности (общий для артефактов) — кладёт сюда
# test_variant4_sequence, если прогон удался.
SEQ = None


# ---------------------------------------------------------------------------
# Измерения
# ---------------------------------------------------------------------------
def intervals_of(times):
    """Расстояния между соседними фронтами, мс."""
    return [round(times[i + 1] - times[i], 6) for i in range(len(times) - 1)]


def periods_of(times):
    """Полные периоды меандра (фронт через фронт), мс."""
    return [round(times[i + 2] - times[i], 6) for i in range(len(times) - 2)]


def delta_pct(t_zam, t_zad):
    """δT = |Tзам - Tзад| / Tзад * 100 %."""
    return abs(t_zam - t_zad) / t_zad * 100.0


def group_intervals(edges):
    """Группировка фронт-фронт интервалов по ARR, управлявшему интервалом.

    edges[i]["arr"] — рабочий ARR, закончивший интервал edges[i-1] -> edges[i].
    Возвращает список {"arr", "intervals", "i0", "i1"}: интервалы группы и
    диапазон индексов фронтов edges[i0..i1], между которыми они измерены.
    """
    groups = []
    for i in range(1, len(edges)):
        arr = edges[i]["arr"]
        d = round(edges[i]["t_ms"] - edges[i - 1]["t_ms"], 6)
        if not groups or groups[-1]["arr"] != arr:
            groups.append({"arr": arr, "intervals": [], "i0": i - 1, "i1": i - 1})
        groups[-1]["intervals"].append(d)
        groups[-1]["i1"] = i
    return groups


# ---------------------------------------------------------------------------
# Позитивные тесты
# ---------------------------------------------------------------------------
def test_formula():
    """Проверка общей формулой T = (PSC+1)*(ARR+1)/fTIM из TZ."""
    assert TIM2CLK_HZ // (PSC_DEFAULT + 1) == 1000, "PSC=7999 должен дать fCNT = 1 кГц"
    for arr, t_ms in (
        (BASE_MS - 1, BASE_MS),
        (T1_MS - 1, T1_MS),
        (T2_MS - 1, T2_MS),
        (T2_MS - 1 + DIAG_ARR_OFFSET, T2_MS + DIAG_ARR_OFFSET),
    ):
        t = (PSC_DEFAULT + 1) * (arr + 1) / TIM2CLK_HZ * 1000.0
        assert abs(t - t_ms) < 1e-9, (
            f"ARR={arr}: формула даёт {t} мс, ожидалось {t_ms} мс"
        )
    return "формула T = (PSC+1)*(ARR+1)/fTIM: 250/80/40/140 мс — совпадает"


def test_base_250():
    """Базовая часть: фронты строго через 250 мс, период 500 мс, δT = 0."""
    times = run_experiment(BASE_MS, 9)
    assert len(times) == 9, f"ожидалось 9 фронтов, получено {len(times)}"
    iv = intervals_of(times)
    assert all(abs(x - BASE_MS) < 1e-9 for x in iv), f"интервалы {iv} != 250 мс"
    per = periods_of(times)
    assert all(abs(x - 2 * BASE_MS) < 1e-9 for x in per), f"периоды {per} != 500 мс"
    t_zam = sum(iv) / len(iv)
    assert delta_pct(t_zam, BASE_MS) == 0.0, "δT базовой части должен быть ровно 0"
    return (
        f"9 фронтов, интервалы = 250 мс, период = 500 мс, Tзам = {t_zam:g} мс, δT = 0 %"
    )


def test_t1_t2_only_arr():
    """T1 = 80 мс и T2 = 40 мс: между конфигурациями меняется только ARR."""
    m1 = MCU()
    interval_init(m1, T1_MS)
    m2 = MCU()
    interval_init(m2, T2_MS)
    t1, t2 = m1.tim2, m2.tim2
    assert t1.PSC == t2.PSC == PSC_DEFAULT, "PSC должен остаться 7999"
    assert t1.arr_active == T1_MS - 1 and t2.arr_active == T2_MS - 1, (
        f"рабочие ARR = {t1.arr_active}/{t2.arr_active}, ожидались 79/39"
    )
    snap1 = (t1.CR1, t1.DIER, m1.nvic.enabled, m1.gpioa.odr, m1.update_count)
    snap2 = (t2.CR1, t2.DIER, m2.nvic.enabled, m2.gpioa.odr, m2.update_count)
    assert snap1 == snap2, (
        "кроме ARR при переходе T1 -> T2 не должно меняться больше ничего"
    )
    for t_ms, n_evt in ((T1_MS, 7), (T2_MS, 7)):
        times = run_experiment(t_ms, n_evt)
        iv = intervals_of(times)
        assert all(abs(x - t_ms) < 1e-9 for x in iv), f"T={t_ms}: интервалы {iv}"
        per = periods_of(times)
        assert all(abs(x - 2 * t_ms) < 1e-9 for x in per), f"T={t_ms}: периоды {per}"
        assert delta_pct(sum(iv) / len(iv), t_ms) == 0.0, f"T={t_ms}: δT != 0"
    return "T1: 80 мс (ARR=79), T2: 40 мс (ARR=39); изменён только ARR, δT = 0 %"


def test_fault_arr_plus_100():
    """Диагностика ARR+100 на T2: 140 мс (×3,5), затем возврат к 40 мс."""
    mcu = MCU()
    interval_init(mcu, T2_MS)  # ARR = 39 -> 40 мс
    run_until_edges(mcu, 1)
    # Как в main_variant4.c: диагностическая запись ARR после события обновления.
    mcu.tim2.write_arr(T2_MS - 1 + DIAG_ARR_OFFSET)  # ARR = 39 + 100 = 139
    assert mcu.tim2.arr_active == T2_MS - 1, "предзагрузка: рабочий ARR ещё 39"
    run_until_edges(mcu, 8)
    edges = mcu.gpioa.edges
    fault_iv = intervals_of([e["t_ms"] for e in edges])[1:]  # первый интервал ещё 40 мс
    assert len(fault_iv) >= 5, f"измерено всего {len(fault_iv)} интервалов"
    assert all(abs(x - (T2_MS + DIAG_ARR_OFFSET)) < 1e-9 for x in fault_iv), (
        f"интервалы {fault_iv} != 140 мс"
    )
    assert fault_iv[0] / T2_MS == 3.5, "интервал должен вырасти в 3,5 раза"
    assert delta_pct(sum(fault_iv) / len(fault_iv), T2_MS + DIAG_ARR_OFFSET) == 0.0, (
        "δT от Tзад=140 != 0"
    )
    dev_t2 = delta_pct(sum(fault_iv) / len(fault_iv), T2_MS)
    assert dev_t2 == 250.0, f"отклонение от T2 = {dev_t2} %, ожидалось 250 %"
    # Возврат правильной конфигурации: только ARR = 39.
    n0 = len(mcu.gpioa.edges)
    mcu.tim2.write_arr(T2_MS - 1)
    run_until_edges(mcu, n0 + 6)
    back = [e["t_ms"] for e in mcu.gpioa.edges[n0:]]
    back_iv = intervals_of(back)
    assert len(back_iv) >= 5 and all(abs(x - T2_MS) < 1e-9 for x in back_iv), (
        f"после возврата ARR=39 интервалы {back_iv} != 40 мс"
    )
    return (
        f"ARR+100: 140 мс (×3,5 от T2, δT = 250 %); возврат ARR=39: 40 мс подтверждён"
    )


def test_negative_uie_disabled():
    """UIE = 0: прерывание не берётся — фронтов нет, UIF = 1 («нет фронтов»)."""
    mcu = MCU()
    interval_init(mcu, BASE_MS, ui=False)
    run_ms(mcu, 1000)
    assert mcu.gpioa.edges == [], (
        f"PA1 переключился {len(mcu.gpioa.edges)} раз при UIE=0"
    )
    assert mcu.tim2.SR & UIF, "UIF должен быть установлен при каждом событии обновления"
    assert mcu.update_events >= 3, "события обновления должны были происходить"
    assert mcu.update_count == 0, "обработчик не должен был выполниться"
    return f"UIE=0: фронтов нет, UIF=1, событий обновления {mcu.update_events}, g_update_count = 0"


def test_negative_nvic_disabled():
    """NVIC выкл.: линия TIM2_IRQn не разрешена — снова «нет фронтов»."""
    mcu = MCU()
    interval_init(mcu, BASE_MS, ui=True, nvic=False)
    run_ms(mcu, 1000)
    assert mcu.gpioa.edges == [], "PA1 не должен переключаться при выключенном NVIC"
    assert mcu.tim2.SR & UIF, "UIF должен быть установлен"
    assert mcu.update_count == 0, "обработчик не должен был выполниться"
    assert not mcu.nvic.is_enabled(TIM2_IRQn), "проверка: линия действительно выключена"
    return f"NVIC выкл.: фронтов нет, UIF=1, событий обновления {mcu.update_events}"


def test_preload_semantics():
    """Запись ARR посреди интервала не меняет текущий интервал (RM0008)."""
    mcu = MCU()
    interval_init(mcu, BASE_MS)  # рабочий ARR = 249 -> 250 мс
    run_ms(mcu, 100)  # середина интервала
    mcu.tim2.write_arr(T1_MS - 1)  # запись ARR = 79 в предзагрузку
    assert mcu.tim2.arr_active == BASE_MS - 1, "рабочий регистр ARR должен остаться 249"
    run_until_edges(mcu, 1)
    e1 = mcu.gpioa.edges[-1]["t_ms"]
    assert abs(e1 - BASE_MS) < 1e-9, (
        f"текущий интервал изменился: первый фронт в {e1} мс, ожидался 250"
    )
    run_until_edges(mcu, 3)
    e2 = mcu.gpioa.edges[-2]["t_ms"]
    e3 = mcu.gpioa.edges[-1]["t_ms"]
    assert abs(e2 - e1 - T1_MS) < 1e-9, (
        f"после события обновления интервал {e2 - e1} != 80 мс"
    )
    assert abs(e3 - e2 - T1_MS) < 1e-9, f"следующий интервал {e3 - e2} != 80 мс"
    return "запись ARR=79 посреди интервала: текущий интервал 250 мс сохранён, следующие 80 мс"


def test_ug_and_uif_rc_w0():
    """EGR.UG: немедленная загрузка PSC/ARR, сброс CNT, UIF=1; SR — rc_w0.

    Проверяется вся запись SR, а не только бит UIF: различие rc_w0 и обычной
    записи — в записи 1 в уже очищенные биты (1 не должен их поднять).
    """
    mcu = MCU()
    tim = mcu.tim2
    tim.write_psc(PSC_DEFAULT)
    tim.write_arr(BASE_MS - 1)
    tim.CNT = 123
    tim.write_egr(UG)
    assert tim.CNT == 0, "UG должен немедленно обнулить CNT"
    assert tim.psc_active == PSC_DEFAULT and tim.arr_active == BASE_MS - 1, (
        "UG должен загрузить PSC и ARR"
    )
    assert tim.SR == UIF, f"UG должен установить только UIF: SR = 0x{tim.SR:04X}"
    # Очистка записью 0 (как TIM2->SR = (uint16_t)~TIM_SR_UIF в обработчике):
    # rc_w0 — обнуляется вся запись, а не только бит UIF.
    tim.SR = 0xFFFE
    assert tim.SR == 0, f"запись 0xFFFE должна очистить SR: 0x{tim.SR:04X} (rc_w0)"
    # Различающий случай rc_w0: запись 1 в уже очищенные биты.
    tim.write_egr(UG)  # UIF = 1
    assert tim.SR == UIF, f"после UG SR = 0x{tim.SR:04X}, ожидался 0x{UIF:04X}"
    tim.SR = 0x0000  # очистка rc_w0
    assert tim.SR == 0, f"запись 0 должна обнулить SR: 0x{tim.SR:04X}"
    tim.SR = 0xFFFF  # запись 1 в очищенный бит не должна его поднять
    assert tim.SR == 0, (
        f"запись 1 не должна устанавливать очищенный rc_w0-бит: SR = 0x{tim.SR:04X}"
    )
    tim.write_egr(UG)
    assert tim.SR == UIF, "после повторного UG SR должен содержать только UIF"
    tim.SR = 0xFFFE  # запись 0 очищает UIF, остальные биты и так нули
    assert tim.SR == 0, f"запись 0 должна очистить SR: 0x{tim.SR:04X}"
    return (
        "UG: CNT=0, PSC/ARR загружены, UIF=1; SR — rc_w0 по всей записи "
        "(0 очищает, 1 в очищенный бит не поднимает)"
    )


# ---------------------------------------------------------------------------
# Полная последовательность варианта 4 (как main() в main_variant4.c)
# ---------------------------------------------------------------------------
def test_variant4_sequence():
    """Фазная машина main_variant4.c: 250 -> T1 -> T2 -> ARR+100 -> возврат.

    После EVENTS_PER_PHASE событий обновления выполняется только запись
    нового ARR (предзагрузка: новый интервал вступает в силу со следующего
    события обновления). Измерения группируются по ARR, управлявшему каждым
    интервалом.
    """
    global SEQ
    mcu = MCU()
    interval_init(mcu, BASE_MS)
    arr_phases = [
        (T1_MS - 1, T1_MS),  # переход к T1: ARR = 79
        (T2_MS - 1, T2_MS),  # переход к T2: только ARR = 39
        (T2_MS - 1 + DIAG_ARR_OFFSET, T2_MS + DIAG_ARR_OFFSET),  # ARR+100 = 139
        (T2_MS - 1, T2_MS),  # возврат ARR = 39
    ]
    for arr, _t in arr_phases:
        run_until_updates(mcu, mcu.update_count + EVENTS_PER_PHASE)
        mcu.tim2.write_arr(arr)
    run_until_updates(mcu, mcu.update_count + EVENTS_PER_PHASE)  # финальная фаза

    edges = mcu.gpioa.edges
    assert len(edges) == EVENTS_PER_PHASE * 5, (
        f"ожидалось {EVENTS_PER_PHASE * 5} фронтов, получено {len(edges)}"
    )
    assert mcu.update_count == EVENTS_PER_PHASE * 5, (
        "g_update_count должен равняться числу фронтов"
    )

    groups = group_intervals(edges)
    expect = EXPECTED_PHASES
    assert [g["arr"] for g in groups] == [e[0] for e in expect], (
        f"порядок ARR в фазах: {[g['arr'] for g in groups]}"
    )
    records = []
    for g, (arr, name, t_zad) in zip(groups, expect):
        iv = g["intervals"]
        assert len(iv) >= 5, (
            f"«{name}»: измерено только {len(iv)} интервалов (нужно >= 5)"
        )
        assert all(abs(x - (arr + 1)) < 1e-9 for x in iv), (
            f"«{name}»: интервалы {iv} != {arr + 1} мс"
        )
        t_zam = sum(iv) / len(iv)
        # Полный период — той же функцией periods_of, что и в остальных тестах.
        per = periods_of([edges[i]["t_ms"] for i in range(g["i0"], g["i1"] + 1)])
        dev_t2 = delta_pct(t_zam, T2_MS)
        rec = {
            "name": name,
            "T_zad_ms": t_zad,
            "PSC": PSC_DEFAULT,
            "ARR": arr,
            "fCNT_Hz": TIM2CLK_HZ // (PSC_DEFAULT + 1),
            "intervals_ms": iv,
            "T_zam_ms": round(t_zam, 3),
            "full_period_ms": round(sum(per) / len(per), 3),
            "delta_T_pct": round(delta_pct(t_zam, t_zad), 2),
        }
        if name.startswith("Диагностика"):
            rec["T_ref_T2_ms"] = T2_MS
            rec["deviation_from_T2_pct"] = round(dev_t2, 2)
            rec["interval_growth_x"] = round(t_zam / T2_MS, 3)
            assert rec["delta_T_pct"] == 0.0, (
                "δT диагностики от Tзад = 140 мс должен быть 0"
            )
            assert dev_t2 == 250.0, (
                f"отклонение 140 мс от T2 = {dev_t2} %, ожидалось 250 %"
            )
        else:
            assert rec["delta_T_pct"] == 0.0, (
                f"«{name}»: δT = {rec['delta_T_pct']} % != 0"
            )
        assert rec["full_period_ms"] == 2 * (arr + 1), (
            f"«{name}»: полный период != {2 * (arr + 1)} мс"
        )
        records.append(rec)

    # Переходные интервалы: записанный ARR применяется со следующего события.
    trans = [
        round(
            edges[i * EVENTS_PER_PHASE]["t_ms"]
            - edges[i * EVENTS_PER_PHASE - 1]["t_ms"],
            6,
        )
        for i in range(1, 5)
    ]
    assert trans == [BASE_MS, T1_MS, T2_MS, T2_MS + DIAG_ARR_OFFSET], (
        f"переходные интервалы {trans} != [250, 80, 40, 140] — предзагрузка нарушена"
    )
    SEQ = {
        "mcu": mcu,
        "edges": edges,
        "groups": groups,
        "records": records,
        "transition_intervals_ms": trans,  # измеренные, не заданные
    }
    return (
        "5 фаз x 8 событий = 40 фронтов; фазы 250/80/40/140/40 мс, "
        "δT = 0 % везде, диагностика: 250 % от T2, переходы 250/80/40/140 мс"
    )


# ---------------------------------------------------------------------------
# Артефакты: CSV + временные диаграммы + JSON
# ---------------------------------------------------------------------------
def export_waveform_csv(path):
    """Табличные данные фронтов PA1 (используются для диаграмм)."""
    edges = SEQ["edges"]
    phase_of_edge = {}
    for g, (_arr, name, _t) in zip(group_intervals(edges), EXPECTED_PHASES):
        # Интервалы группы заканчиваются на фронтах i0+1 .. i1.
        for i in range(g["i0"] + 1, g["i1"] + 1):
            phase_of_edge[i] = name
    phase_of_edge[0] = EXPECTED_PHASES[0][1]  # первый фронт — базовая часть
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["phase", "t_ms", "pa1", "interval_ms", "arr_active"])
        w.writerow([EXPECTED_PHASES[0][1], "0", "0", "", EXPECTED_PHASES[0][0]])
        for i, e in enumerate(edges):
            iv = "" if i == 0 else round(e["t_ms"] - edges[i - 1]["t_ms"], 6)
            w.writerow(
                [phase_of_edge.get(i, ""), f"{e['t_ms']:g}", e["level"], iv, e["arr"]]
            )
    return path


def render_phase_png(edges, group, t_zad, name, path):
    """Временная диаграмма меандра PA1 для одной фазы (ч/б, для отчёта).

    Показывает не менее пяти измеренных фронт-фронт интервалов с подписями
    длительностей и полный период меандра 2T.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    i0, i1 = group["i0"], group["i1"]
    T = float(t_zad)
    # Окно: контекст слева (последний фронт предыдущей фазы) и все фронты
    # фазы. Справа контекст НЕ рисуется: следующий фронт мог бы уже
    # относиться к другой фазе (другой длительности).
    pts = []
    if i0 > 0:
        pts.append((edges[i0 - 1]["t_ms"], edges[i0 - 1]["level"]))
        start_j = i0
    else:
        pts.append((edges[0]["t_ms"] - T, 0))  # PA1 = 0 до первого события
        start_j = 0
    for j in range(start_j, i1 + 1):
        pts.append((edges[j]["t_ms"], edges[j]["level"]))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]

    fig, ax = plt.subplots(figsize=(10, 4.3), dpi=150)
    for j in range(i0, i1 + 1):
        ax.axvline(edges[j]["t_ms"], color="0.75", lw=0.8, ls=(0, (4, 4)), zorder=1)
    ax.step(xs, ys, where="post", color="black", lw=1.9, zorder=3)

    # Пять измеренных интервалов подряд — стрелками над сигналом.
    n_ann = min(5, i1 - i0)
    for k in range(n_ann):
        x0 = edges[i0 + k]["t_ms"]
        x1 = edges[i0 + k + 1]["t_ms"]
        ax.annotate(
            "",
            xy=(x1, 1.30),
            xytext=(x0, 1.30),
            arrowprops=dict(arrowstyle="<->", lw=1.1, color="black"),
            zorder=4,
        )
        ax.text(
            (x0 + x1) / 2,
            1.40 if k % 2 == 0 else 1.63,
            f"{x1 - x0:g} мс",
            ha="center",
            va="bottom",
            fontsize=12,
            zorder=4,
        )
    # Полный период меандра 2T — стрелкой под сигналом.
    x0 = edges[i0]["t_ms"]
    x2 = edges[min(i0 + 2, i1)]["t_ms"]
    ax.annotate(
        "",
        xy=(x2, -0.42),
        xytext=(x0, -0.42),
        arrowprops=dict(arrowstyle="<->", lw=1.1, color="black"),
        zorder=4,
    )
    ax.text(
        (x0 + x2) / 2,
        -0.60,
        f"полный период 2T = {x2 - x0:g} мс",
        ha="center",
        va="top",
        fontsize=12,
        zorder=4,
    )

    xlim_l = 0.0 if xs[0] == 0 else xs[0] - 0.3 * T  # время не уходит в минус
    ax.set_xlim(xlim_l, xs[-1] + 0.3 * T)
    ax.set_ylim(-1.05, 2.05)
    ax.set_yticks([0, 1])
    ax.set_xlabel("Время, мс", fontsize=13)
    ax.set_ylabel("Уровень PA1, лог. усл. ед.", fontsize=13)
    ax.tick_params(labelsize=11)
    ax.grid(axis="y", ls=":", color="0.85")
    ax.set_title(
        f"{name}: Tзад = {t_zad:g} мс, PSC = {PSC_DEFAULT}, ARR = {group['arr']}, "
        f"fCNT = 1 кГц\n"
        f"модель TIM2, ПР №5-6 вариант 4: {n_ann} измеренных фронт-фронт "
        f"интервалов и полный период",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    assert os.path.getsize(path) > 0, f"пустой файл диаграммы: {path}"
    return path


def render_waveforms():
    """Диаграммы базовой части, T1 и T2 (img/waveform-*.png)."""
    edges = SEQ["edges"]
    groups = SEQ["groups"]
    written = []
    for key, idx in (("base", 0), ("t1", 1), ("t2", 2)):
        _arr, name, t_zad = EXPECTED_PHASES[idx]
        written.append(
            render_phase_png(edges, groups[idx], t_zad, name, PNG_PATHS[key])
        )
    return written


def write_results_json(path, test_results, artifacts):
    """JSON-отчёт: по записи на каждый опыт + отдельная запись диагностики."""
    if SEQ is None:
        # Последовательность не удалась: пишем хотя бы результаты тестов.
        report = {
            "work": "ПР №5-6. Модель TIM2, STM32F103C8",
            "variant": 4,
            "experiments": [],
            "tests": [
                {"name": n, "ok": bool(o), "detail": d} for n, o, d in test_results
            ],
            "all_pass": False,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report
    records = SEQ["records"]
    fault = next(r for r in records if r["name"].startswith("Диагностика"))
    negatives = {
        name: detail
        for name, ok, detail in test_results
        if name.startswith("test_negative")
    }
    report = {
        "work": "ПР №5-6. Организация заданных временных интервалов TIM2, STM32F103C8",
        "variant": 4,
        "note": (
            "Proteus 8.17 недоступен на этой машине (macOS): все измерения "
            "сняты с реестровой модели TIM2, а не из Proteus."
        ),
        "settings": {
            "clock": "HSI 8 МГц, APB1 делитель 1 -> PCLK1 = TIM2CLK = 8 МГц",
            "TIM2CLK_Hz": TIM2CLK_HZ,
            "PSC": PSC_DEFAULT,
            "fCNT_Hz": TIM2CLK_HZ // (PSC_DEFAULT + 1),
            "tick_ms": 1,
            "PA1": "обычный GPIO push-pull, инверсия в TIM2_IRQHandler",
            "events_per_phase": EVENTS_PER_PHASE,
            "formula": "T = (PSC+1)*(ARR+1)/fTIM; при PSC = 7999: ARR = Tмс - 1",
        },
        "experiments": records,
        "diagnostic_fault": fault,
        "sequence": {
            "order": [p[1] for p in EXPECTED_PHASES],
            "total_edges": len(SEQ["edges"]),
            "transition_intervals_ms": SEQ["transition_intervals_ms"],
            "comment": (
                "переходные интервалы равны длительности старого ARR: записанный "
                "ARR вступает в силу только на следующем событии обновления "
                "(предзагрузка PSC/ARR, RM0008)"
            ),
        },
        "negative_diagnostics": negatives,
        "artifacts": {
            "results_json": "out/tim2_results.json",
            "waveform_csv": "out/tim2_waveform.csv",
            "waveform_png": sorted(
                os.path.relpath(p, ROOT).replace(os.sep, "/")
                for p in PNG_PATHS.values()
            ),
        },
        "tests": [
            {"name": name, "ok": bool(ok), "detail": detail}
            for name, ok, detail in test_results
        ],
        "all_pass": all(ok for _n, ok, _d in test_results) and bool(artifacts),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
TESTS = [
    test_formula,
    test_base_250,
    test_t1_t2_only_arr,
    test_fault_arr_plus_100,
    test_negative_uie_disabled,
    test_negative_nvic_disabled,
    test_preload_semantics,
    test_ug_and_uif_rc_w0,
    test_variant4_sequence,
]


def main():
    import traceback

    print("=== ПР №5-6, вариант 4: результаты моделирования TIM2 ===")
    results = []
    for fn in TESTS:
        try:
            detail = fn()
            results.append((fn.__name__, True, detail))
            print(f"[PASS] {fn.__name__}: {detail}")
        except Exception as exc:  # noqa: BLE001 — тестовый раннер
            tb = traceback.format_exc().strip().splitlines()
            results.append((fn.__name__, False, f"{type(exc).__name__}: {exc}"))
            print(f"[FAIL] {fn.__name__}: {type(exc).__name__}: {exc}")
            for line in tb[-3:-1]:
                print(f"       {line.strip()}")

    artifacts = False
    if SEQ is not None:
        try:
            export_waveform_csv(CSV_PATH)
            render_waveforms()
            artifacts = True
            print(
                f"[PASS] артефакты: CSV + 3 диаграммы записаны в {OUT_DIR} / {IMG_DIR}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] артефакты: {type(exc).__name__}: {exc}")
            traceback.print_exc()
    else:
        print(
            "[FAIL] артефакты: прогон последовательности не удался, данные недоступны"
        )

    report = write_results_json(JSON_PATH, results, artifacts)
    all_pass = report["all_pass"]

    print(f"JSON : {JSON_PATH}")
    print(f"CSV  : {CSV_PATH}")
    for key in ("base", "t1", "t2"):
        print(f"PNG  : {PNG_PATHS[key]}")
    print("ALL PASS" if all_pass else "SOME TESTS FAILED")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
