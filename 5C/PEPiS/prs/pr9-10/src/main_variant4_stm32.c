/*====================================================================
 * Практическая работа № 5 «Отображение информации в
 * микроконтроллерных системах» (пр9-10, Proteus),
 * ИНДИВИДУАЛЬНЫЙ ВАРИАНТ 4 (табл. 9.26 методички) для STM32F103C8:
 * последовательная смена четырёх цифр по событию таймера.
 *
 * Параметры варианта 4:
 *   цифры        — 9-8-7-6;
 *   порядок      — обратный (индекс уменьшается, после нулевого
 *                  элемента принимает значение 3): на индикаторе
 *                  последовательность 9, 6, 7, 8, 9, 6, ...;
 *   T_симв       — 400 мс (интервал события таймера);
 *   диагностика  — применить инвертированный код (при неизменном
 *                  индикаторе общего катода все сегменты светятся
 *                  инверсно: нечитаемый символ).
 *
 * Таймер — TIM2 по методике работы 9.3: HSI 8 МГц, APB1 без
 * делителя, TIM2CLK = 8 МГц; PSC = 7999 (отсчёт 1 кГц, 1 мс),
 * ARR = 399 -> событие обновления каждые 400 мс. Программная
 * задержка в пустом цикле не применяется. Обработчик TIM2_IRQHandler
 * устанавливает флаг display_event, а основной цикл выводит
 * следующий элемент массива (листинг 9.15).
 *
 * Порядок проверки по методике: сначала выводятся цифры 0, 8 и
 * одна цифра варианта (9) — каждая в течение одного интервала
 * T_симв (стартовая самопроверка), затем начинается цикл варианта.
 *
 * Сборка: PlatformIO с фреймворком CMSIS (см. platformio.ini).
 * Результат (.elf/.hex) указывается в поле Program File модели
 * STM32F103C8 в Proteus 8.17.
 *====================================================================*/
#include "stm32f1xx.h"
#include <stdint.h>

#define CLOCK_TIMEOUT 1000000U /* тайм-аут ожидания готовности HSI */

/* Диагностическое изменение варианта 4: «применить инвертированный
 * код». 0 — нормальный режим (индикатор общего катода, прямые коды);
 * 1 — код цифры инвертируется в пределах восьми младших битов, как
 * для индикатора с общим анодом. При неизменной схеме (общий катод)
 * изображение становится инверсным и нечитаемым. После наблюдения
 * вернуть 0 и пересобрать — параметры восстановятся. */
#define DISPLAY_INVERTED_CODE 0

/* T_симв = 400 мс: PSC = 7999 -> 1 мс на отсчёт, ARR = 399. */
#define DISPLAY_INTERVAL_MS 400U
#define TIM2_PSC_VALUE      7999U
#define TIM2_ARR_VALUE      (DISPLAY_INTERVAL_MS - 1U) /* 399 */

/* Индивидуальный вариант 4: цифры 9-8-7-6, порядок обратный. */
static const uint8_t sequence[4] = {9U, 8U, 7U, 6U};
static volatile uint8_t display_event; /* флаг задаёт обработчик TIM2 */

/* Таблица кодов цифр для индикатора с ОБЩИМ КАТОДОМ:
 * младший бит — сегмент a, бит 6 — сегмент g, бит 7 — dp. */
static const uint8_t segment_code_cc[10] = {
    0x3FU, 0x06U, 0x5BU, 0x4FU, 0x66U,
    0x6DU, 0x7DU, 0x07U, 0x7FU, 0x6FU
};

static uint8_t Clock_Init_HSI8MHz(void)
{
    uint32_t timeout = CLOCK_TIMEOUT;

    /* HSI 8 МГц без PLL: источником SYSCLK уже является HSI
     * после сброса, поэтому здесь только контроль готовности. */
    RCC->CR |= RCC_CR_HSION;
    while ((RCC->CR & RCC_CR_HSIRDY) == 0U) {
        if (--timeout == 0U) {
            return 1U; /* HSI не запустился */
        }
    }
    RCC->CFGR &= ~RCC_CFGR_SW;     /* SYSCLK = HSI */
    RCC->CFGR &= ~RCC_CFGR_PPRE1;  /* APB1 без делителя */
    RCC->CFGR &= ~RCC_CFGR_PPRE2;  /* APB2 без делителя */
    return 0U;
}

static void Display_Init(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;

    /* PA0–PA7: выход push-pull, частота до 2 МГц. */
    GPIOA->CRL = 0x22222222U;

    /* Начальное состояние всех линий — низкий уровень. */
    GPIOA->BSRR = 0x00FF0000U;
}

static void Display_WriteCode(uint8_t code)
{
    uint32_t set_mask = (uint32_t)code;
    uint32_t reset_mask = ((uint32_t)(~code) & 0xFFU) << 16;

    GPIOA->BSRR = reset_mask | set_mask;
}

static void Display_Digit(uint8_t digit)
{
    uint8_t code = 0U;

    if (digit < 10U) {
        code = segment_code_cc[digit];
    }

#if DISPLAY_INVERTED_CODE
    /* Диагностика варианта 4: инвертированный код. Для индикатора
     * с общим катодом вместо цифры отображается инверсный рисунок
     * (светятся сегменты, которые должны быть погашены). */
    code = (uint8_t)(~code);
#endif

    Display_WriteCode(code);
}

/* TIM2 по методике работы 9.3: PSC = 7999, ARR = 399 -> 400 мс. */
static uint8_t TIM2_DisplayEventInit(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    TIM2->CR1 = 0U;
    TIM2->PSC = TIM2_PSC_VALUE;
    TIM2->ARR = TIM2_ARR_VALUE;
    TIM2->EGR = TIM_EGR_UG;      /* загрузить PSC/ARR немедленно */
    TIM2->SR = 0U;               /* сбросить флаги */
    TIM2->DIER |= TIM_DIER_UIE;  /* прерывание по обновлению */
    NVIC_EnableIRQ(TIM2_IRQn);
    TIM2->CR1 |= TIM_CR1_CEN;    /* запуск счётчика */
    return 0U;
}

void TIM2_IRQHandler(void)
{
    if ((TIM2->SR & TIM_SR_UIF) != 0U) {
        TIM2->SR = (uint32_t)~TIM_SR_UIF; /* сброс флага записью 0 */
        display_event = 1U;
    }
}

int main(void)
{
    uint8_t index = 0U;
    /* Стартовая самопроверка по методике: цифры 0, 8 и цифра
     * варианта 9 — каждая в течение одного интервала T_симв. */
    static const uint8_t selftest[3] = {0U, 8U, 9U};
    uint8_t stage = 0U;

    (void)Clock_Init_HSI8MHz();
    Display_Init();
    TIM2_DisplayEventInit();

    while (1) {
        if (display_event != 0U) {
            display_event = 0U;

            if (stage < 3U) {
                Display_Digit(selftest[stage]);
                stage++;
            } else {
                /* Обратный порядок: индекс уменьшается, после
                 * нулевого элемента принимает значение 3. */
                Display_Digit(sequence[index]);
                if (index == 0U) {
                    index = 3U;
                } else {
                    index--;
                }
            }
        }
    }
}
