#include "stm32f4xx.h"

// Лабораторная работа № 2, вариант 4, задание 5.2 для самостоятельной работы.
// Динамическая индикация числа с десятичной точкой: отображается «20.26» —
// точка (сегмент dp) включена во втором разряде (pos = 1).
// Схема: общий катод; сегменты a-g,dp -> PA0-PA7 (PA7 = dp), катоды разрядов -> PC0-PC3.

// Таблица кодов сегментов для цифр 0-9 (вариант с общим катодом, табл. 1 методички).
// Отображение бит на выводы: бит0=a (PA0), ..., бит6=g (PA6), бит7=dp (PA7).
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

// Бит десятичной точки (сегмент dp на линии PA7)
#define DP_BIT (0x80U)

// Число для отображения и маска точек по разрядам:
// dot_mask[pos] != 0 означает, что в разряде pos точка включена.
static const int number[4]   = {2, 0, 2, 6};
static const int dot_mask[4] = {0, 1, 0, 0}; // точка после второй цифры: «20.26»

// Программная задержка удержания разряда.
static void delay(volatile uint32_t t) {
    while (t--) __NOP();
}

int main(void) {
    // 1. Включаем тактирование портов A и C (шина AHB1)
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOCEN;

    // 2. Настраиваем PA0-PA7 (сегменты a-g,dp) как выходы push-pull.
    //    В отличие от main_dynamic.c здесь задействован и PA7 (сегмент dp).
    for (int i = 0; i <= 7; i++) {
        GPIOA->MODER   &= ~(0x3U << (i * 2U)); // очистить поле режима
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

    while (1) {
        // 4. Перебираем разряды
        for (int pos = 0; pos < 4; pos++) {
            GPIOC->BSRR = 0x000FU; // погасить все разряды (PC0-PC3 = «1»)

            // Код цифры; если в разряде предусмотрена точка — добавляем бит dp.
            uint32_t seg = digit_code[number[pos]];
            if (dot_mask[pos]) {
                seg |= DP_BIT; // включить сегмент dp (PA7 = «1»)
            }

            // Маска 0xFF00 сохраняет состояние PA8-PA15.
            GPIOA->ODR = (GPIOA->ODR & 0xFF00U) | seg;

            GPIOC->BSRR = (1U << (pos + 16U)); // включить разряд pos (PCpos = «0»)
            delay(1500);
        }
    }
}
