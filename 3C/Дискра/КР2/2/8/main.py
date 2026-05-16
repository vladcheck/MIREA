import re
from collections import Counter
import os
from typing import LiteralString

russian_letter_frequencies: dict[str, float] = {
    " ": 17.50,
    "о": 9.00,
    "е": 7.20,
    "а": 6.20,
    "и": 6.20,
    "н": 5.30,
    "т": 5.30,
    "с": 4.50,
    "р": 4.00,
    "в": 3.80,
    "л": 3.50,
    "к": 2.80,
    "м": 2.60,
    "д": 2.50,
    "п": 2.30,
    "у": 2.10,
    "\n": 2,
    "я": 1.80,
    "ы": 1.60,
    "з": 1.60,
    "ж": 0.70,
    "х": 0.90,
    "ч": 1.20,
    "ш": 0.60,
    "ю": 0.60,
    "ц": 0.40,
    "щ": 0.30,
    "э": 0.30,
    "ф": 0.20,
    "ъ": 1.40,
    "ь": 1.40,
    "б": 1.40,
    "г": 1.30,
    "й": 1.00,
}


def preprocess_text(text: str) -> str:
    """Приводит текст к нижнему регистру и удаляет всё, кроме букв и пробелов."""
    processed: str = text.lower()
    processed = re.sub(r"[^а-яё ]", "", processed, flags=re.IGNORECASE)
    processed = re.sub(r"\s+", " ", processed).strip()
    return processed


def caesar_encrypt(text: str, shift: int, alphabet: str) -> str:
    """Шифрует текст шифром Цезаря."""
    encrypted_text: str = ""
    alphabet_size: int = len(alphabet)
    for char in text:
        if char in alphabet:
            old_index: int = alphabet.index(char)
            new_index: int = (old_index + shift) % alphabet_size
            encrypted_text += alphabet[new_index]
        else:
            encrypted_text += char  # Неизвестные символы остаются без изменений
    return encrypted_text


def caesar_decrypt(text: str, shift: int, alphabet: str) -> str:
    """Расшифровывает текст, зашифрованный шифром Цезаря."""
    return caesar_encrypt(text, -shift, alphabet)


def calculate_frequencies(text: str) -> dict[str, float]:
    """Рассчитывает частоту появления каждого символа в тексте (в процентах)."""
    if not text:
        return {}
    total_chars: int = len(text)
    char_counts: Counter[str] = Counter(text)
    return {char: (count / total_chars) * 100 for char, count in char_counts.items()}


def sort_by_frequency(frequencies: dict[str, float]) -> list[tuple[str, float]]:
    """Сортирует символы по убыванию частоты."""
    return sorted(frequencies.items(), key=lambda item: item[1], reverse=True)


def crack_caesar_by_frequency(
    encrypted_text: str, alphabet: str, target_frequencies: dict[str, float]
) -> tuple[int, str]:
    """
    Пытается расшифровать шифр Цезаря методом частотного анализа.
    Возвращает (найденный_сдвиг, расшифрованный_текст).
    """
    enc_freqs: dict[str, float] = calculate_frequencies(encrypted_text)
    sorted_enc_freqs: list[tuple[str, float]] = sort_by_frequency(enc_freqs)
    sorted_target_freqs: list[tuple[str, float]] = sort_by_frequency(target_frequencies)

    if not sorted_enc_freqs or not sorted_target_freqs:
        print("Ошибка: Недостаточно данных для анализа.")
        return (0, "")  # Возвращаем 0 и пустую строку, если анализ невозможен

    most_common_enc_char = sorted_enc_freqs[0][0]
    most_common_rus_char = sorted_target_freqs[0][0]

    print(f"Наиболее частый символ в шифротексте: '{most_common_enc_char}'")
    print(f"Наиболее частый символ в русском языке: '{most_common_rus_char}'")

    idx_enc = alphabet.index(most_common_enc_char)
    idx_rus = alphabet.index(most_common_rus_char)
    calculated_shift = (idx_enc - idx_rus) % len(alphabet)

    print(f"Предполагаемый сдвиг (из самых частых букв): {calculated_shift}")

    decrypted_attempt = caesar_decrypt(encrypted_text, calculated_shift, alphabet)

    print(f"Результат расшифровки с предполагаемым сдвигом {calculated_shift}:")
    print(decrypted_attempt[:200] + ("..." if len(decrypted_attempt) > 200 else ""))
    print("-" * 50)

    best_shift: int = calculated_shift
    best_decrypted: str = decrypted_attempt
    best_match_score = float("-inf")

    print("\n--- Перебор всех возможных сдвигов для подтверждения ---")
    for potential_shift in range(len(alphabet)):
        potential_decrypted: str = caesar_decrypt(
            encrypted_text, potential_shift, alphabet
        )
        potential_freqs: dict[str, float] = calculate_frequencies(potential_decrypted)
        match_score = 0
        for char, freq in target_frequencies.items():
            pot_freq = potential_freqs.get(char, 0)
            match_score += min(pot_freq, freq)

        print(
            f"Сдвиг {potential_shift:2d}: Score={match_score:.2f} -> {potential_decrypted[:50]}..."
        )

        if match_score > best_match_score:
            best_match_score: float = match_score
            best_shift = potential_shift
            best_decrypted = potential_decrypted

    print("-" * 50)
    print(f"Лучший сдвиг по перебору: {best_shift} (Score: {best_match_score:.2f})")
    print(f"Лучший расшифрованный текст (первые 200 символов):")
    print(best_decrypted[:200] + ("..." if len(best_decrypted) > 200 else ""))

    return best_shift, best_decrypted


