#!/bin/bash
# Upload "led" firmware to STM32F4DISCOVERY
cd "$(dirname "$0")/.." && pio run -e led -t upload
