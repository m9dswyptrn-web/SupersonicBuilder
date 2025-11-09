import zipfile, os

def build_security():
    with zipfile.ZipFile("Supersonic_Security.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk("scripts/security"):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, ".")
                z.write(full, rel)
        z.write("requirements.txt")
        z.write("restore_baseline.sh")
    print("🔐  Supersonic_Security.zip built.")

if __name__ == "__main__":
    build_security()
