# SonicBuilder Webhook Listener Guide

Complete guide for the webhook controller that enables remote control of the SonicBuilder deployment system via HTTP API.

---

## 🚀 Overview

The webhook listener provides HTTP endpoints for:
- ✅ Pausing/resuming the autonomous scheduler
- ✅ Triggering manual deployments
- ✅ Checking scheduler status
- ✅ Viewing recent logs

This enables the Founder Dashboard to control deployments remotely from GitHub Pages.

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install flask flask-cors
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Start Webhook Listener

```bash
python3 founder_webhook_listener.py
```

**Default port:** 8080

---

## 🔧 Configuration

### Change Port

Set `PORT` environment variable:

```bash
PORT=5002 python3 founder_webhook_listener.py
```

Or in Replit Secrets:
```
PORT=5002
```

---

## 📡 API Endpoints

### GET `/`
**Service Information**

**Response:**
```json
{
  "service": "SonicBuilder Webhook Controller",
  "version": "2.0.9+ULTRA",
  "status": "online",
  "timestamp": "2025-10-31T01:00:00",
  "endpoints": {
    "GET /": "Service info",
    "GET /status": "Get scheduler status",
    "POST /pause": "Pause scheduler",
    "POST /resume": "Resume scheduler",
    "POST /deploy": "Trigger manual deploy"
  }
}
```

---

### GET `/status`
**Get Scheduler Status**

**Response:**
```json
{
  "status": "ok",
  "paused": false,
  "scheduler_running": true,
  "stats": {
    "total_cycles": 24,
    "successes": 23,
    "failures": 1
  },
  "scheduler_log": [
    "[2025-10-31 00:45:00 UTC] ═══ Cycle #24 ═══",
    "[2025-10-31 00:45:00 UTC] ✅ GitHub reachable",
    "[2025-10-31 00:45:05 UTC] ✅ Deployment succeeded"
  ],
  "verify_log": [
    "[2025-10-31 00:45:01 UTC] === Silent AutoDeploy Start ===",
    "[2025-10-31 00:45:05 UTC] === BUILD VERIFIED ==="
  ],
  "timestamp": "2025-10-31T01:00:00"
}
```

**Example:**
```bash
curl http://localhost:8080/status
```

---

### POST `/pause`
**Pause Scheduler**

Creates `pause.flag` file to pause the autonomous scheduler.

**Response:**
```json
{
  "status": "success",
  "action": "paused",
  "flag_created": "pause.flag",
  "message": "Scheduler will pause at next cycle check",
  "timestamp": "2025-10-31T01:00:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/pause
```

---

### POST `/resume`
**Resume Scheduler**

Removes `pause.flag` file to resume the autonomous scheduler.

**Response:**
```json
{
  "status": "success",
  "action": "resumed",
  "flag_removed": true,
  "message": "Scheduler will resume at next cycle",
  "timestamp": "2025-10-31T01:00:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/resume
```

---

### POST `/deploy`
**Trigger Manual Deploy**

Starts a background deployment using `supersonic_autodeploy_silent.py`.

**Response:**
```json
{
  "status": "success",
  "action": "deploy_triggered",
  "pid": 12345,
  "message": "Manual deployment started in background",
  "check_logs": "verify.log",
  "timestamp": "2025-10-31T01:00:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/deploy
```

---

### GET `/health`
**Health Check**

Simple health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "SonicBuilder Webhook Controller",
  "timestamp": "2025-10-31T01:00:00"
}
```

**Example:**
```bash
curl http://localhost:8080/health
```

---

## 🌐 Integration with Founder Dashboard

Update `docs/founder_dashboard.html` to use your Replit webhook URL:

```javascript
const WEBHOOK_URL = 'https://your-replit-name.username.repl.co';

function pause() {
  fetch(`${WEBHOOK_URL}/pause`, {method: 'POST'})
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      fetchStatus();
    })
    .catch(err => alert('Error: ' + err));
}

function resume() {
  fetch(`${WEBHOOK_URL}/resume`, {method: 'POST'})
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      fetchStatus();
    })
    .catch(err => alert('Error: ' + err));
}

