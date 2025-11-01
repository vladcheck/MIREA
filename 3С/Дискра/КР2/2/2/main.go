package main

import (
	"fmt"
	"math/rand"
	"os"
)

func main() {
	// Читаем бинарный файл
	filePath := "input.bin"
	fileData, err := os.ReadFile(filePath)
	if err != nil {
		fmt.Printf("Ошибка при чтении файла: %v\n", err)
		os.Exit(1)
	}

	if len(fileData) == 0 {
		fmt.Println("Файл пуст")
		os.Exit(1)
	}

	// Преобразуем байты в бинарный срез
	infoBits := bytesToBinary(fileData)
	fmt.Printf("Прочитано %d бит из файла\n", len(infoBits))

	// Определяем m (количество проверочных битов) на основе размера данных
	k := len(infoBits)
	m := calculateM(k)
	fmt.Printf("Выбрано m=%d для кодирования %d информационных битов\n", m, k)

	// Паддируем информационные биты нулями до нужного размера
	n := (1 << uint(m)) - 1
	maxK := n - m
	if k < maxK {
		padding := make([]int, maxK-k)
		infoBits = append(infoBits, padding...)
		fmt.Printf("Добавлено %d нулевых битов для паддирования\n", maxK-k)
	}

	table := generateHammingTable(m)
	encoded := hammingEncode(infoBits, table)

	// Вносим ошибку
	errorPos := rand.Intn(len(encoded))
	encodedWithError := make([]int, len(encoded))
	copy(encodedWithError, encoded)
	encodedWithError[errorPos] = 1 - encodedWithError[errorPos]

	// Находим синдром и исправляем ошибку
	syndrome := findSyndrome(encodedWithError, table)
	errorPosition := findErrorPosition(syndrome, table)
	if errorPosition != -1 {
		encodedWithError[errorPosition] = 1 - encodedWithError[errorPosition]
	}

	// Извлекаем исправленную информационную последовательность
	recoveredBits := extractInfoBits(encodedWithError, m, k)

	// Записываем результаты в файл
	file, err := os.Create("hamming_result.txt")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	writeLine := func(format string, a ...any) {
		fmt.Fprintf(file, format+"\n", a...)
	}

	writeLine("=== РЕЗУЛЬТАТЫ КОДИРОВАНИЯ ХЕММИНГА ===")
	writeLine("Исходный файл: %s", filePath)
	writeLine("Количество информационных битов: %d", len(infoBits))
	writeLine("Количество проверочных битов (m): %d", m)
	writeLine("Всего битов в кодовом слове: %d", len(encoded))
	writeLine("")

	writeLine("Исходная информационная последовательность: %v", infoBits)
	writeLine("")

	writeLine("Таблица Хемминга (%dx%d):", len(table), len(table[0]))
	for i := 0; i < len(table); i++ {
		writeLine("P%d: %v", i+1, table[i])
	}
	writeLine("")

	writeLine("Закодированная комбинация: %v", encoded)
	writeLine("Внесена ошибка в позицию %d", errorPos+1)
	writeLine("Кодовое слово с ошибкой: %v", encodedWithError)
	writeLine("")

	writeLine("Синдром: %v", syndrome)
	if errorPosition != -1 {
		writeLine("Ошибка найдена в позиции %d", errorPosition+1)
		writeLine("Исправленное кодовое слово: %v", encodedWithError)
	} else {
		writeLine("Ошибок не обнаружено")
	}
	writeLine("")

	writeLine("Извлеченная информационная последовательность: %v", recoveredBits)
	if compareVectors(infoBits, recoveredBits) {
		writeLine("✓ Результат совпадает с исходной последовательностью")
	} else {
		writeLine("✗ Результат НЕ совпадает с исходной последовательностью")
	}

	// Сохраняем исправленные данные
	recoveredBytes := binaryToBytes(recoveredBits)
	err = os.WriteFile("output.bin", recoveredBytes, 0644)
	if err != nil {
		fmt.Printf("Ошибка при записи выходного файла: %v\n", err)
	}

	fmt.Println("Результат записан в файл hamming_result.txt")
	fmt.Println("Исправленные данные записаны в файл output.bin")
}