def main():
    print("=== Криптоанализ шифра Цезаря методом частотного анализа ===\n")

    filename = "input.txt"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            original_text_raw = f.read()
        print(f"Текст успешно прочитан из '{filename}'.")
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        print(
            "Создайте файл 'input.txt' с текстом для шифрования или продолжим с примером."
        )
        # Пример текста
        original_text_raw = """Пример текста для криптоанализа. Этот текст будет зашифрован шифром Цезаря, а затем расшифрован методом частотного анализа. В тексте много слов, связанных с шифрами, частотами и анализом."""

    original_text = preprocess_text(original_text_raw)
    print(
        f"Исходный текст (после обработки, первые 200 символов):\n{original_text[:200]}...\n"
    )

    alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя "  # Определяем алфавит
    print(f"Используемый алфавит: {alphabet}\n")
    print("Для шифрования используется шифр Цезаря.")
    try:
        shift = int(input("Введите сдвиг (целое число) для шифра Цезаря: "))
        shift: int = shift % len(alphabet)  # Обеспечиваем валидность сдвига
        if shift < 0:
            shift = shift + len(alphabet)
    except ValueError:
        print("Некорректный ввод. Используем сдвиг 5.")
        shift = 5

    encrypted_text = caesar_encrypt(original_text, shift, alphabet)
    print(f"\nЗашифрованный текст (сдвиг {shift}):\n{encrypted_text}\n")

    dist_path = "out"
    if not os.path.exists(dist_path):
        os.makedirs(dist_path)
    encrypted_file_path: LiteralString = os.path.join(dist_path, "encrypted_caesar.txt")
    with open(encrypted_file_path, "w", encoding="utf-8") as f:
        f.write(encrypted_text)
    print(f"Зашифрованный текст сохранён в '{encrypted_file_path}'.")

    print("--- НАЧАЛО КРИПТОАНАЛИЗА ---")
    try:
        with open(encrypted_file_path, "r", encoding="utf-8") as f:
            encrypted_text_from_file = f.read()
    except Exception as e:
        print(f"Ошибка при чтении зашифрованного файла: {e}")
        return

    found_shift, decrypted_result = crack_caesar_by_frequency(
        encrypted_text_from_file, alphabet, russian_letter_frequencies
    )

    print("\n--- РЕЗУЛЬТАТЫ КРИПТОАНАЛИЗА ---")
    print(f"Предполагаемый сдвиг: {found_shift}")
    print(f"Расшифрованный текст (первые 500 символов):\n{decrypted_result[:500]}...")
    if len(decrypted_result) > 500:
        print("... (вывод обрезан)")
    print("-" * 50)

    print("\n--- СРАВНЕНИЕ ---")
    print(f"Исходный текст (первые 500): {original_text[:500]}...")
    print(f"Расшифрованный текст (первые 500): {decrypted_result[:500]}...")
    is_match = original_text == decrypted_result
    print(f"Тексты совпадают: {is_match}\n")

    results_file_path: LiteralString = os.path.join(dist_path, "results.txt")
    try:
        with open(results_file_path, "w", encoding="utf-8") as f:
            f.write("=== РЕЗУЛЬТАТЫ КРИПТОАНАЛИЗА ШИФРА ЦЕЗАРЯ ===\n\n")
            f.write(f"Использованный сдвиг для шифрования: {shift}\n")
            f.write(f"Предположенный сдвиг (найденный): {found_shift}\n")
            f.write(f"Сдвиги совпадают: {shift == found_shift}\n\n")
            f.write(f"--- ИСХОДНЫЙ ТЕКСТ ---\n{original_text}\n\n")
            f.write(f"--- ЗАШИФРОВАННЫЙ ТЕКСТ ---\n{encrypted_text}\n\n")
            f.write(f"--- РАСШИФРОВАННЫЙ ТЕКСТ ---\n{decrypted_result}\n\n")
            f.write(f"--- СРАВНЕНИЕ ---\n")
            f.write(f"Совпадение: {is_match}\n")
            f.write(f"Частоты русского языка: {russian_letter_frequencies}\n\n\n")
            f.write(
                f"Частоты данного текста: {calculate_frequencies(original_text)}\n\n\n"
            )
        print(f"Результаты анализа сохранены в '{results_file_path}'")
    except Exception as e:
        print(f"Ошибка при записи результатов: {e}")

    print("\n--- КРИПТОАНАЛИЗ ЗАВЕРШЕН ---")


if __name__ == "__main__":
    main()
