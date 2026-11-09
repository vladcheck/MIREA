#include "stm32f4xx.h"

// Лабораторная работа №3, задание 4 (вариант 4).
// Динамическое отображение состояния входов S1-S4 (PB8-PB11) на
// четырёхразрядном семисегментном индикаторе: каждый разряд показывает
// одну двоичную цифру, например 0001, 0010, 1111.
// Раскладка слева направо: DIG1 S1, DIG2 S2, DIG3 S3, DIG4 S4,
// то есть старший бит слева, младший справа.
// Свитчи активные низкие (замкнут на GND читается как 1 после инверсии),
// индикатор с общим катодом: сегменты a-g на PA0-PA6,
// выводы разрядов DIG1-DIG4 на PB12-PB15 (активный низкий).
// Опрос с фильтром дребезга, развёртка на SysTick 1 мс, слот разряда 2 мс.

// Полярность индикатора: 1 — общий анод (выводы разрядов на +3 В, сегмент
// тонет: 0 = горит, разряд включается высоким уровнем на PCx);
// 0 — общий катод (1 = горит, разряд = 0 на PCx) — как на стенде и в методичке.
#define COMMON_ANODE 0

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
    // Тактирование AHB1: порты A, B
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
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
#if COMMON_ANODE
    GPIOA->ODR |= 0x7FU; // сегменты погашены (1 = тёмный)
#else
    GPIOA->ODR &= ~0x7FU; // погасить сегменты
#endif

    // PB12-PB15: выводы разрядов DIG1-DIG4 (на стенде выводы GPIOC для
    // этого задания работают неустойчиво), по умолчанию погашены
    for (int i = 12; i <= 15; i++)
    {
        GPIOB->MODER &= ~(0x3U << (i * 2));
        GPIOB->MODER |= (0x1U << (i * 2));
        GPIOB->OTYPER &= ~(1U << i);
        GPIOB->OSPEEDR &= ~(0x3U << (i * 2));
        GPIOB->PUPDR &= ~(0x3U << (i * 2));
    }
#if COMMON_ANODE
    GPIOB->BSRR = (1U << 12) << 16 | (1U << 13) << 16 |
                  (1U << 14) << 16 | (1U << 15) << 16; // все разряды погашены (0)
#else
    GPIOB->BSRR = (1U << 12) | (1U << 13) | (1U << 14) | (1U << 15);
#endif

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
#if COMMON_ANODE
    odr |= ((~SEG_CODE[num]) & 0x7FU); // общий анод: 0 = сегмент горит
#else
    odr |= (SEG_CODE[num] & 0x7FU);
#endif
    GPIOA->ODR = odr;
}

// Включение разряда pos 0-3 (0 DIG1 левый S1 ... 3 DIG4 правый S4),
// остальные три гасятся. Вывод разряда: PB(12+pos).
// COMMON_ANODE=1: вывод разряда = 1 включает разряд; 0 — общий катод: 0 включает.
static inline void enable_digit(uint8_t pos)
{
#if COMMON_ANODE
    GPIOB->BSRR = (1U << 12) << 16 | (1U << 13) << 16 |
                  (1U << 14) << 16 | (1U << 15) << 16; // все погасить (0)
    GPIOB->BSRR = (1U << (12 + pos)); // выбранный в 1 (включить)
#else
    GPIOB->BSRR = (1U << 12) | (1U << 13) | (1U << 14) | (1U << 15); // все погасить
    GPIOB->BSRR = (1U << (12 + pos)) << 16; // выбранный в 0 (включить)
#endif
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
#if COMMON_ANODE
            GPIOB->BSRR = (1U << 12) << 16 | (1U << 13) << 16 |
                          (1U << 14) << 16 | (1U << 15) << 16; // все погашены (0)
#else
            GPIOB->BSRR = (1U << 12) | (1U << 13) | (1U << 14) | (1U << 15);
#endif
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
