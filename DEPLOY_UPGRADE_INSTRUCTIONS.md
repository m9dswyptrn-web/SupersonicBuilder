# Deploy Target Upgrade Instructions

## Overview
You have two options for improved deployment:
1. **Updated Makefile targets** - Better `deploy` and `ship` targets with git automation
2. **Python ship_all.py script** - Comprehensive release script with version bumping

## Option 1: Update Makefile Targets

### Add PAGES_URL variable
Add this near the top of your Makefile (after `PY ?= python`):

```make
PAGES_URL ?= https://m9dswyptrn-web.github.io/SupersonicBuilder/
```

### Replace the `deploy` target
Find your current `deploy:` target and replace it with:

```make
deploy:  ## Deploy docs and commit/push to main
	@echo "🚀 Deploying everything to GitHub..."
	@python3 supersonic_deploy_pages.py
	@echo "📦 Committing & pushing to main..."
	@git add docs/ && git commit -m "docs: publish $$(date -u +'%F_%H:%M:%S')" || echo "Nothing to commit."
	@git push origin main
	@echo "🌐 Deployment complete. Visit your live site at:"
	@echo "   $(PAGES_URL)"
```

### Update the `ship` target (optional)
You can enhance `ship` to use the ship_all.py script:

```make
ship:  ## Full release with version bump
	@echo "🚢 Shipping with VERSION=$(VERSION)..."
	@python3 scripts/ship_all.py $(if $(VERSION),--version $(VERSION),)
```

## Option 2: Use ship_all.py Script Directly

The script is already saved at `scripts/ship_all.py`. You can use it directly:

```bash
# Deploy without version bump
python3 scripts/ship_all.py

# Deploy with version bump
python3 scripts/ship_all.py --version v0.1.5
```

## What ship_all.py Does

1. ✅ Configures git user (Supersonic Builder)
2. ✅ Syncs with origin/main
3. ✅ Optionally bumps version and tags
4. ✅ Builds all PDFs via `make supersonic-release`
5. ✅ Deploys to GitHub Pages
6. ✅ Commits and pushes docs with timestamp
7. ✅ Shows live hub URL

## Quick Commands After Upgrade

```bash
# Deploy only (no version bump)
make deploy

# Full ship with default version bump
make ship

# Ship with specific version
make ship VERSION=v0.1.5

# Or use Python script directly
python3 scripts/ship_all.py --version v0.1.5
```

## Testing

Test the deploy target:
```bash
make -n deploy  # Dry run to see commands
```

Test ship_all.py:
```bash
python3 scripts/ship_all.py  # Will run actual deployment
```

## Notes

- The improved `deploy` target now commits and pushes automatically
- The `ship_all.py` script handles the complete release workflow
- Both respect your GH_PAT token from Replit Secrets
- Timestamps are in UTC format for consistency
