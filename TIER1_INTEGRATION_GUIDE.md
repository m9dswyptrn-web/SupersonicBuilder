# 🚀 Tier 1 Integration Guide - Auto Orchestrator + Fusion Summary

Complete guide for the newly integrated **Auto Orchestrator v5.0** and **Fusion Summary v4.0** systems.

## 📋 Overview

**Tier 1 Files Installed:**
- ✅ `auto_orchestrator.py` - One-command build automation
- ✅ `generate_fusion_summary.py` - Standalone health summary generator
- ✅ `fusion_summary.py` - Flask server for live health monitoring (port 8093)

## 🎯 Auto Orchestrator v5.0

**Purpose:** Unified build automation that runs all SonicBuilder systems in the correct sequence.

### Features

- **System Health Generation** - Generates system.json with current status
- **Fusion Summary** - Creates health appendix from telemetry/uptime logs
- **PDF Building** - Runs supersonic_autodeploy.py to build manual
- **Health Appendix** - Injects health data into PDF (if appendix script exists)
- **Metadata Stamping** - Timestamps build with version info
- **Auto-Deploy** - Deploys to GitHub Pages (if deploy script exists)

### Usage

**Single Command Build:**
```bash
python3 auto_orchestrator.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════╗
║   🧠 SONICBUILDER AUTO ORCHESTRATOR v5.0                      ║
╚════════════════════════════════════════════════════════════════╝

🔹 Running: Generate System Health
✅ Step complete: Generate System Health

🔹 Running: Generate Fusion Summary
✅ Step complete: Generate Fusion Summary

🔹 Running: Generate PDF Manual
✅ Step complete: Generate PDF Manual

🕓 Metadata stamped at 2025-10-31 14:05:13 UTC

╔════════════════════════════════════════════════════════════════╗
║   🚀 ORCHESTRATION COMPLETE in 4.24s
╚════════════════════════════════════════════════════════════════╝
```

### Files Generated

```
docs/status/
├── system.json              # System health snapshot
├── fusion_summary.json      # Health metrics
└── build_metadata.json      # Build timestamp & info

docs/
└── appendix_system_health.md  # Health report appendix
```

### Configuration

Edit `auto_orchestrator.py` to customize:

```python
# === CONFIG ===
SUMMARY_SCRIPT = "generate_fusion_summary.py"  # Summary generator
PDF_BUILDER = "supersonic_autodeploy.py"       # PDF builder
DEPLOY_SCRIPT = "scripts/deploy_pages.sh"      # Deploy script
SYSTEM_HEALTH = "scripts/gen_system_json.py"   # Health generator
FINAL_PDF = "downloads/latest.pdf"             # Output path
```

### Integration with Existing Systems

**Works With:**
- ✅ Auto-Healer (uses same health monitoring)
- ✅ Uptime Monitor (reads uptime_log.json)
- ✅ System Health (gen_system_json.py)
- ✅ CI Helper (complementary local testing)
- ✅ Badge Engine (uses generated JSONs)

**Replaces:** Nothing - this is purely additive

## 📊 Fusion Summary v4.0

**Purpose:** Generate health reports from telemetry and uptime data.

### Two Modes

**1. Standalone Generator** (`generate_fusion_summary.py`)
- Single-run script for orchestrator
- Generates health appendix markdown
- Creates JSON summary
- No server required

**2. Live Server** (`fusion_summary.py`)
- Flask web server on port 8093
- Real-time health endpoints
- Interactive web dashboard

### Standalone Mode Usage

```bash
python3 generate_fusion_summary.py
```

**Output:**
```
✅ Fusion summary written → docs/appendix_system_health.md
✅ Fusion JSON → docs/status/fusion_summary.json

📊 Health Index: 0.95 | Uptime: 95.0%
```

### Server Mode Usage

```bash
python3 fusion_summary.py
# Server starts on http://localhost:8093
```

**Endpoints:**
- `/charts/summary` - JSON health summary
- `/charts/summary/view` - HTML health dashboard

**Example Request:**
```bash
curl http://localhost:8093/charts/summary
```

**Response:**
```json
{
  "avg_delay": 0.8,
  "date": "2025-10-31",
  "failures": 0,
  "health_index": 0.95,
  "total_entries": 2,
  "uptime_pct": 95.0
}
```

### Health Metrics Explained

| Metric | Description | Range |
|--------|-------------|-------|
| **uptime_pct** | Percentage of successful checks | 0-100% |
| **failures** | Number of failed checks | 0+ |
| **total_entries** | Total number of checks performed | 0+ |
| **avg_delay** | Average response time | 0-∞ seconds |
| **health_index** | Overall health score | 0-1 (1=perfect) |

### Health Status Interpretation

```
🟢 Excellent  - Health Index > 0.9
🟡 Good       - Health Index > 0.7
🔴 Attention  - Health Index < 0.7
```

### Data Sources

**Priority Order:**
1. **Telemetry Logs** - `logs/telemetry/{date}.json` (if exists)
2. **Uptime Log** - `docs/status/uptime_log.json` (fallback)
3. **None** - Shows warning if no data available

