package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"sort"
	"strings"
	"unicode"
)

// Частоты букв русского языка
var russianFrequencies = map[rune]float64{
	'о': 10.97, 'е': 8.45, 'а': 8.01, 'и': 7.35, 'н': 6.70,
	'т': 6.26, 'с': 5.47, 'р': 4.73, 'в': 4.54, 'л': 4.40,
	'к': 3.49, 'м': 3.21, 'д': 2.98, 'п': 2.81, 'у': 2.62,
	'я': 2.01, 'ы': 1.90, 'ь': 1.74, 'г': 1.70, 'з': 1.65,
	'б': 1.59, 'ч': 1.44, 'й': 1.21, 'х': 0.97, 'ж': 0.94,
	'ш': 0.73, 'ю': 0.64, 'ц': 0.48, 'щ': 0.36, 'э': 0.32,
	'ф': 0.26, 'ъ': 0.04, 'ё': 0.04,
}

type charFreq struct {
	char rune
	freq float64
}

type substitution struct {
	from rune
	to   rune
}

func main() {
	inputFile := "input.txt"
	cipherFile := "ciphertext.txt"
	outputFile := "decrypted.txt"

	// 1. Читаем открытый текст
	plaintext, err := readFile(inputFile)
	if err != nil {
		fmt.Printf("Ошибка чтения %s: %v\n", inputFile, err)
		os.Exit(1)
	}

	// 2. Генерируем случайную замену и шифруем
	encryptionMap, _ := generateRandomSubstitution()
	ciphertext := encrypt(plaintext, encryptionMap)

	// 3. Сохраняем зашифрованный текст
	err = writeFile(cipherFile, ciphertext)
	if err != nil {
		fmt.Printf("Ошибка записи %s: %v\n", cipherFile, err)
		os.Exit(1)
	}

	// 4. Расшифровываем частотным анализом
	analysis := analyzeCiphertext(ciphertext)
	guessedSubstitutions := createSubstitutions(analysis)
	decrypted := decrypt(ciphertext, guessedSubstitutions)

	// 5. Записываем полный отчёт
	err = writeResults(outputFile, plaintext, ciphertext, analysis, guessedSubstitutions, encryptionMap, decrypted)
	if err != nil {
		fmt.Printf("Ошибка записи %s: %v\n", outputFile, err)
		os.Exit(1)
	}

	fmt.Printf("Готово!\n")
	fmt.Printf("  Зашифровано → %s\n", cipherFile)
	fmt.Printf("  Анализ → %s\n", outputFile)
}

