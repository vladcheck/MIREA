"""Generate 'wine_knn_solution.ipynb' from md()/code() literals.

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
Датасет `docs/winequality-red.csv`, сплит 70/30 со стратификацией.""")

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
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

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

# --- 5. Баланс классов ---
md(
    r"""## Баланс классов
Классы несбалансированы — это скажется на macro-метриках."""
)
code(r"""# Распределение оценок
sns.countplot(x='quality', hue='quality', data=df)
plt.xlabel('качество')
plt.ylabel('количество')
plt.title('Распределение оценок качества вина')

# Проверяем пропуски и дубликаты
print('missing cells:', int(df.isna().sum().sum()))
print('full-row duplicates:', int(df.duplicated().sum()))
print(df['quality'].value_counts().sort_index())""")

# --- 6. display_confusion_matrix ---
md(r"""## Функция отрисовки матрицы путаницы""")
code(r"""# Отрисовка матрицы путаницы
def display_confusion_matrix(
    matrix, labels=None,
    title="Матрица путаницы",
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

# --- 7. Сплит train/test ---
md(
    r"""## Сплит train/test
Стратификация сохраняет доли классов в обеих выборках."""
)
code(r"""# Стратифицированный сплит; random_state=42 — для воспроизводимости
X = df.drop(['quality'], axis=1)
y = df['quality']

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.3, random_state=42)""")

# --- 8. kNN fit ---
md(
    r"""## Обучение
k=5 по умолчанию, без масштабирования — baseline."""
)
code(r"""# kNN, k=5 по умолчанию
knn = KNeighborsClassifier()
knn.fit(X_train, y_train)""")

# --- 9. Отчёт + accuracy ---
md(
    r"""## Метрики
Precision/recall/F1 по классам и общая accuracy."""
)
code(r"""# Метрики на тесте
preds = knn.predict(X_test)

print(classification_report(y_test, preds))
print('accuracy:', accuracy_score(y_test, preds))""")

# --- 10. Матрица путаницы ---
md(
    r"""## Матрица путаницы
Смотрим, какие оценки путаются между собой."""
)
code(r"""# Матрица путаницы
labels = y.unique()

matrix = confusion_matrix(y_test, preds, labels=labels, normalize=None)
print(matrix)

display_confusion_matrix(matrix, labels)""")

# --- 11. per-class P/R/F1 ---
md(r"""## Сводные метрики
Per-class P/R/F1 и OvR AUC из `wine_knn.py`.""")
code(r"""# Сводные метрики из wine_knn.py
import sys; sys.path.insert(0, '.')
from wine_knn import evaluate_knn
res = evaluate_knn('docs/winequality-red.csv')
for m in ('precision','recall','f1'):
    print('per-class ' + m + ':', {k: round(v,3) for k,v in res['per_class'][m].items()})
print('support_test:', res['per_class']['support_test'])
print('macro P/R/F1:', round(res['precision_macro'],4), round(res['recall_macro'],4), round(res['f1_macro'],4))
print('weighted P/R/F1:', round(res['precision_weighted'],4), round(res['recall_weighted'],4), round(res['f1_weighted'],4))
print('OvR AUC macro/weighted:', round(res['roc_auc_ovr_macro'],4), round(res['roc_auc_ovr_weighted'],4))
print('per-class OvR AUC:', {k: round(v,3) for k,v in res['per_class']['roc_auc_ovr'].items()})""")

# --- 12. recall bar ---
md(r"""## Полнота по классам""")
code(r"""# Полнота по классам
recall_by_class = res['per_class']['recall']
plt.bar(list(recall_by_class.keys()), list(recall_by_class.values()))
plt.xlabel('качество'); plt.ylabel('полнота')
plt.title('Полнота по классам (k=5, тест)'); plt.show()""")

# --- 13. k-sweep overfit ---
md(
    r"""## Зависимость от k
k=1..30: точность на обучении и тесте, macro-recall."""
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
plt.xlabel('число соседей k'); plt.ylabel('значение метрики'); plt.legend(); plt.title('Проверка переобучения: k=1..30'); plt.show()""")

# --- 14. ROC OvR ---
md(
    r"""## ROC-кривые OvR
По классам, пунктир — случайный классификатор."""
)
code(r"""# ROC OvR; AUC — доля верно упорядоченных пар (Дьяконов)
from sklearn.metrics import roc_curve
from sklearn.preprocessing import label_binarize
classes = res['classes']
y_binarized = label_binarize(res['y_test'], classes=classes)
fig, ax = plt.subplots()
for i, cls in enumerate(classes):
    fpr, tpr, _ = roc_curve(y_binarized[:, i], res['y_proba'][:, i])
    ax.plot(fpr, tpr, label=f'класс {cls} (AUC={res["per_class"]["roc_auc_ovr"][cls]:.2f})')
ax.plot([0, 1], [0, 1], linestyle='--', label='случайный классификатор')
ax.set_xlabel('Доля ложноположительных (FPR)'); ax.set_ylabel('Доля истинноположительных (TPR)'); ax.legend(fontsize=8)
plt.title('ROC-кривые OvR по классам (k=5, тест)'); plt.show()""")

# --- 15. Выводы ---
md(r"""## Выводы
- k=5: accuracy ~0.49 на тесте против ~0.64 на обучении; разрыв уменьшается с ростом k.
- Основная путаница — между оценками 5 и 6; recall классов 3, 4, 8 близок к нулю (в тесте их мало).
- Macro F1 ~0.22, weighted ~0.47 — разница отражает дисбаланс классов.
- OvR AUC macro ~0.62; оценки 3 и 8 нестабильны из-за малых выборок.
- Диапазоны признаков различаются на порядки; вариант улучшения — StandardScaler в Pipeline.""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
}

out = sys.argv[1] if len(sys.argv) > 1 else "wine_knn_solution.ipynb"
nbf.write(nb, out)
print(out, "written,", len(cells), "cells")
