import time
from StreamCipher import StreamCipher

LCG_DEFAULT_PARAMS: dict[str, int] = {"a": 1103515245, "c": 12345, "m": 2**32}
BLOCK_SIZE = 4  # байты

if __name__ == "__main__":
    f = open("output.txt", "w", encoding="utf8")
    print("ОБРАБОТКА БЛОКАМИ С LCG:")
    plaintext: str = open("input.txt", encoding="utf8").read()

    print("ПАРАМЕНТРЫ ГЕНЕРАТОРА ПСЕВДОСЛУЧАЙНЫХ ЧИСЕЛ: ")
    print("Если хотите, чтобы параметр имел стандартное значение, введите -1")
    a = int(
        input(
            "Введите параметр a (лучше всего подходят числа с остатком 1 при делении на 4): "
        )
    )
    if a == -1:
        a: int = LCG_DEFAULT_PARAMS["a"]
    c = int(input("Введите параметр c (лучше всего подходят нечётные числа): "))
    if c == -1:
        c: int = LCG_DEFAULT_PARAMS["c"]
    m: int = LCG_DEFAULT_PARAMS["m"]

    # Используем другие параметры LCG для демонстрации
    lcg_params: dict[str, int] = {"a": a, "c": c, "m": m}
    seed = int(input("Введите семя: "))
    if seed == -1:
        seed: int = int(time.time() * 1000000) % m

    cipher = StreamCipher(seed=seed, lcg_params=lcg_params)

    f.write(f"\nИсходный текст: {plaintext}\n")
    f.write(f"Размер блока: {BLOCK_SIZE} символов\n")
    print(
        f"Параметры LCG: a={lcg_params['a']}, c={lcg_params['c']}, m={lcg_params['m']}\n"
    )

    # Шифрование блоками
    f.write("\n\nПРОЦЕСС ШИФРОВАНИЯ:\n\n")
    cipher.lcg.reset()
    encrypted_blocks: list[int] = []
    total_blocks: int = (len(plaintext) + BLOCK_SIZE - 1) // BLOCK_SIZE

    for block_num in range(total_blocks):
        start_idx: int = block_num * BLOCK_SIZE
        end_idx: int = start_idx + BLOCK_SIZE
        block_text: str = plaintext[start_idx:end_idx]

        f.write(f"Блок {block_num + 1}: '{block_text}'\n")

        # Преобразуем блок в байты
        block_bytes: list[int] = cipher.text_to_bytes(block_text)

        # Генерируем гамму для блока
        block_gamma: list[int] = cipher.generate_gamma(len(block_bytes))

        # Шифруем блок
        encrypted_block: list[int] = [
            block_bytes[i] ^ block_gamma[i] for i in range(len(block_bytes))
        ]
        encrypted_blocks.extend(encrypted_block)

        f.write(f"  Байты блока: {block_bytes}\n")
        f.write(f"  Гамма блока: {block_gamma}\n")
        f.write(f"  Зашифрованные байты: {encrypted_block}\n")

    f.write("\n\nШИФРОВАННЫЙ ТЕКСТ В БАЙТАХ:\n\n")
    for i in encrypted_blocks:
        f.write(str(i))
    f.write("\n")

    # Дешифрование блоками
    f.write("\n\nПРОЦЕСС ДЕШИФРОВАНИЯ:\n\n")
    cipher.lcg.reset()
    decrypted_text: str = ""

    for block_num in range(total_blocks):
        start_idx = block_num * BLOCK_SIZE
        end_idx = start_idx + BLOCK_SIZE

        # Берем зашифрованные байты блока
        block_bytes_count: int = min(BLOCK_SIZE, len(encrypted_blocks) - start_idx)
        block_cipher_bytes: list[int] = encrypted_blocks[
            start_idx : start_idx + block_bytes_count
        ]

        # Генерируем гамму для блока
        block_gamma = cipher.generate_gamma(len(block_cipher_bytes))

        # Дешифруем блок
        decrypted_block_bytes = [
            block_cipher_bytes[i] ^ block_gamma[i]
            for i in range(len(block_cipher_bytes))
        ]
        decrypted_block: str = cipher.bytes_to_text(decrypted_block_bytes)
        decrypted_text += decrypted_block

        f.write(f"Блок {block_num + 1}: '{decrypted_block}'\n")
        f.write(f"  Зашифрованные байты: {block_cipher_bytes}\n")
        f.write(f"  Гамма блока: {block_gamma}\n")
        f.write(f"  Расшифрованные байты: {decrypted_block_bytes}\n")

    f.write(decrypted_text)
    f.close()

    print(f"Зашифрованный текст записан в output.txt")
    print(f"Тексты совпадают: {"Да" if plaintext == decrypted_text else "Нет"}")
