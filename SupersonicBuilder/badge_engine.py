#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 BADGE ENGINE
---------------------------------
Dynamic status badge API with auto-updating SVG.
Provides real-time status badges for monitoring.

Endpoints:
  /badge/status.svg - System status badge
  /badge/health.svg - Health feed badge
  /badge/uptime.svg - Uptime badge
"""

import os
import json
import datetime
from flask import Flask, send_file, make_response, request

app = Flask(__name__)

def _make_svg(label, value, color):
    """Generate SVG badge"""
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    # Calculate widths
    label_width = len(label) * 7 + 10
    value_width = len(value) * 7 + 10
    total_width = label_width + value_width
    
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{total_width}' height='20'>
      <linearGradient id='smooth' x2='0' y2='100%'>
        <stop offset='0' stop-color='#bbb' stop-opacity='.1'/>
        <stop offset='1' stop-opacity='.1'/>
      </linearGradient>
      <rect rx='3' width='{total_width}' height='20' fill='#555'/>
      <rect rx='3' x='{label_width}' width='{value_width}' height='20' fill='{color}'/>
      <path fill='{color}' d='M{label_width} 0h4v20h-4z'/>
      <rect rx='3' width='{total_width}' height='20' fill='url(#smooth)'/>
      <g fill='#fff' text-anchor='middle' font-family='DejaVu Sans,Verdana,Geneva,sans-serif' font-size='11'>
        <text x='{label_width/2}' y='15' fill='#010101' fill-opacity='.3'>{label}</text>
        <text x='{label_width/2}' y='14'>{label}</text>
        <text x='{label_width + value_width/2}' y='15' fill='#010101' fill-opacity='.3'>{value}</text>
        <text x='{label_width + value_width/2}' y='14'>{value}</text>
      </g>
    </svg>"""

@app.route("/badge/status.svg")
def badge_status():
    """System status badge"""
    # Check if auto-healer is active
    if os.path.exists("badges/auto_healer_status.json"):
        try:
            with open("badges/auto_healer_status.json") as f:
                data = json.load(f)
                status = data.get("message", "unknown")
                color = "#4c1" if status == "active" else "#fe7d37"
        except:
            status = "unknown"
            color = "#9f9f9f"
    else:
        status = "unknown"
        color = "#9f9f9f"
    
    svg = _make_svg("SonicBuilder", status, color)
    response = make_response(svg)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/badge/health.svg")
def badge_health():
    """Health feed badge"""
    if os.path.exists("docs/status/health.json"):
        try:
            with open("docs/status/health.json") as f:
                data = json.load(f)
                status = data.get("status", "unknown")
                color = "#4c1" if status == "success" else "#e05d44"
        except:
            status = "error"
            color = "#e05d44"
    else:
        status = "no data"
        color = "#9f9f9f"
    
    svg = _make_svg("Health", status, color)
    response = make_response(svg)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/badge/uptime.svg")
def badge_uptime():
    """Uptime badge"""
    if os.path.exists("docs/status/uptime_log.json"):
        try:
            with open("docs/status/uptime_log.json") as f:
                data = json.load(f)
                count = len(data)
                value = f"{count} pings"
                color = "#4c1"
        except:
            value = "error"
            color = "#e05d44"
    else:
        value = "no data"
        color = "#9f9f9f"
    
    svg = _make_svg("Uptime", value, color)
    response = make_response(svg)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "badge_engine", "version": "2.0.9"}

if __name__ == "__main__":
    port = int(os.getenv("BADGE_PORT", 8081))
    print(f"🏷️  Badge Engine starting on port {port}...")
    print(f"   /badge/status.svg - System status")
    print(f"   /badge/health.svg - Health feed")
    print(f"   /badge/uptime.svg - Uptime tracking")
    app.run(host="0.0.0.0", port=port, debug=False)
