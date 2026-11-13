/* Минимальный стуб <avr/io.h> для ATmega32 — только то, что используют
 * main_example_avr.c и main_variant4_avr.c. Для синтаксической проверки
 * clang -fsyntax-only; в прошивке используется реальный avr-libc.
 *
 * Частота модели задаётся в Proteus (генератор 8 МГц), макрос F_CPU
 * нужен только расчётным константам препроцессора.
 */
#ifndef STUB_AVR_IO_H
#define STUB_AVR_IO_H

#include <stdint.h>

/* порт A (индикатор) */
extern volatile uint8_t PINA;
extern volatile uint8_t DDRA;
extern volatile uint8_t PORTA;

/* Timer/Counter0 */
extern volatile uint8_t TCCR0;
extern volatile uint8_t TCNT0;
extern volatile uint8_t OCR0;
extern volatile uint8_t TIMSK;
extern volatile uint8_t TIFR;

/* номера битов */
#define PA0 0
#define PA1 1
#define PA2 2
#define PA3 3
#define PA4 4
#define PA5 5
#define PA6 6
#define PA7 7

#define OCIE0 1 /* прерывание по совпадению Timer0 */
#define OCF0  1 /* флаг совпадения Timer0 */

#define CS00 0 /* предделитель Timer0: биты CS02..CS00 */
#define CS01 1
#define CS02 2

#define WGM01 3 /* CTC-режим Timer0 (WGM01 = 1) */

#endif /* STUB_AVR_IO_H */
