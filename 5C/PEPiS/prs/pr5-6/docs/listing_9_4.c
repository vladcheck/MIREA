#include "stm32f1xx.h"

#define CLOCK_TIMEOUT       1000000U
#define TIMER_INTERVAL_MS   250U

volatile uint32_t g_update_count;

static uint8_t Clock_Init_HSI8MHz(void)
{
    uint32_t timeout = CLOCK_TIMEOUT;

    RCC->CR |= RCC_CR_HSION;
    while ((RCC->CR & RCC_CR_HSIRDY) == 0U) {
        if (--timeout == 0U) return 0U;
    }

    RCC->CFGR &= ~RCC_CFGR_SW;
    timeout = CLOCK_TIMEOUT;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_HSI) {
        if (--timeout == 0U) return 0U;
    }

    RCC->CFGR &= ~(RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    RCC->CR &= ~(RCC_CR_CSSON | RCC_CR_PLLON | RCC_CR_HSEON);
    return 1U;
}

static uint8_t TIM2_IntervalInit(uint32_t interval_ms)
{
    if (interval_ms == 0U || interval_ms > 65536U) return 0U;

    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    RCC->APB1RSTR |= RCC_APB1RSTR_TIM2RST;
    RCC->APB1RSTR &= ~RCC_APB1RSTR_TIM2RST;

    /* PA1 — обычный выход push-pull 2 МГц, а не TIM2_CH2. */
    GPIOA->CRL &= ~(GPIO_CRL_MODE1 | GPIO_CRL_CNF1);
    GPIOA->CRL |= GPIO_CRL_MODE1_1;
    GPIOA->BSRR = GPIO_BSRR_BR1;

    TIM2->CR1 = 0U;
    TIM2->DIER = 0U;
    TIM2->PSC = 7999U;                    /* 8 МГц / 8000 = 1 кГц */
    TIM2->ARR = (uint16_t)(interval_ms - 1U);
    TIM2->CNT = 0U;

    /* EGR — регистр командной записи; событие формируется присваиванием. */
    TIM2->EGR = TIM_EGR_UG;
    TIM2->SR = 0U;                        /* очистка флага после UG */
    TIM2->DIER |= TIM_DIER_UIE;

    NVIC_ClearPendingIRQ(TIM2_IRQn);
    NVIC_SetPriority(TIM2_IRQn, 2U);
    NVIC_EnableIRQ(TIM2_IRQn);
    TIM2->CR1 |= TIM_CR1_CEN;
    return 1U;
}

void TIM2_IRQHandler(void)
{
    if ((TIM2->SR & TIM_SR_UIF) != 0U) {
        /* UIF имеет семантику rc_w0: он очищается записью нуля. */
        TIM2->SR = (uint16_t)~TIM_SR_UIF;
        GPIOA->ODR ^= GPIO_ODR_ODR1;
        ++g_update_count;
    }
}

int main(void)
{
    if (!Clock_Init_HSI8MHz()) while (1) { }
    if (!TIM2_IntervalInit(TIMER_INTERVAL_MS)) while (1) { }

    while (1) {
        __WFI();
    }
}
