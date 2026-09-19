/**
 ******************************************************************************
 * ЛР №2. Порты ввода/вывода. Управление семисегментным индикатором
 * МК: STM32F407VGT6 (учебный стенд DIS_F407VG), код на регистрах CMSIS
 *
 * Схема подключения:
 *   сегменты a..g -> РА0-РА6 (бит0=a, бит1=b, ... бит6=g);
 *   общие катоды 4 разрядов -> РС0-РС3 (активный низкий уровень);
 *   внешний управляющий сигнал (генератор/свитч) -> РВ0 (вход с pull-up).
 *
 * Программа: динамическая индикация 4-разрядного числа. Значение
 * переключается внешним сигналом (задание 7):
 *   РВ0 = 1 -> YEAR_CURRENT (текущий год), РВ0 = 0 -> YEAR_BIRTH.
 ******************************************************************************
 */
#include "stm32f4xx.h"

/* Отображаемые значения (задание: год рождения <-> текущий год) */
#define YEAR_BIRTH   2000U
#define YEAR_CURRENT 2025U

/* Задание 5.2: показывать десятичную точку (сегмент DP на РА7)
 * после старшего разряда (например, "2.025") */
#define SHOW_DP 1

/* Задание 5.3: 0 - отображение года (переключение по РВ0);
 *              1 - счётчик секунд с момента включения */
#define SECONDS_COUNTER 0

/* Таблица кодов сегментов для общего катода (1 = сегмент включён):
 * биты 0..6 = a,b,c,d,e,f,g */
static const uint8_t SEG_CODE[10] = {
    0x3F, /* 0: a b c d e f    */
    0x06, /* 1:       b c      */
    0x5B, /* 2: a b   d e   g  */
    0x4F, /* 3: a b c d      g */
    0x66, /* 4:     c     f  g */
    0x6D, /* 5: a   c d   f  g */
    0x7D, /* 6: a   c d e f  g */
    0x07, /* 7: a b c          */
    0x7F, /* 8: a b c d e f  g */
    0x6F  /* 9: a b c d   f  g */
};

/* Программная задержка (HSI = 16 МГц) */
void delay(volatile uint32_t t)
{
    while (t--) {
        __NOP();
    }
}

/* Инициализация GPIO: сегменты, катоды разрядов, вход РВ0 */
static void gpio_init(void)
{
    /* Тактирование портов A, B, C (шина AHB1) */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN
                  | RCC_AHB1ENR_GPIOBEN
                  | RCC_AHB1ENR_GPIOCEN;

    /* РА0-РА6: выходы push-pull, низкая скорость, без подтяжек */
    for (int i = 0; i <= 6; i++) {
        GPIOA->MODER   &= ~(0x3U << (i * 2U));
        GPIOA->MODER   |=  (0x1U << (i * 2U));  /* 01 = выход */
        GPIOA->OTYPER  &= ~(1U   << i);         /* push-pull  */
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2U));  /* низкая скорость */
        GPIOA->PUPDR   &= ~(0x3U << (i * 2U));  /* без подтяжки */
    }
    GPIOA->ODR &= ~0x007FU;                     /* все сегменты погашены */

#if SHOW_DP
    /* Задание 5.2: РА7 — выход для сегмента DP (десятичной точки) */
    GPIOA->MODER   &= ~(0x3U << (7U * 2U));
    GPIOA->MODER   |=  (0x1U << (7U * 2U));
    GPIOA->OTYPER  &= ~(1U << 7U);
    GPIOA->OSPEEDR &= ~(0x3U << (7U * 2U));
    GPIOA->PUPDR   &= ~(0x3U << (7U * 2U));
    GPIOA->BSRR = (1U << (7U + 16U));           /* точка погашена */
