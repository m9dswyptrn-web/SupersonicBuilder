#!/usr/bin/env python3
"""
Integrate legacy builders (text 12.txt and text 15.txt) into build system
These are complete Python builder scripts that should be made executable
"""
import shutil
from pathlib import Path

TEXT_DIR = Path("uploaded_content/text_files")
BUILDERS_DIR = Path("builders")
BUILDERS_DIR.mkdir(exist_ok=True)

# Legacy builders
legacy = [
    ("text 12.txt", "sonicbuilder_v1.0.0.py", "SonicBuilder v1.0.0"),
    ("text 15.txt", "sonicbuilder_v2.0.0.py", "SonicBuilder v2.0.0")
]

print("🔧 Integrating legacy builders into active build system...")
for txt, py, desc in legacy:
    src = TEXT_DIR / txt
    dst = BUILDERS_DIR / py
    if src.exists():
        content = src.read_text()
        # Add shebang if not present
        if not content.startswith("#!"):
            content = "#!/usr/bin/env python3\n" + content
        dst.write_text(content)
        dst.chmod(0o755)
        print(f"✅ {py} - {desc}")

# Create builder launcher
launcher = BUILDERS_DIR / "run_legacy.sh"
launcher.write_text("""#!/bin/bash
# Legacy Builder Launcher
echo "Available legacy builders:"
echo "  1. SonicBuilder v1.0.0"
echo "  2. SonicBuilder v2.0.0"
echo ""
echo "Usage:"
echo "  python3 builders/sonicbuilder_v1.0.0.py"
echo "  python3 builders/sonicbuilder_v2.0.0.py"
""")
launcher.chmod(0o755)

print(f"\n✅ Legacy builders now active in builders/ directory")
print(f"   Run with: python3 builders/sonicbuilder_v1.0.0.py")
print(f"   Run with: python3 builders/sonicbuilder_v2.0.0.py")
