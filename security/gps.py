#!/usr/bin/env python3
"""
GPS Tracking Module
Real-time location tracking, geofencing, and stolen vehicle recovery
"""

import uuid
import math
import random
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple


class GPSTracker:
    """GPS tracking with geofencing and stolen vehicle recovery."""
    
    def __init__(self):
        self.track_id = f"track_{uuid.uuid4().hex[:8]}"
        self.current_location = None
        self.location_history = []
        self.geofences = []
        self.stolen_mode_active = False
        self.tracking_interval = 5
        
        self.base_location = (37.7749, -122.4194)
        self.current_location = self._get_current_location()
    
    def get_current_location(self) -> Dict[str, Any]:
        """Get current GPS location."""
        location = self._get_current_location()
        self.current_location = location
        
        self.location_history.append({
            **location,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.location_history) > 1000:
            self.location_history = self.location_history[-1000:]
        
        return location
    
    def _get_current_location(self) -> Dict[str, Any]:
        """Simulate GPS reading."""
        if self.current_location:
            lat = self.current_location['latitude'] + random.uniform(-0.001, 0.001)
            lng = self.current_location['longitude'] + random.uniform(-0.001, 0.001)
        else:
            lat, lng = self.base_location
        
        return {
            'latitude': lat,
            'longitude': lng,
            'altitude': random.uniform(0, 100),
            'speed_kmh': random.uniform(0, 80) if random.random() > 0.3 else 0,
            'heading': random.uniform(0, 360),
            'accuracy_meters': random.uniform(3, 15),
            'satellites': random.randint(6, 12),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_location_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get location history."""
        return self.location_history[-limit:]
    
    def create_geofence(self, fence_name: str, center_lat: float, center_lng: float,
                       radius_meters: float, alert_on_exit: bool = True,
                       alert_on_entry: bool = False) -> Dict[str, Any]:
        """Create a geofence."""
        fence_id = f"fence_{uuid.uuid4().hex[:8]}"
        
        geofence = {
            'fence_id': fence_id,
            'fence_name': fence_name,
            'center_lat': center_lat,
            'center_lng': center_lng,
            'radius_meters': radius_meters,
            'alert_on_exit': alert_on_exit,
            'alert_on_entry': alert_on_entry,
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.geofences.append(geofence)
        
        return geofence
    
    def check_geofences(self, location: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Check if current location violates any geofences."""
        if location is None:
            location = self.get_current_location()
        
        violations = []
        current_lat = location['latitude']
        current_lng = location['longitude']
        
        for fence in self.geofences:
            if not fence['enabled']:
                continue
            
            distance = self._calculate_distance(
                current_lat, current_lng,
                fence['center_lat'], fence['center_lng']
            )
            
            inside_fence = distance <= fence['radius_meters']
            
            fence_key = f"last_state_{fence['fence_id']}"
            was_inside = fence.get(fence_key, inside_fence)
            
            if was_inside and not inside_fence and fence['alert_on_exit']:
                violations.append({
                    'fence_id': fence['fence_id'],
                    'fence_name': fence['fence_name'],
                    'event_type': 'exit',
                    'distance_meters': distance,
                    'location': (current_lat, current_lng)
                })
            
            elif not was_inside and inside_fence and fence['alert_on_entry']:
                violations.append({
                    'fence_id': fence['fence_id'],
                    'fence_name': fence['fence_name'],
                    'event_type': 'entry',
                    'distance_meters': distance,
                    'location': (current_lat, current_lng)
                })
            
            fence[fence_key] = inside_fence
        
        return violations
    
    def _calculate_distance(self, lat1: float, lng1: float, 
                           lat2: float, lng2: float) -> float:
        """Calculate distance between two points in meters (Haversine formula)."""
        R = 6371000
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def enable_stolen_mode(self) -> Dict[str, Any]:
        """Enable stolen vehicle recovery mode."""
        self.stolen_mode_active = True
        self.tracking_interval = 1
        
        print("🚨 STOLEN VEHICLE MODE ACTIVATED")
        print("  - High-frequency GPS tracking enabled (1 second intervals)")
        print("  - Location shared with law enforcement")
        print("  - Remote engine disable ready")
        print("  - Stealth mode: No visible indicators")
        
        return {
            'stolen_mode_active': True,
            'tracking_interval': self.tracking_interval,
            'high_frequency_tracking': True,
            'law_enforcement_notified': True,
            'message': 'Stolen vehicle recovery mode activated'
        }
    
    def disable_stolen_mode(self) -> Dict[str, Any]:
        """Disable stolen vehicle recovery mode."""
        self.stolen_mode_active = False
        self.tracking_interval = 5
        
        return {
            'stolen_mode_active': False,
            'tracking_interval': self.tracking_interval,
            'message': 'Stolen vehicle recovery mode deactivated'
        }
    
    def get_geofences(self) -> List[Dict[str, Any]]:
        """Get all geofences."""
        return [
            {k: v for k, v in fence.items() if not k.startswith('last_state_')}
            for fence in self.geofences
        ]
    
    def update_geofence(self, fence_id: str, **kwargs) -> bool:
        """Update geofence settings."""
        for fence in self.geofences:
            if fence['fence_id'] == fence_id:
                fence.update(kwargs)
                return True
        return False
    
    def delete_geofence(self, fence_id: str) -> bool:
        """Delete a geofence."""
        for i, fence in enumerate(self.geofences):
            if fence['fence_id'] == fence_id:
                self.geofences.pop(i)
                return True
        return False
    
    def get_route_summary(self, start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of route traveled."""
        history = self.location_history
        
        if not history:
            return {
                'total_distance_km': 0,
                'total_time_minutes': 0,
                'average_speed_kmh': 0,
                'max_speed_kmh': 0,
                'waypoints': 0
            }
        
        total_distance = 0
        for i in range(1, len(history)):
            prev = history[i-1]
            curr = history[i]
            distance = self._calculate_distance(
                prev['latitude'], prev['longitude'],
                curr['latitude'], curr['longitude']
            )
            total_distance += distance
        
        speeds = [loc.get('speed_kmh', 0) for loc in history]
        
        return {
            'total_distance_km': total_distance / 1000,
            'total_time_minutes': len(history) * (self.tracking_interval / 60),
            'average_speed_kmh': sum(speeds) / len(speeds) if speeds else 0,
            'max_speed_kmh': max(speeds) if speeds else 0,
            'waypoints': len(history)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get GPS tracker status."""
        return {
            'track_id': self.track_id,
            'current_location': self.current_location,
            'stolen_mode_active': self.stolen_mode_active,
            'tracking_interval': self.tracking_interval,
            'geofences_active': len([f for f in self.geofences if f['enabled']]),
            'location_history_count': len(self.location_history)
        }
