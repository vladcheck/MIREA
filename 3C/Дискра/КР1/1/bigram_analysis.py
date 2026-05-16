from main import *
from typing import Any, Literal
import math
import os


def create_bigram_dist_folder() -> str:
    """
    Создает папку bigram_dist в текущей директории и возвращает её абсолютный путь.
    """
    folder_name = "bigram_dist"
    dist_path = os.path.abspath(folder_name)

    if not os.path.exists(dist_path):
        os.makedirs(dist_path, exist_ok=True)
        print(f"Папка {dist_path} создана.")
    else:
        print(f"Папка {dist_path} уже существует.")

    return dist_path


DIST_PATH: str = create_bigram_dist_folder()


def create_bigram_alphabet_with_frequencies(text: str) -> dict[str, int]:
    """
    Создает алфавит биграмм с их частотами из текста.
    """
    bigram_alphabet: dict[str, int] = {}
    for i in range(len(text) - 1):
        bigram: str = text[i : i + 2]  # Берем пару символов
        if bigram in bigram_alphabet:
            bigram_alphabet[bigram] += 1
        else:
            bigram_alphabet[bigram] = 1
    return bigram_alphabet


def calculate_bigram_entropy(bigram_alphabet) -> float | int:
    """
    Вычисляет энтропию для биграмм.
    """
    total_bigrams: int = sum(bigram_alphabet.values())
    probabilities: list[float] = [
        freq / total_bigrams for freq in bigram_alphabet.values()
    ]
    entropy: float | int = -sum(p * math.log2(p) for p in probabilities if p > 0)
    return entropy


def write_bigram_codes_to_csv(codes, csv_filename) -> None:
    """
    Записывает схему кодирования биграмм в CSV файл, используя функцию из main.py.
    Путь к файлу формируется с учетом DIST_PATH.
    """
    full_csv_path: str = os.path.join(DIST_PATH, csv_filename)
    write_codes_to_csv(codes, full_csv_path)


def encode_text_bigrams(text: str, codes: dict[str, str]) -> str:
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
            raise KeyError(f"Биграмма '{bigram}' не найдена в словаре кодирования.")

    if len(text) % 2 == 1:
        last_char: str = text[-1]
        print(
            f"Примечание: Последний символ '{last_char}' не является частью биграммы и не закодирован."
        )

    return encoded_text


def decode_text_bigrams(encoded_text: str, codes: dict[str, str]) -> str:
    """
    Декодирует текст, где исходный текст был представлен как последовательность биграмм.
    Кодированный текст декодируется с использованием инвертированного словаря 'codes'.
    """
    inverted_codes: dict[str, str] = {code: bigram for bigram, code in codes.items()}

    decoded_text: str = ""
    code_buffer: str = ""  # Буфер для сбора битов кода

    for bit in encoded_text:
        code_buffer += bit
        if code_buffer in inverted_codes:
            decoded_text += inverted_codes[code_buffer]
            code_buffer = ""  # Сброс буфера после нахождения соответствия

    if code_buffer:
        print(
            f"Предупреждение: Неполная последовательность кода '{code_buffer}' найдена в конце кодированного текста при декодировании."
        )

    return decoded_text


def main() -> None:
    filename = "input.txt"
    text: str = read_text_from_file(filename).lower().strip()

    bigram_alphabet: dict[str, int] = create_bigram_alphabet_with_frequencies(text)
    bigram_entropy: float | int = calculate_bigram_entropy(bigram_alphabet)
    shannon_fano_bigram_codes: dict[Any, str] | Any = shannon_fano(bigram_alphabet)

    write_bigram_codes_to_csv(
        shannon_fano_bigram_codes, "shannon_fano_bigram_codes.csv"
    )

    avg_bigram_code_length: float = calculate_average_code_length(
        shannon_fano_bigram_codes, bigram_alphabet
    )
    compression_efficiency_bigram: float = calculate_compression_efficiency(
        math.ceil(math.log2(len(bigram_alphabet))), avg_bigram_code_length
    )

    print(f"Энтропия буквосочетаний: {truncate(bigram_entropy)} бит/с")
    print(f"Средняя длина буквосочетаний: {math.ceil(avg_bigram_code_length)} бит")
    print(
        f"Эффективность сжатия буквосочетаний: {truncate(compression_efficiency_bigram)}"
    )

    try:
        encoded_bigram_text: Any | Literal[""] = encode_text_bigrams(
            text, shannon_fano_bigram_codes
        )
    except KeyError as e:
        print(f"Ошибка при кодировании: {e}")
        return  # Выход, если произошла ошибка при кодировании

    decoded_bigram_text: Any | Literal[""] = decode_text_bigrams(
        encoded_bigram_text, shannon_fano_bigram_codes
    )

    encoded_file_path: str = os.path.join(DIST_PATH, "encoded_bigram.txt")
    decoded_file_path: str = os.path.join(DIST_PATH, "decoded_bigram.txt")

    with open(encoded_file_path, "w", encoding="utf-8") as file:
        file.write(encoded_bigram_text)

    with open(decoded_file_path, "w", encoding="utf-8") as file:
        file.write(decoded_bigram_text)


if __name__ == "__main__":
    main()
