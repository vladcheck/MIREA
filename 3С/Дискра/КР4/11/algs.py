def gcd(a: int, b: int) -> int:
    """Вычисление наибольшего общего делителя a и b"""
    t: int = b
    while t != 0:
        a, t = t, a % t
    return a


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Расширенный алгоритм Евклида"""
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    x: int = y1 - (b // a) * x1  # Коэффициент Безу
    y: int = x1  # Коэффициент Безу
    return gcd_val, x, y


def mod_inverse(a: int, m: int) -> int | None:
    """
    Нахождение обратного элемента по модулю
    """
    gcd_val, x, _ = extended_gcd(a, m)
    if gcd_val != 1:
        return None
    return (x % m + m) % m


def modular_exponentiation(a: int, k: int, m: int) -> int:
    """
    Алгоритм возведения в степень по модулю
    - Вход: a, k, m - ненулевые числа, a - целое число
    - Выход: a^k mod m
    """
    # Инициализация
    K: int = k
    B = 1
    A: int = a

    while True:
        # Вычисление следующего бита
        q: int = K // 2
        r: int = K - 2 * q
        K = q

        if r != 0:
            # Умножить и взять остаток по модулю m
            B: int = (A * B) % m

        if K == 0:
            return B % m

        # Возвести в квадрат и взять остаток по модулю m
        A = (A * A) % m


def odd_segmented_sieve(k: int, m: int) -> list[int]:
    """
    Генерация простых чисел по алгоритму сегментированного решета Эратосфена для нечетных чисел
    - Вход: k, m - целые числа, m - нечетное ≥ 3
    - Выход: Простые числа в отрезке [m, m + 2k - 2]
    """
    # Шаг 1: Инициализация
    n: int = m + 2 * k - 2
    A: list[int] = [1] * (k + 1)  # Индексация с 1 до k
    d = 3

    primes: list[int] = []

    # Шаг 2: Основной цикл
    while True:
        if d > n // d:  # d^2 > n
            break

        # Шаг 3: Вычисление j
        r: int = m % d
        j = 1

        if r > 0 and r % 2 == 1:
            j: int = j + (d - r) // 2

        if m <= d:
            j = j + d

        # Шаг 4: Вычеркивание составных чисел
        i: int = j
        while i <= k:
            if i >= 1:
                A[i] = 0
            i += d

        # Шаг 5: Изменение d
        if d % 6 == 1:
            d: int = d + 4
        else:
            d = d + 2

    for i in range(k, 0, -1):
        if A[i] == 1:
            prime: int = m + 2 * i - 2
            if prime <= n:  # Проверка границ
                primes.append(prime)

    return sorted(primes)


def find_two_primes(k: int, m: int) -> tuple[int, int]:
    """
    Нахождение двух различных простых чисел с помощью решета Эратосфена
    """
    primes: list[int] = odd_segmented_sieve(k, m)

    if len(primes) < 2:
        # Если не нашли достаточно простых чисел, увеличиваем диапазон
        return find_two_primes(k * 2, m)

    # Возвращаем два наибольших найденных простых числа
    return primes[-2], primes[-1]


def rsa_encrypt_block(block: int, e: int, N: int) -> int:
    """Шифрование одного блока RSA"""
    return modular_exponentiation(block, e, N)


def rsa_decrypt_block(block: int, d: int, N: int) -> int:
    """Расшифрование одного блока RSA"""
    return modular_exponentiation(block, d, N)


def split_into_blocks(number_str, max_block_value) -> list[int]:
    """Разбиение числовой строки на блоки"""
    blocks: list[int] = []
    current_block: str = ""

    for digit in number_str:
        test_block: str = current_block + digit
        if int(test_block) < max_block_value:
            current_block = test_block
        else:
            if current_block:
                blocks.append(int(current_block))
            current_block = digit

    if current_block:
        blocks.append(int(current_block))

    return blocks
