#!/usr/bin/env python3
import os, sys, json, time
from urllib.request import urlopen, Request

URL = os.getenv("PAGES_GALLERY_URL", "https://m9dswyptrn-web.github.io/SonicBuilder/docs/images/mobo_back/gallery.html")
TIMEOUT = float(os.getenv("PAGES_SMOKE_TIMEOUT", "10"))

def fetch(url):
    t0 = time.time()
    r = urlopen(Request(url, headers={"Cache-Control":"no-cache"}), timeout=TIMEOUT)
    dt = time.time() - t0
    body = r.read().decode("utf-8","ignore")
    return r.getcode(), dt, body

def check(url):
    try:
        code, dt, body = fetch(url)
        ok = (code == 200 and "<html" in body.lower())
        return {"url": url, "status": code, "latency_ms": int(dt*1000), "ok": ok}
    except Exception as e:
        return {"url": url, "status": "error", "latency_ms": None, "ok": False, "error": str(e)}

def main():
    dark = check(URL)
    light = check(URL + ("&" if "?" in URL else "?") + "theme=light")
    overall = dark["ok"] and light["ok"]
    color = "brightgreen" if overall else ("orange" if (dark["ok"] or light["ok"]) else "red")
    msg = "ok" if overall else ("partial" if (dark["ok"] or light["ok"]) else "down")
    badge = {"schemaVersion":1,"label":"pages smoke","message":msg,"color":color,"labelColor":"2f363d"}
    os.makedirs("docs/status", exist_ok=True)
    with open("docs/status/pages_smoke_status.json","w",encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)
    print(json.dumps({"dark": dark, "light": light, "overall": overall}, indent=2))

if __name__ == "__main__":
    sys.exit(main())
