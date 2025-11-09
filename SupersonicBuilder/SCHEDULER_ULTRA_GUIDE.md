# SonicBuilder Scheduler ULTRA Guide

Complete guide for the autonomous scheduler with Discord notifications, pause control, and advanced features.

---

## 🚀 Features

- ✅ **Discord Notifications** - Real-time deployment updates
- ✅ **Pause Control** - Pause/resume with a simple flag file
- ✅ **Adjustable Interval** - Configure deployment frequency
- ✅ **Heartbeat Monitoring** - GitHub availability checks
- ✅ **Statistics Tracking** - Success/failure counts
- ✅ **Graceful Shutdown** - Clean exit with Ctrl+C

---

## 📦 Setup

### 1. Install Dependencies (Optional)

For Discord notifications:
```bash
pip install requests
```

**Note:** If `requests` is not installed, Discord notifications will be disabled but the scheduler will still work.

### 2. Set Environment Variables

In **Replit Secrets** panel, add:

| Secret | Required | Purpose |
|--------|----------|---------|
| `GITHUB_TOKEN` | Yes | Git push authentication |
| `DISCORD_WEBHOOK` | No | Discord notifications |
| `SB_INTERVAL_HOURS` | No | Deploy interval (default: 12) |

**Example Discord Webhook:**
1. Go to Discord Server Settings → Integrations → Webhooks
2. Click "New Webhook"
3. Copy webhook URL
4. Add to Replit Secrets as `DISCORD_WEBHOOK`

---

## 🚀 Quick Start

### Start Scheduler

```bash
# Start in background
nohup python3 supersonic_scheduler_ultra.py &

# View PID
echo $!
```

### Check Status

```bash
# Check if running
ps aux | grep supersonic_scheduler_ultra

# View live logs
tail -f scheduler.log

# View last 50 lines
tail -50 scheduler.log
```

### Stop Scheduler

```bash
# Find process
ps aux | grep supersonic_scheduler_ultra

# Kill by name
pkill -f supersonic_scheduler_ultra.py

# Or use Ctrl+C if running in foreground
```

---

## ⏸️ Pause Control

### Pause Scheduler

```bash
touch pause.flag
```

The scheduler will:
- Skip deployment cycles
- Check every 10 minutes for flag removal
- Send Discord notification (if configured)

### Resume Scheduler

```bash
rm pause.flag
```

The scheduler will:
- Resume normal deployment cycles
- Continue at next scheduled interval

---

## 🔧 Configuration

### Adjust Deploy Interval

Set `SB_INTERVAL_HOURS` in Replit Secrets:

| Value | Frequency |
|-------|-----------|
| `1` | Every hour |
| `6` | Every 6 hours |
| `12` | Every 12 hours (default) |
| `24` | Once per day |

**Example:**
```bash
# In Replit Secrets
SB_INTERVAL_HOURS=6
```

---

## 📊 Discord Notifications

### Notification Types

| Event | Color | Example |
|-------|-------|---------|
| **Scheduler Started** | Blue (0x00AAFF) | 🟢 Scheduler ULTRA online |
| **Deploy Success** | Green (0x00FF00) | ✅ Deployment succeeded in 3.2s |
| **Deploy Failed** | Red (0xFF0000) | ❌ Deployment FAILED (exit 1) |
| **GitHub Unreachable** | Orange (0xFFA500) | ⚠️ GitHub unreachable |
| **Paused** | Gray (0xAAAAAA) | ⏸️ Scheduler paused |
| **Sleeping** | Purple (0x6666FF) | 💤 Sleeping for 12 hours |
| **Stopped** | Orange (0xFF6600) | 🛑 Scheduler stopped |
| **Crashed** | Red (0xFF0000) | 🔥 Scheduler crashed! |

### Example Discord Message

```
⚡ SonicBuilder Deployment Update

✅ SonicBuilder deployment succeeded in 3.2s

SonicBuilder v2.0.9 • 2025-10-31 01:00 UTC
```

---

## 📝 Log Files

### scheduler.log

Complete scheduler activity log with timestamps:

```
[2025-10-31 00:45:00 UTC] ╔════════════════════════════════════════════════════════════════╗
[2025-10-31 00:45:00 UTC] ║     🚀 SonicBuilder Autonomous Scheduler ULTRA                ║
[2025-10-31 00:45:00 UTC] ╚════════════════════════════════════════════════════════════════╝
[2025-10-31 00:45:00 UTC] Interval: 12.0 hours
[2025-10-31 00:45:00 UTC] Silent script: supersonic_autodeploy_silent.py
[2025-10-31 00:45:00 UTC] Pause flag: pause.flag
[2025-10-31 00:45:00 UTC] Discord notifications: Enabled
[2025-10-31 00:45:00 UTC] Log file: scheduler.log
[2025-10-31 00:45:00 UTC] 
[2025-10-31 00:45:00 UTC] ═══ Cycle #1 ═══
[2025-10-31 00:45:00 UTC] ✅ GitHub reachable, starting deploy cycle
[2025-10-31 00:45:00 UTC] 🚀 Starting silent auto-deploy...
[2025-10-31 00:45:05 UTC] ✅ SonicBuilder deployment succeeded in 4.8s
[2025-10-31 00:45:05 UTC] 📊 Stats: 1 successes, 0 failures
[2025-10-31 00:45:05 UTC] Next deploy cycle: 2025-10-31 12:45:05 UTC
[2025-10-31 00:45:05 UTC] 💤 Sleeping for 12.0 hours...
```

### verify.log

Silent autodeploy output (updated each cycle):

