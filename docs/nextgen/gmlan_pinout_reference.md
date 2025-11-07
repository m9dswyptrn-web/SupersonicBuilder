# GMLAN Pinout Reference

**Vehicle:** 2014 Chevrolet Sonic LTZ  
**System:** GMLAN (General Motors Local Area Network)  
**Architecture:** Dual-bus (HS-CAN + SW-CAN)

---

## Overview

The 2014 Chevy Sonic uses GM's dual-bus GMLAN architecture:
- **HS-GMLAN (High-Speed):** 500 kbps, powertrain/chassis/body modules
- **SW-GMLAN (Single-Wire):** 33.333 kbps, infotainment/radio/HVAC

---

## Radio 11-Pin Connector Pinout

**Location:** Behind factory radio (dash disassembly required)

| Pin | Signal           | Wire Color | Voltage | Notes                          |
|-----|------------------|------------|---------|--------------------------------|
| 1   | HS-GMLAN High    | White      | 2.5V    | CAN High (500 kbps)            |
| 2   | HS-GMLAN Low     | Green      | 2.5V    | CAN Low (500 kbps)             |
| 3   | SW-GMLAN         | Yellow     | Var.    | Single-wire CAN (33.333 kbps)  |
| 4   | Ground           | Black      | 0V      | Chassis ground                 |
| 5   | +12V Accessory   | Red        | 12V     | Switched (ignition on)         |
| 6   | +12V Battery     | Orange     | 12V     | Always-on (memory power)       |
| 7   | Illumination     | Gray       | Var.    | Dash dimmer signal             |
| 8   | Reverse Signal   | Purple     | 12V     | Active when in reverse         |
| 9   | Parking Brake    | Brown      | 0V/12V  | Grounded when brake engaged    |
| 10  | Speed Signal     | Pink       | Pulse   | VSS (vehicle speed sensor)     |
| 11  | Antenna          | Blue       | Var.    | Power antenna control          |

---

## EOENKK Android Head Unit Wiring

**Harness:** 44-pin connector (aftermarket radio harness)  
**Adapter Required:** Maestro RR2 GM5 (retains steering wheel controls, chimes)

### Critical GMLAN Connections

| EOENKK Pin | Signal        | Sonic 11-Pin | RR2 GM5 Connection |
|------------|---------------|--------------|---------------------|
| CAN_H      | HS-GMLAN High | Pin 1        | RR2 CAN_H out       |
| CAN_L      | HS-GMLAN Low  | Pin 2        | RR2 CAN_L out       |
| SW_CAN     | SW-GMLAN      | Pin 3        | RR2 SW_CAN out      |
| GND        | Ground        | Pin 4        | Common ground       |

### Maestro RR2 GM5 Role
- **Purpose:** Translates steering wheel control (SWC) signals to EOENKK
- **Chime Reroute:** Routes factory chimes to head unit speakers
- **Retention:** Keeps OnStar, backup camera, factory amp signals

---

## OBD-II Port Pinout (For Reference)

**Location:** Driver's side lower dash panel

| Pin | Signal           | Use for GMLAN               |
|-----|------------------|-----------------------------|
| 1   | HS-GMLAN High    | Can tap for diagnostics     |
| 6   | HS-GMLAN Low     | Can tap for diagnostics     |
| 4   | Chassis Ground   | Common ground               |
| 16  | +12V Battery     | Power for CAN adapters      |

**Note:** OBD-II provides HS-GMLAN only (no SW-CAN access).

---

## CAN Bus Termination

### HS-GMLAN (Differential CAN)
- **Standard:** ISO 11898-2
- **Termination:** 120Ω resistor between CANH/CANL at **both ends** of bus
- **Verify:** Measure ~60Ω between pins 1 & 2 with vehicle off (parallel 120Ω resistors)

### SW-GMLAN (Single-Wire CAN)
- **Standard:** GM-specific (not ISO 11898)
- **Termination:** Non-standard impedance (consult GM service manual)
- **Voltage:** Varies 0-5V (not differential like HS-CAN)

---

## Voltage Levels

