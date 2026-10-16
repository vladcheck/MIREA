"""Экспорт ноутбуков в PDF: nbconvert -> HTML -> headless Chrome (Playwright).

Использование (из корня AMODRPZ):
    uv run python utils/export_pdf.py "tk7-8/*.ipynb" --out-dir tk7-8/pdf
    uv run python utils/export_pdf.py "tk5-6/*.ipynb" --out-dir tk5-6/pdf
    uv run python utils/export_pdf.py tk7-8/notebook.ipynb   # -> tk7-8/pdf/*.pdf

Без --out-dir PDF кладётся в подкаталог ``pdf/`` рядом с ноутбуком.
Тяжёлые ноутбуки НЕ исполняются: экспортируется текущее содержимое
ячеек (включая уже сохранённые outputs). Не запускать insclass/kNN
ноутбуки ради экспорта — только инфраструктурная проверка.

Требуется установленный Google Chrome (channel="chrome") и пакет
playwright (``uv add playwright``); скачивание Chromium через
``playwright install`` не нужно и не выполняется автоматически.
"""

import argparse
import base64
import glob
import io
import os
import sys
import tempfile

import nbformat as nbf
from nbconvert import HTMLExporter
from PIL import Image

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

DEJAVU_CSS = (
    "<style>body, div, span, p, li, h1, h2, h3, h4 "
    '{ font-family: "DejaVu Sans", sans-serif !important; }'
    "</style>"
)


def gif_to_filmstrip(gif_b64, max_frames=12, cols=4):
    """Собрать первые кадры GIF в одну PNG-диаграмму (filmstrip)."""
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


def replace_gifs(nb, max_frames=12, cols=4):
    # nbconvert не имеет блока output_gif и молча выбрасывает GIF-выводы,
    # поэтому заменяем их диаграммами кадров в формате PNG
    n = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            gif_b64 = data.pop("image/gif", None)
            if gif_b64:
                data["image/png"] = gif_to_filmstrip(
                    gif_b64, max_frames=max_frames, cols=cols
                )
                n += 1
    print(f"  GIF заменено диаграммами кадров: {n}")
    return nb


def notebook_to_html(nb_path, max_frames=12, cols=4):
    nb = nbf.read(nb_path, as_version=4)
    nb = replace_gifs(nb, max_frames=max_frames, cols=cols)
    exporter = HTMLExporter()
    html, _ = exporter.from_notebook_node(nb)
    # фикс текстового слоя PDF: без принудительного DejaVu Sans
    # Chrome подставляет в ToUnicode латинские гомоглифы (ĸ вместо
    # кириллической к), ломая поиск и копирование по-русски
    html = html.replace("</head>", DEJAVU_CSS + "</head>")
    return html


def export_notebooks(
    nb_paths,
    out_dir=None,
    channel="chrome",
    max_frames=12,
    cols=4,
    mathjax_timeout=30000,
):
    """Экспортировать ноутбуки в PDF. Возвращает список созданных PDF."""
    if sync_playwright is None:
        raise SystemExit(
            "ОШИБКА: пакет playwright не установлен. Выполните: uv add playwright"
        )
    pdfs = []
    with tempfile.TemporaryDirectory() as tmp:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel=channel, headless=True)
            except Exception as e:
                raise SystemExit(
                    f"ОШИБКА: не удалось запустить Chrome "
                    f"(channel={channel!r}): {e}\n"
                    "Установите Google Chrome или передайте "
                    "--channel chromium (потребуется "
                    "'playwright install chromium')."
                )
            page = browser.new_page()
            for nb_path in nb_paths:
                name = os.path.splitext(os.path.basename(nb_path))[0]
                target_dir = out_dir or os.path.join(
                    os.path.dirname(nb_path) or ".", "pdf"
                )
                os.makedirs(target_dir, exist_ok=True)
                html = notebook_to_html(nb_path, max_frames=max_frames, cols=cols)
                html_path = os.path.join(tmp, f"{name}.html")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html)
                page.goto(f"file://{os.path.abspath(html_path)}")
                page.wait_for_load_state("networkidle")
                # ждём, пока MathJax сверстает формулы; при отсутствии
                # сети (CDN недоступен) не висим, а предупреждаем
                try:
                    page.wait_for_function(
                        "() => !document.querySelector('span.math') || "
                        "document.querySelector('mjx-container') !== null",
                        timeout=mathjax_timeout,
                    )
                except Exception:
                    print(
                        "  ПРЕДУПРЕЖДЕНИЕ: MathJax не сверстал формулы "
                        f"за {mathjax_timeout} мс (возможно, нет сети "
                        "для CDN) — PDF всё равно будет создан."
                    )
                page.wait_for_timeout(2000)
                pdf = os.path.join(target_dir, f"{name}.pdf")
                page.pdf(
                    path=pdf,
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                )
                print(f"PDF: {pdf} ({os.path.getsize(pdf)} байт)")
                pdfs.append(pdf)
            browser.close()
    return pdfs


def resolve_inputs(patterns):
    nb_paths = []
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if not hits and os.path.isfile(pat):
            hits = [pat]
        nb_paths.extend(hits)
    # убрать дубли, сохранить порядок
    seen = set()
    unique = []
    for nb in nb_paths:
        if nb not in seen:
            seen.add(nb)
            unique.append(nb)
    return unique


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Экспорт Jupyter-ноутбуков в PDF через headless Chrome."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="пути к .ipynb и/или glob-шаблоны (напр. 'tk7-8/*.ipynb')",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="каталог для PDF; по умолчанию pdf/ рядом с каждым ноутбуком",
    )
    parser.add_argument(
        "--channel",
        default="chrome",
        help="канал браузера Playwright (по умолчанию 'chrome')",
    )
    parser.add_argument(
        "--max-frames", type=int, default=12, help="максимум кадров GIF в filmstrip"
    )
    parser.add_argument(
        "--cols", type=int, default=4, help="колонок в filmstrip-диаграмме"
    )
    parser.add_argument(
        "--mathjax-timeout",
        type=int,
        default=30000,
        help="ожидание вёрстки MathJax, мс",
    )
    args = parser.parse_args(argv)

    nb_paths = resolve_inputs(args.inputs)
    if not nb_paths:
        print(f"ОШИБКА: ничего не найдено: {args.inputs}", file=sys.stderr)
        return 1
    print(f"Ноутбуков к экспорту: {len(nb_paths)}")
    export_notebooks(
        nb_paths,
        out_dir=args.out_dir,
        channel=args.channel,
        max_frames=args.max_frames,
        cols=args.cols,
        mathjax_timeout=args.mathjax_timeout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
