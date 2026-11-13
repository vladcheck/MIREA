/* Минимальный стуб CMSIS-заголовка stm32f1xx.h для синтаксической
 * проверки исходников командой `clang -fsyntax-only` прямо на macOS,
 * без установки ARM-тулчейна. Определения соответствуют RM0008
 * (порядок полей структур совпадает с порядком адресов регистров).
 * В реальной прошивке PlatformIO (framework = cmsis) этот файл не
 * используется: там подключается штатный заголовок CMSIS.
 */
#ifndef STUB_STM32F1XX_H
#define STUB_STM32F1XX_H

#include <stdint.h>

#define __IO volatile

/* --- Структуры регистров --- */

/* RCC, базовый адрес 0x4002 1000 (RM0008, таблица 3) */
typedef struct
{
    __IO uint32_t CR;       /* 0x00: регистр управления тактированием */
    __IO uint32_t CFGR;     /* 0x04: конфигурация тактирования */
    __IO uint32_t CIR;      /* 0x08: регистр прерываний */
    __IO uint32_t APB2RSTR; /* 0x0C: сброс устройств APB2 */
    __IO uint32_t APB1RSTR; /* 0x10: сброс устройств APB1 */
    __IO uint32_t APB2ENR;  /* 0x14: тактирование устройств APB2 */
    __IO uint32_t APB1ENR;  /* 0x18: тактирование устройств APB1 */
} RCC_TypeDef;

/* GPIO, базовый адрес GPIOA 0x4001 0800 (RM0008, таблица 3) */
typedef struct
{
    __IO uint32_t CRL;  /* 0x00: конфигурация выводов 0..7 */
    __IO uint32_t CRH;  /* 0x04: конфигурация выводов 8..15 */
    __IO uint32_t IDR;  /* 0x08: входные данные */
    __IO uint32_t ODR;  /* 0x0C: выходные данные */
    __IO uint32_t BSRR; /* 0x10: установка/сброс битов */
    __IO uint32_t BRR;  /* 0x14: сброс битов */
    __IO uint32_t LCKR; /* 0x18: блокировка конфигурации */
} GPIO_TypeDef;

/* TIM2..TIM4, базовый адрес TIM2 0x4000 0000 (RM0008, таблица 3) */
typedef struct
{
    __IO uint32_t CR1;  /* 0x00: управление 1 */
    __IO uint32_t CR2;  /* 0x04: управление 2 */
    __IO uint32_t SMCR; /* 0x08: режим ведомого устройства */
    __IO uint32_t DIER; /* 0x0C: разрешение прерываний/DMA */
    __IO uint32_t SR;   /* 0x10: состояние */
    __IO uint32_t EGR;  /* 0x14: генерация событий */
    __IO uint32_t CCMR1;/* 0x18: режим захвата/сравнения 1 */
    __IO uint32_t CCMR2;/* 0x1C: режим захвата/сравнения 2 */
    __IO uint32_t CCER; /* 0x20: разрешение захвата/сравнения */
    __IO uint32_t CNT;  /* 0x24: счётчик */
    __IO uint32_t PSC;  /* 0x28: предделитель */
    __IO uint32_t ARR;  /* 0x2C: регистр автоперезагрузки */
} TIM_TypeDef;

#define RCC   ((RCC_TypeDef  *)0x40021000U) /* RM0008: 0x4002 1000 */
#define GPIOA ((GPIO_TypeDef *)0x40010800U) /* RM0008: 0x4001 0800 */
#define TIM2  ((TIM_TypeDef  *)0x40000000U) /* RM0008: 0x4000 0000 */

/* --- RCC_CR --- */
#define RCC_CR_HSION  (1U << 0)  /* 0x00000001: вкл. внутр. генератора HSI */
#define RCC_CR_HSIRDY (1U << 1)  /* 0x00000002: HSI готов */

/* --- RCC_CFGR --- */
#define RCC_CFGR_SW      (3U << 0)  /* 0x00000003: выбор системной частоты */
#define RCC_CFGR_SW_HSI  (0U << 0)  /* 0x00000000: источник = HSI */
#define RCC_CFGR_SWS     (3U << 2)  /* 0x0000000C: фактический SYSCLK */
#define RCC_CFGR_SWS_HSI (0U << 2)  /* 0x00000000: факт. источник = HSI */
#define RCC_CFGR_HPRE    (15U << 4) /* 0x000000F0: делитель AHB */
#define RCC_CFGR_PPRE1   (7U << 8)  /* 0x00000700: делитель APB1 */
#define RCC_CFGR_PPRE2   (7U << 11) /* 0x00003800: делитель APB2 */

/* --- RCC_APB2ENR --- */
#define RCC_APB2ENR_IOPAEN (1U << 2) /* 0x00000004: тактирование GPIOA */

/* --- RCC_APB1ENR --- */
#define RCC_APB1ENR_TIM2EN (1U << 0) /* 0x00000001: тактирование TIM2 */

/* --- GPIO_CRL: поля MODEy[1:0]/CNFy[1:0] для выводов 0..7 --- */
/* Значение 0x2 в MODEy: выход 2 МГц; 0x0 в CNFy: push-pull. */
#define GPIO_CRL_OUT_2MHZ_PP 0x2U /* режим одного вывода в CRL/CRH */

/* --- TIM2 CR1 --- */
#define TIM_CR1_CEN (1U << 0) /* 0x0001: разрешение счёта */

/* --- TIM2 DIER --- */
#define TIM_DIER_UIE (1U << 0) /* 0x0001: прерывание по обновлению */

/* --- TIM2 SR --- */
#define TIM_SR_UIF (1U << 0) /* 0x0001: флаг обновления */

/* --- TIM2 EGR --- */
#define TIM_EGR_UG (1U << 0) /* 0x0001: генерация события обновления */

/* --- NVIC --- */
typedef enum
{
    TIM2_IRQn = 28 /* глобальное прерывание TIM2, номер 28 (RM0008, таблица 63) */
} IRQn_Type;

/* Заглушки функций CMSIS: на хосте они ничего не делают,
 * в реальной прошивке их предоставляет CMSIS core_cm3.h. */
static inline void NVIC_EnableIRQ(IRQn_Type irq)
{
    (void)irq;
}

static inline void __enable_irq(void)
{
}

/* Переменная состояния CMSIS, обновляемая SystemCoreClockUpdate(). */
extern uint32_t SystemCoreClock;
void SystemCoreClockUpdate(void);

#endif /* STUB_STM32F1XX_H */
