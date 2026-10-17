/* Минимальный стуб CMSIS-заголовка stm32f1xx.h для синтаксической
 * проверки исходников `clang -fsyntax-only` прямо на macOS, без
 * ARM-тулчейна. Это ЗАГЛУШКА, а не настоящий CMSIS: здесь описаны
 * только те периферийные регистры, битовые маски и функции NVIC,
 * которые реально используются в src/main_example.c и
 * src/main_variant4.c.
 *
 * Настоящая прошивка собирается PlatformIO с фреймворком CMSIS и
 * подлинным заголовком STM32F1xx (см. platformio.ini), поэтому в
 * реальной сборке этот файл не участвует.
 *
 * Все значения битов приведены по справочнику RM0008
 * (STM32F103xx reference manual), выдуманных чисел здесь нет.
 */
#ifndef STUB_STM32F1XX_H
#define STUB_STM32F1XX_H

#include <stdint.h>

/* --- Структуры регистров (поля идут в порядке адресов RM0008) --- */

/* RCC, базовый адрес 0x4002 1000 */
typedef struct
{
    volatile uint32_t CR;      /* +0x00 */
    volatile uint32_t CFGR;    /* +0x04 */
    volatile uint32_t CIR;     /* +0x08 */
    volatile uint32_t APB2RSTR;/* +0x0C */
    volatile uint32_t APB1RSTR;/* +0x10 */
    volatile uint32_t AHBENR;  /* +0x14 */
    volatile uint32_t APB2ENR; /* +0x18 */
    volatile uint32_t APB1ENR; /* +0x1C */
    volatile uint32_t BDCR;    /* +0x20 */
    volatile uint32_t CSR;     /* +0x24 */
} RCC_TypeDef;

/* GPIOA, базовый адрес 0x4001 0800 */
typedef struct
{
    volatile uint32_t CRL;  /* +0x00 */
    volatile uint32_t CRH;  /* +0x04 */
    volatile uint32_t IDR;  /* +0x08 */
    volatile uint32_t ODR;  /* +0x0C */
    volatile uint32_t BSRR; /* +0x10 */
    volatile uint32_t BRR;  /* +0x14 */
    volatile uint32_t LCKR; /* +0x18 */
} GPIO_TypeDef;

/* USART1, базовый адрес 0x4001 3800 */
typedef struct
{
    volatile uint32_t SR;   /* +0x00 */
    volatile uint32_t DR;   /* +0x04 */
    volatile uint32_t BRR;  /* +0x08 */
    volatile uint32_t CR1;  /* +0x0C */
    volatile uint32_t CR2;  /* +0x10 */
    volatile uint32_t CR3;  /* +0x14 */
    volatile uint32_t GTPR; /* +0x18 */
} USART_TypeDef;

#define RCC    ((RCC_TypeDef   *)0x40021000U) /* RM0008: 0x4002 1000 */
#define GPIOA  ((GPIO_TypeDef  *)0x40010800U) /* RM0008: 0x4001 0800 */
#define USART1 ((USART_TypeDef *)0x40013800U) /* RM0008: 0x4001 3800 */

/* --- RCC_CR --- */
#define RCC_CR_HSION   (1U << 0)  /* 0x00000001: вкл. внутр. генератора HSI */
#define RCC_CR_HSIRDY  (1U << 1)  /* 0x00000002: HSI готов */

/* --- RCC_CFGR --- */
#define RCC_CFGR_SW       (3U << 0)  /* 0x00000003: выбор системной частоты */
#define RCC_CFGR_SW_HSI   (0U << 0)  /* 0x00000000: SYSCLK = HSI */
#define RCC_CFGR_SWS      (3U << 2)  /* 0x0000000C: фактический SYSCLK */
#define RCC_CFGR_SWS_HSI  (0U << 2)  /* 0x00000000: факт. источник = HSI */

/* --- RCC_APB2ENR --- */
#define RCC_APB2ENR_IOPAEN   (1U << 2)  /* 0x00000004: тактирование GPIOA */
#define RCC_APB2ENR_USART1EN (1U << 14) /* 0x00004000: тактирование USART1 */

/* --- GPIO_CRL: поля MODEy[1:0]/CNFy[1:0] для вывода y < 8 --- */
#define GPIO_CRL_MODE1   (3U << 4)  /* 0x00000030 */
#define GPIO_CRL_CNF1    (3U << 6)  /* 0x000000C0 */
#define GPIO_CRL_MODE1_1 (1U << 5)  /* 0x00000020: выход 2 МГц */

/* --- GPIO_CRH: поля MODEy[1:0]/CNFy[1:0] для вывода y >= 8 --- */
#define GPIO_CRH_MODE9   (3U << 20) /* 0x00300000 */
#define GPIO_CRH_CNF9    (3U << 22) /* 0x00C00000 */
#define GPIO_CRH_MODE9_1 (1U << 21) /* 0x00200000: выход 2 МГц */
#define GPIO_CRH_CNF9_1  (1U << 23) /* 0x00800000: альт. функция push-pull */
#define GPIO_CRH_MODE10  (3U << 24) /* 0x03000000 */
#define GPIO_CRH_CNF10   (3U << 26) /* 0x0C000000 */
#define GPIO_CRH_CNF10_0 (1U << 26) /* 0x04000000: плавающий вход */

/* --- GPIO_ODR --- */
#define GPIO_ODR_ODR1 (1U << 1) /* 0x00000002: уровень на PA1 */

/* --- USART_SR: у STM32F1 бит 4 — флаг IDLE, поэтому RXNE стоит
 *      в бите 5 (не в бите 4, как у семейства STM32F4) --- */
#define USART_SR_PE  (1U << 0) /* 0x01: ошибка чётности */
#define USART_SR_FE  (1U << 1) /* 0x02: ошибка кадра (нет стопового бита) */
#define USART_SR_NE  (1U << 2) /* 0x04: ошибка шума */
#define USART_SR_ORE (1U << 3) /* 0x08: переполнение приёмника */
#define USART_SR_RXNE (1U << 5) /* 0x20: принятый байт в DR */
#define USART_SR_TC   (1U << 6) /* 0x40: передача кадра завершена */
#define USART_SR_TXE  (1U << 7) /* 0x80: DR свободен для передачи */

/* --- USART_CR1 --- */
#define USART_CR1_RE    (1U << 2)  /* 0x0004: включить приёмник */
#define USART_CR1_TE    (1U << 3)  /* 0x0008: включить передатчик */
#define USART_CR1_RXNEIE (1U << 5) /* 0x0020: прерывание по RXNE */
#define USART_CR1_UE    (1U << 13) /* 0x2000: включить USART */

/* --- NVIC --- */
typedef enum
{
    USART1_IRQn = 37 /* USART1 глобальное прерывание, номер 37 (RM0008) */
} IRQn_Type;

/* Заглушки функций CMSIS: на хосте они ничего не делают,
 * в реальной прошивке их предоставляет CMSIS core_cm3.h. */
static inline void NVIC_EnableIRQ(IRQn_Type irq)
{
    (void)irq;
}

static inline void NVIC_SetPriority(IRQn_Type irq, uint32_t priority)
{
    (void)irq;
    (void)priority;
}

static inline void NVIC_ClearPendingIRQ(IRQn_Type irq)
{
    (void)irq;
}

#endif /* STUB_STM32F1XX_H */
