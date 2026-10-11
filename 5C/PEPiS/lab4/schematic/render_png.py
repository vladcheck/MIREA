#!/usr/bin/env python3
"""Рендер SVG схемы в PNG через cairosvg (уважает textLength, как в lab3)."""

import cairosvg

cairosvg.svg2png(
    url="schematic/render/svg/lab4-atmega32.svg",
    write_to="schematic/render/schematic.png",
    output_width=2000,
)
print("render ok")
