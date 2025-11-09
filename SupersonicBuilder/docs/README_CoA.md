# SonicBuilder Certificate of Authenticity (CoA) System

Complete documentation for the SonicBuilder CoA generator and automation system.

## Overview

The SonicBuilder CoA system generates numbered Certificates of Authenticity for build kits, with automatic serial tracking, audit logging, and GitHub workflow integration.

## Features

✅ **Auto-increment serial numbers** - No manual tracking needed  
✅ **CSV audit logging** - Complete trail of all generated CoAs  
✅ **Customer tracking** - Record installation details  
✅ **Version control** - Per-CoA version override  
✅ **QR code integration** - Link to documentation  
✅ **GitHub automation** - Auto-mint on release  

---

## Quick Start

### Installation

```bash
pip install reportlab qrcode pillow
```

### Basic Usage

```bash
cd tools/CoA_Generator

# Auto-increment (recommended)
python generate_coa.py --auto-increment --qr "https://sonicbuilder.io/latest"

# Manual serial
python generate_coa.py --serial 0042 --qr "https://your.link/manual"
```

---

## Parameters

### Required (Choose One)

- `--serial XXXX` - Manual serial number (e.g., 0002, 0042, 0100)
- `--auto-increment` - Auto-increment from CoA_Log.csv

### Optional

- `--qr URL` - QR code URL for documentation link
- `--version VER` - Version override (default: v2.0.9)
- `--date YYYY-MM-DD` - Build date (default: today)
- `--installer NAME` - Installer name (default: Christopher Elgin)
- `--customer NAME` - Customer/installation info
- `--output-dir DIR` - Output directory (default: output/)
- `--log FILE` - Log file (default: CoA_Log.csv)

---

## Usage Examples

### Customer Installation

```bash
python generate_coa.py --auto-increment \
  --customer "Acme Corp - 2014 Chevy Sonic LTZ" \
  --qr "https://sonicbuilder.io/customers/acme-001" \
  --installer "Christopher Elgin"
```

### Internal Prototype

```bash
python generate_coa.py --auto-increment \
  --customer "Internal Prototype Build - Beta Testing" \
  --version v2.6.0-beta \
  --qr "https://github.com/user/sonicbuilder/tree/beta"
```

### Community Build

```bash
python generate_coa.py --auto-increment \
  --customer "Community Build - John Doe Variant" \
  --installer "John Doe (Verified by C. Elgin)" \
  --qr "https://community.sonicbuilder.io/builds/042"
```

### Warranty Replacement

```bash
python generate_coa.py --auto-increment \
  --customer "Warranty Replacement for CoA #0025" \
  --qr "https://support.sonicbuilder.io/warranty/001"
```

---

## Batch Generation

### Multiple Customer Builds

```bash
#!/bin/bash

customers=(
    "Acme Corp - Unit 001"
    "Beta Motors - Unit 002"
    "Gamma Auto - Unit 003"
)

for customer in "${customers[@]}"; do
    python generate_coa.py --auto-increment \
        --customer "$customer" \
        --qr "https://sonicbuilder.io/customers/$(echo $customer | sed 's/ /-/g' | tr '[:upper:]' '[:lower:]')"
    echo "✅ Generated for: $customer"
done
```

### Sequential Builds

```bash
for i in {2..10}; do
    serial=$(printf "%04d" $i)
    python generate_coa.py --auto-increment \
        --qr "https://sonicbuilder.io/builds/$serial"
done
```

---

## CoA_Log.csv Format

Every generated CoA is automatically logged:

```csv
serial,date,version,installer,customer,qr,filename
0002,2025-10-28,v2.5.0,Christopher Elgin,,https://sonicbuilder.io/manuals/0002,output/SonicBuilder_CoA_#0002.pdf
0003,2025-10-28,v2.5.0,Christopher Elgin,,https://sonicbuilder.io/latest,output/SonicBuilder_CoA_#0003.pdf
0004,2025-10-28,v2.5.0,Christopher Elgin,Acme Corp Installation,https://sonicbuilder.io/acme,output/SonicBuilder_CoA_#0004.pdf
```

### Log Analysis

```bash
# Count total CoAs
tail -n +2 CoA_Log.csv | wc -l

# Find latest serial
tail -1 CoA_Log.csv | cut -d',' -f1

# List all customers
tail -n +2 CoA_Log.csv | cut -d',' -f5 | sort | uniq

# Search for customer
grep "Acme Corp" CoA_Log.csv
```

---

## GitHub Workflow Automation

The `.github/workflows/coa-on-release.yml` workflow automatically generates a CoA when you publish a GitHub release.

### How It Works

