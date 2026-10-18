# pr56-pr78-worktrees plan

## Context
Complete and review `pr5-6/` (TIM2 intervals, variant 4: T1=80ms T2=40ms ARR+100) and `pr7-8/` (USART1 variant 4: 19200, BRR=417) in isolated git worktrees (main worktree untouched). pr5-6 is incomplete: schematic has components but zero wires, `.gost-report/` is empty, no docx exists. pr7-8 is essentially done (src/sim/out/kicad/docx-pdf fresh) and needs verification plus cosmetic cleanup. Schematic work MUST prefer kicad-mcp (`xd://mcp__kicad_*`); reports via gost-report. Talk to human in English; all professor artifacts in Russian.

## Approach
Order: create both worktrees first (independent), then complete pr5-6, then review/cleanup pr7-8, then verify both.

### Step 1. Create worktrees (independent, do first)
- From repo root `/Users/valdemar_check/github/vladcheck/MIREA`, run:
  `git worktree add -b agent/pr5-6-complete ../MIREA-pr56 HEAD`
  `git worktree add -b agent/pr7-8-review ../MIREA-pr78 HEAD`
- If a branch/worktree path already exists, reuse it (`git worktree list` to confirm) instead of failing; never touch main worktree files.
- All steps below run with cwd inside the respective worktree.

### Step 2. pr5-6 worktree: verify existing base (do before edits)
- Rerun: `clang -fsyntax-only -Wall -Wextra -Itools/include src/*.c` and `uv run --with matplotlib python3 sim/test_tim2.py`; expect exit 0 and `out/tim2_results.json` `all_pass=true`. Do not hand-edit sim outputs; they regenerate.

### Step 3. pr5-6 worktree: verify KiCad schematic with kicad-mcp (no rewiring)
Scout verified `kicad/pr5-6.kicad_sch` (75.5KB, 4468 lines) is DONE: U1 STM32F103C8 + R2 330 Ом + D1 LED + TP1 + R1/R3 10k + C1-C4 + 5x +3V3 + PWR_FLAGs + ~30 no_connects on unused MCU pins + 27 wire segments + junctions, title block (TIM2/PA1/Logic Analyzer, variant 4) and `img/scheme.png`/`.svg` renders exist. No `.kicad_pcb` (not required).
With kicad-mcp: `validate_schematic` + `run_erc` to confirm zero errors/warnings, `get_schematic_view` and Read the PNG to confirm the PA1-R2-D1-GND chain visually. Fix only what validation flags: normalize U1 lib-Tx vs instance-T6 naming if flagged, fill empty footprints only if ERC/BOM demands (U1 already has LQFP-48). Do not rewire or recreate the schematic; re-export `img/scheme.*` only if changed. Keep mm-only, 1.27mm grid.
### Step 4. pr5-6 worktree: build gost-report from scratch
- `.gost-report/` is empty. Model new `.gost-report/build.py` + `refs.json` on `pr7-8/.gost-report/build.py` structure (Report, toc_static, r.table/r.figure/r.listing/r.formula, bib via refs.json). Content: variant-4 timing table (250/ARR249; T1 80/79; T2 40/39; ARR+100 -> 140/139, PSC=7999, fCNT=1кГц), formula T=(PSC+1)(ARR+1)/fTIM, TIM2 register roles, both src listings with in-text citations, waveform figures from `img/waveform-*.png` + scheme figure, TZ section-7 coverage (13 пунктов) + 17 контрольных вопросов. No long/medium dashes in text; references via `r.ref.*`.
- Build with the skill entry (`python3 <skill>/gost-report/scripts/ensure_env.py .gost-report/build.py`, same as pr5-6 PLAN.md); output `ПР_5_6_Валекжанин_В_С.docx` at `pr5-6/` root. Never Read/parse the docx with Read tool; verify by rebuild exit 0 + file size.

### Step 5. pr7-8 worktree: verify + cosmetic cleanup (no remake)
- Known-good state: ERC 0E/0W, `out/usart_results.json` all_pass, docx/pdf fresh. Do NOT rebuild sim/schematic/report unless verification fails.
- Cleanup: rename `kicad/tmp/cupwarmer-*` to `pr78-*`, remove duplicate `pr7-8/tmp/` vs `kicad/tmp/` (keep one), delete `__pycache__/` and `kicad/.kicad-tool-cache/`, decide stray `Практическая работа 4_Proteus.docx` (delete if duplicate of docs source, else move into `docs/`). If reality differs (ERC dirty, JSON stale), fix minimally with kicad-mcp/sim rerun instead.
- Build firmware for Proteus: `pio run -e pr78_example -e pr78_variant4` (platformio.ini envs) so .elf/.hex exist; `.pdsprj` absence is normal, do not create one.

### Step 6. Both worktrees: re-validate schematics + review + commit
- Re-run `validate_schematic` + `run_erc` on both sch files; rerun both sim test suites; confirm docx files open (rebuild log clean).
- Run code-review skill on changed sources/build scripts; fix only flagged defects, no scope expansion.
- Commit per worktree with conventional prefixes (`feat(pr5-6):`, `docs(pr5-6):`, `fix(pr7-8):`, `chore(pr7-8):`). Do not merge to main, do not push.

## Critical files & anchors
- `pr5-6/PLAN.md` — task list + timing single-source-of-truth (T1=80/79, T2=40/39, diag 140/139).
- `pr7-8/.gost-report/build.py` — template for pr5-6 report builder (Report/toc/figure/table/listing pattern).
- `pr5-6/kicad/pr5-6.kicad_sch` — needs wires (zero `(wire` entries verified).
- `pr7-8/kicad/pr7-8.kicad_sch` + `kicad/tmp/cupwarmer-erc.rpt` — rename target, ERC baseline.
- `opencode.jsonc` — MCP routes: `kicad` = KiCAD-MCP-Server (preferred), `kicad-copilot` = fallback.

## Verification
- pr5-6: `clang -fsyntax-only ...` clean; `sim/test_tim2.py` exit 0; sch has `(wire` entries, `validate_schematic` + `run_erc` clean, rendered PNG visually shows PA1-R-D1-GND chain; docx exists and rebuilds deterministically.
- pr7-8: `sim/test_usart.py` exit 0; `pio run` produces firmware; ERC still 0/0; docx/pdf present and newer than inputs or byte-identical rebuild.
- `git worktree list` shows both worktrees; `git status --short` in each shows only intended files; main worktree untouched.

## Assumptions & contingencies
- gost-report skill path assumed from `opencode.jsonc` (`~/github/agentic/kicad-happy/skills`, currently absent on disk — unverified, confirm first); if missing, locate skill via `glob`/`find-skills` and use its `ensure_env.py`; if unfindable, hand-build docx with python-docx using pr7-8 docx as style reference.
- kicad-mcp assumed healthy (experimental on macOS); if schematic writes misbehave, close KiCad GUI / `close_project` first, then fall back to kicad-copilot (`extract_circuit`) or kicad-cli, re-validating after.
- Proteus cannot run on macOS: no real Proteus screenshots required; waveforms come from TIM2/USART models, stated as such in reports (existing JSON notes already do this).
