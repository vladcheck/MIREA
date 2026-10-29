#!/bin/bash
# Upload "binary4" firmware to STM32F4DISCOVERY
cd "$(dirname "$0")/.." && pio run -e binary4 -t upload
