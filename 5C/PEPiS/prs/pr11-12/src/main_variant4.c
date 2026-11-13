/*====================================================================
 * Практическая работа № 11-12 «Исследование цифро-аналогового
 * преобразования на матрице R-2R» (учебная работа № 6 методички).
 * Платформа STM32F103C8, порт матрицы PA0..PA7, питание 3,3 В.
 *
 * Индивидуальный вариант 4:
 *   коды для расчёта и измерения: D1 = 76, D2 = 133, D3 = 207;
 *   шаг пилообразного сигнала: Tш = 10 мс (таблица 9.35 методички);
 *   расчётный период пилы: 256 * Tш = 2560 мс;
 *   диагностическое изменение (аппаратное): отключить завершающий
 *   резистор 2R матрицы, прошивка не меняется.
 *
 * Программа сначала последовательно удерживает коды 76, 133 и 207
 * по DWELL_MS на каждый, чтобы заполнить первые три строки таблицы
 * 9.33 за один запуск, затем формирует непрерывную пилу 0..255
 * прерыванием таймера TIM2 с шагом Tш = 10 мс.
 *
 * Тактирование: HSI 8 МГц без PLL (по методичке). TIM2: PSC = 7999,
 * период обновления 1 мс, ARR = Tш - 1 = 9, шаг пилы 10 мс.
 *====================================================================*/
#include "stm32f1xx.h"
#include <stdint.h>

#define D1        76U  /* первый код варианта 4 */
#define D2        133U /* второй код варианта 4 */
#define D3        207U /* третий код варианта 4 */
#define T_STEP_MS 10U  /* шаг пилы варианта 4, таблица 9.35 */
#define DWELL_MS  2000U /* удержание каждого из трёх кодов, мс */

static volatile uint8_t dac_code = 0U;

/* Перевод тактирования на внутренний генератор HSI 8 МГц без PLL. */
static void Clock_HSI8_Init(void)
{
    RCC->CR |= RCC_CR_HSION;
    while ((RCC->CR & RCC_CR_HSIRDY) == 0U) { }
    RCC->CFGR &= ~(RCC_CFGR_SW | RCC_CFGR_HPRE |
                   RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2);
    RCC->CFGR |= RCC_CFGR_SW_HSI;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_HSI) { }
    SystemCoreClockUpdate();
}

/* Настройка PA0..PA7 как выходов push-pull 2 МГц, сброс линий в 0. */
static void R2R_Init(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;
    GPIOA->CRL = 0x22222222U; /* PA0..PA7: MODE=10 (2 МГц), CNF=00 (push-pull) */
    GPIOA->BSRR = 0x00FF0000U;
}

/* Одновременная установка восьми разрядов D7..D0 через регистр BSRR. */
static void R2R_Write(uint8_t code)
{
    uint32_t reset_mask = ((uint32_t)(~code) & 0xFFU) << 16;
    GPIOA->BSRR = reset_mask | (uint32_t)code;
}

/* Программная пауза на уже настроенном TIM2 (счётчик 1 кГц). */
static void Delay_ms(uint16_t ms)
{
    while (ms != 0U) {
        TIM2->SR &= ~TIM_SR_UIF;
        while ((TIM2->SR & TIM_SR_UIF) == 0U) { }
        ms--;
    }
}

/* Базовая настройка TIM2: тактирование, сброс, предделитель 1 кГц. */
static void TIM2_Base_Init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;
    TIM2->CR1 = 0U;
    TIM2->PSC = 7999U; /* 8 МГц / 8000 = 1 кГц */
    TIM2->CNT = 0U;
}

/* TIM2 как генератор пауз 1 мс (ARR = 0), прерывания не нужны. */
static void TIM2_Delay_Mode(void)
{
    TIM2->ARR = 0U;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->SR = 0U;
    TIM2->DIER = 0U;
    TIM2->CR1 = TIM_CR1_CEN;
}

/* TIM2 как генератор шага пилы: обновление каждые step_ms миллисекунд,
 * прерывание по обновлению разрешено. */
static void TIM2_Ramp_Init(uint16_t step_ms)
{
    if (step_ms == 0U) {
        step_ms = 1U;
    }
    TIM2->CR1 = 0U;
    TIM2->ARR = (uint32_t)step_ms - 1U; /* ARR = 9 при Tш = 10 мс */
    TIM2->CNT = 0U;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->SR = 0U;
    TIM2->DIER = TIM_DIER_UIE;
    NVIC_EnableIRQ(TIM2_IRQn);
    TIM2->CR1 = TIM_CR1_CEN;
}

/* Обработчик прерывания TIM2: следующий код пилы, полный цикл 256
 * ступеней, после кода 255 восьмиразрядная переменная переходит к 0. */
void TIM2_IRQHandler(void)
{
    if ((TIM2->SR & TIM_SR_UIF) != 0U) {
        TIM2->SR &= ~TIM_SR_UIF;
        dac_code++;
        R2R_Write(dac_code);
    }
}

int main(void)
{
    Clock_HSI8_Init();
    R2R_Init();
    TIM2_Base_Init();

    /* Индивидуальная часть: последовательное удержание кодов 76,
     * 133 и 207 для заполнения первых трёх строк таблицы 9.33. */
    TIM2_Delay_Mode();
    dac_code = (uint8_t)D1;
    R2R_Write(dac_code);
    Delay_ms(DWELL_MS);
    dac_code = (uint8_t)D2;
    R2R_Write(dac_code);
    Delay_ms(DWELL_MS);
    dac_code = (uint8_t)D3;
    R2R_Write(dac_code);
    Delay_ms(DWELL_MS);

    /* Непрерывная пила 0..255 с шагом Tш = 10 мс. */
    dac_code = 0U;
    R2R_Write(dac_code);
    TIM2_Ramp_Init(T_STEP_MS);
    __enable_irq();

    while (1) { }
}