// Чтение файла
func readFile(filename string) (string, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// Запись файла
func writeFile(filename, content string) error {
	return os.WriteFile(filename, []byte(content), 0644)
}

func generateRandomSubstitution() (map[rune]rune, map[rune]rune) {
	russianLetters := "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
	letters := []rune(russianLetters)
	shuffled := make([]rune, len(letters))
	copy(shuffled, letters)
	rand.Shuffle(len(shuffled), func(i, j int) {
		shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
	})

	enc := make(map[rune]rune)
	dec := make(map[rune]rune)
	for i, ch := range letters {
		enc[ch] = shuffled[i]
		dec[shuffled[i]] = ch
	}
	return enc, dec
}

// Шифрование
func encrypt(text string, sub map[rune]rune) string {
	var b strings.Builder
	for _, ch := range text {
		lower := unicode.ToLower(ch)
		if newCh, ok := sub[lower]; ok {
			if unicode.IsUpper(ch) {
				b.WriteRune(unicode.ToUpper(newCh))
			} else {
				b.WriteRune(newCh)
			}
		} else {
			b.WriteRune(ch)
		}
	}
	return b.String()
}

// Анализ частот
func analyzeCiphertext(text string) []charFreq {
	text = strings.ToLower(text)
	letterCount := make(map[rune]int)
	totalLetters := 0

	for _, ch := range text {
		if isRussianLetter(ch) {
			letterCount[ch]++
			totalLetters++
		}
	}

	frequencies := make([]charFreq, 0, len(letterCount))
	for char, count := range letterCount {
		freq := float64(count) / float64(totalLetters) * 100
		frequencies = append(frequencies, charFreq{char, freq})
	}

	sort.Slice(frequencies, func(i, j int) bool {
		return frequencies[i].freq > frequencies[j].freq
	})

	return frequencies
}

// Предполагаемые замены
func createSubstitutions(cipherFreqs []charFreq) map[rune]rune {
	russianSorted := make([]charFreq, 0, len(russianFrequencies))
	for char, freq := range russianFrequencies {
		russianSorted = append(russianSorted, charFreq{char, freq})
	}
	sort.Slice(russianSorted, func(i, j int) bool {
		return russianSorted[i].freq > russianSorted[j].freq
	})

	substitutions := make(map[rune]rune)
	for i := 0; i < len(cipherFreqs) && i < len(russianSorted); i++ {
		substitutions[cipherFreqs[i].char] = russianSorted[i].char
	}

	return substitutions
}

// Расшифровка
func decrypt(ciphertext string, substitutions map[rune]rune) string {
	var result strings.Builder
	for _, ch := range ciphertext {
		lowerCh := unicode.ToLower(ch)
		if sub, ok := substitutions[lowerCh]; ok {
			if unicode.IsUpper(ch) {
				result.WriteRune(unicode.ToUpper(sub))
			} else {
				result.WriteRune(sub)
			}
		} else {
			result.WriteRune(ch)
		}
	}
	return result.String()
}

// Запись отчёта
func writeResults(filename, plaintext, ciphertext string, analysis []charFreq,
	guessedSubs, realEncMap map[rune]rune, decrypted string) error {

	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	w := bufio.NewWriter(file)
	defer w.Flush()

	printHeader := func(title string) {
		w.WriteString("\n" + strings.Repeat("=", 72) + "\n")
		w.WriteString(title + "\n")
		w.WriteString(strings.Repeat("=", 72) + "\n")
	}

	// 1. Исходный текст
	printHeader("1. ИСХОДНЫЙ ОТКРЫТЫЙ ТЕКСТ")
	w.WriteString(plaintext + "\n")

	// 2. Зашифрованный
	printHeader("2. ЗАШИФРОВАННЫЙ ТЕКСТ")
	w.WriteString(ciphertext + "\n")

	// 3. Частотный анализ
	printHeader("3. ЧАСТОТНЫЙ АНАЛИЗ")
	w.WriteString(fmt.Sprintf("%-10s %-15s %-15s %-15s\n",
		"Шифр", "Частота (%)", "Ожидаемая", "Предположение"))
	w.WriteString(strings.Repeat("-", 72) + "\n")

	for _, cf := range analysis {
		guess := guessedSubs[cf.char]
		expected := fmt.Sprintf("%.2f%%", russianFrequencies[guess])
		w.WriteString(fmt.Sprintf("%-10c %-15.2f %-15s %-15c\n",
			cf.char, cf.freq, expected, guess))
	}

	// 4. Настоящая замена
	printHeader("4. НАСТОЯЩАЯ ЗАМЕНА (ОТКРЫТЫЙ → ШИФР)")
	sortedReal := make([]substitution, 0, len(realEncMap))
	for from, to := range realEncMap {
		sortedReal = append(sortedReal, substitution{from, to})
	}
	sort.Slice(sortedReal, func(i, j int) bool {
		return sortedReal[i].from < sortedReal[j].from
	})

	for i := 0; i < len(sortedReal); i += 8 {
		line := ""
		for j := i; j < i+8 && j < len(sortedReal); j++ {
			line += fmt.Sprintf("%c→%c  ", sortedReal[j].from, sortedReal[j].to)
		}
		w.WriteString(line + "\n")
	}

	// 5. Предполагаемая замена
	printHeader("5. ПРЕДПОЛАГАЕМАЯ ЗАМЕНА (ЧАСТОТНЫЙ АНАЛИЗ)")
	sortedGuessed := make([]substitution, 0, len(guessedSubs))
	for from, to := range guessedSubs {
		sortedGuessed = append(sortedGuessed, substitution{from, to})
	}
	sort.Slice(sortedGuessed, func(i, j int) bool {
		return sortedGuessed[i].from < sortedGuessed[j].from
	})

	for i := 0; i < len(sortedGuessed); i += 8 {
		line := ""
		for j := i; j < i+8 && j < len(sortedGuessed); j++ {
			line += fmt.Sprintf("%c→%c  ", sortedGuessed[j].from, sortedGuessed[j].to)
		}
		w.WriteString(line + "\n")
	}

	// 6. Расшифровка
	printHeader("6. РАСШИФРОВКА (ЧАСТОТНЫЙ АНАЛИЗ)")
	w.WriteString(decrypted + "\n")

	// 7. Статистика
	printHeader("7. СТАТИСТИКА")
	total := len([]rune(ciphertext))
	letters := 0
	for _, ch := range ciphertext {
		if isRussianLetter(unicode.ToLower(ch)) {
			letters++
		}
	}
	w.WriteString(fmt.Sprintf("Всего символов: %d\n", total))
	w.WriteString(fmt.Sprintf("Русских букв: %d\n", letters))
	w.WriteString(fmt.Sprintf("Уникальных в шифре: %d\n", len(analysis)))

	return nil
}

func isRussianLetter(ch rune) bool {
	return (ch >= 'а' && ch <= 'я') || ch == 'ё'
}
