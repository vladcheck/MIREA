import time
from typing import List


class LCG:
    """
    Линейный конгруэнтный генератор (LCG) псевдослучайных чисел
    X(n+1) = (a * Xn + c) mod m
    Генерирует последовательность заранее при инициализации
    """

    def __init__(
        self,
        seed: int | None = None,
        length: int = 1024,
        a: int = 1664525,
        c: int = 1013904223,
        m: int = 2**32 - 1,
    ) -> None:
        """
        Инициализация генератора и предвычисление последовательности

        Args:
            seed: Начальное значение (если None, используется текущее время)
            length: Длина генерируемой последовательности в байтах
            a, c, m: Параметры LCG
        """
        if seed is None:
            seed = int(time.time() * 1000000) % m

        self.seed: int = seed
        self.a: int = a
        self.c: int = c
        self.m: int = m
        self.length: int = length

        # Генерируем всю последовательность сразу
        self.sequence: List[int] = self._generate_sequence()
        self.index = 0  # Текущая позиция в последовательности

    def _generate_sequence(self) -> List[int]:
        """Генерирует последовательность байтов заданной длины"""
        X: int = self.seed
        bytes_sequence = []

        # Генерируем достаточно целых чисел, чтобы получить нужное количество байтов
        while len(bytes_sequence) < self.length:
            X = (self.a * X + self.c) % self.m
            # Извлекаем байты из каждого целого числа
            for i in range(4):  # 4 байта в 32-битном числе
                byte = (X >> (i * 8)) & 0xFF
                bytes_sequence.append(byte)
                if len(bytes_sequence) >= self.length:
                    break

        return bytes_sequence[: self.length]

    def next_byte(self) -> int:
        """Возвращает следующий байт из заранее сгенерированной последовательности"""
        if self.index >= self.length:
            # Если достигли конца последовательности, начинаем заново
            self.index = 0
        byte: int = self.sequence[self.index]
        self.index += 1
        return byte

    def get_bytes(self, count: int) -> bytes:
        """Возвращает указанное количество байтов из последовательности"""
        if self.index + count > self.length:
            # Если не хватает байтов, начинаем сначала
            self.index = 0

        result: List[int] = self.sequence[self.index : self.index + count]
        self.index += count
        if self.index >= self.length:
            self.index = 0

        return bytes(result)

    def reset(self) -> None:
        """
        Сбрасывает генератор, пересоздавая последовательность с исходным сидом
        """
        self.sequence = self._generate_sequence()
        self.index = 0
