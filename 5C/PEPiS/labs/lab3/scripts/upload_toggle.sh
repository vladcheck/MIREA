#!/bin/bash
# Upload "toggle" firmware to STM32F4DISCOVERY
cd "$(dirname "$0")/.." && pio run -e toggle -t upload
