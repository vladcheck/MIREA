#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

// Лабораторная работа №4, задача 13, бегущий огонь с накоплением.
// Вначале загорается бит PD0, затем к нему добавляется PD1 и так далее,
// пока не загорятся все светодиоды порта D, после чего цикл повторяется.
// Пауза между шагами 300 мс.

int main(void)
{
    uint8_t k;
    uint8_t pattern;
    DDRD = 0xFF; // порт D на выход
    while (1)
    {
        pattern = 0;
        for (k = 0; k < 8; k++)
        {
            pattern |= (uint8_t)(1u << k); // добавить очередной разряд
            PORTD = pattern;
            _delay_ms(300);
        }
    }
}
