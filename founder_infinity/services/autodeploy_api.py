#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 FOUNDER-INFINITY-AUTODEPLOY-API
---------------------------------------------------
REST API for unified deployment operations.

Endpoints:
  POST /autodeploy/mirror   - Trigger mirror sync
  POST /autodeploy/docs     - Rebuild documentation
  POST /autodeploy/deploy   - Deploy to GitHub Pages
  POST /autodeploy/refresh  - Update badges and dashboards
  POST /autodeploy/full     - Execute complete pipeline

All endpoints require API key authentication.

Requires:
  - FOUNDER_API_KEY - API key for authentication
"""

import os
import subprocess
import datetime
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
FOUNDER_API_KEY = os.getenv("FOUNDER_API_KEY")

# Harmony Watchdog
last_github_heartbeat = 0

def harmony_watchdog():
    """Background watchdog that triggers local deploy if GitHub heartbeat stops"""
    global last_github_heartbeat
    
    print("🕓 Harmony Watchdog started...")
    
    while True:
        # Check last heartbeat
        if os.path.exists("last_heartbeat.txt"):
            try:
                with open("last_heartbeat.txt") as f:
                    last_github_heartbeat = float(f.read().strip())
            except Exception:
                pass
        
        elapsed = time.time() - last_github_heartbeat
        
        # If no heartbeat for 1.5 hours, trigger local cycle
        if elapsed > 5400 and last_github_heartbeat > 0:
            print("⚠️  No GitHub Actions heartbeat detected for 1.5 hours!")
            print("   Triggering local AutoDeploy cycle as fallback...")
            
            try:
                # Run documentation rebuild
                subprocess.run(
                    ["python3", "supersonic_autodeploy.py"],
                    capture_output=True,
                    timeout=300
                )
                print("✅ Local deploy cycle completed")
                
                # Update heartbeat to prevent immediate re-trigger
                last_github_heartbeat = time.time()
                with open("last_heartbeat.txt", "w") as f:
                    f.write(str(last_github_heartbeat))
            except Exception as e:
                print(f"⚠️  Local deploy cycle failed: {e}")
        
        # Check every 10 minutes
        time.sleep(600)

def verify_api_key(req):
    """Verify API key from header or query parameter"""
    key = req.headers.get("X-API-KEY") or req.args.get("key")
    return key == FOUNDER_API_KEY if FOUNDER_API_KEY else False

@app.route("/autodeploy/mirror", methods=["POST"])
def trigger_mirror():
    """Trigger mirror sync (runs in background)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        # Start mirror sync in background
        subprocess.Popen(
            ["python3", "founder_infinity/services/mirror_sync.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return jsonify({
            "status": "success",
            "action": "mirror_sync_triggered",
            "message": "Mirror sync started in background",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/autodeploy/docs", methods=["POST"])
def rebuild_docs():
    """Rebuild documentation bundle"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        # Run documentation build
        result = subprocess.run(
            ["python3", "supersonic_autodeploy.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        success = result.returncode == 0
        
        return jsonify({
            "status": "success" if success else "error",
            "action": "docs_rebuild",
            "returncode": result.returncode,
            "output": result.stdout[-500:] if result.stdout else "",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "error": "Documentation build timeout (>5min)"
        }), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/autodeploy/deploy", methods=["POST"])
def deploy_pages():
    """Deploy to GitHub Pages"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        # Check if deployment script exists
        if not os.path.exists("founder_infinity/scripts/deploy_pages.sh"):
            return jsonify({
                "status": "error",
                "error": "Deployment script not found"
            }), 404
        
        # Run deployment
        result = subprocess.run(
            ["bash", "founder_infinity/scripts/deploy_pages.sh"],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        success = result.returncode == 0
        
        return jsonify({
            "status": "success" if success else "error",
            "action": "github_pages_deploy",
            "returncode": result.returncode,
            "output": result.stdout[-500:] if result.stdout else "",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "error": "Deployment timeout (>3min)"
        }), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/autodeploy/refresh", methods=["POST"])
def refresh_badges():
    """Update badges and dashboards"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        # Run badge update script
        result = subprocess.run(
            ["python3", "founder_infinity/scripts/update_badges.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        
        return jsonify({
            "status": "success" if success else "error",
            "action": "badges_refreshed",
            "returncode": result.returncode,
            "output": result.stdout[-500:] if result.stdout else "",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "error": "Badge refresh timeout"
        }), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/autodeploy/full", methods=["POST"])
def full_pipeline():
    """Execute complete deployment pipeline"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    results = []
    
    # Step 1: Mirror sync
    try:
        subprocess.Popen(
            ["python3", "founder_infinity/services/mirror_sync.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        results.append({"step": "mirror", "status": "triggered"})
    except Exception as e:
        results.append({"step": "mirror", "status": "failed", "error": str(e)})
    
    # Step 2: Rebuild docs
    try:
        result = subprocess.run(
            ["python3", "supersonic_autodeploy.py"],
            capture_output=True,
            timeout=300
        )
        results.append({
            "step": "docs", 
            "status": "success" if result.returncode == 0 else "failed",
            "returncode": result.returncode
        })
    except Exception as e:
        results.append({"step": "docs", "status": "failed", "error": str(e)})
    
    # Step 3: Deploy
    if os.path.exists("founder_infinity/scripts/deploy_pages.sh"):
        try:
            result = subprocess.run(
                ["bash", "founder_infinity/scripts/deploy_pages.sh"],
                capture_output=True,
                timeout=180
            )
            results.append({
                "step": "deploy",
                "status": "success" if result.returncode == 0 else "failed",
                "returncode": result.returncode
            })
        except Exception as e:
            results.append({"step": "deploy", "status": "failed", "error": str(e)})
    
    # Step 4: Refresh badges
    try:
        result = subprocess.run(
            ["python3", "founder_infinity/scripts/update_badges.py"],
            capture_output=True,
            timeout=30
        )
        results.append({
            "step": "refresh",
            "status": "success" if result.returncode == 0 else "failed",
            "returncode": result.returncode
        })
    except Exception as e:
        results.append({"step": "refresh", "status": "failed", "error": str(e)})
    
    return jsonify({
        "status": "completed",
        "pipeline": "full_autodeploy",
        "results": results,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route("/health")
def health():
    """Health check"""
    return jsonify({
        "service": "SonicBuilder AutoDeploy API",
        "status": "operational",
        "auth_configured": FOUNDER_API_KEY is not None,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("AUTODEPLOY_PORT", 8082))
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🚀 SonicBuilder AutoDeploy API v2.0.9+Harmony              ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nStarting AutoDeploy API on port {port}...")
    print(f"\nEndpoints:")
    print(f"  POST http://0.0.0.0:{port}/autodeploy/mirror   - Trigger mirror sync")
    print(f"  POST http://0.0.0.0:{port}/autodeploy/docs     - Rebuild docs")
    print(f"  POST http://0.0.0.0:{port}/autodeploy/deploy   - Deploy to Pages")
    print(f"  POST http://0.0.0.0:{port}/autodeploy/refresh  - Update badges")
    print(f"  POST http://0.0.0.0:{port}/autodeploy/full     - Full pipeline")
    print(f"  GET  http://0.0.0.0:{port}/health             - Health check")
    print(f"\nAuthentication:")
    print(f"  Header:  X-API-KEY: <your-key>")
    print(f"  Query:   ?key=<your-key>")
    print(f"\n🕓 Harmony Watchdog:")
    print(f"  Monitors GitHub Actions heartbeat")
    print(f"  Triggers local deploy if no heartbeat for 1.5 hours")
    print(f"\nPress Ctrl+C to stop\n")
    
    # Start Harmony Watchdog in background thread
    watchdog_thread = threading.Thread(target=harmony_watchdog, daemon=True)
    watchdog_thread.start()
    
    app.run(host="0.0.0.0", port=port, debug=False)
