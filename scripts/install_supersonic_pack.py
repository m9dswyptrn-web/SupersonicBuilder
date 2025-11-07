#!/usr/bin/env python3
"""
Supersonic Control & Health Pack - Idempotent Installer
Patches serve_pdfs.py and Makefile to add doctor endpoints and Control Panel.
"""
import os
import sys
import re
from pathlib import Path

def backup_file(filepath):
    """Create a .bak backup if it doesn't exist"""
    bak = f"{filepath}.bak"
    if not os.path.exists(bak) and os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        with open(bak, 'w') as f:
            f.write(content)
        print(f"✅ Backed up {filepath} → {bak}")
    return bak

def patch_serve_pdfs():
    """Patch serve_pdfs.py to add endpoints and /panel route"""
    filepath = "serve_pdfs.py"
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "doctor_endpoints_secure" in content:
        print(f"✅ {filepath} already patched (doctor_endpoints_secure found)")
        return True
    
    # Add imports after existing imports
    import_patch = """
# Supersonic Control & Health Pack
from tools.doctor_endpoints_secure import mount_health_endpoints, mount_sync_endpoints
"""
    
    # Find a good place to insert imports (after Flask import)
    if "from flask import" in content:
        content = content.replace(
            "from flask import",
            import_patch + "\nfrom flask import"
        )
    else:
        print("⚠️  Could not find Flask import, adding at top")
        content = import_patch + "\n" + content
    
    # Add endpoint mounting before app.run()
    endpoint_mount = """
# Mount Supersonic Control & Health endpoints
mount_health_endpoints(app)
mount_sync_endpoints(app)

@app.route('/panel')
def panel():
    from flask import render_template
    return render_template('panel.html')

"""
    
    # Insert before if __name__ == '__main__'
    if 'if __name__ ==' in content:
        content = content.replace(
            'if __name__ ==',
            endpoint_mount + '\nif __name__ =='
        )
    else:
        content += "\n" + endpoint_mount
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Patched {filepath} with doctor endpoints and /panel route")
    return True

def patch_makefile():
    """Add make panel, doctor, snapshot targets to Makefile"""
    filepath = "Makefile"
    if not os.path.exists(filepath):
        print(f"⚠️  {filepath} not found, skipping")
        return True
    
    backup_file(filepath)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "make panel" in content or "Supersonic Control Panel" in content:
        print(f"✅ {filepath} already has panel/doctor targets")
        return True
    
    # Add targets at the end
    makefile_patch = """
# --- Supersonic Control Panel & Doctor ---
.PHONY: panel doctor snapshot

panel:
\tpython -c "import webbrowser; webbrowser.open('http://127.0.0.1:5000/panel')"

doctor:
\tcurl -s http://127.0.0.1:5000/health | python3 -m json.tool

snapshot:
\tpython3 scripts/snapshot_full.py
# --- End Supersonic Pack ---
"""
    
    content += "\n" + makefile_patch
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Added panel/doctor/snapshot targets to {filepath}")
    return True

def verify_files():
    """Verify all required files are present"""
    required = {
        "tools/doctor_endpoints_secure.py": "Doctor endpoints module",
        "templates/panel.html": "Control Panel UI",
        "scripts/snapshot_full.py": "Snapshot tool"
    }
    
    missing = []
    for filepath, desc in required.items():
        if not os.path.exists(filepath):
            missing.append(f"{filepath} ({desc})")
    
    if missing:
        print("\n⚠️  Missing files:")
        for item in missing:
            print(f"   - {item}")
        print("\nPlease ensure the Supersonic Pack is fully extracted.")
        return False
    
    print("✅ All required files present")
    return True

def main():
    print("═" * 70)
    print("Supersonic Control & Health Pack - Installer v4 Ultimate")
    print("═" * 70)
    print()
    
    if not verify_files():
        sys.exit(1)
    
    success = True
    success = patch_serve_pdfs() and success
    success = patch_makefile() and success
    
    print()
    print("═" * 70)
    if success:
        print("✅ Installation Complete!")
        print()
        print("Next steps:")
        print("  1. (Optional) Set ADMIN_TOKEN in Replit Secrets for security")
        print("  2. Restart your Flask server")
        print("  3. Visit http://127.0.0.1:5000/panel")
        print()
        print("Make targets:")
        print("  make panel     - Open Control Panel in browser")
        print("  make doctor    - Quick health check")
        print("  make snapshot  - Create full project snapshot")
    else:
        print("⚠️  Installation completed with warnings")
    print("═" * 70)

if __name__ == "__main__":
    main()