### HS-GMLAN (Idle State)
- **CANH:** ~2.5V (idle), 3.5V (dominant), 1.5V (recessive)
- **CANL:** ~2.5V (idle), 1.5V (dominant), 3.5V (recessive)
- **Differential:** 2V peak-to-peak

### SW-GMLAN (Idle State)
- **SW-CAN:** Variable 0-5V pulses
- **Protocol:** GM Class 2 / GMLAN Single-Wire
- **Monitoring:** Requires GM-specific transceiver (not standard MCP2551)

---

## Signal Integrity Checks

### Multimeter Tests (Vehicle Off)

| Test                     | Expected Value | Notes                        |
|--------------------------|----------------|------------------------------|
| CANH to GND              | Open circuit   | No continuity                |
| CANL to GND              | Open circuit   | No continuity                |
| CANH to CANL             | ~60Ω           | Parallel 120Ω terminators    |
| SW-CAN to GND            | High impedance | GM-specific termination      |
| +12V ACC to GND          | 0V (key off)   | 12V when ignition on         |

### Oscilloscope Tests (Vehicle On)

```
HS-GMLAN (500 kbps):
- Differential signal: 2V pp
- Bit time: 2 μs
- Frame rate: Variable (10-1000 msgs/sec)

SW-GMLAN (33.333 kbps):
- Single-ended signal: 0-5V
- Bit time: 30 μs
- Frame rate: Lower than HS (mostly infotainment)
```

---

## Common CAN IDs (2014 Sonic)

### HS-GMLAN IDs

| CAN ID (Hex) | Description                    | Rate (ms) |
|--------------|--------------------------------|-----------|
| 0x0C9        | Vehicle speed, engine RPM      | 10        |
| 0x1E9        | Steering angle                 | 20        |
| 0x3E9        | Gear position (PRNDL)          | 100       |
| 0x4E1        | Engine data (coolant, oil)     | 100       |

### SW-GMLAN IDs

| CAN ID (Hex) | Description                    | Rate (ms) |
|--------------|--------------------------------|-----------|
| 0x241        | Radio/HVAC controls            | 100       |
| 0x431        | Steering wheel button presses  | Event     |
| 0x501        | Chime requests                 | Event     |

**Note:** These are examples; full CAN database requires reverse engineering or GM service docs.

---

## Wiring Best Practices

### 1. Twisted Pair for HS-GMLAN
- Use twisted pair wire (22-24 AWG) for CANH/CANL
- Minimizes electromagnetic interference (EMI)

### 2. Shielded Cable for Long Runs
- If extending GMLAN beyond 1 meter, use shielded twisted pair
- Connect shield to chassis ground at ONE end only (avoid ground loops)

### 3. Proper Crimping
- Use weatherproof crimp connectors (Deutsch/AMP style)
- Heat-shrink all connections to prevent corrosion

### 4. Color Coding
- Follow GM wire colors (white = CANH, green = CANL, yellow = SW-CAN)
- Label all connections with wire tags

---

## Safety Warnings

⚠️ **CRITICAL:**
- **Never short CANH/CANL to 12V or GND** — will damage ECU modules
- **Never tap into airbag CAN bus** — separate system, safety-critical
- **Always disconnect battery** before splicing into factory harness
- **Use proper fuses** on all 12V power connections (5A recommended)

---

## Reverse Engineering Tools

### Capture CAN Traffic
```bash
# Use CANable or Teensy 4.1
candump can0 -l  # Log to file
```

### Decode CAN Messages
```bash
# Install Kayak or SavvyCAN for DBC editing
# Create custom DBC file for Sonic-specific IDs
```

### Identify Unknown IDs
```bash
# Trigger action in vehicle, compare logs
canbusload can0@500000 baseline.log test.log
```

---

## Resources

- **GM Service Manual:** 2014 Sonic Electrical Wiring Diagrams
- **GMLAN Protocol:** GM LAN Technical Specification (internal doc)
- **ISO Standards:** ISO 11898-2 (HS-CAN), SAE J2411 (SW-CAN single-wire)

---

**For Teensy 4.1 wiring, see:** `teensy41_firmware.md`  
**For CANable wiring, see:** `canable_wiring_table.md`
