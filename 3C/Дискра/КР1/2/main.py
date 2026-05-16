from math import log2, ceil
from typing import List, Tuple
import random
import os


def create_output_folder() -> str:
    """
    Создает папку 'out' в текущей директории и возвращает её абсолютный путь.
    """
    folder_name = "out"
    dist_path: str = os.path.abspath(folder_name)

    if not os.path.exists(dist_path):
        os.makedirs(dist_path, exist_ok=True)
        print(f"Папка {dist_path} создана.")
    else:
        print(f"Папка {dist_path} уже существует.")

    return dist_path


DIST_PATH: str = create_output_folder()


def print_and_write(text: str, file_handle, prepend: bool = True) -> None:
    """
    Печатает текст в консоль и записывает его в файл.
    """
    res = f"\n{text}\n" if prepend else f"{text}\n"
    print(res)
    file_handle.write(res)


def print_and_write_table(table: List[List[int]], file_handle) -> None:
    """
    Печатает таблицу Хемминга в нужном формате и записывает её в файл.
    """
    m = len(table)  # Количество проверочных битов
    n = len(table[0]) if table else 0  # Общее количество битов (длина кодового слова)
    table_header = f"Таблица Хемминга ({m}x{n}):"
    print(table_header)
    file_handle.write(table_header + "\n")

    for i, row in enumerate(table):
        row_str = f"P{i+1}: {row}"
        print(row_str)
        file_handle.write(row_str + "\n")


def generate_random_combination(size: int) -> str:
    """
    Генерирует случайную бинарную комбинацию заданного размера.
    """
    return "".join(random.choice("01") for _ in range(size))


def generate_hamming_table_for_encoding(k: int, r: int) -> List[List[int]]:
    """
    Генерирует таблицу Хемминга для вычисления синдрома/проверочных битов.
    Каждая строка соответствует одному проверочному биту P_i.
    Каждый столбец соответствует позиции в кодовом слове (1-индексированной).
    Значение 1 означает, что проверочный бит P_i влияет на бит в этой позиции.
    """
    n = k + r
    actual_m = (n - 1).bit_length()
    if actual_m > r:
        actual_m = r

    table = []
    for i in range(actual_m):
        row = []
        for j in range(1, n + 1):
            if j & (1 << i):
                row.append(1)
            else:
                row.append(0)
        table.append(row)

    return table


def calculate_parity_bits(data: str, r: int) -> List[int]:
    """
    Рассчитывает проверочные биты для кода Хемминга.
    r - количество *всех возможных* проверочных битов, заданное пользователем.
    На практике будут использованы только log2(k+r) битов, но r должно быть >= log2(k+r).
    """
    k: int = len(data)
    n: int = k + r

    max_k_for_r = (2**r) - r - 1
    if k > max_k_for_r:
        raise ValueError(
            f"Размер информационного слова k={k} слишком велик для r={r} проверочных битов. Максимальное допустимое k: {max_k_for_r}."
        )

    hamming_code: List[int] = [0] * n

    data_index = 0
    for i in range(1, n + 1):
        pos_0_indexed = i - 1
        if (i & (i - 1)) == 0:
            continue
        else:
            if data_index < k:
                hamming_code[pos_0_indexed] = int(data[data_index])
                data_index += 1
            else:
                break

    j = 0
    while (2**j) <= n:
        parity_pos_1_indexed = 2**j
        parity_pos_0_indexed = parity_pos_1_indexed - 1

        if parity_pos_0_indexed >= n:
            break

        parity = 0
        for l in range(1, n + 1):
            if l & parity_pos_1_indexed:
                if l != parity_pos_1_indexed:  # Исключаем сам проверочный бит из суммы
                    hamming_code_bit = hamming_code[l - 1]
                    parity ^= hamming_code_bit
        hamming_code[parity_pos_0_indexed] = parity
        j += 1

    return hamming_code


def encode_hamming(data: str, r: int) -> str:
    """
    Кодирует информационную комбинацию методом Хемминга.
    """
    encoded_list: List[int] = calculate_parity_bits(data, r)
    return "".join(map(str, encoded_list))


def introduce_error(code: str) -> Tuple[str, int]:
    """
    Вносит ошибку в один случайный разряд кодового вектора.
    Возвращает измененный код и индекс ошибки (0-индексированный).
    """
    code_list = list(code)
    error_pos = random.randint(0, len(code) - 1)
    # Инвертируем бит
    code_list[error_pos] = "0" if code_list[error_pos] == "1" else "1"
    return "".join(code_list), error_pos


def calculate_syndrome(received_code: str, r: int) -> int:
    """
    Рассчитывает синдром для полученного кодового слова.
    Возвращает номер позиции ошибки (1-индексированный) или 0, если ошибки нет.
    """
    n = len(received_code)
    syndrome = 0
    for i in range(r):
        parity_check = 0
        for j in range(1, n + 1):
            if j & (2**i):  # Если j-ая позиция проверяется i-ым битом
                if received_code[j - 1] == "1":
                    parity_check ^= 1
        # Бит синдрома
        syndrome |= parity_check << i
    return syndrome


