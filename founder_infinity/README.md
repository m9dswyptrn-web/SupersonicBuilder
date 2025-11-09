# 🚀 SonicBuilder Infinity Suite

**Enterprise-grade autonomous deployment infrastructure with complete monitoring and control capabilities.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Dashboards](#dashboards)
- [Services](#services)
- [API Reference](#api-reference)
- [Deployment](#deployment)

---

## 🌟 Overview

The **SonicBuilder Infinity Suite** is a comprehensive deployment automation system that provides:

✅ **Real-time Monitoring** - Live dashboards for system status  
✅ **Automated Mirror Sync** - Hourly GitHub backups  
✅ **Dynamic Status Badges** - Visual health indicators  
✅ **One-Click Deployment** - Complete pipeline automation  
✅ **Security Audit Trail** - Complete event logging  
✅ **REST API Control** - Programmatic access to all features  

---

## 🏗️ Architecture

```
SonicBuilder Infinity Suite
├── Services (Background)
│   ├── Badge Engine (Port 8081)         - Dynamic SVG badges
│   ├── Mirror Sync                       - Hourly GitHub backups
│   └── AutoDeploy API (Port 8082)       - REST automation endpoints
│
├── Dashboards (Web UI)
│   ├── Command Deck                      - Control center + audit log
│   ├── Mirror Dashboard                  - Browse GitHub syncs
│   ├── Mirror Watchtower                 - Health monitoring + diffs
│   └── Infinity Console                  - One-click pipeline execution
│
├── Scripts (Automation)
│   ├── update_badges.py                  - Shields.io badge generation
│   └── deploy_pages.sh                   - GitHub Pages deployment
│
└── Integration
    └── Fortified+ Webhook Listener       - Main control API (Port 8080)
```

---

## 🧩 Components

### **Core Services**

1. **Fortified+ Webhook Listener** (Port 8080)
   - Main control API with 8 security features
   - Serves all dashboards via `/founder/*` routes
   - Complete REST API for scheduler control

2. **Badge Engine** (Port 8081)
   - Dynamic SVG status badge generation
   - Real-time system state detection
   - API key protected

3. **Mirror Sync Service**
   - Runs every 60 minutes
   - Backs up: `security_audit.json`, `scheduler.log`, `banned_ips.json`, `pause.flag`
   - Commits to GitHub branch: `founder_mirror`

4. **AutoDeploy API** (Port 8082)
   - `/autodeploy/mirror` - Trigger mirror sync
   - `/autodeploy/docs` - Rebuild documentation
   - `/autodeploy/deploy` - Deploy to GitHub Pages
   - `/autodeploy/refresh` - Update badges
   - `/autodeploy/full` - Execute complete pipeline

---

## 🚀 Quick Start

### **Prerequisites**

1. **Environment Variables** (Set in Replit Secrets):
   ```bash
   FOUNDER_API_KEY=SonicBuilder-2025-AlphaKey-42X!
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_REPO=username/repository
   DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
   ```

2. **Python Dependencies**:
   ```bash
   pip install flask flask-cors requests
   ```

### **Start All Services**

```bash
# Terminal 1: Main Webhook Listener (includes dashboards)
python3 founder_webhook_listener_fortified_persist.py

# Terminal 2: Badge Engine
python3 founder_infinity/services/badge_engine.py

# Terminal 3: AutoDeploy API
python3 founder_infinity/services/autodeploy_api.py

# Terminal 4: Mirror Sync (background)
nohup python3 founder_infinity/services/mirror_sync.py &

# Terminal 5: Scheduler ULTRA (autonomous deployment)
nohup python3 supersonic_scheduler_ultra.py &
```

### **Alternative: All-in-One Startup** (Recommended for production)

Create `start_infinity.sh`:
```bash
#!/bin/bash
python3 founder_webhook_listener_fortified_persist.py &
python3 founder_infinity/services/badge_engine.py &
python3 founder_infinity/services/autodeploy_api.py &
python3 founder_infinity/services/mirror_sync.py &
python3 supersonic_scheduler_ultra.py &
echo "🚀 SonicBuilder Infinity Suite started!"
```

---

## ⚙️ Configuration

### **GitHub Token Setup**

1. Go to GitHub Settings → Developer Settings → Personal Access Tokens
2. Create token with `repo` scope
3. Add to Replit Secrets as `GITHUB_TOKEN`

### **Discord Webhook Setup**

1. Go to Discord Server Settings → Integrations → Webhooks
2. Create new webhook
3. Copy URL and add to Replit Secrets as `DISCORD_WEBHOOK`

### **Founder API Key**

Set in Replit Secrets:
```
FOUNDER_API_KEY=SonicBuilder-2025-AlphaKey-42X!
```

(Or generate your own secure key)

---

## 🖥️ Dashboards

All dashboards are served via the main webhook listener:

### **Command Deck**
**URL:** `https://your-replit.repl.co/founder/command-deck`

**Features:**
- Real-time security audit log viewer
- Manual deploy trigger
- Pause/Resume scheduler
- View banned IPs
- Dynamic status badge display

### **Mirror Dashboard**
**URL:** `https://your-replit.repl.co/founder/mirror-dashboard`

**Features:**
- Browse all mirror sync commits
- View sync timestamps
- Link to GitHub commits
- Sync status indicators

### **Mirror Watchtower**
**URL:** `https://your-replit.repl.co/founder/watchtower`

**Features:**
- Mirror sync health monitoring
- Commit comparison/diff viewer
- Staleness detection
- Real-time health indicator

### **Infinity Console**
**URL:** `https://your-replit.repl.co/founder/infinity-console`

**Features:**
- One-click complete pipeline execution
- Real-time progress logging
- Sequential step execution
- Error handling and reporting

---

## 🔧 Services

### **Badge Engine**

**Start:**
```bash
python3 founder_infinity/services/badge_engine.py
```

**Endpoint:**
```
GET /badge/status.svg?key=<API_KEY>
```

**Status Detection:**
- 🟢 **Online** (green) - Normal operation
- 🟢 **Deployed** (green) - Successful deployment
- 🔵 **Generating** (blue) - PDF generation in progress
- 🟠 **Paused** (orange) - Scheduler paused
- 🔴 **Error** (red) - Error detected in logs

### **Mirror Sync Service**

**Start:**
```bash
python3 founder_infinity/services/mirror_sync.py
```

**Schedule:** Every 60 minutes

**Synced Files:**
- `security_audit.json` - Complete security audit trail
- `scheduler.log` - Deployment history
- `banned_ips.json` - IP ban list
- `pause.flag` - Pause state (if exists)

**GitHub Branch:** `founder_mirror`

### **AutoDeploy API**

**Start:**
```bash
python3 founder_infinity/services/autodeploy_api.py
```

**Endpoints:** (All require API key authentication)

```bash
# Trigger mirror sync
POST /autodeploy/mirror

# Rebuild documentation
POST /autodeploy/docs

# Deploy to GitHub Pages
POST /autodeploy/deploy

# Update badges
POST /autodeploy/refresh

# Execute full pipeline
POST /autodeploy/full
```

---

## 📡 API Reference

### **Webhook Listener API** (Port 8080)

#### **Public Endpoints**
```bash
GET  /                 # Service information
GET  /health           # Health check
```

#### **Protected Endpoints** (Require API key)
```bash
# Scheduler Control
GET  /status           # Get scheduler status
POST /pause            # Pause scheduler
POST /resume           # Resume scheduler
POST /deploy           # Trigger manual deployment

# Security Management
GET  /bans             # View banned IPs
POST /unban            # Remove IP from ban list
GET  /audit            # View security audit log

# Dashboards
GET  /founder/command-deck      # Command Deck UI
GET  /founder/mirror-dashboard  # Mirror Dashboard UI
GET  /founder/watchtower        # Watchtower UI
GET  /founder/infinity-console  # Infinity Console UI
```

#### **Authentication**

**Method 1: Header**
```bash
curl -H "X-API-KEY: your-api-key" https://your-replit.repl.co/status
```

**Method 2: Query Parameter**
```bash
curl "https://your-replit.repl.co/status?key=your-api-key"
```

---

## 🚢 Deployment

### **Complete Deployment Workflow**

1. **Manual Trigger via Dashboard:**
   - Visit Infinity Console: `https://your-replit.repl.co/founder/infinity-console`
   - Click "Execute Infinity Pipeline"

2. **API Trigger:**
   ```bash
   curl -X POST "https://your-replit.repl.co/autodeploy/full" \
     -H "X-API-KEY: your-api-key"
   ```

3. **Individual Steps:**
   ```bash
   # Mirror sync
   curl -X POST "https://your-replit.repl.co/autodeploy/mirror" \
     -H "X-API-KEY: your-api-key"

   # Rebuild docs
   curl -X POST "https://your-replit.repl.co/autodeploy/docs" \
     -H "X-API-KEY: your-api-key"

   # Deploy to Pages
   curl -X POST "https://your-replit.repl.co/autodeploy/deploy" \
     -H "X-API-KEY: your-api-key"

   # Update badges
   curl -X POST "https://your-replit.repl.co/autodeploy/refresh" \
     -H "X-API-KEY: your-api-key"
   ```

### **Badge Integration**

Add to your README.md:

```markdown
<!-- BADGES_START -->
![Last Updated](https://img.shields.io/badge/Last%20Updated-2025--01--01-brightgreen.svg)
![PDF Health](https://img.shields.io/badge/PDF%20Status-Healthy-brightgreen.svg)
![Pages](https://img.shields.io/badge/Pages-Deployed-blue.svg)
![Mirror](https://img.shields.io/badge/Mirror-Active-blueviolet.svg)
![Security](https://img.shields.io/badge/Security-Fort%20Infinity-red.svg)
<!-- BADGES_END -->
```

Or use dynamic badge:
```markdown
![SonicBuilder Status](https://your-replit.repl.co/badge/status.svg?key=your-api-key)
```

---

## 📊 Monitoring & Observability

### **Real-Time Monitoring**
- 🔔 **Discord Notifications** - All security events
- 📊 **Command Deck** - Live audit log viewer
- 🛰️ **Watchtower** - Mirror sync health

### **Historical Analysis**
- 🗂️ **security_audit.json** - Complete event timeline
- 📝 **scheduler.log** - Deployment history
- 🪞 **GitHub Mirror** - Off-site backup (branch: founder_mirror)

### **Status Indicators**
- 🎨 **Dynamic Badges** - Visual health status
- 💚 **Health Endpoints** - Programmatic checks
- 🚦 **Watchtower Lights** - Sync freshness monitoring

---

## 🔐 Security Features

1. ✅ **API Key Authentication** - Dual method (header/query)
2. ✅ **Rate Limiting** - 1 request per 10 seconds per IP
3. ✅ **Brute-Force Protection** - 5 attempt maximum
4. ✅ **Persistent IP Banning** - Survives restarts
5. ✅ **Discord Security Alerts** - Real-time notifications
6. ✅ **Ban List Viewing** - GET /bans endpoint
7. ✅ **Manual Unbanning** - POST /unban endpoint
8. ✅ **Security Audit Trail** - Complete event logging

---

## 🎯 Use Cases

### **For Developers**
- Continuous documentation deployment
- Automated backup of critical logs
- Real-time system monitoring
- One-click deployment pipeline

### **For DevOps**
- Infrastructure health monitoring
- Security audit trail
- Automated GitHub Pages deployment
- Off-site log backup

### **For Security Teams**
- Complete audit trail
- IP ban management
- Real-time security alerts
- Historical event analysis

---

## 📝 Troubleshooting

### **Mirror Sync Not Working**
1. Check `GITHUB_TOKEN` is set in Replit Secrets
2. Verify token has `repo` scope
3. Ensure `founder_mirror` branch exists on GitHub
4. Check Mirror Watchtower for sync health

### **Dashboards Not Loading**
1. Ensure main webhook listener is running
2. Check browser console for errors
3. Verify dashboard files exist in `founder_infinity/dashboards/`

### **Badge Not Updating**
1. Verify Badge Engine is running on port 8081
2. Check API key in badge URL is correct
3. Clear browser cache (badges use cache-control headers)

### **Deploy Failing**
1. Check `GITHUB_TOKEN` permissions
2. Ensure `docs_build/` directory exists
3. Verify `deploy_pages.sh` is executable
4. Review AutoDeploy API logs

---

## 🎉 Complete System Status

**Your SonicBuilder Infinity Suite includes:**

✅ 4 Interactive Dashboards  
✅ 3 Background Services  
✅ 2 Automation Scripts  
✅ 9 REST API Endpoints (Webhook Listener)  
✅ 5 AutoDeploy Endpoints  
✅ 8 Security Features  
✅ Complete Documentation  

---

## 📞 Support

For issues, questions, or feature requests, please check:

1. **Documentation** - This README
2. **Audit Logs** - `/founder/command-deck`
3. **Health Status** - `GET /health` endpoint
4. **Mirror Watchtower** - Sync health monitoring

---

**Built with 🧠 by SonicBuilder v2.0.9 — Fort-Infinity Edition**
