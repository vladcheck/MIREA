/*
 * Задание 11c по ЛР4
 * Добавлен счётчик зарегистрированных нажатий клавиш (0..99),
 * выводимый на свободной строке дисплея (page 4).
 * После достижения 99 счётчик начинается заново с 0.
 */
#ifndef F_CPU
#define F_CPU 8000000UL
#endif
#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

/* ---------------- Пины графического дисплея ---------------- */
#define GLCD_DATA_DDR DDRA
#define GLCD_DATA_PORT PORTA
#define GLCD_CTRL_DDR DDRD
#define GLCD_CTRL_PORT PORTD
#define GLCD_CS1 PD0
#define GLCD_CS2 PD1
#define GLCD_RST PD2
#define GLCD_RW PD3
#define GLCD_DI PD4
#define GLCD_E PD5

/* ---------------- Пины матричной клавиатуры ---------------- */
#define KP_DDR DDRB
#define KP_PORT PORTB
#define KP_PINR PINB

static void glcd_init(void);
static void glcd_clear(void);
static void glcd_clear_area(uint8_t x0, uint8_t x1, uint8_t page);
static void glcd_put_char(uint8_t x, uint8_t page, char c);
static void glcd_puts(uint8_t x, uint8_t page, const char *s);
static char keypad_getkey_event(void);
static void screen_draw_static(void);
static void screen_show_key(char key);
static void screen_show_buffer(const char *buf);

/* Таблица соответствия строк и столбцов символам клавиатуры */
static const char keymap[4][4] = {
    {'1', '2', '3', 'A'},
    {'4', '5', '6', 'B'},
    {'7', '8', '9', 'C'},
    {'*', '0', '#', 'D'}};

/* Небольшой набор символов 5x7, достаточный для ЛР */
static const uint8_t *font5x7(char c)
{
    static const uint8_t space[5] = {0x00, 0x00, 0x00, 0x00, 0x00};
    static const uint8_t colon[5] = {0x00, 0x36, 0x36, 0x00, 0x00};
    static const uint8_t star_[5] = {0x14, 0x08, 0x3E, 0x08, 0x14};
    static const uint8_t hash_[5] = {0x14, 0x7F, 0x14, 0x7F, 0x14};
    static const uint8_t dash_[5] = {0x08, 0x08, 0x08, 0x08, 0x08};
    static const uint8_t d0[5] = {0x3E, 0x51, 0x49, 0x45, 0x3E};
    static const uint8_t d1[5] = {0x00, 0x42, 0x7F, 0x40, 0x00};
    static const uint8_t d2[5] = {0x42, 0x61, 0x51, 0x49, 0x46};
    static const uint8_t d3[5] = {0x21, 0x41, 0x45, 0x4B, 0x31};
    static const uint8_t d4[5] = {0x18, 0x14, 0x12, 0x7F, 0x10};
    static const uint8_t d5[5] = {0x27, 0x45, 0x45, 0x45, 0x39};
    static const uint8_t d6[5] = {0x3C, 0x4A, 0x49, 0x49, 0x30};
    static const uint8_t d7[5] = {0x01, 0x71, 0x09, 0x05, 0x03};
    static const uint8_t d8[5] = {0x36, 0x49, 0x49, 0x49, 0x36};
    static const uint8_t d9[5] = {0x06, 0x49, 0x49, 0x29, 0x1E};
    static const uint8_t A_[5] = {0x7E, 0x11, 0x11, 0x11, 0x7E};
    static const uint8_t B_[5] = {0x7F, 0x49, 0x49, 0x49, 0x36};
    static const uint8_t C_[5] = {0x3E, 0x41, 0x41, 0x41, 0x22};
    static const uint8_t D_[5] = {0x7F, 0x41, 0x41, 0x22, 0x1C};
    static const uint8_t E_[5] = {0x7F, 0x49, 0x49, 0x49, 0x41};
    static const uint8_t F_[5] = {0x7F, 0x09, 0x09, 0x09, 0x01};
    static const uint8_t K_[5] = {0x7F, 0x08, 0x14, 0x22, 0x41};
    static const uint8_t L_[5] = {0x7F, 0x40, 0x40, 0x40, 0x40};
    static const uint8_t R_[5] = {0x7F, 0x09, 0x19, 0x29, 0x46};
    static const uint8_t S_[5] = {0x46, 0x49, 0x49, 0x49, 0x31};
    static const uint8_t U_[5] = {0x3F, 0x40, 0x40, 0x40, 0x3F};
    static const uint8_t Y_[5] = {0x07, 0x08, 0x70, 0x08, 0x07};
    switch (c)
    {
    case ' ':
        return space;
    case ':':
        return colon;
    case '*':
        return star_;
    case '#':
        return hash_;
    case '-':
        return dash_;
    case '0':
        return d0;
    case '1':
        return d1;
    case '2':
        return d2;
    case '3':
        return d3;
    case '4':
        return d4;
    case '5':
        return d5;
    case '6':
        return d6;
    case '7':
        return d7;
    case '8':
        return d8;
    case '9':
        return d9;
    case 'A':
        return A_;
    case 'B':
        return B_;
    case 'C':
        return C_;
    case 'D':
        return D_;
    case 'E':
        return E_;
    case 'F':
        return F_;
    case 'K':
        return K_;
    case 'L':
        return L_;
    case 'R':
        return R_;
    case 'S':
        return S_;
    case 'U':
        return U_;
    case 'Y':
        return Y_;
    default:
        return space;
    }
}

