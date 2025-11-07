#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 SonicBuilder GitHub Pages Deployment Script v2.0.9        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
REPO="${GITHUB_REPO:-m9dswyptrn-web/SonicBuilder}"
BRANCH="gh-pages"
BUILD_DIR="docs_build"
GIT_USER="SonicBuilder-AutoDeploy"
GIT_EMAIL="autodeploy@sonicbuilder.local"
TOKEN="${GITHUB_TOKEN}"

# Check prerequisites
if [ -z "$TOKEN" ]; then
  echo "❌ Error: GITHUB_TOKEN environment variable not set"
  echo "   Please configure GITHUB_TOKEN in Replit Secrets"
  exit 1
fi

if [ ! -d "$BUILD_DIR" ]; then
  echo "❌ Error: Build directory '$BUILD_DIR' not found"
  echo "   Please run documentation build first:"
  echo "   python3 supersonic_autodeploy.py"
  exit 1
fi

# Configure Git
echo "🔧 Configuring Git..."
git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"

# Clone gh-pages branch
echo "📂 Checking out gh-pages branch..."
rm -rf .ghpages 2>/dev/null || true

git clone --depth=1 --branch "$BRANCH" \
  "https://${TOKEN}@github.com/${REPO}.git" .ghpages 2>/dev/null || {
  echo "⚠️  Branch '$BRANCH' doesn't exist, creating it..."
  git clone --depth=1 "https://${TOKEN}@github.com/${REPO}.git" .ghpages
  cd .ghpages
  git checkout --orphan "$BRANCH"
  git rm -rf . 2>/dev/null || true
  cd ..
}

# Sync build artifacts
echo "📦 Syncing documentation build..."
rsync -av --delete --exclude='.git' "${BUILD_DIR}/" .ghpages/

# Commit and push
cd .ghpages

if [ -n "$(git status --porcelain)" ]; then
  echo "📝 Committing changes..."
  git add .
  git commit -m "🧠 AutoDeploy: Publish documentation build [$(date -u '+%Y-%m-%d %H:%M:%S UTC')]"
  
  echo "⬆️  Pushing to GitHub..."
  git push origin "$BRANCH"
  
  echo ""
  echo "✅ Deployment complete!"
  echo "   GitHub Pages will update within 1-2 minutes"
  echo "   URL: https://$(echo $REPO | cut -d'/' -f1).github.io/$(echo $REPO | cut -d'/' -f2)/"
else
  echo "ℹ️  No changes detected, skipping deployment"
fi

cd ..
rm -rf .ghpages

echo ""
echo "🎉 GitHub Pages deployment finished"
