# SonicBuilder Certificate of Authenticity Generator

Auto-generate SonicBuilder Certificates of Authenticity with serial numbers, QR codes, and audit logging.

## Quick Start

```bash
cd tools/CoA_Generator

# Auto-increment (recommended)
python generate_coa.py --auto-increment --qr "https://sonicbuilder.io/manuals/latest"

# Manual serial
python generate_coa.py --serial 0003 --qr "https://your.link/manuals/0003"

# With customer info
python generate_coa.py --auto-increment \
  --customer "Acme Corp - 2014 Sonic LTZ" \
  --qr "https://sonicbuilder.io/customers/acme-001"
```

## Features

- **Auto-increment serial numbers** from CoA_Log.csv
- **Automatic audit logging** of all generated CoAs
- **Customer tracking** for installations
- **Version override** per CoA
- **QR code integration** for documentation links
- **Batch generation** support

## Parameters

```bash
# Required (choose one)
--serial XXXX          # Manual serial number
--auto-increment       # Auto-increment from log

# Optional
--qr URL              # QR code URL
--version VER         # Override version (default: v2.0.9)
--date YYYY-MM-DD     # Build date (default: today)
--installer NAME      # Installer name (default: Christopher Elgin)
--customer NAME       # Customer/installation info
--output-dir DIR      # Output directory (default: output/)
--log FILE            # Log file (default: CoA_Log.csv)
```

## Examples

### Customer Installation
```bash
python generate_coa.py --auto-increment \
  --customer "Premium Audio Install - VIN: 1G1JC5SH0E4123456" \
  --qr "https://sonicbuilder.io/installs/premium-001"
```

### Internal Prototype
```bash
python generate_coa.py --auto-increment \
  --customer "Internal QA Testing" \
  --version v2.6.0-alpha
```

### Batch Generation
```bash
for i in {2..10}; do
  python generate_coa.py --auto-increment \
    --qr "https://sonicbuilder.io/builds/$(printf %04d $i)"
done
```

## Output

**Generated PDFs:** `output/SonicBuilder_CoA_#XXXX.pdf`

**Audit Log:** `CoA_Log.csv`
```csv
serial,date,version,installer,customer,qr,filename
0002,2025-10-28,v2.0.9,Christopher Elgin,,https://sonicbuilder.io/manuals/0002,output/SonicBuilder_CoA_#0002.pdf
```

## GitHub Workflow

The `.github/workflows/coa-on-release.yml` workflow automatically generates a CoA when you create a release:

1. Reads VERSION.txt
2. Auto-increments serial number
3. Generates CoA with release info
4. Commits back to repository

**Trigger:** Create a GitHub release

---

For complete documentation, see: `docs/README_CoA.md`
