#include "stm32f4xx.h"

// Лабораторная работа № 2, вариант 4.
// Статическая индикация: цифра «4» (номер варианта) на одном разряде.
// Схема: общий катод; сегменты a-g -> PA0-PA6, катод разряда -> PC0 (активный низкий).

// Таблица кодов сегментов для цифр 0-9 (вариант с общим катодом, табл. 1 методички).
// Отображение бит на выводы: бит0=a (PA0), бит1=b (PA1), ..., бит6=g (PA6).
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

// Программная задержка. Параметр volatile запрещает компилятору удалять цикл.
static void delay(volatile uint32_t t) {
    while (t--) __NOP();
}

int main(void) {
    // 1. Включаем тактирование портов A и C (шина AHB1)
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOCEN;

    // 2. Настраиваем PA0-PA6 (сегменты a-g) как выходы push-pull,
    //    низкая скорость, без подтяжек
    for (int i = 0; i <= 6; i++) {
        GPIOA->MODER   &= ~(0x3U << (i * 2U)); // очистить поле режима
        GPIOA->MODER   |=  (0x1U << (i * 2U)); // 01 — выход
        GPIOA->OTYPER  &= ~(1U << i);          // 0 — push-pull
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2U)); // 00 — низкая скорость
        GPIOA->PUPDR   &= ~(0x3U << (i * 2U)); // 00 — без подтяжки
    }

    // 3. Настраиваем PC0 (общий катод разряда) как выход push-pull
    GPIOC->MODER   &= ~(0x3U << (0U * 2U));
    GPIOC->MODER   |=  (0x1U << (0U * 2U)); // 01 — выход
    GPIOC->OTYPER  &= ~(1U << 0U);          // 0 — push-pull
    GPIOC->OSPEEDR &= ~(0x3U << (0U * 2U));
    GPIOC->PUPDR   &= ~(0x3U << (0U * 2U));

    // 4. Вариант 4: отображаемая цифра — «4»
    const int digit = 4;

    while (1) {
        // 5. Подаём код цифры на линии сегментов (PA0-PA6).
        //    Маска 0xFF80 сохраняет состояние PA7-PA15.
        GPIOA->ODR = (GPIOA->ODR & 0xFF80U) | digit_code[digit];

        // 6. Активируем катод разряда (низкий уровень на PC0).
        //    Старшие 16 бит BSRR атомарно сбрасывают линию в «0».
        GPIOC->BSRR = (1U << (0U + 16U));

        delay(400000); // задержка для наблюдения (статический режим)
    }
}
