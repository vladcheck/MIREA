from main import *
import math
import os
import heapq


def create_huffman_dist_folder() -> str:
    """
    Создает папку huffman_dist в текущей директории и возвращает её абсолютный путь.
    """
    folder_name = "huffman_dist"
    dist_path: str = os.path.abspath(folder_name)

    if not os.path.exists(dist_path):
        os.makedirs(dist_path, exist_ok=True)
        print(f"Папка {dist_path} создана.")
    else:
        print(f"Папка {dist_path} уже существует.")

    return dist_path


DIST_PATH: str = create_huffman_dist_folder()


def huffman_tree(alphabet: dict[str, int]) -> dict[str, str]:
    """
    Строит дерево Хаффмана и возвращает словарь с кодами для каждого символа.
    """
    heap = [[freq, [char, ""]] for char, freq in alphabet.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        low = heapq.heappop(heap)
        high = heapq.heappop(heap)

        for pair in low[1:]:
            pair[1] = "0" + pair[1]
        for pair in high[1:]:
            pair[1] = "1" + pair[1]

        new_node = [low[0] + high[0]] + low[1:] + high[1:]
        heapq.heappush(heap, new_node)

    huffman_codes = heap[0][1:]
    return {char: code for char, code in huffman_codes}


def write_huffman_codes_to_csv(codes: dict[str, str], csv_filename: str) -> None:
    """
    Записывает схему кодирования Хаффмана в CSV файл.
    Путь к файлу формируется с учетом DIST_PATH.
    """
    full_csv_path: str = os.path.join(DIST_PATH, csv_filename)
    write_codes_to_csv(codes, full_csv_path)


def encode_text_huffman_single_chars(text: str, codes: dict[str, str]) -> str:
    """
    Кодирует текст, используя коды Хаффмана для отдельных символов.
    Каждый символ заменяется соответствующим кодом из словаря 'codes'.
    """
    encoded_text: str = ""
    for char in text:
        if char in codes:
            encoded_text += codes[char]
        else:
            raise KeyError(f"Символ '{char}' не найден в словаре кодирования Хаффмана.")
    return encoded_text


def decode_text_huffman_single_chars(encoded_text: str, codes: dict[str, str]) -> str:
    """
    Декодирует текст, закодированный с помощью кодов Хаффмана для отдельных символов.
    Использует инвертированный словарь кодов для восстановления исходного текста.
    """
    inverted_codes: dict[str, str] = {code: char for char, code in codes.items()}

    decoded_text: str = ""
    code_buffer: str = ""

    for bit in encoded_text:
        code_buffer += bit
        if code_buffer in inverted_codes:
            decoded_text += inverted_codes[code_buffer]
            code_buffer = ""

    if code_buffer:
        print(
            f"Предупреждение: Неполная последовательность кода '{code_buffer}' найдена в конце кодированного текста при декодировании."
        )

    return decoded_text


def encode_text_huffman_bigrams(text: str, codes: dict[str, str]) -> str:
    """
    Кодирует текст, рассматривая его как последовательность биграмм.
    Каждая биграмма заменяется соответствующим кодом из словаря 'codes'.
    """
    encoded_text: str = ""

    for i in range(0, len(text) - 1, 2):
        bigram: str = text[i : i + 2]
        if bigram in codes:
            encoded_text += codes[bigram]
        else:
            raise KeyError(
                f"Биграмма '{bigram}' не найдена в словаре кодирования Хаффмана."
            )

    if len(text) % 2 == 1:
        last_char: str = text[-1]
        print(
            f"Примечание: Последний символ '{last_char}' не является частью биграммы и не закодирован."
        )

    return encoded_text


def decode_text_huffman_bigrams(encoded_text: str, codes: dict[str, str]) -> str:
    """
    Декодирует текст, закодированный с помощью кодов Хаффмана для биграмм.
    Использует инвертированный словарь кодов для восстановления исходного текста.
    """
    inverted_codes: dict[str, str] = {code: bigram for bigram, code in codes.items()}

    decoded_text: str = ""
    code_buffer: str = ""

    for bit in encoded_text:
        code_buffer += bit
        if code_buffer in inverted_codes:
            decoded_text += inverted_codes[code_buffer]
            code_buffer = ""

    if code_buffer:
        print(
            f"Предупреждение: Неполная последовательность кода '{code_buffer}' найдена в конце кодированного текста при декодировании."
        )

    return decoded_text


def main() -> None:
    filename = "./input.txt"
    text: str = read_text_from_file(filename).lower().strip()

    # 8. Построить схему алфавитного кодирования для однобуквенных сочетаний методом Хаффмана
    alphabet: dict[str, int] = create_alphabet_with_frequencies(text)
    huffman_codes: dict[str, str] = huffman_tree(alphabet)

    # 9. Вывести схему в CSV файл
    write_huffman_codes_to_csv(huffman_codes, "huffman_codes.csv")

    # 17*. Повторить для биграмм
    bigram_alphabet: dict[str, int] = {}
    for i in range(len(text) - 1):
        bigram: str = text[i : i + 2]
        if bigram in bigram_alphabet:
            bigram_alphabet[bigram] += 1
        else:
            bigram_alphabet[bigram] = 1

    huffman_bigram_codes: dict[str, str] = huffman_tree(bigram_alphabet)
    write_huffman_codes_to_csv(huffman_bigram_codes, "huffman_bigram_codes.csv")

    avg_huffman_code_length: float = calculate_average_code_length(
        huffman_codes, alphabet
    )
    compression_efficiency_huffman: float = calculate_compression_efficiency(
        math.ceil(math.log2(len(alphabet))), avg_huffman_code_length
    )

    avg_huffman_bigram_code_length: float = calculate_average_code_length(
        huffman_bigram_codes, bigram_alphabet
    )
    compression_efficiency_huffman_bigram: float = calculate_compression_efficiency(
        math.ceil(math.log2(len(bigram_alphabet))), avg_huffman_bigram_code_length
    )

    print(f"Средняя длина кода Хаффмана (однобуквенные): {avg_huffman_code_length}")
    print(
        f"Эффективность сжатия Хаффмана (однобуквенные): {truncate(compression_efficiency_huffman)}"
    )
    print(f"Средняя длина кода Хаффмана (биграммы): {avg_huffman_bigram_code_length}")
    print(
        f"Эффективность сжатия Хаффмана (биграммы): {truncate(compression_efficiency_huffman_bigram)}"
    )

    try:
        encoded_huffman_text: str = encode_text_huffman_single_chars(
            text, huffman_codes
        )
        decoded_huffman_text: str = decode_text_huffman_single_chars(
            encoded_huffman_text, huffman_codes
        )
    except KeyError as e:
        print(f"Ошибка при кодировании/декодировании однобуквенных кодов: {e}")
        return

    try:
        encoded_huffman_bigram_text: str = encode_text_huffman_bigrams(
            text, huffman_bigram_codes
        )
        decoded_huffman_bigram_text: str = decode_text_huffman_bigrams(
            encoded_huffman_bigram_text, huffman_bigram_codes
        )
    except KeyError as e:
        print(f"Ошибка при кодировании/декодировании биграмм: {e}")
        return

    with open(
        os.path.join(DIST_PATH, "encoded_huffman.txt"), "w", encoding="utf-8"
    ) as file:
        file.write(encoded_huffman_text)
    with open(
        os.path.join(DIST_PATH, "decoded_huffman.txt"), "w", encoding="utf-8"
    ) as file:
        file.write(decoded_huffman_text)
    with open(
        os.path.join(DIST_PATH, "encoded_huffman_bigram.txt"), "w", encoding="utf-8"
    ) as file:
        file.write(encoded_huffman_bigram_text)
    with open(
        os.path.join(DIST_PATH, "decoded_huffman_bigram.txt"), "w", encoding="utf-8"
    ) as file:
        file.write(decoded_huffman_bigram_text)


if __name__ == "__main__":
    main()
