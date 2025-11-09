# 🧾 SonicBuilder Certificate of Authenticity Generator

## 📦 Complete CoA System

**Generate numbered certificates for SonicBuilder build kits**

```
CoA_Generator/
├── generate_coa.py          - Certificate generator script
├── README_CoA.txt           - Complete documentation
├── EXAMPLES.md              - Usage examples
├── .gitignore               - Ignore generated PDFs
└── output/                  - Generated CoAs
    ├── SonicBuilder_CoA_#0002.pdf
    ├── SonicBuilder_CoA_#0005.pdf
    └── ...
```

---

## 🚀 Quick Start

### Basic Usage
```bash
cd CoA_Generator
python generate_coa.py --serial 0002
```

### With QR Code
```bash
python generate_coa.py --serial 0003 --qr "https://sonicbuilder.io/manuals/0003"
```

---

## 🎨 Certificate Format

```
═══════════════════════════════════════════════════════

          SONICBUILDER PLATFORM
       CERTIFICATE OF AUTHENTICITY

          Serial Number: SB-0002

──────────────────────────────────────────────────────

       This document certifies that

        SONICBUILDER BUILD KIT #0002

         was produced and verified by

   Christopher Elgin — SonicBuilder Founder

      as an official SonicBuilder project.

──────────────────────────────────────────────────────

Platform: EOENKK Android 15 + Maestro RR2 GM5
Version: [auto from VERSION.txt]
Build Date: [auto-generated]
Serial Number: SB-0002

           [QR Code - if URL provided]
        Scan for build documentation

──────────────────────────────────────────────────────

        Christopher Elgin
     SonicBuilder Founder
        [Build Date]

═══════════════════════════════════════════════════════
```

---

## 🔢 Serial Number System

| Range | Purpose |
|-------|---------|
| #0001 | **Reserved** - Founder Certificate |
| #0002-0099 | Prototypes and initial builds |
| #0100-0999 | Production builds |
| #1000+ | Large-scale production |

**Format:** SB-XXXX (e.g., SB-0002, SB-0100)

---

## 🎯 Features

✅ **Numbered Serial System** - SB-XXXX format  
✅ **Auto-Version** - Reads from VERSION.txt  
✅ **Auto-Date** - Current build date  
✅ **QR Code Integration** - Optional URL linking  
✅ **Seal Watermark** - 6% opacity background  
✅ **Badge Integration** - Top-right corner  
✅ **Christopher Elgin Certification** - Official founder signature

---

## 🔗 QR Code Integration

Add QR codes for easy access to documentation:

```bash
# Link to build manual
python generate_coa.py --serial 0002 \
    --qr "https://sonicbuilder.io/manuals/0002"

# Link to GitHub
python generate_coa.py --serial 0003 \
    --qr "https://github.com/user/sonicbuilder-build-003"

# Link to custom docs
python generate_coa.py --serial 0004 \
    --qr "https://docs.example.com/builds/0004"
```

---

## 📦 Batch Generation

### Generate Multiple CoAs
```bash
#!/bin/bash
for i in {2..10}; do
    serial=$(printf "%04d" $i)
    python generate_coa.py --serial $serial \
        --qr "https://sonicbuilder.io/manuals/$serial"
done
```

**Output:** 9 CoAs (#0002 through #0010)

---

## 🎨 Design Elements

**Seal Integration:**
- Watermark: 450px, 6% opacity (center)
- Badge: 80px, 100% opacity (top-right)

**Typography:**
- Title: Helvetica Bold 22pt
- Build kit number: Helvetica Bold 16pt
- Details: Helvetica Bold 11pt

**Colors:**
- Primary: #1a1a1a (near-black)
- Gold accents: #DAA520

**QR Code:**
- Size: 1.2" x 1.2"
- Position: Center, below details
- Caption: "Scan for build documentation"

---

## 🖨️ Printing

**Recommended Settings:**
- Paper: Letter (8.5" x 11")
- Quality: Heavyweight (32 lb+)
- Finish: Matte or semi-gloss
- Color: Full color

---

## 📊 Use Cases

### Customer Builds
```bash
python generate_coa.py --serial 0025 \
    --qr "https://sonicbuilder.io/customers/acme-corp"
```

### Community Projects
```bash
python generate_coa.py --serial 0042 \
    --qr "https://github.com/community/variant-xyz"
```

### Personal Documentation
```bash
python generate_coa.py --serial 0007 \
    --qr "https://mydocs.example.com/car-build"
```

---

## 📋 Command Reference

```bash
# Help
python generate_coa.py --help

# Basic CoA
python generate_coa.py --serial XXXX

# With QR code
python generate_coa.py --serial XXXX --qr "URL"

# Custom output
python generate_coa.py --serial XXXX --output custom_dir/
```

---

## 🎯 Auto-Fill Features

**Version:**
- Reads from `../VERSION.txt`
- Automatically updates

**Build Date:**
- Current date
- Format: "Month DD, YYYY"

**Seal Integration:**
- Watermark: From `../Founder_Seal/SonicBuilder_Seal.png`
- Badge: From `../Founder_Seal/SonicBuilder_Badge.png`

---

## 📦 Integration Ready

Perfect for the **USB DAC Integration Bundle:**

```
SonicBuilder_USB_DAC_Integration_Bundle/
├── Founder_Certificate_#0001.pdf          ← Founder cert
├── Founder_Certificate_#0001_Print.pdf
│
├── CoA_Generator/                         ← CoA system
│   ├── generate_coa.py
│   ├── README_CoA.txt
│   ├── EXAMPLES.md
│   └── output/
│       ├── SonicBuilder_CoA_#0002.pdf
│       ├── SonicBuilder_CoA_#0003.pdf
│       └── ...
│
├── SonicBuilder_Manual.pdf
├── README_FOR_CONTRIBUTORS.pdf
└── Founder_Seal/
```

---

## ✨ Complete SonicBuilder System

**Main Manual:** 108 pages, auto-index, QR codes  
**Parts Lists:** YAML-based with QR sourcing  
**Branding:** Full seal + minimal badge  
**Founder Cert:** Christopher Elgin recognition  
**CoA Generator:** Numbered build certification ✅  

---

**SonicBuilder CoA Generator** - Production Ready! 🎉

**Command:** `python generate_coa.py --serial XXXX --qr "URL"`  
**Output:** Professional build certification PDF
