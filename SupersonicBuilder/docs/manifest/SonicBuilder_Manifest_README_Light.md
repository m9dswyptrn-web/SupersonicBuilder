# SonicBuilder Manifest — v5.0.0

**Build date:** 2025-10-31T19:37:15.765777

**Primary ZIP SHA-256:** `(zip not found)`


---

## Style (Light)
White/cream backgrounds, muted accents.

## Quick Commands
```bash
python3 render_manifest.py --version 5.0.0 --release-zip /path/to/SonicBuilder_2025-10-31_v5.0.0.zip --out ./dist --all
python3 render_manifest.py --version 5.0.0 --out ./dist --dark-only
python3 render_manifest.py --version 5.0.0 --out ./dist --light-only
```

## Package Structure
- ManifestPackage/ (Dark Edition)
- ManifestPackage_Light/ (Light Edition)
- SonicBuilder_Manifest_Package_v5.0.0_FULL.zip
- Version_Certificate*.pdf
- README.txt and CHECKSUMS.txt per edition

## Integration (builder.py hook)
```python
p.add_argument("--render-manifest", action="store_true",
              help="Render dark+light manifest and bundle FULL.zip")
# after packaging in run_build_once()
import subprocess, sys
release_zip = str(full_zip) if full_zip else ""
subprocess.run([sys.executable, "render_manifest.py",
                "--version", version_str,
                "--release-zip", release_zip,
                "--out", str(ROOT),
                "--all"], check=True)
```

## Themes
Dark: Industrial_DarkMetal, Retro_Blueprint, OEM_ShopManual
Light: Industrial_LightSteel, Retro_Draftsheet, OEM_ServiceWhite

## Print & Archive
- Manuals: 8.5×11 in, 300–600 DPI
- FieldCards: 5.5×8.5 in, 7–10 mil laminate
- Keep SHA-256 footer visible for version traceability

