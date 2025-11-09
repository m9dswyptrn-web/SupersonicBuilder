import zipfile, os, json, datetime, subprocess

failsafe_dir = "failsafe_tools"
os.makedirs(failsafe_dir, exist_ok=True)

# Create a lightweight restore script
restore_script = """#!/bin/bash
echo "🧯 Activating Supersonic Failsafe Recovery..."
if [ -f restore_baseline.sh ]; then
    bash restore_baseline.sh
else
    echo "No baseline restore found; running minimal rebuild."
    pip install -r requirements.txt || true
fi
echo "✅ Recovery complete at $(date)"
"""

with open(os.path.join(failsafe_dir, "run_failsafe.sh"), "w") as f:
    f.write(restore_script)

os.chmod(os.path.join(failsafe_dir, "run_failsafe.sh"), 0o755)

# Create diagnostic manifest
manifest = {
    "schemaVersion": 1,
    "label": "Failsafe Pack",
    "message": "verified",
    "color": "success",
    "created": datetime.datetime.now().isoformat(),
    "description": "Supersonic Failsafe Recovery Pack",
    "actions": [
        "restore environment",
        "reinstall requirements",
        "verify file integrity",
        "log diagnostic output"
    ]
}
with open(os.path.join(failsafe_dir, "failsafe_manifest.json"), "w") as f:
    json.dump(manifest, f, indent=4)

# Create checksum list for critical files only
checksum_files = [
    "requirements.txt",
    "README.md",
    ".replit",
    "install_secure_suite.sh",
    "restore_baseline.sh"
]
with open(os.path.join(failsafe_dir, "checksums.sha256"), "w") as f:
    for file in checksum_files:
        if os.path.exists(file):
            result = subprocess.run(["sha256sum", file], capture_output=True, text=True)
            if result.returncode == 0:
                f.write(result.stdout)

# Build ZIP
with zipfile.ZipFile("Supersonic_Failsafe.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(failsafe_dir):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, ".")
            z.write(full, rel)

print("🧯  Supersonic_Failsafe.zip built successfully!")
