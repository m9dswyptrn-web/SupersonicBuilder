import os
import base64
import json
from typing import Dict, List, Optional, Any, Tuple
from io import BytesIO
from PIL import Image
import requests


class ObjectDetector:
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.model = 'claude-sonnet-4-20250514'
        self.has_api_key = bool(self.api_key)
        
        self.object_types = {
            'car': {'priority': 'high', 'typical_width_cm': 180},
            'pedestrian': {'priority': 'critical', 'typical_width_cm': 50},
            'wall': {'priority': 'high', 'typical_width_cm': None},
            'curb': {'priority': 'medium', 'typical_width_cm': 15},
            'pole': {'priority': 'high', 'typical_width_cm': 10},
            'bollard': {'priority': 'high', 'typical_width_cm': 15},
            'motorcycle': {'priority': 'medium', 'typical_width_cm': 80},
            'bicycle': {'priority': 'medium', 'typical_width_cm': 60},
            'cart': {'priority': 'low', 'typical_width_cm': 70}
        }
    
    def analyze_parking_scene(
        self,
        image_data: bytes,
        camera_position: str,
        context: str = "parking"
    ) -> Dict[str, Any]:
        """
        Analyze a parking scene using AI vision.
        Falls back to simulated detection if no API key.
        """
        if not self.has_api_key:
            return self._simulated_detection(camera_position, context)
        
        try:
            return self._ai_detection(image_data, camera_position, context)
        except Exception as e:
            print(f"AI detection error: {e}, falling back to simulation")
            return self._simulated_detection(camera_position, context)
    
    def _ai_detection(
        self,
        image_data: bytes,
        camera_position: str,
        context: str
    ) -> Dict[str, Any]:
        """Use Anthropic Claude for object detection."""
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        prompt = f"""Analyze this {camera_position} camera view for parking assistance.

Identify any objects that could be obstacles or hazards:
- Vehicles (cars, motorcycles, bicycles)
- Pedestrians
- Walls, curbs, poles, bollards
- Any other obstacles

For each object detected, provide:
1. Object type
2. Approximate distance from camera (in centimeters, estimate based on size)
3. Position (left/center/right)
4. Risk level (critical/high/medium/low)
5. Confidence (0.0-1.0)

Respond in JSON format:
{{
  "objects": [
    {{
      "type": "car",
      "distance_cm": 150,
      "position": "center",
      "risk": "high",
      "confidence": 0.9,
      "description": "Silver sedan directly behind"
    }}
  ],
  "overall_risk": "high",
  "recommendation": "Stop immediately, obstacle detected"
}}"""

        headers = {
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
            'x-api-key': self.api_key
        }
        
        payload = {
            'model': self.model,
            'max_tokens': 1024,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/jpeg',
                                'data': base64_image
                            }
                        },
                        {
                            'type': 'text',
                            'text': prompt
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        content_text = result['content'][0]['text']
        
        json_start = content_text.find('{')
        json_end = content_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            content_text = content_text[json_start:json_end]
        
        detection_result = json.loads(content_text)
        
        return {
            'ok': True,
            'method': 'ai',
            'model': self.model,
            'camera_position': camera_position,
            'objects': detection_result.get('objects', []),
            'overall_risk': detection_result.get('overall_risk', 'low'),
            'recommendation': detection_result.get('recommendation', 'Clear'),
            'tokens_used': result.get('usage', {}).get('input_tokens', 0) + 
                          result.get('usage', {}).get('output_tokens', 0)
        }
    
    def _simulated_detection(
        self,
        camera_position: str,
        context: str
    ) -> Dict[str, Any]:
        """Simulate object detection for demo/fallback."""
        import random
        
        simulation_scenarios = {
            'rear': [
                {
                    'objects': [
                        {
                            'type': 'wall',
                            'distance_cm': 120,
                            'position': 'center',
                            'risk': 'medium',
                            'confidence': 0.95,
                            'description': 'Concrete wall behind vehicle'
                        },
                        {
                            'type': 'curb',
                            'distance_cm': 80,
                            'position': 'left',
                            'risk': 'low',
                            'confidence': 0.85,
                            'description': 'Parking curb on left side'
                        }
                    ],
                    'overall_risk': 'medium',
                    'recommendation': 'Proceed slowly, wall at 120cm'
                },
                {
                    'objects': [
                        {
                            'type': 'car',
                            'distance_cm': 200,
                            'position': 'center',
                            'risk': 'low',
                            'confidence': 0.92,
                            'description': 'Parked vehicle behind'
                        }
                    ],
                    'overall_risk': 'low',
                    'recommendation': 'Safe distance maintained'
                }
            ],
            'front': [
                {
                    'objects': [],
                    'overall_risk': 'low',
                    'recommendation': 'Path clear'
                },
                {
                    'objects': [
                        {
                            'type': 'pedestrian',
                            'distance_cm': 300,
                            'position': 'right',
                            'risk': 'medium',
                            'confidence': 0.88,
                            'description': 'Person walking on right side'
                        }
                    ],
                    'overall_risk': 'medium',
                    'recommendation': 'Pedestrian detected, proceed with caution'
                }
            ],
            'left': [
                {
                    'objects': [
                        {
                            'type': 'car',
                            'distance_cm': 150,
                            'position': 'center',
                            'risk': 'medium',
                            'confidence': 0.9,
                            'description': 'Adjacent parked vehicle'
                        }
                    ],
                    'overall_risk': 'medium',
                    'recommendation': 'Maintain clearance from adjacent vehicle'
                }
            ],
            'right': [
                {
                    'objects': [
                        {
                            'type': 'pole',
                            'distance_cm': 90,
                            'position': 'center',
                            'risk': 'high',
                            'confidence': 0.93,
                            'description': 'Light pole close to vehicle'
                        }
                    ],
                    'overall_risk': 'high',
                    'recommendation': 'Caution: Pole at 90cm on right'
                }
            ]
        }
        
        scenario = random.choice(simulation_scenarios.get(camera_position, [
            {'objects': [], 'overall_risk': 'low', 'recommendation': 'Clear'}
        ]))
        
        return {
            'ok': True,
            'method': 'simulated',
            'model': 'simulation',
            'camera_position': camera_position,
            'objects': scenario['objects'],
            'overall_risk': scenario['overall_risk'],
            'recommendation': scenario['recommendation'],
            'note': 'Simulated detection (no AI API key configured)'
        }
    
    def estimate_distance_from_size(
        self,
        object_type: str,
        pixel_width: int,
        image_width: int,
        focal_length_mm: float = 3.6,
        sensor_width_mm: float = 5.76
    ) -> float:
        """Estimate distance based on object size in image."""
        
        if object_type not in self.object_types:
            return None
        
        real_width_cm = self.object_types[object_type]['typical_width_cm']
        if not real_width_cm:
            return None
        
        real_width_mm = real_width_cm * 10
        
        distance_mm = (real_width_mm * focal_length_mm * image_width) / (pixel_width * sensor_width_mm)
        
        distance_cm = distance_mm / 10
        
        return distance_cm
    
    def calculate_collision_risk(
        self,
        objects: List[Dict[str, Any]],
        vehicle_speed_kmh: float = 0.0,
        parking_mode: str = "reverse"
    ) -> Dict[str, Any]:
        """Calculate overall collision risk based on detected objects."""
        
        if not objects:
            return {
                'risk_level': 'low',
                'risk_score': 0.0,
                'should_alert': False,
                'should_stop': False,
                'message': 'No obstacles detected'
            }
        
        critical_distance_cm = 50
        warning_distance_cm = 100
        safe_distance_cm = 150
        
        closest_object = min(objects, key=lambda x: x.get('distance_cm', 999999))
        closest_distance = closest_object.get('distance_cm', 999999)
        
        risk_score = 0.0
        
        if closest_distance < critical_distance_cm:
            risk_score = 1.0
        elif closest_distance < warning_distance_cm:
            risk_score = 0.5 + (warning_distance_cm - closest_distance) / (warning_distance_cm - critical_distance_cm) * 0.5
        elif closest_distance < safe_distance_cm:
            risk_score = (safe_distance_cm - closest_distance) / (safe_distance_cm - warning_distance_cm) * 0.5
        
        for obj in objects:
            if obj.get('type') == 'pedestrian':
                risk_score = min(1.0, risk_score + 0.3)
        
        if vehicle_speed_kmh > 5:
            risk_score = min(1.0, risk_score * 1.2)
        
        if risk_score >= 0.8:
            risk_level = 'critical'
            should_alert = True
            should_stop = True
            message = f"STOP! {closest_object.get('type', 'Obstacle')} at {closest_distance:.0f}cm"
        elif risk_score >= 0.5:
            risk_level = 'high'
            should_alert = True
            should_stop = False
            message = f"Caution: {closest_object.get('type', 'Obstacle')} at {closest_distance:.0f}cm"
        elif risk_score >= 0.2:
            risk_level = 'medium'
            should_alert = True
            should_stop = False
            message = f"Be aware: {closest_object.get('type', 'Obstacle')} detected"
        else:
            risk_level = 'low'
            should_alert = False
            should_stop = False
            message = "Safe distance maintained"
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'should_alert': should_alert,
            'should_stop': should_stop,
            'message': message,
            'closest_object': closest_object,
            'closest_distance_cm': closest_distance,
            'objects_detected': len(objects)
        }
    
    def get_parking_guidance(
        self,
        objects: List[Dict[str, Any]],
        parking_mode: str = "parallel"
    ) -> Dict[str, Any]:
        """Provide parking guidance based on detected objects."""
        
        guidance = {
            'mode': parking_mode,
            'instructions': [],
            'trajectory_points': [],
            'clearance': {}
        }
        
        if parking_mode == "parallel":
            guidance['instructions'] = [
                "Align vehicle parallel to curb",
                "Begin turning when rear axle aligns with front of parking space",
                "Turn wheel fully right",
                "Monitor right rear camera for curb distance",
                "Straighten when centered in space"
            ]
        elif parking_mode == "perpendicular":
            guidance['instructions'] = [
                "Approach at 45-degree angle",
                "Begin turning when front of vehicle passes target space",
                "Monitor side cameras for clearance",
                "Straighten when aligned with parking lines"
            ]
        elif parking_mode == "reverse":
            guidance['instructions'] = [
                "Check all cameras for obstacles",
                "Reverse slowly in straight line",
                "Monitor rear camera continuously",
                "Stop when reaching desired position"
            ]
        
        for obj in objects:
            position = obj.get('position', 'unknown')
            distance = obj.get('distance_cm', 0)
            
            if position not in guidance['clearance']:
                guidance['clearance'][position] = distance
            else:
                guidance['clearance'][position] = min(guidance['clearance'][position], distance)
        
        return guidance
