#!/usr/bin/env python3
"""
Simple webhook notification script for CI/CD pipelines.

Usage:
  python scripts/notify.py --webhook URL --message "Build complete"
  python scripts/notify.py --webhook URL --status success --title "Release" --message "v2.0.9"
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def detect_webhook_type(url):
    """Detect webhook type from URL."""
    if 'slack.com' in url:
        return 'slack'
    elif 'discord.com' in url:
        return 'discord'
    else:
        return 'generic'


def format_slack_message(title=None, message=None, status=None, url=None):
    """Format message for Slack webhook."""
    color_map = {
        'success': 'good',
        'failure': 'danger',
        'warning': 'warning',
        'info': '#439FE0'
    }
    
    blocks = []
    
    if title:
        blocks.append({
            "type": "header",
            "text": {"type": "plain_text", "text": title}
        })
    
    if message:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": message}
        })
    
    if url:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"<{url}|View Details>"}
        })
    
    payload = {"blocks": blocks}
    
    # Add color attachment if status provided
    if status and status in color_map:
        payload["attachments"] = [{
            "color": color_map[status],
            "text": ""
        }]
    
    return payload


def format_discord_message(title=None, message=None, status=None, url=None):
    """Format message for Discord webhook."""
    color_map = {
        'success': 0x00FF00,  # Green
        'failure': 0xFF0000,  # Red
        'warning': 0xFFA500,  # Orange
        'info': 0x0099FF     # Blue
    }
    
    embed = {}
    
    if title:
        embed["title"] = title
    
    if message:
        embed["description"] = message
    
    if url:
        embed["url"] = url
    
    if status and status in color_map:
        embed["color"] = color_map[status]
    
    return {"embeds": [embed]} if embed else {"content": message or title or "Notification"}


def format_generic_message(title=None, message=None, status=None, url=None):
    """Format generic JSON message."""
    payload = {}
    
    if title:
        payload["title"] = title
    
    if message:
        payload["message"] = message
    
    if status:
        payload["status"] = status
    
    if url:
        payload["url"] = url
    
    return payload


def send_notification(webhook_url, title=None, message=None, status=None, url=None):
    """Send notification to webhook."""
    if not webhook_url:
        print("Error: No webhook URL provided", file=sys.stderr)
        return False
    
    # Detect webhook type and format message
    webhook_type = detect_webhook_type(webhook_url)
    
    if webhook_type == 'slack':
        payload = format_slack_message(title, message, status, url)
    elif webhook_type == 'discord':
        payload = format_discord_message(title, message, status, url)
    else:
        payload = format_generic_message(title, message, status, url)
    
    # Send request
    try:
        request = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status in (200, 204):
                print(f"✅ Notification sent successfully ({webhook_type})")
                return True
            else:
                print(f"⚠️ Unexpected response: {response.status}", file=sys.stderr)
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Send webhook notifications')
    parser.add_argument('--webhook', help='Webhook URL (or use SB_NOTIFY_WEBHOOK env var)')
    parser.add_argument('--title', help='Notification title')
    parser.add_argument('--message', help='Notification message')
    parser.add_argument('--status', choices=['success', 'failure', 'warning', 'info'],
                        help='Status for color coding')
    parser.add_argument('--url', help='URL to include in notification')
    args = parser.parse_args()
    
    # Get webhook from args or environment
    webhook = args.webhook or os.environ.get('SB_NOTIFY_WEBHOOK')
    
    if not webhook:
        print("Error: No webhook URL provided. Use --webhook or set SB_NOTIFY_WEBHOOK", file=sys.stderr)
        sys.exit(1)
    
    # Send notification
    success = send_notification(
        webhook_url=webhook,
        title=args.title,
        message=args.message,
        status=args.status,
        url=args.url
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
