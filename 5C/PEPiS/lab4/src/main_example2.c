#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

// Лабораторная работа №4, учебный пример 2, бегущий огонь.
// По порту D циклически сдвигается единственная единица: младший разряд
// зажигается, затем бит движется к старшему, после 0x80 цикл повторяется.
// Задержка между переключениями задана пустым циклом, как в методичке:
// время переключения удобно измерять симулятором AVR Studio (задачи 10, 11).
// LOOP_START равен 1, полный проход счетчика 65535 итерации.
// Задача 10а (задержка вдвое меньше): LOOP_START равен 32768.
// Задача 10б (задержка вчетверо больше): LOOP_REPEAT равен 4.

#define LOOP_START 1
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
    uint16_t i;
    uint8_t r;
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
