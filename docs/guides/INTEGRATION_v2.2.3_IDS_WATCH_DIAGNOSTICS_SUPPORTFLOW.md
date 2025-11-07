# SonicBuilder Integration: IDS Watch + Diagnostics + Support Flow

**Version:** v2.2.3 (IDS Watch) + v1.0.0 (Diagnostics) + v1.0.1 (Support Flow)  
**Integration Date:** October 29, 2025  
**Status:** ✅ Production Ready (Architect Approved)

---

## 🎯 Overview

This integration adds three critical support and diagnostics capabilities to SonicBuilder:

1. **IDS Watch (v2.2.3)** - Auto-monitoring for CAN log changes with automatic ID artifact export
2. **Diagnostics (v1.0.0)** - Project state collection for rapid troubleshooting
3. **Support Flow (v1.0.1)** - Automated workflow chaining IDS analysis → diagnostics bundle

---

## 📦 What's Included

### 1️⃣ IDS Watch - Auto-Monitor CAN Logs
**Location:** `tools/can/ids_watch.py`

Watches CAN log files and automatically re-runs ID discovery workflow when changes are detected.

**Features:**
- ✅ Monitors CSV and JSONL CAN logs using watchdog
- ✅ Auto-triggers `make ids-flow` on file changes
- ✅ Non-blocking background watcher
- ✅ Multi-path monitoring support

**Usage:**
```bash
# Start watching CAN logs
make ids-watch

# Runs continuously, watching:
# - out/can_log.csv
# - out/teensy_raw.jsonl
```

**How It Works:**
1. Monitors specified log files for modifications
2. Triggers `make ids-flow` automatically when changes detected
3. Exports artifacts to `exports/ids/<timestamp>_<commit>/`
4. Continues watching until Ctrl+C

---

### 2️⃣ Diagnostics - Project State Collection
**Location:** `tools/diag/diag_collect.py`

Creates sanitized ZIP bundle of project state for troubleshooting without exposing secrets.

**Features:**
- ✅ Collects Makefile, requirements, scripts, workflows
- ✅ Includes environment info (Python version, pip freeze)
- ✅ Optional PDF inclusion (use `--include-pdf`)
- ✅ Excludes sensitive dirs (.git, node_modules, venv)
- ✅ Size-limited files (500 KB max)

**What Gets Collected:**
```
✅ Configuration files:
   - Makefile, .replit, requirements*.txt, pyproject.toml
   
✅ Scripts:
   - scripts/**/*.py (under 500 KB)
   
✅ Workflows:
   - .github/workflows/*.yml
   
✅ Documentation:
   - docs/**/*.md (under 500 KB)
   
✅ Logs:
   - out/*.log
   
✅ PDFs (with --include-pdf):
   - out/*.pdf
   
✅ Environment info:
   - Python version, platform, timezone
   - pip freeze output
   
❌ Excluded:
   - .git/, node_modules/, venv/, __pycache__/
   - exports/, large binaries
   - Secrets and API keys
```

**Usage:**
```bash
# Create bundle without PDFs
make diag

# Create bundle with PDFs (may be large)
make diag-pdf

# Output: diag/diag_bundle.zip (~216 KB without PDFs)
```

---

### 3️⃣ Support Flow - Automated Support Workflow
**Location:** `tools/support/support_auto.py`

Chains CAN ID analysis and diagnostics collection into single automated workflow.

**Features:**
- ✅ One-shot mode: Run full flow once
- ✅ Auto mode: Watch and re-run on changes
- ✅ Combines IDS export + diagnostics bundle
- ✅ Timestamped output directories

**Usage:**
```bash
# One-shot: Run full support flow once
make support-flow IDS_LOG=out/can_log.csv
# Creates:
# - exports/ids/<timestamp>_<commit>/
# - support/support_bundle.zip

# Auto mode: Watch and re-run on changes
make support-auto
# Initial run + continuous monitoring
# Re-runs on changes to:
# - out/can_log.csv
# - out/teensy_raw.jsonl
```

**Workflow Chain:**
```
support-flow:
  ↓
  ids-flow (parse CAN logs)
  ├─→ out/ids_summary.csv
  ├─→ out/ids_tag_template.json
  └─→ exports/ids/<timestamp>_<commit>/
  ↓
  support-bundle (collect diagnostics)
  └─→ support/support_bundle.zip
```

---

## 🚀 Quick Start

### Install Dependencies
```bash
# Dependencies already added to requirements.txt
pip install -r requirements.txt

# Includes: watchdog, pyserial (for CAN monitoring)
```

### Basic Workflows

