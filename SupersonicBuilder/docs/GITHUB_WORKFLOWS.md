# SonicBuilder GitHub Workflows

## Overview

The SonicBuilder project uses GitHub Actions for automated builds, releases, and Certificate of Authenticity (CoA) generation.

## Workflow Files

### Core Workflows

#### 1. `repo-url-setup.yml` - Reusable URL Setup
**Purpose:** Provides `SB_REPO_URL` to other workflows

**Outputs:**
- `SB_REPO_URL` - Repository URL (GitHub or Replit fallback)

**Usage in other workflows:**
```yaml
jobs:
  setup-url:
    uses: ./.github/workflows/repo-url-setup.yml
  
  your-job:
    needs: [setup-url]
    env:
      SB_REPO_URL: ${{ needs.setup-url.outputs.SB_REPO_URL }}
```

**URL Resolution:**
1. If on GitHub: `https://github.com/<owner>/<repo>`
2. Fallback: `https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev`

---

#### 2. `coa-on-release.yml` - Auto-mint CoA
**Trigger:** When a GitHub release is published

**What it does:**
1. Sets up repository URL via `repo-url-setup.yml`
2. Reads version from `VERSION.txt`
3. Generates CoA with auto-incremented serial
4. Commits CoA to repository
5. Uploads PDF to release assets
6. Comments on release with CoA details

**Environment:**
- `SB_REPO_URL` - Auto-detected repository URL
- CoA QR code points to `$SB_REPO_URL`

**Example:**
```bash
# Create a release on GitHub
git tag v2.5.1
git push origin v2.5.1

# Workflow automatically:
# - Generates CoA #0006
# - QR: https://github.com/YourUser/sonicbuilder
# - Uploads SonicBuilder_CoA_#0006.pdf
```

---

#### 3. `release.yml` - Main Release Workflow
**Trigger:** Push tags starting with `v*` (e.g., `v2.5.0`)

**What it does:**
1. Runs full test suite
2. Builds PDF manual
3. Creates GitHub release
4. Uploads release artifacts

**Artifacts:**
- `SonicBuilder_Manual_v*.pdf`
- `Pro_Installer_Bundle_v*.zip`
- Version metadata

---

#### 4. `sonicbuilder-ci.yml` - Continuous Integration
**Trigger:** Push to main/master, pull requests

**What it does:**
1. Validates YAML configuration
2. Builds PDF manual
3. Runs tests
4. Checks for errors

**Status:** ✅ Must pass before merging

---

#### 5. `qr-url-fallback.yml` - Simple QR URL Setup
**Trigger:** Manual (`workflow_dispatch`) or called by other workflows

**Purpose:** Legacy fallback for setting environment variables

**Note:** Use `repo-url-setup.yml` instead for new workflows

---

### Support Workflows

#### `project-auto.yml` - Project Automation
Auto-manages GitHub project boards and issues

#### `version-badge.yml` - Version Badge
Updates README badges with current version

---

## Environment Variables

### `SB_REPO_URL`
**Source:** `repo-url-setup.yml` workflow
**Format:** `https://github.com/<owner>/<repo>` or Replit URL
**Used by:** CoA generator, PDF metadata, QR codes

### Setting Custom URL
```yaml
env:
  SB_REPO_URL: "https://sonicbuilder.io"
```

---

## CoA Generation

### Automatic (via GitHub Actions)
```yaml
# Triggered on release
on:
  release:
    types: [published]

# Uses SB_REPO_URL automatically
env:
  SB_REPO_URL: ${{ needs.setup-url.outputs.SB_REPO_URL }}
```

### Manual (local development)
```bash
cd tools/CoA_Generator

# Auto-detect URL (Replit fallback)
python generate_coa.py --auto-increment --version v2.5.0

# Override URL
SB_REPO_URL="https://github.com/user/repo" \
  python generate_coa.py --auto-increment

# Explicit QR URL
python generate_coa.py --auto-increment \
  --qr "https://custom.url/build/0042"
```

---

## URL Resolution Priority

1. **CLI `--qr` flag** (highest priority)
2. **Environment:** `SB_REPO_URL`
3. **Environment:** `GITHUB_REPOSITORY` → `https://github.com/<slug>`
4. **Replit Domain:** Hardcoded fallback
5. **Default:** `https://example.com/sonicbuilder`

---

## Integration Examples

### Add SB_REPO_URL to Existing Workflow

**Before:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make build
```

**After:**
```yaml
jobs:
  setup-url:
    uses: ./.github/workflows/repo-url-setup.yml
  
  build:
    needs: [setup-url]
    runs-on: ubuntu-latest
    env:
      SB_REPO_URL: ${{ needs.setup-url.outputs.SB_REPO_URL }}
    steps:
      - run: make build
```

---

## Development vs Production

### Development (Replit)
```bash
# SB_REPO_URL auto-detected
python generate_coa.py --auto-increment
# QR: https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev
```

### Production (GitHub)
```bash
# GitHub Actions workflow
# SB_REPO_URL: https://github.com/user/sonicbuilder
```

### Custom Domain
```yaml
env:
  SB_REPO_URL: "https://sonicbuilder.io"
```

---

## Troubleshooting

### QR Code Shows Replit URL on GitHub
**Problem:** CoA uses Replit domain instead of GitHub  
**Solution:** Ensure workflow includes `setup-url` job:
```yaml
jobs:
  setup-url:
    uses: ./.github/workflows/repo-url-setup.yml
```

### CoA Generation Fails
**Problem:** Missing Python dependencies  
**Solution:** Add install step:
```yaml
- run: pip install reportlab qrcode pillow
```

### Wrong Version Number
**Problem:** CoA shows wrong version  
**Solution:** Update `VERSION.txt` before release:
```bash
echo "version: v2.5.1" > VERSION.txt
git commit -m "chore: bump version to v2.5.1"
git tag v2.5.1
git push origin v2.5.1
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────┐
│ GitHub Release Published                             │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────▼─────────────┐
    │  setup-url (reusable)      │
    │  - Detect GitHub repo      │
    │  - Set SB_REPO_URL         │
    └─────────────┬──────────────┘
                  │ outputs.SB_REPO_URL
    ┌─────────────▼──────────────┐
    │  mint-coa                   │
    │  - Read VERSION.txt         │
    │  - Generate CoA PDF         │
    │  - Auto-increment serial    │
    │  - Commit to repo           │
    │  - Upload to release        │
    └─────────────┬───────────────┘
                  │
    ┌─────────────▼───────────────┐
    │  Release Assets              │
    │  - SonicBuilder_CoA_#0006.pdf│
    │  - QR: github.com/user/repo  │
    └──────────────────────────────┘
```

---

## Current Replit Domain

**Domain:** `08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev`  
**Slug:** `workspace`  
**Usage:** Development fallback for QR codes

---

## Migration Checklist

- [x] Install `repo-url-setup.yml` workflow
- [x] Update `coa-on-release.yml` to use setup-url
- [x] Update `config/repo_urls.json` with Replit domain
- [ ] Push to GitHub repository
- [ ] Create test release to verify CoA generation
- [ ] Verify QR code points to GitHub URL
- [ ] Update documentation with GitHub URL

---

**See also:**
- `docs/USING_SB_REPO_URL.md` - Usage guide
- `docs/README_SB_REPO_URL_PATCH.md` - Patch notes
- `tools/CoA_Generator/README_QR_PATCH.md` - QR configuration
