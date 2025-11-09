#!/bin/bash
set -e

echo "🔄 Restoring SonicBuilder badges and syncing to GitHub Pages..."

# Create docs/badges directory if it doesn't exist
mkdir -p docs/badges

# Find most recent backup with badges
LATEST_BACKUP=""
if [ -d "backups" ]; then
    # Find the most recent backup directory that contains docs/badges
    for backup_dir in $(ls -td backups/backup_* 2>/dev/null); do
        if [ -d "$backup_dir/docs/badges" ]; then
            LATEST_BACKUP="$backup_dir"
            break
        fi
    done
fi

# Check if backup badges exist
if [ -d "backup/badges" ]; then
    echo "  📦 Restoring from backup/badges/..."
    cp -r ./backup/badges/* ./docs/badges/ 2>/dev/null || true
elif [ -n "$LATEST_BACKUP" ] && [ -d "$LATEST_BACKUP/docs/badges" ]; then
    echo "  📦 Restoring from backup: $(basename "$LATEST_BACKUP")..."
    cp -r "$LATEST_BACKUP/docs/badges/"* ./docs/badges/ 2>/dev/null || true
else
    echo "  ⚠️  No backup found, creating placeholder badges..."
    # Create placeholder badge files
    cat > docs/badges/latest.json << 'JSON'
{
  "schemaVersion": 1,
  "label": "latest",
  "message": "no file",
  "color": "lightgrey"
}
JSON

    cat > docs/badges/downloads.json << 'JSON'
{
  "schemaVersion": 1,
  "label": "downloads",
  "message": "0",
  "color": "lightgrey"
}
JSON

    cat > docs/badges/updated.json << 'JSON'
{
  "schemaVersion": 1,
  "label": "last updated",
  "message": "never",
  "color": "lightgrey"
}
JSON

    cat > docs/badges/size.json << 'JSON'
{
  "schemaVersion": 1,
  "label": "size",
  "message": "0 MB",
  "color": "lightgrey"
}
JSON

    cat > docs/badges/pdf-health.json << 'JSON'
{
  "schemaVersion": 1,
  "label": "PDF health",
  "message": "n/a",
  "color": "lightgrey"
}
JSON

    cat > docs/badges/pages-deploy.json << 'JSON'
{
  "schemaVersion": 1,
  "label": "pages deploy",
  "message": "n/a",
  "color": "lightgrey"
}
JSON
fi

# Git operations (user must run manually due to Replit restrictions)
echo "  📝 To sync to GitHub, run these commands:"
echo "     git add docs/badges README.md"
echo "     git commit -m '🔄 Sync: Restore badges + README'"
echo "     git push origin main"
echo ""

echo "✅ Done. Pages and badges will update automatically."
echo ""
echo "📊 Badge files in docs/badges/:"
ls -lh docs/badges/*.json 2>/dev/null || echo "  No badge files found"
