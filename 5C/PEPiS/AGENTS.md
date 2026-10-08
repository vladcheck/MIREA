# Practice works and labaratories on microcontrollers in university

Platform: KiCad
KiCad version: V10 (10.0.6)
Student: Валекжанин Владимир Сергеевич, group: ЭФБО-04-24
My individual variant: 4 (fourth)
Additional tools: pip3, python3.13, uv

## MCP servers

- `kicad` (via `opencode.jsonc`): KiCAD MCP Server v2.7.0 (clone at `~/KiCAD-MCP-Server`, built `dist/index.js`) for schematic/PCB automation. Uses KiCad 10's bundled Python (`KICAD_PYTHON` env var in config). ~230 tools in 16 categories. Note: opencode only discovers `opencode.json`/`opencode.jsonc` in the project root — `.opencode/` config files are NOT loaded as project config.
- `kicad-copilot` (via `opencode.jsonc`): `kicad-copilot-mcp@0.1.0` (biosshot), launched via `npx -y kicad-copilot-mcp` (Node ≥20; v26.3.0 installed). 22 tools. Fully headless, file-oriented S-expression editing of `.kicad_sch` — NO KiCad GUI/plugin needed, so no GUI-conflict risk. Explicitly supports KiCad 9/10. Key tools: `create_doc`, `extract_circuit` (apply component/net changes), `get_schematic`, `beautify_schematic`, `component_search`, `save_checkpoint`/`restore_checkpoint`, plus PCB tools. Use this as the ALTERNATIVE authoring path (A/B vs the `kicad` MCP) — prefer it when the `kicad` MCP misbehaves on macOS. Note: young project (v0.1.0).
- macOS support of the `kicad` server is marked **experimental** (Linux primary). If MCP schematic writes misbehave, fall back to kicad-cli / `kicad-copilot` / hand-editing S-expressions and verify with `validate_schematic`.

### Schematic authoring (CREATE) tools in the `kicad` MCP

The MCP is NOT read-only — it has ~46 schematic tools. Use them to author schematics instead of hand-writing S-expressions:

- `create_schematic`, `add_schematic_component` (place symbols from ~10,000 lib symbols), `batch_add_components`
- `add_schematic_wire`, `connect_to_net`, `batch_connect`, `add_schematic_net_label`, `add_no_connect`
- `edit_schematic_component`, `move/rotate_schematic_component`, `delete_schematic_*`, `annotate_schematic`
- `create_symbol` / `create_footprint` (new library parts with pins)
- **Always run `validate_schematic` after a write batch** (post-write integrity check).

### Schematic visualization (PICTURE) tools

Never guess what a schematic looks like — render it and Read the image:

1. MCP `get_schematic_view` (PNG preview, uses kicad-cli SVG + cairosvg) or `export_schematic_svg` / `export_schematic_pdf` — preferred.
2. Backup without MCP: `kicad-cli sch export svg -o <outdir> <file>.kicad_sch` — NOTE quirk: `-o` is treated as an **output directory**; the file lands at `<outdir>/<basename>.svg`. There is **no** `sch export png` in KiCad 10; rasterize the SVG with cairosvg from KiCad's bundled python (`/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 -m cairosvg in.svg -o out.png`).
- `kicad-cli` is on PATH at `/usr/local/bin/kicad-cli` (v10.0.6). Read-only exports work with the KiCad GUI open.

### GUI conflict warning

Schematic WRITES through the MCP while the project is open in the KiCad GUI risk stale-overwrite/lost edits (both directions). Before MCP write batches: close the project in the KiCad GUI (or MCP `close_project`), and let the GUI reload afterwards.

## AI skills (kicad-happy)

- `kicad-happy` skills are loaded project-wide via `opencode.jsonc` → `"skills": { "paths": ["~/github/agentic/kicad-happy/skills"] }` (clone lives OUTSIDE this repo at `~/github/agentic/kicad-happy`; upgrade with `git pull` there).
- 11 skills available: `kicad` (schematic/PCB analysis, design review), `spice` (simulation, needs ngspice/LTspice/Xyce), `emc` (EMC pre-compliance), `datasheets` (PDF spec extraction), `bom`, `digikey`, `mouser`, `lcsc`, `element14`, `jlcpcb`, `pcbway` (sourcing/fabrication).
- Analysis scripts are pure Python 3.10+ stdlib, run directly, e.g. `python3 ~/github/agentic/kicad-happy/skills/kicad/scripts/analyze_schematic.py <file>.kicad_sch`.
- **Important: kicad-happy skills are ANALYSIS-ONLY.** No script creates/wires components. The ONLY `.kicad_sch` writer in that family is `bom/scripts/edit_properties.py` (symbol property edits, use `--dry-run` first). For creating schematics use the MCP tools above.
- Other locally installed skill dirs: `~/.agents/skills` (41 software-process skills; `find-skills` can search the skills.sh registry via `npx skills find <query>`) and `~/.claude/skills` (includes `docx-mcp` — Word report generation; NOTE its MCP server is NOT registered in `opencode.jsonc`, so its tool workflows currently can't run).
- `kicad-harness` skill (at `~/github/zxkmm/kicad-harness`, AGPL-3.0, loaded via skills.paths): complements the MCP — GUI-free rendering/verification. Key command: `kh sview --sch <file.kicad_sch> --out <out.png>` (renders schematic sheets to PNG), plus `kh erc`, `kh view` (board), DRC, netlist/BOM, datasheet→footprint. IMPORTANT: (1) `kh` and its `rsvg-convert` shim (cairosvg-backed) live in `~/github/zxkmm/kicad-harness/.venv/bin` — that dir MUST be on PATH to invoke `kh`; (2) do NOT re-run its `setup.sh` on macOS (Linux-oriented, would rebuild the venv with system Python and break pcbnew); (3) NO schematic editing API — schematics are edited as text or via the MCP tools above.

## Recommended workflow for a practice work

1. Read the TZ (docx) by parsing with python (`docx` lib / pandoc) — NEVER via the Read tool.
2. Write the C sources (`src/*.c`) and check syntax (`clang -fsyntax-only -Wall -Wextra` with a CMSIS stub if needed).
3. Author the schematic in KiCad via MCP tools (components → wires → net labels → `validate_schematic`), then `get_schematic_view` and **Read the rendered image**; iterate until visually correct. Export SVG/PDF for the report.
4. Cross-check: run `analyze_schematic.py` + ERC; verify pin assignments match the C code (CRL/CRH, pins, RCC enable).
5. Render schematic images, insert into the report (python-docx / docx-mcp).
6. Screenshots of Proteus/CooCox runs must be real captures — never ship placeholder boxes (e.g. «ВСТАВИТЬ СЮДА СКРИНШОТ») in a final report.

## Caveats

- All units MUST be in mm (millimeters). Never use mil, inch, or any other unit in schematic/PCB files, coordinates, footprints, or design rules.
- NEVER read pdf or docx files using 'Read' tool - it immediately breaks opencode and makes me stuck. Always parse them using python, or use docx-mcp if available.
- Keep all schematic/PCB coordinates on the 1.27 mm grid.

## Requirements
- You talk to me in english, only. Never speak to me in russian;
- All source code, reports, and other media intended for my professor must be in russian.
- Always choose proteus over multisim. If proteus document is not available, tell the user and stop any work.

## Practice works

### Requirements

Every practice requires:
- write a docx report (отчет)
- implement an introductory example (учебный пример)
- implement a task by an individual variant (индивидуальный вариант)

# Labaratories