def correct_error(received_code: str, syndrome: int) -> str:
    """
    Исправляет ошибку в кодовом слове по синдрому.
    Синдром - это 1-индексированная позиция ошибки.
    """
    if syndrome == 0:
        return received_code  # Нет ошибки

    code_list = list(received_code)
    error_pos_0_indexed = syndrome - 1  # Преобразуем в 0-индексированную позицию

    if 0 <= error_pos_0_indexed < len(code_list):
        # Инвертируем бит
        code_list[error_pos_0_indexed] = (
            "0" if code_list[error_pos_0_indexed] == "1" else "1"
        )
    else:
        print(
            f"Предупреждение: Синдром указывает на позицию {syndrome}, которая выходит за пределы кодового слова длиной {len(code_list)}."
        )

    return "".join(code_list)


def ask_positive_int(question: str) -> int:
    """
    Запрашивает у пользователя положительное целое число.
    Повторяет запрос до тех пор, пока не будет введено корректное значение.
    """
    while True:
        try:
            value = int(input(question))
            if value <= 0:
                print("Ошибка: Значение должно быть положительным целым числом.")
                continue
            return value
        except ValueError:
            print("Ошибка: Введите корректное целое число.")


def ask_valid_k_and_r() -> Tuple[int, int]:
    """
    Запрашивает у пользователя значения k и r с проверкой корректности.
    Повторяет запрос до тех пор, пока не будут введены корректные значения.
    """
    while True:
        r = ask_positive_int(
            "Введите количество проверочных битов (r) для кода Хемминга: "
        )
        k = ask_positive_int("Введите размер информационной комбинации (k): ")

        max_k_for_r = (2**r) - r - 1
        if k > max_k_for_r:
            print(
                f"Ошибка: Для r={r} максимальное допустимое значение k составляет {max_k_for_r}."
            )
            print(f"Введенное k ({k}) слишком велико.")
            print("Пожалуйста, введите значения снова.")
            continue  # Повторный запрос

        print(f"Введенные значения r={r} и k={k} корректны.")
        return r, k


def main() -> None:
    # Открываем файл для записи результатов
    result_file_path: str = os.path.join(DIST_PATH, "hamming_results.txt")
    with open(result_file_path, "w", encoding="utf-8") as result_file:

        k: int = ask_positive_int("Введите размер информационной комбинации (k): ")
        r: int = ceil(log2(k))

        print_and_write(f"Введенные значения r={r} и k={k} корректны.", result_file)

        # 1. Генерируем комбинацию длины k
        data_combination: str = generate_random_combination(k)
        print_and_write(
            f"Сгенерирована случайная комбинация длины {k}: {data_combination}",
            result_file,
        )

        # 2. Вывести комбинацию в консоль
        info_combination_list = [
            int(c) for c in data_combination
        ]  # Преобразуем строку в список int
        print_and_write(
            f"Сгенерированная информационная комбинация: {info_combination_list}",
            result_file,
            prepend=False,
        )

        # 3. Методом Хемминга закодировать комбинацию
        try:
            encoded_combination = encode_hamming(data_combination, r)
        except ValueError as e:
            print_and_write(f"Ошибка при кодировании: {e}", result_file)
            return  # Завершаем программу, если кодирование невозможно из-за некорректных данных

        encoded_combination_list = [int(c) for c in encoded_combination]
        print_and_write(
            f"Закодированная комбинация: {encoded_combination_list}",
            result_file,
            prepend=False,
        )

        # Генерация и вывод таблицы Хемминга
        hamming_encoding_table = generate_hamming_table_for_encoding(k, r)
        print_and_write_table(hamming_encoding_table, result_file)

        print_and_write(
            f"Результат кодирования записан в {os.path.join(DIST_PATH, 'hamming_encoded.txt')}",
            result_file,
        )

        # 5. Внести ошибку в один из разрядов кодового вектора
        received_combination_with_error, error_index = introduce_error(
            encoded_combination
        )
        print_and_write(
            f"Внесена ошибка в позицию: {error_index + 1}", result_file, prepend=False
        )  # 1-индексированная позиция
        received_with_error_list = [
            int(c) for c in received_combination_with_error
        ]  # Преобразуем строку в список int
        print_and_write(
            f"Комбинация с ошибкой: {received_with_error_list}",
            result_file,
            prepend=False,
        )

        # 7. Найти синдром
        syndrome = calculate_syndrome(received_combination_with_error, r)
        # Вывод синдрома в двоичном виде (для наглядности, как в примере)
        syndrome_binary_str = bin(syndrome)[2:].zfill(r) if syndrome != 0 else "0"
        syndrome_list = [
            int(c) for c in syndrome_binary_str
        ]  # Преобразуем строку в список int
        print_and_write(f"Синдром: {syndrome_list}", result_file, prepend=False)
        print_and_write(
            f"Обнаруженная позиция ошибки: {syndrome}", result_file, prepend=False
        )

        # 8. Найти и исправить ошибку
        corrected_combination = correct_error(received_combination_with_error, syndrome)
        corrected_combination_list = [
            int(c) for c in corrected_combination
        ]  # Преобразуем строку в список int
        print_and_write(
            f"Исправленная комбинация: {corrected_combination_list}",
            result_file,
            prepend=False,
        )

        # 9. Сравнить результат с изначальным
        is_corrected = corrected_combination == encoded_combination
        print_and_write("Сравнение результатов:", result_file)
        print_and_write(f"Исходная комбинация:    {info_combination_list}", result_file)
        print_and_write(
            f"Извлеченная комбинация: {corrected_combination_list[:k]}", result_file
        )  # Извлекаем первые k битов
        print_and_write(f"Комбинации совпадают: {is_corrected}", result_file)

    print(f"Результаты сохранены в файл: hamming_results.txt")


if __name__ == "__main__":
    main()
