"""Сборка ноутбука «Листок 4» из ячеек с помощью nbformat."""

from shared import cells, code, md
import nbformat as nbf

from l4_parts import (
    part_4_1, part_4_2, part_4_3, part_4_4, part_4_5, part_4_6, part_4_7,
    part_4_8, part_4_9, part_4_10, part_4_11, part_4_12, part_4_13,
    part_4_14, part_4_15, part_4_16, part_4_17,
)

nb = nbf.v4.new_notebook()

md(r"""# Листок № 4. Классическое, статистическое, геометрическое определение вероятности

Для задач с числовым ответом строим график зависимости относительной частоты
$\hat p(A) = N(A)/N$ от числа реализаций опыта $N$. Используются NumPy,
Matplotlib и стандартные модули `math`/`random`.""")

code("""import math
import random
from itertools import combinations, permutations

import numpy as np
import matplotlib.pyplot as plt

%matplotlib inline

random.seed(42)


def plot_convergence(simulate_one, title, N_max=150_000, points=200):
    \"\"\"График относительной частоты события по числу испытаний.\"\"\"
    N_vals = np.unique(np.logspace(1, np.log10(N_max), points).astype(int))
    hits = np.fromiter((simulate_one() for _ in range(N_vals[-1])), dtype=np.int64)
    freqs = np.cumsum(hits)[N_vals - 1] / N_vals
    plt.figure(figsize=(8, 4))
    plt.semilogx(N_vals, freqs)
    plt.xlabel('N')
    plt.ylabel(r'$\\hat{p}(A)$')
    plt.title(title)
    plt.grid(True)
    plt.show()
    return freqs[-1]""")

for part in (part_4_1, part_4_2, part_4_3, part_4_4, part_4_5, part_4_6,
             part_4_7, part_4_8, part_4_9, part_4_10, part_4_11, part_4_12,
             part_4_13, part_4_14, part_4_15, part_4_16, part_4_17):
    part.build()

md(r"""---

Все задачи листка решены: классическое, статистическое и геометрическое
определения вероятности, встречи, монте-карло оценки.""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.14"},
}
nbf.write(nb, "notebooks/Листок-4.ipynb")
print("notebooks/Листок-4.ipynb written,", len(cells), "cells")
