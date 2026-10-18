#include "stm32f4xx.h"

// Программная задержка. Параметр объявлен как volatile,
// чтобы компилятор не выбросил "пустой" цикл при оптимизации.
void delay(volatile uint32_t t) {
    while (t--) __NOP();
}

int main(void) {
    // 1. Включаем тактирование порта A (шина AHB1)
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    // 2. Настраиваем PA0 как выход push-pull, низкая скорость, без подтяжки
    GPIOA->MODER   &= ~(0x3U << (0U * 2U)); // очистить 2-битное поле режима
    GPIOA->MODER   |=  (0x1U << (0U * 2U)); // 01 — выход
    GPIOA->OTYPER  &= ~(1U << 0U);          // 0 — push-pull
    GPIOA->OSPEEDR &= ~(0x3U << (0U * 2U)); // 00 — низкая скорость
    GPIOA->PUPDR   &= ~(0x3U << (0U * 2U)); // 00 — без подтяжки

    // 3. Основной цикл: мигание светодиода на PA0
    while (1) {
        GPIOA->BSRR = (1U << 0U);          // включить (младшие 16 бит BSRR = "1")
        delay(300000);
        GPIOA->BSRR = (1U << (0U + 16U));  // выключить (старшие 16 бит BSRR = "0")
        delay(300000);
    }
}
