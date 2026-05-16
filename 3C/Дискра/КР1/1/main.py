import csv
import math
from typing import Any, Literal
import os
from truncate import truncate


def create_dist_folder() -> str:
    """
    Создает папку bigram_dist в текущей директории и возвращает её абсолютный путь.
    """
    folder_name = "main_dist"
    dist_path: str = os.path.abspath(folder_name)

    if not os.path.exists(dist_path):
        os.makedirs(dist_path, exist_ok=True)
        print(f"Папка {dist_path} создана.")
    else:
        print(f"Папка {dist_path} уже существует.")

    return dist_path


DIST_PATH: str = create_dist_folder()


def read_text_from_file(filename) -> str:
    with open(filename, "r", encoding="utf-8") as file:
        t: str = file.read().strip()
        return t


def create_alphabet_with_frequencies(text) -> dict[str, int]:
    alphabet: dict[str, int] = {}
    for char in text.lower():
        if char in alphabet:
            alphabet[char] += 1
        else:
            alphabet[char] = 1
    return alphabet


def write_alphabet_to_csv(alphabet, csv_filename) -> None:
    total_chars: int = sum(alphabet.values())
    with open(
        os.path.join(DIST_PATH, csv_filename), "w", newline="", encoding="utf-8"
    ) as csvfile:
        fieldnames: list[str] = [
            "Символ",
            "Частота",
            "Вероятность",
        ]
        writer: csv.DictWriter[str] = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for char, freq in alphabet.items():
            probability: float = freq / total_chars
            writer.writerow(
                {"Символ": char, "Частота": float(freq), "Вероятность": (probability)}
            )


def calculate_entropy(alphabet) -> int:
    total_chars: int = sum(alphabet.values())
    probabilities = [freq / total_chars for freq in alphabet.values()]
    entropy: int = -sum(p * math.log2(p) for p in probabilities if p > 0)
    return entropy


def calculate_uniform_code_length(alphabet) -> int:
    unique_chars: int = len(alphabet)
    return math.ceil(math.log2(unique_chars))


def calculate_redundancy(entropy, uniform_code_length) -> float:
    return (uniform_code_length - entropy) / uniform_code_length


def assign_code(alphabet_list, code="") -> dict[Any, str] | Any:
    if len(alphabet_list) == 1:
        return {alphabet_list[0][0]: code}

    total_freq = sum(freq for _, freq in alphabet_list)
    cumulative_freq = 0
    split_index = 0

    for i, (char, freq) in enumerate(alphabet_list):
        cumulative_freq += freq
        if cumulative_freq >= total_freq / 2:
            split_index: int = i
            break

    left_codes: dict[Any, str] | Any = assign_code(
        alphabet_list[: split_index + 1], code + "0"
    )
    right_codes: dict[Any, str] | Any = assign_code(
        alphabet_list[split_index + 1 :], code + "1"
    )

    left_codes.update(right_codes)
    return left_codes


def shannon_fano(alphabet) -> dict[Any, str] | Any:
    sorted_alphabet = sorted(alphabet.items(), key=lambda x: x[1], reverse=True)
    return assign_code(sorted_alphabet)


def calculate_average_code_length(codes, alphabet) -> float:
    total_chars: int = sum(alphabet.values())
    avg_length: float = (
        sum(alphabet[char] * len(code) for char, code in codes.items()) / total_chars
    )
    return avg_length


def calculate_compression_efficiency(uniform_code_length, avg_code_length) -> float:
    return (uniform_code_length - avg_code_length) / uniform_code_length


def write_codes_to_csv(codes, csv_filename) -> None:
    with open(
        os.path.join(DIST_PATH, csv_filename), "w", newline="", encoding="utf-8"
    ) as csvfile:
        fieldnames: list[str] = ["Символ", "Код"]
        writer: csv.DictWriter[str] = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for char, code in codes.items():
            writer.writerow({"Символ": char, "Код": code})


def encode_text(text, codes) -> Any | Literal[""]:
    encoded_text: Literal[""] = ""

    for char in text:
        encoded_text += codes[char]
    return encoded_text


def decode_text(encoded_text, codes) -> Any | Literal[""]:
    inverted_codes = {code: char for char, code in codes.items()}
    decoded_text: Literal[""] = ""
    code: Literal[""] = ""

    for bit in encoded_text:
        code += bit
        if code in inverted_codes:
            decoded_text += inverted_codes[code]
            code = ""
    return decoded_text


if __name__ == "__main__":
    filename: str = os.path.abspath("./input.txt")
    text: str = read_text_from_file(filename)

    text = text.lower()

    alphabet: dict[str, int] = create_alphabet_with_frequencies(text)

    write_alphabet_to_csv(alphabet, "alphabet.csv")

    entropy: int = calculate_entropy(alphabet)
    uniform_code_length: int = calculate_uniform_code_length(alphabet)
    redundancy: float = calculate_redundancy(entropy, uniform_code_length)

    shannon_fano_codes: dict[Any, str] | Any = shannon_fano(alphabet)

    write_codes_to_csv(shannon_fano_codes, "shannon_fano_codes.csv")

    avg_code_length: float = calculate_average_code_length(shannon_fano_codes, alphabet)
    compression_efficiency: float = calculate_compression_efficiency(
        uniform_code_length, avg_code_length
    )

    print(f"Энтропия: {truncate(entropy)}")
    print(f"Длина равномерного кода: {truncate(uniform_code_length)}")
    print(f"Избыточность: {truncate(redundancy)}")
    print(f"Средняя длина кода: {truncate(avg_code_length)}")
    print(f"Эффективность сжатия: {truncate(compression_efficiency)}")

    encoded_text: Any | Literal[""] = encode_text(text, shannon_fano_codes)
    decoded_text: Any | Literal[""] = decode_text(encoded_text, shannon_fano_codes)

    with open(os.path.join(DIST_PATH, "encoded.txt"), "w", encoding="utf-8") as file:
        file.write(encoded_text)

    with open(os.path.join(DIST_PATH, "decoded.txt"), "w", encoding="utf-8") as file:
        file.write(decoded_text)
