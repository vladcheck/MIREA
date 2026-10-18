/*====================================================================
 * ПР №3-4, ИНДИВИДУАЛЬНЫЙ ВАРИАНТ 4 (табл. 9.9 методички, Proteus) —
 * запись и чтение EEPROM 24LC64 и чтение регистра DS1307 через I2C1
 * STM32F103C8 (HSI 8 МГц, fSCL = 100 кГц: FREQ=8, CCR=40, TRISE=9).
 *
 * Вариант 4: ячейка EEPROM 0x003F, записываемый байт 0x67,
 * регистр DS1307 0x00 (секунды). Ожидаемый результат: считанный байт
 * равен 0x67; регистр секунд после установки 12:34:00 даёт raw BCD 0x00
 * (CH=0) -> десятичное 0; светодиод PA1 включён (успех).
 *
 * Светодиод результата — PA1 (1 = успех, 0 = ошибка).
 * Сборка: CooCox CoIDE / GCC ARM Embedded (stm32f10x.h).
 *====================================================================*/
#include "stm32f10x.h"

#ifndef SET_BIT
#define SET_BIT(REG, BIT)     ((REG) |= (BIT))
#endif
#ifndef CLEAR_BIT
#define CLEAR_BIT(REG, BIT)   ((REG) &= ~(BIT))
#endif
#ifndef READ_BIT
#define READ_BIT(REG, BIT)    ((REG) & (BIT))
#endif
#ifndef MODIFY_REG
#define MODIFY_REG(REG, CLEARMASK, SETMASK) \
    do {                                     \
        CLEAR_BIT((REG), (CLEARMASK));       \
        SET_BIT((REG), (SETMASK));           \
    } while (0)
#endif

#define I2C_TIMEOUT       100000U
#define EEPROM_ADDR       0x50U
#define DS1307_ADDR       0x68U

/* Индивидуальный вариант 4 (табл. 9.9): ячейка 0x003F, байт 0x67,
 * регистр DS1307 0x00 (секунды). */
#define EEPROM_CELL       0x003FU
#define EEPROM_TEST_VALUE 0x67U
#define DS1307_TEST_REG   0x00U

static void Clock_Init_HSI8MHz(void)
{
    SET_BIT(RCC->CR, RCC_CR_HSION);
    while (READ_BIT(RCC->CR, RCC_CR_HSIRDY) == 0U) { }

    MODIFY_REG(RCC->CFGR, RCC_CFGR_SW, RCC_CFGR_SW_HSI);
    while (READ_BIT(RCC->CFGR, RCC_CFGR_SWS) !=
           RCC_CFGR_SWS_HSI) { }

    MODIFY_REG(RCC->CFGR,
               RCC_CFGR_HPRE | RCC_CFGR_PPRE1 | RCC_CFGR_PPRE2,
               0U);
    CLEAR_BIT(RCC->CR,
              RCC_CR_CSSON | RCC_CR_PLLON | RCC_CR_HSEON);
}

static void ResultLED_Init(void)
{
    SET_BIT(RCC->APB2ENR, RCC_APB2ENR_IOPAEN);
    MODIFY_REG(GPIOA->CRL,
               GPIO_CRL_MODE1 | GPIO_CRL_CNF1,
               GPIO_CRL_MODE1_1);
    GPIOA->BSRR = GPIO_BSRR_BR1;
}

static void ResultLED_Set(uint8_t state)
{
    GPIOA->BSRR = state ? GPIO_BSRR_BS1 : GPIO_BSRR_BR1;
}

static uint8_t I2C1_WaitBusFree(void)
{
    uint32_t timeout = I2C_TIMEOUT;
    while (READ_BIT(I2C1->SR2, I2C_SR2_BUSY) != 0U) {
        if (--timeout == 0U) return 0U;
    }
    return 1U;
}

static uint8_t I2C1_WaitSR1(uint32_t mask)
{
    uint32_t timeout = I2C_TIMEOUT;
    const uint32_t errors = I2C_SR1_AF | I2C_SR1_BERR |
                            I2C_SR1_ARLO | I2C_SR1_OVR;

    while (READ_BIT(I2C1->SR1, mask) == 0U) {
        if (READ_BIT(I2C1->SR1, errors) != 0U) return 0U;
        if (--timeout == 0U) return 0U;
    }
    return 1U;
}

static void I2C1_ClearADDR(void)
{
    volatile uint32_t tmp;
    tmp = I2C1->SR1;
    tmp = I2C1->SR2;
    (void)tmp;
}

