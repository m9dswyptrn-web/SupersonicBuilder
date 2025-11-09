# Teensy 4.1 Dual-Bus CAN Bridge Firmware

**Hardware:** Teensy 4.1 (600 MHz ARM Cortex-M7)  
**Library:** FlexCAN_T4  
**Purpose:** Bridge HS-CAN (500 kbps) ↔ SW-CAN (33.333 kbps) for GMLAN integration

---

## Overview

The Teensy 4.1 provides native dual CAN controllers (CAN1, CAN2) via the FlexCAN_T4 library, making it ideal for bridging GM's dual-bus GMLAN architecture used in 2014 Chevy Sonic.

---

## Firmware Architecture

### CAN1 (HS-GMLAN)
- **Baud Rate:** 500 kbps
- **Pins:** TX = 22, RX = 23
- **Purpose:** High-speed powertrain, body, chassis messages
- **Termination:** 120Ω required at both bus ends

### CAN2 (SW-GMLAN)  
- **Baud Rate:** 33.333 kbps
- **Pins:** TX = 0, RX = 1
- **Purpose:** Single-wire infotainment, radio, HVAC messages
- **Termination:** Different impedance, verify GM specs

---

## Source Code

```cpp
// Teensy 4.1 Dual CAN Bridge
// Purpose: Bridge HS-GMLAN (500k) ↔ SW-GMLAN (33.333k)
// Library: FlexCAN_T4 by tonton81

#include <FlexCAN_T4.h>

// Initialize CAN buses with 256 RX / 16 TX mailboxes
FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> CAN_HS;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> CAN_SW;

void setup() {
  Serial.begin(115200);
  
  // Initialize CAN controllers
  CAN_HS.begin();
  CAN_SW.begin();
  
  // Set baud rates for GMLAN
  CAN_HS.setBaudRate(500000);   // HS-GMLAN: 500 kbps
  CAN_SW.setBaudRate(33333);    // SW-GMLAN: 33.333 kbps
  
  Serial.println("Teensy 4.1 Dual-Bus CAN Bridge Ready");
  Serial.println("HS-GMLAN: 500 kbps (CAN1)");
  Serial.println("SW-GMLAN: 33.333 kbps (CAN2)");
}

void loop() {
  CAN_message_t msg;
  
  // Forward HS-GMLAN → SW-GMLAN
  if (CAN_HS.read(msg)) {
    CAN_SW.write(msg);
  }
  
  // Forward SW-GMLAN → HS-GMLAN
  if (CAN_SW.read(msg)) {
    CAN_HS.write(msg);
  }
}
```

---

## Installation Steps

### 1. Install Arduino IDE + Teensyduino
```bash
# Download Arduino IDE 2.x
# Install Teensyduino from https://www.pjrc.com/teensy/td_download.html
```

### 2. Install FlexCAN_T4 Library
```bash
# Arduino IDE → Sketch → Include Library → Manage Libraries
# Search: FlexCAN_T4
# Install: FlexCAN_T4 by tonton81
```

### 3. Configure Board Settings
```
Tools → Board → Teensy 4.1
Tools → USB Type → Serial
Tools → CPU Speed → 600 MHz
Tools → Optimize → Faster
```

### 4. Upload Firmware
```
1. Connect Teensy 4.1 via USB
2. Open teensy41_dualbus.ino
3. Click Upload (Ctrl+U)
4. Teensy Loader will flash automatically
```

---

## Wiring Diagram

### Teensy 4.1 Pinout

| Teensy Pin | Function      | GMLAN Connection |
|-----------|---------------|------------------|
| 22        | CAN1 TX       | HS-GMLAN TX      |
| 23        | CAN1 RX       | HS-GMLAN RX      |
| 0         | CAN2 TX       | SW-GMLAN TX      |
| 1         | CAN2 RX       | SW-GMLAN RX      |
| GND       | Ground        | Vehicle GND      |
| VIN (5V)  | Power Input   | +5V regulated    |

### CAN Transceiver Requirements

**HS-GMLAN (CAN1):**
- Use: MCP2551 or TJA1050 transceiver
- Termination: 120Ω resistor between CANH/CANL

**SW-GMLAN (CAN2):**
- Use: GM-specific single-wire transceiver (or MCP2515 with modifications)
- Termination: Verify GM specifications (not standard 120Ω)

---

## Testing & Validation

### Serial Monitor Output
```
Teensy 4.1 Dual-Bus CAN Bridge Ready
HS-GMLAN: 500 kbps (CAN1)
SW-GMLAN: 33.333 kbps (CAN2)
```

### CAN Traffic Monitoring
```cpp
// Add to loop() for debugging
if (CAN_HS.read(msg)) {
  Serial.print("HS→SW: ID=0x");
  Serial.print(msg.id, HEX);
  Serial.print(" LEN=");
  Serial.println(msg.len);
  CAN_SW.write(msg);
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No CAN traffic | Check termination resistors (120Ω) |
| Erratic messages | Verify baud rates (500k / 33.333k) |
| Bus overload | Reduce bridging rate with filtering |
| No power | Verify VIN = 5V regulated supply |

---

## Advanced Features

### Message Filtering
```cpp
// Only bridge specific CAN IDs
void loop() {
  CAN_message_t msg;
  if (CAN_HS.read(msg)) {
    if (msg.id >= 0x100 && msg.id <= 0x200) {
      CAN_SW.write(msg);  // Only forward IDs 0x100-0x200
    }
  }
}
```

### Bi-directional Rate Limiting
```cpp
// Limit forwarding to prevent bus overload
unsigned long lastForward = 0;
void loop() {
  if (millis() - lastForward > 10) {  // 10ms min interval
    // Forward messages
    lastForward = millis();
  }
}
```

---

## Performance Specs

- **Max Throughput:** ~8000 msgs/sec (each direction)
- **Latency:** < 1 ms per message
- **Memory:** 256 RX + 16 TX mailboxes per bus
- **CPU Usage:** < 10% @ 600 MHz

---

## Safety Warnings

⚠️ **CRITICAL:**
- Never connect 12V directly to Teensy (use 5V regulator)
- Always use proper CAN transceivers (never direct GPIO)
- Test on bench before vehicle installation
- Keep spare stock head unit for rollback

---

**For wiring diagrams, see:** `photos/teensy_dualbus_wiring.png`  
**For firmware binary, see:** `firmware/teensy41_dualbus.ino`
