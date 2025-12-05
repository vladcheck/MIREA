from typing import Any
from LCG import LCG


class StreamCipher:
    """
    Потоковый шифр
    """

    def __init__(self, seed: Any = None, lcg_params: Any = None) -> None:
        if lcg_params is None:
            # Параметры по умолчанию для максимального периода
            lcg_params = {
                "a": 1664525,  # множитель
                "c": 1013904223,  # приращение (нечетное)
                "m": 2**32,  # модуль
            }

        self.lcg = LCG(
            seed=seed, a=lcg_params["a"], c=lcg_params["c"], m=lcg_params["m"]
        )
        self.seed: int = seed  # Сохраняем начальное значение

    def generate_gamma(self, length) -> list[int]:
        """
        Генерация "гаммы" - псевдослучайной последовательности БАЙТОВ
        """
        gamma: list[int] = []
        for _ in range(length):
            random_byte: int = self.lcg.next_byte()
            gamma.append(random_byte)
        return gamma

    def text_to_bytes(self, text: str) -> list[int]:
        """
        Возвращает текст в виде набора байтов
        """
        return [ord(c) for c in text]

    def bytes_to_text(self, bytes_list) -> str:
        return "".join([chr(c) for c in bytes_list])

    def encrypt(self, plaintext) -> tuple[list[int], list[int]]:
        """
        Побитовая шифровка текста
        Работает посредством XOR соответствующего байта и члена гаммы
        """
        self.lcg.reset()
        plaintext_bytes: list[int] = self.text_to_bytes(plaintext)
        gamma: list[int] = self.generate_gamma(len(plaintext_bytes))

        # Шифрование: сложение по модулю 2 (XOR)
        ciphertext_bytes: list[int] = []
        for i in range(len(plaintext_bytes)):
            encrypted_byte: int = plaintext_bytes[i] ^ gamma[i]
            ciphertext_bytes.append(encrypted_byte)

        return ciphertext_bytes, gamma

    def decrypt(self, ciphertext_bytes) -> tuple[str, list[int]]:
        """
        Побитовая расшифровка текста
        Работает посредством XOR соответствующего байта и члена гаммы
        """
        self.lcg.reset()
        gamma: list[int] = self.generate_gamma(len(ciphertext_bytes))

        # Дешифрование: сложение по модулю 2 (XOR)
        plaintext_bytes: list[int] = []
        for i in range(len(ciphertext_bytes)):
            decrypted_byte: int = ciphertext_bytes[i] ^ gamma[i]
            plaintext_bytes.append(decrypted_byte)

        plaintext: str = self.bytes_to_text(plaintext_bytes)
        return plaintext, gamma
