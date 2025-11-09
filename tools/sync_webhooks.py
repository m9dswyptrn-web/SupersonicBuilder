#!/usr/bin/env python3
"""
sync_webhooks.py
Webhook notification system for sync events.

Sends POST requests to configured webhook URLs on sync events.
Supports Slack, Discord, and generic webhook formats.
"""

import json
import time
import requests
from typing import Dict, Any, List
from datetime import datetime

class WebhookNotifier:
    """Manages webhook notifications for sync events."""
    
    def __init__(self, urls: List[str], timeout_sec: int = 5, retry_enabled: bool = True, max_retries: int = 3):
        self.urls = urls
        self.timeout_sec = timeout_sec
        self.retry_enabled = retry_enabled
        self.max_retries = max_retries
    
    def notify(self, event_type: str, payload: Dict[str, Any]):
        """
        Send notification to all configured webhooks.
        
        Args:
            event_type: Event type ('sync_success', 'sync_failure', 'sync_start', 'rate_limit_hit')
            payload: Event metadata
        """
        if not self.urls:
            return
        
        # Build generic webhook payload
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": payload,
        }
        
        # Send to all URLs
        for url in self.urls:
            try:
                self._send_webhook(url, event_type, webhook_payload)
            except Exception as e:
                print(f"[WARN] Webhook notification failed for {url}: {e}")
    
    def _send_webhook(self, url: str, event_type: str, payload: Dict[str, Any]):
        """Send webhook to a single URL with retry logic."""
        # Detect webhook type and format payload accordingly
        formatted_payload = self._format_payload(url, event_type, payload)
        
        attempts = 0
        while attempts <= (self.max_retries if self.retry_enabled else 0):
            try:
                response = requests.post(
                    url,
                    json=formatted_payload,
                    timeout=self.timeout_sec,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in (200, 201, 202, 204):
                    return  # Success
                else:
                    print(f"[WARN] Webhook returned {response.status_code}: {response.text[:200]}")
            except requests.exceptions.Timeout:
                print(f"[WARN] Webhook timeout for {url}")
            except Exception as e:
                print(f"[WARN] Webhook error: {e}")
            
            attempts += 1
            if attempts <= self.max_retries and self.retry_enabled:
                time.sleep(min(2 ** attempts, 10))  # Exponential backoff
    
    def _format_payload(self, url: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Format payload based on webhook type."""
        # Slack webhook
        if "slack.com" in url:
            return self._format_slack(event_type, payload)
        
        # Discord webhook
        elif "discord.com" in url:
            return self._format_discord(event_type, payload)
        
        # Generic webhook (pass as-is)
        else:
            return payload
    
    def _format_slack(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Format payload for Slack incoming webhooks."""
        data = payload.get("data", {})
        
        # Icon and color based on event type
        if event_type == "sync_success":
            icon = ":white_check_mark:"
            color = "good"
            title = "Sync Successful"
        elif event_type == "sync_failure":
            icon = ":x:"
            color = "danger"
            title = "Sync Failed"
        elif event_type == "rate_limit_hit":
            icon = ":warning:"
            color = "warning"
            title = "Rate Limit Hit"
        else:
            icon = ":information_source:"
            color = "#3AA3E3"
            title = "Sync Event"
        
        # Build message
        fields = []
        if "duration_sec" in data:
            fields.append({"title": "Duration", "value": f"{data['duration_sec']:.2f}s", "short": True})
        if "files_changed" in data:
            fields.append({"title": "Files Changed", "value": str(data["files_changed"]), "short": True})
        if "commit_hash" in data:
            fields.append({"title": "Commit", "value": f"`{data['commit_hash'][:8]}`", "short": True})
        if "error_msg" in data:
            fields.append({"title": "Error", "value": data["error_msg"][:200], "short": False})
        
        return {
            "text": f"{icon} *{title}*",
            "attachments": [
                {
                    "color": color,
                    "fields": fields,
                    "footer": "Supersonic Sync",
                    "ts": int(time.time())
                }
            ]
        }
    
    def _format_discord(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Format payload for Discord webhooks."""
        data = payload.get("data", {})
        
        # Color based on event type
        if event_type == "sync_success":
            color = 0x00ff00  # Green
            title = "✅ Sync Successful"
        elif event_type == "sync_failure":
            color = 0xff0000  # Red
            title = "❌ Sync Failed"
        elif event_type == "rate_limit_hit":
            color = 0xffaa00  # Orange
            title = "⚠️ Rate Limit Hit"
        else:
            color = 0x3aa3e3  # Blue
            title = "ℹ️ Sync Event"
        
        # Build fields
        fields = []
        if "duration_sec" in data:
            fields.append({"name": "Duration", "value": f"{data['duration_sec']:.2f}s", "inline": True})
        if "files_changed" in data:
            fields.append({"name": "Files Changed", "value": str(data["files_changed"]), "inline": True})
        if "commit_hash" in data:
            fields.append({"name": "Commit", "value": f"`{data['commit_hash'][:8]}`", "inline": True})
        if "error_msg" in data:
            fields.append({"name": "Error", "value": data["error_msg"][:1024], "inline": False})
        
        return {
            "embeds": [
                {
                    "title": title,
                    "color": color,
                    "fields": fields,
                    "footer": {"text": "Supersonic Sync"},
                    "timestamp": payload.get("timestamp")
                }
            ]
        }


def send_webhook_notification(event_type: str, payload: Dict[str, Any], config=None):
    """
    Send webhook notification using config settings.
    
    Args:
        event_type: Event type
        payload: Event metadata
        config: Optional SyncConfig instance (auto-loads if not provided)
    """
    if config is None:
        from tools.sync_config import get_config
        config = get_config()
    
    if not config.webhooks_enabled:
        return
    
    if event_type not in config.webhook_events:
        return
    
    notifier = WebhookNotifier(
        urls=config.webhook_urls,
        timeout_sec=config.webhook_timeout_sec,
        retry_enabled=config.webhook_retry_enabled,
        max_retries=config.webhook_max_retries
    )
    
    notifier.notify(event_type, payload)


if __name__ == "__main__":
    # CLI test utility
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sync_webhooks.py <event_type> [payload_json]")
        sys.exit(1)
    
    event_type = sys.argv[1]
    payload = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    send_webhook_notification(event_type, {"data": payload})
