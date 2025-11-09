# Repository URL Management (Single Source of Truth)

Use `scripts/repo_url.py` to resolve the canonical project URL for **all** tools.

Priority:
1. CLI-provided URL
2. `SB_REPO_URL` env var
3. `GITHUB_REPOSITORY` env var → `https://github.com/<slug>`
4. Replit fallback URL

Always pass the resolved URL into QR generators, PDF stampers, and release notes.
