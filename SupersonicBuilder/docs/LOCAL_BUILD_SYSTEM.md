# Local Build & Release System

Complete local documentation build/release system with commit metadata stamping, git guards, and README auto-updating.

## Quick Reference

```bash
# Build docs locally (same as CI)
make docs_build_local

# Full release package (build + stamp + rename + zip + checksums)
make docs_release_local

# Preview README "Latest Docs" block
make docs_latest_block
```

---

## Features

### 1. Commit Metadata Stamping

All PDFs are automatically stamped with build metadata:

```python
/Version: v2.0.9+SB-appendix-demo
/Commit: e05247101a22
/Repository: owner/repo
/BuildDate: 2025-10-28T22:40:47Z
/Producer: SonicBuilder
/Creator: SonicBuilder PDF Pipeline
```

**Inspect metadata:**
```bash
python3 -c "from pypdf import PdfReader; print(PdfReader('file.pdf').metadata)"
```

### 2. Commit-Aware File Naming

All release artifacts include the short commit hash:

```
Before:                          After:
dist.zip                    →    dist_ge05247101a22.zip
supersonic_manual_dark.pdf  →    supersonic_manual_dark_ge05247101a22.pdf
```

This ensures every release artifact is uniquely identifiable and traceable.

### 3. Git Clean Guard

Prevents accidental dirty builds:

```bash
# ✅ Clean repo - builds normally
make docs_release_local

# ❌ Dirty repo (uncommitted changes) - blocks build
make docs_release_local
# Error: Working tree has uncommitted changes

# ⚠️ Override guard explicitly
ALLOW_DIRTY=1 make docs_release_local
```

### 4. README Auto-Updater

On each GitHub release, the `readme-latest-docs` workflow automatically updates your README with:

```markdown
<!-- SB_LATEST_DOCS_BEGIN -->
### Latest documentation bundle

**Release:** `v2.0.9+SB-appendix-demo`
**Commit:** [ge05247101a22](https://github.com/owner/repo/commit/e05247101a22...)

**View release:** https://github.com/owner/repo/releases/tag/v2.0.9+SB-appendix-demo

| File | Size |
|---|---:|
| dist_ge05247101a22.zip | 105M |
| Appendix_C_I2S_Integration_ge05247101a22.zip | 92K |
<!-- SB_LATEST_DOCS_END -->
```

---

## Make Targets

### `docs_build_local`

Builds documentation locally (same steps as CI):

```bash
make docs_build_local
```

