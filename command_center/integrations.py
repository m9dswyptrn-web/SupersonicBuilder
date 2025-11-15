#!/usr/bin/env python3
"""
Service Integrations Module
Pull live data from all SONIC services for unified dashboard
"""

import requests
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ServiceIntegrations:
    """Integration layer for pulling data from all services."""
    
    def __init__(self):
        self.timeout = 2
        self.base_url = 'http://localhost'
    
    def _fetch(self, port: int, endpoint: str) -> Optional[Dict]:
        """Fetch data from a service endpoint."""
        url = f"{self.base_url}:{port}{endpoint}"
        
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.debug(f"Failed to fetch from {url}: {e}")
            return None
    
    def get_canbus_data(self) -> Optional[Dict]:
        """Get live CAN bus data (speed, RPM, fuel)."""
        data = self._fetch(7000, '/api/session/current')
        
        if data and data.get('ok'):
            stats = data.get('stats', {})
            return {
                'speed_mph': stats.get('speed_mph', 0),
                'rpm': stats.get('rpm', 0),
                'fuel_level': stats.get('fuel_level', 0),
                'coolant_temp_f': stats.get('coolant_temp_f', 0),
                'session_active': data.get('session') is not None
            }
        
        return {
            'speed_mph': 0,
            'rpm': 0,
            'fuel_level': 0,
            'coolant_temp_f': 0,
            'session_active': False
        }
    
    def get_media_data(self) -> Optional[Dict]:
        """Get now playing from media center."""
        data = self._fetch(9500, '/api/player/now-playing')
        
        if data and data.get('ok'):
            playing = data.get('now_playing', {})
            return {
                'is_playing': data.get('is_playing', False),
                'title': playing.get('title', 'Not Playing'),
                'artist': playing.get('artist', ''),
                'album': playing.get('album', ''),
                'duration_sec': playing.get('duration_sec', 0),
                'position_sec': playing.get('position_sec', 0)
            }
        
        return {
            'is_playing': False,
            'title': 'Not Playing',
            'artist': '',
            'album': '',
            'duration_sec': 0,
            'position_sec': 0
        }
    
    def get_climate_data(self) -> Optional[Dict]:
        """Get climate control status."""
        data = self._fetch(8800, '/api/status')
        
        if data and data.get('ok'):
            state = data.get('state', {})
            zones = state.get('zones', {})
            driver = zones.get('driver', {})
            
            return {
                'temperature_c': driver.get('target_temp_c', 22),
                'temperature_f': driver.get('target_temp_f', 72),
                'fan_speed': driver.get('fan_speed', 0),
                'ac_enabled': state.get('ac_enabled', False),
                'auto_mode': state.get('auto_mode', False),
                'outside_temp_c': state.get('outside_temp_c', 20),
                'outside_temp_f': state.get('outside_temp_f', 68)
            }
        
        return {
            'temperature_c': 22,
            'temperature_f': 72,
            'fan_speed': 0,
            'ac_enabled': False,
            'auto_mode': False,
            'outside_temp_c': 20,
            'outside_temp_f': 68
        }
    
    def get_tpms_data(self) -> Optional[Dict]:
        """Get tire pressure monitoring data."""
        data = self._fetch(9700, '/api/readings/current')
        
        if data and data.get('ok'):
            readings = data.get('readings', {})
            
            return {
                'front_left': readings.get('FL', {}).get('pressure_psi', 0),
                'front_right': readings.get('FR', {}).get('pressure_psi', 0),
                'rear_left': readings.get('RL', {}).get('pressure_psi', 0),
                'rear_right': readings.get('RR', {}).get('pressure_psi', 0),
                'all_ok': all(
                    28 <= readings.get(pos, {}).get('pressure_psi', 0) <= 36
                    for pos in ['FL', 'FR', 'RL', 'RR']
                )
            }
        
        return {
            'front_left': 0,
            'front_right': 0,
            'rear_left': 0,
            'rear_right': 0,
            'all_ok': False
        }
    
    def get_wireless_charger_data(self) -> Optional[Dict]:
        """Get wireless charger status."""
        data = self._fetch(10000, '/api/status')
        
        if data and data.get('ok'):
            return {
                'is_charging': data.get('is_charging', False),
                'battery_percentage': data.get('battery_percentage', 0),
                'charging_power_watts': data.get('charging_power_watts', 0),
                'device_detected': data.get('device_detected', False)
            }
        
        return {
            'is_charging': False,
            'battery_percentage': 0,
            'charging_power_watts': 0,
            'device_detected': False
        }
    
    def get_security_data(self) -> Optional[Dict]:
        """Get security system status."""
        data = self._fetch(9300, '/api/status')
        
        if data and data.get('ok'):
            return {
                'armed': data.get('armed', False),
                'alarm_triggered': data.get('alarm_triggered', False),
                'doors_locked': data.get('doors_locked', True),
                'active_events': data.get('active_events', 0)
            }
        
        return {
            'armed': False,
            'alarm_triggered': False,
            'doors_locked': True,
            'active_events': 0
        }
    
    def get_maintenance_data(self) -> Optional[Dict]:
        """Get maintenance reminders."""
        data = self._fetch(9800, '/api/reminders/upcoming')
        
        if data and data.get('ok'):
            reminders = data.get('reminders', [])
            overdue = [r for r in reminders if r.get('is_overdue', False)]
            
            return {
                'total_reminders': len(reminders),
                'overdue_count': len(overdue),
                'next_service_miles': reminders[0].get('due_mileage', 0) if reminders else 0,
                'next_service_name': reminders[0].get('service_name', '') if reminders else ''
            }
        
        return {
            'total_reminders': 0,
            'overdue_count': 0,
            'next_service_miles': 0,
            'next_service_name': ''
        }
    
    def get_dashcam_data(self) -> Optional[Dict]:
        """Get dashcam status."""
        data = self._fetch(10100, '/api/status')
        
        if data and data.get('ok'):
            return {
                'is_recording': data.get('is_recording', False),
                'storage_used_gb': data.get('storage_used_gb', 0),
                'storage_total_gb': data.get('storage_total_gb', 0),
                'recording_count': data.get('recording_count', 0)
            }
        
        return {
            'is_recording': False,
            'storage_used_gb': 0,
            'storage_total_gb': 0,
            'recording_count': 0
        }
    
    def get_performance_data(self) -> Optional[Dict]:
        """Get performance metrics."""
        data = self._fetch(8700, '/api/metrics/current')
        
        if data and data.get('ok'):
            return {
                'cpu_usage': data.get('cpu_usage', 0),
                'memory_usage': data.get('memory_usage', 0),
                'disk_usage': data.get('disk_usage', 0),
                'temperature_c': data.get('temperature_c', 0)
            }
        
        return {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'temperature_c': 0
        }
    
    def get_all_widget_data(self) -> Dict[str, Any]:
        """Get all data for dashboard widgets."""
        return {
            'canbus': self.get_canbus_data(),
            'media': self.get_media_data(),
            'climate': self.get_climate_data(),
            'tpms': self.get_tpms_data(),
            'wireless_charger': self.get_wireless_charger_data(),
            'security': self.get_security_data(),
            'maintenance': self.get_maintenance_data(),
            'dashcam': self.get_dashcam_data(),
            'performance': self.get_performance_data()
        }
