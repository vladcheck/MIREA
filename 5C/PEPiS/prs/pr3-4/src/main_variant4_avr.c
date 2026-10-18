/*====================================================================
 * ПР №3-4, индивидуальный вариант 4 для СРАВНИТЕЛЬНОЙ платформы
 * ATmega32 (листинги 9.5 и 9.6 методички, Proteus) — та же задача,
 * что и в main_variant4.c, но через интерфейс TWI (регистры TWSR/TWBR/
 * TWCR/TWDR) с контролем кодов состояния.
 *
 * Вариант 4: ячейка EEPROM 0x003F, байт 0x67, регистр DS1307 0x00.
 * FCPU = 8 МГц, TWPS = 00 (пределитель 1), TWBR = 32 -> fSCL = 100 кГц.
 * Макрос F_CPU не задаёт частоту модели: в Proteus свойстве CKSEL
 * ATmega32 должен стоять генератор 8 МГц.
 *
 * Светодиод результата — PB1 (1 = успех, 0 = ошибка).
 * Сборка: AVR GCC / avr-libc.
 *====================================================================*/
#define F_CPU 8000000UL
#include <avr/io.h>
#include <stdint.h>

#define TWI_TIMEOUT        60000U
#define EEPROM_ADDR        0x50U
#define DS1307_ADDR        0x68U

/* Индивидуальный вариант 4 (табл. 9.9): ячейка 0x003F, байт 0x67,
 * регистр DS1307 0x00 (секунды). */
#define EEPROM_CELL        0x003FU
#define EEPROM_TEST_VALUE  0x67U
#define DS1307_TEST_REG    0x00U

static uint8_t TWI_Wait(void)
{
    uint16_t timeout = TWI_TIMEOUT;
    while ((TWCR & (1U << TWINT)) == 0U) {
        if (--timeout == 0U) return 0U;
    }
    return 1U;
}

static uint8_t TWI_Status(void)
{
    return (uint8_t)(TWSR & 0xF8U);
}

static void TWI_Init_100k(void)
{
    TWSR &= (uint8_t)~((1U << TWPS1) | (1U << TWPS0));
    TWBR = 32U;
    TWCR = (1U << TWEN);
}

static uint8_t TWI_Start(uint8_t address_rw)
{
    uint8_t status;

    TWCR = (1U << TWINT) | (1U << TWSTA) | (1U << TWEN);
    if (!TWI_Wait()) return 0U;
    status = TWI_Status();
    if (status != 0x08U && status != 0x10U) return 0U;

    TWDR = address_rw;
    TWCR = (1U << TWINT) | (1U << TWEN);
    if (!TWI_Wait()) return 0U;
    status = TWI_Status();

    if ((address_rw & 1U) == 0U) return (status == 0x18U);
    return (status == 0x40U);
}

static uint8_t TWI_Write(uint8_t data)
{
    TWDR = data;
    TWCR = (1U << TWINT) | (1U << TWEN);
    if (!TWI_Wait()) return 0U;
    return (TWI_Status() == 0x28U);
}

static uint8_t TWI_ReadNack(uint8_t *data)
{
    if (data == 0) return 0U;
    TWCR = (1U << TWINT) | (1U << TWEN);
    if (!TWI_Wait()) return 0U;
    if (TWI_Status() != 0x58U) return 0U;
    *data = TWDR;
    return 1U;
}

static uint8_t TWI_Stop(void)
{
    uint16_t timeout = TWI_TIMEOUT;

    TWCR = (1U << TWINT) | (1U << TWSTO) | (1U << TWEN);
    while ((TWCR & (1U << TWSTO)) != 0U) {
        if (--timeout == 0U) return 0U;
    }
    return 1U;
}

static void ResultLED_Init(void)
{
    DDRB |= (1U << PB1);
    PORTB &= (uint8_t)~(1U << PB1);
}

static void ResultLED_Set(uint8_t state)
{
    if (state != 0U) PORTB |= (1U << PB1);
    else PORTB &= (uint8_t)~(1U << PB1);
}

static uint8_t EEPROM_WaitReady(void)
{
    uint16_t attempt;
    uint8_t status;

    for (attempt = 0U; attempt < 1000U; ++attempt) {
        if (TWI_Start((uint8_t)(EEPROM_ADDR << 1))) {
            return TWI_Stop();
        }
        status = TWI_Status();
        (void)TWI_Stop();
        if (status != 0x20U) return 0U; /* SLA+W, NACK. */
    }
    return 0U;
}

static uint8_t EEPROM_WriteByte(uint16_t mem, uint8_t data)
{
    if (mem > 0x1FFFU) return 0U;
    if (!TWI_Start((uint8_t)(EEPROM_ADDR << 1))) goto error;
    if (!TWI_Write((uint8_t)(mem >> 8))) goto error;
    if (!TWI_Write((uint8_t)mem)) goto error;
    if (!TWI_Write(data)) goto error;
    if (!TWI_Stop()) return 0U;
    return EEPROM_WaitReady();

error:
    (void)TWI_Stop();
    return 0U;
}

static uint8_t EEPROM_ReadByte(uint16_t mem, uint8_t *data)
{
    if (data == 0 || mem > 0x1FFFU) return 0U;
    if (!TWI_Start((uint8_t)(EEPROM_ADDR << 1))) goto error;
    if (!TWI_Write((uint8_t)(mem >> 8))) goto error;
    if (!TWI_Write((uint8_t)mem)) goto error;
    if (!TWI_Start((uint8_t)((EEPROM_ADDR << 1) | 1U)))
        goto error;
    if (!TWI_ReadNack(data)) goto error;
    return TWI_Stop();

error:
    (void)TWI_Stop();
    return 0U;
}

static uint8_t DS1307_WriteBytes(uint8_t reg,
                                 const uint8_t *data,
                                 uint8_t count)
{
    uint8_t i;

    if (data == 0 || count == 0U) return 0U;
    if (!TWI_Start((uint8_t)(DS1307_ADDR << 1))) goto error;
    if (!TWI_Write(reg)) goto error;
    for (i = 0U; i < count; ++i) {
        if (!TWI_Write(data[i])) goto error;
    }
    return TWI_Stop();

error:
    (void)TWI_Stop();
    return 0U;
}

static uint8_t DS1307_ReadReg(uint8_t reg, uint8_t *data)
{
    if (data == 0) return 0U;
    if (!TWI_Start((uint8_t)(DS1307_ADDR << 1))) goto error;
    if (!TWI_Write(reg)) goto error;
    if (!TWI_Start((uint8_t)((DS1307_ADDR << 1) | 1U)))
        goto error;
    if (!TWI_ReadNack(data)) goto error;
    return TWI_Stop();

error:
    (void)TWI_Stop();
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

    ResultLED_Init();
    TWI_Init_100k();

    if (!EEPROM_WriteByte(EEPROM_CELL, EEPROM_TEST_VALUE))
        goto error;
    if (!EEPROM_ReadByte(EEPROM_CELL, &value)) goto error;
    g_eeprom_read = value;
    if (value != EEPROM_TEST_VALUE) goto error;

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
