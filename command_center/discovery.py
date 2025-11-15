#!/usr/bin/env python3
"""
Service Discovery Module
Auto-detect and health-check all SONIC services
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

SERVICES = [
    {
        'id': 'canbus',
        'name': 'CAN Bus Monitor',
        'port': 7000,
        'category': 'hardware',
        'icon': '🔌',
        'description': 'Live GMLAN/OBD-II monitoring'
    },
    {
        'id': 'maestro',
        'name': 'Maestro RR2',
        'port': 7200,
        'category': 'hardware',
        'icon': '🎛️',
        'description': 'Maestro RR2 integration control'
    },
    {
        'id': 'cameras',
        'name': 'Camera System',
        'port': 7300,
        'category': 'hardware',
        'icon': '📹',
        'description': 'Multi-camera monitoring'
    },
    {
        'id': 'health',
        'name': 'System Health',
        'port': 7400,
        'category': 'hardware',
        'icon': '💊',
        'description': 'Component health monitoring'
    },
    {
        'id': 'logger',
        'name': 'Data Logger',
        'port': 7600,
        'category': 'hardware',
        'icon': '📊',
        'description': 'Multi-channel data logging'
    },
    {
        'id': 'audio_path',
        'name': 'Audio Path Designer',
        'port': 7700,
        'category': 'hardware',
        'icon': '🔊',
        'description': 'Audio routing visualization'
    },
    {
        'id': 'remote',
        'name': 'Remote Diagnostics',
        'port': 7800,
        'category': 'hardware',
        'icon': '🔧',
        'description': 'Remote troubleshooting'
    },
    {
        'id': 'harness',
        'name': 'Wire Harness',
        'port': 7900,
        'category': 'hardware',
        'icon': '🔌',
        'description': 'Harness designer & analyzer'
    },
    {
        'id': 'pcb',
        'name': 'PCB Designer',
        'port': 7100,
        'category': 'hardware',
        'icon': '🖥️',
        'description': 'PCB layout and design'
    },
    {
        'id': 'ai_board',
        'name': 'AI Board Analyzer',
        'port': 7500,
        'category': 'hardware',
        'icon': '🤖',
        'description': 'AI-powered board analysis'
    },
    {
        'id': 'bom',
        'name': 'BOM Generator',
        'port': 5052,
        'category': 'hardware',
        'icon': '📋',
        'description': 'Bill of materials generator'
    },
    {
        'id': 'quotes',
        'name': 'Quote System',
        'port': 5053,
        'category': 'hardware',
        'icon': '💰',
        'description': 'Quote & invoice generator'
    },
    {
        'id': 'dsp',
        'name': 'DSP Control',
        'port': 8100,
        'category': 'audio',
        'icon': '🎚️',
        'description': '31-band EQ & processing'
    },
    {
        'id': 'soundstage',
        'name': 'Sound Stage',
        'port': 8200,
        'category': 'audio',
        'icon': '🎭',
        'description': 'Time alignment & staging'
    },
    {
        'id': 'visualizer',
        'name': 'Audio Visualizer',
        'port': 8300,
        'category': 'audio',
        'icon': '📊',
        'description': 'Real-time audio visualization'
    },
    {
        'id': 'bass',
        'name': 'Bass Management',
        'port': 8400,
        'category': 'audio',
        'icon': '🔊',
        'description': 'Subwoofer control & tuning'
    },
    {
        'id': 'lighting',
        'name': 'RGB Lighting',
        'port': 8500,
        'category': 'visual',
        'icon': '💡',
        'description': 'LED control & effects'
    },
    {
        'id': 'themes',
        'name': 'Theme Designer',
        'port': 8600,
        'category': 'visual',
        'icon': '🎨',
        'description': 'Custom themes & wallpapers'
    },
    {
        'id': 'performance',
        'name': 'Performance Dashboard',
        'port': 8700,
        'category': 'visual',
        'icon': '⚡',
        'description': 'Real-time performance metrics'
    },
    {
        'id': 'climate',
        'name': 'Climate Control',
        'port': 8800,
        'category': 'smart',
        'icon': '❄️',
        'description': 'Advanced HVAC control'
    },
    {
        'id': 'voice',
        'name': 'Voice Assistant',
        'port': 8900,
        'category': 'smart',
        'icon': '🎤',
        'description': 'Voice command system'
    },
    {
        'id': 'parking',
        'name': 'Parking Assistant',
        'port': 9100,
        'category': 'smart',
        'icon': '🅿️',
        'description': 'Parking sensors & guidance'
    },
    {
        'id': 'analytics',
        'name': 'Analytics Dashboard',
        'port': 9200,
        'category': 'smart',
        'icon': '📈',
        'description': 'Data analytics & insights'
    },
    {
        'id': 'security',
        'name': 'Security System',
        'port': 9300,
        'category': 'smart',
        'icon': '🔒',
        'description': 'Security & alarm system'
    },
    {
        'id': 'apps',
        'name': 'App Manager',
        'port': 9400,
        'category': 'smart',
        'icon': '📱',
        'description': 'Application management'
    },
    {
        'id': 'media',
        'name': 'Media Center',
        'port': 9500,
        'category': 'smart',
        'icon': '🎵',
        'description': 'Music & video library'
    },
    {
        'id': 'navigation',
        'name': 'Navigation',
        'port': 9600,
        'category': 'smart',
        'icon': '🗺️',
        'description': 'GPS navigation system'
    },
    {
        'id': 'tpms',
        'name': 'TPMS Monitor',
        'port': 9700,
        'category': 'smart',
        'icon': '🛞',
        'description': 'Tire pressure monitoring'
    },
    {
        'id': 'maintenance',
        'name': 'Maintenance Tracker',
        'port': 9800,
        'category': 'smart',
        'icon': '🔧',
        'description': 'Service scheduling & tracking'
    },
    {
        'id': 'fuel',
        'name': 'Fuel Optimizer',
        'port': 9900,
        'category': 'smart',
        'icon': '⛽',
        'description': 'Fuel economy optimization'
    },
    {
        'id': 'wireless',
        'name': 'Wireless Charger',
        'port': 10000,
        'category': 'smart',
        'icon': '🔋',
        'description': 'Wireless charging control'
    },
    {
        'id': 'dashcam',
        'name': 'Dash Cam',
        'port': 10100,
        'category': 'smart',
        'icon': '📹',
        'description': 'Dashcam recording & playback'
    }
]


class ServiceDiscovery:
    """Service discovery and health checking system."""
    
    def __init__(self):
        self.services = SERVICES
        self.timeout = 2
        self.base_url = 'http://localhost'
    
    def get_all_services(self) -> List[Dict]:
        """Get all registered services."""
        return self.services
    
    def get_service_by_id(self, service_id: str) -> Optional[Dict]:
        """Get service by ID."""
        for service in self.services:
            if service['id'] == service_id:
                return service
        return None
    
    def get_services_by_category(self, category: str) -> List[Dict]:
        """Get services by category."""
        return [s for s in self.services if s['category'] == category]
    
    def get_categories(self) -> Dict[str, List[Dict]]:
        """Get services grouped by category."""
        categories = {
            'hardware': [],
            'audio': [],
            'visual': [],
            'smart': []
        }
        
        for service in self.services:
            cat = service['category']
            if cat in categories:
                categories[cat].append(service)
        
        return categories
    
    def check_health(self, service_id: str) -> Dict:
        """Check health of a specific service."""
        service = self.get_service_by_id(service_id)
        if not service:
            return {
                'online': False,
                'error': 'Service not found'
            }
        
        url = f"{self.base_url}:{service['port']}/health"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'online': True,
                    'status': data.get('status', 'unknown'),
                    'data': data,
                    'response_time_ms': int(response.elapsed.total_seconds() * 1000)
                }
            else:
                return {
                    'online': False,
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}'
                }
        
        except requests.exceptions.Timeout:
            return {
                'online': False,
                'error': 'Timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'online': False,
                'error': 'Connection refused'
            }
        except Exception as e:
            return {
                'online': False,
                'error': str(e)
            }
    
    def check_all_health(self) -> Dict[str, Dict]:
        """Check health of all services."""
        results = {}
        
        for service in self.services:
            service_id = service['id']
            results[service_id] = self.check_health(service_id)
        
        return results
    
    def get_system_status(self) -> Dict:
        """Get overall system status."""
        health_checks = self.check_all_health()
        
        total = len(health_checks)
        online = sum(1 for h in health_checks.values() if h.get('online', False))
        offline = total - online
        
        return {
            'total_services': total,
            'online': online,
            'offline': offline,
            'health_percentage': round((online / total) * 100, 1) if total > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'services': health_checks
        }
    
    def get_service_url(self, service_id: str, path: str = '') -> Optional[str]:
        """Get full URL for a service."""
        service = self.get_service_by_id(service_id)
        if not service:
            return None
        
        return f"{self.base_url}:{service['port']}{path}"
