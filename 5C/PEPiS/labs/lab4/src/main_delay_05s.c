#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

// Лабораторная работа №4, задача 11г (вариант 4): переключение разрядов
// каждые 0,5 с. Тот же бегущий огонь Примера 2, константы подобраны
// подсчётом тактов по дизассемблированному коду при тактировании 8 МГц.
// Одна итерация пустого цикла занимает 19 тактов, полный проход счётчика
// при LOOP_START равном 12904 даёт 52632 итерации, четыре повтора дают
// около 4 000 000 тактов, то есть около 0,5 с между переключениями.
// Счётчики volatile, иначе оптимизатор удаляет пустой цикл.

#define LOOP_START 12904
#define LOOP_REPEAT 4

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
