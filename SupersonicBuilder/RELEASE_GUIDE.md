# 🚀 Release Automation Guide

Complete guide for releasing Supersonic v4 Ultimate Edition.

---

## 📦 Release Automation System

Your project now includes a complete release automation system:

### Installed Tools

| Tool | Purpose | Location |
|------|---------|----------|
| **Version Bumper** | Auto-increment versions | `tools/simple_bump.py` |
| **Changelog Generator** | Generate from git commits | `tools/update_changelog.py` |
| **Release Shipper** | Tag, push, create GitHub release | `tools/ship_release.py` |
| **Summary Generator** | Create release summaries | `tools/release_summary.py` |

### Files Created

- ✅ `VERSION` - Current version (v1.0.0)
- ✅ `CHANGELOG.md` - Auto-generated changelog
- ✅ `.github/workflows/release.yml` - Automated release workflow (ready to commit)

---

## 🎯 Quick Start: Your First Release

### Option 1: Automated Release (Simplest)

```bash
# 1. Prepare: Commit all pending changes
git add -A
git commit -m "feat: add health scan system, fix compile errors, activate CI"

# 2. Push to main
git push -u origin main

# 3. Create and push tag (triggers GitHub Actions)
git tag -a v1.0.0 -m "Release v1.0.0 – Supersonic v4 Ultimate Edition"
git push origin v1.0.0
```

GitHub Actions will automatically:
- Generate CHANGELOG from commits
- Create GitHub Release
- Add release notes

### Option 2: Manual Release (Full Control)

```bash
# 1. Update changelog
REPO_URL=https://github.com/ChristopherElgin/SonicBuilderSupersonic \
  python3 tools/update_changelog.py --version v1.0.0

# 2. Review changelog
cat CHANGELOG.md

# 3. Commit everything
git add -A
git commit -m "build: prep release v1.0.0"

# 4. Push main
git push -u origin main

# 5. Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 6. Create GitHub release (requires GitHub CLI)
gh release create v1.0.0 \
  --title "Supersonic v4 Ultimate Edition – v1.0.0" \
  --notes-file CHANGELOG.md
```

### Option 3: Using ship_release.py

```bash
# All-in-one release script
python3 tools/ship_release.py --version v1.0.0

# Skip health-apply step
python3 tools/ship_release.py --version v1.0.0 --skip_health_apply
```

---

## 📈 Version Bumping

### Automatic Bumping

```bash
# Bump patch (v1.0.0 → v1.0.1)
python3 tools/simple_bump.py patch

# Bump minor (v1.0.0 → v1.1.0)
python3 tools/simple_bump.py minor

# Bump major (v1.0.0 → v2.0.0)
python3 tools/simple_bump.py major
```

### Manual VERSION Update

```bash
# Edit VERSION file directly
echo "v1.0.1" > VERSION
```

---

## 📝 Changelog Management

### Auto-Generate from Git Commits

The changelog generator uses **Conventional Commits** format:

```bash
# Generate changelog for current version
REPO_URL=https://github.com/ChristopherElgin/SonicBuilderSupersonic \
  python3 tools/update_changelog.py

# Generate for specific version
REPO_URL=https://github.com/ChristopherElgin/SonicBuilderSupersonic \
  python3 tools/update_changelog.py --version v1.0.1

# Specify range
python3 tools/update_changelog.py --version v1.0.1 --from-tag v1.0.0
```

### Conventional Commit Format

Your commits should follow this pattern:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`

**Examples**:
```bash
git commit -m "feat: add health scan system"
git commit -m "fix(docs): correct badge URLs"
git commit -m "chore: bump version to v1.0.1"
git commit -m "feat!: redesign API (BREAKING CHANGE)"
```

---

## 🔄 Complete Release Workflow

### Patch Release (v1.0.0 → v1.0.1)

```bash
# 1. Bump version
python3 tools/simple_bump.py patch
VERSION=$(cat VERSION)

# 2. Generate changelog
REPO_URL=https://github.com/ChristopherElgin/SonicBuilderSupersonic \
  python3 tools/update_changelog.py --version $VERSION

# 3. Commit
git add VERSION CHANGELOG.md
git commit -m "chore: prepare release $VERSION"
git push

# 4. Tag and release
git tag -a $VERSION -m "Release $VERSION"
git push origin $VERSION
```

### Minor Release (v1.0.0 → v1.1.0)

```bash
# 1. Bump version
python3 tools/simple_bump.py minor
VERSION=$(cat VERSION)

