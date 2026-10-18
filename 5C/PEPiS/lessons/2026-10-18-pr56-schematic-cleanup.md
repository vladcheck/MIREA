# Lessons: pr5-6 schematic manual cleanup (canonical style)

Date: 2026-10-18 · Project: pr5-6 (TIM2 intervals, STM32F103C8, variant 4)

## Why this exists
The MCP-generated schematic was electrically correct (ERC 0/0, 28 wires, 36 no-connects)
but stylistically raw. A manual cleanup pass in KiCad re-saved the file; the diff is
large (every instance block re-emitted) while the semantic changes fit in one list.
This note records what is canonical so future cleanups converge instead of churning.

## What changed (HEAD vs working copy, `git diff`)
- Sheet title: `ПР №5-6. Изм...` became `ПР #5-6. Изм...` and shortened
  (dropped `(STM32F103C8, меандр на PA1)` detail to fit the title block).
- One floating text removed: `Logic Analyzer, канал A` (the PA1 net label already says this).
- Four note texts kept verbatim (C1 decoupling, U1 power, PA1 chain, TIM2 250 ms).
- Title-block comments 1-2, paper A4, net label `PA1`, all 24 annotated references
  (U1 R1-R3 C1-C4 D1 TP1 PWR/FLG/GND) unchanged in name, library, and value.
- Layout: whole sheet re-placed (U1 shifted +22.86 mm in X, all followers moved,
  28 wires became 25 with 8 junctions instead of 3). Same connectivity, new geometry.
- Test point: TP1 keeps `Reference TP1` visible, `Value TestPoint` set `(hide yes)`.
  The stray un-annotated `TP` reference from the generator is gone from instances
  (it survives only as the library default inside `lib_symbols`).
- File hygiene: `lib_symbols` now embeds all 8 used symbols (was effectively empty,
  resolved from libraries); `.kicad_pro` gained explicit board/erc defaults;
  `.kicad_prl` change in pr3-4 is only a window-position record, unrelated.
- Re-validated after cleanup: ERC 0 errors, 0 warnings.

## Canonical rules distilled
- `#` instead of `№` in sheet titles (ASCII, fits narrow title blocks, no font risk).
- `GND` in front of the arrow: write `VSS/VSSA → GND`, `D1 → GND`, never `→ общий провод`.
  Power direction reads left to right: source first, `GND` last.
- Test points: reference visible (`TP1`), value hidden. `Value TestPoint` is the
  library default and carries no information; hiding beats deleting (footprint
  filters and BOM still see the symbol type).
- Power symbols and flags: reference hidden (`PWR*`, `GND*`, `FLG*` are already
  self-describing); only real parts (R/C/D/U/TP) show references.
- One label per net tap: either a wire to the pin or a net label, not both plus
  a floating text saying the same thing (`Logic Analyzer, канал A` was the third).
- Values stay explicit on passives (`330 Ом`, `10 кОм`, `100 нФ` visible); they are
  the schematic, not decoration.
- Journals: record window/position-only diffs (`.kicad_prl`, `.kicad_pro` defaults)
  as noise, not as cleanup; never commit them as if they were design changes.
