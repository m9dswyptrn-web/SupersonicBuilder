#!/usr/bin/env python3

# SonicBuilder CAN ID Helper v2.2.3
# Reads Teensy discovery CSV or raw JSON lines, counts IDs per bus, suggests tag stubs.
# Outputs:
#  - CSV summary: id,bus,count
#  - JSON tag template: { "HS": {"0x123":"TAG_NAME"}, "SW": {...} }
#
# Usage:
#   python tools/can/id_discovery_to_tags.py --in can_log.csv --out-prefix out/ids
#   python tools/can/id_discovery_to_tags.py --jsonl discovery.jsonl --out-prefix out/ids
import csv, json, argparse, sys
from collections import Counter, defaultdict
from pathlib import Path

def load_from_csv(p):
    hs, sw = Counter(), Counter()
    with open(p, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            bus = (row.get("bus") or "").strip().upper()
            cid = (row.get("id") or "").strip()
            if not cid: 
                continue
            if bus == "HS":
                hs[cid] += 1
            elif bus == "SW":
                sw[cid] += 1
    return hs, sw

def load_from_jsonl(p):
    hs, sw = Counter(), Counter()
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): 
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            bus = (obj.get("bus") or "").strip().upper()
            cid = (obj.get("id") or "").strip()
            if not cid: 
                continue
            if bus == "HS":
                hs[cid] += 1
            elif bus == "SW":
                sw[cid] += 1
    return hs, sw

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="incsv", help="CSV from usb_can_logger.py")
    ap.add_argument("--jsonl", help="Raw JSON lines from Teensy bridge")
    ap.add_argument("--out-prefix", default="out/ids")
    ap.add_argument("--top", type=int, default=50, help="suggest tags for top N per bus")
    A = ap.parse_args()
    Path("out").mkdir(exist_ok=True)
    if not A.incsv and not A.jsonl:
        print("Provide --in CSV or --jsonl JSONL", file=sys.stderr)
        sys.exit(2)

    hs, sw = Counter(), Counter()
    if A.incsv:
        h1, s1 = load_from_csv(A.incsv)
        hs += h1; sw += s1
    if A.jsonl:
        h2, s2 = load_from_jsonl(A.jsonl)
        hs += h2; sw += s2

    # Write CSV summary
    csv_path = Path(f"{A.out_prefix}_summary.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bus","id","count"])
        for bus, ctr in (("HS", hs), ("SW", sw)):
            for cid, cnt in ctr.most_common():
                w.writerow([bus, cid, cnt])

    # Write tag template JSON
    def make_template(ctr, n):
        return { cid: "TAG_ME" for cid,_ in ctr.most_common(n) }
    tag_json = {
        "HS": make_template(hs, A.top),
        "SW": make_template(sw, A.top)
    }
    json_path = Path(f"{A.out_prefix}_tag_template.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tag_json, f, indent=2)

    print("Wrote:", csv_path, json_path)

if __name__ == "__main__":
    main()
