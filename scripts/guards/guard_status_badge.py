#!/usr/bin/env python3
import os, json, urllib.request

OWNER = os.getenv("OWNER", "m9dswyptrn-web")
REPO  = os.getenv("REPO",  "SonicBuilder")
TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

def gh_json(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def get_last_guard_issue():
    # Find most recent open or recently closed guard issue
    q = f"repo:{OWNER}/{REPO} in:title [Guard] Post-release issues detected sort:updated-desc"
    url = f"https://api.github.com/search/issues?q={urllib.request.quote(q)}&per_page=1"
    data = gh_json(url)
    items = data.get("items", [])
    return items[0] if items else None

def main():
    # Default badge (unknown)
    badge = {"schemaVersion":1,"label":"post-release guard","message":"unknown","color":"lightgrey","labelColor":"2f363d"}

    try:
        issue = get_last_guard_issue()
        if issue:
            state = issue.get("state","open")
            title = issue.get("title","guard issue")
            number = issue.get("number")
            url = issue.get("html_url")
            if state == "open":
                badge["message"] = f"issue #{number} open"
                badge["color"]   = "red"
            else:
                badge["message"] = f"last issue closed"
                badge["color"]   = "brightgreen"
            badge["namedLogo"] = "github"
            badge["logoColor"] = "white"
        else:
            badge["message"] = "no issues"
            badge["color"]   = "brightgreen"
    except Exception as e:
        badge["message"] = "error"
        badge["color"]   = "orange"

    os.makedirs("docs/badges", exist_ok=True)
    with open("docs/badges/guard_status.json","w",encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)
    print(json.dumps(badge, indent=2))

if __name__ == "__main__":
    main()
