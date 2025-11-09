#!/usr/bin/env python3
"""
SonicBuilder v2.0.9+ULTRA — Webhook Listener + Discord Notify
Live Replit webhook controller for Founder Dashboard actions:
Pause, Resume, Deploy, and Status — with Discord confirmations.

Usage:
  python3 founder_webhook_listener.py
  
Endpoints:
  GET  /           - Service info
  GET  /status     - Get scheduler status
  POST /pause      - Pause scheduler
  POST /resume     - Resume scheduler
  POST /deploy     - Trigger manual deploy
  GET  /health     - Health check
"""

import os
import subprocess
import json
import datetime
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for GitHub Pages

PAUSE_FLAG = "pause.flag"
SILENT_SCRIPT = "supersonic_autodeploy_silent.py"
STATUS_FILE = "scheduler.log"
VERIFY_LOG = "verify.log"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord_notification(msg, color=0x00AAFF):
    """Send a message embed to Discord webhook"""
    if not DISCORD_WEBHOOK:
        return
    
    try:
        payload = {
            "username": "SonicBuilder Control",
            "embeds": [{
                "title": "🎛️ Founder Console Action",
                "description": msg,
                "color": color,
                "footer": {"text": f"SonicBuilder v2.0.9 • {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️  Discord notification error: {e}")

@app.route("/")
def root():
    """Service information"""
    return jsonify({
        "service": "SonicBuilder Webhook Controller",
        "version": "2.0.9+ULTRA",
        "status": "online",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "endpoints": {
            "GET /": "Service info",
            "GET /status": "Get scheduler status",
            "POST /pause": "Pause scheduler",
            "POST /resume": "Resume scheduler",
            "POST /deploy": "Trigger manual deploy"
        }
    })

@app.route("/status", methods=["GET"])
def status():
    """Get current scheduler status and recent logs"""
    try:
        paused = os.path.exists(PAUSE_FLAG)
        
        # Read scheduler log
        scheduler_log = []
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE) as f:
                lines = f.read().splitlines()
                scheduler_log = lines[-20:]  # Last 20 lines
        
        # Read verify log
        verify_log = []
        if os.path.exists(VERIFY_LOG):
            with open(VERIFY_LOG) as f:
                lines = f.read().splitlines()
                verify_log = lines[-10:]  # Last 10 lines
        
        # Parse statistics
        stats = {
            "total_cycles": 0,
            "successes": 0,
            "failures": 0
        }
        
        for line in reversed(scheduler_log):
            if "Stats:" in line:
                import re
                success_match = re.search(r'(\d+) successes', line)
                failure_match = re.search(r'(\d+) failures', line)
                if success_match:
                    stats["successes"] = int(success_match.group(1))
                if failure_match:
                    stats["failures"] = int(failure_match.group(1))
                break
        
        return jsonify({
            "status": "ok",
            "paused": paused,
            "scheduler_running": len(scheduler_log) > 0,
            "stats": stats,
            "scheduler_log": scheduler_log,
            "verify_log": verify_log,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500

@app.route("/pause", methods=["POST"])
def pause():
    """Pause the scheduler by creating pause flag"""
    try:
        with open(PAUSE_FLAG, "w") as f:
            f.write(f"Paused at {datetime.datetime.utcnow().isoformat()}\n")
        
        send_discord_notification("⏸️ Scheduler Paused (via Founder Dashboard)", color=0xAAAAAA)
        
        return jsonify({
            "status": "success",
            "action": "paused",
            "flag_created": PAUSE_FLAG,
            "message": "Scheduler will pause at next cycle check",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500

@app.route("/resume", methods=["POST"])
def resume():
    """Resume the scheduler by removing pause flag"""
    try:
        removed = False
        if os.path.exists(PAUSE_FLAG):
            os.remove(PAUSE_FLAG)
            removed = True
        
        send_discord_notification("▶️ Scheduler Resumed (via Founder Dashboard)", color=0x00FF00)
        
        return jsonify({
            "status": "success",
            "action": "resumed",
            "flag_removed": removed,
            "message": "Scheduler will resume at next cycle" if removed else "Scheduler was not paused",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500

@app.route("/deploy", methods=["POST"])
def deploy():
    """Trigger manual deployment"""
    try:
        # Start deployment in background
        process = subprocess.Popen(
            ["python3", SILENT_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        send_discord_notification("🚀 Manual Deploy Triggered (via Founder Dashboard)", color=0x45A29E)
        
        return jsonify({
            "status": "success",
            "action": "deploy_triggered",
            "pid": process.pid,
            "message": "Manual deployment started in background",
            "check_logs": "verify.log",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SonicBuilder Webhook Controller",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🚀 SonicBuilder Webhook Listener v2.0.9+ULTRA            ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nStarting webhook listener on port {port}...")
    print(f"\nDiscord notifications: {'Enabled' if DISCORD_WEBHOOK else 'Disabled'}")
    print(f"\nEndpoints:")
    print(f"  GET  http://0.0.0.0:{port}/         - Service info")
    print(f"  GET  http://0.0.0.0:{port}/status   - Scheduler status")
    print(f"  POST http://0.0.0.0:{port}/pause    - Pause scheduler")
    print(f"  POST http://0.0.0.0:{port}/resume   - Resume scheduler")
    print(f"  POST http://0.0.0.0:{port}/deploy   - Trigger deploy")
    print(f"  GET  http://0.0.0.0:{port}/health   - Health check")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
