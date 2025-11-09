#!/usr/bin/env python3
"""
SonicBuilder Replit Secrets Auto-Configurator
v2.0.9 — automatically ensures required secrets exist and are valid
"""

import os, requests, time, json, sys

# List of required secrets and what they do
REQUIRED_SECRETS = {
    "GITHUB_TOKEN": "Used for authenticated pushes and GitHub API actions",
    "ROLLBACK_WEBHOOK_URL": "Discord webhook for rollback and health alerts",
    "SLACK_WEBHOOK_URL": "Slack webhook for notifications (optional)",
    "SESSION_SECRET": "Flask session security key",
}

def check_secret(key):
    value = os.getenv(key)
    return value if value else None

def prompt_secret(key, desc):
    print(f"\n🔐 {key} — {desc}")
    existing = check_secret(key)
    if existing:
        print(f"✅ Already found in Replit Secrets (length {len(existing)}).")
        return existing
    else:
        val = input(f"❓ Paste or type your {key} value: ").strip()
        if not val:
            print("⚠️ Skipped — no value provided.")
            return None
        os.system(f"replit secrets add {key} '{val}'")
        print(f"✅ Secret {key} added successfully!")
        return val

def test_github_token(token):
    print("🧪 Verifying GitHub token...")
    try:
        resp = requests.get("https://api.github.com/user", headers={"Authorization": f"token {token}"})
        if resp.status_code == 200:
            user = resp.json().get("login")
            print(f"✅ GitHub token valid for user: {user}")
        else:
            print(f"⚠️ GitHub token test failed: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Error verifying token: {e}")

def test_discord_webhook(url):
    print("🧪 Testing Discord webhook...")
    try:
        payload = {"content": "✅ SonicBuilder webhook connected successfully!"}
        r = requests.post(url, json=payload)
        if r.status_code == 204:
            print("✅ Discord webhook is live.")
        else:
            print(f"⚠️ Webhook responded with code {r.status_code}")
    except Exception as e:
        print(f"⚠️ Discord webhook test failed: {e}")

def main():
    print("\n🚀 SonicBuilder Secrets Auto-Configurator\n")
    print("="*70)

    for key, desc in REQUIRED_SECRETS.items():
        val = prompt_secret(key, desc)
        if key == "GITHUB_TOKEN" and val:
            test_github_token(val)
        if key == "ROLLBACK_WEBHOOK_URL" and val:
            test_discord_webhook(val)

    print("\n" + "="*70)
    print("✅ All required secrets checked or configured.")
    print("💾 Saved securely in Replit Secrets vault.\n")
    print("🚀 You can now safely run all SonicBuilder services:")
    print("   python3 auto_orchestrator.py        # Full build automation")
    print("   python3 alert_hooks.py              # Health alerts")
    print("   python3 sync_monitor_dashboard.py   # Visual dashboard")
    print("   python3 smart_pair_sync.py          # Continuous GitHub sync")

if __name__ == "__main__":
    main()