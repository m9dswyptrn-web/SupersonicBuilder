# scripts/repo_url.py
"""
Canonical repository URL resolver for SonicBuilder tools.
Priority:
1) Explicit provided URL (argument)
2) env SB_REPO_URL
3) env GITHUB_REPOSITORY -> https://github.com/<slug>
4) Replit fallback (current app URL)
"""

import os

DEFAULT_REPLIT = "https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev"

def resolve(url: str | None = None) -> str:
    if url: return url
    env = os.environ.get("SB_REPO_URL")
    if env: return env
    gh = os.environ.get("GITHUB_REPOSITORY")
    if gh: return f"https://github.com/{gh}"
    return DEFAULT_REPLIT
