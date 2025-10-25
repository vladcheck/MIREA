def sieve_of_eratosthenes(n) -> list[int]:
    if n < 2:
        return []
    is_prime: list[bool] = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False

    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False

    return [i for i, prime in enumerate(is_prime) if prime]


def sieve_of_atkin(n: int) -> list[int]:
    """
    Реализация решета Аткина.
    Алгоритм использует квадратичные формы для маркировки потенциальных простых чисел.
    """
    if n < 2:
        return []
    if n == 2:
        return [2]
    if n == 3:
        return [2, 3]

    is_prime: list[bool] = [False] * (n + 1)
    sqrt_n: int = int(n**0.5) + 1

    # Этап 1: Маркировка потенциальных простых чисел
    for x in range(1, sqrt_n):
        x_sq: int = x * x
        for y in range(1, sqrt_n):
            y_sq = y * y
            num = 4 * x_sq + y_sq
            if num <= n and (num % 12 == 1 or num % 12 == 5):
                is_prime[num] = not is_prime[num]

            num: int = 3 * x_sq + y_sq
            if num <= n and num % 12 == 7:
                is_prime[num] = not is_prime[num]

            num = 3 * x_sq - y_sq
            if x > y and num <= n and num % 12 == 11:
                is_prime[num] = not is_prime[num]

    # Этап 2: Вычеркивание квадратов простых чисел
    for i in range(5, sqrt_n):
        if is_prime[i]:
            for j in range(i * i, n + 1, i * i):
                is_prime[j] = False

    # Этап 3: Сбор простых чисел
    primes: list[int] = [2, 3] + [i for i in range(5, n + 1) if is_prime[i]]
    return primes


def optimized_sieve_of_eratosthenes(n) -> list[int]:
    if n < 2:
        return []
    primes: list[int] = [2]
    if n == 2:
        return primes

    limit: int = (n - 1) // 2
    is_prime: list[bool] = [True] * (limit + 1)

    for i in range(1, int(limit**0.5) + 1):
        if is_prime[i]:
            p: int = 2 * i + 1
            # Запоминаем множители, начиная с p^2
            start_index: int = 2 * i * (i + 1)
            for j in range(start_index, limit + 1, p):
                is_prime[j] = False

    # Ищем простые числа
    for i in range(1, limit + 1):
        if is_prime[i]:
            primes.append(2 * i + 1)
    return primes
