"""Задача 4.14."""

from shared import md, code


def build():
    md(r"""## 4.14. Две корзины со случайным числом белых шаров

Две корзины: в первой 6 шаров, число белых $\sim \mathrm{Bin}(3, 0{,}8)$;
во второй 11 шаров, число белых $\sim \mathrm{Bin}(4, 0{,}7)$.
Все шары перекладывают в третью корзину.

1) Найти $P(A)$ — вероятность того, что случайный шар из третьей корзины белый.
2) Найти $P(H \mid A)$ — вероятность того, что он первоначально был в первой корзине.""")

    code(r"""import math

# Параметры корзин
N1, n1, p1 = 6, 3, 0.8   # первая: 6 шаров, белых ~ Bin(3, 0.8)
N2, n2, p2 = 11, 4, 0.7  # вторая: 11 шаров, белых ~ Bin(4, 0.7)
N = N1 + N2


def binom_pmf(k, n, p):
    return math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))


# Формула полной вероятности по распределениям числа белых шаров:
# P(A) = sum_{k1,k2} P(K1=k1) P(K2=k2) * (k1+k2) / N
# P(H∩A) = sum_{k1,k2} P(K1=k1) P(K2=k2) * k1 / N
PA = 0.0
PHA = 0.0
for k1 in range(n1 + 1):
    for k2 in range(n2 + 1):
        prob = binom_pmf(k1, n1, p1) * binom_pmf(k2, n2, p2)
        PA += prob * (k1 + k2) / N
        PHA += prob * k1 / N

PH_given_A = PHA / PA  # формула Байеса

print(f"P(A)      = {PA:.4f}")
print(f"P(H | A)  = {PH_given_A:.4f}")

# Упрощённая проверка: среднее число белых
mean_white_1 = n1 * p1
mean_white_2 = n2 * p2
PA_check = (mean_white_1 + mean_white_2) / N
PH_given_A_check = mean_white_1 / (mean_white_1 + mean_white_2)
print(f"\nПроверка: P(A) = {PA_check:.4f}, P(H|A) = {PH_given_A_check:.4f}")""")

    md(r"""**Ответ:** $P(A) = \dfrac{3 \cdot 0{,}8 + 4 \cdot 0{,}7}{17} = \dfrac{5{,}2}{17} \approx 0{,}3059$; по формуле Байеса $P(H \mid A) = \dfrac{3 \cdot 0{,}8}{3 \cdot 0{,}8 + 4 \cdot 0{,}7} = \dfrac{2{,}4}{5{,}2} = \dfrac{6}{13} \approx 0{,}4615$, что совпадает с ответом листка.""")
