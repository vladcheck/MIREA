# main.py (обновленный)

# --- (ВАШ СУЩЕСТВУЮЩИЙ КОД ДО ФУНКЦИИ main) ---


# --- НОВАЯ ФУНКЦИЯ ДЛЯ АТАКИ НА ШИФР ЦЕЗАРЯ ---
import os


def brute_force_caesar(
    ciphertext: str, alphabet: str = "абвгдежзийклмнопрстуфхцчшщъыьэюя "
) -> list[tuple[int, str]]:
    """
    Перебирает все возможные сдвиги для шифра Цезаря и возвращает список пар (сдвиг, расшифрованный_текст).
    """
    possible_decryptions = []
    alphabet_size = len(alphabet)

    # Перебираем все возможные сдвиги (от 1 до 31 включительно, 0 - это отсутствие сдвига)
    for shift in range(1, alphabet_size):
        decrypted_text = ""
        for char in ciphertext:
            if char in alphabet:
                old_index = alphabet.index(char)
                # Вычисляем новый индекс, учитывая "зацикленность" алфавита
                new_index = (old_index - shift) % alphabet_size
                decrypted_text += alphabet[new_index]
            else:
                # Если символ не в алфавите (например, цифра или специальный символ),
                # оставляем его без изменений.
                # В вашем случае с предварительной обработкой таких символов быть не должно.
                decrypted_text += char
        possible_decryptions.append((shift, decrypted_text))

    return possible_decryptions


# --- ОБНОВЛЁННАЯ ФУНКЦИЯ main ---
def main() -> None:
    """Основная функция программы."""
    print("=== ИНСТРУМЕНТ КРИПТОАНАЛИЗА АФФИННОГО ШИФРА ===")

    # --- ШАГ 1: ШИФРОВАНИЕ АФФИННЫМ ШИФРОМ (ВАШ СУЩЕСТВУЮЩИЙ КОД) ---
    # ... (весь ваш существующий код для шифрования) ...
    # Предположим, что после выполнения шага 1 у вас есть файл 'encrypted.txt'
    # и вы знаете, что он содержит зашифрованный АФФИННЫМ шифром текст.
    # ...

    # --- ШАГ 4: КРИПТОАНАЛИЗ ЗАШИФРОВАННОГО ТЕКСТА (ВАШ СУЩЕСТВУЮЩИЙ КОД) ---
    # ... (ваш существующий код для анализа Хемминга) ...
    # ...

    # --- НОВЫЙ ШАГ: АТАКА НА ШИФР ЦЕЗАРЯ ---
    print("\n=== ШАГ: АТАКА ПОЛНЫМ ПЕРЕБОРОМ НА ШИФР ЦЕЗАРЯ ===")
    print(
        "Предполагается, что зашифрованный текст в 'encrypted.txt' может быть результатом шифра Цезаря."
    )
    print("Будут перебраны все возможные сдвиги.")

    # 1. Прочитать зашифрованный текст
    encrypted_filename = "encrypted.txt"
    try:
        with open(encrypted_filename, "r", encoding="utf-8") as f:
            caesar_ciphertext = f.read().strip()
        print(
            f"Зашифрованный текст из '{encrypted_filename}':\n{caesar_ciphertext[:200]}..."
        )  # Печатаем первые 200 символов
        print("-" * 50)
    except FileNotFoundError:
        print(f"Файл '{encrypted_filename}' не найден. Пропуск атаки на Цезарь.")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла '{encrypted_filename}': {e}")
        return

    # 2. Перебрать все сдвиги
    possible_outcomes = brute_force_caesar(caesar_ciphertext)

    # 3. Вывести все результаты в консоль
    print("\n--- РЕЗУЛЬТАТЫ ПЕРЕБОРА (Сдвиг -> Текст) ---")
    for shift, decrypted in possible_outcomes:
        print(
            f"Сдвиг {shift:2d}: {decrypted[:100]}..."
        )  # Печатаем первые 100 символов каждого результата
    print("-" * 50)

    # 4. Сохранить все результаты в файл
    output_file_path = "caesar_brute_force_results.txt"
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("=== РЕЗУЛЬТАТЫ АТАКИ ПОЛНЫМ ПЕРЕБОРОМ НА ШИФР ЦЕЗАРЯ ===\n\n")
            for shift, decrypted in possible_outcomes:
                f.write(f"--- Сдвиг {shift:2d} ---\n")
                f.write(f"{decrypted}\n")
                f.write("\n" + "=" * 20 + "\n")
        print(f"\nВсе результаты перебора сохранены в '{output_file_path}'.")
    except Exception as e:
        print(f"Ошибка при записи файла '{output_file_path}': {e}")

    print("\n--- АТАКА НА ШИФР ЦЕЗАРЯ ЗАВЕРШЕНА ---")
    print(
        "Проанализируйте результаты в консоли или файле, чтобы найти осмысленный текст."
    )
    print("Сдвиг, при котором получен осмысленный текст, является искомым ключом.")


if __name__ == "__main__":
    main()