static void I2C1_Recover(void)
{
    const uint32_t errors = I2C_SR1_AF | I2C_SR1_BERR |
                            I2C_SR1_ARLO | I2C_SR1_OVR;

    if (READ_BIT(I2C1->SR2, I2C_SR2_MSL) != 0U) {
        SET_BIT(I2C1->CR1, I2C_CR1_STOP);
    }
    CLEAR_BIT(I2C1->SR1, errors);
    CLEAR_BIT(I2C1->CR1, I2C_CR1_POS);
    SET_BIT(I2C1->CR1, I2C_CR1_ACK);
}

static void I2C1_Init_100k(void)
{
    SET_BIT(RCC->APB2ENR, RCC_APB2ENR_IOPBEN);
    SET_BIT(RCC->APB1ENR, RCC_APB1ENR_I2C1EN);

    SET_BIT(RCC->APB1RSTR, RCC_APB1RSTR_I2C1RST);
    CLEAR_BIT(RCC->APB1RSTR, RCC_APB1RSTR_I2C1RST);

    /* PB6=SCL, PB7=SDA: альтернативная функция, открытый сток, 2 МГц. */
    MODIFY_REG(GPIOB->CRL,
               GPIO_CRL_MODE6 | GPIO_CRL_CNF6,
               GPIO_CRL_MODE6_1 |
               GPIO_CRL_CNF6_0 | GPIO_CRL_CNF6_1);
    MODIFY_REG(GPIOB->CRL,
               GPIO_CRL_MODE7 | GPIO_CRL_CNF7,
               GPIO_CRL_MODE7_1 |
               GPIO_CRL_CNF7_0 | GPIO_CRL_CNF7_1);

    CLEAR_BIT(I2C1->CR1, I2C_CR1_PE);
    MODIFY_REG(I2C1->CR2, I2C_CR2_FREQ, 8U);
    I2C1->CCR = 40U;
    I2C1->TRISE = 9U;
    I2C1->OAR1 = (1U << 14);
    CLEAR_BIT(I2C1->CR1, I2C_CR1_POS);
    SET_BIT(I2C1->CR1, I2C_CR1_ACK | I2C_CR1_PE);
}

static uint8_t I2C1_StartWrite(uint8_t address)
{
    SET_BIT(I2C1->CR1, I2C_CR1_START);
    if (!I2C1_WaitSR1(I2C_SR1_SB)) return 0U;

    I2C1->DR = (uint8_t)(address << 1);
    if (!I2C1_WaitSR1(I2C_SR1_ADDR)) return 0U;
    I2C1_ClearADDR();
    return 1U;
}

static uint8_t EEPROM_WaitReady(void)
{
    uint16_t attempt;
    uint32_t timeout;
    uint32_t sr1;
    const uint32_t fatal = I2C_SR1_BERR |
                           I2C_SR1_ARLO | I2C_SR1_OVR;

    for (attempt = 0U; attempt < 1000U; ++attempt) {
        if (!I2C1_WaitBusFree()) return 0U;

        SET_BIT(I2C1->CR1, I2C_CR1_START);
        if (!I2C1_WaitSR1(I2C_SR1_SB)) {
            I2C1_Recover();
            return 0U;
        }
        I2C1->DR = (uint8_t)(EEPROM_ADDR << 1);

        timeout = I2C_TIMEOUT;
        do {
            sr1 = I2C1->SR1;
            if (READ_BIT(sr1, I2C_SR1_ADDR) != 0U) {
                I2C1_ClearADDR();
                SET_BIT(I2C1->CR1, I2C_CR1_STOP);
                return 1U;
            }
            if (READ_BIT(sr1, I2C_SR1_AF) != 0U) {
                CLEAR_BIT(I2C1->SR1, I2C_SR1_AF);
                SET_BIT(I2C1->CR1, I2C_CR1_STOP);
                break;
            }
            if (READ_BIT(sr1, fatal) != 0U) {
                I2C1_Recover();
                return 0U;
            }
        } while (--timeout != 0U);

        if (timeout == 0U) {
            I2C1_Recover();
            return 0U;
        }
    }
    return 0U;
}

static uint8_t EEPROM_WriteByte(uint16_t mem, uint8_t data)
{
    if (mem > 0x1FFFU || !I2C1_WaitBusFree()) return 0U;
    if (!I2C1_StartWrite(EEPROM_ADDR)) goto error;

    if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
    I2C1->DR = (uint8_t)(mem >> 8);
    if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
    I2C1->DR = (uint8_t)mem;
    if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
    I2C1->DR = data;
    if (!I2C1_WaitSR1(I2C_SR1_BTF)) goto error;

    SET_BIT(I2C1->CR1, I2C_CR1_STOP);
    return EEPROM_WaitReady();

error:
    I2C1_Recover();
    return 0U;
}

