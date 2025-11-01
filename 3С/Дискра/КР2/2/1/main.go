package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"math"
	"os"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

// хранит информацию о каждом символе/биграмме для анализа и кодирования.
type Symbol struct {
	Char  string  // Символ или биграмма
	Prob  float64 // Вероятность появления
	Code  string  // Двоичный код символа
	Count int     // Количество в тексте
}

type ByProb []Symbol

// реализуем интерфйес чтоб можно было сортировать массив наших данных с помощью внутренней функции
func (a ByProb) Len() int           { return len(a) }
func (a ByProb) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByProb) Less(i, j int) bool { return a[i].Prob > a[j].Prob }

func main() {
	filename := "text.txt"
	content, err := os.ReadFile(filename)
	if err != nil {
		log.Fatal(err)
	}
	text := string(content)

	// Одиночные символы
	alphabet := makeAlphabet(text)
	writeAlphabetToCSV(alphabet, "alphabet.csv")

	// считаем энтропию(среднее количество информации на символ)
	entropy := calculateEntropy(alphabet)
	//Длина равномерного кода(минимальное количество бит для кодирования всех символов)
	uniformLength := math.Ceil(math.Log2(float64(len(alphabet))))
	//вычисляем избыточность
	redundancy := uniformLength - entropy

	fmt.Printf("Энтропия: %.4f бит/символ\n", entropy)
	fmt.Printf("Длина равномерного кода: %.0f бит\n", uniformLength)
	fmt.Printf("Избыточность: %.4f бит\n", redundancy)

	shannonFanoCodes := generateShannonFanoCodes(alphabet)
	writeCodesToCSV(shannonFanoCodes, "shannon_fano_codes.csv")

	avgLength := calculateAverageCodeLength(alphabet, shannonFanoCodes)
	efficiency := entropy / avgLength

	fmt.Printf("Средняя длина кода: %.4f бит\n", avgLength)
	fmt.Printf("Эффективность сжатия: %.4f\n", efficiency)

	encoded := encodeText(text, shannonFanoCodes)
	saveToFile(encoded, "encoded.txt")

	decoded := decodeText(encoded, shannonFanoCodes)
	saveToFile(decoded, "decoded.txt")

	// Биграммы(по сути повторяем все те же действия что и выше только для биограм, биограма - 2 идущих подряд символа)
	bigramAlphabet := makeBigramAlphabet(text)
	bigramShannonFano := generateShannonFanoCodes(bigramAlphabet)
	writeCodesToCSV(bigramShannonFano, "bigram_shannon_fano_codes.csv")

	huffmanCodes := generateHuffmanCodes(alphabet)
	writeCodesToCSV(huffmanCodes, "huffman_codes.csv")

	bigramHuffman := generateHuffmanCodes(bigramAlphabet)
	writeCodesToCSV(bigramHuffman, "bigram_huffman_codes.csv")
}

// Алфавит одиночных символов
//
// # Подсчитывает количество каждого символа
//
// # Вычисляет вероятности появления
//
// Сортирует по убыванию вероятности
func makeAlphabet(text string) []Symbol {
	counts := make(map[string]int)
	total := 0

	for _, r := range text {
		char := string(r)
		counts[char]++
		total++
	}

	alphabet := make([]Symbol, 0, len(counts))
	for char, count := range counts {
		alphabet = append(alphabet, Symbol{
			Char:  char,
			Prob:  float64(count) / float64(total),
			Count: count,
		})
	}

	sort.Sort(ByProb(alphabet))
	return alphabet
}

// Алфавит биграмм
func makeBigramAlphabet(text string) []Symbol {
	runes := []rune(text)
	counts := make(map[string]int)
	total := 0

	for i := 0; i < len(runes)-1; i++ {
		bigram := string(runes[i : i+2])
		counts[bigram]++
		total++
	}

	alphabet := make([]Symbol, 0, len(counts))
	for bigram, count := range counts {
		alphabet = append(alphabet, Symbol{
			Char:  bigram,
			Prob:  float64(count) / float64(total),
			Count: count,
		})
	}

	sort.Sort(ByProb(alphabet))
	return alphabet
}

func writeAlphabetToCSV(alphabet []Symbol, filename string) {
	file, err := os.Create(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{"Символ", "Частота", "Вероятность"})
	for _, s := range alphabet {
		displayChar := escapeSpecialChars(s.Char)
		writer.Write([]string{
			displayChar,
			strconv.Itoa(s.Count),
			strconv.FormatFloat(s.Prob, 'f', 6, 64),
		})
	}
}

