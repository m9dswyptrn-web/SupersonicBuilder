# 🧪 SonicBuilder Smart CI Helper Guide

Complete guide for local CI testing, health monitoring, and dynamic badge generation.

## 📋 Overview

The Smart CI system provides three key components:

1. **CI Helper** - Local build testing and validation
2. **Health Feed Generator** - GitHub Actions integration
3. **Badge Engine** - Real-time SVG badge service

## 🏗️ Components

### 1. Smart CI Helper (`ci_helper.py`)

Complete local CI/CD simulation tool.

**Features:**
- PDF verification with size validation
- Health feed generation
- ZIP artifact archival
- Discord/Slack notifications
- Rollback simulation
- Comprehensive logging

**Usage:**
```bash
# Basic run
python3 ci_helper.py

# With webhooks
export ROLLBACK_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
python3 ci_helper.py
```

**Output:**
- `docs/status/health.json` - Build health status
- `logs/ci.log` - Execution logs
- `artifacts/SonicBuilder_*.zip` - Archived build

**What it validates:**
- PDFs in `docs/` directory
- PDFs in `docs_build/` directory
- Minimum file size (2KB)
- Build success/failure

### 2. Health Feed Generator (`scripts/gen_health_feed.py`)

GitHub Actions integration for build metadata.

**Usage in Workflows:**
```yaml
- name: Generate Health Feed
  if: always()
  env:
    JOB_STATUS: ${{ job.status }}
  run: python3 scripts/gen_health_feed.py

- name: Upload Health Feed
  uses: actions/upload-artifact@v4
  with:
    name: health-feed
    path: docs/status/health.json
```

**Output Format:**
```json
{
  "build_id": "123",
  "commit": "abc123de",
  "status": "success",
  "timestamp": "2025-10-31T12:00:00.000000",
  "artifacts_url": "https://github.com/user/repo/actions/runs/123",
  "workflow": "System Health CI/CD",
  "branch": "main"
}
```

### 3. Badge Engine (`badge_engine.py`)

Dynamic SVG badge service with real-time updates.

**Start Service:**
```bash
# Default port 8081
python3 badge_engine.py

# Custom port
export BADGE_PORT=9000
python3 badge_engine.py
```

**Endpoints:**

| Endpoint | Description | Color Logic |
|----------|-------------|-------------|
| `/badge/status.svg` | Auto-healer status | Green=active, Orange=paused, Grey=unknown |
| `/badge/health.svg` | Build health | Green=success, Red=failure, Grey=no data |
| `/badge/uptime.svg` | Uptime pings | Green=data exists, Grey=no data |
| `/health` | Health check (JSON) | Service status |

**Badge Colors:**
- 🟢 Green (`#4c1`) - Success/Active
- 🟡 Orange (`#fe7d37`) - Warning/Paused
- 🔴 Red (`#e05d44`) - Error/Failure
- ⚪ Grey (`#9f9f9f`) - Unknown/No Data

## 🚀 Usage Scenarios

### Scenario 1: Pre-Commit Testing

Test your build locally before pushing to GitHub.

```bash
# 1. Run CI helper
python3 ci_helper.py

# 2. Check logs
cat logs/ci.log

# 3. Review health feed
cat docs/status/health.json

# 4. Inspect artifacts
ls -lh artifacts/
```

**Expected Output:**
```
[2025-10-31T12:00:00] 🚀 SonicBuilder Smart CI Helper starting…
[2025-10-31T12:00:01] ✅ latest.pdf OK (245.3 KB)
[2025-10-31T12:00:01] 🧩 health.json updated
[2025-10-31T12:00:02] 📦 Artifact archived: artifacts/SonicBuilder_local-1730379600.zip
[2025-10-31T12:00:02] ✅ CI run complete.
```

### Scenario 2: Badge Monitoring

Start the badge engine for real-time status monitoring.

```bash
# Start badge engine
python3 badge_engine.py &

# Test badges
curl http://localhost:8081/badge/status.svg > status.svg
curl http://localhost:8081/badge/health.svg > health.svg
curl http://localhost:8081/badge/uptime.svg > uptime.svg

# View in browser
open status.svg
```

**Use in README:**
```markdown
![Status](http://your-replit.repl.co:8081/badge/status.svg)
![Health](http://your-replit.repl.co:8081/badge/health.svg)
![Uptime](http://your-replit.repl.co:8081/badge/uptime.svg)
```

### Scenario 3: GitHub Actions Integration

Add health feed generation to your workflows.

