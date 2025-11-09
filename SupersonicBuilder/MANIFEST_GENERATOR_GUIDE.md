# 📜 SonicBuilder Manifest Generator Guide

## Overview

The **Manifest Generator** creates professional, certified PDF documentation packages with:
- **Certified Manifests** - Full technical manuals (8.5x11")
- **Field Cards** - Laminated quick-reference cards (5.5x8.5")
- **Certificates** - Version certificates with QR codes
- **Theme Support** - 6 professional themes (3 dark + 3 light)
- **SHA-256 Checksums** - Complete integrity verification

---

## Quick Start

### Generate Complete Manifest Package

```bash
./generate_manifest.sh 5.0.0 downloads/latest.pdf docs/manifests
```

**Arguments:**
1. Version number (e.g., `5.0.0`)
2. Path to release ZIP/PDF for checksum
3. Output directory

---

## Features

### 📦 Package Contents

Each manifest package includes:

**Dark Themes:**
- Industrial DarkMetal
- Retro Blueprint  
- OEM ShopManual

**Light Themes:**
- Industrial LightSteel
- Retro Draftsheet
- OEM ServiceWhite

**Files per theme:**
- `Manifest_Full.pdf` - Complete technical manual
- `FieldCards.pdf` - 3-card quick reference set

**Additional files:**
- `Version_Certificate.pdf` - Dark certificate
- `Version_Certificate_Light.pdf` - Light certificate
- `README.txt` - Package documentation
- `CHECKSUMS.txt` - SHA-256 verification

---

## Usage Examples

### 1. Generate Both Dark & Light (Default)

```bash
python3 render_manifest.py \
  --version 5.0.0 \
  --release-zip downloads/latest.pdf \
  --out docs/manifests \
  --all
```

**Output:**
- `docs/manifests/ManifestPackage/` (Dark themes)
- `docs/manifests/ManifestPackage_Light/` (Light themes)
- `docs/manifests/SonicBuilder_Manifest_Package_v5.0.0_FULL.zip`

### 2. Dark Themes Only

```bash
python3 render_manifest.py \
  --version 5.0.0 \
  --out docs/manifests \
  --dark-only
```

### 3. Light Themes Only

```bash
python3 render_manifest.py \
  --version 5.0.0 \
  --out docs/manifests \
  --light-only
```

### 4. Without Release ZIP (No Checksum)

```bash
python3 render_manifest.py \
  --version 5.0.0 \
  --out docs/manifests \
  --all
```

Checksum will show as "(zip not found)"

---

## Integration with Auto Orchestrator

Add manifest generation to your build pipeline:

```python
# In auto_orchestrator.py
MANIFEST_SCRIPT = "generate_manifest.sh"

if os.path.exists(MANIFEST_SCRIPT):
    run_step("Generate Manifests", f"bash {MANIFEST_SCRIPT} 5.0.0")
```

---

## Theme Showcase

### Dark Themes

**Industrial DarkMetal**
- Background: Pure black
- Text: Light gray (#E6E6E6)
- Accent: Cyan (#00D2FF)
- Best for: High-contrast technical documentation

**Retro Blueprint**
- Background: Deep blue (#0D1B3D)
- Text: White
- Accent: Neon green (#36F9A0)
- Best for: Classic engineering aesthetic

**OEM ShopManual**
- Background: Dark gray (#1C1C1C)
- Text: Cream (#E7D8A7)
- Accent: Red (#E53935)
- Best for: Automotive manual style

### Light Themes

**Industrial LightSteel**
- Background: Off-white
- Text: Dark navy (#1F2933)
- Accent: Sky blue (#0EA5E9)
- Best for: Professional print documentation

**Retro Draftsheet**
- Background: Cream (#FAF7F2)
- Text: Dark blue (#0B4F6C)
- Accent: Green (#22C55E)
- Best for: Vintage engineering drawings

**OEM ServiceWhite**
- Background: Pure white
- Text: Black (#1F1F1F)
- Accent: Red (#E53935)
- Best for: OEM service manuals

---

## Manifest Contents

Each manifest PDF includes:

### Page 1: Cover
- SonicBuilder version
- Theme identifier
- Decorative grid pattern

### Page 2+: Documentation Sections
- **Version Timeline** - v4.0 → v5.0 feature evolution
- **CLI Command Map** - All build.sh options
- **Workflows** - Tuning, Release, Compare modes
- **Config** - sonicbuilder.toml settings
- **Report Screens** - Placeholder for screenshots

### Footer
- Version number
- SHA-256 checksum (first 32 chars)
- Generation date

---

## Field Cards

Three laminated cards (5.5" x 8.5"):

**Tuning Card**
```
--mode tuning
--html-report --html-dark --html-bands
--diff group/A.json,group/B.json
--adb-group <name> --zip-group-only
```

**Release Card**
```
--mode release
--export-schema --lint --autofix
PDFs on, HTML report dark
Versioned outputs, checksums
```

**Compare Card**
```
--mode compare
--diff group/A.json,group/B.json
Auto-pair if omitted
```

---

## Certificates

Professional version certificates with:
- SonicBuilder branding
- Version information
- Primary package details
- SHA-256 checksum
- QR code (version + checksum)
- Generation timestamp

---

## Checksums

Every PDF is SHA-256 hashed and listed in `CHECKSUMS.txt`:

```
a1b2c3d4...  Industrial_DarkMetal/Manifest_Full.pdf
e5f6g7h8...  Industrial_DarkMetal/FieldCards.pdf
...
```

Verify integrity:
```bash
cd docs/manifests/ManifestPackage
sha256sum -c CHECKSUMS.txt
```

---

## Directory Structure

After generation:

```
docs/manifests/
├── ManifestPackage/                 (Dark themes)
│   ├── Industrial_DarkMetal/
│   │   ├── Manifest_Full.pdf
│   │   └── FieldCards.pdf
│   ├── Retro_Blueprint/
│   │   ├── Manifest_Full.pdf
│   │   └── FieldCards.pdf
│   ├── OEM_ShopManual/
│   │   ├── Manifest_Full.pdf
│   │   └── FieldCards.pdf
│   ├── Version_Certificate.pdf
│   ├── README.txt
│   └── CHECKSUMS.txt
│
├── ManifestPackage_Light/           (Light themes)
│   ├── Industrial_LightSteel/
│   ├── Retro_Draftsheet/
│   ├── OEM_ServiceWhite/
│   ├── Version_Certificate_Light.pdf
│   ├── README.txt
│   └── CHECKSUMS.txt
│
└── SonicBuilder_Manifest_Package_v5.0.0_FULL.zip
```

---

## Command Line Options

```
python3 render_manifest.py [OPTIONS]

Required:
  --version VERSION       Version string (e.g., 5.0.0)

Optional:
  --release-zip PATH      Path to release ZIP for checksum
  --out DIR               Output directory (default: ./dist)
  
Modes (mutually exclusive):
  --all                   Both dark+light + FULL.zip (default)
  --dark-only             Dark themes only
  --light-only            Light themes only
```

---

## Dependencies

All required dependencies already installed:
- ✅ `reportlab` - PDF generation
- ✅ `qrcode` - QR code generation
- ✅ `Pillow` - Image support

---

## File Sizes (Approximate)

- **Manifest PDF:** 40-60 KB each
- **Field Cards:** 15-25 KB each
- **Certificate:** 30-40 KB each
- **Complete package:** ~500 KB (all themes)
- **FULL.zip:** ~200-300 KB (compressed)

---

## Best Practices

1. **Always generate checksums:**
   ```bash
   python3 render_manifest.py --version 5.0.0 --release-zip path/to/release.zip --all
   ```

2. **Verify after generation:**
   ```bash
   cd docs/manifests/ManifestPackage
   sha256sum -c CHECKSUMS.txt
   ```

3. **Archive old versions:**
   ```bash
   mv docs/manifests/ManifestPackage docs/manifests/archive/v5.0.0/
   ```

4. **Test QR codes:**
   Use phone camera to scan certificates and verify data

---

## Troubleshooting

### No PDF Output
```bash
# Check ReportLab installation
python3 -c "from reportlab.pdfgen import canvas; print('OK')"
```

### Checksum Shows "(zip not found)"
Provide valid path to release ZIP:
```bash
python3 render_manifest.py --version 5.0.0 --release-zip downloads/latest.pdf --all
```

### Permission Denied
Make output directory writable:
```bash
chmod +w docs/manifests
```

### QR Code Not Scanning
- Ensure good lighting
- Use high-contrast theme
- Print at least 1.5" x 1.5" size

---

## Integration Examples

### With supersonic_autodeploy.py

```python
import subprocess

# Generate PDF
subprocess.run(["python3", "supersonic_autodeploy.py"])

# Generate manifests
subprocess.run([
    "python3", "render_manifest.py",
    "--version", "5.0.0",
    "--release-zip", "downloads/latest.pdf",
    "--out", "docs/manifests",
    "--all"
])
```

### With Auto Orchestrator

Add to `auto_orchestrator.py`:

```python
# After PDF generation
if os.path.exists("render_manifest.py"):
    run_step("Generate Manifests", 
             "bash generate_manifest.sh 5.0.0 downloads/latest.pdf docs/manifests")
```

---

## Advanced Usage

### Custom Version String

```bash
python3 render_manifest.py --version "5.0.0-beta" --out dist --all
```

### Separate Dark/Light Builds

```bash
# Dark only
python3 render_manifest.py --version 5.0.0 --out dist/dark --dark-only

# Light only  
python3 render_manifest.py --version 5.0.0 --out dist/light --light-only
```

### Multiple Releases

```bash
for v in 5.0.0 5.1.0 5.2.0; do
    python3 render_manifest.py \
        --version "$v" \
        --release-zip "releases/SonicBuilder_v${v}.zip" \
        --out "docs/manifests/v${v}" \
        --all
done
```

---

## Changelog

**v5.0.0** (2025-10-31)
- Initial integration into SonicBuilder
- 6 professional themes (3 dark + 3 light)
- QR code certificates
- SHA-256 checksums
- Field card generation
- FULL.zip packaging

---

## Support

For issues or questions:
1. Check ReportLab is installed: `pip list | grep reportlab`
2. Verify output directory permissions
3. Test with minimal command: `python3 render_manifest.py --version 1.0.0 --out /tmp --dark-only`

---

**Generated by SonicBuilder Manifest System v5.0**  
*Professional PDF Documentation for Android Head Unit Installation*
