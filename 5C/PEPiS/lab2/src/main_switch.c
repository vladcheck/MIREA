#include "stm32f4xx.h"

// Лабораторная работа № 2, вариант 4, задание 5.1 для самостоятельной работы.
// Динамическая индикация с переключением отображаемого значения по внешнему сигналу:
//   - исходное состояние: текущий год 2026;
//   - при активном низком уровне («0») на входе PB0: год рождения студента (в примере 2005).
// Кнопка S1: вывод PB0, внутренняя подтяжка к питанию, нажатие замыкает на GND.
// Схема индикатора: общий катод; сегменты a-g -> PA0-PA6, катоды разрядов -> PC0-PC3.

// Таблица кодов сегментов для цифр 0-9 (вариант с общим катодом, табл. 1 методички).
// Отображение бит на выводы: бит0=a (PA0), ..., бит6=g (PA6).
static const uint8_t digit_code[10] = {
    0x3F, // 0 -> a b c d e f
    0x06, // 1 -> b c
    0x5B, // 2 -> a b d e g
    0x4F, // 3 -> a b c d g
    0x66, // 4 -> b c f g
    0x6D, // 5 -> a c d f g
    0x7D, // 6 -> a c d e f g
    0x07, // 7 -> a b c
    0x7F, // 8 -> a b c d e f g
    0x6F  // 9 -> a b c d f g
};

// Отображаемые значения (разряды слева направо: тысячи -> единицы)
static const int year_current[4] = {2, 0, 2, 6}; // текущий год
static const int year_birth[4]   = {2, 0, 0, 5}; // год рождения студента (пример; указать свой)

// Программная задержка удержания разряда.
static void delay(volatile uint32_t t) {
    while (t--) __NOP();
}

int main(void) {
    // 1. Включаем тактирование портов A, B и C (шина AHB1)
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN | RCC_AHB1ENR_GPIOCEN;

    // 2. Настраиваем PA0-PA6 (сегменты a-g) как выходы push-pull
    for (int i = 0; i <= 6; i++) {
        GPIOA->MODER   &= ~(0x3U << (i * 2U));
        GPIOA->MODER   |=  (0x1U << (i * 2U)); // 01 — выход
        GPIOA->OTYPER  &= ~(1U << i);          // 0 — push-pull
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2U)); // 00 — низкая скорость
        GPIOA->PUPDR   &= ~(0x3U << (i * 2U)); // 00 — без подтяжки
    }

    // 3. Настраиваем PC0-PC3 (катоды разрядов) как выходы push-pull
    for (int i = 0; i < 4; i++) {
        GPIOC->MODER   &= ~(0x3U << (i * 2U));
        GPIOC->MODER   |=  (0x1U << (i * 2U)); // 01 — выход
        GPIOC->OTYPER  &= ~(1U << i);
        GPIOC->OSPEEDR &= ~(0x3U << (i * 2U));
        GPIOC->PUPDR   &= ~(0x3U << (i * 2U));
    }

    // 4. Настраиваем PB0 (кнопка S1) как вход с подтяжкой к питанию:
    //    MODER = 00 (вход), PUPDR = 01 (pull-up). Ненажатая кнопка читается как «1»,
    //    нажатая (замыкание на GND) — как «0».
    GPIOB->MODER &= ~(0x3U << (0U * 2U)); // 00 — вход
    GPIOB->PUPDR &= ~(0x3U << (0U * 2U));
    GPIOB->PUPDR |=  (0x1U << (0U * 2U)); // 01 — pull-up

    // Простое подавление дребезга: решение о состоянии кнопки принимается
    // только после DEBOUNCE_N одинаковых последовательных чтений.
    const int DEBOUNCE_N = 50;
    int pressed_cnt = 0;   // счётчик последовательных чтений «0»
    int released_cnt = 0;  // счётчик последовательных чтений «1»
    int show_birth = 0;    // 0 — текущий год, 1 — год рождения

    while (1) {
        // 5. Опрос кнопки с подавлением дребезга
        if ((GPIOB->IDR & (1U << 0U)) == 0U) {
            pressed_cnt++;
            released_cnt = 0;
        } else {
            released_cnt++;
            pressed_cnt = 0;
        }
        if (pressed_cnt >= DEBOUNCE_N) {
            show_birth = 1;
        } else if (released_cnt >= DEBOUNCE_N) {
            show_birth = 0;
        }

        // 6. Выбор отображаемого значения
        const int *number = show_birth ? year_birth : year_current;

        // 7. Один проход мультиплексирования по четырём разрядам
        for (int pos = 0; pos < 4; pos++) {
            GPIOC->BSRR = 0x000FU; // погасить все разряды (PC0-PC3 = «1»)
            GPIOA->ODR = (GPIOA->ODR & 0xFF80U) | digit_code[number[pos]];
            GPIOC->BSRR = (1U << (pos + 16U)); // включить разряд pos (PCpos = «0»)
            delay(1500);
        }
    }
}
