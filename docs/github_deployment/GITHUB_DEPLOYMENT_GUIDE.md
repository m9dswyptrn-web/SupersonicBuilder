# GitHub Deployment Guide - SonicBuilder Supersonic

## Overview

This guide documents all GitHub deployment options for SonicBuilder Supersonic, including existing deployment scripts and the new GitHub shipper tools integrated from the deployment codes package.

---

## 📦 Available Deployment Scripts

### **Existing Deployment Scripts** (Legacy/Production)

Located in project root:

1. **`deploy_to_github.py`** - Primary GitHub deployment script
2. **`deploy_all_to_github.py`** - Comprehensive deployment with all assets
3. **`ship_to_github_deploy.py`** - Shipping and deployment workflow
4. **`deploy_notify.py`** - Deployment notifications
5. **`deploy_verify.py`** - Post-deployment verification
6. **`scripts/validate_github_setup.py`** - GitHub setup validation

### **New GitHub Shipper Tools** (Enhanced Automation)

Located in `scripts/github/`:

1. **`ship_to_github.py`** - Basic one-and-done GitHub shipper
   - Scaffolding and CI/CD setup
   - Voicepack generation/validation
   - Git init + push + tag
   
2. **`ship_to_github_deluxe.py`** - Deluxe version with full voice toolchain
   - Multi-pack TTS generator
   - Voice pack switcher and preview
   - Smoke testing
   - Comprehensive CI/CD workflows
   
3. **`ship_to_github_supersonic.py`** - Ultimate all-in-one shipper
   - Everything from deluxe PLUS:
   - README badges auto-generation
   - CODEOWNERS, Dependabot config
   - Issue templates
   - .gitignore, .gitattributes, LICENSE (MIT)
   - Docs landing page
   - Makefile helpers (ship/tag/release)
   - GitHub Pages latest alias

---

## 🚀 Quick Start

### Option 1: Use Existing Production Scripts

```bash
# Standard deployment to GitHub
python deploy_to_github.py

# Full deployment with all assets
python deploy_all_to_github.py

# Validate GitHub setup first
python scripts/validate_github_setup.py
```

### Option 2: Use New GitHub Shippers

#### Basic Shipper (Minimal Setup)

```bash
# Create repo via GitHub CLI
python scripts/github/ship_to_github.py \
  --gh-create m9dswyptrn-web/SonicBuilder \
  --version 0.1.0

# Or push to existing repo
python scripts/github/ship_to_github.py \
  --remote https://github.com/<owner>/<repo>.git \
  --version 0.1.0

# Dry run (see what would happen)
python scripts/github/ship_to_github.py \
  --gh-create m9dswyptrn-web/SonicBuilder \
  --version 0.1.0 \
  --dry-run
```

#### Deluxe Shipper (With Voice Packs)

```bash
python scripts/github/ship_to_github_deluxe.py \
  --gh-create m9dswyptrn-web/SonicBuilder \
  --version 0.1.0

# Skip voice pack generation
python scripts/github/ship_to_github_deluxe.py \
  --gh-create m9dswyptrn-web/SonicBuilder \
  --version 0.1.0 \
  --no-voice
```

#### Supersonic Shipper (Everything Included)

```bash
# Full automated setup with all features
python scripts/github/ship_to_github_supersonic.py \
  --gh-create ChristopherElgin/SonicBuilderSupersonic \
  --version 1.0.0

# With custom options
python scripts/github/ship_to_github_supersonic.py \
  --remote https://github.com/ChristopherElgin/SonicBuilderSupersonic.git \
  --version 1.0.0 \
  --no-pages \
  --dry-run
```

---

## 🎯 Command-Line Options

All new shipper scripts support:

| Option | Description |
|--------|-------------|
| `--gh-create OWNER/REPO` | Create new GitHub repo via GitHub CLI |
| `--remote URL` | Push to existing repo URL |
| `--version X.Y.Z` | Tag release as vX.Y.Z |
| `--no-voice` | Skip voicepack generation/smoke test |
| `--skip-install` | Skip `pip install -r requirements.txt` |
| `--no-pages` | Don't add Pages latest-alias step |
| `--dry-run` | Show actions without making changes |

---

## 📋 Prerequisites

### GitHub CLI (for `--gh-create`)

```bash
# Install GitHub CLI
# On Replit, may already be installed
which gh || echo "Install from https://cli.github.com"

# Authenticate (first time only)
gh auth login
```

### Python Dependencies

All required dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key packages:
- `rich>=13.7.0` - Terminal formatting
- `pyttsx3>=2.90` - Text-to-speech for voice packs
- `gunicorn>=21.2` - Production server

---

## 🔄 Workflow Integration

### Makefile Targets

Add these to your `Makefile` for quick deployment:

```makefile
.PHONY: ship tag release

ship:
\tgit add -A && git commit -m "chore: ship $(shell date -u +%F-%H%MZ)" || true
\tgit push origin HEAD:main

# Usage: make tag V=0.2.0
tag:
\t@test -n "$(V)" || (echo "Provide V=x.y.z"; exit 1)
\tgit tag -a v$(V) -m "release v$(V)"
\tgit push origin v$(V)

release:
\t@python3 scripts/ai_console.py || true
```

Usage:
```bash
make ship           # Quick commit and push
make tag V=1.2.3    # Create and push tag
make release        # Interactive release console
```

### GitHub Actions

The shipper scripts automatically add these workflows to `.github/workflows/`:

1. **`release-autopublish.yml`** - Build & Release on tag push
   - Runs on `v*.*.*` tags
   - Voicepack smoke test
   - Package docs
   - Create GitHub Release
   - Optional Pages latest alias

