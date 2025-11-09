#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
import textwrap

ROOT = Path(".")

def create_dir(p: Path):
    if not p.exists():
        p.mkdir(parents=True)
        print(f"🆕 Created: {p}")
    else:
        print(f"✅ Exists: {p}")

def ensure_version():
    vf = ROOT/"VERSION"
    if not vf.exists():
        vf.write_text("v0.0.1", encoding="utf-8")
        print("🆕 Created VERSION file with v0.0.1")
    else:
        print("✅ VERSION file already exists")

def ensure_yaml():
    cfg = ROOT/"config"; create_dir(cfg)
    yml = cfg/"pinout_44pin.yaml"
    if not yml.exists():
        sample = textwrap.dedent("""
        # Example pinout for 2014 Chevy Sonic LTZ (sample)
        pinout:
          - pin: 10
            name: "Right AUX Input +"
            color: "green"
            function: "Auxiliary Audio Input Right (+)"
          - pin: 11
            name: "AUX Detect"
            color: "blue"
            function: "Auxiliary Detection Signal"
          - pin: 23
            name: "AUX Common"
            color: "brown"
            function: "Auxiliary Audio Common"
          - pin: 24
            name: "Left AUX Input +"
            color: "gray"
            function: "Auxiliary Audio Input Left (+)"
          - pin: 38
            name: "Chassis Ground"
            color: "black"
            function: "Ground"
          - pin: 44
            name: "Battery B+"
            color: "red/blue"
            function: "12V Constant"
        """).strip()+"\n"
        yml.write_text(sample, encoding="utf-8")
        print(f"🆕 Seeded example: {yml}")
    else:
        print(f"✅ {yml} already exists")

def ensure_assets(): create_dir(ROOT/"assets")
def ensure_build():  create_dir(ROOT/"build")
def ensure_scripts_and_tools():
    create_dir(ROOT/"scripts")
    create_dir(ROOT/"tools")

def ensure_python_deps():
    missing=[]
    for mod in ("reportlab","PIL"):
        try:
            __import__("PIL.Image" if mod=="PIL" else mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"⚠️ Missing Python deps: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable,"-m","pip","install"]+missing)
            print("✅ Installed missing deps")
        except Exception as e:
            print(f"❌ Failed to auto-install: {e}")
    else:
        print("✅ Python deps already satisfied")

def main():
    print("🧰 Sonic Doctor Fix — auto repair starting...\n")
    ensure_assets(); ensure_build(); ensure_scripts_and_tools()
    ensure_version(); ensure_yaml(); ensure_python_deps()
    print("\n✅ Done. You can re-run: make doctor")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
