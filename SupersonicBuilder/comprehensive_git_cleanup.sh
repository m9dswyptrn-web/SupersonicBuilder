#!/bin/bash
# Comprehensive Git Cleanup - Remove large files from working tree AND history

set -e  # Exit on error

echo "======================================================================"
echo "🧹 COMPREHENSIVE GIT CLEANUP - Phase 3 & 4"
echo "======================================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "\n${YELLOW}Step 1: Remove git lock files${NC}"
rm -f .git/index.lock .git/HEAD.lock .git/refs/heads/main.lock 2>/dev/null || true
echo "✅ Git locks cleared"

echo -e "\n${YELLOW}Step 2: Identify large files in working tree${NC}"
echo "Large files found:"
find . -type f -size +95M ! -path "./.git/*" 2>/dev/null | while read file; do
    size=$(du -h "$file" | cut -f1)
    echo "  - $size  $file"
done

echo -e "\n${YELLOW}Step 3: Remove large files from working tree${NC}"

# Remove specific large files identified in inventory
if [ -f "SonicBuilderSupersonic_Clean.zip" ]; then
    echo "Removing SonicBuilderSupersonic_Clean.zip (163MB)..."
    rm -f "SonicBuilderSupersonic_Clean.zip"
    echo "✅ Removed"
fi

if [ -f "ziQEO1Rx" ]; then
    echo "Removing ziQEO1Rx (101MB temp file)..."
    rm -f "ziQEO1Rx"
    echo "✅ Removed"
fi

# Remove all large archives from working tree
echo "Removing other large archives..."
find . -type f \( -name "*.zip" -o -name "*.tar" -o -name "*.tar.gz" -o -name "*.7z" -o -name "*.rar" \) -size +95M ! -path "./.git/*" -delete 2>/dev/null || true
echo "✅ Large archives removed from working tree"

echo -e "\n${YELLOW}Step 4: Untrack large files from git (keep local copies if any remain)${NC}"
git rm --cached -r "*.zip" 2>/dev/null || true
git rm --cached -r "*.tar" "*.tar.gz" "*.7z" "*.rar" "*.iso" 2>/dev/null || true
git rm --cached -r build/ dist/ release/ exports/ downloads/ 2>/dev/null || true
git rm --cached -f ziQEO1Rx 2>/dev/null || true
git rm --cached -f SonicBuilderSupersonic_Clean.zip 2>/dev/null || true
echo "✅ Files untracked from git index"

echo -e "\n${YELLOW}Step 5: Update .gitignore to prevent re-adding${NC}"

# Ensure .gitignore has proper excludes (it already does, but double-check)
if ! grep -q "# SupersonicBuilder large file excludes" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# SupersonicBuilder large file excludes
*.zip
*.tar
*.tar.gz
*.7z
*.rar
*.iso
build/
dist/
release/
exports/
downloads/
attached_assets/*.zip
release_assets/
support_bundle_*
EOF
    echo "✅ .gitignore updated"
else
    echo "✅ .gitignore already configured"
fi

echo -e "\n${YELLOW}Step 6: Check git history for large files${NC}"
echo "Scanning git history for files >100MB..."

# Find large files in git history
git rev-list --objects --all | \
    git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
    awk '/^blob/ {if ($3 > 100*1024*1024) print $3/1024/1024 " MB " $4}' | \
    sort -rn | head -20 > large_files_in_history.txt

if [ -s large_files_in_history.txt ]; then
    echo -e "${RED}⚠️  Large files found in git history:${NC}"
    cat large_files_in_history.txt
    echo ""
    echo "These files are in git history and MUST be removed for GitHub push to work."
    echo ""
    echo -e "${YELLOW}CRITICAL: Git history rewrite required${NC}"
    echo ""
    echo "You have two options:"
    echo ""
    echo "Option 1 (RECOMMENDED): Create a fresh repository"
    echo "  This is the safest and fastest approach:"
    echo "  1. Backup .git folder: mv .git .git.backup"
    echo "  2. Initialize fresh repo: git init"
    echo "  3. Add all files: git add -A"
    echo "  4. Commit: git commit -m 'Initial commit: clean SupersonicBuilder'"
    echo "  5. Push to GitHub: git push -u origin main --force"
    echo ""
    echo "Option 2: Use BFG Repo-Cleaner (advanced)"
    echo "  Download: https://rtyley.github.io/bfg-repo-cleaner/"
    echo "  Run: java -jar bfg.jar --strip-blobs-bigger-than 95M ."
    echo ""
    echo "Recommendation saved to: git_history_cleanup_recommendation.txt"
    
    cat > git_history_cleanup_recommendation.txt << 'EOFR'
CRITICAL: Git History Contains Large Files
==========================================

Your git history contains files larger than GitHub's 100MB limit.
These files prevent pushing to GitHub.

RECOMMENDED SOLUTION: Fresh Repository
--------------------------------------

This is the cleanest, safest, and fastest approach:

# 1. Backup current .git folder
mv .git .git.backup

# 2. Initialize fresh repository
git init
git branch -M main

# 3. Configure git user
git config user.name "m9dswyptrn-web"
git config user.email "m9dswyptrn@privaterelay.appleid.com"

# 4. Add all current files (large files already removed and gitignored)
git add -A

# 5. Create clean first commit
git commit -m "Initial commit: SupersonicBuilder v2.0.9 (clean)"

# 6. Add remote
git remote add origin https://github.com/m9dswyptrn-web/SupersonicBuilder.git

# 7. Push to GitHub (force push since this is a new history)
git push -u origin main --force

This creates a fresh, clean git history with ONLY your current files,
and none of the large files from previous commits.

EOFR
    
else
    echo "✅ No large files found in git history!"
fi

echo -e "\n${YELLOW}Step 7: Summary of changes${NC}"
echo "Files staged for removal:"
git status --short | grep -E "^D" | head -20 || echo "  (none in staging)"

echo ""
echo "======================================================================"
echo "✅ Phase 3 Complete: Working Tree Cleanup"
echo "======================================================================"
echo ""
echo "NEXT STEPS:"
echo "1. Review: cat git_history_cleanup_recommendation.txt"
echo "2. Choose: Fresh repo (recommended) or BFG cleanup"
echo "3. Execute: Follow the commands in the recommendation file"
echo ""