**What it does:**
1. Detects VERSION (git tag > VERSION file > default)
2. Installs Python dependencies
3. Runs `make docs_ci` (your project's build entrypoint)
4. Outputs to `release_assets/`

### `docs_package_local`

Packages artifacts with commit metadata:

```bash
make docs_package_local
```

**What it does:**
1. Runs `docs_build_local`
2. Stamps all PDFs with commit metadata
3. Renames files to include commit hash (`_g{COMMIT}`)
4. Zips folders with commit hash
5. Generates `SHA256SUMS.txt`

### `docs_release_local`

Complete release build with safety checks:

```bash
make docs_release_local
```

**What it does:**
1. Runs `git_guard` (blocks if dirty repo)
2. Runs `docs_package_local`
3. Shows total package size

**Override dirty check:**
```bash
ALLOW_DIRTY=1 make docs_release_local
```

### `docs_latest_block`

Preview the README "Latest Docs" block:

```bash
make docs_latest_block
```

Outputs the markdown block that will be inserted into README.md by the GitHub workflow.

### `git_guard`

Check working tree cleanliness:

```bash
make git_guard              # Must be clean
ALLOW_DIRTY=1 make git_guard  # Allow dirty
```

---

## Environment Variables

The system automatically detects these values:

| Variable | Source | Fallback |
|----------|--------|----------|
| `VERSION` | git tag → VERSION file | `v2.0.9+SB-appendix-demo` |
| `COMMIT` | `git rev-parse --short=12 HEAD` | `unknown` |
| `BUILD_DATE` | `date -u +%Y-%m-%dT%H:%M:%SZ` | - |
| `REPO_URL` | `git config remote.origin.url` | `unknown` |

**Manual override:**
```bash
VERSION=v3.0.0 COMMIT=abc123 make docs_release_local
```

---

## GitHub Workflow Integration

### `readme-latest-docs.yml`

Automatically updates README on every release:

**Trigger:** Release published  
**Permissions:** `contents: write`  
**Action:** Replaces `<!-- SB_LATEST_DOCS_BEGIN -->` ... `<!-- SB_LATEST_DOCS_END -->` block

**Setup:**
1. Add placeholder to README.md:
   ```markdown
   <!-- SB_LATEST_DOCS_BEGIN -->
   <!-- SB_LATEST_DOCS_END -->
   ```

2. Workflow handles the rest automatically on release

**Features:**
- Resolves commit SHA from git tag (handles annotated tags)
- Generates human-readable file sizes
- Creates download links with verified checksums
- Commits update automatically

---

## File Structure

```
scripts/
  stamp_commit_meta.py       # PDF metadata stamper

.github/workflows/
  readme-latest-docs.yml     # README auto-updater
  docs-build.yml             # CI build
  docs-release.yml           # CI release
  docs-release-notes-enricher.yml  # Release notes enricher

Makefile                     # Enhanced with local targets
  docs_build_local
  docs_package_local
  docs_release_local
  docs_latest_block
  git_guard

release_assets/              # Local build output
  dist_g{COMMIT}.zip
  Appendix_C_I2S_Integration_g{COMMIT}.zip
  SHA256SUMS.txt
```

---

## Troubleshooting

### Git lock errors

```bash
# Clear stale git lock
rm -f .git/index.lock
```

### Build fails at docs_ci

Check that `MAKEFRAG.docs` exists and has proper tabs (not spaces).

### PDFs not stamped

Ensure `pypdf` is installed:
```bash
pip install pypdf
```

### Checksums missing

Make sure `shasum` or `sha256sum` is available:
```bash
which shasum  # macOS/BSD
which sha256sum  # Linux
```

---

## Best Practices

1. **Always use git tags for releases**
   ```bash
   git tag v2.0.10
   git push --tags
   ```

2. **Commit before building**
   - Clean working tree ensures accurate commit hashes
   - Use `ALLOW_DIRTY=1` only for testing

3. **Verify PDF metadata**
   ```bash
   python3 -c "from pypdf import PdfReader; print(PdfReader('file.pdf').metadata)"
   ```

4. **Check SHA256 before distribution**
   ```bash
   cd release_assets
   shasum -a 256 -c SHA256SUMS.txt
   ```

---

## CI/CD Integration

The local system mirrors the CI/CD pipeline:

| Local | CI/CD | Purpose |
|-------|-------|---------|
| `docs_build_local` | `docs-build.yml` | Build docs |
| `docs_release_local` | `docs-release.yml` | Package & publish |
| `docs_latest_block` | `readme-latest-docs.yml` | Update README |

**Workflow:**
```
Local Dev              →  GitHub CI/CD
─────────────────────────────────────────
make docs_build_local  →  push to main (docs-build.yml)
make docs_release_local →  git tag v* (docs-release.yml)
make docs_latest_block  →  release published (readme-latest-docs.yml)
```

---

## Examples

### Full Local Release

```bash
# 1. Make changes
vim manual/01-Systems/Audio/speakers.md

# 2. Commit
git add -A
git commit -m "docs: update speaker wiring"

# 3. Build & package
make docs_release_local

# 4. Inspect
ls -lah release_assets
cat release_assets/SHA256SUMS.txt

# 5. Tag & push
git tag v2.0.10
git push origin v2.0.10
```

### Testing Without Git Guard

```bash
# Quick iteration during development
ALLOW_DIRTY=1 make docs_package_local
```

### Preview README Block

```bash
# See what will be added to README
make docs_latest_block

# Copy to README manually (or let workflow do it)
make docs_latest_block >> README.md
```

---

## Version History

- **v2.0.9+SB-appendix-demo** - Initial release with commit stamping system
