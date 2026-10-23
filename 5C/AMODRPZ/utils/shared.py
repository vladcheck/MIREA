"""Shared notebook cell-builder, same pattern as maths-for-programming-5c/scripts/shared.py.

One module-global list + two append helpers. Cell order in the .ipynb
== call order in the build script. Used by all tk* builders.
"""

import random

import nbformat as nbf

cells = []


def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))


def code(src):
    cells.append(nbf.v4.new_code_cell(src))


def definition(term, text):
    """Определение термина; форма подачи выбирается случайно через random.random().

    Возвращает либо «<термин> - это ...», либо «Термином «<термин>» называют
    то, что ...» (оборот «то, что» сохраняет именительный падеж определения).
    ``text`` подаётся без заключительной точки.
    """
    text = text.strip().rstrip(".")
    if random.random() < 0.5:
        body = f"{term} - это {text}"
    else:
        body = f"Термином «{term}» называют то, что {text}"
    return body + "."
