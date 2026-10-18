/* Минимальный стуб CMSIS-заголовка stm32f10x.h для синтаксической
 * проверки clang -fsyntax-only. В прошивке используется реальный
 * заголовок CooCox / STM32Cube / Std Peripheral Library.
 */
#ifndef STUB_STM32F10X_H
#define STUB_STM32F10X_H

#include <stdint.h>

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
    volatile uint32_t OAR1;
    volatile uint32_t OAR2;
    volatile uint32_t DR;
    volatile uint32_t SR1;
    volatile uint32_t SR2;
    volatile uint32_t CCR;
    volatile uint32_t TRISE;
} I2C_TypeDef;

#define RCC   ((RCC_TypeDef *)0x40021000U)
#define GPIOA ((GPIO_TypeDef *)0x40010800U)
#define GPIOB ((GPIO_TypeDef *)0x40010C00U)
#define I2C1  ((I2C_TypeDef *)0x40005400U)

/* RCC_CR */
#define RCC_CR_HSION   (1U << 0)
#define RCC_CR_HSIRDY  (1U << 1)
#define RCC_CR_HSEON   (1U << 16)
#define RCC_CR_PLLON   (1U << 24)
#define RCC_CR_CSSON   (1U << 19)
/* RCC_CFGR */
#define RCC_CFGR_SW        (3U << 0)
#define RCC_CFGR_SW_HSI    (0U << 0)
#define RCC_CFGR_SWS       (3U << 2)
#define RCC_CFGR_SWS_HSI   (0U << 2)
#define RCC_CFGR_HPRE      (15U << 4)
#define RCC_CFGR_PPRE1     (7U << 8)
#define RCC_CFGR_PPRE2     (7U << 11)
/* RCC_APB1RSTR */
#define RCC_APB1RSTR_I2C1RST (1U << 21)
/* RCC_APB2ENR */
#define RCC_APB2ENR_IOPAEN (1U << 2)
#define RCC_APB2ENR_IOPBEN (1U << 3)
/* RCC_APB1ENR */
#define RCC_APB1ENR_I2C1EN (1U << 21)

/* GPIO_CRL: поля MODEy[1:0]/CNFy[1:0] для вывода y */
#define GPIO_CRL_MODE1      (3U << 4)
#define GPIO_CRL_CNF1       (3U << 6)
#define GPIO_CRL_MODE1_1    (2U << 4)
#define GPIO_CRL_MODE6      (3U << 24)
#define GPIO_CRL_CNF6       (3U << 26)
#define GPIO_CRL_MODE6_1    (2U << 24)
#define GPIO_CRL_CNF6_0     (1U << 26)
#define GPIO_CRL_CNF6_1     (2U << 26)
#define GPIO_CRL_MODE7      (3U << 28)
#define GPIO_CRL_CNF7       (3U << 30)
#define GPIO_CRL_MODE7_1    (2U << 28)
#define GPIO_CRL_CNF7_0     (1U << 30)
#define GPIO_CRL_CNF7_1     (2U << 30)
/* GPIO_BSRR */
#define GPIO_BSRR_BR1 (1U << 17)
#define GPIO_BSRR_BS1 (1U << 1)

/* I2C_CR1 */
#define I2C_CR1_PE    (1U << 0)
#define I2C_CR1_START (1U << 8)
#define I2C_CR1_STOP  (1U << 9)
#define I2C_CR1_ACK   (1U << 10)
#define I2C_CR1_POS   (1U << 11)
/* I2C_CR2 */
#define I2C_CR2_FREQ (63U << 0)
/* I2C_SR1 */
#define I2C_SR1_SB   (1U << 0)
#define I2C_SR1_ADDR (1U << 1)
#define I2C_SR1_BTF  (1U << 2)
#define I2C_SR1_RXNE (1U << 6)
#define I2C_SR1_TXE  (1U << 7)
#define I2C_SR1_OVR  (1U << 11)
#define I2C_SR1_AF   (1U << 10)
#define I2C_SR1_ARLO (1U << 9)
#define I2C_SR1_BERR (1U << 8)
/* I2C_SR2 */
#define I2C_SR2_MSL  (1U << 0)
#define I2C_SR2_BUSY (1U << 1)

#endif /* STUB_STM32F10X_H */
