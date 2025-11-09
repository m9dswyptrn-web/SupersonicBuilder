#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 HARMONY FEED DASHBOARD
-------------------------------------------
Interactive web dashboard for monitoring Harmony feed health.
Provides visual status, manual refresh trigger, and real-time updates.

Access: http://your-replit.repl.co:8099/
"""

import os
import json
import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, redirect

# === CONFIGURATION ===
FEED_PATH = "harmony_feed.json"
FALLBACK_FEED_PATH = "docs/status/feed.json"
PDF_PATH = "docs_build/latest.pdf"
BADGE_PATH = "badges/feed_health.json"

CHECK_INTERVAL = 900  # 15 minutes
MAX_AGE_HOURS = 24

GITHUB_REPO = os.getenv("GITHUB_REPO", "m9dswyptrn-web/SonicBuilder")
GH_TOKEN = os.getenv("GITHUB_TOKEN")

# === Flask Setup ===
app = Flask(__name__)

# === HTML TEMPLATE ===
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SonicBuilder Feed Health Monitor</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: linear-gradient(135deg, #0e0e0e 0%, #1a1a2e 100%);
      color: #e6edf3;
      font-family: 'Courier New', monospace;
      padding: 20px;
      min-height: 100vh;
    }
    .container { max-width: 900px; margin: 0 auto; }
    h1 {
      color: #00ffcc;
      text-align: center;
      margin-bottom: 30px;
      font-size: 2em;
      text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);
    }
    .card {
      background: rgba(17, 17, 17, 0.8);
      border: 1px solid #333;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .status-indicator {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-right: 8px;
      animation: pulse 2s infinite;
    }
    .ok { background: #00ff00; }
    .warn { background: #ffaa00; }
    .bad { background: #ff4444; }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .stat-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid #222;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: #999; }
    .stat-value { color: #00ffcc; font-weight: bold; }
    .btn {
      background: linear-gradient(135deg, #111 0%, #222 100%);
      color: #00ffcc;
      border: 2px solid #00ffcc;
      padding: 12px 24px;
      cursor: pointer;
      margin-top: 10px;
      border-radius: 6px;
      font-size: 16px;
      font-family: 'Courier New', monospace;
      transition: all 0.3s ease;
      width: 100%;
    }
    .btn:hover {
      background: #00ffcc;
      color: #111;
      box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
      transform: translateY(-2px);
    }
    .btn:active { transform: translateY(0); }
    a {
      color: #00ffcc;
      text-decoration: none;
      border-bottom: 1px dashed #00ffcc;
    }
    a:hover { border-bottom: 1px solid #00ffcc; }
    .footer {
      text-align: center;
      color: #666;
      margin-top: 30px;
      font-size: 12px;
    }
    .countdown {
      background: rgba(0, 255, 204, 0.1);
      padding: 5px 10px;
      border-radius: 4px;
      display: inline-block;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 SonicBuilder Feed Health Monitor</h1>

    <!-- Feed Status Card -->
    <div class="card">
      <h2 style="color: #00ffcc; margin-bottom: 15px;">
        <span class="status-indicator {{status_class}}"></span>
        Feed Status: {{status_msg}}
      </h2>
      <div class="stat-row">
        <span class="stat-label">Last Feed Update:</span>
        <span class="stat-value">{{last_time or 'N/A'}}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Feed Age:</span>
        <span class="stat-value">{{hours_old}}h old</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Health Threshold:</span>
        <span class="stat-value">{{max_age}}h maximum</span>
      </div>
      <form action="/trigger" method="post">
        <button class="btn">🔁 Trigger GitHub Refresh Now</button>
      </form>
    </div>

    <!-- PDF Status Card -->
    <div class="card">
      <h2 style="color: #00ffcc; margin-bottom: 15px;">📄 Documentation Build</h2>
      <div class="stat-row">
        <span class="stat-label">Latest PDF:</span>
        <span class="stat-value">{{latest_pdf}}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">PDF Age:</span>
        <span class="stat-value">{{pdf_age}}h</span>
      </div>
      {% if latest_pdf_url %}
      <div style="margin-top: 10px;">
        <a href="{{latest_pdf_url}}" target="_blank">→ Open Latest PDF</a>
      </div>
      {% endif %}
    </div>

    <!-- Deployment Info Card -->
    <div class="card">
      <h2 style="color: #00ffcc; margin-bottom: 15px;">🌐 GitHub Pages</h2>
      <div class="stat-row">
        <span class="stat-label">Last Deploy:</span>
        <span class="stat-value">{{last_deploy or 'Unknown'}}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Feed Mirror:</span>
        <span class="stat-value">
          <a href="https://{{github_owner}}.github.io/SonicBuilder/status/feed.json" target="_blank">
            View JSON
          </a>
        </span>
      </div>
    </div>

    <!-- Auto-Refresh Card -->
    <div class="card">
      <div class="stat-row">
        <span class="stat-label">Next Auto-Check:</span>
        <span class="stat-value">
          <span class="countdown" id="countdown">{{next_refresh}}s</span>
        </span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Page Refresh:</span>
        <span class="stat-value">Every 30 seconds</span>
      </div>
    </div>

    <div class="footer">
      <p>SonicBuilder v2.0.9 — Harmony Feed Dashboard</p>
      <p>Last refresh: {{now}}</p>
    </div>
  </div>

  <script>
    let t = {{next_refresh}};
    setInterval(() => {
      if (t > 0) {
        t--;
        document.getElementById("countdown").textContent = t + "s";
      }
    }, 1000);
    
    // Auto-refresh page every 30 seconds
    setTimeout(() => location.reload(), 30000);
  </script>
</body>
</html>
"""

