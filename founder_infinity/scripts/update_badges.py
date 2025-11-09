#!/usr/bin/env python3
"""
SonicBuilder v2.0.9 FOUNDER-INFINITY-BADGE-UPDATER
--------------------------------------------------
Generates and updates Shields.io badges for README and documentation.

Creates badges for:
  - Last Updated timestamp
  - PDF Health status
  - GitHub Pages deployment status
  - Mirror Sync status

Updates:
  - badges/badges.json - Badge metadata
  - README.md - Injects badges between markers
"""

import datetime
import json
import os
import re

# Configuration
REPO = os.getenv("GITHUB_REPO", "m9dswyptrn-web/SonicBuilder")
PDF_PATH = "docs_build/latest.pdf"
BADGE_DIR = "badges"
README = "README.md"
AUDIT_LOG = "security_audit.json"

# Ensure badge directory exists
os.makedirs(BADGE_DIR, exist_ok=True)

def make_badge_url(label, message, color):
    """Generate Shields.io badge URL"""
    safe_label = label.replace(' ', '%20')
    safe_message = message.replace(' ', '%20')
    return f"https://img.shields.io/badge/{safe_label}-{safe_message}-{color}.svg"

def check_pdf_health():
    """Check if PDF exists and is recent"""
    if not os.path.exists(PDF_PATH):
        return "Missing", "red"
    
    # Check file age
    mod_time = os.path.getmtime(PDF_PATH)
    age_hours = (datetime.datetime.now().timestamp() - mod_time) / 3600
    
    if age_hours < 24:
        return "Healthy", "brightgreen"
    elif age_hours < 72:
        return "Stale", "yellow"
    else:
        return "Outdated", "orange"

def check_mirror_sync():
    """Check mirror sync status from audit log"""
    if not os.path.exists(AUDIT_LOG):
        return "Unknown", "lightgray"
    
    try:
        with open(AUDIT_LOG, 'r') as f:
            entries = json.load(f)
        
        if not entries:
            return "No%20Data", "lightgray"
        
        # Check last sync timestamp
        last_entry = entries[-1]
        last_time = datetime.datetime.fromisoformat(last_entry["timestamp"].replace("Z", "+00:00"))
        age_hours = (datetime.datetime.now(datetime.timezone.utc) - last_time).total_seconds() / 3600
        
        if age_hours < 2:
            return "Active", "blueviolet"
        elif age_hours < 24:
            return "Recent", "blue"
        else:
            return "Inactive", "gray"
    
    except Exception:
        return "Unknown", "lightgray"

def check_harmony_status():
    """Check Harmony heartbeat status from badge file"""
    if not os.path.exists("badges/heartbeat.json"):
        return "Unknown", "lightgray"
    
    try:
        with open("badges/heartbeat.json", 'r') as f:
            hb = json.load(f)
        
        status = hb.get("status", "Unknown")
        color = hb.get("color", "lightgray")
        
        return status, color
    except Exception:
        return "Unknown", "lightgray"

def generate_badges():
    """Generate all badge URLs and metadata"""
    print("🎨 Generating badges...")
    
    now = datetime.datetime.utcnow().strftime("%Y--%m--%d%%20%H:%M%%20UTC")
    pdf_status, pdf_color = check_pdf_health()
    mirror_status, mirror_color = check_mirror_sync()
    harmony_status, harmony_color = check_harmony_status()
    
    badges = {
        "last_updated": {
            "url": make_badge_url("Last%20Updated", now, "brightgreen"),
            "description": "Last badge update time"
        },
        "pdf_health": {
            "url": make_badge_url("PDF%20Status", pdf_status, pdf_color),
            "description": "PDF generation health"
        },
        "pages_status": {
            "url": make_badge_url("Pages", "Deployed", "blue"),
            "description": "GitHub Pages deployment status"
        },
        "mirror_sync": {
            "url": make_badge_url("Mirror", mirror_status, mirror_color),
            "description": "Mirror sync status"
        },
        "harmony": {
            "url": make_badge_url("Harmony", harmony_status, harmony_color),
            "description": "GitHub Actions heartbeat status"
        },
        "security": {
            "url": make_badge_url("Security", "Fort%20Infinity", "red"),
            "description": "Security level"
        }
    }
    
    # Save badge metadata
    badge_file = os.path.join(BADGE_DIR, "badges.json")
    with open(badge_file, "w") as f:
        json.dump(badges, f, indent=2)
    
    print(f"✅ Badges saved to {badge_file}")
    
    for name, data in badges.items():
        print(f"   • {name}: {data['description']}")
    
    return badges

def update_readme_badges(badges):
    """Update README.md with generated badges"""
    if not os.path.exists(README):
        print(f"⚠️  README not found at {README}, skipping injection.")
        return
    
    print(f"\n📝 Updating {README}...")
    
    with open(README, "r") as f:
        content = f.read()
    
    # Create badge block
    badge_block = (
        "<!-- BADGES_START -->\n"
        f"![Last Updated]({badges['last_updated']['url']}) "
        f"![PDF Health]({badges['pdf_health']['url']}) "
        f"![Pages]({badges['pages_status']['url']}) "
        f"![Mirror]({badges['mirror_sync']['url']}) "
        f"![Harmony]({badges['harmony']['url']}) "
        f"![Security]({badges['security']['url']})\n"
        "<!-- BADGES_END -->"
    )
    
    # Try to replace existing badge block
    pattern = r"<!-- BADGES_START -->.*?<!-- BADGES_END -->"
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, badge_block, content, flags=re.DOTALL)
        print("   ✅ Updated existing badge block")
    else:
        # Prepend badge block if not found
        new_content = badge_block + "\n\n" + content
        print("   ✅ Added new badge block")
    
    # Write updated content
    with open(README, "w") as f:
        f.write(new_content)
    
    print(f"   ✅ README updated successfully")

def main():
    """Main execution"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   🎨 SonicBuilder Badge Updater v2.0.9                        ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    badges = generate_badges()
    update_readme_badges(badges)
    
    print("\n✨ Badge update complete!\n")

if __name__ == "__main__":
    main()