1. **Trigger:** You publish a GitHub release
2. **Setup:** Workflow installs Python dependencies
3. **Generate:** Creates CoA with auto-increment serial
4. **Commit:** Commits CoA and log back to repository
5. **Upload:** Attaches CoA PDF to release assets
6. **Comment:** Posts CoA info as release comment

### What Gets Generated

- **Serial:** Auto-incremented from CoA_Log.csv
- **Version:** Read from VERSION.txt
- **Customer:** "GitHub Release {tag}"
- **QR Code:** Links to release URL
- **Date:** Release publication date

### Example Output

When you create release `v2.5.0`:

```
✅ Certificate of Authenticity Generated

Serial: SB-0042
Version: v2.5.0
Date: 2025-10-28

Certificate attached to release assets.
```

---

## Certificate Format

Each CoA includes:

```
═══════════════════════════════════════════════════════

          SONICBUILDER PLATFORM
       CERTIFICATE OF AUTHENTICITY

          Serial Number: SB-0042

──────────────────────────────────────────────────────

       This document certifies that

        SONICBUILDER BUILD KIT #0042

         was produced and verified by

   Christopher Elgin — SonicBuilder Founder

      as an official SonicBuilder project.

──────────────────────────────────────────────────────

Platform: EOENKK Android 15 + Maestro RR2 GM5
Version: v2.5.0
Build Date: October 28, 2025
Built for: [Customer Name]

           [QR CODE]
     Scan for build documentation

──────────────────────────────────────────────────────

        Christopher Elgin
     SonicBuilder Founder
      October 28, 2025

═══════════════════════════════════════════════════════
```

---

## Serial Number System

| Range | Purpose |
|-------|---------|
| **#0001** | **Reserved** - Founder Certificate |
| #0002-0099 | Prototypes and initial builds |
| #0100-0999 | Customer installations |
| #1000-9999 | Production units |
| #10000+ | Large-scale manufacturing |

**Format:** SB-XXXX (e.g., SB-0002, SB-0100, SB-1000)

---

## Best Practices

### Use Auto-Increment

```bash
# ✅ Good - Automatic tracking
python generate_coa.py --auto-increment

# ⚠️ Manual only when needed
python generate_coa.py --serial 0042
```

### Include Customer Info

```bash
# ✅ Good - Full traceability
python generate_coa.py --auto-increment \
  --customer "John Smith - 2014 Sonic LTZ" \
  --qr "https://support.example.com/build-042"

# ❌ Less useful - No context
python generate_coa.py --auto-increment
```

### Use Permanent QR URLs

```bash
# ✅ Good - Permanent, traceable
--qr "https://sonicbuilder.io/builds/0042"

# ❌ Bad - Temporary, breaks
--qr "https://dropbox.com/s/abc123/temp.pdf"
```

---

## Backup & Recovery

### Backup Log

```bash
cp CoA_Log.csv CoA_Log_backup_$(date +%Y%m%d).csv
```

### Archive Generated CoAs

```bash
tar -czf CoA_Archive_$(date +%Y%m%d).tar.gz output/ CoA_Log.csv
```

### Restore from Backup

```bash
cp CoA_Log_backup_20251028.csv CoA_Log.csv
```

---

## Troubleshooting

### QR Code Not Generating

**Issue:** `[warn] Could not generate QR code`

**Solution:**
```bash
pip install qrcode pillow
```

### Serial Number Conflict

**Issue:** Duplicate serial numbers

**Solution:**
- Use `--auto-increment` instead of manual serials
- Check CoA_Log.csv for last serial
- Backup and clean log if corrupted

### Missing Dependencies

**Issue:** Import errors

**Solution:**
```bash
pip install reportlab qrcode pillow
```

---

## Integration with SonicBuilder System

The CoA generator integrates seamlessly with the SonicBuilder documentation system:

```
SonicBuilder_Project/
├── tools/
│   └── CoA_Generator/          ← CoA generation
│       ├── generate_coa.py
│       ├── CoA_Log.csv
│       └── output/
├── scripts/
│   ├── gen_manual.py           ← Manual generation
│   └── gen_seal.py             ← Seal generation
├── certificates/
│   └── Founder_Certificate_#0001.pdf
├── Founder_Seal/               ← Branding assets
├── VERSION.txt                 ← Version source
└── .github/workflows/
    └── coa-on-release.yml      ← Automation
```

---

## Support

For issues or questions:

1. Check this documentation
2. Review `tools/CoA_Generator/README.md`
3. Check GitHub workflow logs
4. Review CoA_Log.csv for tracking

---

## License

Part of the SonicBuilder Platform  
Founded by Christopher Elgin (#0001)

---

**Ready to generate professional Certificates of Authenticity!** 🎉
