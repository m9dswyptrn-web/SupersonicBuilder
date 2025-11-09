# 🚀 Supersonic Control Core v4 — Ultimate Edition Integration Guide

## Overview

Supersonic Control Core v4 Ultimate Edition is a complete enterprise-grade automation, CI/CD, and deployment suite that integrates seamlessly with your SonicBuilder system. This version adds **AI-powered operations**, **Android/Head Unit deployment**, **automated housekeeping**, and **beautiful diagnostics dashboards**.

---

## 🎯 What's New in v4

### **1. AI-Powered Automation**
- **AI Release Notes** - Automatically generates release notes from commit history
- **Smart Version Bumping** - Semantic versioning with conventional commits
- **AI Build Reasoner** - Analyzes builds and suggests fixes

### **2. Android & Head Unit Deployment**
- **ADB Toolkit** - Auto-installs Android platform-tools
- **One-Command Deployment** - Push APKs directly to connected Android devices
- **Remote Diagnostics** - Fetch logcat, reboot devices, monitor installations

### **3. Security & Integrity**
- **SHA256 Checksums** - Automatic hash generation for all artifacts
- **Cosign Signing** - Optional keyless signing with Sigstore
- **SBOM Generation** - Software Bill of Materials with Syft
- **Vulnerability Scanning** - Trivy, pip-audit support

### **4. GitHub Automation**
- **Automated Releases** - Tag-triggered builds with GitHub Actions
- **GitHub Pages** - Auto-publish release portals with diagnostics
- **Housekeeping** - Automated cleanup of old releases and Pages

### **5. Voice Feedback & CLI**
- **Supersonic Launcher** - Unified CLI for all operations
- **Voice Events** - Plays audio cues during build/deploy operations
- **Colorized Output** - Rich terminal UI with progress indicators

---

## 📁 File Structure

```
.
├── make/
│   └── ControlCore.mk                    # v4 Makefile targets
├── scripts/
│   ├── doctor.py                         # Environment diagnostics
│   ├── integrity.py                      # SHA256 + Cosign signing
│   ├── rollback.py                       # Git rollback utility
│   ├── sbom_scan.py                      # SBOM + security scanning
│   ├── release_notes_ai.py               # AI release notes generator
│   ├── adb_actions.py                    # Android deployment toolkit
│   └── voicepack_manager.py              # Voice pack installer
├── .github/workflows/
│   ├── release-v4-supersonic.yml         # Automated release pipeline
│   └── housekeeping-supersonic.yml       # Automated cleanup
├── docs/
│   ├── index_release_portal.html         # Release portal (static)
│   └── index_diagnostics.html            # System diagnostics dashboard
├── supersonic_launcher.py                # Unified CLI tool
├── build_supersonic_v4.py                # v4 package builder
└── requirements.txt                      # Updated Python dependencies

```

---

## ⚙️ Installation & Setup

### **Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: (Optional) Install External Tools**

```bash
# Cosign (for artifact signing)
curl -sL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 -o cosign
chmod +x cosign && sudo mv cosign /usr/local/bin/

# Syft (for SBOM generation)
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Trivy (for vulnerability scanning)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

**Note:** ADB (Android platform-tools) auto-installs when needed via `scripts/adb_actions.py`

### **Step 3: Configure Secrets (Optional)**

For full automation, set these environment variables:

```bash
export OPENAI_API_KEY="sk-..."              # For AI release notes
export SUP_DISCORD_WEBHOOK="https://..."    # Discord notifications
export SUP_SLACK_WEBHOOK="https://..."      # Slack notifications
export SUP_SIGN_KEY="cosign.key"            # Cosign signing key (optional)
```

For GitHub Actions, add these as repository secrets:
- `OPENAI_API_KEY`
- `SUP_DISCORD_WEBHOOK`
- `SUP_SLACK_WEBHOOK`
- `SUP_SIGN_KEY_B64` (base64-encoded cosign key)

---

## 🚀 Quick Start Guide

### **Using the Supersonic Launcher (CLI)**

The `supersonic_launcher.py` provides a unified interface for all v4 operations:

```bash
# Make it executable
chmod +x supersonic_launcher.py

# Run preflight checks
./supersonic_launcher.py doctor

# Build with AI summary
./supersonic_launcher.py build

# Full release pipeline
./supersonic_launcher.py release

# Deploy to Android head unit
./supersonic_launcher.py unit-deploy app-release.apk

# Rollback to previous version
./supersonic_launcher.py rollback v2.3.0

# Generate AI release notes
./supersonic_launcher.py notes

