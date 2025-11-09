#!/usr/bin/env python3
"""
Supersonic Control Core Doctor — v4
Performs a complete environment check and prints actionable diagnostics.
"""
import os, shutil, sys, subprocess
from pathlib import Path

CHECKS = {
    "python_version": sys.version,
    "cosign": shutil.which("cosign"),
    "adb": shutil.which("adb"),
    "git": shutil.which("git"),
    "openai_key": bool(os.getenv("OPENAI_API_KEY")),
    "discord_webhook": bool(os.getenv("SUP_DISCORD_WEBHOOK")),
    "slack_webhook": bool(os.getenv("SUP_SLACK_WEBHOOK")),
}

def banner():
    print("="*60)
    print("🚀 Supersonic Control Core Doctor v4")
    print("="*60)

def check(name, result):
    status = "✅" if result else "⚠️"
    print(f"{status} {name:<20} : {result}")

def main():
    banner()
    for k,v in CHECKS.items():
        check(k, v)
    print("\nRun `pip install watchdog colorama rich pyttsx3 playsound requests semver` if any module errors appear.")
    print("Doctor completed ✅")

if __name__ == "__main__":
    main()
