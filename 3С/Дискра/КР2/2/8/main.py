import random
from freq import russian_frequencies

class CharFreq:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq

class Substitution:
    def __init__(self, frm, to):
        self.frm = frm
        self.to = to

def generate_random_substitution():
    russian_letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    letters_list = list(russian_letters)
    shuffled_list = letters_list[:]
    random.shuffle(shuffled_list)

    enc = {}
    dec = {}
    for i, ch in enumerate(letters_list):
        enc[ch] = shuffled_list[i]
        dec[shuffled_list[i]] = ch
    return enc, dec

def encrypt(text, sub):
    result = []
    for ch in text:
        lower_ch = ch.lower()
        if lower_ch in sub:
            new_ch = sub[lower_ch]
            if ch.isupper():
                result.append(new_ch.upper())
            else:
                result.append(new_ch)
        else:
            result.append(ch)
    return ''.join(result)

def analyze_ciphertext(text):
    text = text.lower()
    letter_count = {}
    total_letters = 0

    for ch in text:
        if is_russian_letter(ch):
            letter_count[ch] = letter_count.get(ch, 0) + 1
            total_letters += 1

    frequencies = []
    for char, count in letter_count.items():
        freq = (count / total_letters) * 100 if total_letters > 0 else 0
        frequencies.append(CharFreq(char, freq))

    frequencies.sort(key=lambda x: x.freq, reverse=True)
    return frequencies

def create_substitutions(cipher_freqs):
    russian_sorted = [CharFreq(char, freq) for char, freq in russian_frequencies.items()]
    russian_sorted.sort(key=lambda x: x.freq, reverse=True)

    substitutions = {}
    for i in range(min(len(cipher_freqs), len(russian_sorted))):
        substitutions[cipher_freqs[i].char] = russian_sorted[i].char

    return substitutions

def decrypt(ciphertext, substitutions):
    result = []
    for ch in ciphertext:
        lower_ch = ch.lower()
        if lower_ch in substitutions:
            sub_ch = substitutions[lower_ch]
            if ch.isupper():
                result.append(sub_ch.upper())
            else:
                result.append(sub_ch)
        else:
            result.append(ch)
    return ''.join(result)

def write_results(filename, plaintext, ciphertext, analysis, guessed_subs, real_enc_map, decrypted):
    with open(filename, 'w', encoding='utf-8') as f:
        def print_header(title):
            f.write("\n" + "="*72 + "\n")
            f.write(title + "\n")
            f.write("="*72 + "\n")

        print_header("1. Исходный текст")
        f.write(plaintext + "\n")

        print_header("2. Зашифрованный текст")
        f.write(ciphertext + "\n")

        print_header("3. Частотный анализ")
        f.write(f"{'Шифр':<10} {'Частота (%)':<15} {'Ожидаемая':<15} {'Предположение':<15}\n")
        f.write("-" * 72 + "\n")

        for cf in analysis:
            guess = guessed_subs.get(cf.char, '?')
            expected = f"{russian_frequencies.get(guess, 0.0):.2f}%"
            f.write(f"{cf.char:<10} {cf.freq:<15.2f} {expected:<15} {guess:<15}\n")

        print_header("4. Настоящая замена")
        sorted_real = [Substitution(frm, to) for frm, to in real_enc_map.items()]
        sorted_real.sort(key=lambda x: x.frm)

        line_parts = []
        for sr in sorted_real:
            line_parts.append(f"{sr.frm}->{sr.to}  ")
            if len(line_parts) == 8:
                f.write(''.join(line_parts) + "\n")
                line_parts = []
        if line_parts:
            f.write(''.join(line_parts) + "\n")

        print_header("5. Предполагаемая замена (частотный анализ)")
        sorted_guessed = [Substitution(frm, to) for frm, to in guessed_subs.items()]
        sorted_guessed.sort(key=lambda x: x.frm)

        line_parts = []
        for sg in sorted_guessed:
            line_parts.append(f"{sg.frm}->{sg.to}  ")
            if len(line_parts) == 8:
                f.write(''.join(line_parts) + "\n")
                line_parts = []
        if line_parts:
            f.write(''.join(line_parts) + "\n")

        print_header("6. Расшифровка (частотный анализ)")
        f.write(decrypted + "\n")

        print_header("7. Статистика")
        total = len(ciphertext)
        letters = sum(1 for ch in ciphertext if is_russian_letter(ch.lower()))
        unique_in_cipher = len(analysis)
        f.write(f"Всего символов: {total}\n")
        f.write(f"Русских букв: {letters}\n")
        f.write(f"Уникальных в шифре: {unique_in_cipher}\n")

def is_russian_letter(ch):
    return 'а' <= ch <= 'я' or ch == 'ё'

def main():
    input_file = "input.txt"
    cipher_file = "ciphertext.txt"
    decipher_file = "decyphered.txt"
    output_file = "results.txt"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            plaintext = f.read()
    except Exception as e:
        print(f"Ошибка чтения {input_file}: {e}")
        return

    encryption_map, decryption_map = generate_random_substitution()
    ciphertext = encrypt(plaintext, encryption_map)

    try:
        with open(cipher_file, 'w', encoding='utf-8') as f:
            f.write(ciphertext)
    except Exception as e:
        print(f"Ошибка записи {cipher_file}: {e}")
        return

    analysis = analyze_ciphertext(ciphertext)
    guessed_substitutions = create_substitutions(analysis)
    decrypted = decrypt(ciphertext, guessed_substitutions)

    try:
        with open(decipher_file, 'w', encoding='utf-8') as f:
            f.write(decrypted)
    except Exception as e:
        print(f"Ошибка записи {decipher_file}: {e}")
        return

    try:
        write_results(output_file, plaintext, ciphertext, analysis, guessed_substitutions, encryption_map, decrypted)
    except Exception as e:
        print(f"Ошибка записи {output_file}: {e}")
        return

    print("Готово!")
    print(f"  Зашифровано -> {cipher_file}")
    print(f"  Расшифровано -> {decipher_file}")
    print(f"  Анализ -> {output_file}")

if __name__ == "__main__":
    main()