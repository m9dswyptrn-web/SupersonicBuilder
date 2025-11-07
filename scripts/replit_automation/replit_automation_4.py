#!/usr/bin/env python3
import sys, time, argparse, urllib.request, urllib.error, json

DEFAULT_PATHS = ["/", "/healthz", "/readyz"]

def fetch(url: str, timeout: float = 3.0):
    req = urllib.request.Request(url, headers={"User-Agent": "supersonic-healthcheck/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return r.getcode(), body

def main():
    p = argparse.ArgumentParser(description="Supersonic health check")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--paths", nargs="*", default=DEFAULT_PATHS)
    p.add_argument("--retries", type=int, default=30)
    p.add_argument("--sleep", type=float, default=1.0)
    p.add_argument("--timeout", type=float, default=3.0)
    args = p.parse_args()

    base = f"http://{args.host}:{args.port}"
    ok = False

    for attempt in range(1, args.retries + 1):
        try:
            all_ok = True
            for path in args.paths:
                url = base + path
                code, body = fetch(url, timeout=args.timeout)

                if path in ("/healthz", "/readyz"):
                    # expect JSON payloads here
                    try:
                        data = json.loads(body.decode("utf-8"))
                        if path == "/readyz" and data.get("status") not in ("ready", "ok"):
                            all_ok = False
                    except Exception:
                        all_ok = False

                if code != 200:
                    all_ok = False

            if all_ok:
                print(f"[OK] {base} passed health checks on attempt {attempt}")
                ok = True
                break
            else:
                print(f"[WAIT] {base} unhealthy on attempt {attempt} …")
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"[ERR] {base} check failed on attempt {attempt}: {e}")
        time.sleep(args.sleep)

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()