// Преобразует байты в бинарный срез
func bytesToBinary(data []byte) []int {
	binary := make([]int, len(data)*8)
	for i, b := range data {
		for j := 0; j < 8; j++ {
			if (b & (1 << (7 - j))) != 0 {
				binary[i*8+j] = 1
			}
		}
	}
	return binary
}

// Преобразует бинарный срез обратно в байты
func binaryToBytes(binary []int) []byte {
	// Паддируем до полного байта
	padding := (8 - len(binary)%8) % 8
	for i := 0; i < padding; i++ {
		binary = append(binary, 0)
	}

	data := make([]byte, len(binary)/8)
	for i := 0; i < len(data); i++ {
		var b byte
		for j := 0; j < 8; j++ {
			if binary[i*8+j] == 1 {
				b |= (1 << (7 - j))
			}
		}
		data[i] = b
	}
	return data
}

// Вычисляет необходимое количество проверочных битов
func calculateM(k int) int {
	m := 1
	for {
		maxK := (1 << uint(m)) - 1 - m // 2^m - 1 - m
		if maxK >= k {
			return m
		}
		m++
	}
}

// Создает таблицу проверочных битов Хэмминга
func generateHammingTable(m int) [][]int {
	n := 1<<m - 1
	table := make([][]int, m)
	for i := 0; i < m; i++ {
		table[i] = make([]int, n)
		pattern := 1 << i
		for j := 0; j < n; j++ {
			if ((j + 1) & pattern) != 0 {
				table[i][j] = 1
			}
		}
	}
	return table
}

// Кодирует информационные биты кодом Хемминга
func hammingEncode(infoBits []int, table [][]int) []int {
	m := len(table)
	n := len(table[0])
	k := len(infoBits)

	if k != n-m {
		panic("Несоответствие размеров")
	}

	encoded := make([]int, n)
	infoIndex := 0
	for i := 0; i < n; i++ {
		if !isPowerOfTwo(i + 1) {
			encoded[i] = infoBits[infoIndex]
			infoIndex++
		}
	}

	for i := 0; i < m; i++ {
		parity := 0
		for j := 0; j < n; j++ {
			if table[i][j] == 1 {
				parity ^= encoded[j]
			}
		}
		pos := (1 << i) - 1
		if pos < n {
			encoded[pos] = parity
		}
	}
	return encoded
}

// Находит синдром
func findSyndrome(encoded []int, table [][]int) []int {
	m := len(table)
	syndrome := make([]int, m)
	for i := 0; i < m; i++ {
		parity := 0
		for j := 0; j < len(encoded); j++ {
			if table[i][j] == 1 {
				parity ^= encoded[j]
			}
		}
		syndrome[i] = parity
	}
	return syndrome
}

// Находит позицию ошибки по синдрому
func findErrorPosition(syndrome []int, table [][]int) int {
	if isZero(syndrome) {
		return -1
	}
	for j := 0; j < len(table[0]); j++ {
		match := true
		for i := 0; i < len(syndrome); i++ {
			if table[i][j] != syndrome[i] {
				match = false
				break
			}
		}
		if match {
			return j
		}
	}
	return -1
}

// Извлекает информационные биты из кодового слова
func extractInfoBits(encoded []int, m int, originalLength int) []int {
	var infoBits []int
	for i := 0; i < len(encoded); i++ {
		if !isPowerOfTwo(i + 1) {
			infoBits = append(infoBits, encoded[i])
		}
	}
	// Возвращаем только оригинальное количество битов (без паддирования)
	if len(infoBits) > originalLength {
		infoBits = infoBits[:originalLength]
	}
	return infoBits
}

// Проверяет, является ли число степенью двойки
func isPowerOfTwo(n int) bool {
	return n > 0 && (n&(n-1)) == 0
}

// Проверяет, является ли вектор нулевым
func isZero(vector []int) bool {
	for _, v := range vector {
		if v != 0 {
			return false
		}
	}
	return true
}

// Сравнивает два вектора
func compareVectors(v1, v2 []int) bool {
	if len(v1) != len(v2) {
		return false
	}
	for i := 0; i < len(v1); i++ {
		if v1[i] != v2[i] {
			return false
		}
	}
	return true
}
