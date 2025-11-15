#!/usr/bin/env python3
"""
Speed Limit Detection Module
Detects speed limits, provides color-coded warnings, and generates audio alerts
"""

import math
from typing import Dict, Optional, Tuple
from datetime import datetime


class SpeedLimitDetector:
    """Speed limit detection and warning system."""
    
    def __init__(self, database):
        """Initialize speed limit detector."""
        self.db = database
        self.speed_limits_by_road_type = {
            'highway': 65,
            'freeway': 70,
            'interstate': 75,
            'arterial': 45,
            'residential': 25,
            'school_zone': 15,
            'business': 25,
            'rural': 55,
            'urban': 35,
            'default': 35
        }
        
        self.last_alert_time = None
        self.alert_cooldown_seconds = 10
    
    def detect_speed_limit(self, road_name: str = None, road_type: str = None,
                          latitude: float = None, longitude: float = None) -> int:
        """
        Detect speed limit for current location.
        Priority: cached data > road type > default
        """
        if road_name:
            cached_limit = self.db.get_speed_limit(road_name)
            if cached_limit:
                return cached_limit
        
        if road_type and road_type in self.speed_limits_by_road_type:
            speed_limit = self.speed_limits_by_road_type[road_type]
            
            if road_name and latitude and longitude:
                self.db.cache_speed_limit(road_name, latitude, longitude, speed_limit, road_type)
            
            return speed_limit
        
        return self.speed_limits_by_road_type['default']
    
    def get_speed_status(self, current_speed_mph: float, speed_limit_mph: int) -> Dict:
        """
        Get speed status with color coding.
        
        Returns:
            - status: 'safe', 'warning', 'danger'
            - color: 'green', 'yellow', 'red'
            - over_limit_mph: how much over the limit
            - percentage_over: percentage over the limit
        """
        if current_speed_mph <= speed_limit_mph:
            return {
                'status': 'safe',
                'color': 'green',
                'over_limit_mph': 0,
                'percentage_over': 0,
                'message': 'Speed OK'
            }
        
        over_limit = current_speed_mph - speed_limit_mph
        percentage_over = (over_limit / speed_limit_mph) * 100
        
        if over_limit <= 5:
            return {
                'status': 'warning',
                'color': 'yellow',
                'over_limit_mph': over_limit,
                'percentage_over': percentage_over,
                'message': f'Slightly over limit (+{over_limit:.0f} mph)'
            }
        else:
            return {
                'status': 'danger',
                'color': 'red',
                'over_limit_mph': over_limit,
                'percentage_over': percentage_over,
                'message': f'Speeding! (+{over_limit:.0f} mph)'
            }
    
    def should_trigger_audio_alert(self, current_speed_mph: float, 
                                   speed_limit_mph: int) -> Tuple[bool, Optional[str]]:
        """
        Determine if audio alert should be triggered.
        
        Returns:
            (should_alert, alert_message)
        """
        status = self.get_speed_status(current_speed_mph, speed_limit_mph)
        
        if status['status'] == 'safe':
            return False, None
        
        now = datetime.now()
        if self.last_alert_time:
            time_since_last = (now - self.last_alert_time).total_seconds()
            if time_since_last < self.alert_cooldown_seconds:
                return False, None
        
        if status['status'] == 'danger':
            self.last_alert_time = now
            return True, f"Speed limit exceeded. Slow down to {speed_limit_mph} miles per hour."
        elif status['status'] == 'warning' and status['over_limit_mph'] > 3:
            self.last_alert_time = now
            return True, f"Approaching speed limit. Current limit is {speed_limit_mph} miles per hour."
        
        return False, None
    
    def get_speed_limit_display(self, current_speed_mph: float, speed_limit_mph: int) -> Dict:
        """
        Get complete speed limit display data.
        
        Returns comprehensive display information including:
        - speed_limit
        - current_speed
        - status (safe/warning/danger)
        - color (green/yellow/red)
        - display_text
        - audio_alert
        """
        status = self.get_speed_status(current_speed_mph, speed_limit_mph)
        should_alert, alert_message = self.should_trigger_audio_alert(current_speed_mph, speed_limit_mph)
        
        display_text = f"{int(current_speed_mph)} mph"
        if status['status'] != 'safe':
            display_text += f" (Limit: {speed_limit_mph})"
        
        return {
            'speed_limit_mph': speed_limit_mph,
            'current_speed_mph': round(current_speed_mph, 1),
            'status': status['status'],
            'color': status['color'],
            'over_limit_mph': round(status['over_limit_mph'], 1),
            'percentage_over': round(status['percentage_over'], 1),
            'display_text': display_text,
            'message': status['message'],
            'audio_alert': alert_message if should_alert else None,
            'should_alert': should_alert
        }
    
    def estimate_road_type(self, speed_mph: float, road_name: str = None) -> str:
        """
        Estimate road type based on speed and road name.
        """
        if not road_name:
            if speed_mph >= 60:
                return 'highway'
            elif speed_mph >= 40:
                return 'arterial'
            else:
                return 'residential'
        
        road_name_lower = road_name.lower()
        
        if any(x in road_name_lower for x in ['interstate', 'i-', 'i ']):
            return 'interstate'
        elif any(x in road_name_lower for x in ['highway', 'hwy']):
            return 'highway'
        elif any(x in road_name_lower for x in ['freeway', 'expressway']):
            return 'freeway'
        elif any(x in road_name_lower for x in ['avenue', 'ave', 'boulevard', 'blvd']):
            return 'arterial'
        elif any(x in road_name_lower for x in ['street', 'st', 'road', 'rd', 'drive', 'dr']):
            return 'residential'
        elif 'school' in road_name_lower:
            return 'school_zone'
        else:
            return 'default'
    
    def get_advisory_speed(self, conditions: Dict) -> Optional[int]:
        """
        Get advisory speed based on road conditions.
        
        conditions can include:
        - weather: 'rain', 'snow', 'fog', 'ice'
        - visibility: 'poor', 'moderate', 'good'
        - traffic: 'heavy', 'moderate', 'light'
        """
        advisories = []
        
        weather = conditions.get('weather')
        if weather == 'ice' or weather == 'snow':
            advisories.append("Reduce speed by 50% due to winter conditions")
        elif weather == 'rain':
            advisories.append("Reduce speed by 20% due to wet roads")
        elif weather == 'fog':
            advisories.append("Reduce speed due to low visibility")
        
        visibility = conditions.get('visibility')
        if visibility == 'poor':
            advisories.append("Slow down due to poor visibility")
        
        traffic = conditions.get('traffic')
        if traffic == 'heavy':
            advisories.append("Heavy traffic ahead - maintain safe following distance")
        
        return advisories if advisories else None
