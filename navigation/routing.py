#!/usr/bin/env python3
"""
Route Planning Module
Provides route optimization with different strategies: fastest, fuel-efficient, avoid tolls/highways
"""

import math
import random
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


class RoutePlanner:
    """Advanced route planning with multiple optimization strategies."""
    
    def __init__(self, database):
        """Initialize route planner."""
        self.db = database
        
        self.route_strategies = {
            'fastest': 'Fastest route using highways',
            'fuel_efficient': 'Most fuel-efficient route',
            'avoid_tolls': 'Avoid toll roads',
            'avoid_highways': 'Use surface streets only',
            'scenic': 'Scenic route with minimal traffic'
        }
    
    def calculate_distance(self, lat1: float, lng1: float, 
                          lat2: float, lng2: float) -> float:
        """Calculate distance in miles using Haversine formula."""
        R = 3959
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def plan_route(self, origin: Dict, destination: Dict, 
                   strategy: str = 'fastest', options: Dict = None) -> Dict:
        """
        Plan route with specified strategy.
        
        Args:
            origin: {'lat': float, 'lng': float, 'address': str (optional)}
            destination: {'lat': float, 'lng': float, 'address': str (optional)}
            strategy: 'fastest', 'fuel_efficient', 'avoid_tolls', 'avoid_highways', 'scenic'
            options: Additional options like waypoints, departure_time
        """
        if options is None:
            options = {}
        
        distance_miles = self.calculate_distance(
            origin['lat'], origin['lng'],
            destination['lat'], destination['lng']
        )
        
        base_stats = self._calculate_base_route_stats(distance_miles, strategy)
        
        waypoints = self._generate_waypoints(
            origin['lat'], origin['lng'],
            destination['lat'], destination['lng'],
            num_waypoints=5
        )
        
        turns = self._generate_turn_by_turn(waypoints, strategy)
        
        lane_guidance = self._generate_lane_guidance(turns)
        
        route_id = f"route_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        route = {
            'route_id': route_id,
            'origin': origin,
            'destination': destination,
            'strategy': strategy,
            'strategy_description': self.route_strategies.get(strategy, 'Custom route'),
            'distance_miles': round(distance_miles, 2),
            'duration_minutes': base_stats['duration_minutes'],
            'estimated_fuel_gallons': base_stats['fuel_gallons'],
            'estimated_fuel_cost': round(base_stats['fuel_gallons'] * 3.50, 2),
            'avg_speed_mph': base_stats['avg_speed'],
            'waypoints': waypoints,
            'turns': turns,
            'lane_guidance': lane_guidance,
            'toll_roads': base_stats['has_tolls'],
            'estimated_toll_cost': base_stats['toll_cost'],
            'highways_used': base_stats['highways_used'],
            'created_at': datetime.now().isoformat()
        }
        
        self.db.save_route(
            route_id, origin, destination, strategy,
            distance_miles, base_stats['duration_minutes'], waypoints
        )
        
        return route
    
    def _calculate_base_route_stats(self, distance_miles: float, strategy: str) -> Dict:
        """Calculate base route statistics based on strategy."""
        if strategy == 'fastest':
            avg_speed = 60
            fuel_efficiency = 28
            has_tolls = random.choice([True, False])
            highways_used = True
        elif strategy == 'fuel_efficient':
            avg_speed = 50
            fuel_efficiency = 35
            has_tolls = False
            highways_used = False
        elif strategy == 'avoid_tolls':
            avg_speed = 55
            fuel_efficiency = 30
            has_tolls = False
            highways_used = True
        elif strategy == 'avoid_highways':
            avg_speed = 35
            fuel_efficiency = 32
            has_tolls = False
            highways_used = False
        elif strategy == 'scenic':
            avg_speed = 45
            fuel_efficiency = 33
            has_tolls = False
            highways_used = False
        else:
            avg_speed = 50
            fuel_efficiency = 30
            has_tolls = False
            highways_used = True
        
        duration_minutes = (distance_miles / avg_speed) * 60
        fuel_gallons = distance_miles / fuel_efficiency
        toll_cost = random.uniform(2, 10) if has_tolls else 0
        
        return {
            'duration_minutes': round(duration_minutes, 1),
            'avg_speed': avg_speed,
            'fuel_gallons': round(fuel_gallons, 2),
            'has_tolls': has_tolls,
            'toll_cost': round(toll_cost, 2),
            'highways_used': highways_used
        }
    
    def _generate_waypoints(self, start_lat: float, start_lng: float,
                           end_lat: float, end_lng: float,
                           num_waypoints: int = 5) -> List[Dict]:
        """Generate waypoints along route."""
        waypoints = []
        
        for i in range(num_waypoints + 1):
            progress = i / num_waypoints
            
            lat = start_lat + (end_lat - start_lat) * progress
            lng = start_lng + (end_lng - start_lng) * progress
            
            if i == 0:
                instruction = "Start"
                road_name = "Origin"
            elif i == num_waypoints:
                instruction = "Arrive at destination"
                road_name = "Destination"
            else:
                road_name = random.choice([
                    "Interstate 75", "Highway 31", "Main Street", "Oak Avenue",
                    "Park Boulevard", "Commerce Drive", "State Route 50"
                ])
                instruction = f"Continue on {road_name}"
            
            waypoint = {
                'waypoint_id': i,
                'latitude': lat,
                'longitude': lng,
                'instruction': instruction,
                'road_name': road_name,
                'distance_from_start': round(
                    self.calculate_distance(start_lat, start_lng, lat, lng), 2
                )
            }
            
            waypoints.append(waypoint)
        
        return waypoints
    
    def _generate_turn_by_turn(self, waypoints: List[Dict], strategy: str) -> List[Dict]:
        """Generate turn-by-turn directions."""
        turns = []
        turn_types = ['left', 'right', 'slight_left', 'slight_right', 'straight', 
                     'merge', 'exit', 'roundabout']
        
        for i in range(1, len(waypoints)):
            prev = waypoints[i - 1]
            current = waypoints[i]
            
            if i == len(waypoints) - 1:
                turn_type = 'arrive'
                instruction = "Arrive at destination on right"
            else:
                turn_type = random.choice(turn_types)
                instruction = self._generate_turn_instruction(
                    turn_type, current['road_name']
                )
            
            distance_to_turn = current['distance_from_start'] - prev['distance_from_start']
            
            turn = {
                'turn_id': i,
                'turn_type': turn_type,
                'instruction': instruction,
                'distance_miles': round(distance_to_turn, 2),
                'road_name': current['road_name'],
                'latitude': current['latitude'],
                'longitude': current['longitude'],
                'voice_instruction': self._generate_voice_instruction(
                    turn_type, current['road_name'], distance_to_turn
                )
            }
            
            turns.append(turn)
        
        return turns
    
    def _generate_turn_instruction(self, turn_type: str, road_name: str) -> str:
        """Generate text instruction for turn."""
        instructions = {
            'left': f"Turn left onto {road_name}",
            'right': f"Turn right onto {road_name}",
            'slight_left': f"Bear left onto {road_name}",
            'slight_right': f"Bear right onto {road_name}",
            'straight': f"Continue straight on {road_name}",
            'merge': f"Merge onto {road_name}",
            'exit': f"Take exit to {road_name}",
            'roundabout': f"At roundabout, take exit onto {road_name}",
            'arrive': "Arrive at destination"
        }
        return instructions.get(turn_type, f"Continue on {road_name}")
    
    def _generate_voice_instruction(self, turn_type: str, road_name: str, 
                                   distance_miles: float) -> str:
        """Generate voice guidance instruction."""
        if distance_miles > 0.5:
            distance_text = f"In {distance_miles:.1f} miles"
        elif distance_miles > 0.1:
            distance_text = f"In {int(distance_miles * 5280)} feet"
        else:
            distance_text = "Now"
        
        action = self._generate_turn_instruction(turn_type, road_name)
        
        return f"{distance_text}, {action.lower()}"
    
    def _generate_lane_guidance(self, turns: List[Dict]) -> List[Dict]:
        """Generate lane guidance for each turn."""
        lane_guidance = []
        
        for turn in turns:
            turn_type = turn['turn_type']
            
            if turn_type == 'arrive':
                lanes = ['any']
                preparation = "Prepare to arrive at destination"
            elif turn_type in ['left', 'slight_left']:
                lanes = ['left', 'center_left']
                preparation = "Move to left lane"
            elif turn_type in ['right', 'slight_right', 'exit']:
                lanes = ['right', 'center_right']
                preparation = "Move to right lane"
            elif turn_type == 'merge':
                lanes = ['right']
                preparation = "Prepare to merge"
            else:
                lanes = ['center', 'center_left', 'center_right']
                preparation = "Stay in center lanes"
            
            guidance = {
                'turn_id': turn['turn_id'],
                'recommended_lanes': lanes,
                'preparation_distance_miles': 0.5,
                'preparation_instruction': preparation,
                'warning_distance_miles': 0.1,
                'warning_instruction': f"Prepare to {turn['instruction'].lower()}"
            }
            
            lane_guidance.append(guidance)
        
        return lane_guidance
    
    def compare_routes(self, origin: Dict, destination: Dict, 
                      strategies: List[str] = None) -> List[Dict]:
        """Compare multiple route strategies."""
        if strategies is None:
            strategies = ['fastest', 'fuel_efficient', 'avoid_tolls']
        
        routes = []
        
        for strategy in strategies:
            route = self.plan_route(origin, destination, strategy)
            routes.append(route)
        
        routes.sort(key=lambda x: x['duration_minutes'])
        
        for i, route in enumerate(routes):
            route['rank'] = i + 1
            if i == 0:
                route['recommended'] = True
                route['recommendation_reason'] = f"Fastest route - {route['duration_minutes']:.0f} min"
        
        return routes
    
    def get_next_turn(self, current_position: Dict, turns: List[Dict]) -> Optional[Dict]:
        """Get next turn based on current position."""
        if not turns:
            return None
        
        current_lat = current_position['lat']
        current_lng = current_position['lng']
        
        for turn in turns:
            turn_lat = turn['latitude']
            turn_lng = turn['longitude']
            
            distance_to_turn = self.calculate_distance(
                current_lat, current_lng, turn_lat, turn_lng
            )
            
            if distance_to_turn > 0.01:
                return {
                    **turn,
                    'distance_to_turn_miles': round(distance_to_turn, 2),
                    'distance_to_turn_feet': int(distance_to_turn * 5280)
                }
        
        return None
    
    def calculate_eta(self, remaining_distance_miles: float, 
                     avg_speed_mph: float, traffic_delay_minutes: float = 0) -> Dict:
        """Calculate estimated time of arrival."""
        base_time = (remaining_distance_miles / avg_speed_mph) * 60
        total_time = base_time + traffic_delay_minutes
        
        arrival_time = datetime.now() + timedelta(minutes=total_time)
        
        return {
            'remaining_distance_miles': round(remaining_distance_miles, 2),
            'base_eta_minutes': round(base_time, 1),
            'traffic_delay_minutes': round(traffic_delay_minutes, 1),
            'total_eta_minutes': round(total_time, 1),
            'estimated_arrival': arrival_time.strftime('%I:%M %p'),
            'estimated_arrival_iso': arrival_time.isoformat()
        }
