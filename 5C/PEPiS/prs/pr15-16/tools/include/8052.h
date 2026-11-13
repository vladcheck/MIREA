/*====================================================================
 * Заглушка заголовка <8052.h> для проверки синтаксиса компилятором
 * clang (практическая работа 15-16, курс PEPiS).
 *
 * Целевой инструментарий для сборки прошивки МК-52: SDCC
 * (platformio, platform = intel_mcs51), который поставляет собственный
 * «настоящий» <8052.h> с объявлениями __sfr/__sbit/__at. Под SDCC этот
 * файл не используется (см. ветку #ifdef __SDCC в исходниках).
 *
 * Здесь специальные регистры (SFR) и биты объявлены обычными
 * volatile-переменными: это достаточно для «clang -fsyntax-only
 * -Wall -Wextra», потому что проверяется только синтаксис и
 * типовая дисциплина кода, а адресация регистров к синтаксису
 * отношения не имеет. Семантика «чтение модифицирует / запись
 * сразу видна» сохранена через volatile.
 *====================================================================*/
#ifndef PEPIS_STUB_8052_H
#define PEPIS_STUB_8052_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* --- Порты P0..P3 (адреса 80h, 90h, A0h, B0h) ---------------------- */
extern volatile uint8_t P0;
extern volatile uint8_t P1;
extern volatile uint8_t P2;
extern volatile uint8_t P3;

/* --- Регистр разрешения прерываний IE (адрес A8h) ------------------ */
extern volatile uint8_t IE;
/* Биты IE: EA (A8h.7), ET2 (A8h.5) используются в программах. */

/* --- Группа таймера/счётчика 2 (SFR таймера 2) --------------------- */
extern volatile uint8_t T2CON;  /* управление и контроль, адрес C8h  */
extern volatile uint8_t RCAP2L; /* младший байт перезагрузки, CAh    */
extern volatile uint8_t RCAP2H; /* старший байт перезагрузки, CBh    */
extern volatile uint8_t TL2;    /* младший байт счётчика, CCh        */
extern volatile uint8_t TH2;    /* старший байт счётчика, CDh        */

/* --- Биты регистра T2CON (битовая адресация C8h) ------------------- */
extern volatile uint8_t TF2;    /* C8h.7 флаг переполнения таймера 2  */
extern volatile uint8_t EXF2;   /* C8h.6 флаг перепада на T2EX       */
extern volatile uint8_t RCLK;   /* C8h.5 приём UART на таймере 2     */
extern volatile uint8_t TCLK;   /* C8h.4 передача UART на таймере 2  */
extern volatile uint8_t EXEN2;  /* C8h.3 разрешение захвата/перезагр.*/
extern volatile uint8_t TR2;    /* C8h.2 запуск таймера 2            */
extern volatile uint8_t C_T2;   /* C8h.1 счётчик/таймер              */
extern volatile uint8_t CP_RL2; /* C8h.0 захват/автоперезагрузка     */

/* --- Биты порта P1 (битовая адресация 90h) ------------------------- */
extern volatile uint8_t P1_0;   /* 90h.0 вывод P1.0, линия ШИМ       */
extern volatile uint8_t T2;     /* 90h.0 альтернативная функция: T2  */
extern volatile uint8_t T2EX;   /* 90h.1 альтернативная функция: T2EX*/

/* --- Биты регистра IE (битовая адресация A8h) ---------------------- */
extern volatile uint8_t EA;     /* A8h.7 глобальное разрешение       */
extern volatile uint8_t ET2;    /* A8h.5 прерывание от таймера 2     */

#ifdef __cplusplus
}
#endif

#endif /* PEPIS_STUB_8052_H */
