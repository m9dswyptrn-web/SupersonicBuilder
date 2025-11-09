#!/bin/bash
# Cleanup large files from git tracking (but keep them on disk)

echo "🧹 Removing large files from git tracking..."

# Remove the git lock first
rm -f .git/index.lock

# Untrack all ZIP files (keep them on disk)
echo "Untracking *.zip files..."
git rm --cached -r *.zip 2>/dev/null || true
git rm --cached -r **/*.zip 2>/dev/null || true

# Untrack other large archives
echo "Untracking other large archives..."
git rm --cached -r *.tar *.tar.gz *.7z *.rar *.iso 2>/dev/null || true
git rm --cached -r **/*.tar **/*.tar.gz **/*.7z **/*.rar **/*.iso 2>/dev/null || true

# Untrack specific large directories
echo "Untracking large directories..."
git rm --cached -r build/ dist/ release/ exports/ downloads/ 2>/dev/null || true
git rm --cached -r attached_assets/ release_assets/ 2>/dev/null || true

# Show what we're about to commit
echo ""
echo "📋 Files removed from tracking:"
git status --short | grep "^D" | head -20

echo ""
echo "✅ Large files untracked. Now run:"
echo "   git add -A"
echo "   git commit -m 'chore: remove large files from tracking'"
echo "   git push origin main"