func writeCodesToCSV(codes map[string]string, filename string) {
	file, err := os.Create(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	writer.Write([]string{"Символ", "Код"})

	// Сортируем для вывода
	keys := make([]string, 0, len(codes))
	for char := range codes {
		keys = append(keys, char)
	}
	sort.Strings(keys)

	for _, char := range keys {
		code := codes[char]
		displayChar := escapeSpecialChars(char)
		writer.Write([]string{displayChar, code})
	}
	writer.Flush()

	if err := writer.Error(); err != nil {
		log.Fatal(err)
	}
}

func escapeSpecialChars(s string) string {
	return strings.NewReplacer(
		"\n", "\\n",
		"\t", "\\t",
		"\r", "\\r",
		"\"", "\\\"",
	).Replace(s)
}

// вычисляет энтропию
func calculateEntropy(alphabet []Symbol) float64 {
	entropy := 0.0
	for _, s := range alphabet {
		if s.Prob > 0 {
			entropy -= s.Prob * math.Log2(s.Prob)
		}
	}
	return entropy
}

// кодирование Шеннона-Фано
//
// рекурсивно делит символы на две группы с примерно равными вероятностями, левой ветке присваиваем 0, правой ветке 1
func generateShannonFanoCodes(alphabet []Symbol) map[string]string {
	codes := make(map[string]string)
	if len(alphabet) == 0 {
		return codes
	}

	var assignCodes func(symbols []Symbol, code string)
	assignCodes = func(symbols []Symbol, code string) {
		if len(symbols) == 1 {
			codes[symbols[0].Char] = code
			return
		}
		splitIndex := findSplitIndex(symbols)
		assignCodes(symbols[:splitIndex], code+"0")
		assignCodes(symbols[splitIndex:], code+"1")
	}

	assignCodes(alphabet, "")
	return codes
}

func findSplitIndex(symbols []Symbol) int {
	total := 0.0
	for _, s := range symbols {
		total += s.Prob
	}
	half := total / 2
	current := 0.0
	for i, s := range symbols {
		current += s.Prob
		if current >= half {
			return i + 1
		}
	}
	return len(symbols)
}

func generateHuffmanCodes(alphabet []Symbol) map[string]string {
	type Node struct {
		Symbols []Symbol
		Prob    float64
		Left    *Node
		Right   *Node
	}

	nodes := make([]*Node, len(alphabet))
	for i, s := range alphabet {
		nodes[i] = &Node{Symbols: []Symbol{s}, Prob: s.Prob}
	}

	for len(nodes) > 1 {
		sort.Slice(nodes, func(i, j int) bool { return nodes[i].Prob < nodes[j].Prob })
		left, right := nodes[0], nodes[1]
		newNode := &Node{
			Symbols: append(append([]Symbol{}, left.Symbols...), right.Symbols...),
			Prob:    left.Prob + right.Prob,
			Left:    left,
			Right:   right,
		}
		nodes = append(nodes[2:], newNode)
	}

	codes := make(map[string]string)
	var traverse func(node *Node, code string)
	traverse = func(node *Node, code string) {
		if node.Left == nil && node.Right == nil {
			if len(node.Symbols) == 1 {
				codes[node.Symbols[0].Char] = code
			}
			return
		}
		traverse(node.Left, code+"0")
		traverse(node.Right, code+"1")
	}

	if len(nodes) > 0 {
		traverse(nodes[0], "")
	}
	return codes
}

func calculateAverageCodeLength(alphabet []Symbol, codes map[string]string) float64 {
	avg := 0.0
	for _, s := range alphabet {
		if code, exists := codes[s.Char]; exists {
			avg += s.Prob * float64(utf8.RuneCountInString(code))
		}
	}
	return avg
}

func encodeText(text string, codes map[string]string) string {
	var encoded strings.Builder
	for _, r := range text {
		char := string(r)
		if code, exists := codes[char]; exists {
			encoded.WriteString(code)
		}
	}
	return encoded.String()
}

func decodeText(encoded string, codes map[string]string) string {
	reverseCodes := make(map[string]string)
	for char, code := range codes {
		reverseCodes[code] = char
	}

	var decoded strings.Builder
	var current strings.Builder

	for _, bit := range encoded {
		current.WriteRune(bit)
		if char, exists := reverseCodes[current.String()]; exists {
			decoded.WriteString(char)
			current.Reset()
		}
	}

	return decoded.String()
}

func saveToFile(content, filename string) {
	if err := os.WriteFile(filename, []byte(content), 0644); err != nil {
		log.Fatal(err)
	}
}
