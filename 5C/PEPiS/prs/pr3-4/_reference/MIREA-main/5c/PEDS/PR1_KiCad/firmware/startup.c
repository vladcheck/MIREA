/* Minimal Cortex-M3 startup for STM32F100C8 (no HAL, no CMSIS).
 * Copies .data to RAM, zeroes .bss, then calls main().
 * Vector table: initial SP + 15 core exceptions, IRQs default to
 * Default_Handler (infinite loop). BOOT0=0 -> boots from Flash 0x08000000,
 * so the table below must sit at the start of Flash (see stm32f100.ld).
 * No libc: integer types defined manually (ARM EABI: char=8 bit, int=32 bit).
 */
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;

extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss;
extern int main(void);

void Reset_Handler(void) {
    uint32_t *src = &_sidata, *dst;
    for (dst = &_sdata; dst < &_edata;) *dst++ = *src++;
    for (dst = &_sbss; dst < &_ebss;) *dst++ = 0;
    main();
    for (;;) { /* main must not return; loop if it does */ }
}

void Default_Handler(void) {
    for (;;) { /* hang on unexpected interrupt */ }
}

void NMI_Handler(void) __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void) __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void) __attribute__((weak, alias("Default_Handler")));
void DebugMon_Handler(void) __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void) __attribute__((weak, alias("Default_Handler")));

extern uint32_t _estack;

__attribute__((section(".isr_vector"), used)) void (* const g_vector_table[])(void) = {
    (void (*)(void)) &_estack,
    Reset_Handler,
    NMI_Handler,
    HardFault_Handler,
    MemManage_Handler,
    BusFault_Handler,
    UsageFault_Handler,
    0, 0, 0, 0,
    SVC_Handler,
    DebugMon_Handler,
    0,
    PendSV_Handler,
    SysTick_Handler,
};
