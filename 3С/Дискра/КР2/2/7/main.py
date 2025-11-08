import re
from typing import LiteralString
from simple import *
from vigenere import *


def test_simple():
    f = open("simple.txt", "+w", encoding="utf8")
    cipher_map_simple = create_simple_substitution_cipher_key()
    encrypted_text_simple: LiteralString = encrypt_simple_substitution(
        processed_text, cipher_map_simple
    )
    f.write(encrypted_text_simple)
    f.close()
    print(f"\nТекст, зашифрованный шифром простой замены:\n{encrypted_text_simple}\n")

    decipher_map_simple = create_decryption_map_from_encryption(cipher_map_simple)
    decrypted_text_simple: LiteralString = decrypt_simple_substitution(
        encrypted_text_simple, decipher_map_simple
    )
    print(f"Текст, расшифрованный шифром простой замены:\n{decrypted_text_simple}\n")
    print(
        f"Совпадает ли расшифрованный текст с обработанным? {decrypted_text_simple == processed_text}"
    )


def test_vigenere():
    f = open("vigenere.txt", "+w", encoding="utf8")
    vigenere_key: str = create_vigenere_key()
    encrypted_text_vigenere: LiteralString = encrypt_vigenere(
        processed_text, vigenere_key
    )
    f.write(f"Ключ: {vigenere_key}\n\n")
    f.write(encrypted_text_vigenere)
    f.close()
    print(
        f"\nТекст, зашифрованный шифром Виженера (сложная замена):\n{encrypted_text_vigenere}\n"
    )

    decrypted_text_vigenere: LiteralString = decrypt_vigenere(
        encrypted_text_vigenere, vigenere_key
    )
    print(
        f"Текст, расшифрованный шифром Виженера (сложная замена):\n{decrypted_text_vigenere}\n"
    )
    print(
        f"Совпадает ли расшифрованный текст с обработанным? {decrypted_text_vigenere == processed_text}"
    )

    print_per_symbol(decrypted_text_vigenere, encrypted_text_vigenere, vigenere_key)


if __name__ == "__main__":
    punctuation: LiteralString = (
        r",|\.|\-|:;|\?|\!|\"|\'|\(|\)|\[|\]|{|}|\*|&|\^|%|\$|@|~|`|<|>|/|\\|_|=|\+|№"
    )
    initial_text: str = open("./in.txt", "r", encoding="utf8").read()
    print(f"Оригинальный текст:\n{initial_text}\n")

    processed_text: str = initial_text.lower()
    processed_text = re.sub(punctuation, "", processed_text)
    processed_text = re.sub(r"\s+", " ", processed_text).strip()

    print(f"Предварительно обработанный текст:\n{processed_text}\n")

    test_simple()
    test_vigenere()
