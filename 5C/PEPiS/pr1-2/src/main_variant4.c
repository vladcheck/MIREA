/*
 * Практическая работа №1 — индивидуальный вариант 4 (таблица 9.3, STM32F1).
 * Входной вывод:  PA6 (ключ SW-SPDT подаёт лог. 1 или лог. 0).
 * Выходной вывод: PA7 (светодиод через резистор 270 Ом, активный высокий уровень).
 *
 * Оба вывода относятся к порту GPIOA, линии 6 и 7 < 8,
 * поэтому настройка выполняется в регистре GPIOA->CRL.
 * Тактирование включается для порта GPIOA (бит IOPAEN в RCC->APB2ENR).
 *
 * Сборка: CooCox CoIDE, компоненты CMSIS, CMSIS BOOT, RCC, GPIO.
 * Прошивка: PR1_STM32_GPIO_IO.hex — указывается в поле Program File
 * модели STM32F103C8 в Proteus.
 */

#include "stm32f10x.h"

#ifndef SET_BIT
#define SET_BIT(REG, BIT)     ((REG) |= (BIT))
#endif

#ifndef CLEAR_BIT
#define CLEAR_BIT(REG, BIT)   ((REG) &= ~(BIT))
#endif

#ifndef READ_BIT
#define READ_BIT(REG, BIT)    ((REG) & (BIT))
#endif

#ifndef MODIFY_REG
#define MODIFY_REG(REG, CLEARMASK, SETMASK) \
    do {                                     \
        CLEAR_BIT((REG), (CLEARMASK));       \
        SET_BIT((REG), (SETMASK));           \
    } while (0)
#endif

int main(void)
{
    /*
     * Включение тактирования порта GPIOA.
     * В варианте 4 используется только порт GPIOA,
     * поэтому достаточно установить бит IOPAEN.
     * Без тактирования порт не будет работать корректно.
     */
    SET_BIT(RCC->APB2ENR, RCC_APB2ENR_IOPAEN);

    /*
     * PA6 — входной вывод (ключ).
     * MODE6 = 00: режим входа.
     * CNF6  = 01: плавающий вход.
     *
     * Переключатель SW-SPDT явно соединяет вход PA6
     * либо с цепью питания (лог. 1), либо с общим проводом (лог. 0),
     * поэтому внутренняя подтяжка не требуется.
     */
    MODIFY_REG(GPIOA->CRL,
            GPIO_CRL_MODE6 | GPIO_CRL_CNF6,
            GPIO_CRL_CNF6_0);

    /*
     * PA7 — выход push-pull со скоростью 2 МГц (светодиод).
     * MODE7 = 10: выход 2 МГц.
     * CNF7  = 00: выход общего назначения push-pull.
     */
    MODIFY_REG(GPIOA->CRL,
            GPIO_CRL_MODE7 | GPIO_CRL_CNF7,
            GPIO_CRL_MODE7_1);

    while (1)
    {
        /*
         * Если на входе PA6 логическая единица,
         * устанавливаем высокий уровень на PA7 (светодиод включён).
         * Если на входе PA6 логический ноль,
         * сбрасываем PA7 (светодиод выключен).
         */
        if (READ_BIT(GPIOA->IDR, GPIO_IDR_IDR6) != 0U)
        {
            SET_BIT(GPIOA->BSRR, GPIO_BSRR_BS7);
        }
        else
        {
            SET_BIT(GPIOA->BSRR, GPIO_BSRR_BR7);
        }
    }
}