function triggerDeploy() {
  fetch(`${WEBHOOK_URL}/deploy`, {method: 'POST'})
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      fetchStatus();
    })
    .catch(err => alert('Error: ' + err));
}
```

---

## 🚀 Deployment Options

### Option 1: Run as Workflow (Recommended for Replit)

1. Add workflow configuration:

```bash
# In Replit, add a new workflow
Name: Webhook Listener
Command: python3 founder_webhook_listener.py
Output Type: webview
Port: 8080
```

2. The webhook will be accessible at your Replit webview URL

### Option 2: Run in Background

```bash
nohup python3 founder_webhook_listener.py &
```

### Option 3: Run with Supervisor

Create `supervisor.conf`:
```ini
[program:webhook_listener]
command=python3 founder_webhook_listener.py
directory=/path/to/sonicbuilder
autostart=true
autorestart=true
```

---

## 🔐 Security Considerations

### 1. Add Authentication (Optional)

Add token-based authentication:

```python
@app.before_request
def check_auth():
    if request.endpoint not in ['root', 'health']:
        token = request.headers.get('Authorization')
        if token != f"Bearer {os.getenv('WEBHOOK_TOKEN')}":
            return jsonify({"error": "Unauthorized"}), 401
```

### 2. CORS Configuration

The listener uses `flask-cors` to allow requests from GitHub Pages.

To restrict to specific origins:

```python
CORS(app, origins=['https://m9dswyptrn-web.github.io'])
```

### 3. Rate Limiting

Add rate limiting for production:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])
```

---

## 📊 Monitoring

### Check if Webhook is Running

```bash
# Check process
ps aux | grep founder_webhook_listener

# Test endpoint
curl http://localhost:8080/health
```

### View Logs

```bash
# If running with nohup
tail -f nohup.out

# If running in foreground
# Logs appear in console
```

---

## ⚠️ Troubleshooting

### Issue: "Address already in use"

**Solution:** Change port
```bash
PORT=8081 python3 founder_webhook_listener.py
```

### Issue: CORS errors from dashboard

**Check:** flask-cors is installed
```bash
pip install flask-cors
```

### Issue: Webhook not accessible from dashboard

**Check:**
1. Webhook listener is running
2. Correct URL in dashboard
3. Firewall/network settings

---

## 🎯 Use Cases

### Remote Control

Control deployments from anywhere via the dashboard:
- Pause before maintenance
- Resume after fixes
- Trigger immediate deploy

### API Integration

Integrate with other tools:
```bash
# CI/CD pipeline
curl -X POST https://your-replit.repl.co/deploy

# Monitoring systems
curl https://your-replit.repl.co/health
```

### Dashboard Enhancement

The Founder Dashboard uses these endpoints for:
- Real-time status updates
- One-click pause/resume
- Manual deployment triggers

---

## 📝 Example Workflow

**Scenario:** Need to pause deployments during maintenance

1. **Via Dashboard:**
   - Click "⏸ Pause" button
   - Dashboard sends POST to `/pause`
   - Scheduler pauses at next cycle

2. **Via API:**
   ```bash
   curl -X POST http://localhost:8080/pause
   ```

3. **Do Maintenance:**
   - Make changes
   - Test locally

4. **Resume:**
   - Click "▶️ Resume" button
   - Dashboard sends POST to `/resume`
   - Scheduler resumes normal operation

---

## 🔗 Related Systems

The webhook listener integrates with:
- ✅ **supersonic_scheduler_ultra.py** - Reads/writes pause.flag
- ✅ **supersonic_autodeploy_silent.py** - Triggered for manual deploys
- ✅ **scheduler.log** - Status information source
- ✅ **verify.log** - Deployment verification
- ✅ **Founder Dashboard** - Primary consumer

---

## 🚀 Quick Reference

```bash
# Start webhook listener
python3 founder_webhook_listener.py

# Check status
curl http://localhost:8080/status

# Pause scheduler
curl -X POST http://localhost:8080/pause

# Resume scheduler
curl -X POST http://localhost:8080/resume

# Trigger deploy
curl -X POST http://localhost:8080/deploy

# Health check
curl http://localhost:8080/health
```

---

**Your SonicBuilder system now has complete remote control capabilities!** 🎉

Start the webhook listener and control deployments from the Founder Dashboard! 🚀
