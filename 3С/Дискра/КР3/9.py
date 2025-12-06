import time
import sys
from typing import List, Tuple


class LCGGenerator:
    def __init__(self, seed: int):
        self.state = seed
        self.a = 1103515245
        self.c = 12345
        self.m = 1 << 31

    def next_byte(self) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state % 256


class XorShiftStarPRNG:
    def __init__(self, seed: int = 0):
        if seed == 0:
            seed = int(time.time_ns())
        if seed == 0:
            seed = 1
        self.state = seed

    def next_uint64(self) -> int:
        x = self.state
        x ^= x >> 12
        x ^= x << 25
        x ^= x >> 27
        self.state = x
        return (x * 2685821657736338717) & 0xFFFFFFFFFFFFFFFF


def generate_custom_gamma(seed: int, length: int) -> List[int]:
    gen = XorShiftStarPRNG(seed)
    gamma = []
    i = 0
    while i < length:
        r = gen.next_uint64()
        for _ in range(8):
            if i >= length:
                break
            gamma.append(r & 0xFF)
            r >>= 8
            i += 1
    return gamma


def stream_encrypt(plaintext: str, gamma: List[int]) -> List[int]:
    data = [b for b in plaintext.encode("utf-8")]
    encrypted = []
    for i in range(len(data)):
        encrypted.append(data[i] ^ gamma[i % len(gamma)])
    return encrypted


def stream_decrypt(ciphertext: List[int], gamma: List[int]) -> str:
    decrypted = []
    for i in range(len(ciphertext)):
        decrypted.append(ciphertext[i] ^ gamma[i % len(gamma)])
    return bytes(decrypted).decode("utf-8", errors="replace")


def demonstrate_two_time_pad(c1: List[int], c2: List[int]) -> List[int]:
    length = min(len(c1), len(c2))
    return [c1[i] ^ c2[i] for i in range(length)]


def _check_mr_auxiliary(a: int, n: int, d: int, s: int) -> bool:
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    if n < 9:
        return True  # 5, 7

    if n < 4759123141:
        # Детерминированный Миллер-Рабин для n < 4,759,123,141
        bases = [2, 7, 61]
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for a in bases:
            if a % n == 0:
                continue
            if not _check_mr_auxiliary(a, n, d, s):
                return False
        return True

    # Для больших n (>=4_759_123_141) — пробное деление до sqrt(n)
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


# =========================================================================
# ПРИМИТИВ 3: САМОПИСНОЕ МОДУЛЬНОЕ ВОЗВЕДЕНИЕ В СТЕПЕНЬ
# =========================================================================


def modular_exponentiation(base: int, exponent: int, modulus: int) -> int:
    if modulus == 1:
        return 0
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        exponent >>= 1
        base = (base * base) % modulus
    return result


# =========================================================================
# УТИЛИТЫ
# =========================================================================


def print_bytes(data: List[int], n: int = 10) -> str:
    if len(data) <= n:
        return str(data)
    return str(data[:n]) + "..."


def to_hex(data: List[int]) -> str:
    return "".join(f"{b:02x}" for b in data)


# =========================================================================
# MAIN
# =========================================================================