static void glcd_pulse_enable(void)
{
    GLCD_CTRL_PORT |= (1U << GLCD_E);
    _delay_us(2);
    GLCD_CTRL_PORT &= ~(1U << GLCD_E);
    _delay_us(2);
}

static void glcd_select_chip(uint8_t chip)
{
    GLCD_CTRL_PORT &= ~((1U << GLCD_CS1) | (1U << GLCD_CS2));
    if (chip == 1)
        GLCD_CTRL_PORT |= (1U << GLCD_CS1);
    else
        GLCD_CTRL_PORT |= (1U << GLCD_CS2);
}

static void glcd_write_raw(uint8_t chip, uint8_t is_data, uint8_t value)
{
    glcd_select_chip(chip);
    if (is_data)
        GLCD_CTRL_PORT |= (1U << GLCD_DI);
    else
        GLCD_CTRL_PORT &= ~(1U << GLCD_DI);
    GLCD_CTRL_PORT &= ~(1U << GLCD_RW); /* Режим записи */
    GLCD_DATA_PORT = value;
    glcd_pulse_enable();
    /* Запас времени вместо чтения busy-флага */
    _delay_us(10);
}

static void glcd_command_both(uint8_t cmd)
{
    glcd_write_raw(1, 0, cmd);
    glcd_write_raw(2, 0, cmd);
}

static void glcd_set_address(uint8_t x, uint8_t page)
{
    uint8_t chip = (x < 64) ? 1 : 2;
    uint8_t col = x & 0x3F;
    glcd_write_raw(chip, 0, (uint8_t)(0xB8 | (page & 0x07)));
    glcd_write_raw(chip, 0, (uint8_t)(0x40 | col));
}

static void glcd_draw_byte(uint8_t x, uint8_t page, uint8_t data)
{
    uint8_t chip = (x < 64) ? 1 : 2;
    glcd_set_address(x, page);
    glcd_write_raw(chip, 1, data);
}

static void glcd_clear(void)
{
    for (uint8_t page = 0; page < 8; page++)
    {
        for (uint8_t x = 0; x < 128; x++)
        {
            glcd_draw_byte(x, page, 0x00);
        }
    }
}

static void glcd_clear_area(uint8_t x0, uint8_t x1, uint8_t page)
{
    for (uint8_t x = x0; x <= x1; x++)
    {
        glcd_draw_byte(x, page, 0x00);
    }
}

static void glcd_put_char(uint8_t x, uint8_t page, char c)
{
    const uint8_t *bmp = font5x7(c);
    for (uint8_t i = 0; i < 5; i++)
    {
        glcd_draw_byte((uint8_t)(x + i), page, bmp[i]);
    }
    glcd_draw_byte((uint8_t)(x + 5), page, 0x00);
}

static void glcd_puts(uint8_t x, uint8_t page, const char *s)
{
    while (*s != '\0')
    {
        glcd_put_char(x, page, *s++);
        x = (uint8_t)(x + 6);
        if (x > 122)
            break;
    }
}

