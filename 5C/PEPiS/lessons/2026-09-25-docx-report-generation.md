# Lessons: generating a Russian university lab-report .docx programmatically

Date: 2026-09-26 · Output: `lab1-gpio/ЛР_1_Валекжанин_В_С.docx` via `lab1-gpio/generate_report.py` (python-docx), modeled on `pr1-2/ПР_1_Валекжанин_В_С.docx`.

## Reading source material (never Read-tool binaries on this host)

- NEVER use the Read tool on PDF/docx — it breaks the host. Extract with:
  - `uv run --with pypdf python -c "..."` for PDFs (pypdf is not installed globally).
  - `uv run --with python-docx python -c "..."` for docx.
- Mining a previous student report for conventions: print `sections[0]` margins/size, then for each paragraph dump `(style.name, alignment, line_spacing, run font name/size/bold)`. This reveals the whole GOST recipe in one pass, including title-page wording, heading casing (ALL CAPS, centered), listing font, and caption format ("Рисунок 1 — ..."). Check `zipfile` for footer parts and a `PAGE` field inside `word/footer1.xml`.
- `pr1-2` conventions discovered: footer has a `PAGE` field centered; professor name was blank ("Проверил: ____"), so reuse a blank line.

## Formatting recipe that worked (matches pr1-2)

- A4, margins L=3.0 R=1.5 T=2.0 B=2.0 cm; Normal style = Times New Roman 14 pt, 1.5 spacing, justified.
- Headings: Heading 1 style overridden to TNR 14 bold black, centered (recipe style: "1. ЦЕЛЬ РАБОТЫ" in caps).
- Code listings: Consolas 10 pt, left-aligned, single spacing, one paragraph per line (no native code-block support — just loop).
- Images: `paragraph.add_run().add_picture(..., width=Cm(15.5))` inside a centered paragraph; numbered caption centered below.
- Title page: small centered header block, blank spacer paragraphs, RIGHT-aligned "Выполнил/Принял" block, "Москва 2026" centered; then `add_page_break()`.

## Footer page number (python-docx has no native API)

- Build the PAGE field by appending raw XML runs to a footer paragraph run:
  `OxmlElement('w:fldChar' begin) → 'w:instrText' with text ' PAGE ' → 'w:fldChar' end`; set `footer.paragraphs[0].alignment = CENTER`.

## Verification (python-docx has no validator; lessons from 2026-09-25 say only Word is authoritative)

- Re-open the output and check: `zipfile.testzip()`, `word/media/` parts exist (embedded image present), footer part exists and contains `PAGE`, headings list, 5 listing captions, code-line count, and spot-check key code strings + Russian text (Cyrillic round-trips fine — no special handling needed, just write UTF-8 source).
- Keep a rerunnable `generate_report.py` next to the output: content edits become one-line changes and a re-run, no manual docx surgery.

## Integrity rule (from AGENTS.md — non-negotiable)

- Bench-run screenshots/photos DO NOT exist yet → insert a bold red marker paragraph («ВСТАВИТЬ РЕАЛЬНОЕ ФОТО...») as an explicit to-do. Never fabricate or generate fake "evidence" images in a report submitted to a professor.

## Pitfalls hit this session

- `pio` was not on PATH (exit 127) — the real binary is `~/.platformio/penv/bin/pio`; the SUCCESS table it prints is a good build-log excerpt for the results section.
- KiCad schematic render: `kicad-cli sch export svg` puts the file at `<outdir>/<basename>.svg`; crop by rewriting the SVG `viewBox` and rasterizing with `uv run --with cairosvg` — iterate the viewBox 2–3 times and Read the PNG until nothing important is cut.