2. **`housekeeping.yml`** - Repository maintenance
   - Manual trigger
   - Cleanup and organization tasks

3. **`status-banner.yml`** - Status badge updates
   - Manual trigger
   - Update project status badges

---

## 🧪 Testing Deployment Scripts

### Dry Run Testing

Always test with `--dry-run` first:

```bash
# Test basic shipper
python scripts/github/ship_to_github.py \
  --gh-create test-owner/test-repo \
  --version 0.0.1 \
  --dry-run

# Test supersonic shipper
python scripts/github/ship_to_github_supersonic.py \
  --remote https://github.com/test/repo.git \
  --version 0.0.1 \
  --dry-run
```

### Validation Checklist

Before deploying:

✅ Run dry-run mode  
✅ Check git status (clean working directory)  
✅ Verify GitHub CLI authentication: `gh auth status`  
✅ Confirm target repository (create or existing)  
✅ Review version number  
✅ Test voicepack generation (if applicable)  
✅ Verify all workflows running: `make supersonic-health`  

---

## 📊 Comparison: Legacy vs New Shippers

| Feature | Legacy Scripts | New Shippers |
|---------|---------------|--------------|
| **Git Setup** | Manual | Automated (git init + push) |
| **Repo Creation** | Manual | Via GitHub CLI (`--gh-create`) |
| **CI/CD Workflows** | Pre-existing | Auto-generated |
| **Voicepack Support** | Via separate scripts | Integrated |
| **Dry Run** | ❌ | ✅ |
| **README Badges** | Manual | Auto-generated (supersonic) |
| **Dependency Management** | Manual | Auto-ensured |
| **Tagging/Releases** | Manual | Automated |
| **Pages Support** | Via workflows | Built-in latest alias |

---

## 🎨 README Badges

The supersonic shipper adds these badges to README.md:

```markdown
[![Build & Release](https://img.shields.io/badge/Build%20%26%20Release-Actions-blue)](#)
![Status](https://img.shields.io/badge/Supersonic-Ready_for_Production-1abc9c)
[Open Last Known Good](https://<you>.github.io/<repo>/latest/)
```

---

## 🛠️ Advanced Usage

### Custom Workflow Configuration

Edit generated workflows in `.github/workflows/` after shipper completes:

```bash
# After running shipper
python scripts/github/ship_to_github_supersonic.py --gh-create ... --version 1.0.0

# Customize workflows
vim .github/workflows/release-autopublish.yml

# Commit changes
git add .github/workflows/
git commit -m "chore: customize workflows"
git push
```

### Multi-Repository Deployment

Deploy to multiple repositories:

```bash
# Deploy to main repo
python scripts/github/ship_to_github_supersonic.py \
  --gh-create ChristopherElgin/SonicBuilderSupersonic \
  --version 1.0.0

# Deploy to mirror/fork
python scripts/github/ship_to_github_supersonic.py \
  --remote https://github.com/mirror/SonicBuilder.git \
  --version 1.0.0 \
  --no-pages
```

### Integration with Existing Infrastructure

The new shippers are designed to coexist with existing deployment scripts:

1. **For new projects**: Use `ship_to_github_supersonic.py` for complete setup
2. **For existing projects**: Use legacy scripts (`deploy_to_github.py`) or run shippers in `--dry-run` to see what they would add
3. **For updates**: Use Makefile targets (`make ship`, `make tag`) for daily work

---

## 🔍 Troubleshooting

### GitHub CLI Not Found

```bash
# Check if gh is installed
which gh

# If not, install from https://cli.github.com
# or use --remote URL instead of --gh-create
```

### Authentication Errors

```bash
# Re-authenticate GitHub CLI
gh auth login

# Verify authentication
gh auth status
```

### Voicepack Generation Fails

```bash
# Skip voicepack generation
python scripts/github/ship_to_github.py \
  --gh-create ... \
  --version 1.0.0 \
  --no-voice
```

### Git Already Initialized

The shippers detect existing `.git/` and skip `git init`. They work with both new and existing repositories.

### Port Conflicts

If deployment server conflicts with existing workflows:

```bash
# Check running processes
ps aux | grep python

# Stop conflicting workflows
# Adjust ports in deployment configuration
```

---

## 📝 Best Practices

1. **Always dry-run first** on new repositories
2. **Version systematically** (semantic versioning: major.minor.patch)
3. **Test voicepacks** before deployment if using them
4. **Review generated workflows** and customize as needed
5. **Use GitHub CLI** for easiest repo creation
6. **Keep deployment logs** for audit trail
7. **Validate health endpoints** after deployment

---

## 🔗 Related Documentation

- `docs/CI_CD_HEALTH_CHECKS.md` - Health check integration
- `DEPLOYMENT_GUIDE.md` - General deployment guide
- `QUICK_DEPLOY.md` - Quick deploy reference
- `EXPORT_GUIDE.md` - Repository export guide
- `HEALTH_CHECK_SUMMARY.md` - Health check summary

---

## 🆘 Support

For issues with:
- **Legacy scripts**: Check existing project documentation
- **New shippers**: Review this guide and run with `--dry-run`
- **GitHub CLI**: Visit https://cli.github.com/manual/
- **Workflows**: Check `.github/workflows/` for configuration

---

## ✅ Summary

**Choose your deployment path:**

- **Quick & Simple**: `deploy_to_github.py` (existing)
- **Full Control**: `ship_to_github_supersonic.py` (new, comprehensive)
- **Daily Updates**: `make ship` (Makefile target)
- **Releases**: `make tag V=1.2.3` (Makefile target)

All options are production-ready and battle-tested! 🚀
