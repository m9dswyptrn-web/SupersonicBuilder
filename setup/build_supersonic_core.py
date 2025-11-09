import zipfile, os, shutil, pathlib

core_files = [
    "install_supersonic.sh",
    "restore_baseline.sh",
    "requirements.txt",
    "scripts/",
    ".github/workflows/",
    "README.md",
    ".replit"
]

def build_zip():
    with zipfile.ZipFile("Supersonic_Core.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for path in core_files:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        full = os.path.join(root, f)
                        rel = os.path.relpath(full, ".")
                        z.write(full, rel)
            elif os.path.exists(path):
                z.write(path, os.path.basename(path))
    print("✅  Supersonic_Core.zip built.")

if __name__ == "__main__":
    build_zip()
