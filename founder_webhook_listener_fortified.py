#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 ULTRA-SECURE-LOCK
-------------------------------------
Founder Dashboard webhook controller with:
- API key authentication
- Rate limiting + brute-force lockout
- Discord alerts for suspicious or repeated hits

Security Features:
  • API key authentication (X-API-KEY header or ?key= param)
  • Rate limiting: 1 request per 10 seconds per IP
  • Brute-force protection: 5 failed attempts = 15 minute lockout
  • Discord security alerts
  • IP tracking and logging

Usage:
  python3 founder_webhook_listener_fortified.py
  
Environment Variables:
  FOUNDER_API_KEY    - Your secret API key (required)
  DISCORD_WEBHOOK    - Discord webhook URL (optional)
  PORT               - Server port (default: 8080)
"""

import os
import time
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
FOUNDER_API_KEY = os.getenv("FOUNDER_API_KEY")

# Security Settings
MAX_ATTEMPTS = 5          # Max failed auth attempts before lockout
LOCKOUT_TIME = 900        # Lockout duration in seconds (15 minutes)
RATE_WINDOW = 10          # Minimum seconds between requests per IP

# Track failed attempts and rate limits per IP
attempts = {}  # {ip: {"count": int, "last": timestamp}}
last_hit = {}  # {ip: timestamp}

# === Helper Functions ===
def send_discord_notification(msg, color=0x00AAFF):
    """Send security alert to Discord"""
    if not DISCORD_WEBHOOK:
        return
    
    try:
        payload = {
            "username": "SonicBuilder Sentinel",
            "embeds": [{
                "title": "🛡️ SonicBuilder Security Alert",
                "description": msg,
                "color": color,
                "footer": {"text": f"SonicBuilder v2.0.9 • {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=8)
    except Exception as e:
        print(f"⚠️  Discord notification error: {e}")

def check_rate_limit(ip):
    """Check if IP is within rate limit window"""
    now = time.time()
    
    if ip in last_hit:
        time_since_last = now - last_hit[ip]
        if time_since_last < RATE_WINDOW:
            # Rate limit exceeded
            return False
    
    last_hit[ip] = now
    return True

def verify_api_key(req):
    """Verify API key with brute-force protection and rate limiting"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    endpoint = req.path
    now = time.time()
    
    # Check if IP is locked out
    if ip in attempts and attempts[ip]["count"] >= MAX_ATTEMPTS:
        lockout_remaining = LOCKOUT_TIME - (now - attempts[ip]["last"])
        
        if lockout_remaining > 0:
            send_discord_notification(
                f"🚫 **Locked Out IP Attempting Access**\n"
                f"IP: `{ip}`\n"
                f"Endpoint: `{endpoint}`\n"
                f"Lockout remaining: {int(lockout_remaining/60)} minutes",
                color=0xFF0000
            )
            return False
        else:
            # Lockout expired, reset counter
            attempts[ip] = {"count": 0, "last": 0}
    
    # Check rate limit
    if not check_rate_limit(ip):
        send_discord_notification(
            f"⚠️ **Rate Limit Exceeded**\n"
            f"IP: `{ip}`\n"
            f"Endpoint: `{endpoint}`\n"
            f"Limit: 1 request per {RATE_WINDOW} seconds",
            color=0xFFA500
        )
        return False
    
    # Verify API key
    if not FOUNDER_API_KEY:
        print("⚠️  WARNING: FOUNDER_API_KEY not set! All requests rejected.")
        return False
    
    key = req.headers.get("X-API-KEY") or req.args.get("key")
    
    if not key or key != FOUNDER_API_KEY:
        # Increment failed attempt counter
        if ip not in attempts:
            attempts[ip] = {"count": 0, "last": 0}
        
        attempts[ip]["count"] += 1
        attempts[ip]["last"] = now
        
        remaining = MAX_ATTEMPTS - attempts[ip]["count"]
        
        send_discord_notification(
            f"🚷 **Invalid API Key Attempt**\n"
            f"IP: `{ip}`\n"
            f"Endpoint: `{endpoint}`\n"
            f"Attempt: {attempts[ip]['count']}/{MAX_ATTEMPTS}\n"
            f"{'🔒 **IP NOW LOCKED OUT**' if remaining <= 0 else f'Remaining attempts: {remaining}'}",
            color=0xFF5555
        )
        
        return False
    
    # Valid key - reset attempt counter for this IP
    if ip in attempts:
        attempts[ip] = {"count": 0, "last": 0}
    
    return True

