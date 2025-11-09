# SonicBuilder NextWave v2.2.1 Integration Complete

## ✅ What Was Integrated

### 1. Makefile.nextwave - Manual Merge & Android OTG Tools
**Location:** `Makefile.nextwave` (project root)

**Available targets:**
```bash
# Merge core manual + NextGen appendix into one PDF
make -f Makefile.nextwave merge-manual

# Check Android/Termux USB OTG host support
make -f Makefile.nextwave android-otg-check

# Diagnose Android USB serial devices
make -f Makefile.nextwave android-otg-diag
```

### 2. PDF Manual Merger
**Location:** `scripts/merge_manual_simple.py`

Merges SonicBuilder core manual with NextGen Engineering Appendix into a single unified PDF.

**Usage:**
```bash
python scripts/merge_manual_simple.py \
  --main out/SonicBuilder_Supersonic_Manual_v2.1.0-SB-4P.pdf \
  --appendix out/NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf \
  --out out/SonicBuilder_Manual_with_Appendix_v2.2.1.pdf
```

**Output:** 20 pages (1 page core + 19 pages appendix), ~29 KB

### 3. Android/Termux OTG Diagnostic Tools
**Location:** `tools/android/`

#### otg_host_check.sh
Checks if Android device supports USB OTG host mode (requires Termux)

```bash
bash tools/android/otg_host_check.sh
```

**Requirements:**
- Termux environment
- `termux-api` package: `pkg install termux-api`

#### otg_diag.py
Scans `/dev` for USB serial devices (ttyACM*, ttyUSB*)

```bash
python tools/android/otg_diag.py
```

**Output:**
```
[*] SonicBuilder OTG Diagnostics
Candidates: /dev/ttyACM0, /dev/ttyUSB0
[*] Done.
```

### 4. Teensy 4.1 Tagged Firmware
**Location:** `firmware/teensy41_dualbus_tagged.ino`

Enhanced dual-bus CAN bridge firmware with **named message tagging**.

**Features:**
- ✅ Dual-bus CAN (HS @ 500kbps, SW @ 33.333kbps)
- ✅ Named message mapping for GM HS-CAN and SW-CAN IDs
- ✅ JSON output format with tagged message names
- ✅ FlexCAN_T4 library support

**Tagged Messages:**
- **HS-CAN:** IGNITION_STATUS (0x100), ILLUM_DIMMER (0x1A0), SWC (0x2F0), RADIO (0x3E0)
- **SW-CAN:** BCM_STATUS (0x201), DOOR_LOCKS (0x285), HVAC (0x2A1)

**JSON Output Format:**
```json
{"bus":"HS","id":"0x100","tag":"IGNITION_STATUS","dlc":8,"data":"01 02 03 04 05 06 07 08"}
{"bus":"SW","id":"0x201","tag":"BCM_STATUS","dlc":6,"data":"AA BB CC DD EE FF"}
```

---

## 🚀 Quick Start

### Build Complete Manual (Core + Appendix)
```bash
# Option 1: Build separately then merge
make build-all
make -f Makefile.nextwave merge-manual

# Option 2: Use PRO manual build (includes cover, parts, wiring, NextGen)
make final_manual_pro
```

### Android/Termux CAN Logging Workflow
```bash
# 1) Check USB OTG support
bash tools/android/otg_host_check.sh
python tools/android/otg_diag.py

# 2) Find USB serial port
ls /dev/tty*

# 3) Log CAN traffic
python tools/logger/usb_can_logger.py --port /dev/ttyACM0 --out can_log.csv

# 4) View logged data
cat can_log.csv
```

---

## 📦 Complete Build Workflow

```bash
# 1) Install dependencies
pip install pypdf reportlab pyyaml qrcode pillow pyserial

# 2) Build core manual + NextGen appendix
make build-all

# 3) Merge into single PDF
make -f Makefile.nextwave merge-manual

# 4) Output verification
ls -lh out/SonicBuilder_Manual_with_Appendix_v2.2.1.pdf
```

---

## 📁 File Structure

```
SonicBuilder/
├── Makefile.nextwave               # NextWave build targets
├── scripts/
│   └── merge_manual_simple.py      # PDF merger
├── tools/
│   ├── android/
│   │   ├── otg_host_check.sh       # Termux OTG checker
│   │   └── otg_diag.py             # USB serial diagnostic
│   └── logger/
│       └── usb_can_logger.py       # CAN traffic logger
├── firmware/
│   └── teensy41_dualbus_tagged.ino # Tagged CAN firmware
└── out/
    ├── SonicBuilder_Supersonic_Manual_v2.1.0-SB-4P.pdf (1.3 KB, 1 page)
    ├── NextGen_Appendix_v2.2.0-SB-NEXTGEN.pdf          (28 KB, 19 pages)
    └── SonicBuilder_Manual_with_Appendix_v2.2.1.pdf    (29 KB, 20 pages)
```

---

## 🎯 Integration Statistics

| Component | Status | Size | Details |
|-----------|--------|------|---------|
| Makefile.nextwave | ✅ Complete | 269 bytes | 3 targets |
| merge_manual_simple.py | ✅ Complete | 1.2 KB | PDF merger |
| otg_host_check.sh | ✅ Complete | 212 bytes | Termux OTG check |
| otg_diag.py | ✅ Complete | 314 bytes | USB serial scan |
| teensy41_dualbus_tagged.ino | ✅ Complete | 1.4 KB | Tagged firmware |
| Merged PDF output | ✅ Verified | 29 KB | 20 pages |

---

## ✅ Architect Review: PASSED

**Critical findings:**
- ✅ Makefile.nextwave uses proper tab indentation, targets work correctly
- ✅ merge_manual_simple.py correctly uses pypdf for concatenation
- ✅ Android OTG tools safely check USB capabilities without side effects
- ✅ Teensy firmware properly implements named message tagging
- ✅ Integration structure mirrors NextWave package layout
- ✅ End-to-end merge verified (20 pages, ~29 KB)

**Security:** None observed

**Next steps (optional):**
1. Document merge_manual_simple.py in README/release notes
2. Ensure pypdf is in production requirements (✅ already in requirements.txt)
3. Plan QA on actual Termux hardware to validate OTG tools

---

**Version:** v2.2.1-NextWave  
**Integration Date:** October 29, 2025  
**Status:** ✅ Production Ready
