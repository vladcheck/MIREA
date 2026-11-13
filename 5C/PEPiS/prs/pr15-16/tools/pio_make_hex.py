# Дополнительный скрипт PlatformIO: сборка firmware.hex из firmware.ihx.
#
# Платформа intel_mcs51 (SDCC) по умолчанию оставляет результат в формате
# .ihx (Intel HEX от SDCC), а поле Program File среды моделирования
# принимает классический .hex. Скрипт добавляет постдействие: после
# сборки пакетный objcopy платформы превращает .ihx в .hex в тот же
# каталог сборки, поэтому обычный `pio run` даёт оба формата.
#
# Подключается в platformio.ini строкой:
#   extra_scripts = post:tools/pio_make_hex.py

Import("env")

env.AddPostAction(
    "$BUILD_DIR/${PROGNAME}.ihx",
    env.VerboseAction(
        "$OBJCOPY -I ihex -O ihex "
        "$BUILD_DIR/${PROGNAME}.ihx $BUILD_DIR/${PROGNAME}.hex",
        "Building $BUILD_DIR/${PROGNAME}.hex",
    ),
)
