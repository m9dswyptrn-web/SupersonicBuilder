#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 FOUNDER-INFINITY-BADGE-ENGINE
-------------------------------------------------
Dynamic SVG badge generator for system status visualization.

Endpoints:
  GET /badge/status.svg?key=<API_KEY>  - System status badge
  
Status Detection:
  - Paused (orange) - pause.flag exists
  - Error (red) - Error in logs
  - Generating Docs (blue) - PDF generation in progress
  - Docs Ready (green) - Deployment complete
  - Online (green) - Normal operation

Requires:
  - FOUNDER_API_KEY (same as webhook listener)
"""

import os
import datetime
import re
from flask import Flask, make_response, request

app = Flask(__name__)

# Configuration
PAUSE_FLAG = "pause.flag"
STATUS_FILE = "scheduler.log"
AUDIT_LOG = "security_audit.json"
FOUNDER_API_KEY = os.getenv("FOUNDER_API_KEY")

def verify_api_key(req):
    """Verify API key from header or query parameter"""
    key = req.headers.get("X-API-KEY") or req.args.get("key")
    return key == FOUNDER_API_KEY if FOUNDER_API_KEY else False

def tail_file(filename, lines=20):
    """Read last N lines from file"""
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, 'r') as f:
            data = f.readlines()
        return data[-lines:]
    except Exception:
        return []

def detect_system_state():
    """Infer current system status from flags and logs"""
    # Check for pause flag
    if os.path.exists(PAUSE_FLAG):
        return "Paused", "orange"
    
    # Check scheduler logs
    log_lines = tail_file(STATUS_FILE)
    joined = " ".join(log_lines).lower()
    
    # Error detection
    if "error" in joined or "traceback" in joined or "failed" in joined:
        return "Error", "red"
    
    # PDF generation
    if re.search(r"pdf.?generat|building.*doc", joined):
        return "Generating", "blue"
    
    # Successful deployment
    if re.search(r"deploy|build complete|success|published", joined):
        return "Deployed", "green"
    
    # Default healthy state
    return "Online", "green"

@app.route("/badge/status.svg")
def status_badge():
    """Generate dynamic status badge"""
    if not verify_api_key(request):
        svg = generate_svg("Unauthorized", "darkred")
    else:
        status, color = detect_system_state()
        svg = generate_svg(status, color)
    
    resp = make_response(svg)
    resp.headers["Content-Type"] = "image/svg+xml"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

def generate_svg(status_text, color):
    """Generate SVG badge with status"""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='230' height='35'>
      <rect width='230' height='35' fill='{color}' rx='3'/>
      <text x='115' y='20' text-anchor='middle' fill='white'
            font-family='Arial, sans-serif' font-size='15' font-weight='bold'>
        SonicBuilder: {status_text}
      </text>
      <text x='115' y='32' text-anchor='middle' fill='white'
            font-family='Arial, sans-serif' font-size='9' opacity='0.9'>
        {timestamp}
      </text>
    </svg>"""

@app.route("/health")
def health():
    """Health check endpoint"""
    return {
        "service": "SonicBuilder Badge Engine",
        "status": "operational",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("BADGE_PORT", 8081))
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🎨 SonicBuilder Badge Engine v2.0.9                       ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nStarting badge engine on port {port}...")
    print(f"\nEndpoint:")
    print(f"  GET  http://0.0.0.0:{port}/badge/status.svg?key=<API_KEY>")
    print(f"  GET  http://0.0.0.0:{port}/health")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
