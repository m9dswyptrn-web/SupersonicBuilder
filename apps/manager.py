#!/usr/bin/env python3
"""
Android App Manager - Core app management logic
Simulated for development environment
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class AppManager:
    """Manages Android apps with simulated operations for development."""
    
    CATEGORIES = {
        'music': ['spotify', 'pandora', 'youtube.music', 'soundcloud', 'tidal', 'apple.music'],
        'navigation': ['google.maps', 'waze', 'here', 'tomtom', 'sygic', 'maps.me'],
        'games': ['game', 'play', 'minecraft', 'pokemon', 'clash', 'candy'],
        'social': ['facebook', 'instagram', 'twitter', 'snapchat', 'tiktok', 'whatsapp'],
        'productivity': ['office', 'docs', 'sheets', 'notes', 'evernote', 'trello'],
        'tools': ['file', 'manager', 'cleaner', 'battery', 'camera', 'calculator'],
        'video': ['youtube', 'netflix', 'hulu', 'disney', 'twitch', 'vimeo'],
        'communication': ['gmail', 'outlook', 'slack', 'teams', 'zoom', 'skype'],
        'shopping': ['amazon', 'ebay', 'walmart', 'target', 'aliexpress', 'shop'],
        'health': ['fitness', 'health', 'workout', 'strava', 'myfitnesspal', 'nike']
    }
    
    CAR_RECOMMENDED_APPS = {
        'navigation': [
            {'name': 'Google Maps', 'package': 'com.google.android.apps.maps', 'reason': 'Best real-time traffic'},
            {'name': 'Waze', 'package': 'com.waze', 'reason': 'Community-based alerts'},
            {'name': 'HERE WeGo', 'package': 'com.here.app.maps', 'reason': 'Offline maps support'}
        ],
        'music': [
            {'name': 'Spotify', 'package': 'com.spotify.music', 'reason': 'Best music streaming'},
            {'name': 'YouTube Music', 'package': 'com.google.android.apps.youtube.music', 'reason': 'Integrated with YouTube'},
            {'name': 'Pandora', 'package': 'com.pandora.android', 'reason': 'Great for radio stations'}
        ],
        'communication': [
            {'name': 'Android Auto', 'package': 'com.google.android.projection.gearhead', 'reason': 'Hands-free driving'},
            {'name': 'WhatsApp', 'package': 'com.whatsapp', 'reason': 'Voice messages'},
            {'name': 'Google Assistant', 'package': 'com.google.android.apps.googleassistant', 'reason': 'Voice control'}
        ],
        'tools': [
            {'name': 'GasBuddy', 'package': 'gbis.gbandroid', 'reason': 'Find cheap gas'},
            {'name': 'Parkopedia', 'package': 'com.parkopedia.parkopedia', 'reason': 'Parking finder'},
            {'name': 'IFTTT', 'package': 'com.ifttt.ifttt', 'reason': 'Automation for car'}
        ]
    }
    
    def __init__(self):
        self.mock_apps = self._generate_mock_apps()
    
    def _generate_mock_apps(self) -> List[Dict[str, Any]]:
        """Generate realistic mock app data for development."""
        apps = []
        
        app_templates = [
            ('Spotify', 'com.spotify.music', 'music', 250, 180, 120),
            ('Google Maps', 'com.google.android.apps.maps', 'navigation', 180, 450, 85),
            ('Waze', 'com.waze', 'navigation', 120, 230, 45),
            ('YouTube', 'com.google.android.youtube', 'video', 180, 850, 320),
            ('Netflix', 'com.netflix.mediaclient', 'video', 220, 1200, 45),
            ('WhatsApp', 'com.whatsapp', 'communication', 150, 980, 180),
            ('Instagram', 'com.instagram.android', 'social', 190, 650, 280),
            ('Facebook', 'com.facebook.katana', 'social', 280, 890, 420),
            ('Chrome', 'com.android.chrome', 'tools', 180, 520, 340),
            ('Gmail', 'com.google.android.gm', 'communication', 140, 280, 65),
            ('Amazon Music', 'com.amazon.mp3', 'music', 160, 340, 95),
            ('Pandora', 'com.pandora.android', 'music', 145, 210, 78),
            ('HERE WeGo', 'com.here.app.maps', 'navigation', 165, 380, 52),
            ('Android Auto', 'com.google.android.projection.gearhead', 'tools', 95, 120, 35),
            ('Telegram', 'org.telegram.messenger', 'communication', 130, 450, 120),
            ('Twitter', 'com.twitter.android', 'social', 150, 380, 165),
            ('TikTok', 'com.zhiliaoapp.musically', 'social', 180, 1450, 520),
            ('Snapchat', 'com.snapchat.android', 'social', 170, 680, 240),
            ('Amazon Shopping', 'com.amazon.mShop.android.shopping', 'shopping', 140, 220, 85),
            ('Google Photos', 'com.google.android.apps.photos', 'tools', 160, 3200, 280),
            ('Discord', 'com.discord', 'communication', 145, 420, 180),
            ('Slack', 'com.slack', 'productivity', 160, 380, 95),
            ('Microsoft Teams', 'com.microsoft.teams', 'productivity', 180, 420, 110),
            ('Zoom', 'us.zoom.videomeetings', 'communication', 135, 280, 75),
            ('Uber', 'com.ubercabz', 'tools', 120, 180, 45),
            ('Lyft', 'me.lyft.android', 'tools', 115, 165, 38),
            ('GasBuddy', 'gbis.gbandroid', 'tools', 85, 95, 28),
            ('Shazam', 'com.shazam.android', 'music', 95, 145, 42),
            ('SoundCloud', 'com.soundcloud.android', 'music', 135, 280, 95),
            ('Audible', 'com.audible.application', 'music', 125, 1850, 65),
            ('Podcast Addict', 'com.bambuna.podcastaddict', 'music', 95, 450, 85),
            ('VLC', 'org.videolan.vlc', 'video', 75, 120, 35),
            ('Reddit', 'com.reddit.frontpage', 'social', 140, 420, 185),
            ('Pinterest', 'com.pinterest', 'social', 135, 380, 165),
            ('LinkedIn', 'com.linkedin.android', 'social', 150, 280, 95),
            ('Dropbox', 'com.dropbox.android', 'productivity', 125, 220, 65),
            ('Google Drive', 'com.google.android.apps.docs', 'productivity', 140, 180, 48),
            ('Microsoft OneDrive', 'com.microsoft.skydrive', 'productivity', 135, 195, 52),
            ('Evernote', 'com.evernote', 'productivity', 120, 280, 75),
            ('Google Keep', 'com.google.android.keep', 'productivity', 65, 85, 22),
        ]
        
        for i, (name, package, category, app_mb, data_mb, cache_mb) in enumerate(app_templates):
            days_ago = random.randint(10, 365)
            last_used_days = random.randint(0, days_ago)
            
            apps.append({
                'app_name': name,
                'package_name': package,
                'category': category,
                'version_name': f'{random.randint(1, 15)}.{random.randint(0, 99)}.{random.randint(0, 999)}',
                'version_code': random.randint(1000, 99999),
                'app_size_mb': app_mb,
                'data_size_mb': data_mb,
                'cache_size_mb': cache_mb,
                'total_size_mb': app_mb + data_mb + cache_mb,
                'installation_date': (datetime.now() - timedelta(days=days_ago)).isoformat(),
                'last_used': (datetime.now() - timedelta(days=last_used_days)).isoformat(),
                'is_system_app': False,
                'is_enabled': True
            })
        
        system_apps = [
            ('Android System', 'android', 'system', 450, 1200, 85),
            ('System UI', 'com.android.systemui', 'system', 280, 180, 45),
            ('Settings', 'com.android.settings', 'system', 95, 65, 12),
            ('Google Play Services', 'com.google.android.gms', 'system', 380, 850, 180),
            ('Google Play Store', 'com.android.vending', 'system', 145, 220, 65),
        ]
        
        for name, package, category, app_mb, data_mb, cache_mb in system_apps:
            apps.append({
                'app_name': name,
                'package_name': package,
                'category': category,
                'version_name': f'{random.randint(8, 14)}.0.0',
                'version_code': random.randint(10000, 999999),
                'app_size_mb': app_mb,
                'data_size_mb': data_mb,
                'cache_size_mb': cache_mb,
                'total_size_mb': app_mb + data_mb + cache_mb,
                'installation_date': (datetime.now() - timedelta(days=400)).isoformat(),
                'last_used': datetime.now().isoformat(),
                'is_system_app': True,
                'is_enabled': True
            })
        
        return apps
    
    def get_all_apps(self, include_system: bool = False) -> List[Dict[str, Any]]:
        """Get all installed apps."""
        if include_system:
            return self.mock_apps
        return [app for app in self.mock_apps if not app['is_system_app']]
    
    def get_app_by_package(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get app by package name."""
        for app in self.mock_apps:
            if app['package_name'] == package_name:
                return app
        return None
    
    def categorize_app(self, package_name: str) -> str:
        """Auto-categorize app based on package name."""
        package_lower = package_name.lower()
        
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in package_lower:
                    return category
        
        return 'other'
    
    def get_app_permissions(self, package_name: str) -> List[Dict[str, Any]]:
        """Get app permissions (simulated)."""
        common_permissions = [
            {
                'permission_name': 'android.permission.INTERNET',
                'permission_group': 'network',
                'is_granted': True,
                'is_dangerous': False,
                'privacy_concern_level': 'low'
            },
            {
                'permission_name': 'android.permission.ACCESS_FINE_LOCATION',
                'permission_group': 'location',
                'is_granted': True,
                'is_dangerous': True,
                'privacy_concern_level': 'high'
            },
            {
                'permission_name': 'android.permission.READ_CONTACTS',
                'permission_group': 'contacts',
                'is_granted': False,
                'is_dangerous': True,
                'privacy_concern_level': 'high'
            },
            {
                'permission_name': 'android.permission.CAMERA',
                'permission_group': 'camera',
                'is_granted': True,
                'is_dangerous': True,
                'privacy_concern_level': 'medium'
            },
            {
                'permission_name': 'android.permission.RECORD_AUDIO',
                'permission_group': 'microphone',
                'is_granted': True,
                'is_dangerous': True,
                'privacy_concern_level': 'high'
            },
            {
                'permission_name': 'android.permission.READ_EXTERNAL_STORAGE',
                'permission_group': 'storage',
                'is_granted': True,
                'is_dangerous': True,
                'privacy_concern_level': 'medium'
            },
        ]
        
        app = self.get_app_by_package(package_name)
        if not app:
            return []
        
        num_perms = random.randint(3, len(common_permissions))
        return random.sample(common_permissions, num_perms)
    
    def get_app_performance(self, package_name: str) -> Dict[str, Any]:
        """Get app performance metrics (simulated)."""
        app = self.get_app_by_package(package_name)
        if not app:
            return {}
        
        category = app['category']
        
        if category in ['music', 'video']:
            battery_base = random.uniform(8, 15)
            cpu_base = random.uniform(3, 8)
            ram_base = random.uniform(200, 500)
            network_base = random.uniform(50, 200)
        elif category == 'navigation':
            battery_base = random.uniform(15, 25)
            cpu_base = random.uniform(10, 20)
            ram_base = random.uniform(300, 600)
            network_base = random.uniform(20, 80)
        elif category == 'games':
            battery_base = random.uniform(20, 35)
            cpu_base = random.uniform(25, 50)
            ram_base = random.uniform(400, 1000)
            network_base = random.uniform(10, 100)
        elif category == 'social':
            battery_base = random.uniform(5, 12)
            cpu_base = random.uniform(2, 6)
            ram_base = random.uniform(150, 400)
            network_base = random.uniform(30, 150)
        else:
            battery_base = random.uniform(2, 8)
            cpu_base = random.uniform(1, 5)
            ram_base = random.uniform(100, 300)
            network_base = random.uniform(5, 50)
        
        return {
            'battery_usage_mah': round(battery_base * 100, 2),
            'battery_percent': round(battery_base, 2),
            'cpu_usage_percent': round(cpu_base, 2),
            'ram_usage_mb': round(ram_base, 2),
            'network_rx_mb': round(network_base, 2),
            'network_tx_mb': round(network_base * 0.3, 2)
        }
    
    def launch_app(self, package_name: str) -> Dict[str, Any]:
        """Launch an app (simulated)."""
        app = self.get_app_by_package(package_name)
        if not app:
            return {'success': False, 'message': f'App {package_name} not found'}
        
        return {
            'success': True,
            'message': f'Launched {app["app_name"]}',
            'package_name': package_name,
            'intent': f'android.intent.action.MAIN/{package_name}'
        }
    
    def uninstall_app(self, package_name: str) -> Dict[str, Any]:
        """Uninstall an app (simulated)."""
        app = self.get_app_by_package(package_name)
        if not app:
            return {'success': False, 'message': f'App {package_name} not found'}
        
        if app['is_system_app']:
            return {'success': False, 'message': 'Cannot uninstall system app'}
        
        space_freed = app['total_size_mb']
        
        self.mock_apps = [a for a in self.mock_apps if a['package_name'] != package_name]
        
        return {
            'success': True,
            'message': f'Uninstalled {app["app_name"]}',
            'space_freed_mb': round(space_freed, 2)
        }
    
    def clear_app_cache(self, package_name: str) -> Dict[str, Any]:
        """Clear app cache (simulated)."""
        app = self.get_app_by_package(package_name)
        if not app:
            return {'success': False, 'message': f'App {package_name} not found'}
        
        cache_cleared = app['cache_size_mb']
        app['cache_size_mb'] = 0
        app['total_size_mb'] = app['app_size_mb'] + app['data_size_mb']
        
        return {
            'success': True,
            'message': f'Cleared cache for {app["app_name"]}',
            'space_freed_mb': round(cache_cleared, 2)
        }
    
    def clear_app_data(self, package_name: str) -> Dict[str, Any]:
        """Clear app data (simulated)."""
        app = self.get_app_by_package(package_name)
        if not app:
            return {'success': False, 'message': f'App {package_name} not found'}
        
        if app['is_system_app']:
            return {'success': False, 'message': 'Cannot clear system app data'}
        
        data_cleared = app['data_size_mb'] + app['cache_size_mb']
        app['data_size_mb'] = 0
        app['cache_size_mb'] = 0
        app['total_size_mb'] = app['app_size_mb']
        
        return {
            'success': True,
            'message': f'Cleared data for {app["app_name"]}',
            'space_freed_mb': round(data_cleared, 2),
            'warning': 'App will be reset to initial state'
        }
    
    def force_stop_app(self, package_name: str) -> Dict[str, Any]:
        """Force stop an app (simulated)."""
        app = self.get_app_by_package(package_name)
        if not app:
            return {'success': False, 'message': f'App {package_name} not found'}
        
        return {
            'success': True,
            'message': f'Force stopped {app["app_name"]}',
            'package_name': package_name
        }
    
    def clear_all_caches(self) -> Dict[str, Any]:
        """Clear all app caches (simulated)."""
        total_freed = 0
        apps_cleared = 0
        
        for app in self.mock_apps:
            if app['cache_size_mb'] > 0:
                total_freed += app['cache_size_mb']
                app['cache_size_mb'] = 0
                app['total_size_mb'] = app['app_size_mb'] + app['data_size_mb']
                apps_cleared += 1
        
        return {
            'success': True,
            'message': f'Cleared cache for {apps_cleared} apps',
            'apps_cleared': apps_cleared,
            'space_freed_mb': round(total_freed, 2)
        }
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get app recommendations for car use."""
        return {
            'navigation_apps': self.CAR_RECOMMENDED_APPS['navigation'],
            'music_apps': self.CAR_RECOMMENDED_APPS['music'],
            'communication_apps': self.CAR_RECOMMENDED_APPS['communication'],
            'tool_apps': self.CAR_RECOMMENDED_APPS['tools']
        }
    
    def get_removal_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for apps to remove."""
        recommendations = []
        
        for app in self.mock_apps:
            if app['is_system_app']:
                continue
            
            days_unused = (datetime.now() - datetime.fromisoformat(app['last_used'])).days
            
            if days_unused > 90 and app['total_size_mb'] > 100:
                recommendations.append({
                    'package_name': app['package_name'],
                    'app_name': app['app_name'],
                    'reason': f'Not used in {days_unused} days',
                    'space_savings_mb': round(app['total_size_mb'], 2),
                    'priority': 'high'
                })
            elif days_unused > 60 and app['total_size_mb'] > 200:
                recommendations.append({
                    'package_name': app['package_name'],
                    'app_name': app['app_name'],
                    'reason': f'Not used in {days_unused} days and large size',
                    'space_savings_mb': round(app['total_size_mb'], 2),
                    'priority': 'medium'
                })
        
        return sorted(recommendations, key=lambda x: x['space_savings_mb'], reverse=True)[:10]
    
    def get_cache_cleanup_recommendations(self) -> List[Dict[str, Any]]:
        """Get cache cleanup recommendations."""
        recommendations = []
        
        for app in self.mock_apps:
            if app['cache_size_mb'] > 50:
                recommendations.append({
                    'package_name': app['package_name'],
                    'app_name': app['app_name'],
                    'cache_size_mb': round(app['cache_size_mb'], 2),
                    'priority': 'high' if app['cache_size_mb'] > 200 else 'medium'
                })
        
        return sorted(recommendations, key=lambda x: x['cache_size_mb'], reverse=True)[:10]
