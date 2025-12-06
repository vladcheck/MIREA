from typing import List, Tuple, Dict, Any

# --- КОНФИГУРАЦИЯ ---

STANDART: dict[str, int] = {"k": 50, "m": 101}

# Таблица кодирования (только то, что гарантированно не содержит '0', чтобы не ломать int conversion)
encoding_table: Dict[str, str] = {
    "А": "45",
    "Б": "11",
    "В": "12",
    "Г": "13",
    "Д": "14",
    "Е": "15",
    "Ё": "93",
    "Ж": "16",
    "З": "17",
    "И": "18",
    "Й": "19",
    "К": "21",
    "Л": "22",
    "М": "23",
    "Н": "24",
    "О": "25",
    "П": "26",
    "Р": "27",
    "С": "28",
    "Т": "29",
    "У": "31",
    "Ф": "32",
    "Х": "33",
    "Ц": "34",
    "Ч": "35",
    "Ш": "36",
    "Щ": "37",
    "Ъ": "38",
    "Ы": "39",
    "Ь": "41",
    "Э": "42",
    "Ю": "43",
    "Я": "44",
    " ": "99",
}

# Создаем обратную таблицу для декодирования
decoding_table: Dict[str, str] = {v: k for k, v in encoding_table.items()}


# --- МАТЕМАТИЧЕСКИЕ АЛГОРИТМЫ (ALGS) ---


