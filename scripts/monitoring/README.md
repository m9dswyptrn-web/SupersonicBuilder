# GitHub Pages Monitoring Scripts

Quick verification tools for your SonicBuilder GitHub Pages deployment.

## Scripts

### 1. `verify_pages.py` - One-Time Verification

Checks all Pages endpoints once and generates a detailed report.

**Usage:**
```bash
python3 scripts/monitoring/verify_pages.py
```

**Output:**
- Prints verification report to console
- Saves `pages_verification_report.txt`

**What it checks:**
- ✅ Home page (`/`)
- ✅ Latest PDF (`/downloads/latest.pdf`)
- ✅ All 6 badge JSON endpoints:
  - `pdf-health.json`
  - `pages-deploy.json`
  - `updated.json`
  - `downloads.json`
  - `latest.json`
  - `size.json`

**Example output:**
```
GitHub Pages Verification Report
Repo: m9dswyptrn-web/SonicBuilder
Base: https://m9dswyptrn-web.github.io/SonicBuilder
Time: 2024-10-30 15:00:00 UTC

[home]             200  https://m9dswyptrn-web.github.io/SonicBuilder/
[latest.pdf]       200  size=12547891  ok=True
[pdf_health]
  Status: 200
  URL: https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pdf-health.json
  JSON: {"schemaVersion": 1, "label": "pdf health", "message": "OK", "color": "brightgreen"}
...
```

---

### 2. `pages_watch.sh` - Continuous Monitoring

Polls all endpoints every 20 seconds until everything is healthy.

**Usage:**
```bash
./scripts/monitoring/pages_watch.sh
```

**What it does:**
- Checks all endpoints in a loop
- Shows real-time status with icons:
  - 🟢 Green = healthy (200 OK)
  - 🔴 Red = error or no content
  - 🟡 Yellow = checking...
- Runs until Ctrl+C

**Example output:**
```
Watching GitHub Pages for https://m9dswyptrn-web.github.io/SonicBuilder
Press Ctrl+C to stop.

---- 2024-10-30 15:00:00 UTC ----
🟢  200         -  https://m9dswyptrn-web.github.io/SonicBuilder/
🟢  200  12547891  https://m9dswyptrn-web.github.io/SonicBuilder/downloads/latest.pdf
🟢  200       142  https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pdf-health.json
🟢  200       156  https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/pages-deploy.json
🟢  200       128  https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/updated.json
🟢  200       119  https://m9dswyptrn-web.github.io/SonicBuilder/docs/badges/downloads.json
✅ All endpoints healthy!

---- 2024-10-30 15:00:20 UTC ----
...
```

**Perfect for:**
- Waiting for initial Pages deployment
- Monitoring after pushing changes
- Debugging deployment issues

---

## Environment Variables

Both scripts support custom repo configuration:

```bash
# Override defaults
export GH_USER="your-username"
export GH_REPO="your-repo-name"

# Then run scripts
python3 scripts/monitoring/verify_pages.py
./scripts/monitoring/pages_watch.sh
```

**Defaults:**
- `GH_USER=m9dswyptrn-web`
- `GH_REPO=SonicBuilder`

---

## Common Workflows

### After Initial Deployment

```bash
# Deploy to Pages
make pages
git push

# Watch until everything is live
./scripts/monitoring/pages_watch.sh
```

### Quick Health Check

```bash
# One-time verification
python3 scripts/monitoring/verify_pages.py

# Check the report
cat pages_verification_report.txt
```

### Debugging Deployment Issues

```bash
# Continuous monitoring shows exactly when endpoints become available
./scripts/monitoring/pages_watch.sh

# Expected progression:
# 🔴 404 → 🟡 Checking → 🟢 200 OK
```

---

## What Each Badge Shows

| Badge | Endpoint | Shows |
|-------|----------|-------|
| **Latest** | `latest.json` | Current PDF filename |
| **Updated** | `updated.json` | Last build time (human-readable) |
| **Size** | `size.json` | File size in MB |
| **Downloads** | `downloads.json` | Total download count |
| **PDF Health** | `pdf-health.json` | PDF availability (OK/ERR) |
| **Pages Deploy** | `pages-deploy.json` | Deployment status (built/building/errored) |

---

## Expected Behavior

### Before Deployment:
```
🔴  404  latest.pdf
🔴  404  pdf-health.json
🔴  404  pages-deploy.json
```

### After Deployment:
```
🟢  200  latest.pdf (with file size)
🟢  200  pdf-health.json (shows "OK")
🟢  200  pages-deploy.json (shows "built")
```

---

## Troubleshooting

### Issue: All endpoints show 404

**Cause:** Pages not deployed yet

**Solution:**
```bash
# Make sure Pages is enabled in repo settings
# Settings → Pages → Source = gh-pages or main/docs

# Deploy
make pages
git push

# Wait 2-5 minutes for Pages to build
./scripts/monitoring/pages_watch.sh
```

### Issue: PDF shows 404 but badges work

**Cause:** No PDFs in `downloads/` directory

**Solution:**
```bash
# Build PDFs
make build_dark
make build_light

# Copy to downloads
cp output/*.pdf downloads/

# Deploy
make pages
```

### Issue: Script hangs or timeouts

**Cause:** Network issues or Pages building

**Solution:**
```bash
# Check GitHub Pages status
gh api repos/m9dswyptrn-web/SonicBuilder/pages/builds/latest

# Check workflow runs
gh run list --limit 5

# Increase timeout in scripts if needed
```

---

## Integration with CI/CD

Add to your workflow for automated verification:

```yaml
- name: Verify Pages Deployment
  run: |
    python3 scripts/monitoring/verify_pages.py
    
- name: Upload Verification Report
  uses: actions/upload-artifact@v3
  with:
    name: pages-verification
    path: pages_verification_report.txt
```

---

## Complete Monitoring Stack

**Local:**
- ✅ `verify_pages.py` - One-time checks
- ✅ `pages_watch.sh` - Continuous monitoring

**Automated (GitHub Actions):**
- ✅ `badge-update.yml` - Updates badges every 30 min
- ✅ `pages-health-badge.yml` - Health check every 20 min
- ✅ `pages-deploy-badge.yml` - Deploy status monitoring

**Live (Flask Server):**
- ✅ `/badge/*.json` endpoints - Real-time badge data

---

**Your Pages deployment now has complete local + automated monitoring!** 🎉
