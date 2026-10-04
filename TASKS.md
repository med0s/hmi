# TASKS — prompts to give Claude Code, one phase at a time

Folder layout before starting:
```
hmi_rev_a/
  CLAUDE.md
  netlist_spec.md
  pinmap.csv
  TASKS.md
  docs/HMI_7inch_Hardware_Design_Guide_RevA.pdf
  datasheets/   (STM32H743 datasheet, DWIN LN80480T070IA9098 -TR/-TCF, TPS65150, TPS54360B,
                 TLV62569, TPS22918, TPS61165, LP2951, W9812G6KH, W25Q256JV, M24C64,
                 THVD1450, SP3232E, USBLC6-2SC6, TPD4E05U06, BAT54S, USB4105-GF-A, DM3AT)
```
Run `git init` in the folder first.

## Phase 1 — setup and audit
> Read CLAUDE.md, netlist_spec.md and pinmap.csv. Check the KiCad version. Create the KiCad project `hmi_rev_a` with the hierarchical sheets listed in netlist_spec.md (empty for now). Then produce `build/library_audit.md`: for every part in netlist_spec.md, the KiCad symbol and footprint you will use (verified to exist in the installed libraries) or "custom needed". Do not draw anything yet.

## Phase 2 — verification tooling
> Write `tools/check_nets.py` that parses a KiCad netlist export and checks it against pinmap.csv and the connection tables in netlist_spec.md, reporting missing nets, wrong pins and unexpected connections per sheet. Add a `--sheets` option so it only checks finished sheets. Test it on the empty project.

## Phase 3 — custom symbols and footprints
> Create the custom symbols and footprints listed as "custom needed" in the audit, from the datasheets in `datasheets/`. For each one, print a table of pin number → name from the datasheet next to the symbol's pins so I can review it. Stop after this phase.

## Phase 4 — schematic, one sheet at a time
Repeat for each sheet in order (01 → 13):
> Build sheet NN_<name> exactly per netlist_spec.md. Run the verification loop from CLAUDE.md (ERC, netlist export, check_nets.py for completed sheets) and commit. Show me the ERC summary and the check result.

Suggested order: 03_MCU_Core → 04_MCU_IO → 01_Power_Input → 02_Regulators → 05_SDRAM → 06_QSPI_EEPROM → 07_LCD_Connector → 08_LCD_Bias → 09_Backlight → 10_Touch → 11_RS485_TTL → 12_USB → 13_microSD_Misc.

## Phase 5 — schematic sign-off
> Run full ERC and check_nets.py on all sheets. Export a PDF of the schematic (`kicad-cli sch export pdf`) and a BOM CSV with value, footprint, DNP and TBD columns. List every TBD value with the datasheet equation needed.

Send the schematic PDF and BOM back to Claude chat for a review before starting the PCB.

## Phase 6 — PCB setup
> Set up the board: outline from the DWIN mechanical drawing (164.9 × 100.0 mm, confirm), M3 mounting holes, 4-layer stack-up, net classes and DRC rules from CLAUDE.md. I will run "Update PCB from Schematic" (F8) in the GUI; then place parts per the floorplan in section 17 of the design guide. Do not route. Run DRC and show unrouted counts.

## Phase 7 — routing
You route (or review) SDRAM, LTDC, QSPI and USB. Then:
> Route power pours, ground stitching and the remaining low-speed nets. Do not touch nets in the SDRAM, LCD, QSPI or USB net classes. Run DRC after every session and commit.

## Phase 8 — release
> Final DRC with zero errors, generate Gerbers, drill files, pick-and-place and BOM for JLCPCB/PCBWay (ask me which), and a fab notes file with the stack-up and impedance requirements.

## Phase 0 — datasheets (do this first)
> Run `python download_datasheets.py`. Then open `datasheets/MISSING.md` and get every missing file from the official vendor website only (TI, ST, Winbond, Littelfuse, Hirose, etc.), saving it under the file name in the manifest. For GT911 ask me for the copy from DWIN. For every PDF, confirm the part number on page 1 matches the manifest and report the datasheet revision. Do not use third-party mirrors.
