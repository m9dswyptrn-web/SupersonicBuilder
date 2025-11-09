import subprocess, os

scripts = [
    "build_supersonic_core.py",
    "build_supersonic_security.py",
    "build_supersonic_diagnostics.py",
    "build_supersonic_addons.py",
    "build_supersonic_failsafe.py"
]

for script in scripts:
    path = os.path.join("setup", script)
    subprocess.run(["python3", path], check=True)

print("\n🚀  All Supersonic bundles built successfully!\n"
      "Upload them to Replit root to auto-install.")
