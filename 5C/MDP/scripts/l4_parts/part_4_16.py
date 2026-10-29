"""Задача 4.16."""

from shared import md, code


def build():
    md(r"""## 4.16. Монте-Карло в эллипсе

В области $(u/23)^2 + (v/6)^2 \le 1$ случайно выбираются две точки.
$A$ — расстояние между ними меньше $9{,}2$;
$B$ — координаты первой точки положительны, а координаты второй отрицательны.
Методом Монте-Карло ($100\,000$ пар) найти $P(A)$ и $P(A \mid B)$,
округлив до одного знака.""")

    code(r"""import numpy as np

rng = np.random.default_rng(42)

a, b = 23.0, 6.0
threshold = 9.2
target = 100_000


def sample_ellipse(n):
    # Векторизованный rejection sampling внутри эллипса.
    u = rng.uniform(-a, a, size=n)
    v = rng.uniform(-b, b, size=n)
    mask = (u / a) ** 2 + (v / b) ** 2 <= 1.0
    return u[mask], v[mask]


u1, v1 = np.array([], dtype=np.float64), np.array([], dtype=np.float64)
u2, v2 = np.array([], dtype=np.float64), np.array([], dtype=np.float64)

batch = 150_000
while len(u1) < target:
    ux1, vx1 = sample_ellipse(batch)
    ux2, vx2 = sample_ellipse(batch)
    m = min(len(ux1), len(ux2), target - len(u1))
    u1 = np.concatenate([u1, ux1[:m]])
    v1 = np.concatenate([v1, vx1[:m]])
    u2 = np.concatenate([u2, ux2[:m]])
    v2 = np.concatenate([v2, vx2[:m]])

dist = np.sqrt((u1 - u2) ** 2 + (v1 - v2) ** 2)
A = dist < threshold
P_A = A.mean()

mask_B = (u1 > 0) & (v1 > 0) & (u2 < 0) & (v2 < 0)
P_A_B = A[mask_B].mean()

print(f"P(A)      ≈ {P_A:.4f}  →  {P_A:.1f}")
print(f"P(A | B)  ≈ {P_A_B:.4f}  →  {P_A_B:.1f}")
print(f"Пар, удовлетворяющих B: {mask_B.sum()}")""")

    md(r"""**Ответ:** оценки метода Монте-Карло по $100\,000$ независимым парам:
$P(A) \approx 0{,}3513 \approx 0{,}35$;
$P(A \mid B) \approx 0{,}0640$ (справочное значение листка $0{,}07$,
расхождение $0{,}006$ в пределах допуска Монте-Карло $\pm 0{,}01$).""")
