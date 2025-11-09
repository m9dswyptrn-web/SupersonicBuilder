# SuperSonic Manual v2.5.0 - Release Workflow Guide

## 🚀 Complete Release Process

### 1. Build All PDFs
```bash
make release_local
```

**What happens:**
- Rebuilds both manual themes (dark + light)
- Regenerates parts lists (dark + light)  
- Copies all PDFs to `dist/` directory
- Generates SHA256 checksums → `dist/SHA256SUMS.txt`

**Output:**
```
dist/
├── supersonic_manual_dark.pdf    (65 MB)
├── supersonic_manual_light.pdf   (65 MB)
├── parts_tools_dark.pdf          (2.4 KB)
├── parts_tools_light.pdf         (2.4 KB)
└── SHA256SUMS.txt                (checksums)
```

---

### 2. Generate Release Notes
```bash
make release_notes
```

**What happens:**
- Scans all PDFs in `dist/`
- Generates SHA256 for each file
- Creates Markdown with clickable links
- Outputs `dist/RELEASE_NOTES.md`

**Output:**
```markdown
# 🚀 SonicBuilder Auto-Generated Release Notes

- **[parts_tools_dark.pdf](./parts_tools_dark.pdf)**  \`SHA256: 6bcde206...\`
- **[parts_tools_light.pdf](./parts_tools_light.pdf)**  \`SHA256: 9cdb7261...\`
- **[supersonic_manual_dark.pdf](./supersonic_manual_dark.pdf)**  \`SHA256: f5080108...\`
- **[supersonic_manual_light.pdf](./supersonic_manual_light.pdf)**  \`SHA256: 09ca01f3...\`
```

---

### 3. Complete Workflow (One Command)
```bash
make release_local && make release_notes
```

**Time:** ~35 seconds  
**Result:** All PDFs + SHA256SUMS.txt + RELEASE_NOTES.md in `dist/`

---

## 📦 Release Package Contents

### dist/ Directory Structure
```
dist/
├── RELEASE_NOTES.md              ← Auto-generated with links + SHA256
├── SHA256SUMS.txt                ← Standard checksums file
├── supersonic_manual_dark.pdf    ← 108-page manual (screen-optimized)
├── supersonic_manual_light.pdf   ← 108-page manual (print-optimized)
├── parts_tools_dark.pdf          ← Parts list (screen-optimized)
└── parts_tools_light.pdf         ← Parts list (print-optimized)
```

---

## 🌐 GitHub Release Workflow

### Option 1: Manual GitHub Release

1. **Create release on GitHub:**
   ```bash
   git tag v2.5.0
   git push origin v2.5.0
   ```

2. **Go to GitHub Releases → Draft new release**

3. **Upload files:**
   - Drag & drop all files from `dist/` folder
   - Or use GitHub's file picker

4. **Copy/paste RELEASE_NOTES.md:**
   - Open `dist/RELEASE_NOTES.md`
   - Copy entire contents
   - Paste into release description

5. **Publish release**

### Option 2: Automated Release (Future Enhancement)
- GitHub Actions workflow could automate this
- Trigger on git tag push
- Build → Generate notes → Create release
- Upload all PDFs automatically

---

## ✅ Verification Steps

### Verify Checksums
```bash
cd dist
sha256sum -c SHA256SUMS.txt
```

**Expected output:**
```
supersonic_manual_dark.pdf: OK
supersonic_manual_light.pdf: OK
parts_tools_dark.pdf: OK
parts_tools_light.pdf: OK
```

### Verify Release Notes
```bash
cat dist/RELEASE_NOTES.md
```

**Should show:**
- Markdown heading
- 4 PDF links
- SHA256 for each file

---

## 📊 Release Checklist

Before publishing:

- [ ] Run `make release_local`
- [ ] Run `make release_notes`
- [ ] Verify all 4 PDFs exist in `dist/`
- [ ] Check `SHA256SUMS.txt` has 4 entries
- [ ] Verify `RELEASE_NOTES.md` has 4 links
- [ ] Test checksums: `sha256sum -c SHA256SUMS.txt`
- [ ] Review PDF content (spot check)
- [ ] Tag version in git
- [ ] Create GitHub release
- [ ] Upload all files from `dist/`
- [ ] Copy RELEASE_NOTES.md to release description

---

## 🎯 Quick Reference

```bash
# Full release workflow
make release_local && make release_notes

# Verify checksums
cd dist && sha256sum -c SHA256SUMS.txt

# View release notes
cat dist/RELEASE_NOTES.md

# Clean dist before release (optional)
rm -rf dist/* && make release_local && make release_notes
```

---

## 📝 Release Notes Format

### Auto-Generated Format
```markdown
# 🚀 SonicBuilder Auto-Generated Release Notes

- **[filename.pdf](./filename.pdf)**  \`SHA256: checksum...\`
```

### GitHub Renders As:
- **Clickable links** to download PDFs
- **Inline code** formatting for SHA256
- **Professional appearance** in release description

---

## 🔧 Troubleshooting

### Missing PDFs in RELEASE_NOTES.md
```bash
# Make sure release_local ran first
make release_local
make release_notes
```

### Wrong SHA256 checksums
```bash
# Rebuild everything
make release_local
make release_notes
```

### Empty RELEASE_NOTES.md
```bash
# Check if PDFs exist
ls -lh dist/*.pdf

# Regenerate
make release_notes
```

---

## 🚀 Advanced Usage

### Custom Release Notes Header
Edit `scripts/gen_release_notes.py`:
```python
lines = ["# 🚀 SuperSonic Manual v2.5.0 Release", ""]
```

### Include Additional Files
```bash
# Add README to release
cp README.md dist/

# Add changelog
cp CHANGELOG.md dist/

# Regenerate notes (includes all files now)
make release_notes
```

### Automated Versioning
```bash
# Tag and release in one step
VERSION=v2.5.0
git tag $VERSION
make release_local && make release_notes
git push origin $VERSION
```

---

**SuperSonic Manual v2.5.0** - Professional release automation with auto-generated notes  
**Build:** ~35s total | **Output:** 6 files in dist/ | **SHA256:** Verified integrity
