#include "stm32f4xx.h"

// Программная задержка. volatile запрещает компилятору удалять цикл.
void delay(volatile uint32_t t) {
    while (t--) __NOP();
}

int main(void) {
    // 1. Включаем тактирование порта A (шина AHB1)
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    // 2. Настройка PA0–PA3 как выходы push-pull, низкая скорость, без подтяжки
    for (int i = 0; i < 4; i++) {
        GPIOA->MODER   &= ~(0x3U << (i * 2U)); // очистить 2-битное поле режима
        GPIOA->MODER   |=  (0x1U << (i * 2U)); // 01 — выход
        GPIOA->OTYPER  &= ~(1U << i);          // 0 — push-pull
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2U)); // 00 — низкая скорость
        GPIOA->PUPDR   &= ~(0x3U << (i * 2U)); // 00 — без подтяжки
    }

    // 3. Основной цикл: бегущий огонь в ОБРАТНУЮ сторону, PA3 -> PA0
    uint8_t pattern = 0x08U; // 0000 1000 — старт с PA3

    while (1) {
        GPIOA->ODR = (GPIOA->ODR & 0xFFF0U) | pattern;
        delay(200000);

        pattern >>= 1;              // сдвиг "огня" к младшему выводу
        if (pattern == 0U) {        // после PA0 вернуться к PA3
            pattern = 0x08U;
        }
    }
}
