/* Минимальный стуб CMSIS-заголовка stm32f1xx.h для синтаксической
 * проверки clang -fsyntax-only. В прошивке используется реальный
 * заголовок CMSIS stm32f1xx.h из пакета устройства STM32F1
 * (CMSIS Device STM32F103xb: RCC, GPIOA, TIM2, NVIC, __WFI).
 */
#ifndef STUB_STM32F1XX_H
#define STUB_STM32F1XX_H

#include <stdint.h>

/* Номера прерываний NVIC (для STM32F103): TIM2 — 28. */
typedef enum
{
    TIM2_IRQn = 28
} IRQn_Type;

typedef struct
{
    volatile uint32_t CR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t APB2RSTR;
    volatile uint32_t APB1RSTR;
    volatile uint32_t AHBENR;
    volatile uint32_t APB2ENR;
    volatile uint32_t APB1ENR;
    volatile uint32_t BDCR;
    volatile uint32_t CSR;
} RCC_TypeDef;

typedef struct
{
    volatile uint32_t CRL;
    volatile uint32_t CRH;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t BRR;
    volatile uint32_t LCKR;
} GPIO_TypeDef;

typedef struct
{
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
    volatile uint32_t RCR;
    volatile uint32_t CCR1;
    volatile uint32_t CCR2;
    volatile uint32_t CCR3;
    volatile uint32_t CCR4;
    volatile uint32_t BDTR;
    volatile uint32_t DCR;
    volatile uint32_t DMAR;
} TIM_TypeDef;

#define RCC   ((RCC_TypeDef *)0x40021000U)
#define GPIOA ((GPIO_TypeDef *)0x40010800U)
#define TIM2  ((TIM_TypeDef *)0x40000000U)

/* RCC_CR */
#define RCC_CR_HSION   (1U << 0)
#define RCC_CR_HSIRDY  (1U << 1)
#define RCC_CR_HSEON   (1U << 16)
#define RCC_CR_CSSON   (1U << 19)
#define RCC_CR_PLLON   (1U << 24)
/* RCC_CFGR */
#define RCC_CFGR_SW        (3U << 0)
#define RCC_CFGR_SW_HSI    (0U << 0)
#define RCC_CFGR_SWS       (3U << 2)
#define RCC_CFGR_SWS_HSI   (0U << 2)
#define RCC_CFGR_HPRE      (15U << 4)
#define RCC_CFGR_PPRE1     (7U << 8)
#define RCC_CFGR_PPRE2     (7U << 11)
/* RCC_APB2ENR */
#define RCC_APB2ENR_IOPAEN (1U << 2)
/* RCC_APB1ENR */
#define RCC_APB1ENR_TIM2EN (1U << 0)
/* RCC_APB1RSTR */
#define RCC_APB1RSTR_TIM2RST (1U << 0)

/* GPIO_CRL: поля MODEy[1:0]/CNFy[1:0] для вывода y */
#define GPIO_CRL_MODE1      (3U << 4)
#define GPIO_CRL_CNF1       (3U << 6)
#define GPIO_CRL_MODE1_1    (2U << 4)
/* GPIO_ODR */
#define GPIO_ODR_ODR1       (1U << 1)
/* GPIO_BSRR */
#define GPIO_BSRR_BR1       (1U << 17)

/* TIM_CR1 */
#define TIM_CR1_CEN  (1U << 0)
/* TIM_DIER */
#define TIM_DIER_UIE (1U << 0)
/* TIM_EGR */
#define TIM_EGR_UG   (1U << 0)
/* TIM_SR */
#define TIM_SR_UIF   (1U << 0)

/* Заглушки функций CMSIS Core для синтаксической проверки. */
static inline void NVIC_EnableIRQ(IRQn_Type irq)
{
    (void)irq;
}

static inline void NVIC_ClearPendingIRQ(IRQn_Type irq)
{
    (void)irq;
}

static inline void NVIC_SetPriority(IRQn_Type irq, uint32_t priority)
{
    (void)irq;
    (void)priority;
}

static inline void __WFI(void)
{
}

#endif /* STUB_STM32F1XX_H */
