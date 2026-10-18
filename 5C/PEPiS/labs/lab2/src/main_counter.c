#include "stm32f4xx.h"

// Лабораторная работа № 2, вариант 4, задание 5.3 для самостоятельной работы.
// Простейший счётчик секунд с индикацией на четырёхразрядном семисегментном
// индикаторе: значение 0000-9999 увеличивается каждую секунду.
// Схема: сегменты a-g -> PA0-PA6 (активный высокий уровень),
// разряды -> PC0-PC3 через ключевые транзисторы NPN (активный высокий уровень).
// Секундный интервал выдержан аппаратным таймером SysTick (опрос флага COUNTFLAG,
// без прерываний), поэтому длительность секунды не зависит от оптимизации
// компилятора и looptime сканирования. Ядро работает на HSI 16 МГц
// (SystemCoreClock), предделитель SysTick вычисляется автоматически.

// Таблица кодов сегментов для цифр 0-9 (вариант с общим катодом, табл. 1 методички).
// Отображение бит на выводы: бит0=a (PA0), ..., бит6=g (PA6).
static const uint8_t digit_code[10] = {
    0x3F, // 0 -> a b c d e f
    0x06, // 1 -> b c
    0x5B, // 2 -> a b d e g
    0x4F, // 3 -> a b c d g
    0x66, // 4 -> b c f g
    0x6D, // 5 -> a c d f g
    0x7D, // 6 -> a c d e f g
    0x07, // 7 -> a b c
    0x7F, // 8 -> a b c d e f g
    0x6F  // 9 -> a b c d f g
};

// Короткая задержка удержания одного разряда при сканировании.
static void delay_short(volatile uint32_t t) {
    while (t--) __NOP();
}

// Разложить значение 0-9999 на четыре десятичные цифры (тысячи -> единицы).
static void split_digits(int value, int digits[4]) {
    digits[0] = (value / 1000) % 10; // тысячи
    digits[1] = (value / 100) % 10;  // сотни
    digits[2] = (value / 10) % 10;   // десятки
    digits[3] = (value / 1) % 10;    // единицы
}

int main(void) {
    // 1. Включаем тактирование портов A и C (шина AHB1).
    //    Фиктивное чтение — дождаться стабилизации тактирования,
    //    прежде чем обращаться к регистрам GPIO.
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOCEN;
    volatile uint32_t clk_tmp = RCC->AHB1ENR;
    (void)clk_tmp;

    // 2. Настраиваем PA0-PA6 (сегменты a-g) как выходы push-pull
    for (int i = 0; i <= 6; i++) {
        GPIOA->MODER   &= ~(0x3U << (i * 2U));
        GPIOA->MODER   |=  (0x1U << (i * 2U)); // 01 — выход
        GPIOA->OTYPER  &= ~(1U << i);          // 0 — push-pull
        GPIOA->OSPEEDR &= ~(0x3U << (i * 2U));
        GPIOA->PUPDR   &= ~(0x3U << (i * 2U));
    }

    // 3. Настраиваем PC0-PC3 (катоды разрядов) как выходы push-pull
    for (int i = 0; i < 4; i++) {
        GPIOC->MODER   &= ~(0x3U << (i * 2U));
        GPIOC->MODER   |=  (0x1U << (i * 2U)); // 01 — выход
        GPIOC->OTYPER  &= ~(1U << i);
        GPIOC->OSPEEDR &= ~(0x3U << (i * 2U));
        GPIOC->PUPDR   &= ~(0x3U << (i * 2U));
    }

    int seconds = 0; // счётчик секунд 0-9999
    int digits[4] = {0, 0, 0, 0};

    // 4. Настраиваем SysTick на одно срабатывание в секунду:
    //    LOAD = число тактов ядра за 1 с (при HSI 16 МГц укладывается
    //    в 24-битный регистр). Флаг COUNTFLAG опрашиваем вручную,
    //    прерывания не используем.
    SystemCoreClockUpdate();
    SysTick->LOAD = (SystemCoreClock - 1U);
    SysTick->VAL  = 0U;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;

    while (1) {
        split_digits(seconds, digits);

        // 5. Отображаем текущее значение ровно одну секунду:
        //    сканируем разряды, пока SysTick не досчитает до 1 с.
        //    Разряды: гашение низким уровнем («0»), включение высоким («1»).
        //    Флаг COUNTFLAG проверяется только между полными проходами:
        //    чтение CTRL внутри сканирования сбрасывало бы флаг раньше
        //    времени и секунда никогда бы не закончилась.
        SysTick->VAL = 0U; // перезапустить отсчёт секунды
        while ((SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk) == 0U) {
            for (int pos = 0; pos < 4; pos++) {
                GPIOC->BSRR = (0xFU << 16U); // погасить все разряды
                GPIOA->ODR = (GPIOA->ODR & 0xFF80U) | digit_code[digits[pos]];
                GPIOC->BSRR = (1U << pos); // включить разряд pos
                delay_short(1500);
            }
        }

        // 6. Увеличить счётчик; после 9999 начать заново с 0000
        seconds++;
        if (seconds > 9999) {
            seconds = 0;
        }
    }
}
