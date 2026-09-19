/**
 ******************************************************************************
 * ЛР №3. Генератор логических уровней
 * МК: STM32F407VGT6 (учебный стенд DIS_F407VG), код на регистрах CMSIS
 *
 * Схема подключения (объединённая финальная):
 *   свитчи SW1-SW4 -> РВ0-РВ3 (входы с внутренней подтяжкой вверх,
 *                             замыкание на GND = активный низкий уровень);
 *   сегменты a..g -> РА0-РА6;
 *   катоды разрядов -> РС0 (единицы), РС1 (десятки);
 *   светодиод -> РА7 (в методичке для опыта 2 используется РА0, но в
 *              объединённой схеме РА0 занят сегментом a).
 *
 * SysTick: 1 мс, глобальный счётчик millis() для планировщика задач
 * (мультиплексирование индикатора + антидребезг) без блокирующих задержек.
 *
 * Задание выбирается макросом TASK:
 *   0 - основная программа ЛР: светодиод повторяет SW1, на индикаторе
 *       устойчивый код SW1-SW4 (0-15);
 *   1 - переключатель-инвертор: LED меняет состояние при каждом нажатии SW1;
 *   2 - режимы LED по SW1+SW2: 00 выкл / 01 медленно / 10 быстро / 11 вкл;
 *   3 - счётчик нажатий SW1 (0-9) на индикаторе;
 *   4 - состояние SW1-SW4 как двоичное число на 4-х разрядах (РС0-РС3).
 ******************************************************************************
 */
#include "stm32f4xx.h"

#ifndef TASK
#define TASK 0
#endif

/* --- Периоды планировщика --- */
#define MUX_PERIOD_MS   2U          /* переключение разрядов (~250 Гц/разряд) */
#define POLL_DT_MS      2U          /* опрос свитчей */
#define DEBOUNCE_N      6U          /* 6 подтверждений * 2 мс = 12 мс стабильности */

/* --- Таблица кодов сегментов (общий катод, 1 = сегмент включён) --- */
static const uint8_t SEG_CODE[10] = {
    0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F
};

/* --- Глобальный счётчик миллисекунд (SysTick 1 мс) --- */
static volatile uint32_t g_ms = 0;

void SysTick_Handler(void)
{
    g_ms++;
}

static inline uint32_t millis(void)
{
    return g_ms;
}

/* --- Инициализация GPIO --- */
static void gpio_init(void)
{
    /* Тактирование портов A, B, C */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN
                  | RCC_AHB1ENR_GPIOBEN
                  | RCC_AHB1ENR_GPIOCEN;

    /* РА0-РА6 (сегменты) и РА7 (LED): выходы push-pull */
    for (int i = 0; i <= 7; i++) {
        GPIOA->MODER   &= ~(0x3U << (i * 2U));
        GPIOA->MODER   |=  (0x1U << (i * 2U));
        GPIOA->OTYPER  &= ~(1U   << i);
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2U));
        GPIOA->PUPDR   &= ~(0x3U << (i * 2U));
    }
    GPIOA->BSRR = (1U << 7U) << 16;     /* LED выключен (активный высокий) */

    /* РС0-РС3 (катоды разрядов): выходы, по умолчанию погашены (лог.1) */
    for (int i = 0; i <= 3; i++) {
        GPIOC->MODER   &= ~(0x3U << (i * 2U));
        GPIOC->MODER   |=  (0x1U << (i * 2U));
        GPIOC->OTYPER  &= ~(1U   << i);
        GPIOC->OSPEEDR &= ~(0x3U << (i * 2U));
        GPIOC->PUPDR   &= ~(0x3U << (i * 2U));
    }
    GPIOC->BSRR = 0x000FU;              /* все разряды off */

    /* РВ0-РВ3 (свитчи): входы с подтяжкой вверх */
    for (int i = 0; i <= 3; i++) {
        GPIOB->MODER &= ~(0x3U << (i * 2U));        /* 00 = вход */
        GPIOB->PUPDR &= ~(0x3U << (i * 2U));
        GPIOB->PUPDR |=  (0x1U << (i * 2U));        /* 01 = pull-up */
    }
}

