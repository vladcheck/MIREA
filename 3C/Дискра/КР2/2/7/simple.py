original_alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def create_simple_substitution_cipher_key():
    """
    Создает ключ шифрования простой замены.
    Запрашивает у пользователя строку, которая будет использоваться как "алфавит шифра".
    Очищает строку от дубликатов и убирает символы, не входящие в исходный алфавит.
    """
    unique_chars_in_key = []
    seen = set()
    user_input = input("Введите ключевую строку для шифра простой замены: ").lower()
    for char in user_input:
        if char not in seen and char in original_alphabet:
            unique_chars_in_key.append(char)
            seen.add(char)

    cipher_alphabet_list = unique_chars_in_key[:]
    for char in original_alphabet:
        if char not in cipher_alphabet_list:
            cipher_alphabet_list.append(char)

    cipher_alphabet = "".join(cipher_alphabet_list)
    print(f"Созданный алфавит шифра: {cipher_alphabet}")

    cipher_map = {}
    for i, char in enumerate(original_alphabet):
        cipher_map[char] = cipher_alphabet[i]

    print("\nТаблица замен (открытый алфавит -> алфавит шифра):")
    print("-" * 50)
    sorted_items = sorted(cipher_map.items())  # Сортируем по ключу (исходной букве)
    line_parts = []
    for frm, to in sorted_items:
        line_parts.append(f"{frm}->{to}")
        if len(line_parts) == 8:
            print("  ".join(line_parts))
            line_parts = []
    if line_parts:
        print("  ".join(line_parts))
    print("-" * 50)

    return cipher_map


def create_decryption_map_from_encryption(cipher_map):
    """Создает словарь для расшифровки из словаря шифрования."""
    return {v: k for k, v in cipher_map.items()}


def encrypt_simple_substitution(text, cipher_map):
    """Шифрует текст с использованием словаря шифрования."""
    return "".join(cipher_map.get(char, char) for char in text)


def decrypt_simple_substitution(text, decipher_map):
    """Расшифровывает текст с использованием словаря расшифровки."""
    return "".join(decipher_map.get(char, char) for char in text)
