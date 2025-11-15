import math
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DistanceSensor:
    def __init__(self, position: str, max_range_cm: float = 300.0):
        self.position = position
        self.max_range_cm = max_range_cm
        self.min_range_cm = 20.0
        
        self.critical_distance_cm = 30.0
        self.warning_distance_cm = 80.0
        self.safe_distance_cm = 150.0
        
        self._simulated_distance = None
        self._last_update = None
    
    def get_distance(self) -> float:
        """Get current distance reading (simulated)."""
        return self._simulated_distance if self._simulated_distance is not None else self.max_range_cm
    
    def set_simulated_distance(self, distance_cm: float):
        """Set simulated distance for testing."""
        self._simulated_distance = max(self.min_range_cm, min(distance_cm, self.max_range_cm))
        self._last_update = datetime.utcnow()
    
    def get_status(self) -> str:
        """Get status based on current distance."""
        distance = self.get_distance()
        
        if distance <= self.critical_distance_cm:
            return 'critical'
        elif distance <= self.warning_distance_cm:
            return 'warning'
        elif distance <= self.safe_distance_cm:
            return 'caution'
        else:
            return 'safe'
    
    def get_color(self) -> str:
        """Get color code for visualization."""
        status = self.get_status()
        colors = {
            'critical': '#FF0000',
            'warning': '#FFA500',
            'caution': '#FFFF00',
            'safe': '#00FF00'
        }
        return colors.get(status, '#808080')
    
    def should_beep(self) -> bool:
        """Determine if beeping warning should be active."""
        return self.get_status() in ['critical', 'warning']
    
    def get_beep_frequency(self) -> float:
        """Get beeping frequency in Hz (higher = faster beeps)."""
        distance = self.get_distance()
        
        if distance <= self.critical_distance_cm:
            return 4.0
        elif distance <= self.warning_distance_cm:
            progress = (distance - self.critical_distance_cm) / (self.warning_distance_cm - self.critical_distance_cm)
            return 4.0 - (progress * 3.0)
        else:
            return 0.0