/* --- Индикатор: вывод кода на сегменты РА0-РА6 --- */
static inline void seg_write(uint8_t code)
{
    GPIOA->ODR = (GPIOA->ODR & ~0x007FU) | (code & 0x7FU);
}

/* --- Индикатор: включить один разряд (катод = 0), остальные погасить ---
 * idx = 0 -> РС0 (младший/правый), 1 -> РС1, 2 -> РС2, 3 -> РС3.
 * Одна атомарная запись: 1 на все катоды, КРОМЕ выбранного (off),
 * 0 на выбранный (on). BSx выбранного бита не ставим — по RM0090 §8.4.7
 * при одновременном BSx и BRx приоритет у BSx, и разряд не включился бы.
 * Порядок "all off -> on" внутри одной записи BSRR исключает "смазывание"
 * разрядов (см. контр. вопрос 4). */
static inline void digit_enable(uint8_t idx)
{
    uint32_t on = (1U << idx);
    GPIOC->BSRR = (0x000FU & ~on)  /* все катоды -> 1 (off), кроме выбранного */
                | (on << 16);      /* выбранный катод -> 0 (on)              */
}

/* --- Антидребезг: подтверждение нового значения N одинаковых
 *     выборок с интервалом POLL_DT_MS. Возвращает 1, если устойчивое
 *     значение обновилось. --- */
static uint8_t g_stable;    /* последнее устойчивое значение */
static uint8_t g_last;      /* предыдущая выборка */
static uint8_t g_count;     /* счётчик совпадений */

static uint8_t debounce_poll(void)
{
    /* Активный низкий уровень -> инвертируем биты РВ0-РВ3 */
    uint8_t raw = (uint8_t)(~GPIOB->IDR) & 0x0FU;

    if (raw == g_last) {
        if (g_count < DEBOUNCE_N) {
            g_count++;
            if (g_count == DEBOUNCE_N && g_stable != raw) {
                g_stable = raw;
                return 1;
            }
        }
    } else {
        g_last  = raw;
        g_count = 0;
    }
    return 0;
}

/* --- Служебные состояния дисплея --- */
static uint8_t g_disp[4] = {0, 0, 0, 0};  /* цифры для 4 разрядов */
static uint8_t g_mux_idx = 0;             /* текущий разряд */

/* Обновить дисплей: вывести число 0-15 на двух разрядах (РС1:РС0) */
static inline void display_u8(uint8_t value)
{
    g_disp[0] = SEG_CODE[value % 10U];
    g_disp[1] = SEG_CODE[value / 10U];
}

/* Планировщик: мультиплексирование разрядов, вызывать из главного цикла */
static void mux_scheduler(void)
{
    static uint32_t t_next = 0;
    uint32_t now = millis();
    if ((int32_t)(now - t_next) >= 0) {
        t_next += MUX_PERIOD_MS;
        seg_write(g_disp[g_mux_idx]);
        digit_enable(g_mux_idx);
        g_mux_idx ^= 1U;                /* 0 <-> 1 (два разряда) */
    }
}

