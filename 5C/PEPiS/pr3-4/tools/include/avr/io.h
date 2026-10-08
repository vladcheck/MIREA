/* Минимальный стуб <avr/io.h> для ATmega32 — только то, что использует
 * main_variant4_avr.c. Для синтаксической проверки clang -fsyntax-only;
 * в прошивке используется реальный avr-libc.
 */
#ifndef STUB_AVR_IO_H
#define STUB_AVR_IO_H

#include <stdint.h>

/* TWI-регистры ATmega32 */
extern volatile uint8_t TWBR;
extern volatile uint8_t TWSR;
extern volatile uint8_t TWAR;
extern volatile uint8_t TWDR;
extern volatile uint8_t TWCR;
/* порт B */
extern volatile uint8_t PINB;
extern volatile uint8_t DDRB;
extern volatile uint8_t PORTB;

/* номера битов */
#define TWINT 7
#define TWEA  6
#define TWSTA 5
#define TWSTO 4
#define TWWC  3
#define TWEN  2
#define TWIE  0
#define TWPS1 1
#define TWPS0 0

#define PB1 1

#endif /* STUB_AVR_IO_H */
