# USING_SB_REPO_URL

`SB_REPO_URL` resolves like this:
1. GitHub repository slug → `https://github.com/<slug>`
2. Fallback: your current Replit app URL
   `https://08abbd3d-777f-4af5-b274-466c8cc1c573-00-1ko1zjf07c39i.riker.replit.dev`

To override explicitly, set a secret or env in your workflow:

```yaml
env:
  SB_REPO_URL: https://github.com/YourUser/YourRepo
```
