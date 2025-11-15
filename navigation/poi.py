#!/usr/bin/env python3
"""
Points of Interest (POI) Finder Module
Finds nearby gas stations, restaurants, EV charging, rest areas, and parking
"""

import math
import random
from typing import List, Dict, Tuple, Optional


class POIFinder:
    """Points of Interest finder."""
    
    def __init__(self, database):
        """Initialize POI finder."""
        self.db = database
        
        self.poi_templates = {
            'gas_station': [
                'Shell', 'Chevron', 'Exxon', 'Mobil', 'BP', 'Texaco', 
                'Valero', 'Marathon', 'Speedway', 'Circle K', 'Sunoco'
            ],
            'restaurant': [
                "McDonald's", 'Subway', 'Starbucks', 'Taco Bell', 'Wendy\'s',
                'Burger King', 'KFC', 'Pizza Hut', 'Chipotle', 'Panera Bread',
                'Chick-fil-A', 'Arby\'s', 'Sonic Drive-In', 'Dairy Queen'
            ],
            'ev_charging': [
                'Tesla Supercharger', 'ChargePoint', 'EVgo', 'Electrify America',
                'Blink Charging', 'Volta', 'Greenlots', 'SemaConnect'
            ],
            'rest_area': [
                'Highway Rest Area', 'Travel Plaza', 'Service Plaza', 
                'Welcome Center', 'Roadside Rest Stop'
            ],
            'parking': [
                'Public Parking Garage', 'Park & Ride', 'Metered Parking',
                'Parking Lot', 'Street Parking', 'Covered Parking'
            ]
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
    
    def generate_nearby_pois(self, latitude: float, longitude: float, 
                            category: str, radius_miles: float = 5,
                            count: int = 10) -> List[Dict]:
        """
        Generate simulated nearby POIs.
        In production, this would call a real POI API like Google Places.
        """
        pois = []
        
        if category not in self.poi_templates:
            return pois
        
        names = self.poi_templates[category]
        
        for i in range(count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.1, radius_miles)
            
            dlat = (distance / 69.0) * math.cos(angle)
            dlng = (distance / (69.0 * math.cos(math.radians(latitude)))) * math.sin(angle)
            
            poi_lat = latitude + dlat
            poi_lng = longitude + dlng
            
            actual_distance = self.calculate_distance(latitude, longitude, poi_lat, poi_lng)
            
            name = random.choice(names)
            if category != 'rest_area':
                name += f" #{random.randint(1000, 9999)}"
            
            poi = {
                'poi_id': f"{category}_{i}_{int(latitude*1000)}_{int(longitude*1000)}",
                'name': name,
                'category': category,
                'latitude': poi_lat,
                'longitude': poi_lng,
                'distance_miles': round(actual_distance, 2),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'address': f"{random.randint(100, 9999)} Main St",
                'amenities': self._generate_amenities(category),
                'phone': f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                'hours': self._generate_hours(category)
            }
            
            pois.append(poi)
        
        pois.sort(key=lambda x: x['distance_miles'])
        
        for poi in pois:
            self.db.cache_poi(
                poi['poi_id'], poi['name'], poi['category'],
                poi['latitude'], poi['longitude'], poi['address'],
                poi['rating'], poi['distance_miles'], poi['amenities']
            )
        
        return pois
    
    def _generate_amenities(self, category: str) -> List[str]:
        """Generate realistic amenities for POI category."""
        amenities_map = {
            'gas_station': ['Convenience Store', 'ATM', 'Air Pump', 'Car Wash', 'Restrooms'],
            'restaurant': ['Wi-Fi', 'Drive-Thru', 'Outdoor Seating', 'Delivery', 'Takeout'],
            'ev_charging': ['Fast Charging', 'Multiple Ports', 'Covered Parking', 'Wi-Fi', 'Restrooms'],
            'rest_area': ['Restrooms', 'Picnic Tables', 'Vending Machines', 'Pet Area', 'Wi-Fi'],
            'parking': ['Covered', 'Security', '24/7 Access', 'EV Charging', 'Handicap Accessible']
        }
        
        available = amenities_map.get(category, [])
        count = random.randint(2, min(4, len(available)))
        return random.sample(available, count)
    
    def _generate_hours(self, category: str) -> str:
        """Generate operating hours for POI."""
        if category in ['gas_station', 'rest_area']:
            return '24/7'
        elif category == 'ev_charging':
            return '24/7'
        elif category == 'parking':
            return random.choice(['24/7', '6:00 AM - 10:00 PM', '7:00 AM - 9:00 PM'])
        else:
            open_hour = random.randint(6, 8)
            close_hour = random.randint(20, 23)
            return f"{open_hour}:00 AM - {close_hour}:00 PM"
    
    def search_nearby(self, latitude: float, longitude: float,
                     categories: List[str] = None, radius_miles: float = 5,
                     limit: int = 10) -> Dict[str, List[Dict]]:
        """
        Search for nearby POIs across categories.
        
        Returns dict with category as key and list of POIs as value.
        """
        if categories is None:
            categories = ['gas_station', 'restaurant', 'ev_charging', 'rest_area', 'parking']
        
        results = {}
        
        for category in categories:
            pois = self.generate_nearby_pois(latitude, longitude, category, radius_miles, limit)
            results[category] = pois
        
        return results
    
    def find_nearest(self, latitude: float, longitude: float, 
                    category: str, fuel_range_miles: float = None) -> Optional[Dict]:
        """
        Find nearest POI of a specific type.
        Optionally filter by fuel range.
        """
        pois = self.generate_nearby_pois(latitude, longitude, category, 
                                         radius_miles=50, count=20)
        
        if not pois:
            return None
        
        if fuel_range_miles:
            pois = [poi for poi in pois if poi['distance_miles'] <= fuel_range_miles]
        
        return pois[0] if pois else None
    
    def get_poi_details(self, poi_id: str) -> Optional[Dict]:
        """Get detailed POI information."""
        cached_pois = self.db.get_cached_pois()
        
        for poi in cached_pois:
            if poi['poi_id'] == poi_id:
                return poi
        
        return None
    
    def recommend_fuel_stop(self, current_lat: float, current_lng: float,
                           destination_lat: float, destination_lng: float,
                           current_fuel_range_miles: float,
                           prefer_brand: str = None) -> Optional[Dict]:
        """
        Recommend optimal fuel stop based on route and fuel range.
        """
        total_distance = self.calculate_distance(
            current_lat, current_lng, destination_lat, destination_lng
        )
        
        if current_fuel_range_miles >= total_distance:
            return {
                'needs_fuel_stop': False,
                'message': 'Sufficient fuel to reach destination',
                'fuel_range_remaining': current_fuel_range_miles - total_distance
            }
        
        search_radius = min(current_fuel_range_miles * 0.7, 50)
        
        gas_stations = self.generate_nearby_pois(
            current_lat, current_lng, 'gas_station', 
            radius_miles=search_radius, count=20
        )
        
        if prefer_brand:
            preferred = [gs for gs in gas_stations if prefer_brand.lower() in gs['name'].lower()]
            if preferred:
                gas_stations = preferred
        
        if not gas_stations:
            return {
                'needs_fuel_stop': True,
                'message': 'Warning: No gas stations found within fuel range',
                'recommended_station': None
            }
        
        best_station = min(gas_stations, key=lambda x: x['distance_miles'])
        
        return {
            'needs_fuel_stop': True,
            'message': f"Fuel stop recommended in {best_station['distance_miles']} miles",
            'recommended_station': best_station,
            'current_fuel_range': current_fuel_range_miles,
            'distance_to_destination': total_distance
        }
    
    def filter_by_amenities(self, pois: List[Dict], required_amenities: List[str]) -> List[Dict]:
        """Filter POIs by required amenities."""
        filtered = []
        
        for poi in pois:
            amenities = poi.get('amenities', [])
            if all(amenity in amenities for amenity in required_amenities):
                filtered.append(poi)
        
        return filtered
    
    def filter_by_rating(self, pois: List[Dict], min_rating: float = 4.0) -> List[Dict]:
        """Filter POIs by minimum rating."""
        return [poi for poi in pois if poi.get('rating', 0) >= min_rating]
