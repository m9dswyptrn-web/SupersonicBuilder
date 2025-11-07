import zipfile, os

def build_diag():
    with zipfile.ZipFile("Supersonic_Diagnostics.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk("scripts/diagnostics"):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, ".")
                z.write(full, rel)
        if os.path.exists("diagnose_first_run.log"):
            z.write("diagnose_first_run.log")
    print("🩺  Supersonic_Diagnostics.zip built.")

if __name__ == "__main__":
    build_diag()
