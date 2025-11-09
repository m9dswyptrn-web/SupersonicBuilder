# SonicBuilder AutoDeploy System Guide

Complete guide for the three autodeploy scripts: interactive, silent, and scheduled deployment.

---

## 📦 Available Scripts

| Script | Purpose | Output | Usage |
|--------|---------|--------|-------|
| `supersonic_autodeploy.py` | **Interactive deploy** | Console + verify.log | Manual runs |
| `supersonic_autodeploy_silent.py` | **Silent deploy** | verify.log only | CI/automated runs |
| `supersonic_scheduler.py` | **Autonomous scheduler** | scheduler.log | Background daemon |

---

## 🚀 Quick Start

### 1. Interactive Deploy (Manual)

For manual deployment with full console output:

```bash
python3 supersonic_autodeploy.py
```

**Output:**
```
╔════════════════════════════════════════════════════════════════╗
║     🚀 SonicBuilder Supersonic AutoDeploy v2.0.9              ║
╚════════════════════════════════════════════════════════════════╝

🚀 Starting SonicBuilder AutoDeploy...

🔐 Phase 1: Security Patch
✅ Security checks passed

📦 Phase 2: Bundle Building
  ✓ Supersonic_Core.zip (193,320 bytes)
  ✓ Supersonic_Security.zip (817 bytes)
  ✓ Supersonic_Diagnostics.zip (22 bytes)
  ✓ Supersonic_Addons.zip (22 bytes)
  ✓ Supersonic_Failsafe.zip (1,157 bytes)
✅ All bundles built

🔍 Phase 3: Checksum Generation
✅ Generated checksums for 4 files

🔐 Phase 4: Signature Generation
✅ Signature: 2.0.9-SB-ULTRA

🚀 Phase 5: Git Deployment
✅ Pushed to GitHub

════════════════════════════════════════════════════════════════
✅ BUILD VERIFIED
🔐 SIGNATURE: 2.0.9-SB-ULTRA
🌐 DEPLOYED TO: https://m9dswyptrn-web.github.io/SonicBuilder/
════════════════════════════════════════════════════════════════

✅ AutoDeploy Complete!
📄 Deployment log: verify.log
```

### 2. Silent Deploy (CI/Automated)

For silent deployment (minimal console output, writes to verify.log):

```bash
python3 supersonic_autodeploy_silent.py
```

**Console Output:**
```
✅ Silent deploy complete - 2025-10-31T00:39:55
🔐 Signature: 2.0.9-SB-ULTRA
📄 Log: verify.log
```

**Full details in verify.log:**
```
[2025-10-31 00:39:55 UTC] === Silent AutoDeploy Start ===
[2025-10-31 00:39:55 UTC] Running security patch...
[2025-10-31 00:39:56 UTC] Security patch complete
[2025-10-31 00:39:56 UTC] Building bundles...
[2025-10-31 00:39:58 UTC] Bundles built: 5/5
[2025-10-31 00:39:58 UTC] Generating checksums...
[2025-10-31 00:39:58 UTC] Checksums generated: 4 files
[2025-10-31 00:39:58 UTC] Generating signature...
[2025-10-31 00:39:58 UTC] Signature: 2.0.9-SB-ULTRA
[2025-10-31 00:39:58 UTC] Deploying to GitHub...
[2025-10-31 00:39:59 UTC] GitHub deployment complete
[2025-10-31 00:39:59 UTC] === BUILD VERIFIED ===
[2025-10-31 00:39:59 UTC] Signature: 2.0.9-SB-ULTRA
[2025-10-31 00:39:59 UTC] Deployed to: https://m9dswyptrn-web.github.io/SonicBuilder/
[2025-10-31 00:39:59 UTC] === Silent AutoDeploy Complete ===
```

### 3. Autonomous Scheduler (Background Daemon)

For automatic deployment every 12 hours:

```bash
# Start scheduler in background
nohup python3 supersonic_scheduler.py &

# Check if running
ps aux | grep supersonic_scheduler

# View logs
tail -f scheduler.log

# Stop scheduler
pkill -f supersonic_scheduler.py
```

**Scheduler Output (scheduler.log):**
```
[2025-10-31 00:40:00 UTC] ╔════════════════════════════════════════════════════════════════╗
[2025-10-31 00:40:00 UTC] ║     🚀 SonicBuilder Autonomous Scheduler Started              ║
[2025-10-31 00:40:00 UTC] ╚════════════════════════════════════════════════════════════════╝
[2025-10-31 00:40:00 UTC] Interval: 12 hours
[2025-10-31 00:40:00 UTC] Silent script: supersonic_autodeploy_silent.py
[2025-10-31 00:40:00 UTC] Log file: scheduler.log
[2025-10-31 00:40:00 UTC] 
[2025-10-31 00:40:00 UTC] ═══ Cycle #1 ═══
[2025-10-31 00:40:00 UTC] ✅ GitHub reachable, starting deploy cycle
[2025-10-31 00:40:00 UTC] Triggering silent auto-deploy...
[2025-10-31 00:40:05 UTC] Silent deploy exit code: 0
[2025-10-31 00:40:05 UTC] ✅ Deploy cycle completed successfully
[2025-10-31 00:40:05 UTC] Next deploy cycle: 2025-10-31 12:40:05 UTC
[2025-10-31 00:40:05 UTC] Sleeping for 12 hours...
```

---

## 🔧 Configuration

### Environment Variables

All scripts require the following environment variable for Git push functionality:

```bash
# Set in Replit Secrets panel
GITHUB_TOKEN=<your_personal_access_token>
```

