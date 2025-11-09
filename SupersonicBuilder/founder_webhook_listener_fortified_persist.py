#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 ULTRA-SECURE-FORTIFIED+
-------------------------------------------
Maximum security webhook controller with:
- Persistent IP banlist (saved in banned_ips.json)
- API key authentication
- Rate limiting
- Brute-force protection with auto-ban
- Full Discord alerting

Security Features:
  • API Key Authentication
  • Rate Limiting: 1 request per 10 seconds per IP
  • Brute-Force Protection: 5 failed attempts = PERMANENT BAN
  • Persistent IP Banlist (banned_ips.json)
  • Discord Security Alerts
  • IP Tracking

Usage:
  python3 founder_webhook_listener_fortified_persist.py
  
Environment Variables:
  FOUNDER_API_KEY    - Your secret API key (required)
  DISCORD_WEBHOOK    - Discord webhook URL (optional)
  PORT               - Server port (default: 8080)
"""

import os
import time
import json
import datetime
import subprocess
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from xml.etree.ElementTree import Element, SubElement, tostring

app = Flask(__name__)
CORS(app)  # Enable CORS for GitHub Pages

# === Configuration ===
PAUSE_FLAG = "pause.flag"
SILENT_SCRIPT = "supersonic_autodeploy_silent.py"
STATUS_FILE = "scheduler.log"
VERIFY_LOG = "verify.log"
BAN_FILE = "banned_ips.json"
AUDIT_LOG = "security_audit.json"
FEED_FILE = "harmony_feed.json"

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
FOUNDER_API_KEY = os.getenv("FOUNDER_API_KEY")

# Security Settings
MAX_ATTEMPTS = 5          # Max failed attempts before PERMANENT BAN
LOCKOUT_TIME = 900        # Temporary lockout (15 minutes) before ban
RATE_WINDOW = 10          # Seconds between requests per IP

# Track failed attempts and rate limits per IP
attempts = {}  # {ip: {"count": int, "last": timestamp}}
last_hit = {}  # {ip: timestamp}

# === Helper Functions ===
def load_banned_ips():
    """Load persistent ban list from JSON file"""
    try:
        with open(BAN_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_banned_ips(bans):
    """Save ban list to JSON file"""
    try:
        with open(BAN_FILE, 'w') as f:
            json.dump(bans, f, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving ban list: {e}")

def load_audit_log():
    """Load audit log from JSON file"""
    try:
        with open(AUDIT_LOG, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_audit_log(log):
    """Save audit log to JSON file"""
    try:
        with open(AUDIT_LOG, 'w') as f:
            json.dump(log, f, indent=2)
    except Exception as e:
        print(f"⚠️  Error saving audit log: {e}")

def log_audit_event(event, ip, detail):
    """Log security event to audit trail"""
    try:
        log = load_audit_log()
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "ip": ip,
            "event": event,
            "detail": detail
        }
        log.append(entry)
        save_audit_log(log)
        print(f"[AUDIT] {event} from {ip}: {detail}")
        return entry
    except Exception as e:
        print(f"⚠️  Audit logging error: {e}")
        return None

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
                "footer": {"text": f"SonicBuilder v2.0.9+ • {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"},
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
            return False
    
    last_hit[ip] = now
    return True

def verify_api_key(req):
    """Verify API key with persistent ban enforcement"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    endpoint = req.path
    now = time.time()
    
    # Check if IP is permanently banned
    banned_ips = load_banned_ips()
    if ip in banned_ips:
        log_audit_event("banned_access", ip, f"Access attempt from banned IP to {endpoint}")
        send_discord_notification(
            f"🚫 **BANNED IP Attempted Access**\n"
            f"IP: `{ip}`\n"
            f"Endpoint: `{endpoint}`\n"
            f"Status: **PERMANENTLY BANNED**",
            color=0xFF0000
        )
        return False
    
    # Check temporary lockout
    if ip in attempts and attempts[ip]["count"] >= MAX_ATTEMPTS:
        lockout_remaining = LOCKOUT_TIME - (now - attempts[ip]["last"])
        
        if lockout_remaining > 0:
            log_audit_event("lockout", ip, f"Exceeded max attempts, {int(lockout_remaining/60)} min remaining")
            send_discord_notification(
                f"🚫 **Locked Out IP Attempting Access**\n"
                f"IP: `{ip}`\n"
                f"Endpoint: `{endpoint}`\n"
                f"Lockout remaining: {int(lockout_remaining/60)} minutes\n"
                f"⚠️ Will be PERMANENTLY BANNED after lockout if continues",
                color=0xFF0000
            )
            return False
        else:
            # Lockout expired, reset counter
            attempts[ip] = {"count": 0, "last": 0}
    
    # Check rate limit
    if not check_rate_limit(ip):
        log_audit_event("rate_limit", ip, f"Rate limit triggered on {endpoint}")
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
        
        # Check if this IP should be permanently banned
        if attempts[ip]["count"] >= MAX_ATTEMPTS:
            # PERMANENT BAN
            banned_ips.append(ip)
            save_banned_ips(banned_ips)
            
            log_audit_event("ban", ip, f"Permanently banned after {MAX_ATTEMPTS} failed attempts")
            
            send_discord_notification(
                f"🔒 **IP PERMANENTLY BANNED**\n"
                f"IP: `{ip}`\n"
                f"Endpoint: `{endpoint}`\n"
                f"Reason: {MAX_ATTEMPTS} failed authentication attempts\n"
                f"Status: **ADDED TO PERMANENT BAN LIST**\n"
                f"File: `{BAN_FILE}`",
                color=0xFF0000
            )
        else:
            # Still within attempt limit
            log_audit_event("invalid_key", ip, f"Invalid key attempt #{attempts[ip]['count']} on {endpoint}")
            
            send_discord_notification(
                f"🚷 **Invalid API Key Attempt**\n"
                f"IP: `{ip}`\n"
                f"Endpoint: `{endpoint}`\n"
                f"Attempt: {attempts[ip]['count']}/{MAX_ATTEMPTS}\n"
                f"⚠️ Remaining attempts: {remaining}\n"
                f"{'⚠️ **NEXT FAILURE = PERMANENT BAN**' if remaining == 1 else ''}",
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
    banned_count = len(load_banned_ips())
    
    return jsonify({
        "service": "SonicBuilder Fortified+ Webhook Controller",
        "version": "2.0.9+ULTRA-SECURE-FORTIFIED+",
        "status": "online",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "endpoints": {
            "GET /": "Service info (public)",
            "GET /status": "Scheduler status (auth required)",
            "POST /pause": "Pause scheduler (auth required)",
            "POST /resume": "Resume scheduler (auth required)",
            "POST /deploy": "Trigger deploy (auth required)",
            "GET /health": "Health check (public)",
            "GET /bans": "View ban list (auth required)",
            "POST /unban": "Remove IP from ban list (auth required)",
            "GET /audit": "View security audit log (auth required)"
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
            "persistent_bans": True,
            "banned_ips_count": banned_count,
            "ban_file": BAN_FILE,
            "audit_log": AUDIT_LOG,
            "features": [
                "API Key Auth",
                "Rate Limiting",
                "Brute-Force Protection",
                "Persistent IP Banning",
                "Discord Alerts",
                "Security Audit Trail"
            ]
        }
    })

@app.route("/status", methods=["GET"])
def status():
    """Get scheduler status (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
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
        
        log_audit_event("status", request.headers.get('X-Forwarded-For', request.remote_addr), "Status checked")
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
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        with open(PAUSE_FLAG, "w") as f:
            f.write(f"Paused at {datetime.datetime.utcnow().isoformat()}\n")
        
        log_audit_event("pause", request.headers.get('X-Forwarded-For', request.remote_addr), "Scheduler paused")
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
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        removed = False
        if os.path.exists(PAUSE_FLAG):
            os.remove(PAUSE_FLAG)
            removed = True
        
        log_audit_event("resume", request.headers.get('X-Forwarded-For', request.remote_addr), "Scheduler resumed")
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
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        process = subprocess.Popen(
            ["python3", SILENT_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        log_audit_event("deploy", request.headers.get('X-Forwarded-For', request.remote_addr), "Manual deploy triggered")
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

@app.route("/bans", methods=["GET"])
def bans():
    """View banned IPs list (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    banned_ips = load_banned_ips()
    
    log_audit_event("bans_view", request.headers.get('X-Forwarded-For', request.remote_addr), f"Viewed {len(banned_ips)} banned IPs")
    
    return jsonify({
        "status": "ok",
        "banned_ips": banned_ips,
        "count": len(banned_ips),
        "ban_file": BAN_FILE,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route("/unban", methods=["POST"])
def unban():
    """Remove IP from ban list (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    try:
        data = request.get_json(force=True)
        ip_to_unban = data.get("ip")
        
        if not ip_to_unban:
            return jsonify({
                "status": "error",
                "error": "missing ip field",
                "message": "Request body must include 'ip' field"
            }), 400
        
        banned_ips = load_banned_ips()
        
        if ip_to_unban in banned_ips:
            banned_ips.remove(ip_to_unban)
            save_banned_ips(banned_ips)
            
            log_audit_event("unban", request.headers.get('X-Forwarded-For', request.remote_addr), f"Unbanned IP: {ip_to_unban}")
            
            send_discord_notification(
                f"🧹 **IP Manually Unbanned**\n"
                f"IP: `{ip_to_unban}`\n"
                f"Action: Removed from ban list\n"
                f"File: `{BAN_FILE}`",
                color=0x00FFFF
            )
            
            return jsonify({
                "status": "success",
                "action": "unbanned",
                "ip": ip_to_unban,
                "message": f"IP {ip_to_unban} removed from ban list",
                "remaining_bans": len(banned_ips),
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                "status": "info",
                "message": f"IP {ip_to_unban} was not in ban list",
                "ip": ip_to_unban,
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500

@app.route("/audit", methods=["GET"])
def audit():
    """View security audit log (auth required)"""
    if not verify_api_key(request):
        return jsonify({"error": "unauthorized"}), 403
    
    audit_log = load_audit_log()
    
    log_audit_event("audit_view", request.headers.get('X-Forwarded-For', request.remote_addr), f"Viewed audit log ({len(audit_log)} entries)")
    send_discord_notification("🗂️ Audit trail viewed", color=0x9999FF)
    
    return jsonify({
        "status": "ok",
        "audit_entries": audit_log,
        "count": len(audit_log),
        "audit_file": AUDIT_LOG,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route("/health", methods=["GET"])
def health():
    """Health check (public)"""
    return jsonify({
        "status": "healthy",
        "service": "SonicBuilder Fortified+ Webhook Controller",
        "auth_configured": FOUNDER_API_KEY is not None,
        "discord_configured": DISCORD_WEBHOOK is not None,
        "banned_ips_count": len(load_banned_ips()),
        "audit_entries_count": len(load_audit_log()),
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

# === Infinity Dashboard Routes ===
@app.route("/founder/command-deck")
def command_deck():
    """Serve Command Deck dashboard"""
    return send_file("founder_infinity/dashboards/command_deck.html")

@app.route("/founder/mirror-dashboard")
def mirror_dashboard():
    """Serve Mirror Dashboard"""
    return send_file("founder_infinity/dashboards/mirror_dashboard.html")

@app.route("/founder/watchtower")
def watchtower():
    """Serve Mirror Watchtower"""
    return send_file("founder_infinity/dashboards/mirror_watchtower.html")

@app.route("/founder/infinity-console")
def infinity_console():
    """Serve Infinity Console"""
    return send_file("founder_infinity/dashboards/infinity_console.html")

# === Harmony Feed Functions ===
def append_feed_entry(status, color, elapsed):
    """Append an entry to the Harmony feed log"""
    entry = {
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": status,
        "color": color,
        "elapsed_minutes": round(elapsed / 60, 2)
    }
    
    # Read existing feed
    feed = []
    if os.path.exists(FEED_FILE):
        try:
            with open(FEED_FILE) as f:
                feed = json.load(f)
        except Exception:
            feed = []
    
    # Append and prune to last 50 entries
    feed.append(entry)
    feed = feed[-50:]
    
    with open(FEED_FILE, "w") as f:
        json.dump(feed, f, indent=2)
    
    return entry

# === Harmony Sync Endpoints ===
last_heartbeat = 0

@app.route("/founder_autodeploy/harmony", methods=["POST"])
def harmony_heartbeat():
    """Receive heartbeat from GitHub Actions"""
    global last_heartbeat
    last_heartbeat = time.time()
    
    with open("last_heartbeat.txt", "w") as f:
        f.write(str(last_heartbeat))
    
    # Determine current status for feed
    status, color = "Active", "brightgreen"
    elapsed = 0
    
    # Log to feed
    append_feed_entry(status, color, elapsed)
    
    log_audit_event(request.remote_addr, "harmony_ping", "GitHub Actions heartbeat received")
    
    print("💓 Harmony heartbeat received from GitHub Actions.")
    
    send_discord_alert("💓 Harmony Sync", f"GitHub Actions heartbeat received at {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", 0x3498db)
    
    return jsonify({
        "status": "success",
        "message": "Harmony sync acknowledged",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route("/status/harmony", methods=["GET"])
def harmony_status():
    """Returns live Harmony Sync status and badge info"""
    status, color, delta = "Unknown", "lightgrey", 99999
    
    if os.path.exists("last_heartbeat.txt"):
        try:
            with open("last_heartbeat.txt") as f:
                last = float(f.read().strip())
                delta = time.time() - last
                
                if delta < 5400:  # 1.5 hours
                    status, color = "Active", "brightgreen"
                elif delta < 7200:  # 2 hours
                    status, color = "Late", "yellow"
                else:
                    status, color = "Desync", "red"
        except Exception:
            pass
    
    # Update feed with current status
    append_feed_entry(status, color, delta)
    
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    badge_url = f"https://img.shields.io/badge/Harmony-{status}-{color}.svg"
    
    return jsonify({
        "status": status,
        "color": color,
        "badge_url": badge_url,
        "last_heartbeat_age_sec": round(delta, 2),
        "last_update": timestamp,
        "source": "Replit Harmony Sync Engine"
    })

@app.route("/status/feed", methods=["GET"])
def harmony_feed():
    """Serve Harmony feed as JSON or RSS based on format parameter"""
    fmt = request.args.get("format", "json").lower()
    
    feed = []
    if os.path.exists(FEED_FILE):
        try:
            with open(FEED_FILE) as f:
                feed = json.load(f)
        except Exception:
            feed = []
    
    if fmt == "rss":
        # Generate RSS feed
        rss = Element("rss", version="2.0")
        channel = SubElement(rss, "channel")
        SubElement(channel, "title").text = "SonicBuilder Harmony Feed"
        SubElement(channel, "link").text = request.host_url.rstrip("/") + "/status/feed"
        SubElement(channel, "description").text = "Live heartbeat log for SonicBuilder infrastructure."
        
        for item in reversed(feed):
            i = SubElement(channel, "item")
            SubElement(i, "title").text = f"{item['status']} at {item['timestamp']}"
            SubElement(i, "description").text = f"Color: {item['color']} | Elapsed: {item['elapsed_minutes']}m"
            SubElement(i, "pubDate").text = item['timestamp']
        
        xml_data = tostring(rss, encoding="utf-8")
        return app.response_class(xml_data, mimetype="application/rss+xml")
    
    # Default: JSON format
    return app.response_class(json.dumps(feed, indent=2), mimetype="application/json")

@app.route("/status/dashboard")
def harmony_dashboard():
    """Visual dashboard for Harmony heartbeat monitoring"""
    last_time = 0
    if os.path.exists("last_heartbeat.txt"):
        try:
            with open("last_heartbeat.txt") as f:
                last_time = float(f.read().strip())
        except Exception:
            last_time = 0
    
    elapsed = time.time() - last_time
    
    if elapsed < 5400:
        status = "Active"
        color = "#2ecc71"
    elif elapsed < 7200:
        status = "Late"
        color = "#f1c40f"
    else:
        status = "Desync"
        color = "#e74c3c"
    
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    minutes = int(elapsed / 60)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Harmony Sync Dashboard</title>
    <meta http-equiv="refresh" content="60">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #e6edf3;
            font-family: 'Segoe UI', sans-serif;
            text-align: center;
            padding: 50px 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 2.5em;
            margin-bottom: 30px;
            color: #58a6ff;
        }}
        .status {{
            font-size: 4em;
            font-weight: bold;
            color: {color};
            margin: 30px 0;
            text-shadow: 0 0 20px {color}44;
        }}
        .pulse {{
            display: inline-block;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: {color};
            box-shadow: 0 0 20px {color};
            animation: pulse 2s infinite;
            margin-right: 15px;
            vertical-align: middle;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.2); opacity: 0.7; }}
        }}
        .info {{
            font-size: 1.3em;
            margin: 20px 0;
            color: #8b949e;
        }}
        .badge {{
            margin: 40px 0;
        }}
        .badge img {{
            width: 200px;
            height: auto;
        }}
        .links {{
            margin-top: 40px;
        }}
        .links a {{
            display: inline-block;
            color: #58a6ff;
            text-decoration: none;
            margin: 10px 20px;
            padding: 12px 24px;
            border: 2px solid #58a6ff;
            border-radius: 6px;
            transition: all 0.3s;
        }}
        .links a:hover {{
            background: #58a6ff;
            color: #0d1117;
            transform: translateY(-2px);
        }}
        .footer {{
            position: fixed;
            bottom: 20px;
            left: 0;
            right: 0;
            font-size: 0.9em;
            color: #6e7681;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }}
        .stat-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #8b949e;
            margin-bottom: 8px;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #58a6ff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 SonicBuilder Harmony Monitor</h1>
        
        <div class="status">
            <span class="pulse"></span>
            {status}
        </div>
        
        <div class="info">
            Last heartbeat: {minutes} minutes ago
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Status</div>
                <div class="stat-value">{status}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Age (minutes)</div>
                <div class="stat-value">{minutes}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Last Update</div>
                <div class="stat-value" style="font-size: 0.8em;">{timestamp}</div>
            </div>
        </div>
        
        <div class="badge">
            <img src="https://img.shields.io/badge/Harmony-{status}-{color.strip('#')}.svg" alt="Harmony Badge">
        </div>
        
        <div class="links">
            <a href="/status/harmony">📋 JSON API</a>
            <a href="/founder/command-deck">🎛️ Command Deck</a>
            <a href="/founder/infinity-console">🚀 Infinity Console</a>
        </div>
        
        <div class="footer">
            © {datetime.datetime.utcnow().year} SonicBuilder | Harmony Sync Engine v2.0.9 | Auto-refresh every 60s
        </div>
    </div>
</body>
</html>"""
    return html

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  🛡️  SonicBuilder Fortified+ Webhook Listener v2.0.9+ULTRA   ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"\nStarting fortified+ webhook listener on port {port}...")
    
    if not FOUNDER_API_KEY:
        print("\n⚠️  WARNING: FOUNDER_API_KEY not set!")
        print("   All authenticated endpoints will reject requests.")
        print("   Set FOUNDER_API_KEY in Replit Secrets.\n")
    else:
        print(f"\n✅ Authentication enabled")
    
    print(f"Discord notifications: {'Enabled' if DISCORD_WEBHOOK else 'Disabled'}")
    
    # Load and display ban list
    banned_ips = load_banned_ips()
    print(f"Banned IPs: {len(banned_ips)}")
    if banned_ips:
        print(f"   {', '.join(banned_ips)}")
    
    print(f"\n🛡️  Security Features:")
    print(f"   • API Key Authentication")
    print(f"   • Rate Limiting: 1 request per {RATE_WINDOW} seconds")
    print(f"   • Brute-Force Protection: {MAX_ATTEMPTS} attempts max")
    print(f"   • Persistent IP Banning: PERMANENT after {MAX_ATTEMPTS} failures")
    print(f"   • Ban List File: {BAN_FILE}")
    print(f"   • Discord Security Alerts")
    
    print(f"\nEndpoints:")
    print(f"  GET  http://0.0.0.0:{port}/         - Service info (public)")
    print(f"  GET  http://0.0.0.0:{port}/status   - Scheduler status (auth required)")
    print(f"  POST http://0.0.0.0:{port}/pause    - Pause scheduler (auth required)")
    print(f"  POST http://0.0.0.0:{port}/resume   - Resume scheduler (auth required)")
    print(f"  POST http://0.0.0.0:{port}/deploy   - Trigger deploy (auth required)")
    print(f"  GET  http://0.0.0.0:{port}/bans     - View ban list (auth required)")
    print(f"  POST http://0.0.0.0:{port}/unban    - Remove IP from bans (auth required)")
    print(f"  GET  http://0.0.0.0:{port}/audit    - View audit log (auth required)")
    print(f"  GET  http://0.0.0.0:{port}/health   - Health check (public)")
    
    print(f"\nAuthentication:")
    print(f"  Header:  X-API-KEY: <your-key>")
    print(f"  Query:   ?key=<your-key>")
    
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
