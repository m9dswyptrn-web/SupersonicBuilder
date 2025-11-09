#!/bin/bash
# SupersonicBuilder - GitHub Push Readiness Verification
# Run this BEFORE attempting GitHub push to verify everything is ready

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║   SupersonicBuilder - GitHub Push Readiness Check               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0
WARN=0

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARN++))
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. ENVIRONMENT CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check GITHUB_TOKEN
if [ -n "$GITHUB_TOKEN" ]; then
    pass "GITHUB_TOKEN is set"
    echo "     Token length: ${#GITHUB_TOKEN} characters"
else
    fail "GITHUB_TOKEN is not set"
    echo "     Set it in Replit Secrets"
fi

# Check git config
if git config user.name >/dev/null 2>&1; then
    USERNAME=$(git config user.name)
    pass "Git user.name configured: $USERNAME"
else
    fail "Git user.name not configured"
fi

if git config user.email >/dev/null 2>&1; then
    EMAIL=$(git config user.email)
    pass "Git user.email configured: $EMAIL"
else
    fail "Git user.email not configured"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. WORKING TREE CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for large files in working tree
LARGE_FILES=$(find . -type f -size +95M ! -path "./.git/*" 2>/dev/null | wc -l)
if [ "$LARGE_FILES" -eq 0 ]; then
    pass "No large files (>95MB) in working tree"
else
    fail "Found $LARGE_FILES large files in working tree:"
    find . -type f -size +95M ! -path "./.git/*" -exec du -h {} \; 2>/dev/null
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    if grep -q "*.zip" .gitignore; then
        pass ".gitignore excludes *.zip"
    else
        warn ".gitignore missing *.zip exclusion"
    fi
else
    fail ".gitignore not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. GIT REPOSITORY CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if .git exists
if [ -d ".git" ]; then
    pass "Git repository initialized"
    
    # Check git status
    if git status >/dev/null 2>&1; then
        pass "Git repository is healthy"
        
        # Count uncommitted changes
        CHANGES=$(git status --porcelain | wc -l)
        if [ "$CHANGES" -gt 0 ]; then
            warn "$CHANGES uncommitted changes (normal before first push)"
            echo "     To see changes: git status"
        else
            pass "Working tree is clean"
        fi
    else
        fail "Git repository has errors"
    fi
    
    # Check for large files in git history
    echo ""
    echo "Scanning git history for large files (this may take a moment)..."
    HISTORY_CHECK=$(git rev-list --objects --all 2>/dev/null | \
        git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' 2>/dev/null | \
        awk '/^blob/ {if ($3 > 100*1024*1024) print $3/1024/1024 " MB " $4}' | \
        wc -l)
    
    if [ "$HISTORY_CHECK" -eq 0 ]; then
        pass "No large files in git history"
    else
        fail "Found $HISTORY_CHECK large files in git history"
        echo "     This will prevent GitHub push!"
        echo "     Solution: Use fresh repository approach (see GITHUB_PUSH_SOLUTION.md)"
    fi
else
    warn "No .git directory (will be created during push process)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. CORE APPLICATION CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check critical files
CRITICAL_FILES=(
    "replit_auto_healer.py"
    "replit_feed_dashboard.py"
    "serve_pdfs.py"
    "supersonic_settings_server.py"
    "requirements.txt"
    ".gitignore"
)

for FILE in "${CRITICAL_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        pass "Found $FILE"
    else
        fail "Missing $FILE"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. GITHUB CONNECTIVITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test GitHub API
if [ -n "$GITHUB_TOKEN" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        https://api.github.com/user)
    
    if [ "$HTTP_CODE" = "200" ]; then
        pass "GitHub API authentication successful"
        
        # Get username
        USERNAME=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github+json" \
            https://api.github.com/user | grep -o '"login":"[^"]*' | cut -d'"' -f4)
        echo "     Authenticated as: $USERNAME"
        
        # Check if repo exists
        REPO_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: Bearer $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github+json" \
            https://api.github.com/repos/$USERNAME/SupersonicBuilder)
        
        if [ "$REPO_CHECK" = "200" ]; then
            warn "Repository SupersonicBuilder already exists"
            echo "     Using --force will overwrite existing history"
            echo "     Make sure this is what you want!"
        elif [ "$REPO_CHECK" = "404" ]; then
            pass "Repository SupersonicBuilder does not exist (will be created)"
        else
            warn "Could not verify repository status (HTTP $REPO_CHECK)"
        fi
    else
        fail "GitHub API authentication failed (HTTP $HTTP_CODE)"
        echo "     Check your GITHUB_TOKEN"
    fi
else
    fail "Cannot test GitHub - GITHUB_TOKEN not set"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Passed${NC}: $PASS"
echo -e "${YELLOW}Warnings${NC}: $WARN"
echo -e "${RED}Failed${NC}: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}✅ READY FOR GITHUB PUSH!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review GITHUB_PUSH_SOLUTION.md"
    echo "  2. Choose Option 1 (Fresh Repository) or Option 2 (History Rewrite)"
    echo "  3. Execute the commands"
    echo ""
    exit 0
else
    echo -e "${RED}❌ NOT READY - Fix the failures above first${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Set GITHUB_TOKEN in Replit Secrets"
    echo "  - Remove large files: rm <filename>"
    echo "  - Configure git: git config user.name 'your-name'"
    echo ""
    exit 1
fi