**Without GITHUB_TOKEN:**
- Scripts will still build bundles, generate checksums, and create signatures
- Git push will be skipped with a warning message

### Scheduler Settings

Edit `supersonic_scheduler.py` to customize:

```python
INTERVAL_HOURS = 12  # Change to 6, 24, etc.
```

---

## 📊 Deployment Phases

All scripts execute the same 5 phases:

### Phase 1: Security Patch
- Runs 10 comprehensive security checks
- Hardens file permissions
- Detects potential secret exposure
- **Output:** `founder_console/security_status.json`

### Phase 2: Bundle Building
- Builds 5 Supersonic bundles:
  - Core (193 KB)
  - Security (817 bytes)
  - Diagnostics (22 bytes)
  - Addons (22 bytes)
  - Failsafe (1.2 KB)
- **Output:** `Supersonic_*.zip` files

### Phase 3: Checksum Generation
- Generates SHA256 checksums for critical files:
  - README.md
  - requirements.txt
  - .replit
  - serve_pdfs.py
- **Output:** `docs/SHA256.txt`

### Phase 4: Signature Generation
- Creates deployment signature
- Timestamp verification
- **Output:** `docs/SIGNATURE.asc`

### Phase 5: Git Deployment
- Commits all changes
- Pushes to GitHub main branch
- Uses `founder_autodeploy.py` for secure operations
- **Output:** GitHub commit + push

---

## 📝 Log Files

| File | Purpose | Updated By |
|------|---------|------------|
| `verify.log` | Deployment verification summary | All scripts |
| `scheduler.log` | Scheduler activity log | `supersonic_scheduler.py` |
| `founder_console/security_status.json` | Security audit results | Phase 1 |
| `founder_console/health_status.json` | System health metrics | Phase 2 |
| `founder_console/activity_timeline.json` | Event timeline | Phase 5 |

---

## 🎯 Use Cases

### Manual Testing
```bash
python3 supersonic_autodeploy.py
```
- Full console output for debugging
- Watch each phase execute
- Immediate feedback

### CI/CD Integration
```bash
# .github/workflows/autodeploy.yml
- name: Run silent deploy
  run: python3 supersonic_autodeploy_silent.py
```
- Minimal console spam
- All details in verify.log
- Machine-readable output

### Scheduled Deployment
```bash
# Start once, runs forever
nohup python3 supersonic_scheduler.py &
```
- Automatic deployment every 12 hours
- No manual intervention required
- Monitors GitHub availability

---

## 🔍 Verification

### Check Deployment Success

```bash
# View complete deployment log
cat verify.log

# Check last deployment
tail -20 verify.log

# Verify signature
cat docs/SIGNATURE.asc

# Verify checksums
sha256sum -c docs/SHA256.txt
```

### Monitor Scheduler

```bash
# Check if scheduler is running
ps aux | grep supersonic_scheduler

# View live logs
tail -f scheduler.log

# Check last cycle
tail -30 scheduler.log
```

---

## ⚠️ Troubleshooting

### Issue: "GITHUB_TOKEN not set"

**Solution:**
1. Go to Replit Secrets panel
2. Add secret: `GITHUB_TOKEN`
3. Value: Your GitHub Personal Access Token
4. Re-run script

### Issue: Scheduler stopped

**Check:**
```bash
ps aux | grep supersonic_scheduler
```

**Restart:**
```bash
nohup python3 supersonic_scheduler.py &
```

### Issue: Deployment failed

**Check logs:**
```bash
# Interactive deploy
cat verify.log

# Silent deploy
tail -50 verify.log

# Scheduler
tail -50 scheduler.log
```

---

## 🔐 Security Best Practices

1. **Never hardcode GITHUB_TOKEN** - Always use environment variables
2. **Review verify.log** - Check for unexpected changes
3. **Monitor scheduler.log** - Watch for failed cycles
4. **Verify checksums** - Run `sha256sum -c docs/SHA256.txt` regularly
5. **Check signatures** - Ensure `docs/SIGNATURE.asc` is up to date

---

## 📚 Integration with Existing Systems

The autodeploy scripts integrate seamlessly with:

- ✅ **supersonic/** - Uses setup_supersonic.py and security_patch.py
- ✅ **founder_autodeploy/** - Uses founder_autodeploy.py for git operations
- ✅ **setup/** - Builds all 5 bundles via package_all.py
- ✅ **founder_console/** - Updates health and security status JSON files

---

## 🎯 Comparison

| Feature | Interactive | Silent | Scheduler |
|---------|-------------|--------|-----------|
| Console output | Full | Minimal | Medium |
| Log file | verify.log | verify.log | scheduler.log + verify.log |
| Use case | Manual testing | CI/CD | Background daemon |
| User interaction | Required | None | None |
| Best for | Development | Automation | Production |

---

## 🚀 Next Steps

1. **Test interactive deploy:**
   ```bash
   python3 supersonic_autodeploy.py
   ```

2. **Set up GITHUB_TOKEN** in Replit Secrets

3. **Start scheduler for autonomous deployment:**
   ```bash
   nohup python3 supersonic_scheduler.py &
   ```

4. **Monitor logs:**
   ```bash
   tail -f scheduler.log
   ```

---

**Your SonicBuilder project now has complete autonomous deployment capabilities!** 🎉

Choose the script that fits your workflow:
- 🖥️  **Manual**: `python3 supersonic_autodeploy.py`
- 🤖 **Automated**: `python3 supersonic_autodeploy_silent.py`
- 🔄 **Continuous**: `nohup python3 supersonic_scheduler.py &`
