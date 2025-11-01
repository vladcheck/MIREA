original_alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюяqwertyuiopasdfghjklzxcvbnm"


def create_vigenere_key():
    """Запрашивает ключ для шифра Виженера."""
    key = input("\nВведите ключевое слово для шифра Виженера: ").lower()
    # Убираем символы, не входящие в алфавит
    clean_key = "".join(char for char in key if char in original_alphabet)
    if not clean_key:
        print("Ключ не содержит допустимых символов. Используется ключ 'ключ'.")
        clean_key = "ключ"
    return clean_key


def encrypt_vigenere(text, key):
    """Шифрует текст с помощью шифра Виженера."""
    alphabet_size = len(original_alphabet)
    key_index = 0
    encrypted = []

    for char in text:
        if char == " ":  # Пробелы не шифруются
            encrypted.append(char)
            continue

        if char in original_alphabet:
            # Находим индексы в алфавите
            text_char_index = original_alphabet.index(char)
            key_char_index = original_alphabet.index(key[key_index % len(key)])
            # Вычисляем индекс зашифрованного символа
            encrypted_char_index = (text_char_index + key_char_index) % alphabet_size
            encrypted.append(original_alphabet[encrypted_char_index])
            key_index += 1  # Увеличиваем индекс ключа только для букв
        else:
            # Символ не в алфавите, добавляем как есть (хотя предобработка должна была их удалить)
            encrypted.append(char)

    return "".join(encrypted)


def decrypt_vigenere(text, key):
    """Расшифровывает текст, зашифрованный с помощью шифра Виженера."""
    alphabet_size = len(original_alphabet)
    key_index = 0
    decrypted = []

    for char in text:
        if char == " ":  # Пробелы не расшифровываются
            decrypted.append(char)
            continue

        if char in original_alphabet:
            # Находим индексы в алфавите
            text_char_index = original_alphabet.index(char)
            key_char_index = original_alphabet.index(key[key_index % len(key)])
            # Вычисляем индекс расшифрованного символа
            decrypted_char_index = (text_char_index - key_char_index) % alphabet_size
            decrypted.append(original_alphabet[decrypted_char_index])
            key_index += 1  # Увеличиваем индекс ключа только для букв
        else:
            # Символ не в алфавите, добавляем как есть
            decrypted.append(char)

    return "".join(decrypted)


def print_per_symbol(processed_text: str, encrypted_text: str, key: str):
    original_chars = list(processed_text)
    key_repeated = (key * ((len(original_chars) // len(key)) + 1))[
        : len(original_chars)
    ]
    encrypted_chars = list(encrypted_text)

    print("Сообщение " + " ".join(original_chars))
    print("Ключ      " + " ".join(key_repeated))
    print("Шифртекст " + " ".join(encrypted_chars))
    print("----------------------------------------")
