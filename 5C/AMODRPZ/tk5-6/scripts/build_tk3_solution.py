"""Generate 'Текущий контроль 3.ipynb' from md()/code() literals.

Same pattern as tk7-8/scripts/build_tk4_solution.py:
linear md()/code() sequence, cells in call order, structure only
(outputs are left empty; numbers come from wine_knn.py).
Usage: uv run python scripts/build_tk3_solution.py [output.ipynb]
"""

import os
import sys

import nbformat as nbf

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from utils.shared import cells, code, md  # noqa: E402

nb = nbf.v4.new_notebook()

# --- 1. Заголовок ---
md(r"""# ТК 5-6 (ПР3): kNN — качество красного вина
Метод k ближайших соседей (kNN) - это алгоритм классификации, относящий объект к тому классу, который чаще встречается среди его k ближайших соседей в пространстве признаков.

Датасет - это таблица с данными, на которой обучается и проверяется модель. Сплит (train/test, обучающая и тестовая выборки) - это разделение датасета на обучающую часть, по которой настраивается модель, и тестовую, на которой независимо оценивается её качество. Стратификацией называют способ разбиения, при котором доли классов сохраняются в каждой из частей.

В данной работе задача сведена к бинарной классификации: качество вина разделено на два класса, подробности см. в разделе «Бинаризация».""")

# --- 2. Импорты ---
code(r"""# Импорты и настройки
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import itertools

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, roc_auc_score

%matplotlib inline
plt.rcParams["figure.figsize"] = (10,5)""")

# --- 3. Загрузка датасета ---
md(r"""## Загрузка""")
code(r"""# Читаем CSV
df = pd.read_csv('docs/winequality-red.csv')

df.head()""")

# --- 4. Описание данных ---
md(r"""## Описание данных""")
code(r"""# Типы столбцов и пропуски
df.info()""")

# --- 5. Бинаризация ---
md(
    r"""## Бинаризация
Бинарная классификация - это задача классификации, в которой объект относится к одному из двух возможных классов.

В датасете о качестве вина исходный признак `quality` принимает значения от 3 до 8. Чтобы свести задачу к бинарной, введём порог: оценки 5 и ниже считаем плохим вином (класс 0), а оценки 6 и выше — хорошим (класс 1). Порог 6 выбран как «не ниже среднего»: он даёт почти сбалансированное разбиение — 855 образцов хорошего и 744 плохого вина."""
)
code(r"""# Бинарный целевой признак: 1 — хорошее вино (quality >= 6), 0 — плохое
df['good'] = (df['quality'] >= 6).astype(int)
print(df['good'].value_counts().sort_index())""")

# --- 6. Баланс классов ---
md(
    r"""## Баланс классов
Баланс классов - это соотношение числа объектов разных классов в выборке; данные, где классы представлены сильно неравномерно, называют несбалансированными, и это сказывается на метриках качества.

На графике ниже показано распределение бинарного признака `good`: по оси x отложены классы 0 (плохое вино) и 1 (хорошее), по оси y — число образцов каждого класса. Столбцы близки по высоте, поэтому классы почти сбалансированы, а macro- и weighted-метрики качества будут близки друг к другу."""
)
code(r"""# Распределение бинарного признака good
sns.countplot(x='good', data=df)
plt.xlabel('хорошее вино (1 — да, 0 — нет)')
plt.ylabel('количество')
plt.title('Баланс классов: распределение good')

# Проверяем пропуски и дубликаты
print('missing cells:', int(df.isna().sum().sum()))
print('full-row duplicates:', int(df.duplicated().sum()))
print(df['good'].value_counts().sort_index())""")

# --- 7. Функция отрисовки матрицы путаницы ---
md(
    r"""## Функция отрисовки матрицы путаницы
Матрица путаницы - это таблица, в которой строки соответствуют фактическим классам, столбцы — предсказанным, а ячейки содержат число объектов с таким сочетанием."""
)
code(r"""# Отрисовка матрицы путаницы
def display_confusion_matrix(
    matrix, labels=None,
    title="Матрица путаницы (k=5, тестовая выборка)",
    xlabel="Предсказано",
    ylabel="Фактически",
    figsize=None,
    cmap="Blues",
    vmin=None,
    vmax=None,
):
    if labels is None:
        labels = [""]*len(matrix)
    if vmin is None:
        vmin = 0.
    if vmax is None:
        vmax = np.sum(matrix[0])
    t_hold = (vmax-vmin) / 2.
    fig,ax = plt.subplots(figsize=figsize)
    ax.imshow(matrix, cmap=cmap)
    for row,col in itertools.product(range(len(labels)), range(len(labels))):
        color = "white" if matrix[row,col] > t_hold else "black"
        ax.text(col, row, matrix[row, col], horizontalalignment="center", color=color)
    tick_marks = np.arange(len(labels))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=40, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    plt.show()""")

# --- 8. Сплит train/test ---
md(
    r"""## Сплит train/test
Стратификация сохраняет доли классов в обеих выборках."""
)
code(r"""# Стратифицированный сплит; random_state=42 — для воспроизводимости
X = df.drop(['quality', 'good'], axis=1)
y = df['good']

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.3, random_state=42)""")

# --- 9. kNN fit ---
md(
    r"""## Обучение
Baseline (базовая модель) - это простая исходная модель, служащая точкой сравнения для более сложных решений.

k=5 по умолчанию, без масштабирования — baseline."""
)
code(r"""# kNN, k=5 по умолчанию
knn = KNeighborsClassifier()
knn.fit(X_train, y_train)""")

