# SonicBuilder Autodeploy System

Automated deployment system for SonicBuilder with built-in rollback capabilities.

## Features

- **Preflight Checks**: Verifies secrets and git configuration
- **Automated Commits**: Timestamps and pushes changes to GitHub
- **Rollback Recovery**: Automatic rollback on deployment failure
- **Deployment Logs**: JSON logs of all deployment attempts
- **GitHub Actions**: Automated deployment on push to main

## Quick Start

### 1. Set Up GitHub Token

```bash
# In Replit Secrets panel, add:
GITHUB_TOKEN=<your_personal_access_token>

# Or export in shell:
export GITHUB_TOKEN=<your_token>
```

### 2. Run Autodeploy

```bash
python3 founder_autodeploy/founder_autodeploy.py
```

Expected output:
```
╔════════════════════════════════════════════════════════════════╗
║     🚀 SonicBuilder Autodeploy System                         ║
╚════════════════════════════════════════════════════════════════╝

🔍 Running preflight check...
✅ All secrets present

🔍 Checking git status...
  📝 Found 5 changed files
  ✅ Git remote: https://github.com/m9dswyptrn-web/SonicBuilder.git

✅ Preflight checks passed

📦 Committing and pushing changes...
→ git add .
→ git commit -m "autodeploy: 2025-10-30 23:15:00 UTC"
→ git push origin main

✅ Successfully deployed at 2025-10-30 23:15:00 UTC

📄 Deployment log: founder_autodeploy/logs/deploy_2025-10-30T23-15-00.json

╔════════════════════════════════════════════════════════════════╗
║                 ✅ DEPLOYMENT SUCCESSFUL                       ║
╚════════════════════════════════════════════════════════════════╝
```

## Manual Rollback

### Rollback N Commits
```bash
python3 founder_autodeploy/rollback_helper.py --steps 1
```

### Rollback to Specific Commit
```bash
# List recent commits
python3 founder_autodeploy/rollback_helper.py --list-commits 10

# Rollback to specific commit
python3 founder_autodeploy/rollback_helper.py --commit abc123
```

### Rollback to Tag
```bash
# List available tags
python3 founder_autodeploy/rollback_helper.py --list-tags

# Rollback to tag
python3 founder_autodeploy/rollback_helper.py --tag v1.0.0
```

## GitHub Actions Integration

The `.github/workflows/autodeploy.yml` workflow automatically runs on:
- Every push to main branch
- Manual trigger via GitHub Actions UI

The workflow:
1. Checks out the repository
2. Sets up Python 3.11
3. Runs the autodeploy script
4. Uploads deployment logs as artifacts

## Deployment Logs

Logs are stored in `founder_autodeploy/logs/` with format:
```
deploy_2025-10-30T23-15-00.json
```

Example log:
```json
{
  "timestamp": "2025-10-30T23:15:00",
  "branch": "main",
  "repo": "m9dswyptrn-web/SonicBuilder",
  "success": true,
  "error": null
}
```

## Workflow Steps

### 1. Preflight Checks
- Verifies `GITHUB_TOKEN` environment variable
- Checks git status for changes
- Validates git remote configuration

### 2. Commit & Push
- Adds all changes with `git add .`
- Commits with timestamp: `autodeploy: 2025-10-30 23:15:00 UTC`
- Pushes to `main` branch

### 3. Rollback (on failure)
- Resets to previous commit: `git reset --hard HEAD~1`
- Force pushes to remote: `git push -f origin main`
- Logs error for debugging

## Configuration

Edit `founder_autodeploy/founder_autodeploy.py` to customize:

```python
REPO = "m9dswyptrn-web/SonicBuilder"  # Your GitHub repo
BRANCH = "main"                        # Target branch
LOG_DIR = "founder_autodeploy/logs"    # Log directory
```

## Security Best Practices

1. **Never commit GitHub tokens** - Use environment variables or Replit Secrets
2. **Review changes** before running autodeploy
3. **Test locally** before pushing to production
4. **Keep deployment logs** for audit trail

## Troubleshooting

### Missing GITHUB_TOKEN
```
❌ Missing secrets: GITHUB_TOKEN

To fix:
  1. Set environment variables:
     export GITHUB_TOKEN=<your_token>
  2. Or use Replit Secrets panel to add them
```

**Solution**: Add `GITHUB_TOKEN` to Replit Secrets or export in shell

### No Git Remote
```
⚠️  No git remote configured
```

**Solution**: 
```bash
git remote add origin https://github.com/m9dswyptrn-web/SonicBuilder.git
```

### Push Rejected
```
❌ Deploy error: Command failed: git push origin main
```

**Solution**: Pull latest changes first:
```bash
git pull origin main --rebase
python3 founder_autodeploy/founder_autodeploy.py
```

### Rollback Failed
```
❌ Rollback also failed: <error>
```

**Solution**: Manual recovery:
```bash
git reflog  # Find previous commit
git reset --hard <commit-hash>
git push -f origin main
```

## Advanced Usage

### Pre-deployment Checks
Add custom checks to `preflight()` function:

```python
def preflight():
    # Existing checks...
    
    # Add custom check
    if not os.path.exists("README.md"):
        sys.exit("❌ README.md required")
```

### Custom Commit Messages
Modify the commit message format:

```python
commit_msg = f"autodeploy: {ts} - {custom_message}"
```

### Deployment Hooks
Add pre/post deployment hooks:

```python
def main():
    preflight()
    run_pre_deploy_hook()   # Custom hook
    commit_and_push()
    run_post_deploy_hook()  # Custom hook
```

## Integration with Existing Tools

Works with:
- `make secure-build` - Build before deploy
- `make package-all` - Package bundles before deploy
- `make semgrep` - Security scan before deploy

Example workflow:
```bash
# Full secure deployment
make secure-build
python3 founder_autodeploy/founder_autodeploy.py
```

---

**Autodeploy System: Simplify your SonicBuilder deployments with automated workflows and rollback safety!** 🚀
