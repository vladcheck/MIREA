/* Практическая работа N1. Стенд "Учтех-Профи", МК STM32F100C8Tx.
 * Периферия (обозначения по ГОСТ 2.710-81): HL1-8 (PA0-PA7), 7-сегментный
 * индикатор HG1 (PB8-PB15, сегменты A-G,DP через R11-R18 270 Ом, общий катод
 * на GND), кнопки SB1-SB4 (PC13, PC14, PC15, PD0, активный уровень -
 * замыкание на +3V3), потенциометр RP1 (PB0 = ADC12_IN8).
 * Нумерация цепей N01-N25 - см. таблицу цепей на схеме и OTCHET.md.
 * Сборка: arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -nostdlib -nostartfiles
 *   -T stm32f100.ld (без libc: типы заданы вручную, newlib не требуется).
 */
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;

#define RCC_BASE   0x40021000u
#define GPIOA_BASE 0x40010800u
#define GPIOB_BASE 0x40010C00u
#define GPIOC_BASE 0x40011000u
#define GPIOD_BASE 0x40011400u
#define ADC1_BASE  0x40012400u

#define REG(a) (*(volatile uint32_t *)(a))
#define RCC_APB2ENR (RCC_BASE + 0x18u)
#define GPIO_CRL(g) ((g) + 0x00u)
#define GPIO_CRH(g) ((g) + 0x04u)
#define GPIO_IDR(g) ((g) + 0x08u)
#define GPIO_ODR(g) ((g) + 0x0Cu)
#define GPIO_BSRR(g) ((g) + 0x10u)
#define GPIO_BRR(g) ((g) + 0x14u)

/* Индикатор с общим катодом: сегмент горит единицей. Порядок бит: A B C D E F G DP */
static const uint8_t DIGIT_SEG[10] = {
    0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F
};

static void delay(volatile uint32_t n) { while (n--) { __asm__ volatile ("nop"); } }

/* PA0-PA7 - выходы push-pull 2 МГц (HL1-8, цепи N03-N10) */
static void leds_init(void) {
    REG(RCC_APB2ENR) |= (1u << 2);          /* IOPAEN */
    REG(GPIO_CRL(GPIOA_BASE)) = 0x22222222u;
}

static void leds_set(uint8_t v) {
    REG(GPIO_ODR(GPIOA_BASE)) = (REG(GPIO_ODR(GPIOA_BASE)) & ~0xFFu) | v;
}

/* PB8-PB15 - выходы под сегменты HG1 (цепи N11-N18) */
static void seg_init(void) {
    REG(RCC_APB2ENR) |= (1u << 3);          /* IOPBEN */
    REG(GPIO_CRH(GPIOB_BASE)) = 0x22222222u;
}

static void seg_show(uint8_t digit) {
    uint32_t m = ((uint32_t)DIGIT_SEG[digit % 10]) << 8;
    REG(GPIO_ODR(GPIOB_BASE)) = (REG(GPIO_ODR(GPIOB_BASE)) & ~(0xFFu << 8)) | m;
}

/* PC13, PC14, PC15 - входы floating (SB1-SB3, цепи N19-N21);
 * PD0 - вход floating (SB4, цепь N22). Кнопки SPDT активно drives оба уровня. */
static void buttons_init(void) {
    REG(RCC_APB2ENR) |= (1u << 4) | (1u << 5);   /* IOPCEN | IOPDEN */
    /* PC13-PC15: MODE=00 (input), CNF=01 (floating): nibble 0x4 */
    REG(GPIO_CRH(GPIOC_BASE)) = (REG(GPIO_CRH(GPIOC_BASE)) & ~(0xFFFu << 20)) | (0x444u << 20);
    /* PD0: MODE=00, CNF=01 (floating) */
    REG(GPIOD_BASE + 0x00u) = (REG(GPIOD_BASE + 0x00u) & ~0xFu) | 0x4u;
}

static uint8_t button_pressed(void) {
    uint32_t c = REG(GPIO_IDR(GPIOC_BASE));
    uint32_t d = REG(GPIO_IDR(GPIOD_BASE));
    if (c & (1u << 13)) return 1;   /* SB1 */
    if (c & (1u << 14)) return 2;   /* SB2 */
    if (c & (1u << 15)) return 3;   /* SB3 */
    if (d & (1u << 0))  return 4;   /* SB4 */
    return 0;
}

int main(void) {
    uint8_t cnt = 0;
    leds_init();
    seg_init();
    buttons_init();
    /* ADC PB0 (N23) и далее - опрос в цикле расширения работы */
    for (;;) {
        uint8_t b = button_pressed();
        if (b == 1)      cnt++;            /* SB1: +1 */
        else if (b == 2) cnt--;            /* SB2: -1 */
        else if (b == 3) cnt = 0;          /* SB3: сброс */
        else if (b == 4) cnt ^= 0xFFu;     /* SB4: инверсия */
        leds_set(cnt);                     /* HL1-8: двоичный счётчик */
        seg_show(cnt % 10);                /* HG1: младшая цифра */
        delay(200000u);
    }
}
