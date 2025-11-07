# Artifact Management System

Automated compression, splitting, and verification of release artifacts for SonicBuilder.

## Overview

The artifact management system handles large files in releases through a three-stage process:

1. **Auto-Compression** - Attempt to compress oversized files
2. **Auto-Split** - Split files >200MB into ~180MB parts
3. **Preflight Check** - Verify all artifacts meet size requirements

## Quick Reference

```bash
# Local testing
ALLOW_DIRTY=1 make docs_package_local

# Preview release notes with asset table
make release_notes_preview

# Preview only if split parts exist
make parts_help_preview
```

---

## CI/CD Pipeline Order

When you push a tag, the `docs-release.yml` workflow executes these steps:

```
1. Build docs
2. Stamp PDFs with metadata
3. Rename files with commit hash (_g{COMMIT})
4. Verify PDF metadata + suffix
5. Auto-compress oversize artifacts       ⬅ NEW
6. Auto-split oversized artifacts         ⬅ NEW
7. Preflight size check                   ⬅ NEW
8. Upload to GitHub Release (only if passed)
9. Enrich release notes (assets + parts help)
10. Update README with latest docs
```

---

## Size Limits

| Type | Limit | Enforcement |
|------|-------|-------------|
| PDF files | Unlimited | No limit |
| Non-PDF files | 200 MB | Preflight check |
| Split parts | ~180 MB each | Auto-generated |

**Note:** PDF files are exempt from size limits due to the nature of documentation manuals.

---

## Auto-Compression

**Script:** `scripts/auto_compress.py`

### What It Does

1. Scans `release_assets/` for files/folders >200MB (non-PDF)
2. Attempts to compress with maximum compression (`zip -9`)
3. For existing ZIPs, unpacks and repacks with `-9`
4. Keeps smaller version if recompression doesn't help

### Example Output

```
Found 2 oversize artifacts > 200 MB (non-PDF). Attempting compression...
 - dist: 210.50 MB (dir)
   ↳ zipped → dist.zip (98.20 MB)
 - large_archive.zip: 205.00 MB (file)
   ↳ repacked → large_archive.repacked.zip (195.00 MB)

Compression summary:
 ✅ dist.zip: 98.20 MB
 ⚠️  large_archive.zip: 195.00 MB (still over 200 MB)
```

### Manifest

Writes `COMPRESSION_MANIFEST.txt` with compression results:

```
Compressed OK:
  - dist.zip  102975488 bytes

Still oversize:
  - large_archive.zip  204472320 bytes
```

---

## Auto-Split

**Script:** `scripts/split_large_artifacts.py`

### What It Does

1. Finds files >200MB (non-PDF, not already .partNN)
2. Splits into ~180MB chunks
3. Names parts: `{file}.part01`, `{file}.part02`, etc.
4. Generates reassembly instructions

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SB_SPLIT_LIMIT_MB` | 200 | Size threshold for splitting |
| `SB_SPLIT_PART_MB` | 180 | Target size for each part |

### Example Output

```
- dist_ge05247101a22.zip (210.50 MB) exceeds 200 MB; splitting…
   ↳ split dist_ge05247101a22.zip → 2 parts (<~180 MB each)
   • dist_ge05247101a22.zip.part01 (180.00 MB)
   • dist_ge05247101a22.zip.part02 (30.50 MB)
```

### Reassembly Instructions

**macOS / Linux:**
```bash
cat dist_ge05247101a22.zip.part* > dist_ge05247101a22.zip
unzip dist_ge05247101a22.zip
```

**Windows PowerShell:**
```powershell
Get-ChildItem dist_ge05247101a22.zip.part* | Get-Content -Encoding Byte -ReadCount 0 | Set-Content -Encoding Byte dist_ge05247101a22.zip
Expand-Archive .\dist_ge05247101a22.zip
```

### Manifest

Writes `SPLIT_MANIFEST.txt` with reassembly instructions.

---

## Preflight Check

**Script:** `scripts/preflight_size_check.py`

### What It Does

1. Final check before upload
2. Verifies no non-PDF files >200MB (except .partNN files)
3. **Blocks release upload if check fails**

### Example Output

**Success:**
```
✅ Preflight size check passed.
```

**Failure:**
```
❌ Preflight check failed: 1 offending file(s) exceed 200 MB (non-PDF):
   - huge_archive.zip (315.00 MB)

💡 Either compress/split these files or exclude them from release.
```

**Exit Code:** 2 (blocks workflow)

---

## Release Notes Enhancement

### Assets Table

**Always included** in release notes:

```markdown
<!-- SB_ASSETS_TABLE_BEGIN -->
### Download assets (verified)

