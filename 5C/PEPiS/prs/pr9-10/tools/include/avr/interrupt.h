/* Минимальный стуб <avr/interrupt.h> — макрос ISR для синтаксической
 * проверки clang -fsyntax-only; в прошивке используется реальный avr-libc.
 */
#ifndef STUB_AVR_INTERRUPT_H
#define STUB_AVR_INTERRUPT_H

#define ISR(vector) void vector(void)

#define TIMER0_COMP_vect TIMER0_COMP_vect_stub

static inline void sei(void)
{
    /* на хосте ничего не делает; в прошивке разрешает прерывания */
}

#endif /* STUB_AVR_INTERRUPT_H */
