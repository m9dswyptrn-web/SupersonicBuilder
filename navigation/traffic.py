#!/usr/bin/env python3
"""
Traffic Module
Provides simulated real-time traffic data including congestion, accidents, construction
"""

import random
import math
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


class TrafficMonitor:
    """Traffic monitoring and incident detection."""
    
    def __init__(self, database):
        """Initialize traffic monitor."""
        self.db = database
        
        self.congestion_levels = {
            'free_flow': {'speed_reduction': 0, 'color': 'green', 'description': 'Traffic flowing smoothly'},
            'light': {'speed_reduction': 10, 'color': 'yellow', 'description': 'Light traffic'},
            'moderate': {'speed_reduction': 25, 'color': 'orange', 'description': 'Moderate congestion'},
            'heavy': {'speed_reduction': 50, 'color': 'red', 'description': 'Heavy traffic'},
            'stop_and_go': {'speed_reduction': 75, 'color': 'darkred', 'description': 'Stop and go traffic'}
        }
        
        self.incident_types = ['accident', 'construction', 'road_closure', 'disabled_vehicle', 
                              'police_activity', 'weather_hazard', 'debris']
    
    def generate_traffic_conditions(self, latitude: float, longitude: float,
                                    route_distance_miles: float = 10) -> List[Dict]:
        """
        Generate simulated traffic conditions along route.
        In production, would use Google Maps Traffic API or similar.
        """
        segments = []
        num_segments = max(int(route_distance_miles / 2), 5)
        
        for i in range(num_segments):
            segment_start = (i / num_segments) * route_distance_miles
            segment_end = ((i + 1) / num_segments) * route_distance_miles
            
            congestion_type = random.choices(
                list(self.congestion_levels.keys()),
                weights=[0.5, 0.25, 0.15, 0.08, 0.02],
                k=1
            )[0]
            
            congestion_info = self.congestion_levels[congestion_type]
            
            segment = {
                'segment_id': f"seg_{i}",
                'start_mile': round(segment_start, 2),
                'end_mile': round(segment_end, 2),
                'congestion_level': congestion_type,
                'speed_reduction_percent': congestion_info['speed_reduction'],
                'color': congestion_info['color'],
                'description': congestion_info['description'],
                'typical_speed_mph': self._calculate_typical_speed(congestion_type),
                'estimated_delay_minutes': self._calculate_delay(
                    segment_end - segment_start, congestion_type
                )
            }
            
            segments.append(segment)
        
        return segments
    
    def _calculate_typical_speed(self, congestion_level: str) -> int:
        """Calculate typical speed for congestion level."""
        base_speeds = {
            'free_flow': 65,
            'light': 55,
            'moderate': 45,
            'heavy': 30,
            'stop_and_go': 15
        }
        return base_speeds.get(congestion_level, 45)
    
    def _calculate_delay(self, distance_miles: float, congestion_level: str) -> float:
        """Calculate estimated delay in minutes."""
        free_flow_speed = 65
        typical_speed = self._calculate_typical_speed(congestion_level)
        
        free_flow_time = (distance_miles / free_flow_speed) * 60
        actual_time = (distance_miles / typical_speed) * 60
        
        delay = max(0, actual_time - free_flow_time)
        return round(delay, 1)
    
    def generate_incidents(self, latitude: float, longitude: float,
                          radius_miles: float = 10) -> List[Dict]:
        """Generate simulated traffic incidents."""
        num_incidents = random.randint(0, 3)
        incidents = []
        
        for i in range(num_incidents):
            incident_type = random.choice(self.incident_types)
            severity = random.choice(['low', 'medium', 'high'])
            
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.5, radius_miles)
            
            dlat = (distance / 69.0) * math.cos(angle)
            dlng = (distance / (69.0 * math.cos(math.radians(latitude)))) * math.sin(angle)
            
            incident_lat = latitude + dlat
            incident_lng = longitude + dlng
            
            incident_id = f"incident_{uuid.uuid4().hex[:8]}"
            
            incident = {
                'incident_id': incident_id,
                'type': incident_type,
                'latitude': incident_lat,
                'longitude': incident_lng,
                'severity': severity,
                'description': self._generate_incident_description(incident_type, severity),
                'delay_minutes': self._generate_incident_delay(incident_type, severity),
                'distance_miles': round(distance, 2),
                'lanes_affected': random.randint(1, 2) if incident_type in ['accident', 'construction'] else 0,
                'start_time': datetime.now().isoformat(),
                'estimated_clearance': (datetime.now() + timedelta(
                    minutes=random.randint(15, 120)
                )).isoformat(),
                'reported_by': random.choice(['Police', 'Traffic Camera', 'Driver Report', 'DOT'])
            }
            
            self.db.add_traffic_incident(
                incident_id, incident_type, incident_lat, incident_lng,
                severity, incident['description'], incident['delay_minutes']
            )
            
            incidents.append(incident)
        
        incidents.sort(key=lambda x: x['distance_miles'])
        return incidents
    
    def _generate_incident_description(self, incident_type: str, severity: str) -> str:
        """Generate human-readable incident description."""
        descriptions = {
            'accident': {
                'low': 'Minor accident, one lane blocked',
                'medium': 'Multi-vehicle accident, delays expected',
                'high': 'Major accident, road partially closed'
            },
            'construction': {
                'low': 'Lane closure for road work',
                'medium': 'Construction zone, reduced speed limit',
                'high': 'Major construction, significant delays'
            },
            'road_closure': {
                'low': 'Partial road closure',
                'medium': 'Road closure, detour available',
                'high': 'Complete road closure'
            },
            'disabled_vehicle': {
                'low': 'Disabled vehicle on shoulder',
                'medium': 'Stalled vehicle blocking lane',
                'high': 'Multiple disabled vehicles'
            },
            'police_activity': {
                'low': 'Police on scene',
                'medium': 'Police activity, lane blocked',
                'high': 'Major police activity, road closed'
            },
            'weather_hazard': {
                'low': 'Wet road conditions',
                'medium': 'Heavy rain reducing visibility',
                'high': 'Severe weather, hazardous conditions'
            },
            'debris': {
                'low': 'Minor debris in roadway',
                'medium': 'Debris blocking lane',
                'high': 'Large debris, multiple lanes affected'
            }
        }
        
        return descriptions.get(incident_type, {}).get(severity, 'Traffic incident reported')
    
    def _generate_incident_delay(self, incident_type: str, severity: str) -> float:
        """Generate estimated delay from incident."""
        delay_map = {
            'low': random.uniform(2, 5),
            'medium': random.uniform(5, 15),
            'high': random.uniform(15, 45)
        }
        return round(delay_map.get(severity, 5), 1)
    
    def calculate_total_delay(self, traffic_segments: List[Dict], 
                            incidents: List[Dict]) -> float:
        """Calculate total expected delay from traffic and incidents."""
        segment_delay = sum(seg.get('estimated_delay_minutes', 0) for seg in traffic_segments)
        incident_delay = sum(inc.get('delay_minutes', 0) for inc in incidents)
        
        return round(segment_delay + incident_delay, 1)
    
    def suggest_alternative_route(self, origin: Dict, destination: Dict,
                                 current_route_delay: float) -> Optional[Dict]:
        """
        Suggest alternative route if significant delays exist.
        """
        if current_route_delay < 10:
            return None
        
        alternative_delay = random.uniform(0, current_route_delay * 0.7)
        time_savings = current_route_delay - alternative_delay
        
        if time_savings < 5:
            return None
        
        return {
            'has_alternative': True,
            'current_delay_minutes': current_route_delay,
            'alternative_delay_minutes': round(alternative_delay, 1),
            'time_savings_minutes': round(time_savings, 1),
            'reason': self._get_alternative_reason(current_route_delay),
            'route_type': random.choice(['via_highway', 'via_surface_streets', 'scenic_route'])
        }
    
    def _get_alternative_reason(self, delay_minutes: float) -> str:
        """Get reason for alternative route suggestion."""
        if delay_minutes > 30:
            return "Significant delays on current route due to heavy traffic"
        elif delay_minutes > 15:
            return "Moderate delays detected, alternative route available"
        else:
            return "Minor delays on current route"
    
    def get_traffic_summary(self, traffic_segments: List[Dict], 
                           incidents: List[Dict]) -> Dict:
        """Get summary of traffic conditions."""
        if not traffic_segments:
            return {
                'overall_condition': 'unknown',
                'total_delay_minutes': 0,
                'incidents_count': len(incidents),
                'summary': 'Traffic data unavailable'
            }
        
        avg_speed_reduction = sum(
            seg.get('speed_reduction_percent', 0) for seg in traffic_segments
        ) / len(traffic_segments)
        
        if avg_speed_reduction < 10:
            overall_condition = 'good'
            summary = 'Traffic is flowing smoothly'
        elif avg_speed_reduction < 25:
            overall_condition = 'moderate'
            summary = 'Expect some delays'
        else:
            overall_condition = 'heavy'
            summary = 'Heavy traffic, significant delays expected'
        
        total_delay = self.calculate_total_delay(traffic_segments, incidents)
        
        return {
            'overall_condition': overall_condition,
            'avg_speed_reduction_percent': round(avg_speed_reduction, 1),
            'total_delay_minutes': total_delay,
            'incidents_count': len(incidents),
            'summary': summary,
            'color': self._get_traffic_color(overall_condition)
        }
    
    def _get_traffic_color(self, condition: str) -> str:
        """Get color code for traffic condition."""
        colors = {
            'good': 'green',
            'moderate': 'yellow',
            'heavy': 'red',
            'unknown': 'gray'
        }
        return colors.get(condition, 'gray')
    
    def get_eta_with_traffic(self, base_eta_minutes: float, 
                            traffic_delay_minutes: float) -> Dict:
        """Calculate ETA including traffic delays."""
        total_eta = base_eta_minutes + traffic_delay_minutes
        arrival_time = datetime.now() + timedelta(minutes=total_eta)
        
        return {
            'base_eta_minutes': round(base_eta_minutes, 1),
            'traffic_delay_minutes': round(traffic_delay_minutes, 1),
            'total_eta_minutes': round(total_eta, 1),
            'estimated_arrival': arrival_time.strftime('%I:%M %p'),
            'estimated_arrival_iso': arrival_time.isoformat()
        }
