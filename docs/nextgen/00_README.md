# NextGen Engineering Appendix

**Version:** v2.2.0-SB-NEXTGEN  
**Purpose:** Advanced CAN bus integration for 2014 Chevy Sonic LTZ Android head unit

---

## Overview

This appendix provides advanced engineering documentation for implementing dual-bus CAN bridge solutions to enable full vehicle integration with the EOENKK Android head unit and Maestro RR2 GM5 interface.

## What's Inside

### 📄 Documentation
- **teensy41_firmware.md** — Teensy 4.1 dual-bus CAN bridge implementation
- **canable_wiring_table.md** — CANable Pro bridge wiring diagrams
- **gmlan_pinout_reference.md** — Complete GMLAN pinout reference
- **android_digital_audio_path.md** — Digital audio routing architecture

### 🖼️ Photos
- Head unit front/back reference photos
- Teensy 4.1 dual-bus wiring diagram
- Installation examples

### 💾 Firmware
- **teensy41_dualbus.ino** — Arduino sketch for Teensy 4.1 FlexCAN_T4
- **canable_bridge_fw.hex** — CANable Pro firmware binary

---

## Implementation Paths

### Option 1: Teensy 4.1 Dual-Bus Bridge (Recommended)
- **Advantages:** Native dual CAN controllers, 600 MHz ARM Cortex-M7, expandable I/O
- **Use Case:** Full HS-CAN (500 kbps) + SW-CAN (33.333 kbps) bridging
- **Cost:** ~$27 USD
- **Setup:** Flash .ino via Arduino IDE, wire to GMLAN HS/SW buses

### Option 2: CANable Pro Bridge
- **Advantages:** USB-to-CAN adapter, candlelight firmware, slcan compatible  
- **Use Case:** Single-bus monitoring, HS-CAN logging, diagnostic capture
- **Cost:** ~$45 USD
- **Setup:** Flash .hex firmware, configure via candump/cansend

---

## Quick Start

```bash
# Flash Teensy 4.1 firmware
1. Install Arduino IDE + Teensyduino
2. Install FlexCAN_T4 library
3. Open teensy41_dualbus.ino
4. Select Board: Teensy 4.1
5. Upload firmware

# Wire to GMLAN
HS-CAN: CAN1 (pins 22/23) → GMLAN HS (11-pin connector)
SW-CAN: CAN2 (pins 0/1)   → GMLAN SW (11-pin connector)
```

---

## Safety & Compatibility

⚠️ **WARNING:** Improper CAN bus connections can cause vehicle malfunction. Always:
- Use proper CAN termination (120Ω resistors)
- Verify pinouts before connecting
- Test on bench setup before vehicle installation
- Keep backup of stock head unit for rollback

---

## Support

For technical questions, refer to:
- Teensy 4.1 documentation: https://www.pjrc.com/store/teensy41.html
- FlexCAN_T4 library: https://github.com/tonton81/FlexCAN_T4
- GMLAN protocol specs: GM LAN Technical Specification

---

**This appendix is part of the SonicBuilder Professional Installation Manual series.**
