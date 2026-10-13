#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

// Лабораторная работа №4, задача 10а: задержка Примера 2 вдвое меньше.
// Тот же бегущий огонь, LOOP_START равен 32768: полный проход счётчика
// даёт 32768 итераций вместо 65535, время паузы уменьшается вдвое.
// Счётчики volatile, иначе оптимизатор удаляет пустой цикл.

#define LOOP_START 32768
#define LOOP_REPEAT 1

void port_init(void)
{
    PORTD = 0x01; // включить бит 0 порта D
    DDRD = 0xFF;  // порт D на выход
}

void init_devices(void)
{
    cli();
    port_init();
    MCUCR = 0x00;
    GICR = 0x00;
    TIMSK = 0x00;
    sei();
}

int main(void)
{
    volatile uint16_t i;
    volatile uint8_t r;
    init_devices();
    while (1)
    {
        for (r = 0; r < LOOP_REPEAT; r++)
        {
            for (i = LOOP_START; i; i++)
            {
                // пустой цикл, задание задержки
            }
        }
        PORTD = (uint8_t)(PORTD << 1); // новое значение порта D
        if (PORTD == 0)
            PORTD = 1; // значение было нулевым, вернуть единицу
    }
}
