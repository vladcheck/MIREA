#include "stm32f4xx.h"

// Лабораторная работа №3, задание 4 (вариант 4).
// Динамическое отображение состояния входов S1-S4 (PB8-PB11) на
// четырёхразрядном семисегментном индикаторе: каждый разряд показывает
// одну двоичную цифру, например 0001, 0010, 1111.
// Раскладка слева направо: DIG1 S1, DIG2 S2, DIG3 S3, DIG4 S4,
// то есть старший бит слева, младший справа.
// Свитчи активные низкие (замкнут на GND читается как 1 после инверсии),
// индикатор с общим катодом: сегменты a-g на PA0-PA6,
// катоды разрядов на PC0-PC3 (активный низкий).
// Опрос с фильтром дребезга, развёртка на SysTick 1 мс, слот разряда 2 мс.

static const uint8_t SEG_CODE[10] = {
    0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F
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

    // PA0-PA6: сегменты, выходы push-pull, низкая скорость, без подтяжек
    for (int i = 0; i <= 6; i++)
    {
        GPIOA->MODER &= ~(0x3U << (i * 2));
        GPIOA->MODER |= (0x1U << (i * 2)); // 01 выход
        GPIOA->OTYPER &= ~(1U << i);       // push-pull
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2));
        GPIOA->PUPDR &= ~(0x3U << (i * 2));
    }
    GPIOA->ODR &= ~0x7FU; // погасить сегменты

    // PC0-PC3: катоды четырёх разрядов, по умолчанию погашены (лог. 1)
    for (int i = 0; i <= 3; i++)
    {
        GPIOC->MODER &= ~(0x3U << (i * 2));
        GPIOC->MODER |= (0x1U << (i * 2));
        GPIOC->OTYPER &= ~(1U << i);
        GPIOC->OSPEEDR &= ~(0x3U << (i * 2));
        GPIOC->PUPDR &= ~(0x3U << (i * 2));
    }
    GPIOC->BSRR = (1U << 0) | (1U << 1) | (1U << 2) | (1U << 3);

    // PB8-PB11: входы S1-S4 с внутренней подтяжкой вверх
    for (int i = 8; i <= 11; i++)
    {
        GPIOB->MODER &= ~(0x3U << (i * 2)); // 00 вход
        GPIOB->PUPDR &= ~(0x3U << (i * 2));
        GPIOB->PUPDR |= (0x1U << (i * 2)); // 01 pull-up
    }
}

static inline void show_digit_segments(uint8_t num)
{
    uint32_t odr = GPIOA->ODR;
    odr &= ~0x7FU;
    odr |= (SEG_CODE[num] & 0x7FU);
    GPIOA->ODR = odr;
}

// Включение разряда pos 0-3 (0 DIG1 левый S1 ... 3 DIG4 правый S4),
// остальные три гасятся. Катод на PCpos, активный низкий.
static inline void enable_digit(uint8_t pos)
{
    GPIOC->BSRR = (1U << 0) | (1U << 1) | (1U << 2) | (1U << 3); // все погасить
    GPIOC->BSRR = (1U << (pos + 16)); // выбранный в 0 (включить)
}

#define POLL_DT_MS 2U
#define STABLE_COUNT_N 6U // около 12 мс стабильности

static uint8_t stable_bits = 0; // устойчивые биты S1-S4 (бит i = S(i+1))

static void debounce_poll(void)
{
    static uint8_t last_sample = 0;
    static uint8_t same_count = 0;
    // Активный низкий, поэтому инверсия: бит = 1 пока свитч замкнут
    uint8_t raw = (uint8_t)(((~GPIOB->IDR) >> 8) & 0x0F);
    if (raw == last_sample)
    {
        if (same_count < STABLE_COUNT_N)
        {
            same_count++;
            if (same_count == STABLE_COUNT_N)
                stable_bits = raw;
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

    uint32_t t_next_mux = millis();
    uint32_t t_next_poll = millis() + POLL_DT_MS;
    uint8_t mux_pos = 0; // 0 DIG1 (S1) ... 3 DIG4 (S4)

    while (1)
    {
        uint32_t now = millis();

        // Мультиплексирование: слот разряда 2 мс, кадр 8 мс (около 125 Гц)
        if ((int32_t)(now - t_next_mux) >= 0)
        {
            t_next_mux += 2U;
            // DIG слева направо показывают S1 S2 S3 S4; сначала гасим все
            // разряды, потом ставим сегменты и включаем нужный (без гостинга)
            GPIOC->BSRR = (1U << 0) | (1U << 1) | (1U << 2) | (1U << 3);
            uint8_t bit = (stable_bits >> mux_pos) & 0x01;
            show_digit_segments(bit);
            enable_digit(mux_pos);
            mux_pos++;
            if (mux_pos > 3)
                mux_pos = 0;
        }

        // Опрос свитчей с дебаунсом
        if ((int32_t)(now - t_next_poll) >= 0)
        {
            t_next_poll += POLL_DT_MS;
            debounce_poll();
        }
    }
}