```
[2025-10-31 00:45:01 UTC] === Silent AutoDeploy Start ===
[2025-10-31 00:45:02 UTC] Running security patch...
[2025-10-31 00:45:03 UTC] Security patch complete
[2025-10-31 00:45:03 UTC] Building bundles...
[2025-10-31 00:45:05 UTC] Bundles built: 5/5
[2025-10-31 00:45:05 UTC] Signature: 2.0.9-SB-ULTRA
[2025-10-31 00:45:05 UTC] === BUILD VERIFIED ===
[2025-10-31 00:45:05 UTC] === Silent AutoDeploy Complete ===
```

---

## 🎯 Use Cases

### Production Deployment

```bash
# Set 12-hour interval, enable Discord
# In Replit Secrets:
#   GITHUB_TOKEN=<your_token>
#   DISCORD_WEBHOOK=<your_webhook>
#   SB_INTERVAL_HOURS=12

nohup python3 supersonic_scheduler_ultra.py &
```

### Rapid Development

```bash
# Set 1-hour interval for frequent testing
# In Replit Secrets:
#   SB_INTERVAL_HOURS=1

nohup python3 supersonic_scheduler_ultra.py &
```

### Maintenance Window

```bash
# Pause during maintenance
touch pause.flag

# Do maintenance work...

# Resume after maintenance
rm pause.flag
```

---

## 🔍 Monitoring

### Check Scheduler Health

```bash
# Is it running?
ps aux | grep supersonic_scheduler_ultra

# Recent activity?
tail -20 scheduler.log

# Latest deployment?
tail -10 verify.log

# Success rate?
grep "Stats:" scheduler.log | tail -1
```

### Monitor Via Discord

All deployment events are sent to Discord webhook:
- Deployment success/failure
- GitHub availability issues
- Pause/resume events
- Scheduler start/stop

---

## ⚠️ Troubleshooting

### Issue: No Discord Notifications

**Check:**
1. Is `DISCORD_WEBHOOK` set in Replit Secrets?
2. Is webhook URL valid?
3. Is `requests` package installed?

**Solution:**
```bash
pip install requests
```

### Issue: Scheduler Not Running

**Check:**
```bash
ps aux | grep supersonic_scheduler_ultra
```

**Restart:**
```bash
pkill -f supersonic_scheduler_ultra.py
nohup python3 supersonic_scheduler_ultra.py &
```

### Issue: Deployment Failures

**Check logs:**
```bash
# Scheduler log
tail -50 scheduler.log

# Deploy log
tail -50 verify.log
```

**Common causes:**
- GITHUB_TOKEN not set
- Network issues
- GitHub API rate limits
- Bundle build failures

### Issue: Pause Flag Not Working

**Check:**
```bash
ls -la pause.flag
```

**Create:**
```bash
touch pause.flag
```

**Remove:**
```bash
rm pause.flag
```

---

## 📊 Statistics

The scheduler tracks:
- **Cycle count** - Total deployment cycles
- **Success count** - Successful deployments
- **Failure count** - Failed deployments

**View stats:**
```bash
grep "Stats:" scheduler.log | tail -1
```

**Example output:**
```
📊 Stats: 24 successes, 1 failures
```

---

## 🔐 Security Best Practices

1. **Never hardcode secrets** - Always use environment variables
2. **Use Replit Secrets** - Store GITHUB_TOKEN and DISCORD_WEBHOOK securely
3. **Monitor logs** - Check for suspicious activity
4. **Verify webhooks** - Ensure Discord webhook is private
5. **Review deployments** - Check verify.log regularly

---

## 🎯 Comparison with Basic Scheduler

| Feature | Basic Scheduler | Scheduler ULTRA |
|---------|----------------|-----------------|
| Discord Notifications | ❌ | ✅ |
| Pause Control | ❌ | ✅ |
| Adjustable Interval | ❌ | ✅ (via env var) |
| Statistics Tracking | ❌ | ✅ |
| Deployment Metrics | ❌ | ✅ (duration tracking) |
| Error Reporting | Basic | Enhanced + Discord |
| Heartbeat Monitoring | Basic | Enhanced |

---

## 🚀 Advanced Usage

### Custom Interval During Runtime

You can't change interval while running, but you can:

1. Stop scheduler:
   ```bash
   pkill -f supersonic_scheduler_ultra.py
   ```

2. Update `SB_INTERVAL_HOURS` in Replit Secrets

3. Restart scheduler:
   ```bash
   nohup python3 supersonic_scheduler_ultra.py &
   ```

### Multiple Schedulers

Run different intervals for different purposes:

```bash
# Production (12 hours)
SB_INTERVAL_HOURS=12 nohup python3 supersonic_scheduler_ultra.py &

# Not recommended - one scheduler is enough
```

---

## 📝 Example Workflow

**Day 1:**
```bash
# Initial setup
1. Add GITHUB_TOKEN to Replit Secrets
2. Add DISCORD_WEBHOOK to Replit Secrets
3. Set SB_INTERVAL_HOURS=12
4. Start: nohup python3 supersonic_scheduler_ultra.py &
```

**Day 2:**
```bash
# Check status
tail -f scheduler.log
# See Discord notifications
```

**Day 3:**
```bash
# Maintenance needed
touch pause.flag
# Do maintenance...
rm pause.flag
```

**Ongoing:**
```bash
# Monitor via Discord
# Check scheduler.log occasionally
# Review verify.log for deployment details
```

---

**Your SonicBuilder project now has enterprise-grade autonomous deployment with Discord integration!** 🎉

Start with:
```bash
nohup python3 supersonic_scheduler_ultra.py &
```

Monitor via Discord and logs. Enjoy hands-free deployment! 🚀
