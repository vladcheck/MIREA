# Firmware ПР № 1 (стенд «Учтех-Профи», STM32F100C8Tx)

- `main.c` — bare-metal (без HAL): PA0–PA7 выходы (HL), PB8–PB15 выходы
  (сегменты HG1), PC13–PC15/PD0 входы floating (кнопки SB1–SB4), PB0 — вход АЦП
  (опрос — расширение работы). Базы GPIO — 0x4001xxxx по RM0008 Table 3
  (была опечатка 0x0801xxxx — исправлена).
- `startup.c` — таблица векторов + Reset_Handler (копия .data, обнуление .bss).
- `stm32f100.ld` — Flash 0x08000000 64K, RAM 0x20000000 8K. Без libc/newlib
  (типы заданы вручную) — собирается штатным `arm-none-eabi-gcc` из Homebrew.
- Сборка:
  `arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -nostdlib -nostartfiles -T stm32f100.ld -o pr1.elf startup.c main.c`
  `arm-none-eabi-objcopy -O ihex pr1.elf pr1.hex`
  (проверено: .text 716 байт, вектор SP=0x20002000, Reset на 0x08000000).
- Готовый файл: `firmware/pr1.hex` — указывать в Proteus в поле Program File
  модели микроконтроллера.
- Поведение: SB1 +1, SB2 −1, SB3 сброс, SB4 инверсия; HL1–8 — двоичный счётчик,
  HG1 — младшая десятичная цифра.
