#!/usr/bin/env python3
"""
Storage analysis for Android App Manager
Provides storage insights and recommendations
"""

from typing import Dict, Any, List
import random


class StorageAnalyzer:
    """Analyzes storage usage and provides recommendations."""
    
    def __init__(self, total_storage_gb: float = 256):
        self.total_storage_gb = total_storage_gb
        self._simulated_usage = self._init_simulated_storage()
    
    def _init_simulated_storage(self) -> Dict[str, float]:
        """Initialize simulated storage usage."""
        return {
            'apps': random.uniform(25, 35),
            'photos': random.uniform(40, 60),
            'videos': random.uniform(30, 50),
            'audio': random.uniform(15, 25),
            'documents': random.uniform(5, 10),
            'downloads': random.uniform(8, 15),
            'cache': random.uniform(5, 12),
            'system': random.uniform(12, 18),
            'other': random.uniform(3, 8)
        }
    
    def get_storage_overview(self, apps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get overall storage overview."""
        apps_storage_mb = sum(app['total_size_mb'] for app in apps)
        apps_storage_gb = apps_storage_mb / 1024
        
        cache_storage_mb = sum(app['cache_size_mb'] for app in apps)
        cache_storage_gb = cache_storage_mb / 1024
        
        data_storage_mb = sum(app['data_size_mb'] for app in apps)
        data_storage_gb = data_storage_mb / 1024
        
        app_binaries_gb = apps_storage_gb - cache_storage_gb - data_storage_gb
        
        other_usage_gb = sum(self._simulated_usage.values()) - apps_storage_gb
        used_storage_gb = apps_storage_gb + other_usage_gb
        free_storage_gb = self.total_storage_gb - used_storage_gb
        
        usage_percent = (used_storage_gb / self.total_storage_gb) * 100
        
        return {
            'total_storage_gb': round(self.total_storage_gb, 2),
            'used_storage_gb': round(used_storage_gb, 2),
            'free_storage_gb': round(free_storage_gb, 2),
            'usage_percent': round(usage_percent, 2),
            'apps_storage_gb': round(apps_storage_gb, 2),
            'cache_storage_gb': round(cache_storage_gb, 2),
            'data_storage_gb': round(data_storage_gb, 2),
            'app_binaries_gb': round(app_binaries_gb, 2),
            'photos_gb': round(self._simulated_usage['photos'], 2),
            'videos_gb': round(self._simulated_usage['videos'], 2),
            'audio_gb': round(self._simulated_usage['audio'], 2),
            'documents_gb': round(self._simulated_usage['documents'], 2),
            'downloads_gb': round(self._simulated_usage['downloads'], 2),
            'system_gb': round(self._simulated_usage['system'], 2),
            'other_gb': round(self._simulated_usage['other'], 2),
            'status': self._get_storage_status(usage_percent)
        }
    
    def _get_storage_status(self, usage_percent: float) -> str:
        """Get storage status based on usage."""
        if usage_percent < 50:
            return 'healthy'
        elif usage_percent < 75:
            return 'good'
        elif usage_percent < 85:
            return 'warning'
        elif usage_percent < 95:
            return 'critical'
        else:
            return 'emergency'
    
    def get_storage_breakdown(self, apps: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Get storage breakdown by category."""
        breakdown = {}
        
        for app in apps:
            category = app.get('category', 'other')
            if category not in breakdown:
                breakdown[category] = []
            breakdown[category].append({
                'app_name': app['app_name'],
                'package_name': app['package_name'],
                'total_size_mb': app['total_size_mb']
            })
        
        for category in breakdown:
            breakdown[category] = sorted(
                breakdown[category],
                key=lambda x: x['total_size_mb'],
                reverse=True
            )
        
        category_totals = {
            category: {
                'total_size_mb': sum(app['total_size_mb'] for app in apps_list),
                'app_count': len(apps_list),
                'apps': apps_list
            }
            for category, apps_list in breakdown.items()
        }
        
        return category_totals
    
    def get_top_storage_hogs(self, apps: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top apps by storage usage."""
        sorted_apps = sorted(apps, key=lambda x: x['total_size_mb'], reverse=True)
        
        return [{
            'app_name': app['app_name'],
            'package_name': app['package_name'],
            'category': app.get('category', 'other'),
            'total_size_mb': app['total_size_mb'],
            'app_size_mb': app['app_size_mb'],
            'data_size_mb': app['data_size_mb'],
            'cache_size_mb': app['cache_size_mb'],
            'percent_of_total': round((app['total_size_mb'] / sum(a['total_size_mb'] for a in apps)) * 100, 2)
        } for app in sorted_apps[:limit]]
    
    def get_cache_analysis(self, apps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cache usage."""
        total_cache_mb = sum(app['cache_size_mb'] for app in apps)
        apps_with_cache = [app for app in apps if app['cache_size_mb'] > 0]
        
        cache_apps = sorted(
            apps_with_cache,
            key=lambda x: x['cache_size_mb'],
            reverse=True
        )[:10]
        
        return {
            'total_cache_mb': round(total_cache_mb, 2),
            'total_cache_gb': round(total_cache_mb / 1024, 2),
            'apps_with_cache': len(apps_with_cache),
            'potential_savings_mb': round(total_cache_mb, 2),
            'top_cache_apps': [{
                'app_name': app['app_name'],
                'package_name': app['package_name'],
                'cache_size_mb': app['cache_size_mb']
            } for app in cache_apps]
        }
    
    def get_storage_recommendations(self, apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get storage optimization recommendations."""
        recommendations = []
        overview = self.get_storage_overview(apps)
        
        if overview['cache_storage_gb'] > 5:
            recommendations.append({
                'type': 'clear_all_caches',
                'priority': 'high',
                'title': 'Clear All App Caches',
                'description': f'Free up {overview["cache_storage_gb"]:.1f} GB by clearing all app caches',
                'potential_savings_gb': overview['cache_storage_gb'],
                'action': 'clear_all_caches'
            })
        elif overview['cache_storage_gb'] > 2:
            recommendations.append({
                'type': 'clear_all_caches',
                'priority': 'medium',
                'title': 'Clear App Caches',
                'description': f'Free up {overview["cache_storage_gb"]:.1f} GB by clearing caches',
                'potential_savings_gb': overview['cache_storage_gb'],
                'action': 'clear_all_caches'
            })
        
        if overview['usage_percent'] > 85:
            recommendations.append({
                'type': 'storage_critical',
                'priority': 'critical',
                'title': 'Storage Almost Full',
                'description': f'Only {overview["free_storage_gb"]:.1f} GB remaining. Remove unused apps.',
                'potential_savings_gb': None,
                'action': 'review_unused_apps'
            })
        elif overview['usage_percent'] > 75:
            recommendations.append({
                'type': 'storage_warning',
                'priority': 'medium',
                'title': 'Storage Getting Low',
                'description': f'{overview["free_storage_gb"]:.1f} GB free. Consider cleanup.',
                'potential_savings_gb': None,
                'action': 'review_storage'
            })
        
        large_apps = [app for app in apps if app['total_size_mb'] > 500 and not app['is_system_app']]
        if large_apps:
            total_large = sum(app['total_size_mb'] for app in large_apps) / 1024
            recommendations.append({
                'type': 'large_apps',
                'priority': 'medium',
                'title': f'{len(large_apps)} Large Apps Found',
                'description': f'Apps using {total_large:.1f} GB combined. Review if needed.',
                'potential_savings_gb': total_large,
                'action': 'review_large_apps'
            })
        
        cache_apps = [app for app in apps if app['cache_size_mb'] > 100]
        if cache_apps:
            total_cache = sum(app['cache_size_mb'] for app in cache_apps) / 1024
            recommendations.append({
                'type': 'large_caches',
                'priority': 'low',
                'title': f'{len(cache_apps)} Apps with Large Caches',
                'description': f'Can free up {total_cache:.1f} GB by clearing specific caches',
                'potential_savings_gb': total_cache,
                'action': 'clear_large_caches'
            })
        
        return sorted(recommendations, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['priority']])
    
    def get_category_insights(self, apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get insights by app category."""
        breakdown = self.get_storage_breakdown(apps)
        insights = []
        
        for category, data in breakdown.items():
            total_mb = data['total_size_mb']
            if total_mb > 1000:
                insights.append({
                    'category': category,
                    'app_count': data['app_count'],
                    'total_size_gb': round(total_mb / 1024, 2),
                    'average_size_mb': round(total_mb / data['app_count'], 2),
                    'recommendation': f'{category.title()} apps using significant space'
                })
        
        return sorted(insights, key=lambda x: x['total_size_gb'], reverse=True)
    
    def predict_storage_full(self, apps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict when storage will be full."""
        overview = self.get_storage_overview(apps)
        
        if overview['usage_percent'] < 50:
            estimated_days = 180
            urgency = 'low'
        elif overview['usage_percent'] < 75:
            estimated_days = 90
            urgency = 'medium'
        elif overview['usage_percent'] < 85:
            estimated_days = 30
            urgency = 'high'
        elif overview['usage_percent'] < 95:
            estimated_days = 7
            urgency = 'critical'
        else:
            estimated_days = 1
            urgency = 'emergency'
        
        return {
            'current_usage_percent': overview['usage_percent'],
            'free_space_gb': overview['free_storage_gb'],
            'estimated_days_until_full': estimated_days,
            'urgency': urgency,
            'recommendation': self._get_urgency_recommendation(urgency)
        }
    
    def _get_urgency_recommendation(self, urgency: str) -> str:
        """Get recommendation based on urgency."""
        recommendations = {
            'low': 'Storage is healthy. No action needed.',
            'medium': 'Consider periodic cleanup to maintain performance.',
            'high': 'Start removing unused apps and clearing caches.',
            'critical': 'Immediate action required. Remove large unused apps.',
            'emergency': 'Storage critically low. Delete apps and data now.'
        }
        return recommendations.get(urgency, 'Monitor storage regularly.')
