#!/usr/bin/env python3
"""
SonicBuilder Sync Monitor Dashboard
v2.0.9 — Flask dashboard to visualize sync, health, and CI/CD telemetry
"""

from flask import Flask, render_template_string, jsonify
import subprocess, json, os, datetime, threading, time

app = Flask(__name__)

status_cache = {
    "last_pull": None,
    "last_push": None,
    "branch": "main",
    "health": {"status": "unknown"},
    "sync_active": False,
    "commit": "unknown",
    "updated": None
}

# HTML template
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>🚀 SonicBuilder Sync Dashboard</title>
<style>
body { background-color: #0b0c10; color: #66fcf1; font-family: monospace; margin: 20px; }
h1 { color: #45a29e; }
.card { background: #1f2833; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
.badge { color: #0b0c10; padding: 4px 10px; border-radius: 4px; font-weight: bold; }
.success { background: #66fcf1; }
.warning { background: #ffd700; }
.danger { background: #ff4c4c; }
</style>
</head>
<body>
<h1>🧭 SonicBuilder Sync Monitor</h1>
<div class="card"><b>Branch:</b> {{ data.branch }}</div>
<div class="card"><b>Commit:</b> {{ data.commit }}</div>
<div class="card"><b>Last Pull:</b> {{ data.last_pull }}</div>
<div class="card"><b>Last Push:</b> {{ data.last_push }}</div>
<div class="card"><b>Health:</b>
    {% if data.health.status == 'ok' or data.health.status == 'patched' %}
        <span class="badge success">{{ data.health.status }}</span>
    {% else %}
        <span class="badge danger">{{ data.health.status }}</span>
    {% endif %}
</div>
<div class="card"><b>Sync Active:</b> {{ "🟢 Yes" if data.sync_active else "🔴 No" }}</div>
<div class="card"><b>Last Updated:</b> {{ data.updated }}</div>
<hr>
<small>Auto-refresh every 10s</small>
<script>
setTimeout(()=>window.location.reload(), 10000);
</script>
</body>
</html>
"""

def update_status():
    while True:
        try:
            # Git branch and commit
            branch = subprocess.run("git rev-parse --abbrev-ref HEAD", shell=True, text=True, capture_output=True).stdout.strip()
            commit = subprocess.run("git rev-parse --short HEAD", shell=True, text=True, capture_output=True).stdout.strip()
            status_cache["branch"] = branch or "unknown"
            status_cache["commit"] = commit or "unknown"

            # Health
            health_path = "docs/status/health.json"
            if os.path.exists(health_path):
                with open(health_path) as f:
                    status_cache["health"] = json.load(f)
            else:
                status_cache["health"] = {"status": "missing"}

            status_cache["updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            status_cache["sync_active"] = True
        except Exception as e:
            status_cache["health"] = {"status": f"error: {e}"}
        time.sleep(10)

@app.route("/")
def index():
    return render_template_string(TEMPLATE, data=status_cache)

@app.route("/api/status")
def api_status():
    return jsonify(status_cache)

def run_dashboard():
    threading.Thread(target=update_status, daemon=True).start()
    port = int(os.getenv("SYNC_MONITOR_PORT", "8094"))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    port = int(os.getenv("SYNC_MONITOR_PORT", "8094"))
    print(f"🚀 SonicBuilder Sync Monitor running on http://localhost:{port}")
    run_dashboard()