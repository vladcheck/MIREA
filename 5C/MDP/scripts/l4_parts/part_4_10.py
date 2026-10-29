"""Задача 4.10."""

from shared import md, code


def build():
    md(r"""## 4.10. Случайный отрезок в круге

В круге радиуса 1 наудачу выбирается отрезок (хорда). Найти вероятность того,
что его длина меньше радиуса.""")
    code(r"""
import math

# Аналитическое значение: вероятность того, что расстояние между двумя
# независимыми равномерными точками в единичном круге меньше 1,
# равна 1 - 3*sqrt(3)/(4*pi).
p_exact = 1 - 3 * math.sqrt(3) / (4 * math.pi)
p_exact
""")
    code(r"""
import math
import random


def simulate_one():
    '''Одна реализация: две равномерные точки в единичном круге.'''
    r1 = math.sqrt(random.random())
    phi1 = random.random() * 2 * math.pi
    r2 = math.sqrt(random.random())
    phi2 = random.random() * 2 * math.pi
    x1, y1 = r1 * math.cos(phi1), r1 * math.sin(phi1)
    x2, y2 = r2 * math.cos(phi2), r2 * math.sin(phi2)
    return int(math.hypot(x1 - x2, y1 - y2) < 1)


p_est = plot_convergence(simulate_one, r'$P(\text{длина отрезка} < 1)$')
p_est
""")
    md(r"""**Ответ:** $\displaystyle P = 1 - \frac{3\sqrt{3}}{4\pi} \approx 0{,}5865033284336559$ — совпадает с ответом листка.""")