# === HELPER FUNCTIONS ===
def load_feed_time():
    """Get timestamp of last feed entry"""
    feed_path = FEED_PATH if os.path.exists(FEED_PATH) else FALLBACK_FEED_PATH
    
    if not os.path.exists(feed_path):
        return None
    
    try:
        with open(feed_path) as f:
            data = json.load(f)
        
        if not data:
            return None
        
        last_entry = data[-1]["timestamp"] if data else None
        if last_entry:
            return datetime.strptime(last_entry, "%Y-%m-%d %H:%M:%S UTC")
    except Exception as e:
        print(f"Error loading feed: {e}")
        return None

def get_pdf_age():
    """Get PDF age in hours"""
    if not os.path.exists(PDF_PATH):
        return 999
    return round((time.time() - os.path.getmtime(PDF_PATH)) / 3600, 1)

def trigger_github_refresh(reason):
    """Trigger GitHub Actions workflow"""
    if not GH_TOKEN:
        print("❌ Missing GITHUB_TOKEN")
        return False
    
    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "event_type": "feed_badge_refresh",
        "client_payload": {
            "reason": reason,
            "source": "Dashboard Manual Trigger"
        }
    }
    
    try:
        resp = requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/dispatches",
            headers=headers,
            json=payload,
            timeout=10
        )
        return resp.status_code == 204
    except Exception as e:
        print(f"Error triggering GitHub: {e}")
        return False

# === ROUTES ===
@app.route("/")
def index():
    """Main dashboard page"""
    ts = load_feed_time()
    pdf_age = get_pdf_age()
    
    # Determine feed status
    if ts:
        delta = datetime.utcnow() - ts
        hours = round(delta.total_seconds() / 3600, 1)
        
        if hours < MAX_AGE_HOURS:
            status_class = "ok"
            status_msg = f"Healthy ({hours}h old)"
        else:
            status_class = "bad"
            status_msg = f"Stale ({hours}h old)"
    else:
        hours = "N/A"
        status_class = "warn"
        status_msg = "Missing Feed"
    
    # Get GitHub owner from repo
    github_owner = GITHUB_REPO.split("/")[0] if "/" in GITHUB_REPO else "unknown"
    
    return render_template_string(
        html_template,
        last_time=ts.strftime("%Y-%m-%d %H:%M:%S UTC") if ts else None,
        hours_old=hours,
        status_class=status_class,
        status_msg=status_msg,
        max_age=MAX_AGE_HOURS,
        latest_pdf="SonicBuilder_Manual_v2.0.9.pdf",
        pdf_age=pdf_age,
        latest_pdf_url=f"https://{github_owner}.github.io/SonicBuilder/latest.pdf",
        last_deploy=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        next_refresh=CHECK_INTERVAL,
        github_owner=github_owner,
        now=datetime.utcnow().strftime("%H:%M:%S UTC")
    )

@app.route("/trigger", methods=["POST"])
def trigger():
    """Handle manual trigger button"""
    success = trigger_github_refresh("manual_dashboard")
    
    if success:
        print("✅ GitHub refresh triggered from dashboard")
    else:
        print("❌ Failed to trigger GitHub refresh")
    
    # Redirect back to dashboard with a brief delay
    return '<html><head><meta http-equiv="refresh" content="2;url=/" /></head><body style="background:#0e0e0e;color:#00ffcc;font-family:monospace;text-align:center;padding:100px;"><h1>✅ Refresh Triggered!</h1><p>Redirecting back to dashboard...</p></body></html>'

@app.route("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "feed_dashboard", "version": "2.0.9"}

# === BACKGROUND MONITOR ===
def background_monitor():
    """Background thread that monitors feed health"""
    print("🔄 Background monitor started")
    
    while True:
        try:
            ts = load_feed_time()
            
            if ts:
                delta = datetime.utcnow() - ts
                hours = delta.total_seconds() / 3600
                
                if hours > MAX_AGE_HOURS:
                    print(f"⚠️  Feed stale ({hours:.1f}h) — triggering auto-refresh")
                    trigger_github_refresh("auto_stale")
                else:
                    print(f"✅ Feed healthy ({hours:.1f}h old)")
            else:
                print("⚠️  Feed missing — triggering auto-refresh")
                trigger_github_refresh("auto_missing")
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"❌ Error in background monitor: {e}")
            time.sleep(60)

# === MAIN ===
if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   📊 SonicBuilder Feed Dashboard v2.0.9                       ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print("")
    print(f"🌐 Starting dashboard on port 8099...")
    print(f"📋 GitHub Repo: {GITHUB_REPO}")
    print(f"🔑 GitHub Token: {'✅ Set' if GH_TOKEN else '❌ Missing'}")
    print("")
    
    # Start background monitor
    monitor_thread = threading.Thread(target=background_monitor, daemon=True)
    monitor_thread.start()
    
    # Start Flask app on port 8099 (Replit-compatible port)
    app.run(host="0.0.0.0", port=8099, debug=False)
