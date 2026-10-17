/*====================================================================
 * ПР №5-6, ИНДИВИДУАЛЬНЫЙ ВАРИАНТ 4 (табл. 9.9 методички, Proteus) —
 * последовательная проверка интервалов TIM2 на STM32F103C8
 * (HSI 8 МГц, TIM2CLK = 8 МГц, PSC = 7999 → 1 мс на отсчёт).
 *
 * Вариант 4: T1 = 80 мс (ARR = 79), T2 = 40 мс (ARR = 39),
 * диагностическое изменение ARR+100 → ARR = 139 (интервал 140 мс).
 *
 * Фазы эксперимента (в каждой фазе — 8 событий обновления, то есть
 * 7 расстояний между соседними фронтами; требуется не менее пяти):
 *   базовая часть — 250 мс (PSC = 7999, ARR = 249);
 *   T1 = 80 мс — ARR = 79;
 *   T2 = 40 мс — только смена ARR (ARR = 39);
 *   диагностика — ARR+100 (ARR = 39 + 100 = 139 → интервал 140 мс);
 *   восстановление — ARR = 39, подтверждение возврата T2.
 *
 * Внутри программы интервал контролируется счётчиком g_interval_ms,
 * который в фазе диагностики фиксирует значение 140 мс — проявление
 * неисправности (интервал вырос в 3,5 раза вместо 40 мс).
 *
 * PA1 — обычный двухтактный выход GPIO (не TIM2_CH2): в обработчике
 * состояние инвертируется, расстояние между соседними фронтами равно
 * интервалу таймера, полный период меандра — двум интервалам.
 *
 * Сборка: PlatformIO, CMSIS (stm32f1xx.h).
 *====================================================================*/
#include "stm32f1xx.h"

#define CLOCK_TIMEOUT       1000000U
#define TIMER_INTERVAL_MS   250U   /* базовая часть */
#define T1_INTERVAL_MS       80U   /* вариант 4: T1 */
#define T2_INTERVAL_MS       40U   /* вариант 4: T2 */
#define DIAG_ARR_OFFSET     100U   /* вариант 4: диагностическое ARR+100 */
#define EVENTS_PER_PHASE      8U   /* ≥ 6 событий → ≥ 5 измеряемых расстояний */

/* Значения ARR после каждого перехода фазы; PSC = 7999 постоянен во
 * всех фазах, поэтому интервал меняется только записью ARR. */
static const uint16_t g_phase_arr[] = {
    (uint16_t)(T1_INTERVAL_MS - 1U),                   /* ARR = 79 → 80 мс */
    (uint16_t)(T2_INTERVAL_MS - 1U),                   /* ARR = 39 → 40 мс */
    (uint16_t)(T2_INTERVAL_MS - 1U + DIAG_ARR_OFFSET), /* ARR = 139 → 140 мс */
    (uint16_t)(T2_INTERVAL_MS - 1U)                    /* ARR = 39 → 40 мс */
};
#define PHASE_TRANSITIONS (sizeof(g_phase_arr) / sizeof(g_phase_arr[0]))

volatile uint32_t g_update_count;    /* всего событий обновления TIM2 */
volatile uint32_t g_phase_count;     /* событий обновления в текущей фазе */
volatile uint32_t g_interval_ms;     /* текущий интервал, мс (ARR + 1) */
volatile uint32_t g_experiment_done; /* 1 — все фазы эксперимента пройдены */

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

    g_update_count = 0U;
    g_phase_count = 0U;
    g_interval_ms = interval_ms;

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
        ++g_phase_count;
    }
}

int main(void)
{
    uint32_t next_phase = 0U; /* индекс перехода в таблице g_phase_arr */

    if (!Clock_Init_HSI8MHz()) while (1) { }
    if (!TIM2_IntervalInit(TIMER_INTERVAL_MS)) while (1) { }

    /* После EVENTS_PER_PHASE событий обновления текущей фазы выполняется
     * переход к следующей фазе — только записью нового ARR. Запись
     * производится сразу после события обновления (задержка порядка
     * микросекунд), поэтому новый интервал начинается с целого периода. */
    while (g_experiment_done == 0U) {
        __WFI();
        if (g_phase_count < EVENTS_PER_PHASE) continue;

        g_phase_count = 0U;
        if (next_phase >= PHASE_TRANSITIONS) {
            /* Финальная фаза завершена: интервал T2 восстановлен
             * и подтверждён после диагностического изменения. */
            g_experiment_done = 1U;
            continue;
        }

        TIM2->ARR = g_phase_arr[next_phase];
        g_interval_ms = (uint32_t)g_phase_arr[next_phase] + 1U;
        ++next_phase;
    }

    /* Эксперимент завершён: таймер продолжает формировать интервал T2,
     * PA1 продолжает инвертироваться; счётчики доступны в отладчике. */
    while (1) {
        __WFI();
    }
}
