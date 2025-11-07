# PDF Verification System

Automated verification of PDF metadata and filename conventions for SonicBuilder releases.

## Overview

The verification system ensures that all PDFs in releases have:
1. **Required metadata fields** embedded in the PDF
2. **Correct commit hash** in both metadata and filename
3. **Consistent naming** with `_g{COMMIT}` suffix

## Quick Reference

```bash
# Verify metadata only (no suffix required)
python3 scripts/verify_pdf_meta.py --root release_assets --commit e05247101a22

# Verify metadata + require _g{commit} suffix
python3 scripts/verify_pdf_meta.py --root release_assets --require-suffix --commit e05247101a22
```

---

## Required Metadata Fields

Every SonicBuilder PDF must contain these metadata fields:

| Field | Description | Example |
|-------|-------------|---------|
| `/Version` | Release version | `v2.0.9+SB-appendix-demo` |
| `/Commit` | Short commit hash | `e05247101a22` |
| `/BuildDate` | Build timestamp (ISO 8601) | `2025-10-28T22:40:47Z` |
| `/Repository` | GitHub repository | `owner/repo` |
| `/Producer` | PDF producer | `SonicBuilder` |
| `/Creator` | PDF creator | `SonicBuilder PDF Pipeline` |

---

## CI/CD Integration

### docs-build.yml (Metadata Verification)

**When:** Push to main, nightly builds, manual triggers  
**Purpose:** Verify that PDF stamping works correctly  
**Requirements:** Metadata fields only (no filename suffix required)

```yaml
- name: Verify PDF metadata (docs-build)
  run: |
    SB_COMMIT=$(git rev-parse --short=12 HEAD 2>/dev/null || echo "${GITHUB_SHA:0:12}")
    python3 scripts/verify_pdf_meta.py --root release_assets --commit "$SB_COMMIT"
```

**Success:** All PDFs have required metadata  
**Failure:** Missing or invalid metadata fields

---

### docs-release.yml (Full Verification)

**When:** Tag push (`v*`), release published  
**Purpose:** Verify complete release package integrity  
**Requirements:** Metadata + filename suffix `_g{COMMIT}`

```yaml
- name: Build docs
  run: make docs_ci VERSION="${VERSION}"

- name: Stamp and rename release assets with commit
  run: |
    COMMIT_SHORT=$(echo "${{ github.sha }}" | cut -c1-12)
    SB_VERSION="${{ steps.ver.outputs.version }}"
    SB_COMMIT="$COMMIT_SHORT"
    SB_BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    SB_REPO="${{ github.repository }}"
    export SB_VERSION SB_COMMIT SB_BUILD_DATE SB_REPO
    python3 scripts/stamp_commit_meta.py release_assets
    cd release_assets
    for f in *.pdf *.zip; do
      [ -f "$f" ] || continue
      base="${f%.*}"
      ext="${f##*.}"
      mv "$f" "${base}_g${COMMIT_SHORT}.${ext}"
    done

- name: Verify PDF metadata + suffix (release)
  run: |
    COMMIT_SHORT=$(echo "${{ github.sha }}" | cut -c1-12)
    python3 scripts/verify_pdf_meta.py --root release_assets --require-suffix --commit "$COMMIT_SHORT"
```

**Success:** All assets properly stamped and renamed  
**Failure:** Blocks release upload if verification fails

---

## Verification Script

**Location:** `scripts/verify_pdf_meta.py`

### Options

```bash
python3 scripts/verify_pdf_meta.py [OPTIONS]

Options:
  --root DIR              Directory to scan for PDFs (default: release_assets)
  --require-suffix        Require filenames to include _g<commit>.pdf
  --commit HASH           Expected short commit hash (12 chars)
  -h, --help              Show help message
```

### Exit Codes

- **0** - All verifications passed
- **2** - One or more verifications failed

### Example Output

**Success:**
```
[OK]   supersonic_manual_dark_ge05247101a22.pdf
[OK]   supersonic_manual_light_ge05247101a22.pdf
[OK]   parts_tools_dark_ge05247101a22.pdf
[OK]   parts_tools_light_ge05247101a22.pdf
```

**Failure (missing metadata):**
```
[FAIL] example.pdf: missing one or more required metadata keys ['/Version', '/Commit', '/BuildDate', '/Repository']
       found: ['/Author', '/CreationDate', '/Producer']
```

**Failure (wrong commit):**
```
[FAIL] manual_g8b2a3f6d.pdf: /Commit does not contain expected short SHA 'e05247101a22' (got 8b2a3f6d)
```

**Failure (missing suffix):**
```
[FAIL] manual.pdf: filename missing _g<commit> suffix
```

**Failure (mismatched suffix):**
```
[FAIL] manual_g8b2a3f6d.pdf: filename commit '8b2a3f6d' does not match expected 'e05247101a22'
```

---

## Naming Conventions

### Release Files

All release assets MUST follow this pattern:

```
{basename}_g{COMMIT}.{ext}

Examples:
  supersonic_manual_dark_ge05247101a22.pdf
  parts_tools_light_ge05247101a22.pdf
  dist_ge05247101a22.zip
  Appendix_C_I2S_Integration_ge05247101a22.zip
```

