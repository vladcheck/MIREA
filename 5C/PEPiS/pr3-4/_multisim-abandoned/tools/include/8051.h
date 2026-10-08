/* Минимальный стандартный заголовок 8051.h (совместимый с SDCC/Keil)
 * для синтаксической проверки clang -fsyntax-only. В прошивке
 * используется реальный заголовок компилятора (SDCC или Keil C51).
 */
#ifndef STUB_8051_H
#define STUB_8051_H

#define __xdata    /* пусто: квалификатор адресного пространства SDCC */
#define xdata      /* пусто: квалификатор Keil C51 (для учебного примера) */
#define __sbit unsigned char

/* Бит P1.0 — светодиод ошибки. В SDCC: sbit P1_0 = 0x90; */
__sbit P1_0;

#endif /* STUB_8051_H */
