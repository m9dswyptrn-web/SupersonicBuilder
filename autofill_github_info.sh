#!/bin/bash
set -e

echo "🔧 Auto-filling GitHub user and repo information..."

# Get git remote URL
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "⚠️  No git remote configured."
    echo ""
    echo "Would you like to configure it now? (y/n)"
    read -r REPLY
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Enter GitHub username:"
        read -r GITHUB_USER
        echo "Enter repository name:"
        read -r GITHUB_REPO
        
        # Set git remote
        git remote add origin "https://github.com/$GITHUB_USER/$GITHUB_REPO.git" || \
        git remote set-url origin "https://github.com/$GITHUB_USER/$GITHUB_REPO.git"
        
        REMOTE_URL="https://github.com/$GITHUB_USER/$GITHUB_REPO.git"
        echo "✓ Git remote configured: $REMOTE_URL"
    else
        echo "❌ Skipping auto-fill. Please configure git remote manually:"
        echo "   git remote add origin https://github.com/USERNAME/REPO.git"
        exit 1
    fi
fi

# Extract owner and repo from remote URL
# Handles both HTTPS and SSH URLs
if [[ $REMOTE_URL =~ github.com[:/]([^/]+)/([^/.]+) ]]; then
    OWNER="${BASH_REMATCH[1]}"
    REPO="${BASH_REMATCH[2]}"
else
    echo "❌ Could not parse GitHub URL: $REMOTE_URL"
    exit 1
fi

echo "📝 Detected GitHub info:"
echo "   Owner: $OWNER"
echo "   Repo:  $REPO"
echo ""

# Check if already filled
if grep -q "m9dswyptrn-web" README.md 2>/dev/null && [ "$OWNER" = "m9dswyptrn-web" ]; then
    echo "✓ Files already configured for $OWNER/$REPO"
    exit 0
fi

echo "🔄 Replacing placeholders in files..."

# Files to update
FILES_TO_UPDATE=(
    "README.md"
    "scripts/monitoring/verify_pages.py"
    "scripts/monitoring/pages_watch.sh"
    ".github/workflows/semgrep.yml"
    ".github/workflows/security-hardening.yml"
    ".github/workflows/pages-health-badge.yml"
    ".github/workflows/pages-deploy-badge.yml"
)

# Backup original files
BACKUP_DIR=".autofill_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        # Create backup
        cp "$file" "$BACKUP_DIR/$(basename "$file")"
        
        # Replace placeholders
        # Patterns: <USER>, <REPO>, <OWNER>, or existing hardcoded values
        sed -i "s/<USER>/$OWNER/g; s/<REPO>/$REPO/g; s/<OWNER>/$OWNER/g" "$file" 2>/dev/null || true
        sed -i "s/m9dswyptrn-web/$OWNER/g; s/SonicBuilder/$REPO/g" "$file" 2>/dev/null || true
        
        echo "   ✓ Updated: $file"
    fi
done

echo ""
echo "✅ Auto-fill complete!"
echo ""
echo "📦 Backup created at: $BACKUP_DIR"
echo ""
echo "🔍 Changed files:"
git diff --name-only 2>/dev/null || echo "   (no git diff available)"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff"
echo "   2. Commit: git add . && git commit -m 'chore: update GitHub info'"
echo "   3. Push: git push origin main"
echo ""
