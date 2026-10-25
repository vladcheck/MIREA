"""Shared notebook cell-builder, same pattern as maths-for-programming-5c/scripts/shared.py.

One module-global list + two append helpers. Cell order in the .ipynb
== call order in the build script. Used by all tk* builders.
"""

import nbformat as nbf

cells = []


def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))


def code(src):
    cells.append(nbf.v4.new_code_cell(src))
