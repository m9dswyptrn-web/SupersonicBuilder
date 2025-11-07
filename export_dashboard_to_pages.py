#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 HARMONY DASHBOARD EXPORTER
----------------------------------------------
Exports Harmony dashboard HTML snapshot to GitHub Pages directory.

This allows the dashboard to be accessible from GitHub Pages even
when the Replit instance is offline.
"""

import os
import shutil
import datetime
import subprocess

SRC_URL = os.getenv("REPLIT_URL", "https://your-replit.repl.co") + "/status/dashboard"
LOCAL_SRC = "status_dashboard.html"
DEST_DIR = "docs_build/status"
DEST = os.path.join(DEST_DIR, "dashboard.html")

def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🪞 Harmony Dashboard Exporter v2.0.9                        ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Fetch current dashboard from Replit
    if not os.path.exists(LOCAL_SRC):
        print(f"📡 Fetching dashboard from {SRC_URL}...")
        try:
            subprocess.run(
                ["curl", "-s", SRC_URL, "-o", LOCAL_SRC],
                check=True,
                timeout=30
            )
            print("✅ Dashboard fetched successfully")
        except Exception as e:
            print(f"⚠️  Failed to fetch dashboard: {e}")
            print("   Creating placeholder instead...")
            with open(LOCAL_SRC, "w") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head><title>Harmony Dashboard</title></head>
<body style="background:#0d1117;color:white;font-family:sans-serif;text-align:center;padding:50px;">
    <h1>🧠 Harmony Dashboard Offline</h1>
    <p>Visit the live dashboard at: <a href="{SRC_URL}" style="color:#58a6ff;">{SRC_URL}</a></p>
    <p>Last snapshot attempt: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
</body>
</html>""")
    
    # Create destination directory
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # Copy to Pages directory
    shutil.copy(LOCAL_SRC, DEST)
    
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n✅ Dashboard snapshot exported → {DEST}")
    print(f"📅 Timestamp: {timestamp}")
    print(f"\nDashboard will be available at:")
    print(f"   https://your-github.github.io/SonicBuilder/status/dashboard.html\n")

if __name__ == "__main__":
    main()
