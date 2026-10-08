# Lessons: KiCad schematic authoring with the kicad MCP tools

Date: 2026-09-25 · Project: lab1-gpio (STM32F407VGT6 → 4× LED chains)

## Why this exists
The first lab1-gpio schematic **looked correct in the rendered image but its netlist was an open circuit**. Never trust the picture — always verify the exported netlist.

## Failure modes we hit
- **Wire stubs stopping short of pins.** A pin has length; the wire must reach the pin TIP (endpoint), not the symbol body edge. Stubs ending 2.54 mm short look connected but netlist as open.
- **Reversed LEDs.** Anode was wired to GND. Caught only via netlist pin names (`D1/1` = cathode must be on GND, `D1/2` = anode on the resistor side).
- **Unconnected MCU GND.** A single missing power-pin wire → whole GND net floating.
- **"Power pin not driven" ERC errors.** Every power rail needs its power symbol AND a `PWR_FLAG` on the same net.

## Detection workflow (do this every time, in order)
1. `kicad_export_netlist` (KiCad XML) → assert programmatically: every chain net contains exactly the expected `ref/pin` pairs; no `unconnected-` nets on any R/C/D pin. This is the ground truth.
2. `kicad_run_erc` → aim for 0 errors, 0 warnings.
3. `kicad_get_schematic_view` / region renders → Read the image for orientation (LED triangle points anode→cathode bar toward GND) and label collisions.
4. `kicad_validate_schematic` after every write batch.

## MCP T-junction quirk (this MCP build)
- A pin endpoint sitting **mid-wire does NOT form a T-connection** — neither for the MCP connectivity check nor for kicad-cli netlist/ERC. The wire must *end or vertex* exactly on the pin endpoint.
- **Workaround for power rails:** draw the rail as a single polyline with an explicit waypoint (vertex) at *every* pin endpoint along the rail (`kicad_add_schematic_wire` with many waypoints, `snapToPins` on). Junction dots appear at each vertex.
- Verify rail membership with `kicad_get_wire_connections` at a rail point — it must list the power symbol pins.

## Fix patterns that worked
- **Pin-exact wiring:** always get endpoints first via `kicad_get_schematic_pin_locations`, then wire/label with `snapToPins` or `componentRef`+`pinNumber` snapping (labels land exactly on the pin tip).
- **Labels on both ends:** same-name local labels on the MCU pin and the far-end pin join nets without long wire runs — good when pin rows are too tight (2.54 mm) for readable wiring.
- **100-pin MCU symbols:** batch-add no-connect flags to all unused pins (`kicad_batch_add_no_connects`) or ERC floods with 100+ errors.
- **Moving parts:** `preserveWires` stretches wires but can leave diagonals and can **mis-associate vertical stubs with the wrong neighbor** (we got cathodes wired to the GND symbol above). After any group move, re-list wires (`kicad_list_schematic_wires`) and check for spurious segments.
- **Chain row spacing:** 5.08 mm between chains; stagger chain rows +1.27 mm off the MCU pin rows so label texts never share a row and overlap.
- **Cosmetics:** hide redundant power-symbol/PWR_FLAG reference texts; auto-placed U1 Reference/Value can land on power rails — reposition with `kicad_set_schematic_property_position`.
