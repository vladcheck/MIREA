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

# --- Импорты ---
md(r"""## Импорты""")
code(r"""import os
import sys
import time
sys.path.insert(0, os.getcwd())
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from logistic_regression import LogisticRegressionGD
from data_pipeline import load_clean_split, scaled_matrix""")

# --- Данные примера ---
md(
    r"""## Данные примера

В данных есть выбросы x=100 и x=200. Они сильно влияют на МНК; логистическая кривая устойчивее."""
)
code(r"""# x — расходы на рекламу, Y — эффект (0/1)
x = pd.DataFrame(np.array([39, 36, 60, 21, 27, 12, 51, 57, 54, 42, 18, 9, 48, 66, 6, 30, 24, 33, 15, 21, 100, 200]))
Y = pd.DataFrame(np.array([1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1]))
plt.scatter(x, Y, label="Наблюдения")
plt.title("Расходы на рекламу и эффект")
plt.xlabel("Расходы на рекламу (x)")
plt.ylabel("Эффект (Y)")
plt.legend()""")

# --- МНК и логистическая регрессия ---
md(
    r"""## МНК и логистическая регрессия

МНК даёт значения вне [0,1] и чувствителен к выбросам. Для бинарного отклика используем логистическую регрессию."""
)
code(r"""# МНК; чувствителен к выбросам x=100, 200
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

code(r"""# Intercept-столбец: свободный сдвиг сигмоиды
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

code(r"""# Предсказания и коэффициенты CE и LL
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

code(r"""# Сравниваем CE и LL по кривым обучения и метрикам
plt.plot(steps_CE, errors_CE, label="CE")
plt.plot(steps_LL, errors_LL, label="LL")
plt.title("Кривые обучения: CE и LL")
plt.xlabel("Шаг")
plt.ylabel("Ошибка")
plt.legend()
for tag, m in [("CE", regr_CE), ("LL", regr_LL)]:
    print(tag, "accuracy:", m.accuracy(x_, Y), "precision:", m.precision(x_, Y), "recall:", m.recall(x_, Y), "f1:", m.f1(x_, Y))""")

# --- Данные insclass ---
md(
    r"""## Данные insclass

Страховые договоры: 151406 строк, 10 числовых признаков + target. Тестового файла нет — held-out split 70/15/15."""
)

# --- insclass: загрузка ---
code(r"""TRAIN_CSV = os.path.join("docs", "insclass_train.csv")
train, validate, test, scaler = load_clean_split(TRAIN_CSV)
print(len(train), len(validate), len(test))
train.describe()""")

code(r"""# StandardScaler fit только на train, чтобы не допустить утечки.
# 10000 шагов, как в методичке.
Xtr, ytr = scaled_matrix(train, scaler)
Xva, yva = scaled_matrix(validate, scaler)
m_ll, m_ce = LogisticRegressionGD(), LogisticRegressionGD()
t0 = time.time(); m_ll.fit(Xtr, ytr, max_steps=10000, Rtype="LL"); t_ll = time.time() - t0
t0 = time.time(); m_ce.fit(Xtr, ytr, max_steps=10000, Rtype="CE"); t_ce = time.time() - t0
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
