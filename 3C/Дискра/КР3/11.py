import time
import random
from typing import Tuple, Optional

# ========================
# 1. Самописный PRNG (XorShift*)
# ========================


class XorShiftStarPRNG:
    def __init__(self, seed: Optional[int] = None):
        if seed is None:
            seed = int(time.time() * 1e9) % (2**64)
        if seed == 0:
            seed = 1
        self.state = seed & ((1 << 64) - 1)

    def next(self) -> int:
        x = self.state
        x ^= x >> 12
        x ^= x << 25
        x ^= x >> 27
        self.state = x & ((1 << 64) - 1)
        return (x * 2685821657736338717) & ((1 << 64) - 1)

    def read_bigint(self, bits: int) -> int:
        num_bytes = (bits + 7) // 8
        result = 0
        for _ in range(num_bytes):
            byte_val = self.next() & 0xFF
            result = (result << 8) | byte_val
        # Установить старший бит, чтобы гарантировать нужную длину
        if bits > 0:
            result |= 1 << (bits - 1)
        return result


# ========================
# 2. Самописный тест Миллера–Рабина
# ========================


def miller_rabin_test(n: int, d: int, s: int, a: int) -> bool:
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
        if x == 1:
            return False
    return False


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Разложить n-1 = 2^s * d
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # Детерминированные основания для n < 3.4e14
    bases = [2, 3, 5, 7, 11]
    for a in bases:
        if a >= n:
            continue
        if not miller_rabin_test(n, d, s, a):
            return False
    return True


def generate_probable_prime(prng: XorShiftStarPRNG, bits: int) -> int:
    while True:
        candidate = prng.read_bigint(bits)
        candidate |= 1  # сделать нечётным
        if is_probable_prime(candidate):
            return candidate


# ========================
# 3. Расширенный алгоритм Евклида и модульное обратное
# ========================


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, m: int) -> Optional[int]:
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m


# ========================
# 4. Самописное модульное возведение в степень
# ========================


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


# ========================
# 5. RSA структуры и функции
# ========================


class RSAKeypair:
    def __init__(self, n: int, e: int, d: int):
        self.n = n
        self.e = e
        self.d = d


def generate_primes(bits: int) -> Tuple[int, int]:
    prng = XorShiftStarPRNG()
    p = generate_probable_prime(prng, bits)
    q = generate_probable_prime(prng, bits)
    return p, q


def generate_keys(bits: int) -> RSAKeypair:
    p, q = generate_primes(bits)
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    d = mod_inverse(e, phi_n)
    if d is None:
        raise ValueError(
            "Failed to compute modular inverse — e and φ(n) are not coprime"
        )
    return RSAKeypair(n, e, d)


def encrypt(plaintext: bytes, e: int, n: int) -> int:
    m = int.from_bytes(plaintext, "big")
    if m >= n:
        raise ValueError("Message too long for current key size (m >= n)")
    return modular_exponentiation(m, e, n)


def decrypt(ciphertext: int, d: int, n: int) -> bytes:
    m = modular_exponentiation(ciphertext, d, n)
    # Определяем количество байт
    byte_length = (m.bit_length() + 7) // 8
    return m.to_bytes(byte_length, "big")


# ========================
# 6. Демонстрация
# ========================


def main():
    KEY_BITS = 512  # для быстрой демонстрации
    print("--- Генерация ключей RSA (самописные примитивы) ---")

    keypair = generate_keys(KEY_BITS)

    print(f"Размер ключа (N): {keypair.n.bit_length()} бит")
    print(f"Модуль N (n = p*q):\t\t {keypair.n:x}")
    print(f"Открытая экспонента E:\t {keypair.e:x}")
    d_hex = f"{keypair.d:x}"
    print(f"Закрытая экспонента D:\t {d_hex[:40]}...")
    print("-" * 70)

    plain_text = "GoLang Self-Implemented RSA Demo Message"
    message_bytes = plain_text.encode("utf-8")
    print(f"Исходное сообщение:\t\t {plain_text}")
    print(f"Длина сообщения (байты):\t {len(message_bytes)}")
    print("-" * 70)

    print("--- Шифрование (M^E mod N, самописное возведение в степень) ---")
    ciphertext = encrypt(message_bytes, keypair.e, keypair.n)
    print(f"Зашифрованный текст (C):\t {ciphertext:x}...")
    print("-" * 70)

    print("--- Расшифрование (C^D mod N, самописное возведение в степень) ---")
    decrypted_bytes = decrypt(ciphertext, keypair.d, keypair.n)
    decrypted_text = decrypted_bytes.decode("utf-8")
    print(f"Расшифрованное сообщение:\t {decrypted_text}")
    print("-" * 70)

    if plain_text == decrypted_text:
        print(
            "Проверка: Шифрование и расшифрование прошли успешно с самописными примитивами!"
        )
    else:
        print("Ошибка: Расшифрованное сообщение не соответствует исходному!")
    print("=" * 70)


if __name__ == "__main__":
    main()
