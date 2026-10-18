#include "stm32f4xx.h"

// Программная задержка. volatile запрещает компилятору удалять цикл.
// Скорость "огня" регулируется константой DELAY_COUNT: меньше — быстрее.
#define DELAY_COUNT 50000U   // было 200000 — огонь движется в 4 раза быстрее

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

    // 3. Основной цикл: бегущий огонь PA0 -> PA3 с изменённой скоростью
    uint8_t pattern = 0x01U; // 0000 0001 — старт с PA0

    while (1) {
        GPIOA->ODR = (GPIOA->ODR & 0xFFF0U) | pattern;
        delay(DELAY_COUNT);

        pattern <<= 1;              // сдвиг "огня" к следующему выводу
        if (pattern == 0U) {        // после PA3 вернуться к PA0
            pattern = 0x01U;
        }
    }
}
