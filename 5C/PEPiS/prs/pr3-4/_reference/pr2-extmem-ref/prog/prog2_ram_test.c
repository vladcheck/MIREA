/*====================================================================
 * ПР №2, Задание 1 — тестирование внешнего ОЗУ 1 Кбайт (Си, SDCC/Keil C51)
 * Демо: Вар.1 — ОЗУ 8 Кбайт, XX=0xAA, ZZZ=0x0800. Для Вар.2-6 см. defines ниже.
 *   Вар.2: N=2К  XX=0x55 ZZZ=0x0100
 *   Вар.3: N=8К  XX=0x00 ZZZ=0x0C00
 *   Вар.4: N=8К  XX=0xFF ZZZ=0x1000
 *   Вар.5: N=8К  XX=0x55 ZZZ=0x1400
 *   Вар.6: N=2К  XX=0xAA ZZZ=0x0400
 * Аппаратура: МК-51, защелка 74LS373 (ALE), P0=AD0-AD7, P2=A8-A15,
 * /WR=P3.6, /RD=P3.7. Светодиод ошибки на P1.0 (0=норма, 1=ошибка).
 * Компиляция: sdcс prog2_ram_test.c  или  Keil C51 (память модели SMALL, xdata).
 *====================================================================*/
#include <8051.h>              /* SFR: P0..P3, DPTR; __xdata для XRAM */

/* --- вариант (править здесь) --- */
#define TEST_ADDR  ((unsigned int)0x0800)  /* ZZZ, Вар.1 */
#define TEST_PAT   ((unsigned char)0xAA)   /* XX, Вар.1 */
#define TEST_SIZE  ((unsigned int)1024)    /* всегда 1 Кбайт по ТЗ */

void main(void)
{
    __xdata unsigned char *ptr;  /* указатель во внешнее ОЗУ (MOVX) */
    unsigned char back;          /* прочитанное значение */
    unsigned int i;              /* счётчик 0..1023 (16 бит — поэтому Си удобнее asm) */

    P1_0 = 0;                    /* LED погашен */
    ptr = (__xdata unsigned char *)TEST_ADDR;  /* DPTR := ZZZ */

    for (i = 0; i < TEST_SIZE; i++)   /* 1024 ячейки, двойной цикл не нужен — int 16-битный */
    {
        *ptr = TEST_PAT;         /* movx @dptr,a — запись (строб /WR) */
        back = *ptr;             /* movx a,@dptr — чтение (строб /RD) */
        if (back != TEST_PAT)    /* сравнение записанного и считанного */
        {
            P1_0 = 1;            /* несовпадение -> зажечь LED */
            break;               /* останов на первой плохой ячейке */
        }
        ptr++;                   /* DPTR++ (inc dptr) */
    }
    while (1) ;                  /* останов (точка останова отладчика) */
}
