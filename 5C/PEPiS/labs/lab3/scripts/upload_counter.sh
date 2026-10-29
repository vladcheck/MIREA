#!/bin/bash
# Upload "counter" firmware to STM32F4DISCOVERY
cd "$(dirname "$0")/.." && pio run -e counter -t upload