static uint8_t I2C1_ReadOneByte(uint8_t address, uint8_t *data)
{
    SET_BIT(I2C1->CR1, I2C_CR1_START);
    if (!I2C1_WaitSR1(I2C_SR1_SB)) return 0U;

    I2C1->DR = (uint8_t)((address << 1) | 1U);
    if (!I2C1_WaitSR1(I2C_SR1_ADDR)) return 0U;

    CLEAR_BIT(I2C1->CR1, I2C_CR1_ACK);
    I2C1_ClearADDR();
    SET_BIT(I2C1->CR1, I2C_CR1_STOP);

    if (!I2C1_WaitSR1(I2C_SR1_RXNE)) return 0U;
    *data = (uint8_t)I2C1->DR;
    SET_BIT(I2C1->CR1, I2C_CR1_ACK);
    return 1U;
}

static uint8_t EEPROM_ReadByte(uint16_t mem, uint8_t *data)
{
    if (data == 0 || mem > 0x1FFFU ||
        !I2C1_WaitBusFree()) return 0U;
    if (!I2C1_StartWrite(EEPROM_ADDR)) goto error;

    if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
    I2C1->DR = (uint8_t)(mem >> 8);
    if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
    I2C1->DR = (uint8_t)mem;
    if (!I2C1_WaitSR1(I2C_SR1_BTF)) goto error;

    if (!I2C1_ReadOneByte(EEPROM_ADDR, data)) goto error;
    return 1U;

error:
    I2C1_Recover();
    return 0U;
}

static uint8_t DS1307_WriteBytes(uint8_t reg,
                                 const uint8_t *data,
                                 uint8_t count)
{
    uint8_t i;

    if (data == 0 || count == 0U ||
        !I2C1_WaitBusFree()) return 0U;
    if (!I2C1_StartWrite(DS1307_ADDR)) goto error;

    if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
    I2C1->DR = reg;
    for (i = 0U; i < count; ++i) {
        if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
        I2C1->DR = data[i];
    }
    if (!I2C1_WaitSR1(I2C_SR1_BTF)) goto error;
    SET_BIT(I2C1->CR1, I2C_CR1_STOP);
    return 1U;

error:
    I2C1_Recover();
    return 0U;
}

static uint8_t DS1307_ReadReg(uint8_t reg, uint8_t *data)
{
    if (data == 0 || !I2C1_WaitBusFree()) return 0U;
    if (!I2C1_StartWrite(DS1307_ADDR)) goto error;
    if (!I2C1_WaitSR1(I2C_SR1_TXE)) goto error;
    I2C1->DR = reg;
    if (!I2C1_WaitSR1(I2C_SR1_BTF)) goto error;

    if (!I2C1_ReadOneByte(DS1307_ADDR, data)) goto error;
    return 1U;

error:
    I2C1_Recover();
    return 0U;
}

static uint8_t DecToBCD(uint8_t value)
{
    return (uint8_t)(((value / 10U) << 4) |
                     (value % 10U));
}

static uint8_t BCDToDec(uint8_t value)
{
    return (uint8_t)(10U * ((value >> 4) & 0x0FU) +
                     (value & 0x0FU));
}

static uint8_t DS1307_SetTime(uint8_t h, uint8_t m, uint8_t s)
{
    uint8_t raw[3];

    if (h > 23U || m > 59U || s > 59U) return 0U;
    raw[0] = (uint8_t)(DecToBCD(s) & 0x7FU); /* CH=0 */
    raw[1] = DecToBCD(m);
    raw[2] = (uint8_t)(DecToBCD(h) & 0x3FU); /* 24 ч */
    return DS1307_WriteBytes(0x00U, raw, 3U);
}

static uint8_t DS1307_DecodeReg(uint8_t reg, uint8_t raw)
{
    if (reg == 0x00U || reg == 0x01U) raw &= 0x7FU;
    if (reg == 0x02U) raw &= 0x3FU;
    return BCDToDec(raw);
}

volatile uint8_t g_eeprom_read;
volatile uint8_t g_rtc_raw;
volatile uint8_t g_rtc_value;

int main(void)
{
    uint8_t value;

    Clock_Init_HSI8MHz();
    ResultLED_Init();
    I2C1_Init_100k();

    if (!EEPROM_WriteByte(EEPROM_CELL, EEPROM_TEST_VALUE))
        goto error;
    if (!EEPROM_ReadByte(EEPROM_CELL, &value)) goto error;
    g_eeprom_read = value;
    if (value != EEPROM_TEST_VALUE) goto error;

    /* Запуск генератора DS1307 и выбор режима 24 ч. */
    if (!DS1307_SetTime(12U, 34U, 0U)) goto error;
    if (!DS1307_ReadReg(DS1307_TEST_REG, &value)) goto error;
    g_rtc_raw = value;
    g_rtc_value = DS1307_DecodeReg(DS1307_TEST_REG, value);

    ResultLED_Set(1U);
    while (1) { }

error:
    ResultLED_Set(0U);
    while (1) { }
}
