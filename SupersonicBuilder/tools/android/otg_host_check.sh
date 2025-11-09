#!/data/data/com.termux/files/usr/bin/bash
set -e
echo "[*] SonicBuilder OTG Host Checker"
which termux-usb >/dev/null 2>&1 || { echo "Install termux-api: pkg install termux-api"; exit 1; }
termux-usb -l || true
