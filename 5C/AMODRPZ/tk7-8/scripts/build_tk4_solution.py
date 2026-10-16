"""Generate 'Текущий контроль 4 - решение.ipynb' from md()/code() literals.

Same pattern as maths-for-programming-5c/scripts/build_notebook_l*.py:
linear md()/code() sequence, cells in call order, structure only
(outputs are left empty; numbers come from run_experiment.py).
Usage: uv run python scripts/build_tk4_solution.py [output.ipynb]
"""

import os
import sys

import nbformat as nbf

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from utils.shared import cells, code, md  # noqa: E402

nb = nbf.v4.new_notebook()

# --- 2. Импорты ---
md(
    r"""Импорты и настройка окружения. Добавляем текущую папку в `sys.path`, чтобы ноутбук находил локальные модули `logistic_regression` и `data_pipeline`, затем подключаем NumPy, pandas и matplotlib."""
)
code(r"""import os
import sys
import time
sys.path.insert(0, os.getcwd())
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from logistic_regression import LogisticRegressionGD
from data_pipeline import load_clean_split, scaled_matrix""")

# --- 3. Данные примера ---
md(
    r"""Данные примера из методички: `x` — расходы на рекламу, `Y` — эффект (0/1). В выборке специально есть выбросы (x = 100 и x = 200) — дальше будет видно, как они ломают прямую по МНК, а логистическая кривая их выдерживает. Строим диаграмму рассеяния, чтобы увидеть исходные точки."""
)
code(r"""# Исходные данные из методички: x — расходы на рекламу, Y — эффект (0/1)
x = pd.DataFrame(np.array([39, 36, 60, 21, 27, 12, 51, 57, 54, 42, 18, 9, 48, 66, 6, 30, 24, 33, 15, 21, 100, 200]))
Y = pd.DataFrame(np.array([1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1]))
plt.scatter(x, Y, label="Наблюдения")
plt.title("Расходы на рекламу и эффект")
plt.xlabel("Расходы на рекламу (x)")
plt.ylabel("Эффект (Y)")
plt.legend()""")

# --- 4. Прямая по МНК ---
md(
    r"""Прямая по методу наименьших квадратов (МНК) поверх тех же точек. Линейная регрессия здесь не к месту: она предсказывает значения вне отрезка [0, 1] и сильно тянется к выбросам x = 100 и x = 200 — график это наглядно показывает и мотивирует переход к логистической регрессии."""
)
code(r"""# Прямая по МНК — ломается на выбросах x=100, 200
a1 = ((x - x.mean()) * (Y - Y.mean())).mean() / ((x - x.mean()) ** 2).mean()
a0 = Y.mean() - a1 * x.mean()
x_space = np.linspace(6, 70, 20)
Y_pred = a0.item() + a1.item() * x_space
plt.plot(x_space, Y_pred, 'r', label="Прямая МНК")
plt.scatter(x, Y, label="Наблюдения")
plt.title("Прямая по МНК поверх данных примера")
plt.xlabel("Расходы на рекламу (x)")
plt.ylabel("Эффект (Y)")
plt.legend()""")

# --- 5. Обучение CE/LL с замером времени ---
md(
    r"""Обучаем логистическую регрессию двумя способами — максимизацией правдоподобия (LL) и минимизацией кросс-энтропии (CE). Столбец из единиц (intercept) добавляем, как в методичке: без него у сигмоиды не было бы свободного сдвига (порога) и модель была бы обязана проходить через начало координат. Время обучения каждого варианта замеряем — оно понадобится для сравнения а/б."""
)
code(r"""# Intercept-столбец, как в методичке
x_ = x.copy()
intercept = np.ones((x.shape[0], 1))
x_ = pd.DataFrame(np.concatenate((intercept, x), axis=1))

start_time_CE = time.time()
regr_CE = LogisticRegressionGD()
steps_CE, errors_CE = regr_CE.fit(x_, Y, alpha=0.01, epsylon=0.01, max_steps=10000, Rtype="CE")
print(f"Время обучения CE: {time.time() - start_time_CE} сек.")

start_time_LL = time.time()
regr_LL = LogisticRegressionGD()
steps_LL, errors_LL = regr_LL.fit(x_, Y, alpha=0.01, epsylon=0.01, max_steps=10000, Rtype="LL")
print(f"Время обучения LL: {time.time() - start_time_LL} сек.")""")

