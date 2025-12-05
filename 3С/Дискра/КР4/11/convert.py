def text_to_numbers(text, encoding_table) -> str:
    """Преобразование текста в числовую последовательность"""
    result: str = ""
    for char in text:
        if char in encoding_table:
            result += str(encoding_table[char])
        else:
            raise ValueError(f"Символ '{char}' не найден в таблице кодирования")
    return result


def number_to_text(numbers, decoding_table) -> str:
    """Преобразование числовой последовательности в текст"""
    result: str = ""
    num_str = str(numbers)
    i = 0

    while i < len(num_str):
        # Пробел кодируется как 99
        if num_str[i : i + 2] == "99":
            result += " "
            i += 2
        else:
            # Буквы кодируются двузначными числами
            if i + 2 <= len(num_str):
                code: str = num_str[i : i + 2]
                if code in decoding_table:
                    result += decoding_table[code]
                    i += 2
                else:
                    # Если не нашли двузначный код, пробуем однозначный
                    code = num_str[i]
                    if code in decoding_table:
                        result += decoding_table[code]
                        i += 1
                    else:
                        i += 1
            else:
                code = num_str[i]
                if code in decoding_table:
                    result += decoding_table[code]
                i += 1
    return result


def blocks_to_number(decrypted_blocks: list[int]) -> str:
    return "".join(map(str, decrypted_blocks))
