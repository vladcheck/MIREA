import os

# Пытаемся импортировать необходимые модули из cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding


def run_cryptography_demo():
    """
    Демонстрирует основные возможности библиотеки cryptography.
    """

    print("=" * 70)
    print("ЗАДАНИЕ 4: ИСПОЛЬЗОВАНИЕ БИБЛИОТЕКИ CRYPTOGRAPHY")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("ЧАСТЬ 1: AES-256 ШИФРОВАНИЕ (CBC режим)")
    print("=" * 70)

    print("\n1. Подготовка:")

    # Генерация ключа и IV (Initialization Vector)
    key = os.urandom(32)  # 256-bit ключ для AES-256
    iv = os.urandom(16)  # 128-bit IV для AES

    print(f"   Алгоритм: AES-256")
    print(f"   Режим: CBC (Cipher Block Chaining) ")
    print(f"   Ключ (32 байта, hex): {key.hex()[:16]}...")
    print(f"   IV (16 байт, hex): {iv.hex()}")

    # Текст для шифрования
    plaintext_aes = (
        "This is a secret message encrypted with AES-256, a robust symmetric cipher!"
    )
    print(f"\n2. Открытый текст: '{plaintext_aes}'")

    # Padding - выравнивание по блокам (AES использует блоки по 128 бит = 16 байт)
    print(f"\n3. Padding (выравнивание по блокам PKCS7):")
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext_aes.encode()) + padder.finalize()
    print(f"   Исходная длина: {len(plaintext_aes.encode())} байт")
    print(f"   После padding: {len(padded_data)} байт")

    # Создание cipher объекта и шифрование
    print(f"\n4. Шифрование:")
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext_aes = encryptor.update(padded_data) + encryptor.finalize()

    print(f"   Зашифрованный текст (hex): {ciphertext_aes.hex()[:60]}...")

    # Дешифрование
    print(f"\n5. Дешифрование:")
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext_aes) + decryptor.finalize()

    # Удаление padding
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
    decrypted_aes = decrypted_data.decode()

    print(f"   Дешифрованный текст: '{decrypted_aes}'")

    # Проверка
    print(f"\n6. Проверка:")
    if plaintext_aes == decrypted_aes:
        print(f"   ✓ Успех! Тексты совпадают.")
    else:
        print(f"   ✗ Ошибка! Тексты не совпадают.")

    print("\n" + "=" * 70)
    print("ЧАСТЬ 2: FERNET (Симметричное шифрование высокого уровня)")
    print("=" * 70)

    print("\n1. Генерация ключа Fernet:")
    fernet_key = Fernet.generate_key()
    print(f"   Ключ: {fernet_key.decode()[:20]}...")

    # Создание объекта Fernet
    fernet = Fernet(fernet_key)

    # Текст для шифрования
    plaintext_fernet = "Fernet provides easy-to-use symmetric encryption with built-in integrity checks!"
    print(f"\n2. Открытый текст: '{plaintext_fernet}'")

    # Шифрование
    print(f"\n3. Шифрование:")
    encrypted_fernet = fernet.encrypt(plaintext_fernet.encode())
    print(f"   Зашифрованный текст: {encrypted_fernet.decode()[:60]}...")
    print(f"   (Fernet автоматически добавляет временную метку и MAC для целостности)")

    # Дешифрование
    print(f"\n4. Дешифрование:")
    decrypted_fernet = fernet.decrypt(encrypted_fernet).decode()
    print(f"   Дешифрованный текст: '{decrypted_fernet}'")

    # Проверка
    print(f"\n5. Проверка:")
    if plaintext_fernet == decrypted_fernet:
        print(f"   ✓ Успех! Тексты совпадают.")

    print("\n" + "=" * 70)
    print("ЧАСТЬ 3: АСИММЕТРИЧНОЕ RSA ШИФРОВАНИЕ")
    print("=" * 70)

    print("\n1. Генерация пары ключей RSA:")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,  # 2048 бит - стандартный размер
        backend=default_backend(),
    )
    public_key = private_key.public_key()

    print(f"   Размер ключа: {private_key.key_size} бит")

    # Текст для шифрования
    plaintext_rsa = b"Short secret key or message for RSA encryption."
    print(f"\n2. Открытый текст (байты): {plaintext_rsa}")

    # Шифрование открытым ключом (OAEP padding)
    print(f"\n3. Шифрование (public key):")
    ciphertext_rsa = public_key.encrypt(
        plaintext_rsa,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    print(f"   Зашифрованный текст (hex): {ciphertext_rsa.hex()[:60]}...")

    # Дешифрование закрытым ключом
    print(f"\n4. Дешифрование (private key):")
    decrypted_rsa = private_key.decrypt(
        ciphertext_rsa,
        rsa_padding.OAEP(
            mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    decrypted_rsa_text = decrypted_rsa.decode()
    print(f"   Дешифрованный текст: '{decrypted_rsa_text}'")

    # Проверка
    print(f"\n5. Проверка:")
    if plaintext_rsa.decode() == decrypted_rsa_text:
        print(f"   ✓ Успех! Тексты совпадают.")

    # ========================================================================
    # ЧАСТЬ 4: ХЕШИРОВАНИЕ (Однонаправленные функции)
    # ========================================================================

    print("\n" + "=" * 70)
    print("ЧАСТЬ 4: ХЕШИРОВАНИЕ И PBKDF2")
    print("=" * 70)

    text_to_hash = "Hash me please! The cryptography library is great."
    print(f"\n1. Текст для хеширования: '{text_to_hash}'")

    # SHA-256
    print(f"\n2. SHA-256:")
    digest_sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest_sha256.update(text_to_hash.encode())
    hash_sha256 = digest_sha256.finalize()
    print(f"   Хеш (hex): {hash_sha256.hex()}")
    print(f"   Длина: {len(hash_sha256)} байт (256 бит) ")

    # PBKDF2 (Генерация ключа из пароля)
    print(f"\n3. PBKDF2 (Password-Based Key Derivation Function):")

    password = b"my_secure_password_123"
    salt = os.urandom(16)  # Соль для усиления безопасности

    print(f"   Пароль: {password.decode()}")
    print(f"   Соль (hex): {salt.hex()}")
    print(f"   Итераций: 100000 (должно быть высоким!)")

    # Генерация ключа из пароля
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 байта = 256 бит
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )

    derived_key = kdf.derive(password)

    print(f"\n4. Сгенерированный ключ:")
    print(f"   Ключ (hex): {derived_key.hex()[:16]}...")
    print(f"   Длина: {len(derived_key)} байт")
    print(f"   Этот ключ безопасно использовать для AES шифрования!")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_cryptography_demo()
