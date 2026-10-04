# 7" HMI Rev A — Netlist Specification

Source of truth for the schematic. MCU pin assignments are in `pinmap.csv` (validated against ST's STM32_open_pin_data for STM32H743IITx). Every connection below uses net names; build the schematic so that `kicad-cli sch export netlist` reproduces these nets exactly.

Conventions
- Power nets: `+VIN` (terminal), `VIN_PROT`, `+5V`, `+3V3`, `+3V3A`, `LCD_DVDD`, `LCD_BIAS_IN`, `VS_12V`, `AVDD`, `VGH`, `VGL`, `VCOM`, `VBAT`, `GND`.
- Series-terminated lines: MCU side net `<NAME>_MCU`, far side `<NAME>`; the resistor sits within 5 mm of the MCU pin.
- `DNP` = footprint placed, part not fitted (set the DNP attribute).
- `TBD` = value must be computed from the cited datasheet before release; place the part with a placeholder value and a `TBD` field.
- Pin names for non-MCU ICs are given by name; take pin numbers from the KiCad library symbol or the vendor datasheet. Where a number is given, it was checked against the datasheet.

Suggested hierarchical sheets: 01_Power_Input, 02_Regulators, 03_MCU_Core, 04_MCU_IO, 05_SDRAM, 06_QSPI_EEPROM, 07_LCD_Connector, 08_LCD_Bias, 09_Backlight, 10_Touch, 11_RS485_TTL, 12_USB, 13_microSD_Misc.

---

## 01 Power input and protection

| Ref | Part | Value | Pins → nets |
|---|---|---|---|
| J1 | Pluggable terminal block 4-pin 5.08 mm | — | 1 `+VIN`, 2 `GND`, 3 `RS485_A`, 4 `RS485_B` |
| F1 | SMD fuse, time-lag | 2 A, ≥63 V | `+VIN` → `VIN_F` |
| D1 | B360 Schottky (SMC) | 60 V 3 A | A `VIN_F`, K `VIN_PROT` |
| D2 | SMBJ36A TVS (unidirectional) | 36 V | K `VIN_PROT`, A `GND` |
| C1 | Aluminium electrolytic | 47 µF / 63 V | `VIN_PROT` – `GND` |
| C2, C3 | X7R 1210 | 2.2 µF / 100 V | `VIN_PROT` – `GND` |
| L1 | Inductor or 0 Ω (fit 0 Ω) | 4.7 µH option | `VIN_PROT` → `VIN_BUCK` |
| MH1–MH4 | M3 mounting holes (plated) | — | `CHASSIS` |
| R1 / C4 | 1 MΩ ∥ 4.7 nF / 2 kV | — | `CHASSIS` – `GND` |

## 02 Regulators

### U1 TPS54360B (HSOP-8 PowerPAD, DDA) — 5 V buck
| Pin name | Net / part |
|---|---|
| VIN | `VIN_BUCK`; C5, C6 2.2 µF / 100 V X7R at pin |
| EN | Divider `VIN_BUCK` –R2– EN –R3– `GND` (UVLO ≈ 8 V on). R2/R3 = TBD from TPS54360B datasheet EN equations |
| RT/CLK | R4 to `GND`, TBD for ≈500 kHz (datasheet RT equation) |
| BOOT | C7 100 nF to `SW_5V` |
| SW | `SW_5V` → L2 15 µH (Isat ≥ 3 A) → `+5V_REG`; D3 B360 cathode on `SW_5V`, anode `GND` (catch diode, REQUIRED) |
| FB | R5 52.3 kΩ (`+5V_REG`→FB), R6 10 kΩ (FB→`GND`) → 4.98 V |
| COMP | Type-II network to `GND`: R7/C8/C9 TBD (TI WEBENCH or datasheet procedure) |
| GND, PowerPAD | `GND`, thermal vias |
| Output | C10, C11 47 µF / 10 V X5R 1210 on `+5V_REG`; C12 100 µF polymer DNP; JP1 0 Ω `+5V_REG` → `+5V` (bring-up isolation) |

### U2 TLV62569 (SOT-23-5) — 3.3 V buck
| Pin name | Net / part |
|---|---|
| VIN | `+5V`; C13 10 µF |
| EN | R8 100 kΩ to `+5V` |
| SW | L3 2.2 µH (Isat ≥ 3 A) → `+3V3_REG` |
| FB | R9 453 kΩ (`+3V3_REG`→FB), R10 100 kΩ (FB→`GND`) → 3.32 V; C14 feed-forward DNP |
| GND | `GND` |
| Output | C15 22 µF + C16 10 µF on `+3V3_REG`; JP2 0 Ω `+3V3_REG` → `+3V3` |

### Analog rail
FB1 ferrite 600 Ω @100 MHz `+3V3` → `+3V3A`; C17 1 µF, C18 100 nF on `+3V3A`.

### U3, U4 TPS22918 (SOT-23-6) load switches
| Pin | U3 (DVDD) | U4 (BIAS_IN) |
|---|---|---|
| VIN | `+3V3` + C19 1 µF | `+5V` + C21 1 µF |
| VOUT | `LCD_DVDD` + C20 1 µF | `LCD_BIAS_IN` + C22 1 µF |
| ON | `LCD_DVDD_EN` + R11 100 kΩ to GND | `LCD_BIAS_EN` + R12 100 kΩ to GND |
| CT | C23 1 nF to GND | C24 1 nF to GND |
| QOD | tie to VOUT | tie to VOUT |
| GND | `GND` | `GND` |

## 03 MCU core — U5 STM32H743IIT6 (LQFP-176)

All pin numbers in `pinmap.csv`. Unlisted I/O pins: no-connect flags.
- VDD pins (15, 23, 36, 49, 62, 72, 82, 91, 103, 127, 136, 149, 159, 172): `+3V3`, one 100 nF 0402 per pin + C 4.7 µF + 10 µF bulk.
- VSS pins: `GND`. VSSA (37): `GND`.
- VCAP pins 81, 125: nets `VCAP1`, `VCAP2`, each 2.2 µF low-ESR to GND only (confirm in AN4938).
- VDDA (39), VREF+ (38): `+3V3A`, each 1 µF + 100 nF.
- VDD33_USB (114): `+3V3`, 1 µF + 100 nF.
- VBAT (6): `VBAT`, 100 nF. BT1 CR2032 holder: + `VBAT`, − `GND`.
- PDR_ON (171): `+3V3`.
- NRST (31): `NRST`, 100 nF to GND, SW1 tactile to GND, J6 pin 10.
- BOOT0 (166): `BOOT0`, R13 10 kΩ to GND, SW2 tactile to `+3V3` via R14 1 kΩ.
- HSE: Y1 25 MHz crystal between `HSE_IN` (PH0) and `HSE_OUT` (PH1); C25, C26 load caps = 2·(CL − 3 pF).
- LSE: Y2 32.768 kHz (CL 6–7 pF) between `LSE_IN` (PC14) and `LSE_OUT` (PC15); C27, C28 per AN2867.
- J6 Cortex Debug 2×5 1.27 mm: 1 `+3V3`, 2 `SWDIO`, 3 GND, 4 `SWCLK`, 5 GND, 6 `SWO`, 7 key (NC), 8 NC, 9 GND, 10 `NRST`.

## 04 MCU I/O helpers
- Series 33 Ω (4×0402 arrays OK) at the MCU on every LTDC net, `QSPI_CLK`, `SD_CK`, `FMC_SDCLK`.
- `LED_STATUS` → R15 1 kΩ → LED2 → GND. Power LED: `+3V3` → R16 1 kΩ → LED1 → GND.
- Buzzer: `BUZZER_PWM` → R17 100 Ω → Q1 2N7002 gate, R18 100 kΩ gate→GND; Q1 drain `BUZ_N`, source GND; BZ1 5 V magnetic 12 mm between `+5V` and `BUZ_N`; D4 1N4148W A `BUZ_N`, K `+5V`.
- Test header J7 1×6 2.54 mm: `TP1`, `TP2`, `TP3`, `TP4`, `+3V3`, `GND`.

## 05 SDRAM — U6 W9812G6KH-6 (TSOP-II-54, JEDEC x16)
| SDRAM pin | Net |
|---|---|
| 2,4,5,7,8,10,11,13 | `FMC_D0`…`FMC_D7` |
| 42,44,45,47,48,50,51,53 | `FMC_D8`…`FMC_D15` |
| 23,24,25,26,29,30,31,32,33,34 | `FMC_A0`…`FMC_A9` |
| 22 | `FMC_A10` |
| 35 | `FMC_A11` |
| 36 | `FMC_A12` (NC on 128 Mb; route anyway) |
| 20, 21 | `FMC_BA0`, `FMC_BA1` |
| 19 | `FMC_SDNE0` (CS#) |
| 18 / 17 / 16 | `FMC_SDNRAS` / `FMC_SDNCAS` / `FMC_SDNWE` |
| 15 / 39 | `FMC_NBL0` (LDQM) / `FMC_NBL1` (UDQM) |
| 38 | `FMC_SDCLK` (far side of 33 Ω) |
| 37 | `FMC_SDCKE0` |
| 1, 14, 27 / 3, 9, 43, 49 | `+3V3` (VDD / VDDQ), 100 nF each, + 10 µF bulk |
| 28, 41, 54 / 6, 12, 46, 52 | `GND` |
| 40 | NC |

## 06 QSPI flash and EEPROM
U7 W25Q256JVEIQ (WSON-8 8×6): 1 `QSPI_NCS` (+R19 10 kΩ to +3V3), 2 `QSPI_IO1`, 3 `QSPI_IO2`, 4 GND, 5 `QSPI_IO0`, 6 `QSPI_CLK`, 7 `QSPI_IO3`, 8 `+3V3` (100 nF + 1 µF), EP GND.
U8 M24C64-R (SO-8): 1,2,3 GND, 4 GND, 5 `I2C1_SDA`, 6 `I2C1_SCL`, 7 WC# R20 10 kΩ to GND, 8 `+3V3` (100 nF).
I2C pull-ups: R21, R22 4.7 kΩ to `+3V3` on `I2C1_SCL`, `I2C1_SDA`.

## 07 LCD connector — J3 50-pin 0.5 mm FPC (dual-contact), DWIN LN80480T070IA9098
| J3 pin | Net |
|---|---|
| 1, 2 | `LED_A` |
| 3, 4 | `LED_K` |
| 5, 36, 38, 48 | `GND` |
| 6, 46 | `VCOM` (C 1 µF / 25 V at connector) |
| 7 | `LCD_DVDD` (C 1 µF) |
| 8 | `LCD_MODE`: R23 10 kΩ to LCD_DVDD (fit), R24 10 kΩ to GND (DNP) |
| 9 / 10 / 11 | `LCD_DE` / `LCD_VSYNC` / `LCD_HSYNC` |
| 12–16 | `LCD_B7`…`LCD_B3` |
| 17–19 | `GND` via 0 Ω each (option to B7/B6/B5 DNP) |
| 20–25 | `LCD_G7`…`LCD_G2` |
| 26–27 | `GND` via 0 Ω (option to G7/G6 DNP) |
| 28–32 | `LCD_R7`…`LCD_R3` |
| 33–35 | `GND` via 0 Ω (option to R7/R6/R5 DNP) |
| 37 | `LCD_CLK` |
| 39 | `LCD_LR`: R25 10 kΩ to GND (fit), R26 10 kΩ to LCD_DVDD (DNP) |
| 40 | `LCD_UD`: R27 10 kΩ to GND (fit), R28 10 kΩ to LCD_DVDD (DNP) |
| 41 | `VGH` (C 1 µF / 50 V) |
| 42 | `VGL` (C 1 µF / 25 V) |
| 43 | `AVDD` (C 1 µF / 25 V) |
| 44 | `LCD_RESET` (R29 100 kΩ to GND) |
| 47 | `GND` (DITHB) |
| 45, 49, 50 | NC |

## 08 LCD bias — U9 TPS65150PWP (HTSSOP-24), pin numbers from datasheet SLVS576B
| Pin | Name | Net / part |
|---|---|---|
| 1 | FB | R30 681 kΩ (`VS_12V`→FB), R31 71.5 kΩ (FB→GND), C29 22 pF across R30 |
| 2 | DLY1 | C30 10 nF to GND |
| 3 | DLY2 | C31 10 nF to GND |
| 4 | VIN | `LCD_BIAS_IN`; C32 22 µF / 10 V, C33 100 nF |
| 5, 6 | SW | `SW_BIAS`: L4 4.7 µH (Isat ≥ 2 A) from `LCD_BIAS_IN`; D5 MBRS130L A `SW_BIAS`, K `VS_12V` |
| 7, 8 | PGND | GND |
| 9 | SUP | `VS_12V`; C34 1 µF / 25 V at pin; C35 22 µF / 25 V 1210 on `VS_12V` |
| 10 | VCOM | `VCOM`; C36 1 µF |
| 11 | IN | `VCOM_SET`; C37 1 nF to GND |
| 12 | FBP | R32 931 kΩ (`CPI`→FBP), R33 82.5 kΩ (FBP→GND) → 14.91 V |
| 13 | CTRL | `LCD_BIAS_IN` |
| 14 | ADJ | C38 22 pF to GND |
| 15 | VGH | `VGH`; R34 100 kΩ to GND |
| 16 | CPI | `CPI`; C39 1 µF / 50 V 0805 |
| 17 | DRVP | C40 330 nF / 25 V → `CP_P` |
| 18 | DRVN | C41 330 nF / 25 V → `CP_N` |
| 19 | GND | GND |
| 20 | REF | `VREF_BIAS`; C42 220 nF to GND |
| 21 | FBN | R35 649 kΩ (`VGL`→FBN), R36 78.7 kΩ (FBN→`VREF_BIAS`) → −10.00 V |
| 22 | COMP | C43 2.2 nF → R37 0 Ω → GND |
| 23 | GD | NC (test point) |
| 24 | FDLY | C44 100 nF to `LCD_BIAS_IN`; R38 0 Ω DNP to `LCD_BIAS_IN` |
| EP | PAD | GND |

D6 BAT54S (negative pump): pin 3 `CP_N`, pin 2 GND, pin 1 `VGL`. C45 1 µF / 25 V on `VGL`. R39 100 kΩ `VGL`→GND DNP.
D7 BAT54S (positive pump): pin 1 `VS_12V`, pin 3 `CP_P`, pin 2 `CPI`.
(BAT54S: pin 1 = anode D1, pin 2 = cathode D2, pin 3 = common. Confirm with chosen vendor.)

U10 LP2951 (SO-8, adjustable): INPUT `VS_12V` (C46 1 µF / 25 V); OUTPUT `AVDD` (C47 4.7 µF / 16 V); FEEDBACK `AVDD_FB` with R40 741 kΩ 0.1 % (`AVDD`→FB) and R41 100 kΩ 0.1 % (FB→GND) → 10.39 V; SHUTDOWN GND; GND; SENSE, VTAP, ERROR NC.

VCOM divider (prototype): R42 47 kΩ `AVDD`→`VCOM_HI`; RV1 20 kΩ trimmer ends `VCOM_HI`/`VCOM_LO`, wiper `VCOM_SET`; R43 36 kΩ `VCOM_LO`→GND.
VCOM DAC option (DNP): R44 100 kΩ `VCOM_TRIM` (PA4) → `VCOM_SET`.

## 09 Backlight — U11 TPS61165 (SOT-23-6)
VIN `+5V` (C48 4.7 µF); SW `SW_BL`: L5 10 µH (Isat ≥ 1 A) from `+5V`; D8 SS14 A `SW_BL`, K `LED_A`; C49 1 µF / 50 V on `LED_A`; FB `LED_K` with R45 1.1 Ω 1 % 0805 to GND (R46 parallel DNP); CTRL `BL_PWM` + R47 100 kΩ to GND; COMP C50 220 nF (TBD per datasheet); GND.

## 10 Touch
J4 (RTP, 4-pin 1.0 mm FPC): 1 `TOUCH_XM`, 2 `TOUCH_YM`, 3 `TOUCH_XP`, 4 `TOUCH_YP`. U12 TPD4E05U06 on all four at the connector. C51–C54 1 nF each to GND. MCU nets per pinmap.csv.
J9 (CTP GT911, 6-pin FPC, pitch per sample): 1 `CTP_SCL` (R48 33 Ω to `I2C1_SCL`), 2 `CTP_SDA` (R49 33 Ω to `I2C1_SDA`), 3 `CTP_INT` (R50 10 kΩ to +3V3 DNP), 4 GND, 5 `+3V3_CTP` (FB2 ferrite from +3V3, C55 10 µF + C56 100 nF), 6 `CTP_RST` (R51 10 kΩ to +3V3). D9 low-cap ESD array on pins 1–3.

## 11 RS485 and TTL/RS232
U13 THVD1450 (SOIC-8): 1 R `RS485_RX`, 2 /RE + 3 DE `RS485_DE` (R52 10 kΩ to GND), 4 D `RS485_TX`, 5 GND, 6 A `RS485_A`, 7 B `RS485_B`, 8 VCC `+3V3` (100 nF).
D10 SM712 (SOT-23): line pins `RS485_A`, `RS485_B`; GND pin GND.
SW3 3-pos DIP: pos1 R53 120 Ω between A and B; pos2 R54 680 Ω A→+3V3; pos3 R55 680 Ω B→GND.
J5 JST PH 4-pin: 1 `+3V3` via R56 0 Ω DNP, 2 `TTL_TXD_EXT`, 3 `TTL_RXD_EXT`, 4 GND.
TTL default: R57 0 Ω `TTL_TX`→`TTL_TXD_EXT`, R58 0 Ω `TTL_RXD_EXT`→`TTL_RX` (MCU side: R59/R60 100 Ω + D11 low-cap ESD).
RS232 option (DNP): U14 SP3232E: T1IN `TTL_TX`, T1OUT `TTL_TXD_EXT`, R1IN `TTL_RXD_EXT`, R1OUT `TTL_RX`, T2IN GND, R2IN NC, 5× 100 nF on C1±, C2±, V+, V−, VCC `+3V3`.

## 12 USB-C — J2 GCT USB4105-GF-A
A4/A9/B4/B9 `VBUS`; A5 `CC1` R61 5.1 kΩ to GND; B5 `CC2` R62 5.1 kΩ to GND; A6+B6 `USB_DP_C`; A7+B7 `USB_DM_C`; A8/B8 NC; A1/A12/B1/B12 GND; shell `USB_SHIELD` → R63 1 MΩ ∥ C57 4.7 nF to GND.
U15 USBLC6-2SC6: 1 `USB_DP_C`, 6 `USB_DP` (flow-through), 3 `USB_DM_C`, 4 `USB_DM`, 5 `VBUS`, 2 GND.
VBUS sense: R64 100 kΩ `VBUS`→`USB_VBUS`, R65 200 kΩ `USB_VBUS`→GND.
Bench power option (DNP): D12 Schottky + F2 PTC 500 mA `VBUS`→`+5V`.

## 13 microSD — J8 push-push (e.g. Hirose DM3AT-SF-PEJM5)
1 `SD_D2`, 2 `SD_D3`, 3 `SD_CMD`, 4 `+3V3` (C58 10 µF + C59 100 nF), 5 `SD_CK`, 6 GND, 7 `SD_D0`, 8 `SD_D1`; 47 kΩ pull-ups to +3V3 on D0–D3 and CMD; CD switch `SD_CD` with R66 10 kΩ to +3V3, other side GND.