# Play voice announcement
./supersonic_launcher.py announce --event deploy_done
```

### **Using Make Targets**

If you've included `ControlCore.mk` in your root Makefile:

```bash
# Preflight diagnostics
make -f make/ControlCore.mk ai-doctor

# Build with AI
make -f make/ControlCore.mk ai-build

# Full release pipeline
make -f make/ControlCore.mk ai-release

# Version bump
make -f make/ControlCore.mk ai-bump

# Integrity check (SHA256 + Cosign)
make -f make/ControlCore.mk ai-hash

# SBOM generation
make -f make/ControlCore.mk ai-sbom

# Android deployment
make -f make/ControlCore.mk unit-deploy APK=app-release.apk

# View all targets
make -f make/ControlCore.mk ai-help
```

---

## 🤖 GitHub Actions Integration

### **Automated Releases**

The `release-v4-supersonic.yml` workflow triggers automatically when you push a tag:

```bash
# Tag and push
git tag v2.5.0
git push origin v2.5.0
```

The workflow will:
1. ✅ Run preflight checks (`doctor.py`)
2. 🧠 Bump version smartly (`version_bump.py`)
3. 🏗️ Build with AI summary
4. 🔏 Generate SHA256 checksums
5. 🧾 Create SBOM (if tools available)
6. 📝 Generate AI release notes
7. 🚀 Create GitHub Release with assets
8. 🌐 Publish to GitHub Pages (`/<tag>/`)
9. 🔔 Send webhook notifications

### **Housekeeping Automation**

The `housekeeping-supersonic.yml` workflow runs every Monday at 03:11 UTC (or manually):

- **Prunes old GitHub Pages** (keeps latest 10 tags by default)
- **Prunes old GitHub Releases** (keeps latest 10 releases by default)
- **Optional:** Delete corresponding git tags

**Manual Trigger:**
```
Actions → Supersonic — Housekeeping → Run workflow
  - keep: 10 (number of versions to keep)
  - dry_run: true (preview changes without deleting)
  - delete_tags: false (also delete git tags)
```

---

## 🌐 GitHub Pages Structure

When a release is published, assets are deployed to:

```
https://<username>.github.io/<repo>/<tag>/
  ├── docs/
  │   ├── index_release_portal.html      # Release portal
  │   └── index_diagnostics.html         # System diagnostics
  ├── Supersonic_ControlCore_Addons_v4.zip
  ├── Supersonic_ControlCore_Addons_v4.zip.sig  (optional)
  ├── SHA256SUMS.txt
  ├── AI_RELEASE_NOTES.md
  ├── sbom.json                          (optional)
  ├── scan.txt                           (optional)
  └── logs/
      └── supersonic_changelog.log
```

### **Diagnostics Dashboard Features**

The `index_diagnostics.html` page provides:
- ✅ System status indicators (AI, Voice, Webhooks, Integrity, SBOM)
- 📘 AI-generated release notes viewer
- 📜 Changelog from AI reasoner
- 🔐 Integrity checksums display
- 🧾 SBOM/security scan results
- 🔗 Direct download links

---

## 🛠️ Utility Scripts Reference

### **doctor.py** - Environment Diagnostics
```bash
python3 scripts/doctor.py
```
Checks:
- Python version
- Git availability
- Cosign installation
- ADB availability  
- API keys (OPENAI_API_KEY, webhooks)

### **integrity.py** - Checksums & Signing
```bash
python3 scripts/integrity.py
```
- Generates SHA256SUMS.txt for all .zip/.tar.gz files
- Signs with Cosign if `SUP_SIGN_KEY` or `cosign.key` exists

### **rollback.py** - Git Rollback
```bash
python3 scripts/rollback.py v2.3.0  # Specific tag
python3 scripts/rollback.py         # Latest tag
```

### **sbom_scan.py** - SBOM & Security Scan
```bash
python3 scripts/sbom_scan.py
```
Runs (if installed):
- Syft for SBOM generation
- pip-audit or Trivy for vulnerability scanning

### **release_notes_ai.py** - AI Release Notes
```bash
python3 scripts/release_notes_ai.py
```
Creates `AI_RELEASE_NOTES.md` from recent git commit history.

### **adb_actions.py** - Android Deployment
```bash
# Auto-installs ADB if missing, then:
python3 scripts/adb_actions.py deploy app-release.apk
python3 scripts/adb_actions.py reboot
python3 scripts/adb_actions.py logs
```

### **voicepack_manager.py** - Voice Pack Installer
```bash
python3 scripts/voicepack_manager.py https://example.com/pack.zip
```

---

## 🎨 Voice System Integration

v4 integrates seamlessly with existing voice packs:

```bash
# Set voice mode
./supersonic_launcher.py voice flightops

