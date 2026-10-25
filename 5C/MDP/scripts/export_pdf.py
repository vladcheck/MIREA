"""Экспорт выполненных ноутбуков в PDF: nbconvert -> HTML -> Chrome (Playwright).

GIF-анимации в PDF неподвижны, поэтому каждая заменяется диаграммой
из первых кадров (filmstrip), чтобы движение было видно на бумаге.
Используется установленный Google Chrome (channel='chrome'), Chromium
скачивать не нужно.
"""

import base64
import glob
import io
import os
import tempfile

import nbformat as nbf
from nbconvert import HTMLExporter
from PIL import Image
from playwright.sync_api import sync_playwright

OUT_DIR = "notebooks/pdf"
os.makedirs(OUT_DIR, exist_ok=True)

notebooks = sorted(glob.glob("notebooks/Листок-*.ipynb"))


def gif_to_filmstrip(gif_b64, max_frames=12, cols=4):
    img = Image.open(io.BytesIO(base64.b64decode(gif_b64)))
    frames = min(max_frames, getattr(img, "n_frames", 1))
    w, h = img.size
    rows = (frames + cols - 1) // cols
    film = Image.new("RGB", (w * cols, h * rows), "white")
    for i in range(frames):
        img.seek(i)
        film.paste(img.convert("RGB"), (w * (i % cols), h * (i // cols)))
    buf = io.BytesIO()
    film.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def replace_gifs(nb):
    # nbconvert не имеет блока output_gif и молча выбрасывает GIF-выводы,
    # поэтому заменяем их диаграммами кадров в формате PNG
    n = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        for out in cell.outputs:
            data = out.get("data", {})
            gif_b64 = data.pop("image/gif", None)
            if gif_b64:
                data["image/png"] = gif_to_filmstrip(gif_b64)
                n += 1
    print(f"  GIF заменено диаграммами кадров: {n}")
    return nb


with tempfile.TemporaryDirectory() as tmp:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        for nb_path in notebooks:
            name = os.path.splitext(os.path.basename(nb_path))[0]
            nb = nbf.read(nb_path, as_version=4)
            nb = replace_gifs(nb)
            exporter = HTMLExporter()
            html, _ = exporter.from_notebook_node(nb)
            # фикс текстового слоя PDF: без принудительного DejaVu Sans
            # Chrome подставляет в ToUnicode латинские гомоглифы (ĸ вместо
            # кириллической к), ломая поиск и копирование по русски.
            # Код использует Fira Code, формулы MathJax — собственный шрифт TeX.
            css = (
                "<style>"
                "@import url('https://fonts.googleapis.com/css2?family=Fira+Code&display=swap');"
                "body, p, li, h1, h2, h3, h4, .text_cell_render, .output_text pre "
                '{ font-family: "DejaVu Sans", sans-serif !important; }'
                ".input_area pre, .highlight pre, code, pre.code "
                '{ font-family: "Fira Code", "DejaVu Sans Mono", monospace !important; }'
                "</style>"
            )
            html = html.replace("</head>", css + "</head>")
            html_path = os.path.join(tmp, f"{name}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            page.goto(f"file://{os.path.abspath(html_path)}")
            page.wait_for_load_state("networkidle")
            # ждём, пока MathJax сверстает формулы
            page.wait_for_function(
                "() => !document.querySelector('span.math') || "
                "document.querySelector('mjx-container') !== null"
            )
            page.wait_for_timeout(2000)
            pdf = os.path.join(OUT_DIR, f"{name}.pdf")
            page.pdf(
                path=pdf,
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
            )
            print(f"PDF: {pdf} ({os.path.getsize(pdf)} байт)")
        browser.close()
