#!/usr/bin/env python3
"""Convert uploaded config files to structured YAML"""
import json
import yaml
from pathlib import Path

TEXT_DIR = Path("uploaded_content/text_files")
CONFIG_DIR = Path("config/library")
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Config files (key=value format)
CONFIG_FILES = [
    "text 17.txt", "text 21.txt", "text 23.txt", "text 24.txt", "text 25.txt",
    "text 28.txt", "text 29.txt", "text 31.txt", "text 32.txt", "text 33.txt",
    "text 34.txt", "text 35.txt", "text 36.txt", "text 37.txt", "text 40.txt"
]

configs = {}
for fname in CONFIG_FILES:
    fpath = TEXT_DIR / fname
    if fpath.exists():
        content = fpath.read_text().strip()
        if content:
            num = fname.replace("text ", "").replace(".txt", "")
            config_data = {}
            for line in content.splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    try:
                        key, val = line.split("=", 1)
                        config_data[key.strip()] = val.strip()
                    except:
                        pass
            if config_data:
                configs[f"upload_{num}"] = config_data

# Save as YAML
for name, data in configs.items():
    yaml_path = CONFIG_DIR / f"{name}.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"✅ Created: {yaml_path}")

print(f"\n📊 Total configs converted: {len(configs)}")
