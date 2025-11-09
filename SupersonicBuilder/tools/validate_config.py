#!/usr/bin/env python3
import os, glob, yaml, sys
def find_refs(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    refs = []
    for k in ("diagram","photo","diagram_right","left_image","right_image"):
        v = data.get(k)
        if v and isinstance(v, str):
            base = v if not v.startswith("assets/") else v[len("assets/"):]
            refs.append(base)
    return refs
def main():
    missing = []
    cfgs = sorted(glob.glob("config/*.yaml"))
    assets = set()
    for a in glob.glob("assets/*"): 
        if os.path.isfile(a): assets.add(os.path.basename(a))
    for a in glob.glob("assets/**/*", recursive=True):
        if os.path.isfile(a): assets.add(os.path.relpath(a, "assets"))
    for c in cfgs:
        for ref in find_refs(c):
            ok = False
            for ext in ("",".svg",".png",".jpg",".jpeg",".JPG",".JPEG"):
                candidate = ref + ext if not ref.startswith("assets/") else ref[7:] + ext
                if candidate in assets:
                    ok = True; break
            if not ok: missing.append((c, ref))
    if missing:
        print("Missing assets referenced in YAML:")
        for c, r in missing:
            print(f" - {c}: assets/{r}(.svg|.png|.jpg)")
        sys.exit(1)
    print("All assets referenced by YAML exist. ✅")
if __name__ == "__main__":
    main()