# 2-4: Same as patch release...
```

### Major Release (v1.0.0 → v2.0.0)

```bash
# 1. Bump version
python3 tools/simple_bump.py major
VERSION=$(cat VERSION)

# 2-4: Same as patch release...
```

---

## 🎬 GitHub Actions Workflow

The `.github/workflows/release.yml` workflow triggers on:
- **Tag push**: `git push origin v*.*.*`
- **Manual dispatch**: From GitHub Actions UI

### What it does:
1. ✅ Checks out full git history
2. ✅ Generates/updates CHANGELOG.md
3. ✅ Commits changelog back to main
4. ✅ Creates GitHub Release with notes

### Enable it:

```bash
# Commit the workflow
git add .github/workflows/release.yml
git commit -m "ci: add automated release workflow"
git push
```

---

## 🏷️ Tag Management

### List Tags

```bash
# All tags
git tag

# Tags sorted by date
git tag --sort=-creatordate

# Tags with messages
git tag -n
```

### Delete Tag

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin :refs/tags/v1.0.0
```

### Retag

```bash
# Delete old tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Create new tag
git tag -a v1.0.0 -m "Release v1.0.0 (updated)"
git push origin v1.0.0
```

---

## 🎯 Example: Full v1.0.0 Release

```bash
# 1. Ensure you're on main with latest changes
git checkout main
git pull origin main

# 2. Commit all pending work
git add -A
git commit -m "feat: complete health scan system integration"

# 3. Set version
echo "v1.0.0" > VERSION

# 4. Generate changelog
REPO_URL=https://github.com/ChristopherElgin/SonicBuilderSupersonic \
  python3 tools/update_changelog.py --version v1.0.0

# 5. Review
cat CHANGELOG.md | head -50

# 6. Commit release prep
git add VERSION CHANGELOG.md
git commit -m "build: prepare release v1.0.0"

# 7. Push
git push origin main

# 8. Tag
git tag -a v1.0.0 -m "Release v1.0.0 – Supersonic v4 Ultimate Edition

First production release featuring:
- Enterprise health scan system
- Zero compile errors
- CI/CD integration
- Automated deployment
- 5 professional voice packs"

# 9. Push tag (triggers GitHub Actions)
git push origin v1.0.0

# 10. Check GitHub Actions
# Visit: https://github.com/ChristopherElgin/SonicBuilderSupersonic/actions

# 11. Verify release
# Visit: https://github.com/ChristopherElgin/SonicBuilderSupersonic/releases
```

---

## 🔍 Troubleshooting

### "Permission denied" on git push

```bash
# Check remote URL
git remote -v

# Should be HTTPS or SSH
git remote set-url origin https://github.com/ChristopherElgin/SonicBuilderSupersonic.git
```

### Changelog not generating

```bash
# Check git history
git log --oneline | head -10

# Ensure REPO_URL is set
export REPO_URL=https://github.com/ChristopherElgin/SonicBuilderSupersonic
python3 tools/update_changelog.py --version v1.0.0
```

### GitHub Actions not triggering

```bash
# 1. Ensure workflow file is committed
git add .github/workflows/release.yml
git commit -m "ci: add release workflow"
git push

# 2. Push tag AFTER workflow is on main
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Release already exists

```bash
# Delete GitHub release first (via web UI or gh CLI)
gh release delete v1.0.0

# Then retag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 📚 Reference

### Version File (VERSION)

```
v1.0.0
```

Simple text file with semantic version.

### Changelog Structure

```markdown
# Changelog

## v1.0.1 — 2025-11-04 · [Compare](...)

### Features
- **health**: add scan system (a1b2c3d)
- **ci**: activate workflows (e4f5g6h)

### Bug Fixes
- **docs**: fix f-string error (i7j8k9l)

### Chores
- bump version to v1.0.1 (m0n1o2p)
```

---

## ✅ Ready to Release!

Everything is set up. Choose your release method above and ship it! 🚀

**Current Status**:
- ✅ Health scan: 0 compile errors
- ✅ CI workflow: Activated
- ✅ Pages workflow: Active
- ✅ All 4 runtime workflows: Running
- ✅ Release automation: Installed

**Recommended First Release**:
```bash
python3 tools/ship_release.py --version v1.0.0
```

Good luck! 🎉