### Generated Files

**fusion_summary.json:**
```json
{
  "date": "2025-10-31",
  "uptime_pct": 95.0,
  "failures": 0,
  "total_entries": 2,
  "avg_delay": 0.8,
  "health_index": 0.95
}
```

**appendix_system_health.md:**
```markdown
# Appendix: SonicBuilder System Health Report

**Generated:** 2025-10-31 14:04:26 UTC  
**Period:** 2025-10-31

## Health Metrics

| Metric | Value |
|--------|-------:|
| ✅ Uptime | 95.0% |
| ⚠️ Failures | 0 |
| 📊 Total Checks | 2 |
| ⏱ Avg Response | 0.8s |
| 🧠 Health Index | 0.95 |

## System Status

**Overall Health:** 🟢 Excellent

_Integrated with Auto-Healer, Uptime Monitor, and System Health tracking._
```

## 🔧 Advanced Usage

### Add Fusion Server as Workflow

If you want the Fusion server always running:

```bash
# Add to workflows
workflows_set_run_config_tool(
    name="Fusion Monitor",
    command="python3 fusion_summary.py",
    output_type="console",
    wait_for_port=8093
)
```

### Integrate with GitHub Actions

Add to your workflow YAML:

```yaml
- name: Generate Fusion Summary
  run: python3 generate_fusion_summary.py

- name: Upload Health Appendix
  uses: actions/upload-artifact@v4
  with:
    name: health-appendix
    path: docs/appendix_system_health.md
```

### Use in PDF Generation

If you have a PDF appendix injector, it can use:
- `docs/appendix_system_health.md` - Health report
- `docs/status/fusion_summary.json` - Metrics data

### Custom Telemetry Logging

Create telemetry logs in this format:

```json
{"status": "green", "timestamp": "2025-10-31T12:00:00"}
{"status": "green", "timestamp": "2025-10-31T12:15:00"}
{"status": "red", "timestamp": "2025-10-31T12:30:00"}
```

Save to: `logs/telemetry/{YYYY-MM-DD}.json`

## 🎯 Quick Commands

```bash
# Run full orchestration
python3 auto_orchestrator.py

# Generate health summary only
python3 generate_fusion_summary.py

# Start fusion server
python3 fusion_summary.py

# View fusion summary JSON
cat docs/status/fusion_summary.json

# View health appendix
cat docs/appendix_system_health.md

# Check build metadata
cat docs/status/build_metadata.json
```

## 📚 Integration with Other Systems

### With Auto-Healer

Auto-Healer updates `uptime_log.json` → Fusion Summary uses it as data source

### With CI Helper

```bash
# Run CI helper first (validate PDFs)
python3 ci_helper.py

# Then run orchestrator (full build)
python3 auto_orchestrator.py
```

### With Badge Engine

Badge Engine can read `fusion_summary.json` to display health badges.

### With System Health CI

GitHub Actions workflow can call:
```bash
python3 generate_fusion_summary.py
```
To include health appendix in deployed artifacts.

## 🔍 Troubleshooting

### "No telemetry or uptime data available"

**Cause:** No data sources found  
**Solution:** 
- Ensure Auto-Healer is running (creates uptime_log.json)
- Or create telemetry logs manually

### "PDF not found"

**Cause:** supersonic_autodeploy.py didn't create PDF  
**Solution:**
- Check if supersonic_autodeploy.py exists
- Verify downloads/ directory exists
- Check build logs for errors

### Fusion server port conflict

**Cause:** Port 8093 already in use  
**Solution:**
```bash
# Kill existing process
lsof -ti:8093 | xargs kill

# Or edit port in fusion_summary.py
app.run(port=9093)  # Use different port
```

## 📊 Complete File Structure

```
SonicBuilder/
├── auto_orchestrator.py            # ← NEW (Tier 1)
├── generate_fusion_summary.py      # ← NEW (Tier 1)
├── fusion_summary.py               # ← NEW (Tier 1)
│
├── docs/
│   ├── appendix_system_health.md   # ← GENERATED (health report)
│   └── status/
│       ├── fusion_summary.json     # ← GENERATED (health metrics)
│       ├── build_metadata.json     # ← GENERATED (build info)
│       ├── system.json             # Existing system health
│       └── uptime_log.json         # Existing uptime log
│
├── logs/
│   └── telemetry/                  # Optional telemetry logs
│       └── {YYYY-MM-DD}.json
│
└── scripts/
    ├── gen_system_json.py          # Existing system health
    └── deploy_pages.sh             # Existing deployment
```

## 🎉 Benefits

**Before Tier 1:**
- Manual multi-step builds
- Separate health tracking
- No unified build command
- No health appendix generation

**After Tier 1:**
- ✅ One-command orchestration
- ✅ Automatic health summaries
- ✅ Build metadata tracking
- ✅ Health appendix for PDFs
- ✅ Integrated with all systems

---

**SonicBuilder v2.0.9 — Tier 1 Integration Complete**

*Auto Orchestrator + Fusion Summary = Unified Build Automation*
