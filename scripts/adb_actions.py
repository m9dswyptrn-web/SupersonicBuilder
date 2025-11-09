#!/usr/bin/env python3
"""
ADB toolkit for head-unit deployment and diagnostics.
Automatically installs platform-tools if missing.
"""
import os, subprocess, platform, tempfile, urllib.request, zipfile, shutil
from pathlib import Path

def get_adb_url():
    system = platform.system()
    if system == "Windows":
        return "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    elif system == "Darwin":
        return "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
    else:  # Linux and others
        return "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"

ADB_URL = get_adb_url()

def ensure_adb():
    if shutil.which("adb"): return
    print("ADB not found. Installing ...")
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td)/"adb.zip"
        urllib.request.urlretrieve(ADB_URL, zpath)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(td)
        tools = next(Path(td).glob("platform-tools"))
        dest = Path.cwd()/ "platform-tools"
        if dest.exists(): shutil.rmtree(dest)
        shutil.move(str(tools), str(dest))
        print(f"ADB installed to {dest}. Add it to PATH if needed.")

def adb(args):
    ensure_adb()
    subprocess.run(["platform-tools/adb"]+args)

if __name__=="__main__":
    import sys
    if len(sys.argv)<2:
        print("Usage: adb_actions.py [deploy|reboot|logs] [apk]")
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd=="deploy":
        apk=sys.argv[2] if len(sys.argv)>2 else None
        if not apk or not Path(apk).exists():
            print("APK file missing.")
            sys.exit(1)
        adb(["install","-r",apk])
    elif cmd=="reboot":
        adb(["reboot"])
    elif cmd=="logs":
        adb(["logcat","-d"])