# --- 6. Сигмоиды и коэффициенты ---
md(
    r"""Рисуем обе обученные сигмоиды поверх исходных точек и выводим коэффициенты. Наложение предсказаний на данные показывает качество подгонки: видно, насколько кривая отделяет нули от единиц."""
)
code(r"""# Сигмоиды поверх данных + коэффициенты
plt.scatter(x, Y, label="Данные (Y)")
plt.scatter(x, regr_CE.predict(x_), label="Предсказания (CE)")
plt.title("Логистическая регрессия (CE): предсказания поверх данных")
plt.xlabel("Расходы на рекламу (x)")
plt.ylabel("Вероятность эффекта")
plt.legend()
display(regr_CE.coefs())
plt.scatter(x, Y, label="Данные (Y)")
plt.scatter(x, regr_LL.predict(x_), label="Предсказания (LL)")
plt.title("Логистическая регрессия (LL): предсказания поверх данных")
plt.xlabel("Расходы на рекламу (x)")
plt.ylabel("Вероятность эффекта")
plt.legend()
display(regr_LL.coefs())""")

# --- 7. Сравнение а/б ---
md(
    r"""Сравниваем варианты а/б (CE против LL): строим обе кривые обучения на одном графике (ось X — шаг градиентного спуска, ось Y — значение ошибки) и печатаем метрики — время обучения, accuracy, precision, recall и f1. Сравнение нужно, чтобы выбрать, какой способ обучения лучше на этих данных."""
)
code(r"""# Кривые обучения и сравнение а/б: время, accuracy, precision, recall, f1
plt.plot(steps_CE, errors_CE, label="CE")
plt.plot(steps_LL, errors_LL, label="LL")
plt.title("Кривые обучения: CE и LL")
plt.xlabel("Шаг")
plt.ylabel("Ошибка")
plt.legend()
for tag, m in [("CE", regr_CE), ("LL", regr_LL)]:
    print(tag, "accuracy:", m.accuracy(x_, Y), "precision:", m.precision(x_, Y), "recall:", m.recall(x_, Y), "f1:", m.f1(x_, Y))""")

# --- 8. insclass: постановка ---
md(
    r"""Страховые договоры (insclass): 151406 строк, 10 числовых признаков + target (1 — рисковый). Тестового файла в архиве нет — вместо него held-out split 70/15/15."""
)

# --- 9. insclass: загрузка ---
code(r"""TRAIN_CSV = os.path.join("docs", "insclass_train.csv")
train, validate, test, scaler = load_clean_split(TRAIN_CSV)
print(len(train), len(validate), len(test))
train.describe()""")

# --- 10. insclass: обучение и метрики ---
md(
    r"""Обучаем обе модели на страховых данных и считаем метрики на train и validate. Масштабирование — StandardScaler, обученный (fit) только на train: иначе в признаки просочилась бы информация из валидации (утечка данных), а без масштабирования градиентный спуск на признаках с разным разбросом расходится. Ограничиваемся 1000 шагами: полный батч (порядка 10 признаков на ~102 тыс. строк) в обычном цикле градиентного спуска считается слишком долго, а Workbook и сам демонстрировал insclass на выборке из 1000 строк."""
)
code(r"""# Признаки масштабированы StandardScaler (fit только на train) — иначе спуск расходится.
# 1000 шагов: полный батч 10000 x 102k строк в обычном GD-цикле не считается за разумное время.
Xtr, ytr = scaled_matrix(train, scaler)
Xva, yva = scaled_matrix(validate, scaler)
m_ll, m_ce = LogisticRegressionGD(), LogisticRegressionGD()
t0 = time.time(); m_ll.fit(Xtr, ytr, max_steps=1000, Rtype="LL"); t_ll = time.time() - t0
t0 = time.time(); m_ce.fit(Xtr, ytr, max_steps=1000, Rtype="CE"); t_ce = time.time() - t0
for tag, m, t in [("LL", m_ll, t_ll), ("CE", m_ce, t_ce)]:
    print(tag, f"{t:.1f} сек.", "train f1:", m.f1(Xtr, ytr), "validate accuracy:", float(np.asarray(m.accuracy(Xva, yva)).mean()), "validate f1:", m.f1(Xva, yva))""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
}

out = sys.argv[1] if len(sys.argv) > 1 else "Текущий контроль 4 - решение.ipynb"
nbf.write(nb, out)
print(out, "written,", len(cells), "cells")
