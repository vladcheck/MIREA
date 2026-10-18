/*====================================================================
 * Практическая работа № 4 «Организация последовательного обмена
 * данными в микроконтроллерной системе» (пр7-8, Proteus),
 * УЧЕБНЫЙ ПРИМЕР — воспроизведение листинга 9.5 методички:
 * передача строки запуска и эхо-обмен через USART1 STM32F103C8
 * методом блокирующего опроса флага RXNE.
 *
 * Базовая конфигурация практикума:
 *   - тактирование: внутренний генератор HSI 8 МГц без PLL,
 *     делитель APB2 = 1, поэтому PCLK2 = 8 МГц;
 *   - USART1: PA9 — TX (выход альтернативной функции push-pull),
 *     PA10 — RX (плавающий вход), формат 8N1, 9600 бит/с;
 *   - расчёт: USART1_BRR = 8 000 000 / 9600 = 833,33 -> 833 = 0x0341,
 *     фактическая скорость 8 000 000 / 833 = 9603,84 бит/с
 *     (относительная ошибка около +0,04 %);
 *   - светодиод с резистором подключён к PA1;
 *   - строка запуска учебного примера: «PR4-01 STM32 READY».
 *
 * Поведение: строка запуска выводится один раз; каждый принятый
 * без ошибок символ возвращается в терминал (эхо); символ 'A'
 * (0x41) переключает состояние светодиода на PA1. Принятые с
 * ошибкой байты (ORE / NE / FE / PE) не эхируются. Перед чтением
 * USART1_DR читается USART1_SR, чтобы связать байт с флагами
 * ошибок.
 *
 * Сборка: PlatformIO с фреймворком CMSIS (см. platformio.ini).
 * Результат (.elf/.hex) указывается в поле Program File модели
 * STM32F103C8 в Proteus 8.17.
 *====================================================================*/
#include "stm32f1xx.h"

#define PCLK2_HZ 8000000UL
#define BAUD     9600UL
#define USART1_BRR_VALUE ((PCLK2_HZ + BAUD / 2UL) / BAUD)
/* 8 000 000 / 9600 = 833,33; округление по формуле даёт 833 = 0x0341. */

static void Clock_Init_HSI8MHz(void)
{
    uint32_t timeout = 1000000UL;
    RCC->CR |= RCC_CR_HSION;
    while (!(RCC->CR & RCC_CR_HSIRDY) && timeout--) { }
    RCC->CFGR &= ~RCC_CFGR_SW;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_HSI) { }
}

static void GPIO_Init(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;
    GPIOA->CRL &= ~(GPIO_CRL_MODE1 | GPIO_CRL_CNF1);
    GPIOA->CRL |= GPIO_CRL_MODE1_1;
    GPIOA->CRH &= ~(GPIO_CRH_MODE9 | GPIO_CRH_CNF9);
    GPIOA->CRH |= (GPIO_CRH_MODE9_1 | GPIO_CRH_CNF9_1);
    GPIOA->CRH &= ~(GPIO_CRH_MODE10 | GPIO_CRH_CNF10);
    GPIOA->CRH |= GPIO_CRH_CNF10_0;
    GPIOA->ODR &= ~GPIO_ODR_ODR1;
}

static void USART1_Init(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1->CR1 = 0U; USART1->CR2 = 0U; USART1->CR3 = 0U;
    USART1->BRR = (uint16_t)USART1_BRR_VALUE;
    USART1->CR1 |= (USART_CR1_TE | USART_CR1_RE | USART_CR1_UE);
}

static void USART1_SendChar(uint8_t data)
{
    while (!(USART1->SR & USART_SR_TXE)) { }
    USART1->DR = data;
}

static void USART1_SendString(const char *text)
{
    while (*text != '\0') USART1_SendChar((uint8_t)*text++);
}

static uint8_t USART1_Receive(uint8_t *data)
{
    uint32_t status;
    while (!(USART1->SR & USART_SR_RXNE)) { }
    status = USART1->SR;
    *data = (uint8_t)USART1->DR;
    return (status & (USART_SR_ORE | USART_SR_NE | USART_SR_FE | USART_SR_PE)) == 0U;
}

static void LED_Toggle(void)
{
    if ((GPIOA->ODR & GPIO_ODR_ODR1)) GPIOA->ODR &= ~GPIO_ODR_ODR1;
    else GPIOA->ODR |= GPIO_ODR_ODR1;
}

int main(void)
{
    uint8_t data;
    Clock_Init_HSI8MHz(); GPIO_Init(); USART1_Init();
    USART1_SendString("PR4-01 STM32 READY\r\n");
    while (1) {
        if (USART1_Receive(&data)) {
            USART1_SendChar(data);
            if (data == 'A') LED_Toggle();
        }
    }
}