static void glcd_init(void)
{
    GLCD_DATA_DDR = 0xFF;
    GLCD_CTRL_DDR |= (1U << GLCD_CS1) | (1U << GLCD_CS2) |
                     (1U << GLCD_RST) | (1U << GLCD_RW) |
                     (1U << GLCD_DI) | (1U << GLCD_E);
    GLCD_CTRL_PORT &= ~((1U << GLCD_CS1) | (1U << GLCD_CS2) |
                        (1U << GLCD_RW) | (1U << GLCD_DI) |
                        (1U << GLCD_E));
    _delay_ms(20);
    /* Аппаратный сброс дисплея */
    GLCD_CTRL_PORT &= ~(1U << GLCD_RST);
    _delay_ms(5);
    GLCD_CTRL_PORT |= (1U << GLCD_RST);
    _delay_ms(5);
    glcd_command_both(0x3F); /* Display ON */
    glcd_command_both(0xC0); /* Start line = 0 */
    glcd_clear();
}

static void keypad_init(void)
{
    /* Коммутация стенда (фактическая): Y0..Y3 -> PB0..PB3 - выходы
       сканирования, X0..X3 -> PB4..PB7 - входы опроса. Группы X и Y
       перепутаны местами относительно методички, код адаптирован. */
    KP_DDR = 0x0F;
    KP_PORT = 0xFF; /* На входах включены pull-up, линии сканирования в "1" */
}

static char keypad_scan_raw(void)
{
    for (uint8_t row = 0; row < 4; row++)
    {
        KP_PORT |= 0x0F;                  /* Все линии сканирования в "1" */
        KP_PORT &= (uint8_t)~(1U << row); /* Текущая линия Y в "0" */
        _delay_us(5);
        uint8_t cols = (uint8_t)((KP_PINR >> 4) & 0x0F); /* уровни X0..X3 */
        if (cols != 0x0F)
        {
            for (uint8_t col = 0; col < 4; col++)
            {
                if ((cols & (1U << col)) == 0)
                {
                    /* keymap[X][Y]: опрошен = X (col), активна = Y (row) */
                    return keymap[col][row];
                }
            }
        }
    }
    return 0;
}

static char keypad_getkey_event(void)
{
    static char last = 0;
    char cur = keypad_scan_raw();
    if (cur != 0 && last == 0)
    {
        _delay_ms(20);
        if (keypad_scan_raw() == cur)
        {
            last = cur;
            return cur;
        }
    }
    if (cur == 0)
        last = 0;
    return 0;
}

static void screen_draw_static(void)
{
    glcd_clear();
    glcd_puts(0, 0, "KEY:");
    glcd_puts(0, 2, "BUF:");
    glcd_puts(0, 4, "CNT:");
    glcd_puts(0, 6, "A CLR B BS");
}

static void screen_show_key(char key)
{
    char s[2] = {key, '\0'};
    glcd_clear_area(30, 60, 0);
    glcd_puts(30, 0, s);
}

static void screen_show_buffer(const char *buf)
{
    glcd_clear_area(30, 127, 2);
    glcd_puts(30, 2, buf);
}

int main(void)
{
    char buffer[17];
    uint8_t len = 0;
    uint8_t count = 0;
    buffer[0] = '\0';
    keypad_init();
    glcd_init();
    screen_draw_static();
    while (1)
    {
        char key = keypad_getkey_event();
        if (key != 0)
        {
            /* Счётчик нажатий 0..99, после 99 снова с 0 */
            if (count < 99)
                count++;
            else
                count = 0;
            {
                char s[3];
                s[0] = (char)('0' + count / 10);
                s[1] = (char)('0' + count % 10);
                s[2] = '\0';
                glcd_clear_area(30, 60, 4);
                glcd_puts(30, 4, s);
            }
            screen_show_key(key);
            if (key == 'A')
            {
                len = 0;
                buffer[0] = '\0';
            }
            else if (key == 'B')
            {
                if (len > 0)
                {
                    len--;
                    buffer[len] = '\0';
                }
            }
            else
            {
                if (len < (sizeof(buffer) - 1))
                {
                    buffer[len++] = key;
                    buffer[len] = '\0';
                }
            }
            screen_show_buffer(buffer);
        }
    }
}
