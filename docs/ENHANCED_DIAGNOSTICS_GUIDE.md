# Enhanced Diagnostics & Support Bundle System

**Version:** v2.2.3+ (Enhanced)  
**Date:** October 29, 2025  
**Status:** ✅ Production Ready

---

## 🎯 Overview

Enhanced diagnostics system with:
- **Lightweight environment collector** (`collect_env.py`)
- **Modular Makefile fragments** (`MAKEFRAG.support.mk`)
- **Webhook notifications** (Slack + Discord)
- **Enhanced CI/CD workflows** with artifact staging
- **Support bundles** with PDFs, checksums, and diagnostics

---

## 📦 Components

### 1️⃣ **Environment Collector** (Lightweight)

**File:** `tools/diag/collect_env.py`

**Purpose:** Fast, minimal diagnostics collection

**Collects:**
- Timestamp (UTC)
- Git commit SHA
- Python version
- System platform and architecture
- Environment variables (REPL_SLUG, GITHUB_*)
- pip freeze output
- Directory listing

**Output:** `diag/diag_report.json`

**Usage:**
```bash
python tools/diag/collect_env.py
# Creates diag/diag_report.json
```

### 2️⃣ **Full Diagnostics Collector** (Comprehensive)

**File:** `tools/diag/diag_collect.py`

**Purpose:** Complete project state collection