#### 1. Create Diagnostics Bundle
```bash
# Without PDFs (~216 KB)
make diag

# With PDFs (larger)
make diag-pdf

# Upload diag/diag_bundle.zip for troubleshooting
```

#### 2. Parse CAN Logs (IDS Flow)
```bash
# From CSV log
make ids-flow IDS_LOG=out/can_log.csv

# From JSONL log
make ids-flow IDS_JSONL=out/teensy_raw.jsonl

# Outputs to: exports/ids/<timestamp>_<commit>/
```

#### 3. Full Support Flow
```bash
# One-shot: Parse + bundle
make support-flow IDS_LOG=out/can_log.csv

# Outputs:
# - exports/ids/<timestamp>_<commit>/
# - support/support_bundle.zip
```

#### 4. Auto-Watch Mode
```bash
# Watch CAN logs and auto-run support flow
make support-auto

# Continuously monitors:
# - out/can_log.csv
# - out/teensy_raw.jsonl
# Re-runs support-flow on changes
```

---

## 📁 File Structure

```
SonicBuilder/
├── tools/
│   ├── can/
│   │   ├── id_discovery_to_tags.py      # CAN ID analyzer (v2.2.2)
│   │   └── ids_watch.py                 # Auto-watcher (NEW v2.2.3)
│   ├── diag/
│   │   └── diag_collect.py              # Diagnostics collector (NEW v1.0.0)
│   └── support/
│       └── support_auto.py              # Support automation (NEW v1.0.1)
├── Makefile                              # Enhanced with new targets
├── requirements.txt                      # Added watchdog
├── exports/
│   └── ids/
│       └── <timestamp>_<commit>/        # IDS artifacts
│           ├── ids_summary.csv
│           └── ids_tag_template.json
├── diag/
│   └── diag_bundle.zip                  # Diagnostics bundle
└── support/
    └── support_bundle.zip               # Support bundle
```

---

## 🎯 Makefile Targets Reference

### New Targets (v2.2.3 + v1.0.x)

| Target | Description | Output |
|--------|-------------|--------|
| `ids-watch` | Auto-watch CAN logs, re-export on changes | Continuous monitoring |
| `diag` | Create diagnostics bundle (no PDFs) | `diag/diag_bundle.zip` |
| `diag-pdf` | Create diagnostics bundle with PDFs | `diag/diag_bundle.zip` |
| `ids-flow` | Parse CAN log, export ID artifacts | `exports/ids/<stamp>_<commit>/` |
| `support-bundle` | Create support bundle | `support/support_bundle.zip` |
| `support-flow` | Run ids-flow → support-bundle | Both outputs |
| `support-auto` | Auto mode: watch + re-run support-flow | Continuous |

### Complete Workflow Examples

```bash
# Development workflow: manual testing
make ids-flow IDS_LOG=out/can_log.csv
make diag

# Field support workflow: one-shot collection
make support-flow IDS_LOG=out/can_log.csv
# Upload support/support_bundle.zip

# Lab workflow: continuous monitoring
make support-auto
# Leave running, automatically processes new CAN data
```

---

## 🔍 Example Output

### IDS Flow Output
```bash
$ make ids-flow IDS_LOG=out/can_log.csv

== Running IDS flow ==
Wrote: out/ids_summary.csv out/ids_tag_template.json
✅ IDS artifacts exported to exports/ids/20251029_181611_b632b7c

$ ls -lh exports/ids/20251029_181611_b632b7c/
-rw-r--r-- 1 user user  62 Oct 29 18:16 ids_summary.csv
-rw-r--r-- 1 user user 122 Oct 29 18:16 ids_tag_template.json
```

**ids_summary.csv:**
```csv
bus,id,count
HS,0x100,15
HS,0x1A0,12
SW,0x201,8
SW,0x285,6
```

**ids_tag_template.json:**
```json
{
  "HS": {
    "0x100": "TAG_ME",
    "0x1A0": "TAG_ME"
  },
  "SW": {
    "0x201": "TAG_ME",
    "0x285": "TAG_ME"
  }
}
```

### Diagnostics Bundle Output
```bash
$ make diag

✅ Diagnostics bundle created: diag/diag_bundle.zip

$ unzip -l diag/diag_bundle.zip | head -15
Archive:  diag/diag_bundle.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    12387  10-29-2025 17:56   Makefile
     1515  10-29-2025 15:58   .replit
      101  10-29-2025 17:58   requirements.txt
     8197  10-29-2025 15:47   README.md
     [... scripts/*, .github/workflows/*.yml ...]
     3456  10-29-2025 18:16   diag/env_info.json
```

