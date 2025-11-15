#!/usr/bin/env python3
"""
Navigation Overlay+ Service
Enhanced navigation with speed limits, POI, real-time traffic, and route planning
Port: 9600
"""

import os
import sys
import json
import uuid
import requests
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
from threading import Thread, Lock
import time

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.navigation.database import NavigationDatabase
from services.navigation.speedlimit import SpeedLimitDetector
from services.navigation.poi import POIFinder
from services.navigation.traffic import TrafficMonitor
from services.navigation.routing import RoutePlanner

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

TEMPLATE_DIR = Path(__file__).parent / 'templates'
STATIC_DIR = Path(__file__).parent / 'static'

TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.template_folder = str(TEMPLATE_DIR)
app.static_folder = str(STATIC_DIR)

db = NavigationDatabase()
speed_detector = SpeedLimitDetector(db)
poi_finder = POIFinder(db)
traffic_monitor = TrafficMonitor(db)
route_planner = RoutePlanner(db)

FUEL_SERVICE_URL = os.environ.get('FUEL_SERVICE_URL', 'http://localhost:9900')
ANALYTICS_SERVICE_URL = os.environ.get('ANALYTICS_SERVICE_URL', 'http://localhost:9200')

current_navigation_session = None
session_lock = Lock()
gps_polling_active = False

navigation_state = {
    'session_id': None,
    'current_route': None,
    'current_position': {'lat': 42.3314, 'lng': -83.0458},
    'current_speed_mph': 0,
    'current_heading': 0,
    'speed_limit_mph': 35,
    'road_name': 'Main Street',
    'road_type': 'arterial',
    'next_turn': None,
    'distance_to_turn_miles': 0,
    'eta_minutes': 0,
    'traffic_delay_minutes': 0,
    'fuel_range_miles': 300,
    'nearby_pois': {},
    'traffic_incidents': [],
    'audio_alerts': []
}


def poll_gps_and_fuel():
    """Poll GPS from analytics service and fuel data from fuel service."""
    global gps_polling_active, navigation_state
    
    while gps_polling_active:
        try:
            if not current_navigation_session:
                time.sleep(2)
                continue
            
            try:
                analytics_response = requests.get(
                    f'{ANALYTICS_SERVICE_URL}/api/trip/current', timeout=2
                )
                if analytics_response.status_code == 200:
                    analytics_data = analytics_response.json()
                    if analytics_data.get('ok'):
                        trip = analytics_data.get('trip', {})
                        navigation_state['current_speed_mph'] = trip.get('current_speed_mph', 0)
            except:
                pass
            
            try:
                fuel_response = requests.get(
                    f'{FUEL_SERVICE_URL}/api/session/current', timeout=2
                )
                if fuel_response.status_code == 200:
                    fuel_data = fuel_response.json()
                    if fuel_data.get('ok'):
                        session = fuel_data.get('session', {})
                        current_mpg = session.get('trip_mpg', 30)
                        fuel_consumed = session.get('fuel_consumed_gallons', 0)
                        tank_capacity = 12.5
                        estimated_fuel_remaining = tank_capacity - fuel_consumed
                        navigation_state['fuel_range_miles'] = estimated_fuel_remaining * current_mpg
            except:
                pass
            
            if navigation_state['current_route']:
                turns = navigation_state['current_route'].get('turns', [])
                next_turn_data = route_planner.get_next_turn(
                    navigation_state['current_position'], turns
                )
                if next_turn_data:
                    navigation_state['next_turn'] = next_turn_data
                    navigation_state['distance_to_turn_miles'] = next_turn_data.get('distance_to_turn_miles', 0)
            
            speed_status = speed_detector.get_speed_limit_display(
                navigation_state['current_speed_mph'],
                navigation_state['speed_limit_mph']
            )
            
            if speed_status.get('audio_alert'):
                navigation_state['audio_alerts'].append({
                    'type': 'speed_warning',
                    'message': speed_status['audio_alert'],
                    'timestamp': datetime.now().isoformat()
                })
            
            db.update_navigation_session(current_navigation_session, {
                'current_lat': navigation_state['current_position']['lat'],
                'current_lng': navigation_state['current_position']['lng'],
                'current_speed_mph': navigation_state['current_speed_mph'],
                'current_speed_limit': navigation_state['speed_limit_mph'],
                'next_turn_distance_miles': navigation_state['distance_to_turn_miles'],
                'next_turn_instruction': navigation_state['next_turn'].get('instruction', '') if navigation_state['next_turn'] else '',
                'eta_minutes': navigation_state['eta_minutes']
            })
        
        except Exception as e:
            print(f"GPS/Fuel polling error: {e}")
        
        time.sleep(2)


