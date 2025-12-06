import random
import math

"""
ЗАДАНИЕ 2: ОПЕРАЦИИ С БОЛЬШИМИ ПРОСТЫМИ ЧИСЛАМИ
Сгенерировать два больших простых числа.
Выполнить с числами операции сложения, вычитания, умножения, деления,
вычисления остатка от деления одного числа на другое,
возведения одного из чисел в степень n по модулю m.
"""

def miller_rabin_test(n: int, k: int = 10) -> bool:
    """Проверяет число на простоту с помощью теста Миллера-Рабина"""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Представляем n-1 как 2^r * d
    n_minus_1 = n - 1
    r = 0
    d = n_minus_1
    while d % 2 == 0:
        r += 1
        d //= 2

    # k раундов теста
    for _ in range(k):
        # Генерируем случайное a в диапазоне [2, n-2]
        a = random.randrange(2, n - 1)
        
        # x = a^d mod n
        x = pow(a, d, n)
        
        if x == 1 or x == n_minus_1:
            continue
            
        continue_outer = False
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n_minus_1:
                continue_outer = True
                break
                
        if not continue_outer:
            return False
            
    return True


def generate_prime(bits: int) -> tuple[int, int]:
    """Генерирует простое число заданной битовой длины"""
    attempts = 0
    while True:
        attempts += 1
        # Генерируем случайное число длиной bits битов
        num = random.getrandbits(bits)
        # Убедимся, что число имеет точную битовую длину
        num |= (1 << (bits - 1)) | 1  # Устанавливаем старший и младший биты в 1
        
        # Проверяем на простоту
        if miller_rabin_test(num, 10):
            return num, attempts


def gcd(a: int, b: int) -> int:
    """Вычисляет НОД (наибольший общий делитель) двух чисел"""
    while b != 0:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """Вычисляет НОК (наименьшее общее кратное) двух чисел"""
    return abs(a * b) // gcd(a, b)


def main():
    print("=" * 70)
    print("ЗАДАНИЕ 2: ОПЕРАЦИИ С БОЛЬШИМИ ПРОСТЫМИ ЧИСЛАМИ")
    print("=" * 70)

    # Шаг 1: Генерируем два больших простых числа
    print("\n1. Генерация двух больших простых чисел:")

    bits = 32  # Битовая длина чисел
    print(f"   Битовая длина: {bits} бит\n")

    print("   Генерация первого простого числа... ", end="", flush=True)
    p, attempts1 = generate_prime(bits)
    print(f"Готово! (попыток: {attempts1})")

    print("   Генерация второго простого числа... ", end="", flush=True)
    q, attempts2 = generate_prime(bits)
    print(f"Готово! (попыток: {attempts2})")

    print("\n   Первое простое число:")
    print(f"   p = {p}")
    print(f"   Битовая длина p: {p.bit_length()} бит")
    print(f"   Количество цифр в p: {len(str(p))} цифр")

    print("\n   Второе простое число:")
    print(f"   q = {q}")
    print(f"   Битовая длина q: {q.bit_length()} бит")
    print(f"   Количество цифр в q: {len(str(q))} цифр")

    # Проверка простоты
    print("\n2. Проверка простоты:")
    print(f"   p простое: {miller_rabin_test(p, 10)}")
    print(f"   q простое: {miller_rabin_test(q, 10)}")

    # Шаг 2: Арифметические операции
    print("\n3. АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ:")

    # Сложение
    print("\n   а) Сложение:")
    result_add = p + q
    print(f"      p + q = {result_add}")
    print(f"      Количество цифр: {len(str(result_add))}")

    # Вычитание
    print("\n   б) Вычитание:")
    result_sub = abs(p - q)
    print(f"      |p - q| = {result_sub}")
    print(f"      p > q: {p > q}")

    # Умножение
    print("\n   в) Умножение:")
    result_mul = p * q
    print(f"      p * q = {result_mul}")
    print(f"      Количество цифр в произведении: {len(str(result_mul))}")
    print(f"      Битовая длина: {result_mul.bit_length()} бит")

    # Деление
    dividend, divisor = (p, q) if p > q else (q, p)

    print("\n   г) Деление (целочисленное):")
    result_div = dividend // divisor
    dividend_str = str(dividend)[:20] + "..." if len(str(dividend)) > 20 else str(dividend)
    divisor_str = str(divisor)[:20] + "..." if len(str(divisor)) > 20 else str(divisor)
    print(f"      {dividend_str} // {divisor_str} = {result_div}")

    # Остаток от деления
    print("\n   д) Остаток от деления:")
    result_mod = dividend % divisor
    print(f"      {dividend_str} % {divisor_str} = {result_mod}")

    # Проверка деления
    print("\n      Проверка деления:")
    check = divisor * result_div + result_mod
    check_str = str(check)[:20] + "..." if len(str(check)) > 20 else str(check)
    print(f"      divisor * quotient + remainder = {check_str}")
    print(f"      Равно dividend: {check == dividend}")

    # Возведение в степень по модулю
    print("\n   е) Возведение в степень по модулю:")

    # Пример 1: малая степень
    print("\n      Пример 1:")
    n1 = 17
    m1 = q
    result_pow1 = pow(p, n1, m1)
    print(f"      p^{n1} mod q = {result_pow1}")
    p_str = str(p)[:30] + "..." if len(str(p)) > 30 else str(p)
    q_str = str(m1)[:30] + "..." if len(str(m1)) > 30 else str(m1)
    print(f"      где p = {p_str}")
    print(f"          q = {q_str}")

    # Пример 2: большая степень
    print("\n      Пример 2 (большая степень):")
    n2 = 1000
    m2 = result_mul
    result_pow2 = pow(p, n2, m2)
    result_pow2_str = str(result_pow2)[:30] + "..." if len(str(result_pow2)) > 30 else str(result_pow2)
    print(f"      p^{n2} mod (p*q) = {result_pow2_str}")

    # Пример 3: возведение q в степень по модулю p
    print("\n      Пример 3:")
    n3 = 65537
    result_pow3 = pow(q, n3, p)
    print(f"      q^{n3} mod p = {result_pow3}")

    # Дополнительная информация
    print("\n4. Дополнительная информация:")
    gcd_result = gcd(p, q)
    lcm_result = lcm(p, q)
    print(f"   НОД(p, q) = {gcd_result}")
    lcm_str = str(lcm_result)[:50] + "..." if len(str(lcm_result)) > 50 else str(lcm_result)
    print(f"   НОК(p, q) = {lcm_str}")
    print("   (Для простых чисел НОД всегда равен 1)")

    # Дополнительные операции
    print("\n5. Дополнительные операции:")

    # Квадрат числа
    p_squared = p * p
    p_squared_str = str(p_squared)[:50] + "..." if len(str(p_squared)) > 50 else str(p_squared)
    print(f"   p² = {p_squared_str}")
    print(f"   Битовая длина p²: {p_squared.bit_length()} бит")

    # Модульное вычитание
    mod_sub = (p - q) % 1000000
    print(f"   (p - q) mod 1000000 = {mod_sub}")

    # Сравнение
    print("\n6. Сравнение чисел:")
    if p > q:
        print("   p > q")
    elif p < q:
        print("   p < q")
    else:
        print("   p = q")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()