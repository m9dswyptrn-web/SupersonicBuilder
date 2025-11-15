#!/usr/bin/env python3
"""
Android App Manager Service
Manages apps on 256GB storage with performance optimization
Port: 9400
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.apps.database import AppDatabase
from services.apps.manager import AppManager
from services.apps.storage import StorageAnalyzer

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

db = AppDatabase()
manager = AppManager()
storage = StorageAnalyzer(total_storage_gb=256)

PERFORMANCE_DASHBOARD_URL = 'http://localhost:8700'


def init_app_data():
    """Initialize database with mock app data."""
    apps = manager.get_all_apps(include_system=True)
    
    for app_data in apps:
        db.upsert_app(app_data)
        
        permissions = manager.get_app_permissions(app_data['package_name'])
        if permissions:
            db.upsert_permissions(app_data['package_name'], permissions)
        
        perf = manager.get_app_performance(app_data['package_name'])
        if perf:
            db.record_performance(app_data['package_name'], perf)
    
    storage_overview = storage.get_storage_overview(apps)
    db.record_storage_snapshot(storage_overview)
    
    print(f"✓ Initialized database with {len(apps)} apps")


init_app_data()


@app.route('/')
def index():
    """Serve the main app manager UI."""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint."""
    port = int(os.environ.get('APPS_PORT', 9400))
    stats = db.get_stats()
    
    return jsonify({
        'ok': True,
        'service': 'android_app_manager',
        'port': port,
        'status': 'healthy',
        'version': '1.0.0',
        'stats': stats
    })


