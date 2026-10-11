#include "stm32f4xx.h"

// Лабораторная работа №3, задание 2 для самостоятельной работы.
// Два свитча S1 (PB0) и S2 (PB1) задают режим светодиода на PA0:
//   SW2 SW1 = 0 0: выключен;
//   SW2 SW1 = 0 1: мигание медленно (период около 1 с);
//   SW2 SW1 = 1 0: мигание быстро (период около 250 мс);
//   SW2 SW1 = 1 1: включён постоянно.
// Свитчи активные низкие (замкнут на GND читается как 1 после инверсии).
// Входы опрашиваются каждые 2 мс с фильтром дребезга 6 совпадений,
// мигание построено на неблокирующем планировщике от SysTick.

static volatile uint32_t ms = 0;

void SysTick_Handler(void)
{
    ms++;
}

static inline uint32_t millis(void) { return ms; }

#define POLL_DT_MS 2U
#define STABLE_N 6U
#define SLOW_HALF_MS 500U // полупериод медленного мигания
#define FAST_HALF_MS 125U // полупериод быстрого мигания

static uint8_t stable_mode = 0; // устойчивый код режима 0-3

static void debounce_poll(void)
{
    static uint8_t last = 0;
    static uint8_t cnt = 0;
    // Активный низкий, поэтому инверсия: бит = 1 пока свитч замкнут
    uint8_t raw = (uint8_t)((~GPIOB->IDR) & 0x03);
    if (raw == last)
    {
        if (cnt < STABLE_N)
        {
            cnt++;
            if (cnt == STABLE_N)
                stable_mode = raw;
        }
    }
    else
    {
        last = raw;
        cnt = 0;
    }
}

int main(void)
{
    // Тактирование портов A и B
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    volatile uint32_t tmp = RCC->AHB1ENR;
    (void)tmp;

    // PB0, PB1: входы с подтяжкой вверх
    for (int i = 0; i <= 1; i++)
    {
        GPIOB->MODER &= ~(0x3U << (i * 2));
        GPIOB->PUPDR &= ~(0x3U << (i * 2));
        GPIOB->PUPDR |= (0x1U << (i * 2));
    }

    // PA0: выход push-pull, LED изначально погашен
    GPIOA->MODER &= ~(0x3U << (0 * 2));
    GPIOA->MODER |= (0x1U << (0 * 2));
    GPIOA->OTYPER &= ~(1U << 0);
    GPIOA->OSPEEDR &= ~(0x3U << (0 * 2));
    GPIOA->PUPDR &= ~(0x3U << (0 * 2));
    GPIOA->BSRR = (1U << (0 + 16));

    SysTick_Config(SystemCoreClock / 1000U);

    uint32_t t_poll = millis() + POLL_DT_MS;
    uint32_t t_blink = millis();
    uint8_t blink_state = 0;

    while (1)
    {
        uint32_t now = millis();

        if ((int32_t)(now - t_poll) >= 0)
        {
            t_poll += POLL_DT_MS;
            debounce_poll();
        }

        switch (stable_mode)
        {
        case 0: // 00: выключен
            GPIOA->BSRR = (1U << (0 + 16));
            blink_state = 0;
            t_blink = now;
            break;
        case 3: // 11: включён постоянно
            GPIOA->BSRR = (1U << 0);
            blink_state = 1;
            t_blink = now;
            break;
        case 1: // 01: медленно
        case 2: // 10: быстро
        {
            uint32_t half = (stable_mode == 1) ? SLOW_HALF_MS : FAST_HALF_MS;
            if ((int32_t)(now - t_blink) >= 0)
            {
                t_blink += half;
                blink_state ^= 1U;
                if (blink_state)
                    GPIOA->BSRR = (1U << 0);
                else
                    GPIOA->BSRR = (1U << (0 + 16));
            }
            break;
        }
        default:
            break;
        }
    }
}
