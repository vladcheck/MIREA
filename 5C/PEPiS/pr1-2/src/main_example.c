/*
 * Практическая работа №1 — учебный пример (листинг 9.1 методички).
 * Передача состояния входа PA0 на выход PA1 для STM32F1.
 *
 * Схема в Proteus: ключ SW-SPDT на PA0 (подаёт лог. 1 или лог. 0),
 * светодиод через токоограничивающий резистор на PA1
 * (активный высокий уровень: 1 — светится, 0 — не светится).
 *
 * Сборка: CooCox CoIDE, компоненты CMSIS, CMSIS BOOT, RCC, GPIO.
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
     * Без тактирования порт не будет реагировать
     * на изменение регистров конфигурации.
     */
    SET_BIT(RCC->APB2ENR, RCC_APB2ENR_IOPAEN);

    /*
     * PA0 — входной вывод.
     * MODE0 = 00: режим входа.
     * CNF0  = 01: плавающий вход.
     *
     * В схеме Proteus вход PA0 подключается
     * к переключателю, который задаёт либо 1, либо 0.
     */
    MODIFY_REG(GPIOA->CRL,
            GPIO_CRL_MODE0 | GPIO_CRL_CNF0,
            GPIO_CRL_CNF0_0);

    /*
     * PA1 — выход push-pull со скоростью 2 МГц.
     * MODE1 = 10: выход 2 МГц.
     * CNF1  = 00: выход общего назначения push-pull.
     */
    MODIFY_REG(GPIOA->CRL,
            GPIO_CRL_MODE1 | GPIO_CRL_CNF1,
            GPIO_CRL_MODE1_1);

    while (1)
    {
        /*
         * Если на входе PA0 логическая единица,
         * устанавливаем высокий уровень на PA1.
         * Если на входе PA0 логический ноль,
         * сбрасываем PA1.
         */
        if (READ_BIT(GPIOA->IDR, GPIO_IDR_IDR0) != 0U)
        {
            SET_BIT(GPIOA->BSRR, GPIO_BSRR_BS1);
        }
        else
        {
            SET_BIT(GPIOA->BSRR, GPIO_BSRR_BR1);
        }
    }
}
