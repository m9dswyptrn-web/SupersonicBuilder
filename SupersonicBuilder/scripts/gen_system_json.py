#!/usr/bin/env python3
"""
System Health Summary Generator
Generates docs/status/system.json with complete system health info
"""

import json
import os
import hashlib
from datetime import datetime

def sha256sum(filename):
    """Calculate SHA256 checksum of a file"""
    try:
        h = hashlib.sha256()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return None

def load_json(path):
    """Load JSON file or return empty list"""
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return []
    return []

def main():
    version_file = "VERSION"
    branch_file = ".git/HEAD" if os.path.exists(".git/HEAD") else None
    heartbeat = "docs/status/heartbeat.json"
    uptime = "docs/status/uptime_log.json"
    pdf_dir = "docs_build"
    output = "docs/status/system.json"

    version = open(version_file).read().strip() if os.path.exists(version_file) else "2.0.9"
    branch = open(branch_file).read().strip().split('/')[-1] if branch_file else "main"
    
    heartbeat_ts = "unknown"
    if os.path.exists(heartbeat):
        hb_data = load_json(heartbeat)
        heartbeat_ts = hb_data.get("timestamp", "unknown") if isinstance(hb_data, dict) else "unknown"
    
    uptime_data = load_json(uptime)
    last_uptime = uptime_data[-1]["timestamp"] if uptime_data else "unknown"

    latest_pdf = None
    pdf_hash = None
    if os.path.exists(pdf_dir):
        pdfs = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
        if pdfs:
            pdfs.sort(key=lambda x: os.path.getmtime(os.path.join(pdf_dir, x)), reverse=True)
            latest_pdf = pdfs[0]
            pdf_hash = sha256sum(os.path.join(pdf_dir, latest_pdf))

    system = {
        "schemaVersion": 1,
        "label": "System",
        "message": "healthy" if heartbeat_ts != "unknown" else "unknown",
        "color": "brightgreen" if heartbeat_ts != "unknown" else "lightgrey",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "version": version,
        "branch": branch,
        "heartbeat": heartbeat_ts,
        "last_uptime_entry": last_uptime,
        "latest_pdf": latest_pdf,
        "pdf_checksum": pdf_hash,
        "status": "healthy" if heartbeat_ts != "unknown" else "unknown"
    }

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w") as f:
        json.dump(system, f, indent=2)
    print(f"✅ System health summary written: {output}")

if __name__ == "__main__":
    main()
