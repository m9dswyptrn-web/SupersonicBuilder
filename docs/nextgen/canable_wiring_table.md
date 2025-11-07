# CANable Pro Wiring Table

**Device:** CANable Pro (USB-to-CAN adapter)  
**Firmware:** candlelight / slcan compatible  
**Use Case:** Single-bus CAN monitoring, diagnostic logging

---

## Overview

The CANable Pro is a USB-to-CAN adapter ideal for monitoring and logging GMLAN traffic without a full bridge implementation. It supports standard Linux SocketCAN tools (candump, cansend, cangen).

---

## Wiring Table

### CANable Pro Pinout

| CANable Pin | Function      | GMLAN Connection   | Wire Color |
|-------------|---------------|--------------------|------------|
| CANH        | CAN High      | HS-GMLAN High      | White      |
| CANL        | CAN Low       | HS-GMLAN Low       | Green      |
| GND         | Ground        | Vehicle GND        | Black      |
| 5V          | Power Output  | (Optional use)     | Red        |

### 2014 Sonic GMLAN 11-Pin Connector

| Pin | Signal        | CANable Connection | Notes                    |
|-----|---------------|--------------------|--------------------------|
| 1   | HS-GMLAN (+)  | CANH              | High-speed CAN High      |
| 2   | HS-GMLAN (-)  | CANL              | High-speed CAN Low       |
| 3   | SW-GMLAN      | —                 | Single-wire (not used)   |
| 4   | Ground        | GND               | Chassis ground           |
| 5-11| N/C or power  | —                 | Not used for CAN bridge  |

---

## Connection Diagram

```
CANable Pro                2014 Sonic 11-Pin Connector
┌─────────────┐            ┌──────────────────┐
│ CANH (white)│───────────>│ Pin 1 (HS-CAN+) │
│ CANL (green)│───────────>│ Pin 2 (HS-CAN-) │
│ GND  (black)│───────────>│ Pin 4 (GND)     │
└─────────────┘            └──────────────────┘
      │
      └──USB──> Laptop/Android (via USB-OTG)
```

---

## Termination Requirements

### HS-GMLAN Termination
- **Required:** 120Ω resistor between CANH and CANL
- **Location:** Both ends of the CAN bus (vehicle + CANable)
- **Check:** Use multimeter to verify ~60Ω between CANH/CANL when vehicle off

### CANable Built-in Termination
- Most CANable Pro devices include an onboard 120Ω terminator
- Check product specs or measure with multimeter
- If missing, add external 120Ω resistor between CANH/CANL pins

---

## Software Setup

### Linux (Ubuntu/Debian)

```bash
# Install CAN utilities
sudo apt install can-utils

# Bring up CAN interface
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Monitor CAN traffic
candump can0

# Send CAN message
cansend can0 123#DEADBEEF
```

### Windows (using slcan)

```bash
# Install Python slcand
pip install python-can

# Connect CANable via serial
python -m can.viewer -i slcan -c COM3 -b 500000
```

### Android (via USB-OTG)

```bash
# Use apps like "Serial USB Terminal" or "CAN Logger"
# Connect CANable → USB-OTG adapter → Android head unit
# Configure: Baud = 500000, Protocol = slcan
```

---

## Firmware Flashing

### candlelight Firmware (Recommended)

```bash
# Download from: https://github.com/candle-usb/candleLight_fw
# Flash using DFU mode:
1. Hold BOOT button, plug in USB
2. Use dfu-util:
   dfu-util -d 0483:df11 -a 0 -s 0x08000000 -D canable_fw.bin
3. Unplug/replug USB
```

### Verify Firmware
```bash
# Check device enumeration
lsusb | grep CAN
# Should show: "OpenMoko, Inc. Geschwister Schneider CAN adapter"
```

---

## Use Cases

### 1. Diagnostic Logging
```bash
# Log all CAN traffic to file
candump -l can0
# Output: candump-2025-10-29_160000.log
```

### 2. Real-time Monitoring
```bash
# Watch specific CAN IDs
candump can0,100:7FF  # Only IDs 0x100-0x1FF
```

### 3. Message Injection
```bash
# Send custom messages for testing
cansend can0 241#0102030405060708
```

### 4. Reverse Engineering
```bash
# Capture baseline, trigger action, compare
candump can0 > baseline.log
# (trigger action in vehicle)
candump can0 > action.log
diff baseline.log action.log
```

---

## Comparison: CANable vs Teensy 4.1

| Feature                | CANable Pro      | Teensy 4.1       |
|------------------------|------------------|------------------|
| **CAN Buses**          | 1 (HS only)      | 2 (HS + SW)      |
| **Use Case**           | Monitoring       | Active bridging  |
| **Cost**               | ~$45 USD         | ~$27 USD         |
| **Setup Complexity**   | Low (USB plug)   | Medium (wiring)  |
| **Firmware**           | candlelight      | Custom Arduino   |
| **Linux Support**      | Excellent        | Good (Serial)    |
| **Android Support**    | USB-OTG          | USB-OTG          |

**Recommendation:**
- Use **CANable** for: Diagnostics, logging, reverse engineering
- Use **Teensy 4.1** for: Full HS↔SW bridge, production installs

---

## Safety Warnings

⚠️ **CRITICAL:**
- Never hot-plug CANable while vehicle ignition is ON
- Always verify ground connection before powering CAN bus
- Use proper USB-OTG cables rated for CAN adapters
- Keep termination resistor in circuit (120Ω)

---

## Troubleshooting

| Issue                  | Solution                                    |
|------------------------|---------------------------------------------|
| No CAN traffic         | Check termination (120Ω), verify baud rate |
| "Device not found"     | Re-flash firmware, check USB cable          |
| Intermittent messages  | Verify CANH/CANL not swapped                |
| Bus overload           | Reduce logging rate, filter specific IDs    |

---

**For firmware binary, see:** `firmware/canable_bridge_fw.hex`  
**For GMLAN pinouts, see:** `gmlan_pinout_reference.md`
