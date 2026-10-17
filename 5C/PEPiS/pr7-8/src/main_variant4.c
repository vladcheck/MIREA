/*====================================================================
 * Практическая работа № 4 «Организация последовательного обмена
 * данными в микроконтроллерной системе» (пр7-8, Proteus),
 * ИНДИВИДУАЛЬНЫЙ ВАРИАНТ 4 — приём USART1 по прерыванию
 * с программным кольцевым буфером (архитектура листинга 9.6).
 *
 * Параметры варианта 4 (табл. 9.13 методички):
 *   - скорость передачи 19200 бит/с;
 *   - приём символов по прерыванию RXNE (кольцевой буфер 16 байт);
 *   - управляющий символ 'D' (0x44) — переключает светодиод PA1;
 *   - диагностическое изменение — уменьшить USART1_BRR в 2 раза.
 *
 * Базовая конфигурация практикума: HSI 8 МГц без PLL, PCLK2 = 8 МГц,
 * USART1 на PA9 (TX, альтернативная функция push-pull) / PA10 (RX,
 * плавающий вход), формат 8N1, светодиод с резистором на PA1.
 *
 * Расчёт значения регистра USART1_BRR при PCLK2 = 8 МГц:
 *   8 000 000 / 19 200 = 416,67 -> округление до 417 = 0x01A1;
 *   фактическая скорость 8 000 000 / 417 = 19 184,65 бит/с,
 *   относительная ошибка (19 184,65 - 19 200) / 19 200 = -0,08 %.
 *
 * Строка запуска: «PR4-04 STM32 READY».
 *
 * В обработчике прерывания выполняются только чтение USART1_SR и
 * USART1_DR, фиксация ошибок ORE / NE / FE / PE и помещение байта
 * в буфер; передача строк, эхо и переключение светодиода —
 * исключительно в основном цикле.
 *
 * Сборка: PlatformIO с фреймворком CMSIS (см. platformio.ini).
 * Результат (.elf/.hex) указывается в поле Program File модели
 * STM32F103C8 в Proteus 8.17.
 *====================================================================*/
#include "stm32f1xx.h"

#define PCLK2_HZ 8000000UL
#define BAUD     19200UL
#define USART1_BRR_VALUE ((PCLK2_HZ + BAUD / 2UL) / BAUD)
/* 8 000 000 / 19 200 = 416,67 -> 417 = 0x01A1 (см. расчёт в шапке). */

/* Диагностическое изменение варианта 4: «уменьшить BRR в 2 раза».
 *   0 — нормальные параметры (BRR = 417 = 0x01A1, 19200 бит/с);
 *   1 — BRR вдвое меньше: 417 / 2 = 208 (0x00D0),
 *       фактическая скорость 8 000 000 / 208 = 38 461,5 бит/с.
 *
 * Эксперимент: соберите прошивку с 1 и запустите модель, оставив
 * Virtual Terminal на 19200 8N1. МК передаёт вдвое быстрее
 * ожидаемого, поэтому приёмник терминала ловит биты не в те
 * моменты времени: в терминале появляются ошибки кадра (FE) и
 * нечитаемый мусор. Зафиксировав эффект, верните значение 0 и
 * пересоберите — параметры восстановятся. */
#define USART_DIAG_BRR_HALF 0

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
#if USART_DIAG_BRR_HALF
    USART1->BRR = 208U; /* 0x00D0: BRR в 2 раза меньше нормы (диагностика) */
#else
    USART1->BRR = (uint16_t)USART1_BRR_VALUE;
#endif
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

static void LED_Toggle(void)
{
    if ((GPIOA->ODR & GPIO_ODR_ODR1)) GPIOA->ODR &= ~GPIO_ODR_ODR1;
    else GPIOA->ODR |= GPIO_ODR_ODR1;
}

/* --- Кольцевой буфер приёма (листинг 9.6) ---------------------- */
#define RX_BUF_SIZE 16U

static volatile uint8_t rx_buffer[RX_BUF_SIZE];
static volatile uint8_t rx_head;
static volatile uint8_t rx_tail;
static volatile uint8_t rx_overflow;
static volatile uint32_t rx_error_flags;

static void USART1_EnableRxInterrupt(void)
{
    volatile uint32_t dummy;
    dummy = USART1->SR; dummy = USART1->DR; (void)dummy;
    NVIC_ClearPendingIRQ(USART1_IRQn);
    NVIC_SetPriority(USART1_IRQn, 2U);
    USART1->CR1 |= USART_CR1_RXNEIE;
    NVIC_EnableIRQ(USART1_IRQn);
}

void USART1_IRQHandler(void)
{
    uint32_t status = USART1->SR;
    if (status & (USART_SR_RXNE | USART_SR_ORE | USART_SR_NE | USART_SR_FE | USART_SR_PE)) {
        uint8_t data = (uint8_t)USART1->DR;
        uint32_t errors = status & (USART_SR_ORE | USART_SR_NE | USART_SR_FE | USART_SR_PE);
        if (errors != 0U) rx_error_flags |= errors;
        else {
            uint8_t next = (uint8_t)((rx_head + 1U) & (RX_BUF_SIZE - 1U));
            if (next != rx_tail) { rx_buffer[rx_head] = data; rx_head = next; }
            else rx_overflow = 1U;
        }
    }
}

static uint8_t USART1_RxPop(uint8_t *data)
{
    if (rx_head == rx_tail) return 0U;
    *data = rx_buffer[rx_tail];
    rx_tail = (uint8_t)((rx_tail + 1U) & (RX_BUF_SIZE - 1U));
    return 1U;
}

int main(void)
{
    uint8_t data;
    Clock_Init_HSI8MHz(); GPIO_Init(); USART1_Init();
    USART1_EnableRxInterrupt();
    USART1_SendString("PR4-04 STM32 READY\r\n");
    while (1) {
        if (USART1_RxPop(&data)) {
            USART1_SendChar(data);
            if (data == 'D') LED_Toggle();
        }
    }
}
