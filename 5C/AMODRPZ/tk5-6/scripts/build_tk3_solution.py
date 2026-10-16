"""Generate 'wine_knn_solution.ipynb' from md()/code() literals.

Same pattern as tk7-8/scripts/build_tk4_solution.py:
linear md()/code() sequence, cells in call order, structure only
(outputs are left empty; numbers come from wine_knn.py).
Workbook: docs/Текущий контроль 3.ipynb (ТК 5-6 = ПР3, kNN);
deviations from it are marked `# отклонение:` in cell sources.
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
Код повторяет приёмы workbook `docs/Текущий контроль 3.ipynb` (ячейки 5/7/9/12/20/39–42); отклонения помечены комментарием `# отклонение:`. Оригиналы в `docs/` не меняются. `random_state=42` — отклонение (в workbook сид не задан), нужно для воспроизводимости.""")

# --- 2. Импорты (workbook, ячейка 5) ---
code(r"""#Импорт необходимых библиотек (workbook, ячейка 5; без mlxtend/datasets — они только для Iris/2D-карт)
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

# --- 3. Загрузка датасета (workbook, ячейка 7) ---
code(r"""#Загрузка датасета (workbook, ячейка 7: df + df.head())
df = pd.read_csv('docs/winequality-red.csv')

df.head()""")

# --- 4. Описание данных (workbook, ячейка 9) ---
code(r"""#Описание набора данных (workbook, ячейка 9: df.info())
df.info()""")

# --- 5. Баланс классов (workbook, ячейка 12) ---
code(r"""#Баланс классов (workbook, ячейка 12: sns.countplot)
sns.countplot(x='quality', hue='quality', data=df)

# отклонение: проверка «плохого датасета» (требование препода)
print('missing cells:', int(df.isna().sum().sum()))
print('full-row duplicates:', int(df.duplicated().sum()))
print(df['quality'].value_counts().sort_index())""")

# --- 6. display_confusion_matrix (workbook, ячейка 20) ---
code(r"""# Helper functions (workbook, ячейка 20 — дословно)
def display_confusion_matrix(
    matrix, labels=None,
    title="Confusion Matrix",
    xlabel="Predicted",
    ylabel="Actual",
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

# --- 7. Сплит train/test (workbook, ячейка 39) ---
code(r"""#Разделение на обучающий/тестовый набор (workbook, ячейка 39)
X = df.drop(['quality'], axis=1)
y = df['quality']

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.3, random_state=42)""")

# --- 8. kNN fit (workbook, ячейка 40) ---
code(r"""#Модель kNN (workbook, ячейка 40)
knn = KNeighborsClassifier()
knn.fit(X_train, y_train)""")

# --- 9. Отчёт + accuracy (workbook, ячейка 41) ---
code(r"""#Оценка: отчёт + accuracy (workbook, ячейка 41; порядок аргументов исправлен: в workbook (preds, y_test))
preds = knn.predict(X_test)

print(classification_report(y_test, preds))
print('accuracy:', accuracy_score(y_test, preds))""")

# --- 10. Матрица путаницы (workbook, ячейка 42) ---
code(r"""#Матрица путаницы (workbook, ячейка 42: labels=wine quality)
labels = y.unique()

matrix = confusion_matrix(y_test, preds, labels=labels, normalize=None)
print(matrix)

display_confusion_matrix(matrix, labels)""")

# --- 11. per-class P/R/F1 (отклонение) ---
code(r"""# отклонение: таблица per-class P/R/F1 (в workbook нет; нужно для сдачи)
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

# --- 12. recall bar (отклонение) ---
code(r"""# отклонение: recall по классам для защиты
recall_by_class = res['per_class']['recall']
plt.bar(list(recall_by_class.keys()), list(recall_by_class.values()))
plt.xlabel('quality'); plt.ylabel('recall')
plt.title('Recall per class (k=5, test)'); plt.show()""")

# --- 13. k-sweep overfit (отклонение) ---
code(r"""# отклонение: проверка обучения k=1..30 (в workbook один k)
from wine_knn import k_sweep
rows = k_sweep('docs/winequality-red.csv')
k_values = [row['k'] for row in rows]
train_accuracy = [row['train_accuracy'] for row in rows]
test_accuracy = [row['test_accuracy'] for row in rows]
recall_macro = [row['recall_macro'] for row in rows]
plt.plot(k_values, train_accuracy, label='train acc')
plt.plot(k_values, test_accuracy, label='test acc')
plt.plot(k_values, recall_macro, label='recall macro')
plt.xlabel('k'); plt.legend(); plt.title('Overfit check: k=1..30'); plt.show()""")

# --- 14. ROC OvR (отклонение) ---
code(r"""# отклонение: ROC OvR по классам (Дьяконов: AUC=доля верно упорядоченных пар)
from sklearn.metrics import roc_curve
from sklearn.preprocessing import label_binarize
classes = res['classes']
y_binarized = label_binarize(res['y_test'], classes=classes)
fig, ax = plt.subplots()
for i, cls in enumerate(classes):
    fpr, tpr, _ = roc_curve(y_binarized[:, i], res['y_proba'][:, i])
    ax.plot(fpr, tpr, label=f'class {cls} (AUC={res["per_class"]["roc_auc_ovr"][cls]:.2f})')
ax.plot([0, 1], [0, 1], linestyle='--', label='chance')
ax.set_xlabel('FPR'); ax.set_ylabel('TPR'); ax.legend(fontsize=8)
plt.title('ROC OvR per class (k=5, test)'); plt.show()""")

# --- 15. Выводы ---
md(r"""## Выводы
- kNN(k=5) без скейлинга: test accuracy ~0.49 при train ~0.64 — переобучение на малых k, разрыв виден на кривой k=1..30.
- Путаница в основном 5↔6 (мажоритарные классы); recall классов 3/4/8 ≈ 0 — в тесте их ~3/16/5 шт, kNN редкие классы не возвращает.
- Macro P/R/F1 ~0.22 против weighted ~0.46–0.49: расхождение — прямое следствие дисбаланса.
- OvR AUC macro ~0.62: ранжирование слабое; per-class AUC классов 3/8 нестабилен (малые выборки, см. Дьяконов про дисперсию AUC) — не использовать для ранжирования моделей.
- Масштабы признаков 0.01–289: для корректного kNN нужен StandardScaler (внутри Pipeline при CV); здесь осознанно оставлен протокол workbook без скейлинга.""")

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
