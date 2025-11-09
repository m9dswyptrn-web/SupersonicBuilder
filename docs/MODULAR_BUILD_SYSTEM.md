# Modular Build System

Complete separation of SonicBuilder automation from your project's main Makefile.

## Overview

The modular build system uses `make/sonicbuilder.mk` to provide all automation targets while keeping your main `Makefile` clean and focused on project-specific tasks.

## Quick Start

The main Makefile includes the modular system with:
```makefile
-include make/sonicbuilder.mk
```

This single line gives you access to all SonicBuilder targets without cluttering your main Makefile.

---

## Available Targets

### 🏗️ Build & Package

```bash
# Simple local build
make docs_build_local

# Package with zips and checksums
make docs_package_local

# Quick non-strict release
make docs_release_local
```

### 🔒 Strict CI-Parity Release

```bash
# Exact CI behavior (git guard + stamp + rename + verify)
make docs_release_local_strict

# Override git guard if needed
ALLOW_DIRTY=1 make docs_release_local_strict
```

**What it does:**
1. ✅ Git clean guard (blocks if uncommitted changes unless `ALLOW_DIRTY=1`)
2. 📦 Build docs
3. 🏷️ Stamp PDF metadata (version, commit, date, repo)
4. 📝 Rename files: `*_g{COMMIT}.{ext}`
5. 🗜️ Auto-compress oversize artifacts
6. ✂️ Auto-split files >200MB
7. 🔍 Preflight check (blocks if >200MB)
8. ✔️ Verify PDF metadata + suffix

---

## 📊 Preview Targets

### Assets Table

```bash
make assets_table_preview
```

**Output:**
```markdown
<!-- SB_ASSETS_TABLE_BEGIN -->
### Download assets (verified)

| File | Size | SHA256 |
|---|---:|---|
| manual_dark_ge05247101a22.pdf | 65.50 MB | `abc123def456…` |
| appendix_ge05247101a22.pdf | 12.30 MB | `789abc012def…` |
<!-- SB_ASSETS_TABLE_END -->
```

### Parts Help (Split Bundles)

```bash
make parts_help_preview
```

**Output:** Reassembly instructions (only if `.zip.partNN` files exist)

### Complete Release Notes

```bash
# Preview to stdout
make release_notes_preview

# Write to file
make release_notes_preview_md  # → RELEASE_NOTES_PREVIEW.md
```

**Includes:**
- Assets table (always)
- Parts help (if split files exist)

### README Latest Docs Block

```bash
make readme_latest_preview
```

**Output:**
```markdown
<!-- SB_LATEST_DOCS_BEGIN -->
### Latest documentation bundle

**Release:** `v2.0.10`
**Commit:** [ge05247101a22](https://github.com/owner/repo/commit/e05247101a22...)

**View release:** https://github.com/owner/repo/releases/tag/v2.0.10

| File | Size |
|---|---:|
| manual_dark_ge05247101a22.pdf | 65.50 MB |
| appendix_ge05247101a22.pdf | 12.30 MB |
<!-- SB_LATEST_DOCS_END -->
```

### Badge Status

```bash
make badge_preview
```

Shows current `.status/docs-release.json` content.

---

## 🎯 Large Artifact Optimization

```bash
make artifacts_optimize_local
```

**Three-stage pipeline:**
1. **Auto-compress** - Recompress with `zip -9`
2. **Auto-split** - Split >200MB → ~180MB parts
3. **Preflight** - Verify all non-PDF <200MB

**Note:** This target is automatically called by `docs_release_local_strict`

---

## 🔐 Git Guard

All strict targets enforce a clean working tree:

```bash
# Will fail if uncommitted changes
make docs_release_local_strict

# Override for testing
ALLOW_DIRTY=1 make docs_release_local_strict
```

---

## 📋 Variables

The modular makefile automatically detects:

| Variable | Detection Order | Fallback |
|----------|----------------|----------|
| `VERSION` | git tag → VERSION file | `v2.0.9+SB-appendix-demo` |
| `COMMIT` | `git rev-parse --short=12` | `unknown` |
| `BUILD_DATE` | `date -u +%Y-%m-%dT%H:%M:%SZ` | - |
| `REPO_URL` | `git config remote.origin.url` | `unknown` |

### Override Variables

```bash
VERSION=v3.0.0 make docs_build_local
PYTHON=python3.11 make docs_build_local
OUTPUT_DIR=artifacts make docs_package_local
```

---

## 📁 File Structure

```
make/
  sonicbuilder.mk          # All SonicBuilder targets

release_assets/            # Default output directory
  *.pdf                    # Generated PDFs
  *.zip                    # Compressed bundles
  *.zip.partNN             # Split parts (if needed)
  *.sha256                 # Checksums
  COMPRESSION_MANIFEST.txt # Compression results
  SPLIT_MANIFEST.txt       # Split file info

.status/
  docs-release.json        # Badge status
```

---

## 🔄 Workflow Integration

### Local → CI Parity

**Local (strict):**
```bash
make docs_release_local_strict
```

**CI (docs-release.yml):**
```yaml
- name: Build docs
  run: make docs_ci VERSION="${VERSION}"
  
- name: Stamp and rename
  run: python3 scripts/stamp_commit_meta.py release_assets
  
- name: Auto-compress
  run: python3 scripts/auto_compress.py
  
- name: Auto-split
  run: python3 scripts/split_large_artifacts.py
  
- name: Preflight
  run: python3 scripts/preflight_size_check.py release_assets
```

