#!/usr/bin/env python3
import re, json, pathlib, sys
BASE = pathlib.Path(__file__).resolve().parents[1]
ROOT = BASE / "docs" / "diagrams"
OUT  = BASE / "data" / "diagrams_index.json"

# expected filenames: <make>/<model>/<year>/<id>.<variant>.<ext>
PATTERN = re.compile(r"^(?P<id>.+?)\.(?P<variant>dark|light)\.(?P<ext>pdf|png)$", re.I)

def main():
    index = {}
    for path in ROOT.rglob("*.*"):
        if not path.is_file():
            continue
        try:
            make = path.parents[2].name
            model = path.parents[1].name
            year = path.parents[0].name
        except IndexError:
            continue
        m = PATTERN.match(path.name)
        if not m:
            continue
        gid = m["id"]
        variant = m["variant"].lower()
        ext = m["ext"].lower()

        index.setdefault(make.title(), {}) \
             .setdefault(model.title(), {}) \
             .setdefault(year, [])

        # find or create diagram record
        bucket = index[make.title()][model.title()][year]
        rec = next((d for d in bucket if d["id"] == gid), None)
        if not rec:
            rec = {
                "id": gid,
                "name": gid.replace("_"," ").title(),
                "category": "unknown",
                "variants": [],
                "formats": [],
                "files": {"pdf": {}, "png": {}}
            }
            bucket.append(rec)

        if variant not in rec["variants"]:
            rec["variants"].append(variant)
        if ext not in rec["formats"]:
            rec["formats"].append(ext)

        rel = path.as_posix().split(str(BASE.as_posix()) + "/")[-1]
        rec["files"].setdefault(ext, {})[variant] = rel

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    sys.exit(main())