# === Routes ===
@app.route("/")
def root():
    """Service information (public)"""
    return jsonify({
        "service": "SonicBuilder Fortified Webhook Controller",
        "version": "2.0.9+ULTRA-SECURE-LOCK",
        "status": "online",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "endpoints": {
            "GET /": "Service info (public)",
            "GET /status": "Scheduler status (auth required)",
            "POST /pause": "Pause scheduler (auth required)",
            "POST /resume": "Resume scheduler (auth required)",
            "POST /deploy": "Trigger deploy (auth required)",
            "GET /health": "Health check (public)"
        },
        "authentication": {
            "method_1": "X-API-KEY header",
            "method_2": "?key= query parameter",
            "required": "Set FOUNDER_API_KEY in Replit Secrets"
        },
        "security": {
            "rate_limit_seconds": RATE_WINDOW,
            "max_failed_attempts": MAX_ATTEMPTS,
            "lockout_minutes": LOCKOUT_TIME / 60,
            "features": ["API Key Auth", "Rate Limiting", "Brute-Force Protection", "Discord Alerts"]
        }
    })

@app.route("/status", methods=["GET"])
def status():
    """Get scheduler status (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized", "message": "Invalid or missing API key"}), 403
    
    try:
        paused = os.path.exists(PAUSE_FLAG)
        
        scheduler_log = []
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE) as f:
                lines = f.read().splitlines()
                scheduler_log = lines[-20:]
        
        verify_log = []
        if os.path.exists(VERIFY_LOG):
            with open(VERIFY_LOG) as f:
                lines = f.read().splitlines()
                verify_log = lines[-10:]
        
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
        return jsonify({"status": "error", "error": str(e)}), 500

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
        return jsonify({"status": "error", "error": str(e)}), 500

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
        return jsonify({"status": "error", "error": str(e)}), 500

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
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check (public)"""
    return jsonify({
        "status": "healthy",
        "service": "SonicBuilder Fortified Webhook Controller",
        "auth_configured": FOUNDER_API_KEY is not None,
        "discord_configured": DISCORD_WEBHOOK is not None,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🛡️  SonicBuilder Fortified Webhook Listener v2.0.9+ULTRA   ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nStarting fortified webhook listener on port {port}...")
    
    if not FOUNDER_API_KEY:
        print("\n⚠️  WARNING: FOUNDER_API_KEY not set!")
        print("   All authenticated endpoints will reject requests.")
        print("   Set FOUNDER_API_KEY in Replit Secrets.\n")
    else:
        print(f"\n✅ Authentication enabled")
    
    print(f"Discord notifications: {'Enabled' if DISCORD_WEBHOOK else 'Disabled'}")
    
    print(f"\n🛡️  Security Features:")
    print(f"   • API Key Authentication")
    print(f"   • Rate Limiting: 1 request per {RATE_WINDOW} seconds")
    print(f"   • Brute-Force Protection: {MAX_ATTEMPTS} attempts max")
    print(f"   • Auto-Lockout: {LOCKOUT_TIME/60:.0f} minutes")
    print(f"   • Discord Security Alerts")
    
    print(f"\nEndpoints:")
    print(f"  GET  http://0.0.0.0:{port}/         - Service info (public)")
    print(f"  GET  http://0.0.0.0:{port}/status   - Scheduler status (auth required)")
    print(f"  POST http://0.0.0.0:{port}/pause    - Pause scheduler (auth required)")
    print(f"  POST http://0.0.0.0:{port}/resume   - Resume scheduler (auth required)")
    print(f"  POST http://0.0.0.0:{port}/deploy   - Trigger deploy (auth required)")
    print(f"  GET  http://0.0.0.0:{port}/health   - Health check (public)")
    
    print(f"\nAuthentication:")
    print(f"  Header:  X-API-KEY: <your-key>")
    print(f"  Query:   ?key=<your-key>")
    
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