int main(void)
{
    gpio_init();

    /* SysTick: прерывание каждую 1 мс */
    SysTick_Config(SystemCoreClock / 1000U);

#if TASK == 0
    /* === Основная программа ЛР ===
     * Опыт 2: светодиод (РА7) горит, пока SW1 (РВ0) замкнут;
     * Опыт 3: на индикаторе устойчивое значение кода SW1-SW4 (0-15). */
    uint8_t value = 0;
    display_u8(0);
    while (1) {
        mux_scheduler();

        static uint32_t t_poll = 0;
        uint32_t now = millis();
        if ((int32_t)(now - t_poll) >= 0) {
            t_poll += POLL_DT_MS;
            if (debounce_poll()) {
                value = g_stable;
                display_u8(value);
            }
            /* LED повторяет SW1 (бит0 устойчивого значения) */
            if (value & 0x01U) {
                GPIOA->BSRR = (1U << 7U);           /* LED on  */
            } else {
                GPIOA->BSRR = (1U << 7U) << 16;     /* LED off */
            }
        }
    }

#elif TASK == 1
    /* === Задание 1: переключатель-инвертор ===
     * Каждое нажатие SW1 (РВ0) меняет состояние LED (РА7).
     * Фронт нажатия выделяем по появлению бита в устойчивом значении. */
    uint8_t prev = 0;
    uint8_t led = 0;
    display_u8(0);
    while (1) {
        mux_scheduler();
        static uint32_t t_poll = 0;
        if ((int32_t)(millis() - t_poll) >= 0) {
            t_poll += POLL_DT_MS;
            if (debounce_poll()) {
                uint8_t pressed = g_stable & ~prev; /* фронт нажатия */
                if (pressed & 0x01U) {
                    led ^= 1U;
                    if (led) {
                        GPIOA->BSRR = (1U << 7U);
                    } else {
                        GPIOA->BSRR = (1U << 7U) << 16;
                    }
                }
                prev = g_stable;
                display_u8(g_stable);
            }
        }
    }

#elif TASK == 2
    /* === Задание 2: режимы LED по SW1+SW2 ===
     * SW2 SW1: 00 - выключен; 01 - медленное мигание (500 мс);
     *          10 - быстрое мигание (100 мс); 11 - постоянно включён. */
    display_u8(0);
    while (1) {
        mux_scheduler();
        static uint32_t t_poll = 0;
        if ((int32_t)(millis() - t_poll) >= 0) {
            t_poll += POLL_DT_MS;
            debounce_poll();
            display_u8(g_stable);
        }
        uint8_t mode = g_stable & 0x03U;
        static uint32_t t_blink = 0;
        static uint8_t led = 0;
        switch (mode) {
        case 0x0:                                   /* 00 - выкл */
            GPIOA->BSRR = (1U << 7U) << 16;
            break;
        case 0x1:                                   /* 01 - медленно */
        case 0x2:                                   /* 10 - быстро   */
            if ((int32_t)(millis() - t_blink) >= 0) {
                t_blink += (mode == 0x1) ? 500U : 100U;
                led ^= 1U;
                GPIOA->BSRR = led ? (1U << 7U) : ((1U << 7U) << 16);
            }
            break;
        default:                                    /* 11 - вкл */
            GPIOA->BSRR = (1U << 7U);
            break;
        }
    }

#elif TASK == 3
    /* === Задание 3: счётчик нажатий SW1 (0-9) на индикаторе === */
    uint8_t count = 0;
    uint8_t prev = 0;
    display_u8(0);
    while (1) {
        mux_scheduler();
        static uint32_t t_poll = 0;
        if ((int32_t)(millis() - t_poll) >= 0) {
            t_poll += POLL_DT_MS;
            if (debounce_poll()) {
                uint8_t pressed = g_stable & ~prev;
                if (pressed & 0x01U) {
                    count = (count + 1U) % 10U;     /* после 9 - сброс в 0 */
                    display_u8(count);
                }
                prev = g_stable;
            }
        }
    }

#elif TASK == 4
    /* === Задание 4: состояние SW1-SW4 как двоичное число
     *     на 4-разрядном индикаторе (РС0-РС3, мл. разряд справа) === */
    while (1) {
        /* Мультиплексирование 4 разрядов */
        static uint32_t t_mux = 0;
        uint32_t now = millis();
        if ((int32_t)(now - t_mux) >= 0) {
            t_mux += MUX_PERIOD_MS;
            static uint8_t idx = 0;
            seg_write(g_disp[idx]);
            digit_enable(idx);
            idx = (idx + 1U) & 0x03U;
        }

        static uint32_t t_poll = 0;
        if ((int32_t)(now - t_poll) >= 0) {
            t_poll += POLL_DT_MS;
            debounce_poll();
            /* Каждый разряд показывает один бит кода: 0 или 1 */
            for (uint8_t i = 0; i < 4; i++) {
                g_disp[i] = SEG_CODE[(g_stable >> i) & 0x01U];
            }
        }
    }
#else
#error "Неверный TASK: допустимы 0-4"
#endif
}
