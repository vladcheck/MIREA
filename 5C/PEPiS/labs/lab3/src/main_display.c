#include "stm32f4xx.h"

// Лабораторная работа №3, пример из п. 3.2 методички (трек STM32F407).
// Свитчи SW1-SW4 на PB0-PB3 (активный низкий, внутренняя подтяжка вверх).
// Семисегментный индикатор с общим катодом: сегменты a-g на PA0-PA6,
// катоды двух разрядов на PC0 (единицы, правый) и PC1 (десятки, левый).
// Считанный 4-битный код 0-15 отображается десятичным числом 0-15.
// Опрос с фильтром дребезга, развёртка на SysTick 1 мс, слот разряда 2 мс.

// Таблица сегментов, бит0 = a (PA0), ..., бит6 = g (PA6)
static const uint8_t SEG_CODE[10] = {
    0x3F, // 0: a b c d e f
    0x06, // 1: b c
    0x5B, // 2: a b d e g
    0x4F, // 3: a b c d g
    0x66, // 4: b c f g
    0x6D, // 5: a c d f g
    0x7D, // 6: a c d e f g
    0x07, // 7: a b c
    0x7F, // 8: a b c d e f g
    0x6F  // 9: a b c d f g
};

static volatile uint32_t ms = 0;

void SysTick_Handler(void)
{
    ms++;
}

static inline uint32_t millis(void) { return ms; }

static void gpio_init(void)
{
    // Тактирование AHB1: порты A, B, C
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN | RCC_AHB1ENR_GPIOCEN;
    volatile uint32_t tmp = RCC->AHB1ENR;
    (void)tmp;

    // PA0-PA6: выход push-pull, низкая скорость, без подтяжек
    for (int i = 0; i <= 6; i++)
    {
        GPIOA->MODER &= ~(0x3U << (i * 2));
        GPIOA->MODER |= (0x1U << (i * 2)); // 01 выход
        GPIOA->OTYPER &= ~(1U << i);       // push-pull
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2));
        GPIOA->PUPDR &= ~(0x3U << (i * 2));
    }
    GPIOA->ODR &= ~0x7FU; // погасить сегменты

    // PC0, PC1: выходы катодов, по умолчанию выключены (лог. 1)
    for (int i = 0; i <= 1; i++)
    {
        GPIOC->MODER &= ~(0x3U << (i * 2));
        GPIOC->MODER |= (0x1U << (i * 2));
        GPIOC->OTYPER &= ~(1U << i);
        GPIOC->OSPEEDR &= ~(0x3U << (i * 2));
        GPIOC->PUPDR &= ~(0x3U << (i * 2));
    }
    GPIOC->BSRR = (1U << 0) | (1U << 1); // оба катода в 1, разряды погашены

    // PB0-PB3: входы с внутренней подтяжкой вверх
    for (int i = 0; i <= 3; i++)
    {
        GPIOB->MODER &= ~(0x3U << (i * 2)); // 00 вход
        GPIOB->PUPDR &= ~(0x3U << (i * 2));
        GPIOB->PUPDR |= (0x1U << (i * 2)); // 01 pull-up
    }
}

// Вывод кода цифры на общие сегменты PA0-PA6, остальные биты порта не трогаем
static inline void show_digit_segments(uint8_t num)
{
    uint32_t odr = GPIOA->ODR;
    odr &= ~0x7FU;
    odr |= (SEG_CODE[num] & 0x7FU);
    GPIOA->ODR = odr;
}

// Выбор активного разряда, общий катод, активный низкий:
// idx = 1 левый (десятки) на PC1, idx = 0 правый (единицы) на PC0
static inline void enable_digit(uint8_t idx)
{
    if (idx)
    {
        GPIOC->BSRR = (1U << 0);        // PC0 = 1 (правый погашен)
        GPIOC->BSRR = (1U << (1 + 16)); // PC1 = 0 (левый включён)
    }
    else
    {
        GPIOC->BSRR = (1U << 1);        // PC1 = 1 (левый погашен)
        GPIOC->BSRR = (1U << (0 + 16)); // PC0 = 0 (правый включён)
    }
}

// Фильтр дребезга: новое значение принимается после N одинаковых
// последовательных опросов с периодом POLL_DT_MS
#define POLL_DT_MS 2U
#define STABLE_COUNT_N 6U // около 12 мс стабильности

static uint8_t debounced_value = 0; // устойчивое значение 0-15

static void debounce_poll(void)
{
    static uint8_t last_sample = 0;
    static uint8_t same_count = 0;
    // Чтение PB3-PB0, активный низкий, поэтому инверсия
    uint8_t raw = (uint8_t)((~GPIOB->IDR) & 0x0F);
    if (raw == last_sample)
    {
        if (same_count < STABLE_COUNT_N)
        {
            same_count++;
            if (same_count == STABLE_COUNT_N)
                debounced_value = raw;
        }
    }
    else
    {
        last_sample = raw;
        same_count = 0;
    }
}

int main(void)
{
    gpio_init();
    SysTick_Config(SystemCoreClock / 1000U); // SysTick 1 мс

    uint8_t current = 0;
    uint8_t tens = 0, ones = 0;
    uint32_t t_next_mux = millis(); // мультиплексирование разрядов
    uint32_t t_next_poll = millis() + POLL_DT_MS; // опрос свитчей
    uint8_t mux_idx = 1; // 1 левый (десятки), 0 правый (единицы)

    while (1)
    {
        uint32_t now = millis();

        // 1) Мультиплексирование каждые 2 мс
        if ((int32_t)(now - t_next_mux) >= 0)
        {
            t_next_mux += 2U;
            if (mux_idx)
            {
                show_digit_segments(tens);
                enable_digit(1);
            }
            else
            {
                show_digit_segments(ones);
                enable_digit(0);
            }
            mux_idx ^= 1U;
        }

        // 2) Опрос свитчей с дебаунсом
        if ((int32_t)(now - t_next_poll) >= 0)
        {
            t_next_poll += POLL_DT_MS;
            debounce_poll();
            if (debounced_value != current)
            {
                current = debounced_value; // 0-15
                tens = current / 10U;      // 0-1
                ones = current % 10U;      // 0-9
            }
        }
    }
}
