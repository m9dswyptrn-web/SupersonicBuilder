#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 ULTRA-SECURE — Webhook Listener + Discord Notify + Auth
---------------------------------------------------------------------------
Handles Founder Dashboard webhooks with authentication and Discord logging.
Only valid API keys can trigger control actions.

Usage:
  python3 founder_webhook_listener_secure.py
  
Authentication:
  Set FOUNDER_API_KEY in Replit Secrets
  
  Option 1 - Header:
    X-API-KEY: your-secret-key
    
  Option 2 - Query param:
    ?key=your-secret-key

Endpoints:
  GET  /           - Service info (no auth required)
  GET  /status     - Get scheduler status (auth required)
  POST /pause      - Pause scheduler (auth required)
  POST /resume     - Resume scheduler (auth required)
  POST /deploy     - Trigger manual deploy (auth required)
  GET  /health     - Health check (no auth required)
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

# === Configuration ===
PAUSE_FLAG = "pause.flag"
SILENT_SCRIPT = "supersonic_autodeploy_silent.py"
STATUS_FILE = "scheduler.log"
VERIFY_LOG = "verify.log"

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
FOUNDER_API_KEY = os.getenv("FOUNDER_API_KEY")  # Required for secure access

# === Helper Functions ===
def send_discord_notification(msg, color=0x00AAFF):
    """Send an embed message to Discord webhook"""
    if not DISCORD_WEBHOOK:
        return
    
    try:
        payload = {
            "username": "SonicBuilder Secure Console",
            "embeds": [{
                "title": "🔐 Secure Action",
                "description": msg,
                "color": color,
                "footer": {"text": f"SonicBuilder v2.0.9 • {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️  Discord notification error: {e}")

def verify_api_key(req):
    """Verify API key in header or query parameter"""
    if not FOUNDER_API_KEY:
        print("⚠️  WARNING: FOUNDER_API_KEY not set! All requests will be rejected.")
        return False
    
    # Check X-API-KEY header
    header_key = req.headers.get("X-API-KEY")
    if header_key and header_key == FOUNDER_API_KEY:
        return True
    
    # Check ?key= query parameter
    query_key = req.args.get("key")
    if query_key and query_key == FOUNDER_API_KEY:
        return True
    
    # Log unauthorized attempt
    ip = req.headers.get('X-Forwarded-For', req.remote_addr)
    endpoint = req.path
    send_discord_notification(
        f"🚫 Unauthorized attempt!\n"
        f"Endpoint: {endpoint}\n"
        f"IP: {ip}\n"
        f"Time: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        color=0xFF0000
    )
    
    return False

# === Routes ===
@app.route("/")
def root():
    """Service information (public)"""
    return jsonify({
        "service": "SonicBuilder Secure Webhook Controller",
        "version": "2.0.9+ULTRA-SECURE",
        "status": "online",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "endpoints": {
            "GET /": "Service info (public)",
            "GET /status": "Get scheduler status (auth required)",
            "POST /pause": "Pause scheduler (auth required)",
            "POST /resume": "Resume scheduler (auth required)",
            "POST /deploy": "Trigger manual deploy (auth required)",
            "GET /health": "Health check (public)"
        },
        "authentication": {
            "method_1": "X-API-KEY header",
            "method_2": "?key= query parameter",
            "required": "Set FOUNDER_API_KEY in Replit Secrets"
        }
    })

@app.route("/status", methods=["GET"])
def status():
    """Get current scheduler status (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized", "message": "Invalid or missing API key"}), 403
    
    try:
        paused = os.path.exists(PAUSE_FLAG)
        
        # Read scheduler log
        scheduler_log = []
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE) as f:
                lines = f.read().splitlines()
                scheduler_log = lines[-20:]
        
        # Read verify log
        verify_log = []
        if os.path.exists(VERIFY_LOG):
            with open(VERIFY_LOG) as f:
                lines = f.read().splitlines()
                verify_log = lines[-10:]
        
        # Parse statistics
        stats = {"total_cycles": 0, "successes": 0, "failures": 0}
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
        
        send_discord_notification("📡 Secure Status Check", color=0x66FCF1)
        
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
    """Pause scheduler (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized", "message": "Invalid or missing API key"}), 403
    
    try:
        with open(PAUSE_FLAG, "w") as f:
            f.write(f"Paused at {datetime.datetime.utcnow().isoformat()}\n")
        
        send_discord_notification("⏸️ Scheduler Paused (secure trigger)", color=0xAAAAAA)
        
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
    """Resume scheduler (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized", "message": "Invalid or missing API key"}), 403
    
    try:
        removed = False
        if os.path.exists(PAUSE_FLAG):
            os.remove(PAUSE_FLAG)
            removed = True
        
        send_discord_notification("▶️ Scheduler Resumed (secure trigger)", color=0x00FF00)
        
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
    """Trigger manual deployment (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized", "message": "Invalid or missing API key"}), 403
    
    try:
        process = subprocess.Popen(
            ["python3", SILENT_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        send_discord_notification("🚀 Manual Deploy Triggered (secure trigger)", color=0x45A29E)
        
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
    """Health check (public)"""
    return jsonify({
        "status": "healthy",
        "service": "SonicBuilder Secure Webhook Controller",
        "auth_configured": FOUNDER_API_KEY is not None,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🔐 SonicBuilder Secure Webhook Listener v2.0.9+ULTRA     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nStarting secure webhook listener on port {port}...")
    
    if not FOUNDER_API_KEY:
        print("\n⚠️  WARNING: FOUNDER_API_KEY not set!")
        print("   All authenticated endpoints will reject requests.")
        print("   Set FOUNDER_API_KEY in Replit Secrets to enable authentication.\n")
    else:
        print(f"\n✅ Authentication enabled (API key configured)")
    
    print(f"Discord notifications: {'Enabled' if DISCORD_WEBHOOK else 'Disabled'}")
    print(f"\nEndpoints:")
    print(f"  GET  http://0.0.0.0:{port}/         - Service info (public)")
    print(f"  GET  http://0.0.0.0:{port}/status   - Scheduler status (auth required)")
    print(f"  POST http://0.0.0.0:{port}/pause    - Pause scheduler (auth required)")
    print(f"  POST http://0.0.0.0:{port}/resume   - Resume scheduler (auth required)")
    print(f"  POST http://0.0.0.0:{port}/deploy   - Trigger deploy (auth required)")
    print(f"  GET  http://0.0.0.0:{port}/health   - Health check (public)")
    print(f"\nAuthentication Methods:")
    print(f"  1. Header:  X-API-KEY: <your-key>")
    print(f"  2. Query:   ?key=<your-key>")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
