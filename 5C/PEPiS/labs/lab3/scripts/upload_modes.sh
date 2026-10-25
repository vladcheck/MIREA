#!/bin/bash
# Upload "modes" firmware to STM32F4DISCOVERY
cd "$(dirname "$0")/.." && pio run -e modes -t upload
