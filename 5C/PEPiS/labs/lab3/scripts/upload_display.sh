#!/bin/bash
# Upload "display" firmware to STM32F4DISCOVERY
cd "$(dirname "$0")/.." && pio run -e display -t upload