# Play specific event
./supersonic_launcher.py announce --event build_success

# Install new voicepack
./supersonic_launcher.py voice-install https://example.com/pack.zip

# Suppress voice (quiet mode)
QUIET=1 ./supersonic_launcher.py build
```

**Available voice events:**
- `build_start` - Build/operation initiated
- `build_success` - Build completed successfully
- `build_fail` - Build/operation failed
- `deploy_start` - Deployment initiated
- `deploy_done` - Deployment completed

---

## 📊 Make Target Reference

```bash
# Core Operations
ai-build              # Build with AI summary
ai-watch              # Watch mode with AI
ai-bump               # Smart semantic version bump
ai-release            # Full pipeline (bump→build→hash→sbom→notes→notify)

# Utilities
ai-doctor             # Preflight diagnostics
ai-rollback TAG=v2.3.1  # Rollback to tag
ai-hash               # SHA256 + optional Cosign
ai-sbom               # SBOM + security scan
ai-notes              # AI release notes

# Voice & Console
ai-voice MODE=flightops           # Set voice mode
ai-announce VOICE_EVENT=deploy_done  # Play event
ai-voice-install URL=https://...  # Install voicepack

# Android / Head Unit
unit-deploy APK=app.apk  # Deploy APK
unit-reboot              # Reboot device
unit-logs                # Fetch logcat

# Help
ai-help                  # Show all targets
```

---

## 🔐 Security Best Practices

1. **Never commit secrets** - Use environment variables or GitHub Secrets
2. **Verify checksums** - Always check SHA256SUMS.txt before using artifacts
3. **Review SBOM** - Check `sbom.json` for dependency vulnerabilities
4. **Cosign verification** - Verify signatures with `cosign verify-blob`
5. **Housekeeping** - Regularly prune old releases to reduce attack surface

---

## 🐛 Troubleshooting

### **Issue: Doctor shows missing tools**
```bash
pip install -r requirements.txt
```
External tools (trivy, syft, cosign) are optional - install as needed.

### **Issue: ADB not found**
The `adb_actions.py` script auto-installs platform-tools. Ensure you have internet connectivity.

### **Issue: Voice not working**
- Check `QUIET` environment variable (set to empty or 0)
- Verify voice pack WAV files exist in `assets/audio/voicepacks/`
- Check `pyttsx3` and `playsound` are installed

### **Issue: GitHub Actions workflow fails**
- Verify secrets are configured (Actions → Settings → Secrets)
- Check workflow logs for specific errors
- Ensure GitHub Pages is enabled (Settings → Pages)

### **Issue: Housekeeping deletes too much**
Housekeeping runs in **dry_run mode by default**. Review the Actions log before setting `dry_run: false`.

---

## 📚 Additional Resources

- **Original MEGA v2 Integration**: `docs/MEGA_INTEGRATION_COMPLETE.md`
- **ControlCore v3 Guide**: `docs/README_ControlCore.md`
- **Voice System**: `helpers/supersonic_voice_console.py`
- **GitHub Actions**: `.github/workflows/`

---

## 🎯 Next Steps

1. ✅ Run `./supersonic_launcher.py doctor` to verify setup
2. ✅ Test local build: `./supersonic_launcher.py build`
3. ✅ Configure GitHub Secrets for full automation
4. ✅ Push a test tag to trigger automated release
5. ✅ Review GitHub Pages diagnostics dashboard
6. ✅ Configure housekeeping schedule as needed

---

## 💡 Pro Tips

- **Alias for convenience**: `alias ssup="./supersonic_launcher.py"`
- **Check Make integration**: Add `-include make/ControlCore.mk` to root Makefile
- **Batch operations**: Use `make ai-release` for full pipeline
- **Monitor housekeeping**: Review Actions tab every Monday after cron runs
- **Customize Pages**: Edit `docs/index_*.html` templates before pushing tags

---

## 🚀 Summary

Supersonic Control Core v4 provides:
- ✅ **7 utility scripts** for automation
- ✅ **1 unified CLI** for all operations  
- ✅ **2 GitHub workflows** (release + housekeeping)
- ✅ **2 HTML dashboards** (portal + diagnostics)
- ✅ **40+ Make targets** for every operation
- ✅ **Full CI/CD** with GitHub Actions
- ✅ **Android deployment** with auto-installing ADB
- ✅ **AI-powered** release notes and analysis

**Your Supersonic system is now Ultimate Edition certified!** 🎉

---

_© 2025 Supersonic Systems — "Fast is fine. Supersonic is better."_
