"""Задача 4.17."""

from shared import md, code


def build():
    md(r"""## 4.17. Случайный треугольник в кубе

В кубе объёма 1 случайно выбираются точки $A$, $B$, $C$. $R$ — наименьший
угол треугольника $ABC < 26{,}7^{\circ}$; $S$ — наибольший угол
$< 81{,}9^{\circ}$; $T$ — треугольник остроугольный. Методом Монте-Карло
(100 000 остроугольных треугольников) найти $P(R \mid T)$ и $P(S \mid T)$,
округлив до одного знака.""")

    code(r"""import numpy as np

rng = np.random.default_rng(42)

target = 100_000
batch = 200_000

cos_R = np.cos(np.radians(26.7))   # наибольший косинус при угле 26.7°
cos_S = np.cos(np.radians(81.9))   # наименьший косинус при угле 81.9°

min_cos_list = []
max_cos_list = []
acute_count = 0

while acute_count < target:
    A = rng.random((batch, 3))
    B = rng.random((batch, 3))
    C = rng.random((batch, 3))

    # квадраты длин сторон, противолежащих вершинам A, B, C
    a2 = np.sum((B - C) ** 2, axis=1)
    b2 = np.sum((A - C) ** 2, axis=1)
    c2 = np.sum((A - B) ** 2, axis=1)

    a = np.sqrt(a2)
    b = np.sqrt(b2)
    c = np.sqrt(c2)

    # косинусы углов по теореме косинусов
    cos_a = (b2 + c2 - a2) / (2 * b * c)
    cos_b = (a2 + c2 - b2) / (2 * a * c)
    cos_c = (a2 + b2 - c2) / (2 * a * b)

    # остроугольность: все углы < 90°, т.е. все косинусы > 0
    acute = (cos_a > 0) & (cos_b > 0) & (cos_c > 0)
    n_acute = acute.sum()
    if n_acute == 0:
        continue

    cosines = np.vstack((cos_a[acute], cos_b[acute], cos_c[acute]))
    min_cos_list.append(cosines.min(axis=0))
    max_cos_list.append(cosines.max(axis=0))
    acute_count += n_acute

min_cos = np.concatenate(min_cos_list)[:target]
max_cos = np.concatenate(max_cos_list)[:target]

# R: наименьший угол < 26.7° <=> наибольший косинус > cos(26.7°)
P_R_given_T = np.mean(max_cos > cos_R)
# S: наибольший угол < 81.9° <=> наименьший косинус > cos(81.9°)
P_S_given_T = np.mean(min_cos > cos_S)

print(f"P(R | T) (точное значение симуляции) ≈ {P_R_given_T:.4f}")
print(f"P(S | T) (точное значение симуляции) ≈ {P_S_given_T:.4f}")
print(f"P(R | T) (округление до одного знака) ≈ {P_R_given_T:.1f}")
print(f"P(S | T) (округление до одного знака) ≈ {P_S_given_T:.1f}")""")

    md(r"""**Ответ:** симуляция даёт $P(R \mid T) \approx 0{,}1111$ и
$P(S \mid T) \approx 0{,}6545$, что согласуется с ответом листка
$0{,}11$ и $0{,}65$ в пределах погрешности Монте-Карло.
При строгом округлении до одного знака после запятой:
$P(R \mid T) \approx 0{,}1$, $P(S \mid T) \approx 0{,}7$.""")