#endif

    /* РС0-РС3: выходы (катоды разрядов), по умолчанию погашены */
    for (int i = 0; i <= 3; i++) {
        GPIOC->MODER   &= ~(0x3U << (i * 2U));
        GPIOC->MODER   |=  (0x1U << (i * 2U));
        GPIOC->OTYPER  &= ~(1U   << i);
        GPIOC->OSPEEDR &= ~(0x3U << (i * 2U));
        GPIOC->PUPDR   &= ~(0x3U << (i * 2U));
    }
    /* Катод активен нулём: подать 1 на РС0-РС3 -> все разряды выключены */
    GPIOC->BSRR = 0x000FU;

    /* РВ0: вход с подтяжкой вверх (внешний управляющий сигнал) */
    GPIOB->MODER &= ~(0x3U << (0U * 2U));       /* 00 = вход */
    GPIOB->PUPDR &= ~(0x3U << (0U * 2U));
    GPIOB->PUPDR |=  (0x1U << (0U * 2U));       /* 01 = pull-up */
}

/* === Этап 2 (статическая индикация): вывод одной цифры на разряд.
 * В финальной программе не вызывается, оставлено для отчёта ЛР. === */
static void show_digit_static(uint8_t digit, uint8_t cathode_pin)
{
    GPIOA->ODR = (GPIOA->ODR & ~0x007FU) | (SEG_CODE[digit] & 0x7FU);
    /* Катод активен низким уровнем: включение разряда — СБРОС через
     * старшую половину BSRR (младшая половина поставила бы 1 = off) */
    GPIOC->BSRR = (1U << (cathode_pin + 16U));    /* РСх = 0 -> разряд on */
}

/* === Этап 4 (динамическая индикация): показать цифру idx на
 * небольшое время, предварительно погасив все разряды. === */
static void mux_digit(const uint8_t digits[4], uint8_t pos)
{
    /* 1. Погасить все разряды: катод активен низким уровнем,
     *    поэтому "off" = лог.1 на РС0-РС3 (младшая половина BSRR) */
    GPIOC->BSRR = 0x000FU;                      /* все разряды off */

    /* 2. Код цифры на сегменты РА0-РА6, точка DP — задание 5.2 */
    uint8_t code = SEG_CODE[digits[pos]];
    GPIOA->ODR = (GPIOA->ODR & ~0x007FU) | (code & 0x7FU);
#if SHOW_DP
    /* Точка горит в старшем разряде (pos == 3) */
    if (pos == 3U) {
        GPIOA->BSRR = (1U << 7U);               /* DP on  (РА7 = 1) */
    } else {
        GPIOA->BSRR = (1U << (7U + 16U));       /* DP off */
    }
#endif

    /* 3. Включить нужный разряд (катод = 0, старшая половина BSRR) */
    GPIOC->BSRR = (1U << (pos + 16U));          /* РС(pos) = 0 -> on */

    /* 4. Время свечения разряда (~1 мс -> ~250 Гц на разряд) */
    delay(2000);
}

#if SECONDS_COUNTER
/* Счётчик миллисекунд для задания 5.3 (SysTick 1 мс) */
static volatile uint32_t g_ms = 0;

void SysTick_Handler(void)
{
    g_ms++;
}

static inline uint32_t millis(void)
{
    return g_ms;
}
#endif

/* Разбор числа 0-9999 на 4 десятичные цифры */
static void split_number(uint16_t value, uint8_t digits[4])
{
    for (int i = 3; i >= 0; i--) {
        digits[i] = (uint8_t)(value % 10U);
        value /= 10U;
    }
}

int main(void)
{
    gpio_init();

#if SECONDS_COUNTER
    /* Задание 5.3: SysTick 1 мс для счётчика секунд */
    SysTick_Config(SystemCoreClock / 1000U);
#endif

    uint8_t digits[4] = {0, 0, 0, 0};

    /* Демонстрация статической индикации (этап 2): цифра 5 на РС0,
     * горит ~3 с до старта динамической индикации */
    show_digit_static(5, 0);
    delay(15000000);

    while (1) {
#if SECONDS_COUNTER
        /* Задание 5.3: счётчик секунд с момента включения */
        uint16_t number = (uint16_t)((millis() / 1000U) % 10000U);
#else
        /* Задание 7: переключение отображаемого значения по РВ0 */
        uint16_t number = (GPIOB->IDR & (1U << 0U)) ? YEAR_CURRENT : YEAR_BIRTH;
#endif

        split_number(number, digits);

        /* Динамическая индикация: последовательный перебор разрядов */
        for (uint8_t pos = 0; pos < 4; pos++) {
            mux_digit(digits, pos);
        }
    }
}
