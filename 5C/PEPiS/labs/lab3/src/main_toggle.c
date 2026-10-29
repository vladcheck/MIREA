#include "stm32f4xx.h"

// Лабораторная работа №3, задание 1 для самостоятельной работы.
// Переключатель-инвертор: каждое нажатие свитча S1 (PB8) меняет состояние
// светодиода (PA0) на противоположное. Дребезг подавлен программно:
// нажатие засчитывается после 6 одинаковых опросов подряд (около 12 мс),
// повторное срабатывание от удержания блокируется флагом ожидания отпускания.

static volatile uint32_t ms = 0;

void SysTick_Handler(void)
{
    ms++;
}

static inline uint32_t millis(void) { return ms; }

int main(void)
{
    // Тактирование портов A и B
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    volatile uint32_t tmp = RCC->AHB1ENR;
    (void)tmp;

    // PB8: вход с подтяжкой вверх (отпущен 1, нажат 0)
    GPIOB->MODER &= ~(0x3U << (8 * 2));
    GPIOB->PUPDR &= ~(0x3U << (8 * 2));
    GPIOB->PUPDR |= (0x1U << (8 * 2));

    // PA0: выход push-pull, LED изначально погашен
    GPIOA->MODER &= ~(0x3U << (0 * 2));
    GPIOA->MODER |= (0x1U << (0 * 2));
    GPIOA->OTYPER &= ~(1U << 0);
    GPIOA->OSPEEDR &= ~(0x3U << (0 * 2));
    GPIOA->PUPDR &= ~(0x3U << (0 * 2));
    GPIOA->BSRR = (1U << (0 + 16));

    SysTick_Config(SystemCoreClock / 1000U);

    uint8_t led_on = 0;      // текущее состояние светодиода
    uint8_t last_raw = 1;    // последний опрос PB8 (1 отпущен)
    uint8_t stable_cnt = 0;  // счётчик одинаковых опросов
    uint8_t press_armed = 1; // 1 пока кнопка отпущена и готова к нажатию
    uint32_t t_next = millis() + 2U;

    while (1)
    {
        uint32_t now = millis();
        if ((int32_t)(now - t_next) < 0)
            continue;
        t_next += 2U;

        uint8_t raw = (GPIOB->IDR & (1U << 8)) ? 1 : 0;
        if (raw == last_raw)
        {
            if (stable_cnt < 6U)
                stable_cnt++;
        }
        else
        {
            last_raw = raw;
            stable_cnt = 0;
        }

        // Устойчивый низкий уровень при взведённом флаге: одно переключение
        if (stable_cnt >= 6U && raw == 0 && press_armed)
        {
            press_armed = 0;
            led_on ^= 1U;
            if (led_on)
                GPIOA->BSRR = (1U << 0);
            else
                GPIOA->BSRR = (1U << (0 + 16));
        }
        // Устойчивый высокий уровень снова взводит флаг
        if (stable_cnt >= 6U && raw == 1)
            press_armed = 1;
    }
}
