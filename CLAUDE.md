# CLAUDE.md — 7" HMI Rev A (KiCad)

## What this project is
Custom 7" industrial HMI board: STM32H743IIT6 (LQFP-176), 16 MB SDRAM, 32 MB QSPI NOR, DWIN LN80480T070IA9098 800×480 RGB panel (resistive -TR or capacitive -TCF touch), RS485, TTL/RS232, USB-C, microSD, 9–36 V input. 4-layer, 1.6 mm board behind the panel (outline 164.9 × 100.0 mm, confirm against the DWIN drawing).

## Sources of truth (in this order)
1. `netlist_spec.md` — every part, value and net. If something here conflicts with your own reasoning, stop and ask; do not "fix" it silently.
2. `pinmap.csv` — every STM32 pin: LQFP-176 number, function, alternate function, net. Validated against ST's STM32_open_pin_data. Do not reassign MCU pins.
3. `datasheets/` — vendor PDFs. Pin numbers for non-MCU ICs come from these or from the KiCad library symbol, never from memory.
4. `docs/HMI_7inch_Hardware_Design_Guide_RevA.pdf` — rationale and layout rules (Arabic text, English tables).

## Environment
- Run `kicad-cli version` first and target that version's file format.
- Library paths: find the installed `symbols/` and `footprints/` directories (Windows: `C:\Program Files\KiCad\<ver>\share\kicad\`, Linux: `/usr/share/kicad/`). Search them before creating anything new.
- Project-local libraries: `lib/hmi.kicad_sym` and `lib/hmi.pretty/`, registered in the project's `sym-lib-table` and `fp-lib-table`.

## How to build the schematic
- Prefer a reproducible generator: a Python script in `tools/` (e.g. using the `kiutils` package) that writes the `.kicad_sch` sheets from `netlist_spec.md` and `pinmap.csv`. Re-run it instead of hand-patching large s-expression files.
- Style: hierarchical sheets as listed in `netlist_spec.md`; symbols on a grid; every IC pin gets a short wire stub and a net label (global/hierarchical label for inter-sheet nets, power symbols for rails). Readable beats clever.
- Reference designators, values, DNP flags and `TBD` fields exactly as in `netlist_spec.md`. Put a `TBD` field on any part whose value is marked TBD.
- Unused MCU I/O pins get no-connect flags.
- Assign a footprint to every symbol. If you choose a footprint name, confirm it exists in the installed library.

## Verification loop (mandatory after every sheet)
1. `kicad-cli sch erc --severity-all -o erc.rpt <project>.kicad_sch` — zero errors; explain every remaining warning.
2. `kicad-cli sch export netlist -o build/hmi.net <project>.kicad_sch`
3. `python tools/check_nets.py` — compares the exported netlist against `pinmap.csv` and the tables in `netlist_spec.md`; must report zero mismatches for completed sheets. Write this script before the first sheet.
4. Commit to git with a message naming the sheet.

## Rules
- Never invent a pin number, a footprint pad mapping or a component value. If a datasheet is missing, list what you need and stop.
- Never change a value marked in `netlist_spec.md` without asking. Computing a `TBD` value is allowed only from the cited datasheet equation; show the calculation in the commit message and in the symbol's `Calc` field.
- Custom symbols (expected: TPS65150PWP, TPS22918, TPS61165, THVD1450, LP2951 adjustable if missing, TPD4E05U06, DWIN J3 if a generic 50-pin connector is not used): build pins from the datasheet pin table, then cross-check pin count and names and report the check.
- Keep the user informed in short status updates; ask before deleting or regenerating sheets the user edited by hand.

## PCB stage (after schematic sign-off)
- Board setup: 4 layers L1 signal / L2 GND / L3 power / L4 signal, 1.6 mm, 1 oz outer. Net classes: Default 0.15 mm; `SDRAM` and `LCD` ~50 Ω single-ended (width from fab stack-up); `USB` 90 Ω differential; `PWR_5V`, `VS_12V`, `VIN` ≥ 0.6–1.0 mm; `LED_A/LED_K` ≥ 0.5 mm.
- DRC minimums: 0.127/0.127 mm track/space, via 0.3 mm drill / 0.6 mm pad.
- Placement follows the floorplan in the design guide (section 17): MCU centre with pin 1 top-left, SDRAM directly below, QSPI left, power input + RS485 at the J1 edge, LCD bias and backlight near J3, touch connectors in the quiet zone.
- 33 Ω series resistors within 5 mm of the MCU pins. LSB 0 Ω options and panel straps at J3.
- The user routes SDRAM, LTDC, QSPI and USB or reviews them before you commit. You may route power pours and low-speed nets. Run `kicad-cli pcb drc` after every routing session.