**Collects:**
- All environment info (from collect_env.py)
- Makefile, requirements.txt, config files
- Scripts (scripts/**/*.py under 500 KB)
- Workflows (.github/workflows/*.yml)
- Documentation (docs/**/*.md under 500 KB)
- Logs (out/*.log)
- Optional: PDFs (with --include-pdf)

**Output:** `diag/diag_bundle.zip` (~216 KB)

**Usage:**
```bash
# Without PDFs
python tools/diag/diag_collect.py --out diag/diag_bundle.zip

# With PDFs
python tools/diag/diag_collect.py --out diag/diag_bundle.zip --include-pdf
```

### 3️⃣ **Makefile Fragment**

**File:** `MAKEFRAG.support.mk`

**Targets:**
- `diag-env` - Lightweight diagnostics with environment collector
- `support-bundle-full` - Full support bundle with PDFs and checksums

**Auto-included** in main Makefile via:
```makefile
-include MAKEFRAG.support.mk
```

### 4️⃣ **Webhook Notifier**

**File:** `scripts/notify_webhook.sh`

**Purpose:** Send notifications to Slack and/or Discord

**Usage:**
```bash
./scripts/notify_webhook.sh \
  "Title" \
  "Message text" \
  "https://link.com" \
  "#color"
```

**Environment Variables:**
- `SLACK_WEBHOOK_URL` - Slack incoming webhook URL
- `DISCORD_WEBHOOK_URL` - Discord webhook URL

**Features:**
- Dual-platform support (Slack + Discord)
- JSON payload generation with jq
- Graceful fallback if webhooks not configured
- Color support for Slack attachments

---

## 🚀 Makefile Targets

### Existing Targets (Preserved)

| Target | Description | Tool |
|--------|-------------|------|
| `diag` | Full diagnostics (original) | diag_collect.py |
| `diag-pdf` | Full diagnostics with PDFs | diag_collect.py --include-pdf |
| `support-bundle` | Support bundle (original) | diag_collect.py |
| `ids-flow` | CAN ID workflow | id_discovery_to_tags.py |
| `support-flow` | IDS + support bundle | Combined |
| `support-auto` | Auto-watch mode | support_auto.py |

### New Enhanced Targets

| Target | Description | Tool |
|--------|-------------|------|
| `diag-env` | Lightweight env diagnostics | collect_env.py |
| `support-bundle-full` | Support bundle with PDFs + checksums | collect_env.py + bundling |

---

## 📊 CI/CD Workflows

### 1️⃣ **Diagnostics on Build** (New)

**File:** `.github/workflows/diag-on-build.yml`

**Triggers:**
- Push to `main` branch
- Pull requests to `main`

**Actions:**
1. Collects environment diagnostics
2. Creates bundle ZIP
3. Uploads as workflow artifact
4. Sends webhook notification (optional)

**Outputs:**
- Artifact: `diagnostics_g<commit_sha>`
- Retention: 14 days

**Webhook Notification:**
```
Title: "Diagnostics Ready"
Message: Diagnostics artifact uploaded
Color: #439fe0 (blue)
```

### 2️⃣ **Release Support Bundle** (Enhanced)

**File:** `.github/workflows/release-support.yml`

**Triggers:**
- After successful release workflow completion
- Monitors: "Docs Release (Commit-Stamped)"

**Actions:**
1. Downloads artifacts from release workflow
2. Stages PDFs, checksums, diagnostics
3. Creates comprehensive support bundle
4. Uploads as workflow artifact
5. Sends webhook notification (optional)

**Outputs:**
- Artifact: `support_bundle_g<commit_sha>`
- Retention: 30 days

**Webhook Notification:**
```
Title: "Support Bundle Ready"
Message: Support bundle created for successful release
Color: #2eb886 (green)
```

### 3️⃣ **Docs Release** (Enhanced - Existing)

**File:** `.github/workflows/docs-release.yml`

**Now includes:**
- `diagnostic-run` job (collects CI diagnostics)
- `support-bundle` job (creates support package)

Both run in parallel after main build completes.

---

## 🔔 Webhook Notifications

### Setup

#### For Slack

1. Create incoming webhook:
   - Go to Slack App Directory
   - Search for "Incoming Webhooks"
   - Add to your workspace
   - Copy webhook URL

2. Add to GitHub Secrets:
   ```
   Repository → Settings → Secrets → Actions
   Name: SLACK_WEBHOOK_URL
   Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

#### For Discord

1. Create webhook:
   - Discord Server Settings → Integrations → Webhooks
   - Create New Webhook
   - Copy Webhook URL

2. Add to GitHub Secrets:
   ```
   Repository → Settings → Secrets → Actions
   Name: DISCORD_WEBHOOK_URL
   Value: https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
   ```

### Notification Examples

**Diagnostics Ready:**
```
🔧 Diagnostics Ready
Diagnostics artifact uploaded: `diagnostics_g<sha>`
Repo: user/SonicBuilder
Branch/Ref: refs/heads/main
Run: https://github.com/user/SonicBuilder/actions/runs/123456
```

**Support Bundle Ready:**
```
📦 Support Bundle Ready
Support bundle created for successful release workflow.
Repo: user/SonicBuilder
Triggered Run: https://github.com/user/SonicBuilder/actions/runs/123456
Releases: https://github.com/user/SonicBuilder/releases
```

---

## 📁 Output Structure

### Diagnostics Bundle

```
diag/
├── diag_report.json          # Environment report
└── diag_bundle.zip           # ZIP of above
```

### Support Bundle (Full)

```
support/
├── GIT_SHA.txt               # Current commit
├── VERSION                   # Version file
├── diag_bundle.zip           # Diagnostics
├── *.pdf                     # PDFs from output/ or dist/
├── *.sha256                  # Checksum files
├── SUPPORT_SHA256.txt        # Checksums of all files
└── support_bundle_<timestamp>_g<sha>.zip  # Final bundle
```

---

## 🎯 Complete Workflows

### Local Development

```bash
# Quick diagnostics
make diag-env
# Output: diag/diag_bundle.zip

# Full diagnostics
make diag
# Output: diag/diag_bundle.zip (comprehensive)

# Support bundle with PDFs
make support-bundle-full
# Output: support/support_bundle_<timestamp>_g<sha>.zip
```

### CI/CD (Automatic)

```bash
# Push to main → triggers diagnostics workflow
git push origin main

# Download artifact:
# Actions → Diagnostics (build) → Artifacts → diagnostics_g<sha>

# Tag release → triggers release + support bundle
git tag v2.2.3
git push --tags

# Artifacts created:
# 1. diagnostics_g<sha> (from release workflow)
# 2. support_bundle_g<sha> (from release-support workflow)
```

### Field Support

```bash
# One-shot support package
make support-flow IDS_LOG=out/can_log.csv
# Creates: exports/ids/<timestamp>_<commit>/ + support/support_bundle.zip

# Continuous monitoring
make support-auto
# Watches CAN logs, re-runs on changes
```

---

## 🔍 Comparison Matrix

| Feature | collect_env.py | diag_collect.py |
|---------|---------------|-----------------|
| **Speed** | Fast (~1 sec) | Slower (~5-10 sec) |
| **Size** | Tiny (~2 KB JSON) | Medium (~216 KB ZIP) |
| **Scope** | Environment only | Full project state |
| **Files** | None collected | Makefile, scripts, configs, docs |
| **PDFs** | No | Optional |
| **Use Case** | CI diagnostics | Troubleshooting bundles |

---

## ⚙️ Configuration

### Customize Retention Days

**diag-on-build.yml:**
```yaml
retention-days: 14  # Change to desired days
```

**release-support.yml:**
```yaml
retention-days: 30  # Change to desired days
```

### Add More Files to Support Bundle

Edit `MAKEFRAG.support.mk`:
```makefile
support-bundle-full: diag-env
    # ... existing code ...
    # Add custom files:
    @cp -f custom/*.txt $(SUPPORT_DIR)/ 2>/dev/null || true
```

### Customize Webhook Messages

Edit workflow files to change notification text:
```yaml
- name: Notify (Slack/Discord)
  run: |
    MSG="Your custom message here"
    ./scripts/notify_webhook.sh "Custom Title" "$MSG" "$URL" "#ff0000"
```

---

## ✅ Testing

### Test Diagnostics Collection

```bash
# Test environment collector
python tools/diag/collect_env.py
cat diag/diag_report.json | python -m json.tool

# Test full collector
python tools/diag/diag_collect.py --out diag/test_bundle.zip
unzip -l diag/test_bundle.zip
```

### Test Makefile Targets

```bash
# Test lightweight
make diag-env
ls -lh diag/diag_bundle.zip

# Test full support bundle
make support-bundle-full
ls -lh support/support_bundle_*.zip
unzip -l support/support_bundle_*.zip
```

### Test Webhook Locally

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK"
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK"

./scripts/notify_webhook.sh \
  "Test Notification" \
  "Testing webhook integration" \
  "https://github.com" \
  "#36a64f"
```

---

## 📊 Statistics

| Component | Size | Lines | Type |
|-----------|------|-------|------|
| collect_env.py | 0.6 KB | 25 | Python |
| diag_collect.py | 3.5 KB | 98 | Python |
| notify_webhook.sh | 1.1 KB | 42 | Bash |
| MAKEFRAG.support.mk | 0.9 KB | 30 | Makefile |
| diag-on-build.yml | 1.1 KB | 41 | YAML |
| release-support.yml | 1.7 KB | 59 | YAML |
| **Total** | **8.9 KB** | **295** | **Mixed** |

---

## 🎯 Benefits

### Lightweight Collector (`collect_env.py`)
- ✅ Fast execution (< 1 second)
- ✅ Minimal dependencies
- ✅ Perfect for CI quick checks
- ✅ Small JSON output easy to parse

### Full Collector (`diag_collect.py`)
- ✅ Comprehensive project snapshot
- ✅ Sanitized (no secrets)
- ✅ Includes documentation and configs
- ✅ Optional PDF inclusion

### Webhook Notifications
- ✅ Real-time alerts
- ✅ Dual platform support
- ✅ Customizable messages
- ✅ Zero impact if not configured

### Enhanced CI/CD
- ✅ Automatic diagnostics per build
- ✅ Support bundles per release
- ✅ Artifact staging from prior workflows
- ✅ Comprehensive troubleshooting data

---

## 📚 Related Documentation

- `docs/CI_CD_WORKFLOW_GUIDE.md` - Complete CI/CD documentation
- `INTEGRATION_v2.2.3_IDS_WATCH_DIAGNOSTICS_SUPPORTFLOW.md` - Original diagnostics integration
- `CI_CD_ENHANCEMENT_SUMMARY.md` - CI/CD enhancements summary

---

**The enhanced diagnostics system provides lightweight, fast environment collection alongside comprehensive project state capture, with optional webhook notifications for real-time alerts!** 🚀
