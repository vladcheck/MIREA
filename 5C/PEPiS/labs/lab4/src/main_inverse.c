#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

// Лабораторная работа №4, задача 14, инверсный бегущий огонь.
// Единственная единица движется от старшего разряда к младшему:
// 0x80, 0x40, ..., 0x01, затем цикл повторяется.
// Пауза между шагами 300 мс.

int main(void)
{
    uint8_t pattern;
    DDRD = 0xFF; // порт D на выход
    while (1)
    {
        pattern = 0x80; // начать со старшего разряда
        while (pattern != 0)
        {
            PORTD = pattern;
            _delay_ms(300);
            pattern = (uint8_t)(pattern >> 1); // сдвиг к младшему
        }
    }
}
