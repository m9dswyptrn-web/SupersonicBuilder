#!/usr/bin/env python3
import os, json, time, pathlib, hashlib

ROOT = pathlib.Path(".").resolve()
DL = ROOT / "downloads"
OUT = DL / "index.json"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    DL.mkdir(parents=True, exist_ok=True)
    items = []
    for p in sorted(DL.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.name == "latest.pdf":
            continue  # Skip symlink/copy
        st = p.stat()
        items.append({
            "name": p.name,
            "href": f"/SonicBuilder/downloads/{p.name}",
            "bytes": st.st_size,
            "mb": round(st.st_size/1024/1024, 2),
            "mtime": int(st.st_mtime),
            "mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
            "md5": md5(p),
        })
    latest = items[0]["name"] if items else None
    output_data = {
        "generated": time.time(),
        "latest": latest,
        "count": len(items),
        "items": items
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"✅ Wrote {OUT} with {len(items)} item(s).")

if __name__ == "__main__":
    main()
