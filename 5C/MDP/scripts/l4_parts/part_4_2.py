"""Задача 4.2."""

from shared import md, code


def build():
    md(r"""## 4.2. Рассадка 5 мужчин и 5 женщин в ряд

5 мужчин и 5 женщин случайным образом рассаживаются в ряд на 10 мест.
Найдите вероятности:

- $A$ — любые две женщины не сидят рядом;
- $B$ — все мужчины сидят рядом.
""")
    code(r"""# Аналитический расчёт
from math import factorial
from itertools import permutations

total = factorial(10)

# A: женщины не сидят рядом.
# Сначала расставляем 5 мужчин: 5! способов.
# Получается 6 возможных промежутков (включая концы): _ M _ M _ M _ M _ M _
# Выбираем 5 из 6 промежутков и рассаживаем женщин: C(6,5) * 5!
fav_A = factorial(5) * 6 * factorial(5)
P_A = fav_A / total

# B: все мужчины сидят рядом.
# Блок из 5 мужчин + 5 женщин = 6 объектов; 6! * 5! (мужчины внутри блока)
fav_B = factorial(6) * factorial(5)
P_B = fav_B / total

print(f"Всего расстановок: {total}")
print(f"P(A) = {fav_A}/{total} = {P_A}")
print(f"P(B) = {fav_B}/{total} = {P_B}")
print(f"1/42 = {1/42}")

# Проверка перебором по позициям женщин (C_10^5 равновозможных размещений)
from itertools import combinations

seats_women = list(combinations(range(10), 5))

count_A = sum(
    1 for w in seats_women
    if all(w[i + 1] - w[i] > 1 for i in range(len(w) - 1))
)

count_B = 0
for w in seats_women:
    men = sorted(set(range(10)) - set(w))
    if all(men[i + 1] - men[i] == 1 for i in range(len(men) - 1)):
        count_B += 1

print(f"\nПеребор: благоприятных A = {count_A}, благоприятных B = {count_B}")
print(f"P(A) (перебор) = {count_A}/{len(seats_women)} = {count_A / len(seats_women)}")
print(f"P(B) (перебор) = {count_B}/{len(seats_women)} = {count_B / len(seats_women)}")
""")
    md(r"""**Ответ:**

- $P(A) = \\dfrac{5! \\cdot C_6^5 \\cdot 5!}{10!} = \\dfrac{1}{42} \\approx 0{,}0238095$;
- $P(B) = \\dfrac{6! \\cdot 5!}{10!} = \\dfrac{1}{42} \\approx 0{,}0238095$.

Совпадает с ответом листка: $P(A) = P(B) = 1/42$.
""")
