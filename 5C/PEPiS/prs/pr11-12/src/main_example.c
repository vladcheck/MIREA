/*====================================================================
 * Практическая работа № 11-12 «Исследование цифро-аналогового
 * преобразования на матрице R-2R» (учебная работа № 6 методички).
 * Платформа STM32F103C8, порт матрицы PA0..PA7, питание 3,3 В.
 *
 * Учебный пример (листинг 9.17 методички): постоянный код TEST_CODE
 * на выходах PA0..PA7 и пилообразный сигнал средствами таймера TIM2.
 *
 * Обязательная общая часть (п. 7 методички) требует последовательно
 * подать коды 0, 64, 128, 192 и 255; по методичке допустимо либо
 * пересобирать проект для каждого кода, либо временно организовать
 * последовательную выдачу кодов. Ниже выбран второй способ:
 * после удержания TEST_CODE программа циклически выдаёт коды
 * 0, 64, 128, 192, 255 с паузой DWELL_MS на каждый код, поэтому все
 * пять проверок выполняются за один запуск моделирования.
 *
 * Тактирование: HSI 8 МГц без PLL (по методичке), TIM2: PSC = 7999,
 * счётчик 1 кГц, период 1 мс.
 *====================================================================*/
#include "stm32f1xx.h"
#include <stdint.h>

#define TEST_CODE 128U  /* постоянный код учебного примера, D = 128 */
#define DWELL_MS  2000U /* удержание каждого кода общей части, мс */

static volatile uint8_t dac_code = 0U;

/* Массив кодов обязательной общей части, таблица 9.32 методички. */
static const uint8_t general_codes[5] = { 0U, 64U, 128U, 192U, 255U };

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

/* TIM2 как генератор пауз 1 мс: PSC = 7999, ARR = 0, обновление
 * каждую миллисекунду; прерывания не используются. */
static void TIM2_Delay_Init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;
    TIM2->CR1 = 0U;
    TIM2->PSC = 7999U; /* 8 МГц / 8000 = 1 кГц */
    TIM2->ARR = 0U;    /* обновление каждый тик, период 1 мс */
    TIM2->CNT = 0U;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->SR = 0U;
    TIM2->CR1 = TIM_CR1_CEN;
}

int main(void)
{
    uint32_t i;

    Clock_HSI8_Init();
    R2R_Init();
    TIM2_Delay_Init();

    /* Учебный пример: постоянный код на матрице R-2R. */
    dac_code = (uint8_t)TEST_CODE;
    R2R_Write(dac_code);

    /* Общая часть: циклическая последовательная выдача кодов
     * 0, 64, 128, 192, 255 с удержанием DWELL_MS на каждый код. */
    while (1) {
        for (i = 0U; i < (uint32_t)sizeof general_codes; i++) {
            dac_code = general_codes[i];
            R2R_Write(dac_code);
            Delay_ms(DWELL_MS);
        }
    }
}
