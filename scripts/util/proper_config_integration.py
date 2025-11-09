#!/usr/bin/env python3
"""Properly integrate ALL uploaded config-like files"""
import yaml
import json
from pathlib import Path

TEXT_DIR = Path("uploaded_content/text_files")
CONFIG_DIR = Path("config/library")
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Map files to their actual type
configs = {}

# Nix config (text 17)
if (TEXT_DIR / "text 17.txt").exists():
    configs["nix_deps"] = {
        "description": "Nix package dependencies",
        "packages": ["python3", "python311Packages.reportlab"],
        "source": "text 17.txt"
    }

# Environment exports (text 21, 23, 24, 29, 32)
for num, desc in [
    ("21", "Android DSP path export"),
    ("23", "Android DSP path export"),
    ("24", "Android ADB configuration"),
    ("29", "ADB enable flag"),
    ("32", "ADB enable flag")
]:
    f = TEXT_DIR / f"text {num}.txt"
    if f.exists():
        content = f.read_text().strip()
        env_vars = {}
        for line in content.splitlines():
            if line.strip().startswith("export "):
                line = line.replace("export ", "")
                if "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
        if env_vars:
            configs[f"env_{num}"] = {
                "description": desc,
                "environment": env_vars,
                "source": f"text {num}.txt"
            }

# Variable definitions (text 25, 28, 31, 33, 34, 40)
for num in ["25", "28", "31", "33", "34", "35", "36", "37", "40"]:
    f = TEXT_DIR / f"text {num}.txt"
    if f.exists():
        content = f.read_text().strip()
        vars_dict = {}
        for line in content.splitlines():
            if "=" in line and not line.strip().startswith(("#", "export", "./")):
                try:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    vars_dict[k] = v
                except:
                    pass
        if vars_dict:
            configs[f"vars_{num}"] = {
                "description": f"Variables from text {num}.txt",
                "variables": vars_dict,
                "source": f"text {num}.txt"
            }

# Save all configs
for name, data in configs.items():
    yaml_path = CONFIG_DIR / f"{name}.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    # Validate
    with open(yaml_path, 'r') as f:
        test = yaml.safe_load(f)
    print(f"✅ {yaml_path.name}")

print(f"\n📊 Total: {len(configs)} configs integrated and validated")