def gcd(a: int, b: int) -> int:
    """Вычисление НОД"""
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида: return (g, x, y) такие, что ax + by = g"""
    if a == 0:
        return b, 0, 1
    d, x1, y1 = extended_gcd(b % a, a)
    x: int = y1 - (b // a) * x1
    y: int = x1
    return d, x, y


def mod_inverse(a: int, m: int) -> int | None:
    """Нахождение обратного элемента: (a * x) % m == 1"""
    d, x, y = extended_gcd(a, m)
    if d != 1:
        return None  # Обратного элемента не существует
    return (x % m + m) % m


def modular_exponentiation(base: int, exp: int, mod: int) -> int:
    """Быстрое возведение в степень по модулю: (base^exp) % mod"""
    res = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            res: int = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res


def odd_segmented_sieve(k: int, m: int) -> List[int]:
    """Генерация простых чисел (сегментированное решето)"""
    n = m + 2 * k - 2
    # Используем простую реализацию решета для надежности в рамках задачи
    # (Для больших чисел нужен тест Миллера-Рабина, но здесь хватит и этого)
    limit: int = n
    sieve: List[bool] = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False

    primes: List[int] = [x for x in range(m, n + 1) if sieve[x]]
    return sorted(primes)


def find_two_primes(k: int, m: int) -> Tuple[int, int]:
    """Поиск двух последних простых чисел в диапазоне"""
    # Если m четное, делаем нечетным
    if m % 2 == 0:
        m += 1

    primes: List[int] = odd_segmented_sieve(k, m)

    # Если мало простых чисел, расширяем диапазон
    if len(primes) < 2:
        return find_two_primes(k * 2, m)

    return primes[-2], primes[-1]


# --- РАБОТА С БЛОКАМИ И ТЕКСТОМ (CONVERT/ALGS) ---


def split_into_blocks(number_str: str, N: int) -> List[int]:
    """
    Разбивает строку цифр на числа (блоки), каждое из которых < N.
    Важно: Этот метод полагается на то, что в number_str нет ведущих нулей,
    которые могут исчезнуть при конвертации в int.
    В текущей таблице кодировки (11-99) нулей нет.
    """
    blocks: List[int] = []
    current_block: str = ""

    for digit in number_str:
        test_block = current_block + digit
        # Проверяем, помещается ли новый кусок в N
        if int(test_block) < N:
            current_block = test_block
        else:
            # Если не помещается, сохраняем предыдущий кусок
            if current_block:
                blocks.append(int(current_block))
            current_block = digit

    if current_block:
        blocks.append(int(current_block))

    return blocks


def text_to_numbers(text: str, enc_table: Dict[str, str]) -> str:
    """
    Переводит текст в строку цифр.
    Игнорирует символы, которых нет в таблице!
    """
    result: List[str] = []
    for char in text:
        if char in enc_table:
            result.append(enc_table[char])
        elif char == "Ё":  # Обработка Ё как Е
            result.append(enc_table["Е"])
        else:
            # Пропускаем символы, которых нет в таблице (знаки препинания)
            # Чтобы не ломать программу
            pass
    return "".join(result)


def number_to_text(number_str: str, dec_table: Dict[str, str]) -> str:
    """Восстанавливает текст из строки цифр."""
    result: List[str] = []
    i = 0
    length: int = len(number_str)

    while i < length:
        # Пытаемся взять 2 цифры (так как у нас все коды двузначные)
        if i + 2 <= length:
            code: str = number_str[i : i + 2]
            if code in dec_table:
                result.append(dec_table[code])
                i += 2
                continue

        # Если вдруг что-то пошло не так (например, осталась 1 цифра), пропускаем
        i += 1

    return "".join(result)


def main() -> None:
    # Создаем dummy input.txt для примера, если его нет
    try:
        with open("input.txt", "r", encoding="utf8") as f:
            pass
    except FileNotFoundError:
        with open("input.txt", "w", encoding="utf8") as f:
            f.write(
                "Николай Евграфович Алмазов едва дождался, пока жена отворила ему двери..."
            )
            f.write("\n")

    with open("output.txt", "w", encoding="utf8") as f:
        print("=== RSA ШИФРОВАНИЕ И РАСШИФРОВЫВАНИЕ ===\n")

        print("1. ГЕНЕРАЦИЯ ПРОСТЫХ ЧИСЕЛ")
        # Упрощенный ввод для теста
        try:
            k_in = int(input(f"Введите k (по умолчанию {STANDART['k']}): ") or -1)
        except ValueError:
            k_in = -1
        k: int = STANDART["k"] if k_in == -1 else k_in

        try:
            m_in = int(input(f"Введите m (по умолчанию {STANDART['m']}): ") or -1)
        except ValueError:
            m_in = -1
        m: int = STANDART["m"] if m_in == -1 else m_in

        p, q = find_two_primes(k, m)
        print(f"p = {p}, q = {q}")

        # 2. Ключи
        N: int = p * q
        phi_N: int = (p - 1) * (q - 1)

        # Проверка безопасности N
        # N должно быть больше любого одиночного кода (99), иначе блокирование не сработает
        if N < 100:
            print("ОШИБКА: Слишком маленькие простые числа! N должно быть > 99.")
            return

        print(f"N = {N}")
        print(f"φ(N) = {phi_N}")

        e = 5
        while gcd(e, phi_N) != 1:
            e += 2

        d: int | None = mod_inverse(e, phi_N)
        if d is None:
            print("Ошибка генерации приватного ключа.")
            return

        print(f"\nОткрытый ключ (e, N): ({e}, {N})\n")
        print(f"\nЗакрытый ключ (d, N): ({d}, {N})\n")

        # 3. Подготовка текста
        raw_text: str = open("./input.txt", "r", encoding="utf8").read().upper()

        # ВАЖНО: Фильтрация текста, чтобы не упасть на запятых
        numeric_text: str = text_to_numbers(raw_text, encoding_table)

        if not numeric_text:
            print("Ошибка: В тексте нет доступных для кодирования символов.")
            return

        blocks: List[int] = split_into_blocks(numeric_text, N)

        f.write(f"\nИсходный текст (сырой): {raw_text[:1000]}...\n")
        f.write(f"\nЧисловое представление: {numeric_text[:1000]}...\n")
        f.write(f"\nБлоки ({len(blocks)} шт): {blocks[:100]}...\n")

        # 4. Шифрование
        print("Шифрование...")
        encrypted_blocks: List[int] = [modular_exponentiation(b, e, N) for b in blocks]
        f.write(f"\nЗашифрованные блоки: {encrypted_blocks}\n")

        # 5. Дешифрование
        print("Дешифрование...")
        decrypted_blocks: List[int] = [
            modular_exponentiation(c, d, N) for c in encrypted_blocks
        ]

        # Склеиваем обратно
        decrypted_numeric: str = "".join(map(str, decrypted_blocks))
        decrypted_text: str = number_to_text(decrypted_numeric, decoding_table)

        f.write(
            f"\nРасшифрованное числовое представление: {decrypted_numeric[:100]}...\n"
        )
        f.write(f"\nРасшифрованный текст: {decrypted_text[:1000]}...\n")

        # Проверка
        # Сравниваем не с raw_text, а с очищенной версией того, что мы закодировали
        original_clean: str = number_to_text(numeric_text, decoding_table)
        is_correct: bool = original_clean == decrypted_text

        print(f"\nУспех: {is_correct}")
        f.write(f"\nРЕЗУЛЬТАТ: {'СОВПАДАЕТ' if is_correct else 'ОШИБКА'}")

        print("Результаты сохранены в output.txt")


if __name__ == "__main__":
    main()
