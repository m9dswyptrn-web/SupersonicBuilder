#!/usr/bin/env python3
"""
SonicBuilder Founder Console
Real-time monitoring dashboard for deployment health, security status, and activity timeline
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
VERSION = "2.0.9"

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SonicBuilder Founder Console v{{ version }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid rgba(255,255,255,0.2);
            margin-bottom: 30px;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.8; font-size: 1.1em; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-success { background: #4ade80; }
        .status-warning { background: #fbbf24; }
        .status-error { background: #ef4444; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric:last-child { border-bottom: none; }
        .metric-value {
            font-weight: bold;
            font-size: 1.1em;
        }
        .timeline {
            max-height: 400px;
            overflow-y: auto;
        }
        .timeline-item {
            padding: 10px;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            border-left: 3px solid #4ade80;
        }
        .timeline-time {
            font-size: 0.85em;
            opacity: 0.7;
        }
        .refresh-btn {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
        }
        .refresh-btn:hover {
            background: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 SonicBuilder Founder Console</h1>
            <p class="subtitle">Version {{ version }} • Real-time System Monitoring</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        </header>
        
        <div class="grid">
            <div class="card">
                <h2>
                    <span class="status-indicator status-success"></span>
                    System Health
                </h2>
                <div id="health-metrics"></div>
            </div>
            
            <div class="card">
                <h2>
                    <span class="status-indicator status-success"></span>
                    Security Status
                </h2>
                <div id="security-metrics"></div>
            </div>
            
            <div class="card">
                <h2>
                    <span class="status-indicator status-success"></span>
                    Bundle Status
                </h2>
                <div id="bundle-metrics"></div>
            </div>
        </div>
        
        <div class="card">
            <h2>📊 Activity Timeline</h2>
            <div class="timeline" id="timeline"></div>
        </div>
    </div>
    
    <script>
        async function loadData() {
            try {
                const health = await fetch('/api/health').then(r => r.json());
                const security = await fetch('/api/security').then(r => r.json());
                const timeline = await fetch('/api/timeline').then(r => r.json());
                
                renderHealth(health);
                renderSecurity(security);
                renderTimeline(timeline);
            } catch (e) {
                console.error('Failed to load data:', e);
            }
        }
        
        function renderHealth(data) {
            const container = document.getElementById('health-metrics');
            const verified = data.secrets?.verified ? '✅ Verified' : '❌ Missing';
            const bundleCount = Object.values(data.bundles || {}).filter(Boolean).length;
            
            container.innerHTML = `
                <div class="metric">
                    <span>Python Version</span>
                    <span class="metric-value">${data.environment?.python_version || 'N/A'}</span>
                </div>
                <div class="metric">
                    <span>Secrets</span>
                    <span class="metric-value">${verified}</span>
                </div>
                <div class="metric">
                    <span>Bundles Built</span>
                    <span class="metric-value">${bundleCount}/5</span>
                </div>
                <div class="metric">
                    <span>Last Update</span>
                    <span class="metric-value">${new Date(data.timestamp).toLocaleTimeString()}</span>
                </div>
            `;
        }
        
        function renderSecurity(data) {
            const container = document.getElementById('security-metrics');
            const summary = data.summary || {};
            
            container.innerHTML = `
                <div class="metric">
                    <span>Total Checks</span>
                    <span class="metric-value">${summary.total || 0}</span>
                </div>
                <div class="metric">
                    <span>✅ Fixed</span>
                    <span class="metric-value">${summary.fixed || 0}</span>
                </div>
                <div class="metric">
                    <span>✓ Verified</span>
                    <span class="metric-value">${summary.verified || 0}</span>
                </div>
                <div class="metric">
                    <span>⚠️ Warnings</span>
                    <span class="metric-value">${summary.warnings || 0}</span>
                </div>
            `;
        }
        
        function renderTimeline(data) {
            const container = document.getElementById('timeline');
            
            if (!data || data.length === 0) {
                container.innerHTML = '<p style="opacity: 0.5; text-align: center;">No activity yet</p>';
                return;
            }
            
            container.innerHTML = data.slice(-10).reverse().map(event => {
                const time = new Date(event.timestamp).toLocaleString();
                const icon = event.status === 'success' ? '✅' : '⚠️';
                return `
                    <div class="timeline-item">
                        <div><strong>${icon} ${event.type}</strong></div>
                        <div>${event.message}</div>
                        <div class="timeline-time">${time}</div>
                    </div>
                `;
            }).join('');
        }
        
        loadData();
        setInterval(loadData, 30000);  // Refresh every 30 seconds
    </script>
</body>
</html>
"""

def load_json_file(filepath, default=None):
    """Load JSON file with fallback"""
    path = Path(filepath)
    if not path.exists():
        return default or {}
    
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default or {}

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template_string(DASHBOARD_HTML, version=VERSION)

@app.route('/api/health')
def api_health():
    """Health status endpoint"""
    data = load_json_file('founder_console/health_status.json', {
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": {"python_version": "3.11.0"},
        "secrets": {"verified": False},
        "bundles": {}
    })
    return jsonify(data)

@app.route('/api/security')
def api_security():
    """Security status endpoint"""
    data = load_json_file('founder_console/security_status.json', {
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {"total": 0, "fixed": 0, "verified": 0, "warnings": 0}
    })
    return jsonify(data)

@app.route('/api/timeline')
def api_timeline():
    """Activity timeline endpoint"""
    data = load_json_file('founder_console/activity_timeline.json', [])
    return jsonify(data)

@app.route('/api/status')
def api_status():
    """Overall system status"""
    health = load_json_file('founder_console/health_status.json')
    security = load_json_file('founder_console/security_status.json')
    
    return jsonify({
        "status": "operational",
        "version": VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "health": health,
        "security": security
    })

if __name__ == '__main__':
    print(f"╔════════════════════════════════════════════════════════════════╗")
    print(f"║     🚀 SonicBuilder Founder Console v{VERSION}                 ║")
    print(f"╚════════════════════════════════════════════════════════════════╝\n")
    print(f"Starting dashboard on http://0.0.0.0:5001")
    print(f"Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
