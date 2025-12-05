from io import TextIOWrapper
from typing import Any
from encoding_table import encoding_table
import algs
import convert
import getters

STANDART: dict[str, int] = {"k": 50, "m": 101}

if __name__ == "__main__":
    f: TextIOWrapper[Any] = open("output.txt", "w", encoding="utf8")
    print("=== RSA ШИФРОВАНИЕ И РАСШИФРОВЫВАНИЕ ===\n")

    # Таблица декодирования
    decoding_table: dict[str, str] = {v: k for k, v in encoding_table.items()}

    # 1. Генерация простых чисел по алгоритму решета Эратосфена
    print("1. ГЕНЕРАЦИЯ ПРОСТЫХ ЧИСЕЛ (алгоритм решета Эратосфена)")
    print("Если хотите, чтобы параметр имел стандартное значение, введите -1")
    k = int(input("Введите параметр k: "))
    if k == -1:
        k: int = STANDART["k"]
    m = int(input("Введите параметр m (подходят нечётные > 3): "))
    if m == -1:
        m = STANDART["m"]

    p, q = algs.find_two_primes(k, m)
    print(f"Параметры генерации: k={k}, m={m}")
    print(f"p = {p}")
    print(f"q = {q}")

    # 2. Вычисление N и φ(N)
    N: int = getters.get_N(p, q)  # Возьмем его за максимальный размер блока
    phi_N: int = getters.get_phi_N(p, q)
    print(f"N = p * q = {N}")
    print(f"φ(N) = (p-1)*(q-1) = {phi_N}")

    # 3. Выбор открытой экспоненты e
    e = 5
    while algs.gcd(e, phi_N) != 1:
        e += 2

    print(f"e = {e} (взаимно простое с φ(N))")

    # 4. Вычисление секретной экспоненты d
    d: int | None = algs.mod_inverse(e, phi_N)
    if d == None:
        raise ValueError("Обратного элемента не существует")

    print(f"d = e^(-1) mod φ(N) = {d}")

    print(f"\nОТКРЫТЫЙ КЛЮЧ: (N={N}, e={e})")
    print(f"ЗАКРЫТЫЙ КЛЮЧ: (N={N}, d={d})")

    # 5. Подготовка текста для шифрования
    plaintext: str = open("input.txt", "r", encoding="utf8").read().upper()

    numeric_text: str = convert.text_to_numbers(
        plaintext, encoding_table
    )  # Преобразование текста в числа
    blocks: list[int] = algs.split_into_blocks(numeric_text, N)  # Разбиение на блоки

    f.write(f"Числовое представление: {numeric_text}\n")
    f.write(f"Блоки для шифрования: {blocks}\n")

    # 6. Шифрование
    f.write("\n3. ШИФРОВАНИЕ\n")
    encrypted_blocks: list[int] = []
    for block in blocks:
        encrypted_block: int = algs.rsa_encrypt_block(block, e, N)
        encrypted_blocks.append(encrypted_block)
        f.write(f"Блок {block} -> {encrypted_block}\n")

    f.write(f"Зашифрованное сообщение: {''.join(map(str, encrypted_blocks))}\n")

    # 7. Расшифровывание
    f.write("\n4. РАСШИФРОВЫВАНИЕ\n")
    decrypted_blocks: list[int] = []
    for encrypted_block in encrypted_blocks:
        decrypted_block: int = algs.rsa_decrypt_block(encrypted_block, d, N)
        decrypted_blocks.append(decrypted_block)
        f.write(f"Блок {encrypted_block} -> {decrypted_block}\n")

    decrypted_numeric: str = convert.blocks_to_number(
        decrypted_blocks
    )  # Восстановление числовой строки
    decrypted_text: str = convert.number_to_text(
        decrypted_numeric, decoding_table
    )  # Преобразование чисел обратно в текст

    f.write(f"Расшифрованное числовое представление: {decrypted_numeric}\n")
    f.write(f"Расшифрованный текст: '{decrypted_text}'\n")
    print("Вывод сохранен в input.txt")

    # Проверка
    print(
        f"\nПРОВЕРКА: Исходный текст совпадает с расшифрованным? {plaintext == decrypted_text}"
    )
    f.close()
