# Supersonic 4-Pack — Expansion Documentation

**Version:** v2.1.0-SB-4P  
**Generated:** 2025-10-29

This index organizes the 4 modular expansion packs included in the Supersonic 4-Pack.

---

## 📦 Pack 1: Electrical Validation

**Location:** `docs/SonicBuilder_ElectricalValidation_v1/`

Power mapping, ground isolation, fuse sizing, validation tests, and measurement log sheets.

**Documentation:**
- Power-Map.md
- Grounding-Strategy.md
- Fuse-Sizing.md
- Validation-Tests.md
- Measurement-Logs.md

---

## 📦 Pack 2: Wiring Expansion

**Location:** `docs/SonicBuilder_WiringExpansion_v1/`

RR2 ↔ GM5 ↔ 44-pin diagrams, bench build guide, chime reroute, and continuity checklists.

**Documentation:**
- Wiring-Overview.md
- RR2-GM5-Integration.md
- Radio-44pin-Notes.md
- Chime-Reroute.md
- Continuity-Checklist.md

---

## 📦 Pack 3: CAN Bridge (Teensy)

**Location:** `docs/SonicBuilder_CANBridge_Teensy_v1/`

HS-CAN + SW-CAN dual-bus support, CANable option, Teensy 4.1 firmware starter, and capture logging.

**Documentation:**
- Bridge-Options.md
- CANable-Path.md
- Teensy41-DualBus.md
- Firmware-Starter.md
- Capture-Logging.md

---

## 📦 Pack 4: Tools & Docs

**Location:** `docs/SonicBuilder_ToolsAndDocs_v1/`

Bench setup, soldering lab, labeling, cable dressing, QR templates, and CI guide.

**Documentation:**
- Tools-Setup.md
- Soldering-Lab.md
- Labeling-CableDressing.md
- QR-Templates.md
- Docs-CI-Guide.md

---

## 🎯 Using the 4-Pack

Each pack's documentation is modular and self-contained. Reference them individually or integrate into your manual builds.

### Build with 4-Pack content

The `supersonic_build_all.py` script can incorporate content from these packs:

```bash
# Build manual with all pack content
python scripts/supersonic_build_all.py --version v2.1.0-SB-4P

# Output includes content from all 4 packs
```

---

**Installation performed by:** `SuperSonic_Installer.sh`  
**Pipeline integration:** DocsPipeline with full CI/CD support