def main():
    print("=" * 70)
    print("ЗАДАНИЕ 1: ПОТОЧНЫЙ ШИФР И САМОПИСНЫЕ КРИПТОГРАФИЧЕСКИЕ ПРИМИТИВЫ")
    print("=" * 70)

    # =========================================================================
    # А. ДЕМОНСТРАЦИЯ УЧЕБНОГО ШИФРА (LCG с повторением гаммы)
    # =========================================================================
    print("\n## 📚 A. Демонстрация LCG-Поточного Шифра (Уязвимо)")
    print("   Используется слабый LCG-генератор и повторение гаммы.")

    plaintext_lcg = "This is a secret message encrypted with a repeating LCG key."
    seed_lcg = 12345
    gen_lcg = LCGGenerator(seed_lcg)
    gamma_lcg = [gen_lcg.next_byte() for _ in range(len(plaintext_lcg))]

    print(f"\n1. Открытый текст: '{plaintext_lcg}' (Длина: {len(plaintext_lcg)})")
    print(
        f"2. Гамма (LCG): Ключ {seed_lcg}. Первые байты: {print_bytes(gamma_lcg, 10)}"
    )

    ciphertext_lcg = stream_encrypt(plaintext_lcg, gamma_lcg)
    print(f"3. Шифротекст (hex): {to_hex(ciphertext_lcg[:30])}...")

    decrypted_lcg = stream_decrypt(ciphertext_lcg, gamma_lcg)
    print(f"4. Дешифрованный текст: '{decrypted_lcg}'")

    if plaintext_lcg == decrypted_lcg:
        print("   ✓ LCG-шифрование/дешифрование успешно.")
    else:
        print("   ✗ Ошибка LCG-шифрования/дешифрования.")

    # =========================================================================
    # Б. ДЕМОНСТРАЦИЯ ONE-TIME PAD (OTP)
    # =========================================================================
    print("\n" + "-" * 70)
    print("## 🔒 Б. Демонстрация One-Time Pad (Самописный PRNG)")
    print("   Используется самописный Xorshift* PRNG.")

    plaintext_otp = "THE OTP IS THE ONLY PROVEN PERFECTLY SECURE CIPHER."
    print(f"\n1. Открытый текст: '{plaintext_otp}'")

    seed_otp = int(time.time_ns())
    gamma_otp = generate_custom_gamma(seed_otp, len(plaintext_otp))

    print(
        f"2. Гамма (Xorshift*): Длина {len(gamma_otp)}. Первые байты: {print_bytes(gamma_otp, 10)}"
    )

    ciphertext_otp = stream_encrypt(plaintext_otp, gamma_otp)
    print(f"3. Шифротекст (hex): {to_hex(ciphertext_otp[:30])}...")

    decrypted_otp = stream_decrypt(ciphertext_otp, gamma_otp)
    print(f"4. Дешифрованный текст: '{decrypted_otp}'")
    if plaintext_otp == decrypted_otp:
        print("   ✓ OTP-шифрование/дешифрование успешно.")

    # =========================================================================
    # В. КРИПТОАНАЛИЗ: АТАКА TWO-TIME PAD
    # =========================================================================
    print("\n" + "-" * 70)
    print("## ⚠️ В. Криптоанализ: Two-Time Pad (Повторное использование гаммы)")

    text1 = "ATTACK AT DAWN AND SECURE THE NORTH BRIDGE."
    text2 = "DEFEND THE CITY WALLS FROM THE WESTERN GATE."

    key_for_attack = generate_custom_gamma(54321, len(text1))
    c1 = stream_encrypt(text1, key_for_attack)
    c2 = stream_encrypt(text2, key_for_attack)

    p1_xor_p2 = demonstrate_two_time_pad(c1, c2)
    result_str = "".join(chr(b) if 32 <= b <= 126 else "?" for b in p1_xor_p2)

    print(f"\n3. Результат атаки (P1 XOR P2): '{result_str}'")
    print("   🔓 Вывод: Это доказывает, что **гамму нельзя использовать повторно**.")

    # =========================================================================
    # Г. ДЕМОНСТРАЦИЯ САМОПИСНЫХ ПРИМИТИВОВ
    # =========================================================================
    print("\n" + "-" * 70)
    print("## ⚙️ Г. Демонстрация Самописных Криптографических Примитивов")

    # 1. Модульное возведение в степень
    base = 7
    exponent = 13
    modulus = 11
    result_mod_exp = modular_exponentiation(base, exponent, modulus)
    expected = pow(base, exponent, modulus)  # built-in для проверки
    print(f"\n1. Самописное Модульное Возведение в Степень (a^b mod m)")
    print(
        f"   {base}^{exponent} mod {modulus} = {result_mod_exp} (Ожидаемый: {expected})"
    )
    if result_mod_exp == expected:
        print("   ✓ Корректно.")
    else:
        print("   ✗ Ошибка.")

    # 2. Проверка на простоту
    prime_candidate = 349
    composite_candidate = 343  # 7^3

    is_prime1 = is_probable_prime(prime_candidate)
    is_prime2 = is_probable_prime(composite_candidate)

    print(f"\n2. Самописная Проверка на Простоту (Упрощенный Миллер-Рабин)")
    print(f"   Проверка {prime_candidate}: Простое? {is_prime1} (Ожидаемый: True)")
    print(f"   Проверка {composite_candidate}: Простое? {is_prime2} (Ожидаемый: False)")

    if is_prime1 and not is_prime2:
        print("   ✓ Корректно.")
    else:
        print("   ✗ Ошибка.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
