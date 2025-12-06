import time
from typing import Any, List
import struct


class LCG:
    """
    Линейный конгруэнтный генератор (LCG) псевдослучайных чисел
    Y(n+1) = (a * Xn + b) mod m, где m = 2^31-1
    """

    Y: int
    m: int = 2**31 - 1

    def __init__(
        self,
        a: int = 1664525,
        b: int = 1013904223,
    ) -> None:
        self.seed: int = int(time.time() * 1000000) % self.m  # Текущее значение
        self.Y: int = self.seed
        self.a: int = a
        self.b: int = b

    def next_int(self) -> int:
        self.Y = (self.a * self.Y + self.b) % self.m
        return self.Y

    def generate_gamma_bytes(self, count: int) -> List[int]:
        gamma_bytes: List[int] = []
        numbers_needed: int = (count + 3) // 4

        for _ in range(numbers_needed):
            rand_num: int = self.next_int()
            bytes_list: List[int] = list(struct.pack("<I", rand_num))
            for byte in bytes_list:
                if len(gamma_bytes) < count:
                    gamma_bytes.append(byte)
                else:
                    break
        return gamma_bytes

    def reset(self, seed=None) -> None:
        # Сброс генератора
        if seed is not None:
            self.Y = seed
        else:
            self.Y = int(time.time() * 1000000) % self.m


class StreamCipher:
    """
    Потоковый шифр, использующий LCG для генерации гаммы
    """

    def __init__(self, lcg_params: dict | None = None) -> None:
        if lcg_params is None:
            lcg_params = {
                "a": 1664525,
                "b": 1013904223,
            }

        self.lcg = LCG(a=lcg_params["a"], b=lcg_params["b"])
        self.seed: int = self.lcg.seed  # Сохраняем начальное значение

    def text_to_bytes(self, text: str) -> List[int]:
        return list(text.encode("utf-8"))

    def bytes_to_text(self, bytes_list: List[int]) -> str:
        return bytes(bytes_list).decode("utf-8")

    def encrypt(self, plaintext: str) -> List[int]:
        # Передаем сохраненный seed для сброса
        self.lcg.reset(self.seed)

        plaintext_bytes: List[int] = self.text_to_bytes(plaintext)
        length: int = len(plaintext_bytes)

        gamma: List[int] = self.lcg.generate_gamma_bytes(length)

        ciphertext_bytes: List[int] = []
        for i in range(length):
            encrypted_byte: int = plaintext_bytes[i] ^ gamma[i]
            ciphertext_bytes.append(encrypted_byte)

        return ciphertext_bytes

    def decrypt(self, ciphertext_bytes: List[int]) -> str:
        # Передаем тот же самый seed
        self.lcg.reset(self.seed)

        length: int = len(ciphertext_bytes)
        gamma: List[int] = self.lcg.generate_gamma_bytes(length)

        plaintext_bytes: List[int] = []
        for i in range(length):
            decrypted_byte: int = ciphertext_bytes[i] ^ gamma[i]
            plaintext_bytes.append(decrypted_byte)

        return self.bytes_to_text(plaintext_bytes)


def main() -> None:
    f = open("output.txt", "w", encoding="utf8")
    print("ОБРАБОТКА ГАММИРОВАНИЕМ С LCG:")

    with open("input.txt", "r", encoding="utf8") as file:
        plaintext: str = file.read()

    print("ПАРАМЕТРЫ ГЕНЕРАТОРА ПСЕВДОСЛУЧАЙНЫХ ЧИСЕЛ: ")
    print("Если хотите, чтобы параметр имел стандартное значение, введите -1")

    # Ввод параметров
    try:
        val: str = input("Введите параметр a (множитель): ")
        a: int = 1664525 if val == "-1" or val == "" else int(val)
    except:
        a = 1664525

    try:
        val = input("Введите параметр b (приращение): ")
        b: int = 1013904223 if val == "-1" or val == "" else int(val)
    except:
        b = 1013904223

    lcg_params: dict[str, int] = {"a": a, "b": b}
    # Инициализация шифра
    cipher = StreamCipher(lcg_params)

    real_seed: int = cipher.seed

    f.write(f"\nИсходный текст: {plaintext}\n")
    f.write(f"\nДлина текста: {len(plaintext)} символов\n")
    f.write(
        f"\nПараметры LCG: a={lcg_params['a']}, b={lcg_params['b']}, m={lcg_params['m']}, seed={real_seed}\n"
    )

    # Шифрование
    f.write("\n\nПРОЦЕСС ШИФРОВАНИЯ:\n\n")
    ciphertext_bytes: List[int] = cipher.encrypt(plaintext)

    # Генерируем гамму для отображения
    # Сбрасываем с конкретным seed
    cipher.lcg.reset(real_seed)
    gamma: List[int] = cipher.lcg.generate_gamma_bytes(len(plaintext.encode("utf-8")))

    plaintext_bytes: List[int] = list(plaintext.encode("utf-8"))

    f.write(f"\nТекст в байтах (UTF-8): {plaintext_bytes}...\n")
    f.write(f"\nГамма шифра: {gamma}...\n")
    f.write(f"\nЗашифрованный текст в байтах: {ciphertext_bytes}...\n")

    # Дешифрование
    f.write("\n\nПРОЦЕСС ДЕШИФРОВАНИЯ:\n\n")
    try:
        decrypted_text: str = cipher.decrypt(ciphertext_bytes)
        f.write(f"\nРасшифрованный текст: {decrypted_text}\n")

        f.write("\n\nРЕЗУЛЬТАТ:\n\n")
        match: bool = plaintext == decrypted_text
        f.write(
            f"\nИсходный текст совпадает с расшифрованным: {'Да' if match else 'Нет'}\n"
        )
        print(f"Результаты записаны в output.txt")
        f.write(f"\nТексты совпадают: {'Да' if match else 'Нет'}")

    except UnicodeDecodeError as e:
        print(f"ОШИБКА ДЕКОДИРОВАНИЯ: {e}")
        f.write(f"ОШИБКА: Не удалось декодировать текст. Гамма рассинхронизирована.\n")

    f.close()


if __name__ == "__main__":
    main()