class DistanceSensorArray:
    def __init__(self):
        self.sensors = {
            'front': DistanceSensor('front'),
            'rear': DistanceSensor('rear'),
            'left_front': DistanceSensor('left_front'),
            'left_rear': DistanceSensor('left_rear'),
            'right_front': DistanceSensor('right_front'),
            'right_rear': DistanceSensor('right_rear')
        }
        
        self._simulation_mode = True
        self._randomize_simulation()
    
    def _randomize_simulation(self):
        """Generate random but realistic simulated distances."""
        base_distances = {
            'front': random.uniform(150, 300),
            'rear': random.uniform(80, 200),
            'left_front': random.uniform(100, 250),
            'left_rear': random.uniform(100, 250),
            'right_front': random.uniform(100, 250),
            'right_rear': random.uniform(100, 250)
        }
        
        for position, distance in base_distances.items():
            self.sensors[position].set_simulated_distance(distance)
    
    def update_distances(self, distances: Dict[str, float]):
        """Update sensor distances manually."""
        for position, distance in distances.items():
            if position in self.sensors:
                self.sensors[position].set_simulated_distance(distance)
    
    def simulate_reverse_parking(self, progress: float = 0.0):
        """Simulate distances during reverse parking (progress: 0.0 to 1.0)."""
        initial_rear = 300.0
        final_rear = 50.0
        
        rear_distance = initial_rear - (progress * (initial_rear - final_rear))
        
        self.sensors['rear'].set_simulated_distance(rear_distance)
        
        self.sensors['left_rear'].set_simulated_distance(
            random.uniform(80, 120) + (random.random() - 0.5) * 20
        )
        self.sensors['right_rear'].set_simulated_distance(
            random.uniform(80, 120) + (random.random() - 0.5) * 20
        )
        
        self.sensors['front'].set_simulated_distance(random.uniform(200, 300))
        self.sensors['left_front'].set_simulated_distance(random.uniform(150, 250))
        self.sensors['right_front'].set_simulated_distance(random.uniform(150, 250))
    
    def simulate_parallel_parking(self, progress: float = 0.0):
        """Simulate distances during parallel parking."""
        self.sensors['right_rear'].set_simulated_distance(
            150.0 - (progress * 100.0) + random.uniform(-10, 10)
        )
        self.sensors['right_front'].set_simulated_distance(
            200.0 - (progress * 120.0) + random.uniform(-10, 10)
        )
        
        self.sensors['rear'].set_simulated_distance(
            250.0 - (progress * 150.0) + random.uniform(-15, 15)
        )
        
        self.sensors['left_rear'].set_simulated_distance(random.uniform(180, 220))
        self.sensors['left_front'].set_simulated_distance(random.uniform(180, 220))
        self.sensors['front'].set_simulated_distance(random.uniform(200, 300))
    
    def get_all_distances(self) -> Dict[str, float]:
        """Get distances from all sensors."""
        return {
            position: sensor.get_distance()
            for position, sensor in self.sensors.items()
        }
    
    def get_all_statuses(self) -> Dict[str, str]:
        """Get status from all sensors."""
        return {
            position: sensor.get_status()
            for position, sensor in self.sensors.items()
        }
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get color codes from all sensors."""
        return {
            position: sensor.get_color()
            for position, sensor in self.sensors.items()
        }
    
    def get_visualization_data(self) -> Dict[str, Dict]:
        """Get complete visualization data for UI."""
        data = {}
        for position, sensor in self.sensors.items():
            data[position] = {
                'distance_cm': round(sensor.get_distance(), 1),
                'status': sensor.get_status(),
                'color': sensor.get_color(),
                'should_beep': sensor.should_beep(),
                'beep_frequency': round(sensor.get_beep_frequency(), 2)
            }
        return data
    
    def get_closest_sensor(self) -> Tuple[str, float]:
        """Get the sensor with the closest reading."""
        closest_position = None
        closest_distance = float('inf')
        
        for position, sensor in self.sensors.items():
            distance = sensor.get_distance()
            if distance < closest_distance:
                closest_distance = distance
                closest_position = position
        
        return closest_position, closest_distance
    
    def get_overall_status(self) -> str:
        """Get overall status (worst status among all sensors)."""
        statuses = list(self.get_all_statuses().values())
        
        if 'critical' in statuses:
            return 'critical'
        elif 'warning' in statuses:
            return 'warning'
        elif 'caution' in statuses:
            return 'caution'
        else:
            return 'safe'
    
    def should_alert(self) -> bool:
        """Determine if any alert should be triggered."""
        return self.get_overall_status() in ['critical', 'warning']
    
    def get_beeping_info(self) -> Dict[str, any]:
        """Get information for beeping simulation."""
        beeping_sensors = [
            (position, sensor.get_beep_frequency())
            for position, sensor in self.sensors.items()
            if sensor.should_beep()
        ]
        
        if not beeping_sensors:
            return {'active': False, 'frequency': 0.0, 'sensors': []}
        
        max_frequency_sensor = max(beeping_sensors, key=lambda x: x[1])
        
        return {
            'active': True,
            'frequency': max_frequency_sensor[1],
            'primary_sensor': max_frequency_sensor[0],
            'sensors': [pos for pos, _ in beeping_sensors]
        }
    
    def calculate_safe_trajectory(
        self,
        parking_mode: str = "reverse"
    ) -> List[Dict[str, float]]:
        """Calculate safe trajectory path based on sensor readings."""
        trajectory = []
        
        if parking_mode == "reverse":
            rear_distance = self.sensors['rear'].get_distance()
            left_distance = self.sensors['left_rear'].get_distance()
            right_distance = self.sensors['right_rear'].get_distance()
            
            safe_travel_distance = max(0, rear_distance - 50)
            
            left_clearance = left_distance > 80
            right_clearance = right_distance > 80
            
            if left_clearance and right_clearance:
                bias = 0.0
            elif left_clearance:
                bias = -0.3
            elif right_clearance:
                bias = 0.3
            else:
                bias = 0.0
            
            num_points = 10
            for i in range(num_points):
                progress = i / (num_points - 1)
                x = bias * progress * 50
                y = -progress * safe_travel_distance
                
                trajectory.append({
                    'x': x,
                    'y': y,
                    'safe': True
                })
        
        elif parking_mode == "parallel":
            trajectory = [
                {'x': 0, 'y': 0, 'safe': True},
                {'x': 20, 'y': -30, 'safe': True},
                {'x': 35, 'y': -60, 'safe': True},
                {'x': 40, 'y': -90, 'safe': True},
                {'x': 40, 'y': -120, 'safe': True},
                {'x': 35, 'y': -150, 'safe': True},
                {'x': 20, 'y': -170, 'safe': True},
                {'x': 0, 'y': -180, 'safe': True}
            ]
        
        return trajectory
