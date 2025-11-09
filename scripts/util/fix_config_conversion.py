#!/usr/bin/env python3
"""Properly convert all 15 config files to valid YAML"""
import yaml
from pathlib import Path

TEXT_DIR = Path("uploaded_content/text_files")
CONFIG_DIR = Path("config/library")
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# ALL config files (15 total)
CONFIG_FILES = [
    "text 17.txt", "text 21.txt", "text 23.txt", "text 24.txt", "text 25.txt",
    "text 28.txt", "text 29.txt", "text 31.txt", "text 32.txt", "text 33.txt",
    "text 34.txt", "text 35.txt", "text 36.txt", "text 37.txt", "text 40.txt"
]

converted = 0
for fname in CONFIG_FILES:
    fpath = TEXT_DIR / fname
    if not fpath.exists():
        print(f"⚠️  File not found: {fname}")
        continue
    
    content = fpath.read_text().strip()
    if not content:
        continue
    
    num = fname.replace("text ", "").replace(".txt", "")
    config_data = {}
    
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            try:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Properly handle lists and quoted values
                if val.startswith("[") and val.endswith("]"):
                    # Parse list
                    config_data[key] = eval(val)  # Safe since it's from our own files
                elif val.startswith('"') and val.endswith('"'):
                    config_data[key] = val[1:-1]
                elif val.startswith("'") and val.endswith("'"):
                    config_data[key] = val[1:-1]
                elif val.isdigit():
                    config_data[key] = int(val)
                elif val.lower() in ['true', 'false']:
                    config_data[key] = val.lower() == 'true'
                else:
                    config_data[key] = val
            except Exception as e:
                print(f"⚠️  Skipping line in {fname}: {line} ({e})")
    
    if config_data:
        yaml_path = CONFIG_DIR / f"upload_{num}.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        # Validate it loads correctly
        with open(yaml_path, 'r') as f:
            test = yaml.safe_load(f)
        print(f"✅ {yaml_path.name} ({len(config_data)} keys)")
        converted += 1

print(f"\n📊 Total: {converted}/15 configs converted and validated")