| File | Size | SHA256 |
|---|---:|---|
| [dist_ge05247101a22.zip](https://...) | 98.20 MB | `f548f7e5a476...` |
| [supersonic_manual_dark_ge05247101a22.pdf](https://...) | 65.00 MB | `abc123def456...` |
<!-- SB_ASSETS_TABLE_END -->
```

### Parts Help (Conditional)

**Only included** if `.zip.partNN` files exist:

```markdown
<!-- SB_PARTS_HELP_BEGIN -->
### How to reassemble multi-part ZIPs

**macOS / Linux:**

```bash
cat <file>.zip.part* > <file>.zip
unzip <file>.zip
```

**Windows (PowerShell):**

```powershell
Get-ChildItem <file>.zip.part* | Get-Content -Encoding Byte -ReadCount 0 | Set-Content -Encoding Byte <file>.zip
Expand-Archive .\<file>.zip
```

**Parts included:**

| Part | Size |
|---|---:|
| dist_ge05247101a22.zip.part01 | 180 MB |
| dist_ge05247101a22.zip.part02 | 31 MB |
<!-- SB_PARTS_HELP_END -->
```

---

## Local Testing

### Build and Package

```bash
# Build docs locally
ALLOW_DIRTY=1 make docs_build_local

# Full package (stamps, renames, zips, checksums)
ALLOW_DIRTY=1 make docs_package_local
```

### Preview Release Notes

```bash
# Preview assets table only
make assets_table_preview

# Preview parts help (only shows if .partNN files exist)
make parts_help_preview

# Complete release notes preview (assets + parts)
make release_notes_preview

# Write to file for sharing
make release_notes_preview_md  # → RELEASE_NOTES_PREVIEW.md
```

### Test Artifact Scripts

```bash
# Test compression
python3 scripts/auto_compress.py

# Test splitting (with custom limits)
SB_SPLIT_LIMIT_MB=150 SB_SPLIT_PART_MB=120 python3 scripts/split_large_artifacts.py

# Test preflight check
python3 scripts/preflight_size_check.py release_assets
```

---

## Workflow Integration

### docs-release.yml

```yaml
- name: Auto-compress oversize non-PDF artifacts
  run: python3 scripts/auto_compress.py

- name: Auto-split oversize non-PDF artifacts into parts (~180MB)
  env:
    SB_SPLIT_LIMIT_MB: "200"
    SB_SPLIT_PART_MB: "180"
  run: python3 scripts/split_large_artifacts.py

- name: Preflight size check (non-PDF artifacts)
  run: python3 scripts/preflight_size_check.py release_assets
```

### docs-release-notes-enricher.yml

```yaml
- name: Generate PARTS.md (if split parts present)
  run: |
    python - << 'PY'
    # Detects .zip.partNN files
    # Generates reassembly instructions
    # Only adds to release notes if parts exist
    PY
```

### readme-latest-docs.yml

```yaml
# Updated asset filter to include .zip.partNN files
const assets = (rel.assets || []).filter(a => /\.(pdf|zip(\.part\d+)?)$/i.test(a.name));
```

---

## File Structure

```
scripts/
  auto_compress.py          # Compression with zip -9
  split_large_artifacts.py  # Split >200MB into ~180MB parts
  preflight_size_check.py   # Final size verification

release_assets/
  dist_ge05247101a22.zip.part01
  dist_ge05247101a22.zip.part02
  COMPRESSION_MANIFEST.txt
  SPLIT_MANIFEST.txt
  SHA256SUMS.txt

Makefile
  assets_table_preview
  parts_help_preview
  release_notes_preview
  release_notes_preview_md
```

---

## Troubleshooting

### Compression doesn't reduce size enough

**Cause:** Files already well-compressed (PDFs, JPEGs, existing ZIPs)

**Solution:** Files will proceed to splitting step

### Splitting fails

**Cause:** Permission errors or disk space

**Fix:**
```bash
# Check permissions
ls -la release_assets/

# Check disk space
df -h
```

### Preflight check blocks release

**Cause:** File >200MB after compression and splitting

**Solutions:**
1. Exclude file from release
2. Manually compress with higher compression
3. Adjust `SB_SPLIT_LIMIT_MB` environment variable

### Parts not showing in release notes

**Cause:** `.partNN` files not detected

**Check:**
```bash
ls release_assets/*.zip.part*
```

### README not showing .partNN files

**Cause:** Asset filter pattern mismatch

**Verify:** Check `.github/workflows/readme-latest-docs.yml`:
```javascript
const assets = (rel.assets || []).filter(a => /\.(pdf|zip(\.part\d+)?)$/i.test(a.name));
```

---

## Best Practices

1. **Test locally before releasing**
   ```bash
   ALLOW_DIRTY=1 make docs_package_local
   make release_notes_preview
   ```

2. **Monitor compression effectiveness**
   - Check `COMPRESSION_MANIFEST.txt` after build
   - Identify files that don't compress well

3. **Communicate split files to users**
   - Release notes automatically include reassembly instructions
   - README shows all parts in download table

4. **Version control**
   - `.gitignore` includes `release_assets/`
   - Never commit generated artifacts
   - Only commit scripts and workflows

5. **Customize limits for your project**
   ```yaml
   env:
     SB_SPLIT_LIMIT_MB: "250"  # Increase if needed
     SB_SPLIT_PART_MB: "200"   # Larger parts
   ```

---

## Examples

### Example 1: Small Project (All files <200MB)

```
Pipeline execution:
1. Build docs → 85 MB total
2. Auto-compress → No action needed
3. Auto-split → No action needed
4. Preflight → ✅ Pass

Release notes:
- Assets table only
- No parts help section
```

### Example 2: Large Project (dist.zip = 320MB)

```
Pipeline execution:
1. Build docs → dist.zip 320 MB
2. Auto-compress → dist.zip 315 MB (marginal improvement)
3. Auto-split → dist.zip.part01 (180 MB), dist.zip.part02 (135 MB)
4. Preflight → ✅ Pass

Release notes:
- Assets table (shows both parts)
- Parts help section with reassembly instructions
```

### Example 3: Mixed Files

```
release_assets/
  manual.pdf                     120 MB  ✅ (PDF exempt)
  appendix.zip                    45 MB  ✅
  images.zip                     250 MB  → compressed → 190 MB ✅
  huge_data.zip                  500 MB  → compressed → 480 MB
                                        → split → .part01-03 ✅

All files pass preflight ✅
```

---

## Version History

- **v2.0.9+SB-appendix-demo** - Initial artifact management system
  - Auto-compression with zip -9
  - Auto-splitting into ~180MB parts
  - Preflight size verification
  - Release notes enhancement with parts help
  - README integration for .partNN files
