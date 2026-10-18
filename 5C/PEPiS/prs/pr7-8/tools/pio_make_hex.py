# Дополнительный скрипт PlatformIO: сборка firmware.hex из firmware.elf.
#
# По умолчанию платформа ststm32 превращает .elf только в .bin, а Proteus
# принимает в поле Program File файл .elf (предпочтительно) либо .hex.
# Скрипт добавляет постдействие: после линковки .elf штатный objcopy
# ARM-тулчейна (arm-none-eabi-objcopy) собирает .hex в тот же каталог
# сборки, поэтому обычный `pio run` даёт оба формата.
#
# Подключается в platformio.ini строкой:
#   extra_scripts = post:tools/pio_make_hex.py

Import("env")

env.AddPostAction(
    "$BUILD_DIR/${PROGNAME}.elf",
    env.VerboseAction(
        "$OBJCOPY -O ihex -R .eeprom "
        "$BUILD_DIR/${PROGNAME}.elf $BUILD_DIR/${PROGNAME}.hex",
        "Building $BUILD_DIR/${PROGNAME}.hex",
    ),
)
