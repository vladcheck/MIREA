#include "stm32f4xx.h"

// Лабораторная работа №3, задание 3 для самостоятельной работы.
// Счётчик нажатий S1 (PB8) с индикацией на двухразрядном семисегментном
// индикаторе: каждое нажатие увеличивает число от 0 до 9, после 9 сброс в 0.
// Индикатор с общим катодом: сегменты a-g на PA0-PA6,
// катоды разрядов на PC0 (единицы) и PC1 (десятки, здесь всегда 0).
// Нажатие выделяется фронтом с дебаунсом и блокировкой удержания.

static const uint8_t SEG_CODE[10] = {
    0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F
};

static volatile uint32_t ms = 0;

void SysTick_Handler(void)
{
    ms++;
}

static inline uint32_t millis(void) { return ms; }

static inline void show_digit_segments(uint8_t num)
{
    uint32_t odr = GPIOA->ODR;
    odr &= ~0x7FU;
    odr |= (SEG_CODE[num] & 0x7FU);
    GPIOA->ODR = odr;
}

static inline void enable_digit(uint8_t idx)
{
    if (idx)
    {
        GPIOC->BSRR = (1U << 0);
        GPIOC->BSRR = (1U << (1 + 16));
    }
    else
    {
        GPIOC->BSRR = (1U << 1);
        GPIOC->BSRR = (1U << (0 + 16));
    }
}

int main(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN | RCC_AHB1ENR_GPIOCEN;
    volatile uint32_t tmp = RCC->AHB1ENR;
    (void)tmp;

    // PA0-PA6: сегменты, выходы push-pull
    for (int i = 0; i <= 6; i++)
    {
        GPIOA->MODER &= ~(0x3U << (i * 2));
        GPIOA->MODER |= (0x1U << (i * 2));
        GPIOA->OTYPER &= ~(1U << i);
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2));
        GPIOA->PUPDR &= ~(0x3U << (i * 2));
    }
    GPIOA->ODR &= ~0x7FU;

    // PC0, PC1: катоды, по умолчанию погашены (лог. 1)
    for (int i = 0; i <= 1; i++)
    {
        GPIOC->MODER &= ~(0x3U << (i * 2));
        GPIOC->MODER |= (0x1U << (i * 2));
        GPIOC->OTYPER &= ~(1U << i);
        GPIOC->OSPEEDR &= ~(0x3U << (i * 2));
        GPIOC->PUPDR &= ~(0x3U << (i * 2));
    }
    GPIOC->BSRR = (1U << 0) | (1U << 1);

    // PB8: вход с подтяжкой вверх
    GPIOB->MODER &= ~(0x3U << (8 * 2));
    GPIOB->PUPDR &= ~(0x3U << (8 * 2));
    GPIOB->PUPDR |= (0x1U << (8 * 2));

    SysTick_Config(SystemCoreClock / 1000U);

    uint8_t count = 0;       // счётчик 0-9
    uint8_t last_raw = 1;    // последний опрос (1 отпущен)
    uint8_t stable_cnt = 0;  // счётчик стабильности
    uint8_t press_armed = 1; // готовность к нажатию
    uint8_t mux_idx = 1;
    uint32_t t_mux = millis();
    uint32_t t_poll = millis() + 2U;

    while (1)
    {
        uint32_t now = millis();

        // Мультиплексирование каждые 2 мс: десятки всегда 0, единицы счётчик
        if ((int32_t)(now - t_mux) >= 0)
        {
            t_mux += 2U;
            if (mux_idx)
            {
                show_digit_segments(0);
                enable_digit(1);
            }
            else
            {
                show_digit_segments(count);
                enable_digit(0);
            }
            mux_idx ^= 1U;
        }

        // Опрос кнопки каждые 2 мс с дебаунсом 6 совпадений
        if ((int32_t)(now - t_poll) >= 0)
        {
            t_poll += 2U;
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
            if (stable_cnt >= 6U && raw == 0 && press_armed)
            {
                press_armed = 0;
                count++;
                if (count > 9)
                    count = 0;
            }
            if (stable_cnt >= 6U && raw == 1)
                press_armed = 1;
        }
    }
}
