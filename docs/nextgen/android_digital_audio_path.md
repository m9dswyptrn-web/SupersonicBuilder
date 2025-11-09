# Android Head Unit Digital Audio Path

**Head Unit:** EOENKK 10.1" Android 13 (2014 Sonic LTZ)  
**Purpose:** I²S/SPDIF digital audio routing for premium sound quality

---

## Overview

The EOENKK Android head unit supports multiple digital audio output paths for superior sound quality compared to analog RCA outputs. This document covers I²S and SPDIF routing options for aftermarket amplifiers and DSPs.

---

## Digital Audio Options

### 1. I²S (Inter-IC Sound)
- **Standard:** Philips I²S specification
- **Channels:** 2-8 channels (stereo to 7.1 surround)
- **Sample Rate:** 44.1 kHz / 48 kHz / 96 kHz
- **Bit Depth:** 16-bit / 24-bit
- **Use Case:** Direct connection to DSP or amplifier with I²S input

### 2. SPDIF (Sony/Philips Digital Interface)
- **Standard:** IEC 60958 / AES3
- **Channels:** 2 (stereo)
- **Sample Rate:** 44.1 kHz / 48 kHz
- **Connector:** Coaxial (RCA) or optical (TOSLINK)
- **Use Case:** Factory amp integration, external DAC

---

## EOENKK I²S Pinout

**Connector:** Internal 5-pin header (requires head unit disassembly)

| Pin | Signal    | Function                          | Voltage |
|-----|-----------|-----------------------------------|---------|
| 1   | BCK       | Bit Clock (BCLK)                  | 3.3V    |
| 2   | LRCK      | Left/Right Clock (WS/Frame Sync)  | 3.3V    |
| 3   | DATA      | Serial Data Output                | 3.3V    |
| 4   | MCLK      | Master Clock (optional)           | 3.3V    |
| 5   | GND       | Ground                            | 0V      |

### Timing Specifications
- **BCLK Frequency:** 64 × sample rate (e.g., 3.072 MHz @ 48 kHz)
- **LRCK Frequency:** Sample rate (e.g., 48 kHz)
- **Data Format:** I²S standard (MSB-first, 2's complement)

---

## SPDIF Output

### Coaxial SPDIF
**Connector:** RCA jack (orange/black on EOENKK rear panel)

| Connection | EOENKK Jack | DSP/Amp Input    |
|------------|-------------|------------------|
| Signal     | Orange RCA  | SPDIF In (coax)  |
| Ground     | Black RCA   | Ground           |

### Optical SPDIF (TOSLINK)
**Note:** EOENKK does not have optical output by default. Use coaxial-to-optical converter if needed.

---

## Wiring Diagram: EOENKK → DSP

### Example: Connecting to Helix DSP Pro

```
EOENKK Head Unit                Helix DSP Pro
┌─────────────────┐             ┌──────────────────┐
│ I²S Header      │             │ I²S Input        │
│  Pin 1 (BCK)    │────────────>│ BCK (Pin 3)      │
│  Pin 2 (LRCK)   │────────────>│ LRCK (Pin 4)     │
│  Pin 3 (DATA)   │────────────>│ DATA (Pin 5)     │
│  Pin 5 (GND)    │────────────>│ GND (Pin 1)      │
└─────────────────┘             └──────────────────┘
```

**Alternative: SPDIF Coaxial**
```
EOENKK SPDIF (Orange RCA) ──────> Helix SPDIF In (RCA)
EOENKK GND (Black RCA)    ──────> Helix GND
```

---

## Audio Configuration (Android Settings)

### Enable I²S Output
1. Go to **Settings → Sound → Advanced Settings**
2. Select **Audio Output Mode → I²S**
3. Set **Sample Rate → 48 kHz** (or 96 kHz if DSP supports)
4. Set **Bit Depth → 24-bit**
5. Disable **Internal Amplifier** if using external amp

### Enable SPDIF Output
1. Go to **Settings → Sound → Advanced Settings**
2. Select **Audio Output Mode → SPDIF (Coaxial)**
3. Set **Sample Rate → 48 kHz**
4. Enable **Passthrough Mode** for Dolby/DTS (if supported)

---

## Signal Integrity Tips

### 1. Cable Length
- **I²S:** Keep cables < 30 cm (1 foot) to avoid jitter
- **SPDIF Coaxial:** Can run up to 10 meters with 75Ω coax cable

### 2. Impedance Matching
- **I²S:** Use 3.3V logic-level wiring (no termination needed)
- **SPDIF Coaxial:** Use 75Ω coaxial cable (not regular RCA cable)

### 3. Grounding
- Connect GND pins between head unit and DSP/amp
- Avoid ground loops (use star grounding topology)

---

## DSP Compatibility

### Verified Compatible DSPs

| DSP Model           | I²S Support | SPDIF Support | Notes                    |
|---------------------|-------------|---------------|--------------------------|
| Helix DSP Pro       | Yes         | Yes           | Auto-detect input        |
| Audison Bit Ten D   | Yes         | Yes           | Requires firmware update |
| AudioControl DM-810 | No          | Yes           | SPDIF only               |
| miniDSP 2x4 HD      | Yes (USB)   | Yes (optical) | Requires USB connection  |

---

## Troubleshooting

| Issue                     | Solution                                      |
|---------------------------|-----------------------------------------------|
| No audio from I²S         | Verify BCK/LRCK/DATA pins, check sample rate |
| Crackling/popping         | Reduce I²S cable length (< 30 cm)            |
| SPDIF not detected        | Use 75Ω coax cable, verify SPDIF enabled     |
| Intermittent audio dropouts | Check GND connection, avoid USB interference |

---

## Advanced: Custom I²S Routing

### Accessing Internal I²S Header

⚠️ **WARNING:** Requires head unit disassembly, voids warranty.

1. Remove EOENKK head unit from dash
2. Unscrew rear panel (4x Phillips screws)
3. Locate 5-pin I²S header (near SoC chip)
4. Solder 22 AWG wires to pins (or use JST connector)
5. Route wires through head unit case grommet
6. Reassemble and test with multimeter (verify 3.3V logic)

---

## Benefits of Digital Audio Path

| Benefit                | Analog (RCA) | I²S        | SPDIF      |
|------------------------|--------------|------------|------------|
| **Noise Immunity**     | Low          | High       | Very High  |
| **Sample Rate**        | N/A          | Up to 96k  | Up to 48k  |
| **Bit Depth**          | N/A          | 24-bit     | 16-24 bit  |
| **Cable Length**       | < 1m         | < 0.3m     | < 10m      |
| **Signal Degradation** | Moderate     | Minimal    | Minimal    |

**Recommendation:** Use I²S for premium DSP setups, SPDIF for factory amp integration.

---

## Audio Pipeline Example

```
Android Audio Stack (48 kHz, 24-bit)
  ↓
EOENKK SoC (Rockchip RK3399 / similar)
  ↓
I²S Interface (BCK/LRCK/DATA @ 3.3V)
  ↓
Helix DSP Pro (8-channel processing)
  ↓
Amplifier (Class D, 4 × 100W RMS)
  ↓
Speakers (component front, coaxial rear)
```

---

## Resources

- **I²S Specification:** Philips I²S Bus Specification (Rev. 2.1)
- **SPDIF Specification:** IEC 60958 (Consumer Audio)
- **Android Audio HAL:** AOSP AudioFlinger documentation

---

**For head unit photos, see:** `photos/headunit_back.jpg`  
**For complete wiring, see:** `gmlan_pinout_reference.md`
