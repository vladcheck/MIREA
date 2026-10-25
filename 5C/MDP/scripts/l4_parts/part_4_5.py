"""Задача 4.5."""

from shared import md, code


def build():
    md(r"""## 4.5. Остановка при двух одинаковых подряд (несимметричная монета)

То же, что 4.4, но монета несимметричная: $P(\text{герба}) = p = 0{,}7$. Найти
вероятность того, что потребуется: а) чётное число бросков; б) число бросков
кратно 4.""")

    code(r"""p = 0.7
q = 1 - p
pq = p * q
p2_q2 = p**2 + q**2

# Замкнутые формулы
P_even_closed = p2_q2 / (1 - pq)
P_div4_closed = pq * p2_q2 / (1 - pq**2)

print(f"p = {p}, q = {q}, pq = {pq}")
print(f"p² + q² = {p2_q2}")
print(f"а) P(чётное) замкнуто = {P_even_closed:.10f}")
print(f"б) P(кратно 4) замкнуто = {P_div4_closed:.10f}")


def prob_stop(k, p, q):
    'P(опыт заканчивается ровно на k-м броске).'
    if k % 2 == 0:
        m = k // 2
        return (p * q) ** (m - 1) * (p**2 + q**2)
    else:
        m = (k - 1) // 2
        return p**m * q ** (m + 1) + q**m * p ** (m + 1)


# Численное суммирование до сходимости
tol = 1e-12
P_even_sum = 0.0
P_div4_sum = 0.0
k = 2
while True:
    term = prob_stop(k, p, q)
    if k % 2 == 0:
        P_even_sum += term
        if k % 4 == 0:
            P_div4_sum += term
    if term < tol:
        break
    k += 1

print(f"а) P(чётное) суммой  = {P_even_sum:.10f}")
print(f"б) P(кратно 4) суммой = {P_div4_sum:.10f}")
print(f"Число учтённых членов ряда: k = 2..{k}")
print(f"Разница а): {abs(P_even_closed - P_even_sum):.2e}")
print(f"Разница б): {abs(P_div4_closed - P_div4_sum):.2e}")""")

    md(r"""**Ответ:**

а) $P(\text{чётное}) = \dfrac{p^2 + q^2}{1 - pq} = \dfrac{0{,}58}{0{,}79} \approx 0{,}7341772$.

б) $P(\text{кратно 4}) = \dfrac{pq\,(p^2 + q^2)}{1 - (pq)^2} \approx 0{,}1274192$.

Численное суммирование членов $P_k$ до достижения $10^{-12}$ совпадает с
замкнутыми формулами в пределах машинной точности.""")
