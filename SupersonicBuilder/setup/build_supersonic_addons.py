import zipfile, os

def build_addons():
    with zipfile.ZipFile("Supersonic_Addons.zip", "w", zipfile.ZIP_DEFLATED) as z:
        addon_dirs = ["scripts/addons", "scripts/enhancements", "tools/addons"]
        for addon_dir in addon_dirs:
            if os.path.isdir(addon_dir):
                for root, _, files in os.walk(addon_dir):
                    for f in files:
                        full = os.path.join(root, f)
                        rel = os.path.relpath(full, ".")
                        z.write(full, rel)
    print("🎨  Supersonic_Addons.zip built.")

if __name__ == "__main__":
    build_addons()