@app.route('/')
def index():
    """Serve navigation dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('NAVIGATION_PORT', 9600))
    
    return jsonify({
        'ok': True,
        'service': 'navigation_overlay_plus',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'features': {
            'speed_limit_detection': True,
            'poi_finder': True,
            'traffic_monitoring': True,
            'route_planning': True,
            'lane_guidance': True,
            'voice_guidance': True,
            'saved_locations': True,
            'fuel_integration': True,
            'gps_integration': True
        },
        'active_navigation': current_navigation_session is not None,
        'gps_polling': gps_polling_active
    })


@app.route('/api/navigation/start', methods=['POST'])
def api_start_navigation():
    """Start navigation session."""
    global current_navigation_session, gps_polling_active, navigation_state
    
    try:
        with session_lock:
            if current_navigation_session:
                return jsonify({
                    'ok': False,
                    'error': 'Navigation session already active',
                    'session_id': current_navigation_session
                }), 400
            
            data = request.json or {}
            
            destination = data.get('destination')
            if not destination or 'lat' not in destination or 'lng' not in destination:
                return jsonify({
                    'ok': False,
                    'error': 'Destination with lat/lng required'
                }), 400
            
            origin = data.get('origin', navigation_state['current_position'])
            route_strategy = data.get('strategy', 'fastest')
            
            route = route_planner.plan_route(origin, destination, route_strategy)
            
            session_id = f"nav_session_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
            
            db.create_navigation_session(
                session_id, route['route_id'], 
                destination.get('address', 'Unknown destination')
            )
            
            current_navigation_session = session_id
            navigation_state['session_id'] = session_id
            navigation_state['current_route'] = route
            navigation_state['current_position'] = origin
            
            if route['turns']:
                navigation_state['next_turn'] = route['turns'][0]
                navigation_state['distance_to_turn_miles'] = route['turns'][0].get('distance_miles', 0)
            
            navigation_state['eta_minutes'] = route['duration_minutes']
            
            traffic_segments = traffic_monitor.generate_traffic_conditions(
                origin['lat'], origin['lng'], route['distance_miles']
            )
            incidents = traffic_monitor.generate_incidents(
                origin['lat'], origin['lng'], route['distance_miles']
            )
            
            navigation_state['traffic_incidents'] = incidents
            traffic_delay = traffic_monitor.calculate_total_delay(traffic_segments, incidents)
            navigation_state['traffic_delay_minutes'] = traffic_delay
            
            nearby_pois = poi_finder.search_nearby(
                origin['lat'], origin['lng'],
                categories=['gas_station', 'restaurant', 'rest_area'],
                radius_miles=10, limit=5
            )
            navigation_state['nearby_pois'] = nearby_pois
            
            if not gps_polling_active:
                gps_polling_active = True
                Thread(target=poll_gps_and_fuel, daemon=True).start()
            
            return jsonify({
                'ok': True,
                'session_id': session_id,
                'route': route,
                'traffic': {
                    'segments': traffic_segments,
                    'incidents': incidents,
                    'total_delay_minutes': traffic_delay
                },
                'nearby_pois': nearby_pois,
                'gps_polling': gps_polling_active
            })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/navigation/stop', methods=['POST'])
def api_stop_navigation():
    """Stop navigation session."""
    global current_navigation_session, gps_polling_active, navigation_state
    
    try:
        with session_lock:
            if not current_navigation_session:
                return jsonify({
                    'ok': False,
                    'error': 'No active navigation session'
                }), 400
            
            db.end_navigation_session(current_navigation_session)
            
            stopped_session = current_navigation_session
            current_navigation_session = None
            gps_polling_active = False
            
            summary = {
                'session_id': stopped_session,
                'route': navigation_state.get('current_route'),
                'total_alerts': len(navigation_state.get('audio_alerts', []))
            }
            
            navigation_state = {
                'session_id': None,
                'current_route': None,
                'current_position': navigation_state['current_position'],
                'current_speed_mph': 0,
                'current_heading': 0,
                'speed_limit_mph': 35,
                'road_name': 'Main Street',
                'road_type': 'arterial',
                'next_turn': None,
                'distance_to_turn_miles': 0,
                'eta_minutes': 0,
                'traffic_delay_minutes': 0,
                'fuel_range_miles': 300,
                'nearby_pois': {},
                'traffic_incidents': [],
                'audio_alerts': []
            }
            
            return jsonify({
                'ok': True,
                'summary': summary
            })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/navigation/current')
def api_current_navigation():
    """Get current navigation state."""
    try:
        if not current_navigation_session:
            return jsonify({
                'ok': False,
                'error': 'No active navigation session',
                'state': navigation_state
            })
        
        speed_status = speed_detector.get_speed_limit_display(
            navigation_state['current_speed_mph'],
            navigation_state['speed_limit_mph']
        )
        
        hud_data = {
            'next_turn_distance_miles': navigation_state['distance_to_turn_miles'],
            'next_turn_distance_feet': int(navigation_state['distance_to_turn_miles'] * 5280),
            'next_turn_instruction': navigation_state['next_turn'].get('instruction', '') if navigation_state['next_turn'] else '',
            'current_speed_mph': navigation_state['current_speed_mph'],
            'speed_limit_mph': navigation_state['speed_limit_mph'],
            'speed_status': speed_status,
            'eta_minutes': navigation_state['eta_minutes'] + navigation_state['traffic_delay_minutes'],
            'traffic_delay_minutes': navigation_state['traffic_delay_minutes']
        }
        
        return jsonify({
            'ok': True,
            'session_id': current_navigation_session,
            'state': navigation_state,
            'hud': hud_data,
            'speed_status': speed_status
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/speed/current')
def api_current_speed():
    """Get current speed and speed limit status."""
    try:
        speed_status = speed_detector.get_speed_limit_display(
            navigation_state['current_speed_mph'],
            navigation_state['speed_limit_mph']
        )
        
        return jsonify({
            'ok': True,
            'speed_status': speed_status,
            'road_name': navigation_state['road_name'],
            'road_type': navigation_state['road_type']
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/speed/detect', methods=['POST'])
def api_detect_speed_limit():
    """Detect speed limit for location."""
    try:
        data = request.json or {}
        
        road_name = data.get('road_name')
        road_type = data.get('road_type')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        speed_limit = speed_detector.detect_speed_limit(
            road_name, road_type, latitude, longitude
        )
        
        return jsonify({
            'ok': True,
            'speed_limit_mph': speed_limit,
            'road_name': road_name,
            'road_type': road_type
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/poi/search')
def api_search_poi():
    """Search for nearby POIs."""
    try:
        latitude = float(request.args.get('lat', navigation_state['current_position']['lat']))
        longitude = float(request.args.get('lng', navigation_state['current_position']['lng']))
        category = request.args.get('category')
        radius_miles = float(request.args.get('radius', 5))
        limit = int(request.args.get('limit', 10))
        
        if category:
            pois = poi_finder.generate_nearby_pois(
                latitude, longitude, category, radius_miles, limit
            )
            results = {category: pois}
        else:
            results = poi_finder.search_nearby(
                latitude, longitude, radius_miles=radius_miles, limit=limit
            )
        
        return jsonify({
            'ok': True,
            'position': {'lat': latitude, 'lng': longitude},
            'pois': results,
            'total': sum(len(pois) for pois in results.values())
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/poi/nearest/<category>')
def api_nearest_poi(category: str):
    """Find nearest POI of specific category."""
    try:
        latitude = float(request.args.get('lat', navigation_state['current_position']['lat']))
        longitude = float(request.args.get('lng', navigation_state['current_position']['lng']))
        fuel_range = request.args.get('fuel_range')
        
        fuel_range_miles = float(fuel_range) if fuel_range else None
        
        nearest = poi_finder.find_nearest(
            latitude, longitude, category, fuel_range_miles
        )
        
        if not nearest:
            return jsonify({
                'ok': False,
                'error': f'No {category} found nearby'
            }), 404
        
        return jsonify({
            'ok': True,
            'poi': nearest
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/poi/fuel_stop')
def api_fuel_stop_recommendation():
    """Get fuel stop recommendation."""
    try:
        dest_lat = float(request.args.get('dest_lat'))
        dest_lng = float(request.args.get('dest_lng'))
        
        current_lat = navigation_state['current_position']['lat']
        current_lng = navigation_state['current_position']['lng']
        fuel_range = navigation_state['fuel_range_miles']
        
        recommendation = poi_finder.recommend_fuel_stop(
            current_lat, current_lng, dest_lat, dest_lng, fuel_range
        )
        
        return jsonify({
            'ok': True,
            'recommendation': recommendation
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/traffic/conditions')
def api_traffic_conditions():
    """Get traffic conditions for route."""
    try:
        latitude = float(request.args.get('lat', navigation_state['current_position']['lat']))
        longitude = float(request.args.get('lng', navigation_state['current_position']['lng']))
        distance = float(request.args.get('distance', 10))
        
        segments = traffic_monitor.generate_traffic_conditions(
            latitude, longitude, distance
        )
        incidents = traffic_monitor.generate_incidents(
            latitude, longitude, distance
        )
        
        summary = traffic_monitor.get_traffic_summary(segments, incidents)
        
        return jsonify({
            'ok': True,
            'traffic_segments': segments,
            'incidents': incidents,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/traffic/incidents')
def api_traffic_incidents():
    """Get active traffic incidents."""
    try:
        incidents = db.get_traffic_incidents(active_only=True)
        
        return jsonify({
            'ok': True,
            'incidents': incidents,
            'count': len(incidents)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/traffic/alternative_route')
def api_alternative_route():
    """Get alternative route suggestion."""
    try:
        if not navigation_state.get('current_route'):
            return jsonify({
                'ok': False,
                'error': 'No active route'
            }), 400
        
        route = navigation_state['current_route']
        origin = route['origin']
        destination = route['destination']
        
        traffic_delay = navigation_state.get('traffic_delay_minutes', 0)
        
        alternative = traffic_monitor.suggest_alternative_route(
            origin, destination, traffic_delay
        )
        
        if alternative:
            return jsonify({
                'ok': True,
                'has_alternative': True,
                'alternative': alternative
            })
        else:
            return jsonify({
                'ok': True,
                'has_alternative': False,
                'message': 'Current route is optimal'
            })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/route/plan', methods=['POST'])
def api_plan_route():
    """Plan a route."""
    try:
        data = request.json or {}
        
        origin = data.get('origin', navigation_state['current_position'])
        destination = data.get('destination')
        
        if not destination:
            return jsonify({
                'ok': False,
                'error': 'Destination required'
            }), 400
        
        strategy = data.get('strategy', 'fastest')
        
        route = route_planner.plan_route(origin, destination, strategy)
        
        return jsonify({
            'ok': True,
            'route': route
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/route/compare', methods=['POST'])
def api_compare_routes():
    """Compare multiple route strategies."""
    try:
        data = request.json or {}
        
        origin = data.get('origin', navigation_state['current_position'])
        destination = data.get('destination')
        
        if not destination:
            return jsonify({
                'ok': False,
                'error': 'Destination required'
            }), 400
        
        strategies = data.get('strategies', ['fastest', 'fuel_efficient', 'avoid_tolls'])
        
        routes = route_planner.compare_routes(origin, destination, strategies)
        
        return jsonify({
            'ok': True,
            'routes': routes,
            'count': len(routes)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/locations/saved')
def api_saved_locations():
    """Get all saved locations."""
    try:
        locations = db.get_saved_locations()
        
        return jsonify({
            'ok': True,
            'locations': locations,
            'count': len(locations)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/locations/save', methods=['POST'])
def api_save_location():
    """Save a location."""
    try:
        data = request.json or {}
        
        name = data.get('name')
        label = data.get('label')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not all([name, label, latitude, longitude]):
            return jsonify({
                'ok': False,
                'error': 'Name, label, latitude, and longitude required'
            }), 400
        
        location_id = f"loc_{uuid.uuid4().hex[:8]}"
        address = data.get('address')
        icon = data.get('icon', 'pin')
        
        success = db.save_location(
            location_id, name, label, latitude, longitude, address, icon
        )
        
        if success:
            return jsonify({
                'ok': True,
                'location_id': location_id,
                'message': 'Location saved successfully'
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to save location'
            }), 500
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/locations/<location_id>', methods=['DELETE'])
def api_delete_location(location_id: str):
    """Delete a saved location."""
    try:
        success = db.delete_location(location_id)
        
        if success:
            return jsonify({
                'ok': True,
                'message': 'Location deleted successfully'
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to delete location'
            }), 500
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/locations/navigate/<location_id>', methods=['POST'])
def api_navigate_to_location(location_id: str):
    """Start navigation to a saved location."""
    try:
        location = db.get_location(location_id)
        
        if not location:
            return jsonify({
                'ok': False,
                'error': 'Location not found'
            }), 404
        
        db.update_location_last_used(location_id)
        
        destination = {
            'lat': location['latitude'],
            'lng': location['longitude'],
            'address': location.get('address', location['name'])
        }
        
        return api_start_navigation()
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/routes/recent')
def api_recent_routes():
    """Get recent routes."""
    try:
        limit = int(request.args.get('limit', 10))
        routes = db.get_recent_routes(limit)
        
        return jsonify({
            'ok': True,
            'routes': routes,
            'count': len(routes)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/hud')
def api_hud_data():
    """Get heads-up display data."""
    try:
        if not current_navigation_session:
            return jsonify({
                'ok': False,
                'error': 'No active navigation'
            })
        
        speed_status = speed_detector.get_speed_limit_display(
            navigation_state['current_speed_mph'],
            navigation_state['speed_limit_mph']
        )
        
        eta_data = route_planner.calculate_eta(
            navigation_state['current_route']['distance_miles'] if navigation_state.get('current_route') else 0,
            navigation_state['current_speed_mph'] if navigation_state['current_speed_mph'] > 0 else 50,
            navigation_state['traffic_delay_minutes']
        )
        
        hud = {
            'next_turn': {
                'distance_miles': navigation_state['distance_to_turn_miles'],
                'distance_feet': int(navigation_state['distance_to_turn_miles'] * 5280),
                'instruction': navigation_state['next_turn'].get('instruction', '') if navigation_state['next_turn'] else 'Continue',
                'road_name': navigation_state['next_turn'].get('road_name', '') if navigation_state['next_turn'] else ''
            },
            'speed': {
                'current_mph': navigation_state['current_speed_mph'],
                'limit_mph': navigation_state['speed_limit_mph'],
                'status': speed_status['status'],
                'color': speed_status['color'],
                'display_text': speed_status['display_text']
            },
            'eta': eta_data,
            'traffic': {
                'delay_minutes': navigation_state['traffic_delay_minutes'],
                'incidents_count': len(navigation_state['traffic_incidents'])
            }
        }
        
        return jsonify({
            'ok': True,
            'hud': hud
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/voice/alerts')
def api_voice_alerts():
    """Get pending voice alerts."""
    try:
        alerts = navigation_state.get('audio_alerts', [])
        
        navigation_state['audio_alerts'] = []
        
        return jsonify({
            'ok': True,
            'alerts': alerts,
            'count': len(alerts)
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('NAVIGATION_PORT', 9600))
    
    print(f"🗺️  Navigation Overlay+ Service")
    print(f"📍 Starting on port {port}")
    print(f"🚗 Features: Speed Limits, POI, Traffic, Route Planning")
    print(f"⛽ Integration: Fuel Service (port 9900), Analytics Service (port 9200)")
    
    app.run(host='0.0.0.0', port=port, debug=True)