```yaml
# .github/workflows/system-health-ci.yml
jobs:
  build:
    steps:
      - name: Build Documentation
        run: make build-docs
      
      - name: Generate Health Feed
        if: always()
        env:
          JOB_STATUS: ${{ job.status }}
        run: python3 scripts/gen_health_feed.py
      
      - name: Upload Health Feed
        uses: actions/upload-artifact@v4
        with:
          name: health-feed-${{ github.run_number }}
          path: docs/status/health.json
          retention-days: 30
```

## 🔧 Configuration

### Environment Variables

**CI Helper:**
```bash
GITHUB_REPOSITORY   # Repository name (default: m9dswyptrn-web/SonicBuilder)
GITHUB_RUN_ID       # Run ID (default: local-{timestamp})
GITHUB_RUN_NUMBER   # Run number (default: 0)
GITHUB_SHA          # Commit SHA (default: local)
ROLLBACK_WEBHOOK_URL # Discord webhook URL
SLACK_WEBHOOK_URL    # Slack webhook URL
```

**Badge Engine:**
```bash
BADGE_PORT          # Port number (default: 8081)
```

**Health Feed Generator:**
```bash
GITHUB_RUN_NUMBER   # Build ID
GITHUB_SHA          # Commit SHA
JOB_STATUS          # Job status (success/failure)
GITHUB_REPOSITORY   # Repository name
GITHUB_RUN_ID       # Run ID
GITHUB_WORKFLOW     # Workflow name
GITHUB_REF_NAME     # Branch name
```

## 📦 Artifact Structure

### ZIP Archive Contents

```
SonicBuilder_{RUN_ID}.zip
├── docs/
│   ├── *.pdf
│   └── status/
│       ├── health.json
│       ├── system.json
│       └── uptime_log.json
├── logs/
│   └── ci.log
└── scripts/
    └── *.py
```

## 🔍 Troubleshooting

### CI Helper Issues

**Problem:** "No PDFs found"
- **Solution:** Ensure PDFs exist in `docs/` or `docs_build/`

**Problem:** "PDF too small"
- **Solution:** Check PDF generation, must be >2KB

**Problem:** Notifications not sending
- **Solution:** Verify webhook URLs are set correctly

### Badge Engine Issues

**Problem:** "Address already in use"
- **Solution:** Kill existing process or use different port
  ```bash
  lsof -ti:8081 | xargs kill
  export BADGE_PORT=9000
  python3 badge_engine.py
  ```

**Problem:** Badges showing "no data"
- **Solution:** Ensure data files exist:
  - `badges/auto_healer_status.json`
  - `docs/status/health.json`
  - `docs/status/uptime_log.json`

### Health Feed Issues

**Problem:** Missing workflow metadata
- **Solution:** Ensure environment variables are set in GitHub Actions

**Problem:** Invalid JSON output
- **Solution:** Check Python version (requires 3.7+)

## 🎨 Customization

### Adding Custom Badges

Edit `badge_engine.py` to add new endpoints:

```python
@app.route("/badge/custom.svg")
def badge_custom():
    # Your custom logic
    value = "my value"
    color = "#4c1"
    
    svg = _make_svg("Label", value, color)
    response = make_response(svg)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Cache-Control"] = "no-cache"
    return response
```

### Custom Health Feed Fields

Edit `scripts/gen_health_feed.py`:

```python
data = {
    "build_id": os.getenv("GITHUB_RUN_NUMBER", "local"),
    # Add custom fields
    "custom_field": "your value",
    "another_field": calculate_something(),
}
```

## 📊 Integration with Existing Systems

### Auto-Healer Integration

The badge engine reads from `badges/auto_healer_status.json`:

```python
# Badge engine automatically displays auto-healer status
# No additional configuration needed
```

### Uptime Monitoring Integration

Uptime badge reads from `docs/status/uptime_log.json`:

```python
# Shows number of uptime pings
# Updates automatically as log grows
```

### Rollback System Integration

CI helper can trigger rollback on failure:

```python
# Checks for rollback_backup.zip
# Restores if build fails
```

## 🎯 Best Practices

1. **Run CI helper before committing**
   - Catches issues early
   - Validates build locally

2. **Monitor badges in real-time**
   - Quick visual health check
   - Embed in documentation

3. **Archive health feeds**
   - Track build history
   - Debugging failed builds

4. **Set up webhook notifications**
   - Get instant alerts
   - Monitor remotely

5. **Use health feed in dashboards**
   - Build custom monitoring
   - Track trends over time

## 📚 Related Documentation

- `HARMONY_SYNC_GUIDE.md` - Harmony feed system
- `ROLLBACK_SYSTEM_README.md` - Rollback protection
- `INFINITY_QUICK_REFERENCE.md` - Quick commands

---

**SonicBuilder v2.0.9 — Smart CI Helper + Badge Engine**

*Complete local testing and real-time monitoring solution*
