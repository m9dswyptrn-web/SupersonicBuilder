#!/usr/bin/env python3
"""
SONIC COMMAND CENTER
The unified master dashboard integrating all 30+ services
Port: 5000 (Main webview port)
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import logging

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.command_center.database import CommandCenterDatabase
from services.command_center.discovery import ServiceDiscovery
from services.command_center.integrations import ServiceIntegrations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sonic-command-center-key')
CORS(app)

TEMPLATE_DIR = Path(__file__).parent / 'templates'
STATIC_DIR = Path(__file__).parent / 'static'

TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.template_folder = str(TEMPLATE_DIR)
app.static_folder = str(STATIC_DIR)

db = CommandCenterDatabase()
discovery = ServiceDiscovery()
integrations = ServiceIntegrations()

start_time = datetime.now()


@app.route('/')
def index():
    """Serve the stunning command center dashboard."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    system_status = discovery.get_system_status()
    uptime_seconds = (datetime.now() - start_time).total_seconds()
    
    return jsonify({
        'ok': True,
        'service': 'sonic_command_center',
        'port': 5000,
        'status': 'healthy',
        'version': '1.0.0',
        'uptime_seconds': uptime_seconds,
        'system_health': {
            'total_services': system_status['total_services'],
            'online': system_status['online'],
            'offline': system_status['offline'],
            'health_percentage': system_status['health_percentage']
        },
        'features': {
            'service_discovery': True,
            'health_monitoring': True,
            'live_widgets': True,
            'quick_actions': True,
            'theme_support': True,
            'search': True,
            'alerts': True,
            'settings': True,
            'favorites': True
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/services/all')
def api_all_services():
    """Get all registered services."""
    services = discovery.get_all_services()
    
    return jsonify({
        'ok': True,
        'services': services,
        'count': len(services)
    })


@app.route('/api/services/categories')
def api_services_by_category():
    """Get services grouped by category."""
    categories = discovery.get_categories()
    
    category_names = {
        'hardware': 'Hardware Tools',
        'audio': 'Premium Audio',
        'visual': 'Visual Upgrades',
        'smart': 'Smart Features'
    }
    
    formatted = {}
    for cat_id, services in categories.items():
        formatted[cat_id] = {
            'name': category_names.get(cat_id, cat_id.title()),
            'services': services,
            'count': len(services)
        }
    
    return jsonify({
        'ok': True,
        'categories': formatted
    })


@app.route('/api/services/<service_id>')
def api_get_service(service_id: str):
    """Get service details."""
    service = discovery.get_service_by_id(service_id)
    
    if not service:
        return jsonify({
            'ok': False,
            'error': 'Service not found'
        }), 404
    
    health = discovery.check_health(service_id)
    
    return jsonify({
        'ok': True,
        'service': service,
        'health': health
    })


@app.route('/api/health/all')
def api_health_all():
    """Check health of all services."""
    status = discovery.get_system_status()
    
    return jsonify({
        'ok': True,
        'status': status
    })


@app.route('/api/health/<service_id>')
def api_health_service(service_id: str):
    """Check health of specific service."""
    service = discovery.get_service_by_id(service_id)
    
    if not service:
        return jsonify({
            'ok': False,
            'error': 'Service not found'
        }), 404
    
    health = discovery.check_health(service_id)
    
    return jsonify({
        'ok': True,
        'service_id': service_id,
        'health': health
    })


@app.route('/api/widgets/data')
def api_widget_data():
    """Get live data for all dashboard widgets."""
    data = integrations.get_all_widget_data()
    
    return jsonify({
        'ok': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/preferences')
def api_get_preferences():
    """Get all user preferences."""
    preferences = db.get_all_preferences()
    
    return jsonify({
        'ok': True,
        'preferences': preferences
    })


@app.route('/api/preferences/<key>')
def api_get_preference(key: str):
    """Get specific preference."""
    value = db.get_preference(key)
    
    if value is None:
        return jsonify({
            'ok': False,
            'error': 'Preference not found'
        }), 404
    
    return jsonify({
        'ok': True,
        'key': key,
        'value': value
    })


@app.route('/api/preferences', methods=['POST'])
def api_set_preferences():
    """Set user preferences."""
    try:
        data = request.json or {}
        
        for key, value in data.items():
            db.set_preference(key, str(value))
        
        return jsonify({
            'ok': True,
            'message': f'{len(data)} preferences updated'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/layouts')
def api_get_layouts():
    """Get all dashboard layouts."""
    layouts = db.get_all_layouts()
    
    return jsonify({
        'ok': True,
        'layouts': layouts
    })


@app.route('/api/layouts/active')
def api_get_active_layout():
    """Get active dashboard layout."""
    layout = db.get_active_layout()
    
    return jsonify({
        'ok': True,
        'layout': layout
    })


@app.route('/api/layouts', methods=['POST'])
def api_save_layout():
    """Save dashboard layout."""
    try:
        data = request.json or {}
        name = data.get('name')
        layout_data = data.get('layout')
        set_active = data.get('set_active', False)
        
        if not name or not layout_data:
            return jsonify({
                'ok': False,
                'error': 'Name and layout required'
            }), 400
        
        db.save_layout(name, layout_data, set_active)
        
        return jsonify({
            'ok': True,
            'message': 'Layout saved successfully'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts')
def api_get_alerts():
    """Get all active alerts."""
    service_id = request.args.get('service_id')
    alerts = db.get_active_alerts(service_id)
    
    return jsonify({
        'ok': True,
        'alerts': alerts,
        'count': len(alerts)
    })


@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def api_acknowledge_alert(alert_id: int):
    """Acknowledge an alert."""
    try:
        db.acknowledge_alert(alert_id)
        
        return jsonify({
            'ok': True,
            'message': 'Alert acknowledged'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts', methods=['POST'])
def api_add_alert():
    """Add system alert."""
    try:
        data = request.json or {}
        
        service_id = data.get('service_id')
        level = data.get('level', 'info')
        message = data.get('message')
        alert_data = data.get('data')
        
        if not service_id or not message:
            return jsonify({
                'ok': False,
                'error': 'service_id and message required'
            }), 400
        
        db.add_alert(service_id, level, message, alert_data)
        
        return jsonify({
            'ok': True,
            'message': 'Alert added'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/favorites')
def api_get_favorites():
    """Get favorite services."""
    favorites = db.get_favorites()
    
    return jsonify({
        'ok': True,
        'favorites': favorites
    })


@app.route('/api/favorites/<service_id>', methods=['POST'])
def api_add_favorite(service_id: str):
    """Add service to favorites."""
    try:
        db.add_favorite(service_id)
        
        return jsonify({
            'ok': True,
            'message': 'Added to favorites'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/favorites/<service_id>', methods=['DELETE'])
def api_remove_favorite(service_id: str):
    """Remove service from favorites."""
    try:
        db.remove_favorite(service_id)
        
        return jsonify({
            'ok': True,
            'message': 'Removed from favorites'
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500


@app.route('/api/search')
def api_search():
    """Search services."""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            'ok': False,
            'error': 'Query parameter required'
        }), 400
    
    all_services = discovery.get_all_services()
    
    results = []
    for service in all_services:
        if (query in service['name'].lower() or
            query in service['description'].lower() or
            query in service['id'].lower() or
            query in service['category'].lower()):
            results.append(service)
    
    return jsonify({
        'ok': True,
        'query': query,
        'results': results,
        'count': len(results)
    })


@app.route('/api/system/status')
def api_system_status():
    """Get comprehensive system status."""
    system_status = discovery.get_system_status()
    widget_data = integrations.get_all_widget_data()
    alerts = db.get_active_alerts()
    uptime_seconds = (datetime.now() - start_time).total_seconds()
    
    return jsonify({
        'ok': True,
        'system': {
            'uptime_seconds': uptime_seconds,
            'start_time': start_time.isoformat(),
            'current_time': datetime.now().isoformat()
        },
        'health': system_status,
        'widgets': widget_data,
        'alerts': {
            'total': len(alerts),
            'critical': len([a for a in alerts if a['level'] == 'critical']),
            'warning': len([a for a in alerts if a['level'] == 'warning']),
            'info': len([a for a in alerts if a['level'] == 'info'])
        }
    })


@app.route('/api/actions/refresh-all', methods=['POST'])
def api_refresh_all():
    """Refresh all service health checks."""
    status = discovery.get_system_status()
    
    return jsonify({
        'ok': True,
        'message': 'All services refreshed',
        'status': status
    })


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(STATIC_DIR, filename)


if __name__ == '__main__':
    port = int(os.environ.get('COMMAND_CENTER_PORT', 5000))
    
    logger.info(f"🚀 SONIC COMMAND CENTER starting on port {port}")
    logger.info(f"📊 Dashboard URL: http://localhost:{port}")
    logger.info(f"💎 Integrating {len(discovery.get_all_services())} services")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