### Support Flow Output
```bash
$ make support-flow IDS_LOG=out/can_log.csv

== Running IDS flow ==
Wrote: out/ids_summary.csv out/ids_tag_template.json
✅ IDS artifacts exported to exports/ids/20251029_181611_b632b7c
== Creating support bundle ==
✅ Diagnostics bundle created: support/support_bundle.zip
✅ Support bundle: support/support_bundle.zip
✅ Support flow complete: see support/support_bundle.zip

# Upload support/support_bundle.zip for rapid troubleshooting
```

---

## ⚙️ Technical Details

### IDS Watch Implementation
- **Technology:** Python watchdog library
- **Monitoring:** File modification events on out/ directory
- **Triggers:** Automatic `make ids-flow` invocation
- **Performance:** Non-blocking, 500ms sleep interval
- **Exit:** Graceful shutdown on Ctrl+C

### Diagnostics Collection
- **Archive:** ZIP with DEFLATE compression
- **Size limit:** 500 KB per file
- **Sanitization:** Excludes .git, node_modules, secrets
- **Metadata:** JSON with Python version, platform, pip freeze
- **Safety:** No token/secret collection

### Support Automation
- **Initial run:** Executes support-flow once on startup
- **Watch mode:** Re-runs on CAN log modifications
- **Error handling:** Gracefully skips if logs missing
- **Output:** Timestamped exports + support bundle

---

## ✅ Architect Review: PASSED

**Approval Date:** October 29, 2025

**Findings:**
- ✅ All tools properly integrated with clear Makefile entrypoints
- ✅ Logic aligns with SonicBuilder conventions
- ✅ All make targets execute successfully end-to-end
- ✅ Dependencies present in requirements.txt
- ✅ Repository structure remains organized
- ✅ No security issues observed
- ✅ Subprocess usage scoped to local make targets
- ✅ Diagnostics excludes sensitive directories

**Cleanup Applied:**
- ✅ Removed duplicate `watchdog` entry from requirements.txt

**Recommended Next Steps:**
1. Document support-auto's initial-run requirement (CAN logs must exist)
2. (Optional) Add CI smoke-test for ids-flow/support-flow on fixture data

---

## 🔄 Integration Timeline

| Pack | Version | Integration Date | Status |
|------|---------|------------------|--------|
| v2.2.0-SB-NEXTGEN | Teensy CAN | Oct 29, 2025 | ✅ Complete |
| v2.2.1-NextWave | Manual Merger + OTG | Oct 29, 2025 | ✅ Complete |
| v2.2.2-FullAttack | Field Cards + ID Discovery | Oct 29, 2025 | ✅ Complete |
| v2.2.3-ReleaseCommit | CI/CD + Commit Stamps | Oct 29, 2025 | ✅ Complete |
| **v2.2.3-IDS_Watch** | **Auto-Watch** | **Oct 29, 2025** | **✅ Complete** |
| **v1.0.0-Diagnostics** | **Bundle Collection** | **Oct 29, 2025** | **✅ Complete** |
| **v1.0.1-SupportFlow** | **Workflow Automation** | **Oct 29, 2025** | **✅ Complete** |

**Total:** 7 packs integrated, all architect-approved! 🎉

---

## 📊 Statistics

| Component | Size | Lines | Status |
|-----------|------|-------|--------|
| ids_watch.py | 1.8 KB | 57 | ✅ Production |
| diag_collect.py | 3.5 KB | 98 | ✅ Production |
| support_auto.py | 2.1 KB | 66 | ✅ Production |
| Makefile additions | 0.8 KB | 62 | ✅ Production |
| Total integration | 8.2 KB | 283 | ✅ Production |

**Bundle Outputs:**
- Diagnostics bundle: ~216 KB (without PDFs)
- IDS exports: ~200 bytes per snapshot
- Support bundle: Same as diagnostics (reuses diag_collect.py)

---

## 🎯 Use Cases

### Field Installer Support
```bash
# Installer encounters issue with CAN bridge
# 1. Collect diagnostics
make support-flow IDS_LOG=out/can_log.csv

# 2. Upload support/support_bundle.zip
# 3. Support team analyzes bundle offline
```

### Lab Development
```bash
# Engineer testing CAN firmware changes
# 1. Start auto-monitor
make support-auto

# 2. Flash new firmware to Teensy
# 3. CAN logs auto-update → support-auto re-runs
# 4. Review exports/ids/ for ID changes
```

### CI/CD Validation
```bash
# Automated testing in CI pipeline
# 1. Generate fixture CAN data
# 2. Run support-flow
# 3. Validate outputs exist
# 4. Archive as CI artifacts
```

---

**Version:** v2.2.3 + v1.0.x  
**Status:** ✅ Production Ready  
**Integration Complete:** All 7 packs successfully integrated!