**Result:** Local builds mirror CI exactly

---

## 🎨 Workflow Examples

### Example 1: Quick Local Test

```bash
# Build and package (no verification)
ALLOW_DIRTY=1 make docs_package_local

# Preview what users will see
make readme_latest_preview
```

### Example 2: Pre-Release Verification

```bash
# Commit all changes first
git add .
git commit -m "Ready for release"

# Full CI-parity build
make docs_release_local_strict

# Preview release notes
make release_notes_preview_md
cat RELEASE_NOTES_PREVIEW.md

# Preview README block
make readme_latest_preview > README_BLOCK.md
```

### Example 3: Test Artifact Management

```bash
# Build with oversized file
ALLOW_DIRTY=1 make docs_package_local

# Manually test optimization
python3 scripts/auto_compress.py
python3 scripts/split_large_artifacts.py
python3 scripts/preflight_size_check.py release_assets

# Or use combined target
make artifacts_optimize_local
```

---

## 📚 Integration with Main Makefile

Your project's `Makefile` remains focused on project tasks:

```makefile
PY ?= python

# Include SonicBuilder targets
-include make/sonicbuilder.mk

# Your project-specific targets
.PHONY: build_dark build_light

build_dark:
	$(PY) scripts/builder.py

build_light:
	$(PY) scripts/builder.py --light

# Combine with SonicBuilder
release: build_dark build_light docs_package_local
	@echo "Complete release ready"
```

---

## 🔧 Customization

### Override Python Interpreter

```bash
PYTHON=python3.11 make docs_build_local
```

### Override Output Directory

```bash
OUTPUT_DIR=artifacts make docs_package_local
```

### Custom Split Limits

```bash
SB_SPLIT_LIMIT_MB=250 SB_SPLIT_PART_MB=200 make artifacts_optimize_local
```

---

## 🐛 Troubleshooting

### Target not found

**Issue:** `make: *** No rule to make target 'docs_release_local_strict'`

**Solution:** Verify include line in main Makefile:
```bash
grep "sonicbuilder.mk" Makefile
# Should show: -include make/sonicbuilder.mk
```

### Git guard blocks release

**Issue:** `❌ Working tree has uncommitted changes`

**Solutions:**
```bash
# Option 1: Commit changes
git add .
git commit -m "Ready for release"
make docs_release_local_strict

# Option 2: Override temporarily
ALLOW_DIRTY=1 make docs_release_local_strict
```

### Preview targets show nothing

**Issue:** Empty output from preview targets

**Solution:** Build first:
```bash
ALLOW_DIRTY=1 make docs_package_local
make release_notes_preview
```

### Python import errors

**Issue:** `ModuleNotFoundError: No module named 'reportlab'`

**Solution:** Dependencies are auto-installed, but you can install manually:
```bash
pip install -r requirements.txt
pip install reportlab pypdf pillow qrcode pdf2image
```

---

## 📖 Related Documentation

- **[ARTIFACT_MANAGEMENT_SYSTEM.md](ARTIFACT_MANAGEMENT_SYSTEM.md)** - Compression, splitting, preflight
- **[PDF_VERIFICATION_SYSTEM.md](PDF_VERIFICATION_SYSTEM.md)** - Metadata stamping and verification
- **[LOCAL_BUILD_SYSTEM.md](LOCAL_BUILD_SYSTEM.md)** - Git guards and local workflows

---

## 🎯 Best Practices

1. **Always use strict mode before tagging releases**
   ```bash
   make docs_release_local_strict
   ```

2. **Preview before pushing**
   ```bash
   make release_notes_preview_md
   make readme_latest_preview > /tmp/readme.md
   # Review files before git tag
   ```

3. **Test artifact management with large files**
   ```bash
   make artifacts_optimize_local
   # Check COMPRESSION_MANIFEST.txt
   # Check SPLIT_MANIFEST.txt
   ```

4. **Keep make/ directory in version control**
   ```bash
   git add make/sonicbuilder.mk
   git commit -m "build: update modular build system"
   ```

5. **Don't commit generated artifacts**
   ```gitignore
   # .gitignore
   release_assets/
   RELEASE_NOTES_PREVIEW.md
   README_BLOCK.md
   ```

---

## 🚀 Complete Release Workflow

```bash
# 1. Ensure clean working tree
git status

# 2. Run strict build (CI parity)
make docs_release_local_strict

# 3. Preview release artifacts
make release_notes_preview
make readme_latest_preview

# 4. Verify all looks good
ls -lh release_assets/

# 5. Tag and push
git tag v2.0.11
git push --tags

# 6. CI automatically:
#    - Builds docs
#    - Stamps metadata
#    - Renames with commit
#    - Compresses/splits
#    - Preflight checks
#    - Uploads to release
#    - Enriches notes
#    - Updates README
#    - Updates badge
```

---

## Version History

- **v2.0.10** - Modular build system
  - Separated `make/sonicbuilder.mk`
  - Added `docs_release_local_strict`
  - Enhanced preview targets
  - README block generation
  - Badge status preview