# --- 10. Отчёт + accuracy ---
md(
    r"""## Метрики
Precision (точность) - это доля объектов, отнесённых моделью к классу, которые действительно к нему принадлежат.
Recall (полнота) - это доля объектов класса, которые модель правильно распознала.
F1-мера - это среднее гармоническое точности и полноты, объединяющее обе метрики в одно число.
Accuracy (доля правильных ответов) - это доля всех объектов, для которых модель дала верный прогноз.

Отчёт выводит precision/recall/F1 по классам и общую accuracy."""
)
code(r"""# Метрики на тесте
preds = knn.predict(X_test)

print(classification_report(y_test, preds))
print('accuracy:', accuracy_score(y_test, preds))""")

# --- 11. Матрица путаницы ---
md(
    f"""## Матрица путаницы
Строки матрицы соответствуют фактическим классам (0 — плохое вино, 1 — хорошее), столбцы — прогнозам модели; цвет ячейки и число в ней показывают, сколько образцов получили данную пару «фактический–предсказанный» класс. По диагонали отслеживаются правильные ответы, а внедиагональные ячейки показывают ложные срабатывания (плохое вино предсказано как хорошее) и пропуски (хорошее вино предсказано как плохое)."""
)
code(r"""# Матрица путаницы
labels = y.unique()

matrix = confusion_matrix(y_test, preds, labels=labels, normalize=None)
print(matrix)

display_confusion_matrix(matrix, labels)""")

# --- 12. k-sweep overfit ---
md(
    r"""## Зависимость от k
Переобучение - это ситуация, когда модель слишком точно запоминает обучающую выборку и теряет способность обобщать на новых данных.

На графике ниже по оси x отложено число соседей k, а по оси y — значения точности на обучающей и тестовой выборках и macro-recall. Разрыв между кривыми train и test позволяет оценить степень переобучения: чем ближе кривые и выше значения на тесте, тем лучше модель обобщается."""
)
code(r"""# Точность train/test при k=1..30
from wine_knn import k_sweep
rows = k_sweep('docs/winequality-red.csv')
k_values = [row['k'] for row in rows]
train_accuracy = [row['train_accuracy'] for row in rows]
test_accuracy = [row['test_accuracy'] for row in rows]
recall_macro = [row['recall_macro'] for row in rows]
plt.plot(k_values, train_accuracy, label='точность на обучении')
plt.plot(k_values, test_accuracy, label='точность на тесте')
plt.plot(k_values, recall_macro, label='макрополнота')
plt.xlabel('число соседей k'); plt.ylabel('значение метрики'); plt.legend(); plt.title('Зависимость качества от числа соседей k (train/test/macro-recall)'); plt.show()""")

# --- 13. ROC-кривая ---
md(
    r"""## ROC-кривая
Доля истинноположительных (TPR) - это доля объектов положительного класса, которых модель правильно распознала.
Доля ложноположительных (FPR) - это доля объектов отрицательного класса, которых модель ошибочно отнесла к положительному.
ROC-кривая - это график зависимости доли истинноположительных ответов (TPR) от доли ложноположительных (FPR) при изменении порога классификации.
AUC - это площадь под ROC-кривой, количественная мера способности модели различать классы.

На графике по оси x отложена доля ложноположительных ответов (FPR), по оси y — доля истинноположительных (TPR). Пунктирная диагональ соответствует случайному классификатору, а величина AUC в легенде показывает, насколько хорошо бинарная модель отделяет хорошее вино от плохого."""
)
code(r"""# ROC бинарного kNN; AUC - площадь под ROC-кривой
proba_good = knn.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, proba_good)
auc = roc_auc_score(y_test, proba_good)
plt.plot(fpr, tpr, label=f'kNN, k=5 (AUC={auc:.2f})')
plt.plot([0, 1], [0, 1], linestyle='--', label='случайный классификатор')
plt.xlabel('Доля ложноположительных (FPR)')
plt.ylabel('Доля истинноположительных (TPR)')
plt.legend()
plt.title('ROC-кривая бинарного kNN (k=5, тест)')
plt.show()""")

# --- 14. Выводы ---
md(
    r"""## Выводы
StandardScaler - это преобразование признаков, вычитающее среднее и делящее значения на стандартное отклонение, чтобы привести признаки к единому масштабу.
Pipeline - это последовательность этапов обработки данных и модели, оформленная в scikit-learn как единый объект.

- Переход от многоклассовой задачи к бинарной (качество ≥ 6 — хорошее вино) заметно упрощает постановку: accuracy k=5 на тесте ~0.64 против ~0.49 у шестиклассовой модели; классы почти сбалансированы (223/257 в тесте), поэтому macro- и weighted-метрики совпадают (~0.64).
- Precision/recall/F1 по обоим классам лежат в диапазоне ~0.60–0.68; разрыв accuracy между обучением (~0.76) и тестом указывает на переобучение, которое уменьшается с ростом k.
- Матрица путаницы показывает распределение правильных ответов и ошибок: ложные срабатывания и пропуски хорошего вина встречаются сопоставимо часто.
- ROC-кривая и AUC (~0.71) характеризуют способность модели ранжировать образцы: кривая заметно выше диагонали, но до хорошего разделения классов не дотягивает.
- Диапазоны признаков различаются на порядки; вариант улучшения — StandardScaler в Pipeline."""
)

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
}

out = sys.argv[1] if len(sys.argv) > 1 else "Текущий контроль 3.ipynb"
nbf.write(nb, out)
print(out, "written,", len(cells), "cells")
