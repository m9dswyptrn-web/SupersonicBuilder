#!/usr/bin/env python3
"""
Custom UI Theme Designer Service
Android Auto theme customization and dynamic wallpapers
Port: 8600
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
import logging

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from services.themes.database import ThemeDatabase
from services.themes.designer import ThemeDesigner
from services.themes.wallpaper import WallpaperManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
CORS(app)

UPLOAD_DIR = Path(__file__).parent / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

db = ThemeDatabase()
designer = ThemeDesigner()
wallpaper_mgr = WallpaperManager(UPLOAD_DIR)


@app.route('/')
def index():
    """Serve the theme designer UI."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'ok': True,
        'service': 'Custom UI Theme Designer',
        'port': 8600,
        'features': [
            'Theme customization',
            'Dynamic wallpapers',
            'Icon packs',
            'Widget themes',
            'Android Auto integration',
            'Export/Import themes'
        ],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/themes', methods=['GET'])
def api_get_themes():
    """Get all themes."""
    try:
        themes = db.get_all_themes()
        
        return jsonify({
            'ok': True,
            'count': len(themes),
            'themes': themes
        })
    except Exception as e:
        logger.error(f"Error getting themes: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<int:theme_id>', methods=['GET'])
def api_get_theme(theme_id):
    """Get specific theme."""
    try:
        theme = db.get_theme(theme_id)
        
        if not theme:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
        
        return jsonify({
            'ok': True,
            'theme': theme
        })
    except Exception as e:
        logger.error(f"Error getting theme: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes', methods=['POST'])
def api_create_theme():
    """Create new theme."""
    try:
        data = request.json
        
        valid, error = designer.validate_theme_data(data)
        if not valid:
            return jsonify({'ok': False, 'error': error}), 400
        
        theme_id = db.create_theme(**data)
        theme = db.get_theme(theme_id)
        
        return jsonify({
            'ok': True,
            'message': 'Theme created successfully',
            'theme_id': theme_id,
            'theme': theme
        })
    except Exception as e:
        logger.error(f"Error creating theme: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<int:theme_id>', methods=['PUT'])
def api_update_theme(theme_id):
    """Update theme."""
    try:
        data = request.json
        
        theme = db.get_theme(theme_id)
        if not theme:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
        
        if theme.get('is_template'):
            return jsonify({'ok': False, 'error': 'Cannot modify template themes'}), 400
        
        valid, error = designer.validate_theme_data({**theme, **data})
        if not valid:
            return jsonify({'ok': False, 'error': error}), 400
        
        db.update_theme(theme_id, **data)
        updated_theme = db.get_theme(theme_id)
        
        return jsonify({
            'ok': True,
            'message': 'Theme updated successfully',
            'theme': updated_theme
        })
    except Exception as e:
        logger.error(f"Error updating theme: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<int:theme_id>', methods=['DELETE'])
def api_delete_theme(theme_id):
    """Delete theme."""
    try:
        theme = db.get_theme(theme_id)
        if not theme:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
        
        if theme.get('is_template'):
            return jsonify({'ok': False, 'error': 'Cannot delete template themes'}), 400
        
        success = db.delete_theme(theme_id)
        
        if success:
            return jsonify({
                'ok': True,
                'message': 'Theme deleted successfully'
            })
        else:
            return jsonify({'ok': False, 'error': 'Failed to delete theme'}), 500
    except Exception as e:
        logger.error(f"Error deleting theme: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<int:theme_id>/apply', methods=['POST'])
def api_apply_theme(theme_id):
    """Apply theme as active."""
    try:
        theme = db.get_theme(theme_id)
        if not theme:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
        
        db.set_active_theme(theme_id)
        
        android_config = designer.get_android_auto_config(theme)
        
        return jsonify({
            'ok': True,
            'message': 'Theme applied successfully',
            'theme': theme,
            'android_auto_config': android_config
        })
    except Exception as e:
        logger.error(f"Error applying theme: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/from-template', methods=['POST'])
def api_create_from_template():
    """Create custom theme from template."""
    try:
        data = request.json
        template_name = data.get('template_name')
        custom_name = data.get('custom_name')
        
        if not template_name or not custom_name:
            return jsonify({'ok': False, 'error': 'Missing template_name or custom_name'}), 400
        
        theme_data = designer.create_theme_from_template(template_name, custom_name)
        
        overrides = data.get('overrides', {})
        theme_data.update(overrides)
        
        theme_id = db.create_theme(**theme_data)
        theme = db.get_theme(theme_id)
        
        return jsonify({
            'ok': True,
            'message': 'Theme created from template',
            'theme_id': theme_id,
            'theme': theme
        })
    except Exception as e:
        logger.error(f"Error creating theme from template: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<int:theme_id>/sonic-colors', methods=['POST'])
def api_apply_sonic_colors(theme_id):
    """Apply Sonic interior colors to theme."""
    try:
        data = request.json
        color_scheme = data.get('color_scheme', 'blue')
        
        theme = db.get_theme(theme_id)
        if not theme:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
        
        if theme.get('is_template'):
            return jsonify({'ok': False, 'error': 'Cannot modify template themes'}), 400
        
        updated_data = designer.apply_sonic_colors(dict(theme), color_scheme)
        
        db.update_theme(theme_id, **updated_data)
        updated_theme = db.get_theme(theme_id)
        
        return jsonify({
            'ok': True,
            'message': f'Sonic {color_scheme} colors applied',
            'theme': updated_theme
        })
    except Exception as e:
        logger.error(f"Error applying Sonic colors: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<int:theme_id>/export', methods=['GET'])
def api_export_theme(theme_id):
    """Export theme as JSON."""
    try:
        theme = db.get_theme(theme_id)
        if not theme:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
        
        json_data = designer.export_theme(theme)
        
        return jsonify({
            'ok': True,
            'theme_name': theme['theme_name'],
            'exported_data': json_data
        })
    except Exception as e:
        logger.error(f"Error exporting theme: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/import', methods=['POST'])
def api_import_theme():
    """Import theme from JSON."""
    try:
        data = request.json
        json_data = data.get('theme_data')
        
        if not json_data:
            return jsonify({'ok': False, 'error': 'Missing theme_data'}), 400
        
        if isinstance(json_data, dict):
            json_data = json.dumps(json_data)
        
        theme_data = designer.import_theme(json_data)
        
        theme_id = db.create_theme(**theme_data)
        theme = db.get_theme(theme_id)
        
        return jsonify({
            'ok': True,
            'message': 'Theme imported successfully',
            'theme_id': theme_id,
            'theme': theme
        })
    except Exception as e:
        logger.error(f"Error importing theme: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/<int:theme_id>/preview-css', methods=['GET'])
def api_get_preview_css(theme_id):
    """Get preview CSS for theme."""
    try:
        theme = db.get_theme(theme_id)
        if not theme:
            return jsonify({'ok': False, 'error': 'Theme not found'}), 404
        
        css = designer.generate_preview_css(theme)
        
        return jsonify({
            'ok': True,
            'css': css
        })
    except Exception as e:
        logger.error(f"Error generating preview CSS: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/wallpapers', methods=['GET'])
def api_get_wallpapers():
    """Get all wallpapers."""
    try:
        wallpapers = db.get_all_wallpapers()
        
        return jsonify({
            'ok': True,
            'count': len(wallpapers),
            'wallpapers': wallpapers
        })
    except Exception as e:
        logger.error(f"Error getting wallpapers: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/wallpapers/upload', methods=['POST'])
def api_upload_wallpaper():
    """Upload and process wallpaper."""
    try:
        if 'file' not in request.files:
            return jsonify({'ok': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'ok': False, 'error': 'No file selected'}), 400
        
        wallpaper_name = request.form.get('name', file.filename)
        
        file_data = file.read()
        
        result = wallpaper_mgr.save_and_resize_wallpaper(file_data, file.filename)
        
        wallpaper_id = db.create_wallpaper(
            wallpaper_name=wallpaper_name,
            **result
        )
        
        return jsonify({
            'ok': True,
            'message': 'Wallpaper uploaded successfully',
            'wallpaper_id': wallpaper_id,
            'wallpaper': {
                'id': wallpaper_id,
                'wallpaper_name': wallpaper_name,
                **result
            }
        })
    except Exception as e:
        logger.error(f"Error uploading wallpaper: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/wallpapers/<int:wallpaper_id>/slideshow', methods=['POST'])
def api_create_slideshow(wallpaper_id):
    """Create slideshow configuration."""
    try:
        data = request.json
        wallpaper_ids = data.get('wallpaper_ids', [wallpaper_id])
        interval = data.get('interval', 300)
        
        config = wallpaper_mgr.create_slideshow_config(wallpaper_ids, interval)
        
        return jsonify({
            'ok': True,
            'message': 'Slideshow configured',
            'config': config
        })
    except Exception as e:
        logger.error(f"Error creating slideshow: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/wallpapers/time-based', methods=['POST'])
def api_create_time_based():
    """Create time-based wallpaper configuration."""
    try:
        data = request.json
        day_wallpaper_id = data.get('day_wallpaper_id')
        night_wallpaper_id = data.get('night_wallpaper_id')
        day_start = data.get('day_start', '06:00')
        night_start = data.get('night_start', '18:00')
        
        if not day_wallpaper_id or not night_wallpaper_id:
            return jsonify({'ok': False, 'error': 'Missing wallpaper IDs'}), 400
        
        config = wallpaper_mgr.create_time_based_config(
            day_wallpaper_id, night_wallpaper_id,
            day_start, night_start
        )
        
        current_id = wallpaper_mgr.get_current_wallpaper(config)
        
        return jsonify({
            'ok': True,
            'message': 'Time-based wallpaper configured',
            'config': config,
            'current_wallpaper_id': current_id
        })
    except Exception as e:
        logger.error(f"Error creating time-based wallpaper: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/icon-packs', methods=['GET'])
def api_get_icon_packs():
    """Get all icon packs."""
    try:
        packs = db.get_all_icon_packs()
        
        return jsonify({
            'ok': True,
            'count': len(packs),
            'icon_packs': packs
        })
    except Exception as e:
        logger.error(f"Error getting icon packs: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/icon-packs', methods=['POST'])
def api_create_icon_pack():
    """Create custom icon pack."""
    try:
        data = request.json
        
        pack_id = db.create_icon_pack(**data)
        
        return jsonify({
            'ok': True,
            'message': 'Icon pack created',
            'pack_id': pack_id
        })
    except Exception as e:
        logger.error(f"Error creating icon pack: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/widgets', methods=['GET'])
def api_get_widgets():
    """Get widget themes."""
    try:
        widget_type = request.args.get('type')
        widgets = db.get_widget_themes(widget_type)
        
        return jsonify({
            'ok': True,
            'count': len(widgets),
            'widgets': widgets
        })
    except Exception as e:
        logger.error(f"Error getting widgets: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/widgets', methods=['POST'])
def api_create_widget():
    """Create custom widget theme."""
    try:
        data = request.json
        
        widget_id = db.create_widget_theme(**data)
        
        return jsonify({
            'ok': True,
            'message': 'Widget theme created',
            'widget_id': widget_id
        })
    except Exception as e:
        logger.error(f"Error creating widget: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/options', methods=['GET'])
def api_get_options():
    """Get all available customization options."""
    try:
        options = designer.get_available_options()
        
        return jsonify({
            'ok': True,
            'options': options
        })
    except Exception as e:
        logger.error(f"Error getting options: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/themes/compare', methods=['POST'])
def api_compare_themes():
    """Compare two themes."""
    try:
        data = request.json
        theme1_id = data.get('theme1_id')
        theme2_id = data.get('theme2_id')
        
        if not theme1_id or not theme2_id:
            return jsonify({'ok': False, 'error': 'Missing theme IDs'}), 400
        
        theme1 = db.get_theme(theme1_id)
        theme2 = db.get_theme(theme2_id)
        
        if not theme1 or not theme2:
            return jsonify({'ok': False, 'error': 'One or both themes not found'}), 404
        
        differences = designer.compare_themes(theme1, theme2)
        
        return jsonify({
            'ok': True,
            'theme1': theme1,
            'theme2': theme2,
            'differences': differences
        })
    except Exception as e:
        logger.error(f"Error comparing themes: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def api_get_history():
    """Get theme application history."""
    try:
        limit = int(request.args.get('limit', 10))
        history = db.get_theme_history(limit)
        
        return jsonify({
            'ok': True,
            'count': len(history),
            'history': history
        })
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8600))
    app.run(host='0.0.0.0', port=port, debug=True)
