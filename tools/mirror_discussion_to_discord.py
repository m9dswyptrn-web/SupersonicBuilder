#!/usr/bin/env python3
"""
Create a thread in a Discord Forum channel for a release discussion.
Env:
  DISCORD_BOT_TOKEN            (required)
  DISCORD_FORUM_CHANNEL_ID     (required)
Args:
  --title "Release vX.Y.Z"
  --content "summary text"
"""
from __future__ import annotations
import os, sys, json, urllib.request

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--content", default="")
    args=ap.parse_args()

    token = os.getenv("DISCORD_BOT_TOKEN","").strip()
    chan  = os.getenv("DISCORD_FORUM_CHANNEL_ID","").strip()
    if not token or not chan:
        print("Discord bot token or channel id missing.", file=sys.stderr); sys.exit(1)

    url = f"https://discord.com/api/v10/channels/{chan}/threads"
    payload = {
        "name": args.title[:95],
        "auto_archive_duration": 10080,
        "rate_limit_per_user": 0,
        "message": {
            "content": args.content[:1900]
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        r.read()
    print("Discord forum thread created.")

if __name__=="__main__":
    main()
