import numpy as np
import math
from typing import List


def sieve_of_eratosthenes(n: int) -> List[int]:
    """Стандартное решето Эратосфена"""
    if n < 2:
        return []

    sieve: List[bool] = [True] * (n + 1)
    sieve[0] = False
    sieve[1] = False

    for i in range(2, n + 1):
        if sieve[i]:
            j = i * i
            while j <= n:
                sieve[j] = False
                j += i

    primes: list[int] = []
    for k in range(2, n + 1):
        if sieve[k]:
            primes.append(k)
    return primes


def segmented_sieve(n: int) -> List[int]:
    """
    Сегментированное решето - обрабатывает числа блоками
    """
    if n < 2:
        return []

    # Шаг 1: находим все простые до sqrt(n) обычным способом
    limit = int(math.sqrt(n)) + 1
    simple_sieve = np.ones(limit + 1, dtype=bool)
    simple_sieve[0] = simple_sieve[1] = False

    for i in range(2, int(math.sqrt(limit)) + 1):
        if simple_sieve[i]:
            simple_sieve[i * i : limit + 1 : i] = False

    base_primes = np.where(simple_sieve)[0][2:].tolist()  # Исключаем индексы 0 и 1

    # Шаг 2: обрабатываем большие числа сегментами
    segment_size: int = max(limit, 32768)  # 32KB - размер L1 cache
    primes: list[int] = base_primes[:]

    low: int = limit + 1
    while low <= n:
        high: int = min(low + segment_size - 1, n)

        # Создаем небольшой сегмент
        segment = np.ones(high - low + 1, dtype=bool)

        # Отсеиваем кратные базовых простых в этом сегменте
        for prime in base_primes:
            # Находим первое кратное prime в [low, high]
            start = ((low + prime - 1) // prime) * prime
            if start < prime * prime:
                start = prime * prime

            # Отмечаем все кратные в сегменте
            if start <= high:
                segment_start_idx = start - low
                # Используем присваивание срезу для эффективности
                segment[segment_start_idx::prime] = False

        # Собираем простые из сегмента
        segment_primes = np.where(segment)[0] + low
        primes.extend(segment_primes.tolist())

        low += segment_size

    return primes


def hybrid_optimized_sieve(n: int) -> List[int]:
    """
    Гибридный алгоритм: выбирает лучший метод в зависимости от n
    - До 10k: простой Эратосфен
    - >100k: сегментированный Эратосфен
    """
    if n < 10000:
        return sieve_of_eratosthenes(n)
    else:
        return segmented_sieve(n)


def bitarray_sieve(n: int) -> List[int]:
    """
    Решето с битовым массивом
    Использует bytearray вместо list[bool]
    """
    if n < 2:
        return []

    # Храним только нечетные числа (четные - не простые кроме 2)
    size: int = (n - 1) // 2
    sieve = bytearray([1] * size)  # 1 = возможно простое

    def get_bit(num):
        if num == 2:
            return True
        if num < 2 or num % 2 == 0:
            return False
        return sieve[(num - 3) // 2]

    def clear_bit(num):
        if num > 2 and num % 2 == 1:
            sieve[(num - 3) // 2] = 0

    # Отсеиваем
    limit: int = int(math.sqrt(n)) + 1
    for i in range(3, limit, 2):
        if get_bit(i):
            # Отмечаем кратные, начиная с i^2
            for j in range(i * i, n + 1, 2 * i):  # шаг 2*i, т.к. четные пропускаем
                clear_bit(j)

    # Собираем результат
    primes: List[int] = [2]
    for i in range(size):
        if sieve[i]:
            primes.append(2 * i + 3)

    return primes


def atkin_sieve(limit):
    """
    Реализация решета Аткина.
    """
    # Обработка краевых случаев
    if limit < 2:
        return []
    if limit == 2:
        return [2]
    if limit == 3:
        return [2, 3]

    is_prime = np.zeros(limit + 1, dtype=bool)

    # x и y используются как переменные для перебора квадратичных форм.
    # Ограничение на x и y определяется приблизительно как sqrt(limit),
    # чтобы значения квадратичных форм не превышали limit.
    x = 1
    while x * x <= limit:
        y = 1
        while y * y <= limit:
            n = 4 * x * x + y * y
            # Форма 4*x^2 + y^2.
            # Если n <= limit и остаток от деления на 12 равен 1 или 5,
            # то n "кандидат в простые". Переключаем его статус.
            if n <= limit and (n % 12 == 1 or n % 12 == 5):
                is_prime[n] = np.logical_not(is_prime[n])

            n = 3 * x * x + y * y
            # Форма 3*x^2 + y^2.
            # Если n <= limit и остаток от деления на 12 равен 7,
            # то n "кандидат в простые". Переключаем его статус.
            if n <= limit and n % 12 == 7:
                is_prime[n] = np.logical_not(is_prime[n])

            n = 3 * x * x - y * y
            # Форма 3*x^2 - y^2.
            # Если n <= limit, x > y и остаток от деления на 12 равен 11,
            # то n "кандидат в простые". Переключаем его статус.
            if x > y and n <= limit and n % 12 == 11:
                is_prime[n] = np.logical_not(is_prime[n])

            y += 1
        x += 1

    # После обработки квадратичных форм, квадраты простых чисел (и их кратные)
    # могут быть помечены как "не простые". Их нужно исключить.
    # Проходим по квадратам чисел i от 5 до sqrt(limit).
    i = 5
    while i * i <= limit:
        if is_prime[i]:
            # Если i помечено как потенциально простое,
            # исключаем квадрат i (i*i) и все его кратные (i*i+i*i, ...).
            is_prime[i * i :: i * i] = False
        i += 1

    # Собираем финальный список простых чисел.
    primes: List[int] = [2, 3] if limit >= 3 else [2] if limit >= 2 else []

    # Проходим по массиву, начиная с 5, и добавляем числа, помеченные как простые.
    # Используем np.where для эффективного поиска индексов True
    primes_from_array = np.where(is_prime)[0]
    # Фильтруем 0 и 1, если они есть, и объединяем
    filtered_primes = primes_from_array[primes_from_array >= 5]
    primes.extend(filtered_primes.tolist())

    return primes
