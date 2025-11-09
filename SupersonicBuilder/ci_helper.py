#!/usr/bin/env python3
"""
SonicBuilder Smart CI Helper v2.0.9
Simulates build, verify, rollback, artifact + notifications locally.
"""

import os, json, time, hashlib, requests, shutil, datetime, zipfile, subprocess

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
REPO          = os.getenv("GITHUB_REPOSITORY", "m9dswyptrn-web/SonicBuilder")
RUN_ID        = os.getenv("GITHUB_RUN_ID", "local-" + str(int(time.time())))
RUN_NUMBER    = os.getenv("GITHUB_RUN_NUMBER", "0")
COMMIT_SHA    = os.getenv("GITHUB_SHA", "local")
ARTIFACT_DIR  = "artifacts"
STATUS_DIR    = "docs/status"
LOG_DIR       = "logs"
WEBHOOKS      = {
    "discord": os.getenv("ROLLBACK_WEBHOOK_URL"),
    "slack":   os.getenv("SLACK_WEBHOOK_URL"),
}
# ─────────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.datetime.utcnow().isoformat()
    print(f"[{ts}] {msg}")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(f"{LOG_DIR}/ci.log", "a") as f:
        f.write(f"{ts} {msg}\n")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:12]

def notify_all(msg, level="info"):
    """Send dual notifications."""
    emoji = {"info":"🟢","warn":"🟡","error":"🔴"}[level]
    color = {"info":65280,"warn":16776960,"error":16711680}[level]
    payload_discord = {
        "username": "SonicBuilder Smart CI",
        "embeds": [{
            "title": f"{emoji} SonicBuilder Deployment",
            "description": msg,
            "color": color,
            "footer": {"text": f"UTC {datetime.datetime.utcnow().isoformat()}"}
        }]
    }
    payload_slack = {"text": f"{emoji} *SonicBuilder* — {msg}"}
    for name,url in WEBHOOKS.items():
        if not url: continue
        try:
            requests.post(url, json=(payload_discord if name=="discord" else payload_slack), timeout=8)
            log(f"Sent {name} notification.")
        except Exception as e:
            log(f"Notify {name} failed: {e}")

def verify_pdfs():
    ok = True
    for root,_,files in os.walk("docs"):
        for fn in files:
            if fn.endswith(".pdf"):
                path = os.path.join(root,fn)
                size = os.path.getsize(path)
                if size < 2000:
                    log(f"❌ {fn} too small ({size} B)"); ok=False
                else:
                    log(f"✅ {fn} OK ({size/1024:.1f} KB)")
    
    # Also check docs_build
    for root,_,files in os.walk("docs_build"):
        for fn in files:
            if fn.endswith(".pdf"):
                path = os.path.join(root,fn)
                size = os.path.getsize(path)
                if size < 2000:
                    log(f"❌ {fn} too small ({size} B)"); ok=False
                else:
                    log(f"✅ {fn} OK ({size/1024:.1f} KB)")
    
    return ok

def gen_health_feed(status="success"):
    os.makedirs(STATUS_DIR, exist_ok=True)
    feed = {
        "build_id": RUN_NUMBER,
        "commit": COMMIT_SHA,
        "status": status,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "artifacts": os.listdir(ARTIFACT_DIR) if os.path.exists(ARTIFACT_DIR) else [],
    }
    with open(f"{STATUS_DIR}/health.json","w") as f: json.dump(feed,f,indent=2)
    log("🧩 health.json updated")

def archive_artifacts():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    out = f"{ARTIFACT_DIR}/SonicBuilder_{RUN_ID}.zip"
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for folder in ("docs","logs","scripts"):
            if not os.path.exists(folder):
                continue
            for root,_,files in os.walk(folder):
                for f in files:
                    path = os.path.join(root,f)
                    z.write(path)
    log(f"📦 Artifact archived: {out}")
    return out

def rollback():
    log("⚠️ Rolling back to previous healthy commit...")
    if os.path.exists("rollback_backup.zip"):
        shutil.unpack_archive("rollback_backup.zip",".")
        log("Rollback restored from backup.")
    else:
        log("No rollback backup found!")

def main():
    log("🚀 SonicBuilder Smart CI Helper starting…")
    notify_all("Local CI test run starting.", "info")

    try:
        # simulate build
        time.sleep(1)
        ok = verify_pdfs()
        status = "success" if ok else "rollback"
        gen_health_feed(status)
        archive_artifacts()

        if ok:
            notify_all("Build verification passed ✅", "info")
        else:
            rollback()
            notify_all("Build failed, rollback executed 🔴", "error")

        log("✅ CI run complete.")
    except Exception as e:
        log(f"Unhandled Error: {e}")
        notify_all(f"Exception occurred {e}", "error")

if __name__ == "__main__":
    main()