### Commit Hash Format

- **Length:** 12 characters (short SHA)
- **Prefix:** `g` (git)
- **Pattern:** `_g[0-9a-f]{12}`
- **Example:** `_ge05247101a22`

---

## Local Testing

### Test Metadata Only

```bash
# Build docs locally
ALLOW_DIRTY=1 make docs_build_local

# Verify metadata (no suffix required)
SB_COMMIT=$(git rev-parse --short=12 HEAD)
python3 scripts/verify_pdf_meta.py --root release_assets --commit "$SB_COMMIT"
```

### Test Full Release

```bash
# Build and package with commit suffix
ALLOW_DIRTY=1 make docs_package_local

# Verify metadata + suffix
SB_COMMIT=$(git rev-parse --short=12 HEAD)
python3 scripts/verify_pdf_meta.py --root release_assets --require-suffix --commit "$SB_COMMIT"
```

---

## How It Works

### 1. Stamping (stamp_commit_meta.py)

```python
# Embed metadata in PDF
metadata = {
    "/Version": "v2.0.9+SB-appendix-demo",
    "/Commit": "e05247101a22",
    "/BuildDate": "2025-10-28T22:40:47Z",
    "/Repository": "owner/repo",
    "/Producer": "SonicBuilder",
    "/Creator": "SonicBuilder PDF Pipeline"
}
```

### 2. Renaming (CI or local build)

```bash
# Rename files to include commit
for f in *.pdf *.zip; do
  base="${f%.*}"
  ext="${f##*.}"
  mv "$f" "${base}_g${COMMIT}.${ext}"
done
```

### 3. Verification (verify_pdf_meta.py)

```python
# Check metadata
required = ["/Version", "/Commit", "/BuildDate", "/Repository"]
for key in required:
    assert key in pdf.metadata

# Check filename suffix (release only)
if require_suffix:
    assert re.search(r"_g[0-9a-f]{12}\.pdf$", filename)
    
# Check commit consistency
assert metadata["/Commit"] == expected_commit
assert filename_commit == expected_commit
```

---

## Troubleshooting

### Verification fails: "missing metadata keys"

**Cause:** PDF wasn't stamped with `stamp_commit_meta.py`

**Fix:**
```bash
SB_VERSION="v2.0.9" SB_COMMIT="abc123456789" \
  SB_BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  SB_REPO="owner/repo" \
  python3 scripts/stamp_commit_meta.py release_assets
```

### Verification fails: "filename missing _g<commit> suffix"

**Cause:** Files not renamed after building

**Fix:**
```bash
COMMIT=$(git rev-parse --short=12 HEAD)
cd release_assets
for f in *.pdf *.zip; do
  [ -f "$f" ] || continue
  base="${f%.*}"
  ext="${f##*.}"
  mv "$f" "${base}_g${COMMIT}.${ext}"
done
```

### Verification fails: "commit does not match expected"

**Cause:** Metadata commit differs from expected commit

**Fix:** Rebuild with correct commit:
```bash
git checkout <correct-commit>
ALLOW_DIRTY=1 make docs_package_local
```

### PDFs inside ZIPs don't have suffix

**This is expected behavior:**
- ZIP archive names have commit suffix
- Files inside ZIPs retain original names
- Metadata inside PDFs has correct commit

```
✅ Appendix_C_I2S_Integration_ge05247101a22.zip
   └─ Appendix_C_I2S_Integration/
      ├─ QR_Index.pdf (metadata: e05247101a22)
      └─ Appendix_C_I2S_Index.pdf (metadata: e05247101a22)
```

---

## Best Practices

1. **Always verify before release**
   - CI automatically verifies in docs-release.yml
   - Blocks upload if verification fails

2. **Use consistent commit format**
   - Always 12 characters
   - Lowercase hexadecimal
   - Prefix with `g`

3. **Test locally before pushing**
   ```bash
   ALLOW_DIRTY=1 make docs_package_local
   python3 scripts/verify_pdf_meta.py --root release_assets --require-suffix
   ```

4. **Check verification output**
   - Read all `[FAIL]` messages
   - Fix issues before retrying
   - Verify `[OK]` for all files

---

## Integration with Other Systems

### Release Notes Enricher

Verification happens **before** the enricher runs:

```
Build → Stamp → Rename → Verify → Upload → Enrich Notes
```

If verification fails, upload never happens.

### README Auto-Updater

The README updater shows commit-suffixed filenames:

```markdown
| dist_ge05247101a22.zip | 105M |
| Appendix_C_I2S_Integration_ge05247101a22.zip | 92K |
```

### Local Build System

Local builds can verify before committing:

```bash
make docs_package_local  # Stamps + renames
make docs_latest_block   # Shows what will be in README
```

---

## Version History

- **v2.0.9+SB-appendix-demo** - Initial verification system
  - Metadata verification in docs-build
  - Metadata + suffix verification in docs-release
  - Automated stamping and renaming in CI