@app.route('/api/apps')
def api_get_apps():
    """Get all installed apps."""
    try:
        include_system = request.args.get('include_system', 'false').lower() == 'true'
        category = request.args.get('category')
        search = request.args.get('search', '').lower()
        
        if category:
            apps = db.get_apps_by_category(category)
        else:
            apps = db.get_all_apps(include_system=include_system)
        
        if search:
            apps = [
                app for app in apps
                if search in app['app_name'].lower() or search in app['package_name'].lower()
            ]
        
        return jsonify({
            'ok': True,
            'apps': apps,
            'count': len(apps)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/<package_name>')
def api_get_app_details(package_name):
    """Get detailed information about an app."""
    try:
        app = db.get_app_by_package(package_name)
        if not app:
            return jsonify({'ok': False, 'error': 'App not found'}), 404
        
        permissions = db.get_app_permissions(package_name)
        performance_history = db.get_app_performance(package_name, limit=20)
        
        privacy_concerns = [p for p in permissions if p['privacy_concern_level'] in ['high', 'medium']]
        
        return jsonify({
            'ok': True,
            'app': app,
            'permissions': permissions,
            'performance_history': performance_history,
            'privacy_concerns': privacy_concerns
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/<package_name>/launch', methods=['POST'])
def api_launch_app(package_name):
    """Launch an app."""
    try:
        result = manager.launch_app(package_name)
        
        if result['success']:
            db.record_action(package_name, 'launch', result['intent'])
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/<package_name>/uninstall', methods=['POST'])
def api_uninstall_app(package_name):
    """Uninstall an app."""
    try:
        result = manager.uninstall_app(package_name)
        
        if result['success']:
            db.record_action(
                package_name, 'uninstall',
                result['message'],
                space_freed_mb=result['space_freed_mb']
            )
            db.delete_app(package_name)
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/<package_name>/clear-cache', methods=['POST'])
def api_clear_cache(package_name):
    """Clear app cache."""
    try:
        result = manager.clear_app_cache(package_name)
        
        if result['success']:
            db.record_action(
                package_name, 'clear_cache',
                result['message'],
                space_freed_mb=result['space_freed_mb']
            )
            
            app = manager.get_app_by_package(package_name)
            if app:
                db.upsert_app(app)
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/<package_name>/clear-data', methods=['POST'])
def api_clear_data(package_name):
    """Clear app data."""
    try:
        result = manager.clear_app_data(package_name)
        
        if result['success']:
            db.record_action(
                package_name, 'clear_data',
                result['message'],
                space_freed_mb=result['space_freed_mb']
            )
            
            app = manager.get_app_by_package(package_name)
            if app:
                db.upsert_app(app)
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/<package_name>/force-stop', methods=['POST'])
def api_force_stop(package_name):
    """Force stop an app."""
    try:
        result = manager.force_stop_app(package_name)
        
        if result['success']:
            db.record_action(package_name, 'force_stop', result['message'])
            
            try:
                requests.post(
                    f'{PERFORMANCE_DASHBOARD_URL}/api/optimize/process/kill',
                    json={'process_name': package_name},
                    timeout=2
                )
            except:
                pass
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/<package_name>/category', methods=['PUT'])
def api_update_category(package_name):
    """Update app category."""
    try:
        data = request.json or {}
        category = data.get('category')
        is_custom = data.get('is_custom', False)
        
        if not category:
            return jsonify({'ok': False, 'error': 'category is required'}), 400
        
        db.update_app_category(package_name, category, is_custom)
        
        return jsonify({
            'ok': True,
            'message': f'Updated category to {category}'
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/batch/clear-cache', methods=['POST'])
def api_batch_clear_cache():
    """Clear cache for all apps."""
    try:
        result = manager.clear_all_caches()
        
        db.record_action(
            'system', 'batch_clear_cache',
            result['message'],
            space_freed_mb=result['space_freed_mb']
        )
        
        apps = manager.get_all_apps(include_system=True)
        for app in apps:
            db.upsert_app(app)
        
        return jsonify({
            'ok': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/apps/batch/uninstall', methods=['POST'])
def api_batch_uninstall():
    """Uninstall multiple apps."""
    try:
        data = request.json or {}
        package_names = data.get('package_names', [])
        
        if not package_names:
            return jsonify({'ok': False, 'error': 'package_names required'}), 400
        
        results = []
        total_freed = 0
        
        for package_name in package_names:
            result = manager.uninstall_app(package_name)
            results.append({
                'package_name': package_name,
                'success': result['success'],
                'message': result['message']
            })
            
            if result['success']:
                total_freed += result['space_freed_mb']
                db.delete_app(package_name)
        
        db.record_action(
            'system', 'batch_uninstall',
            f'Uninstalled {len([r for r in results if r["success"]])} apps',
            space_freed_mb=total_freed
        )
        
        return jsonify({
            'ok': True,
            'results': results,
            'total_freed_mb': round(total_freed, 2)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage/overview')
def api_storage_overview():
    """Get storage overview."""
    try:
        apps = db.get_all_apps(include_system=True)
        overview = storage.get_storage_overview(apps)
        
        db.record_storage_snapshot(overview)
        
        return jsonify({
            'ok': True,
            'storage': overview
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage/breakdown')
def api_storage_breakdown():
    """Get storage breakdown by category."""
    try:
        apps = db.get_all_apps(include_system=True)
        breakdown = storage.get_storage_breakdown(apps)
        
        return jsonify({
            'ok': True,
            'breakdown': breakdown
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage/top-apps')
def api_top_storage_apps():
    """Get top apps by storage usage."""
    try:
        limit = int(request.args.get('limit', 10))
        apps = db.get_all_apps(include_system=False)
        top_apps = storage.get_top_storage_hogs(apps, limit)
        
        return jsonify({
            'ok': True,
            'top_apps': top_apps
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage/cache-analysis')
def api_cache_analysis():
    """Get cache analysis."""
    try:
        apps = db.get_all_apps(include_system=True)
        analysis = storage.get_cache_analysis(apps)
        
        return jsonify({
            'ok': True,
            'cache_analysis': analysis
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage/recommendations')
def api_storage_recommendations():
    """Get storage optimization recommendations."""
    try:
        apps = db.get_all_apps(include_system=True)
        recommendations = storage.get_storage_recommendations(apps)
        
        return jsonify({
            'ok': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/storage/predict-full')
def api_predict_storage_full():
    """Predict when storage will be full."""
    try:
        apps = db.get_all_apps(include_system=True)
        prediction = storage.predict_storage_full(apps)
        
        return jsonify({
            'ok': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/categories')
def api_get_categories():
    """Get all app categories."""
    try:
        categories = list(manager.CATEGORIES.keys()) + ['other', 'system']
        
        apps = db.get_all_apps(include_system=True)
        category_counts = {}
        
        for category in categories:
            count = len([app for app in apps if app.get('category') == category])
            if count > 0:
                category_counts[category] = count
        
        return jsonify({
            'ok': True,
            'categories': categories,
            'counts': category_counts
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recommendations/car-apps')
def api_car_app_recommendations():
    """Get car app recommendations."""
    try:
        recommendations = manager.get_recommendations()
        
        return jsonify({
            'ok': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recommendations/removal')
def api_removal_recommendations():
    """Get app removal recommendations."""
    try:
        recommendations = manager.get_removal_recommendations()
        
        return jsonify({
            'ok': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/recommendations/cache-cleanup')
def api_cache_cleanup_recommendations():
    """Get cache cleanup recommendations."""
    try:
        recommendations = manager.get_cache_cleanup_recommendations()
        
        return jsonify({
            'ok': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/performance/integrate', methods=['POST'])
def api_integrate_performance():
    """Integrate with performance dashboard to free RAM."""
    try:
        data = request.json or {}
        apps_to_kill = data.get('apps', [])
        
        if not apps_to_kill:
            return jsonify({'ok': False, 'error': 'apps list required'}), 400
        
        results = []
        for package_name in apps_to_kill:
            result = manager.force_stop_app(package_name)
            results.append(result)
            
            if result['success']:
                db.record_action(package_name, 'force_stop_for_ram', 'Stopped to free RAM')
                
                try:
                    requests.post(
                        f'{PERFORMANCE_DASHBOARD_URL}/api/optimize/process/kill',
                        json={'process_name': package_name},
                        timeout=2
                    )
                except:
                    pass
        
        return jsonify({
            'ok': True,
            'results': results,
            'apps_stopped': len([r for r in results if r['success']])
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history/actions')
def api_action_history():
    """Get app action history."""
    try:
        limit = int(request.args.get('limit', 100))
        history = db.get_action_history(limit)
        
        return jsonify({
            'ok': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history/storage')
def api_storage_history():
    """Get storage history."""
    try:
        hours = int(request.args.get('hours', 24))
        history = db.get_storage_history(hours)
        
        return jsonify({
            'ok': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/stats')
def api_stats():
    """Get database statistics."""
    try:
        stats = db.get_stats()
        
        return jsonify({
            'ok': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('APPS_PORT', 9400))
    print(f"""
╔══════════════════════════════════════╗
║  Android App Manager Service         ║
║  Port: {port}                           ║
║  Storage: 256 GB                     ║
║  Status: Running                     ║
╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
