#!/usr/bin/env python3
"""
Database Interface for Theme Designer Service
Handles theme storage, wallpapers, and icon packs
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

DB_PATH = ROOT / 'supersonic' / 'data' / 'supersonic.db'


class ThemeDatabase:
    """Database interface for theme designer."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        self.db_path = db_path or DB_PATH
        self._ensure_db()
    
    def _ensure_db(self):
        """Ensure database and tables exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ui_themes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_name TEXT UNIQUE NOT NULL,
                    theme_type TEXT DEFAULT 'custom',
                    mode TEXT DEFAULT 'dark',
                    primary_color TEXT NOT NULL,
                    secondary_color TEXT NOT NULL,
                    accent_color TEXT NOT NULL,
                    background_color TEXT,
                    surface_color TEXT,
                    text_color TEXT,
                    nav_bar_color TEXT,
                    status_bar_color TEXT,
                    button_style TEXT DEFAULT 'rounded',
                    icon_style TEXT DEFAULT 'modern',
                    font_family TEXT DEFAULT 'Roboto',
                    animation_speed TEXT DEFAULT 'normal',
                    transition_effect TEXT DEFAULT 'fade',
                    wallpaper_id INTEGER,
                    widget_config TEXT,
                    icon_pack_id INTEGER,
                    is_template BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (wallpaper_id) REFERENCES wallpapers(id),
                    FOREIGN KEY (icon_pack_id) REFERENCES icon_packs(id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS wallpapers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wallpaper_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    thumbnail_path TEXT,
                    original_width INTEGER,
                    original_height INTEGER,
                    resized_width INTEGER DEFAULT 2000,
                    resized_height INTEGER DEFAULT 1200,
                    file_size_kb INTEGER,
                    time_based BOOLEAN DEFAULT 0,
                    day_wallpaper_id INTEGER,
                    night_wallpaper_id INTEGER,
                    slideshow_enabled BOOLEAN DEFAULT 0,
                    slideshow_interval INTEGER DEFAULT 300,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (day_wallpaper_id) REFERENCES wallpapers(id),
                    FOREIGN KEY (night_wallpaper_id) REFERENCES wallpapers(id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS icon_packs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pack_name TEXT UNIQUE NOT NULL,
                    pack_style TEXT NOT NULL,
                    icon_count INTEGER DEFAULT 0,
                    icon_data TEXT,
                    preview_path TEXT,
                    is_custom BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS widget_themes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    widget_type TEXT NOT NULL,
                    widget_name TEXT NOT NULL,
                    style_config TEXT NOT NULL,
                    preview_image TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS theme_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (theme_id) REFERENCES ui_themes(id)
                )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_themes_name ON ui_themes(theme_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_themes_mode ON ui_themes(mode)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_themes_active ON ui_themes(is_active)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_wallpapers_name ON wallpapers(wallpaper_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_icon_packs_name ON icon_packs(pack_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_theme_history_theme ON theme_history(theme_id)')
            
            conn.commit()
            
            self._ensure_default_data()
    
    def _ensure_default_data(self):
        """Create default themes, icon packs, and widgets."""
        default_themes = [
            {
                'theme_name': 'Modern Dark',
                'theme_type': 'template',
                'mode': 'dark',
                'primary_color': '#1a1a1a',
                'secondary_color': '#2d2d2d',
                'accent_color': '#00b8d4',
                'background_color': '#121212',
                'surface_color': '#1e1e1e',
                'text_color': '#ffffff',
                'nav_bar_color': '#1a1a1a',
                'status_bar_color': '#000000',
                'button_style': 'rounded',
                'icon_style': 'modern',
                'font_family': 'Roboto',
                'is_template': 1
            },
            {
                'theme_name': 'Light Minimal',
                'theme_type': 'template',
                'mode': 'light',
                'primary_color': '#ffffff',
                'secondary_color': '#f5f5f5',
                'accent_color': '#2196f3',
                'background_color': '#fafafa',
                'surface_color': '#ffffff',
                'text_color': '#212121',
                'nav_bar_color': '#ffffff',
                'status_bar_color': '#f5f5f5',
                'button_style': 'rounded',
                'icon_style': 'minimal',
                'font_family': 'Roboto',
                'is_template': 1
            },
            {
                'theme_name': 'Sonic Blue',
                'theme_type': 'template',
                'mode': 'dark',
                'primary_color': '#0d47a1',
                'secondary_color': '#1565c0',
                'accent_color': '#64b5f6',
                'background_color': '#0a1929',
                'surface_color': '#1a2332',
                'text_color': '#e3f2fd',
                'nav_bar_color': '#0d47a1',
                'status_bar_color': '#0a1929',
                'button_style': 'rounded',
                'icon_style': 'modern',
                'font_family': 'Roboto Medium',
                'is_template': 1
            },
            {
                'theme_name': 'Neon',
                'theme_type': 'template',
                'mode': 'dark',
                'primary_color': '#000000',
                'secondary_color': '#1a1a1a',
                'accent_color': '#00ff41',
                'background_color': '#0a0a0a',
                'surface_color': '#141414',
                'text_color': '#00ff41',
                'nav_bar_color': '#000000',
                'status_bar_color': '#000000',
                'button_style': 'sharp',
                'icon_style': 'neon',
                'font_family': 'Roboto Mono',
                'is_template': 1
            },
            {
                'theme_name': 'Classic',
                'theme_type': 'template',
                'mode': 'light',
                'primary_color': '#607d8b',
                'secondary_color': '#78909c',
                'accent_color': '#ff9800',
                'background_color': '#eceff1',
                'surface_color': '#ffffff',
                'text_color': '#263238',
                'nav_bar_color': '#546e7a',
                'status_bar_color': '#455a64',
                'button_style': 'rounded',
                'icon_style': 'classic',
                'font_family': 'Roboto',
                'is_template': 1
            }
        ]
        
        for theme in default_themes:
            try:
                self.create_theme(**theme)
            except sqlite3.IntegrityError:
                pass
        
        default_icon_packs = [
            {
                'pack_name': 'Modern Circular',
                'pack_style': 'circular',
                'icon_count': 150,
                'icon_data': json.dumps({'style': 'circular', 'size': '48dp', 'padding': '8dp'}),
                'is_custom': 0
            },
            {
                'pack_name': 'Square Outline',
                'pack_style': 'square-outline',
                'icon_count': 150,
                'icon_data': json.dumps({'style': 'square-outline', 'size': '48dp', 'stroke': '2dp'}),
                'is_custom': 0
            },
            {
                'pack_name': 'Rounded Square',
                'pack_style': 'rounded-square',
                'icon_count': 150,
                'icon_data': json.dumps({'style': 'rounded-square', 'size': '48dp', 'radius': '12dp'}),
                'is_custom': 0
            }
        ]
        
        for pack in default_icon_packs:
            try:
                self.create_icon_pack(**pack)
            except sqlite3.IntegrityError:
                pass
        
        default_widgets = [
            {
                'widget_type': 'clock',
                'widget_name': 'Digital Bold',
                'style_config': json.dumps({
                    'font_size': '48sp',
                    'font_weight': 'bold',
                    'show_seconds': True,
                    'format_24h': True
                })
            },
            {
                'widget_type': 'weather',
                'widget_name': 'Compact',
                'style_config': json.dumps({
                    'show_temp': True,
                    'show_icon': True,
                    'show_condition': True,
                    'size': 'compact'
                })
            },
            {
                'widget_type': 'music',
                'widget_name': 'Full Player',
                'style_config': json.dumps({
                    'show_album_art': True,
                    'show_controls': True,
                    'show_progress': True,
                    'layout': 'full'
                })
            }
        ]
        
        for widget in default_widgets:
            try:
                self.create_widget_theme(**widget)
            except sqlite3.IntegrityError:
                pass
    
    def create_theme(self, **kwargs) -> int:
        """Create a new theme."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            widget_config = kwargs.get('widget_config')
            if isinstance(widget_config, dict):
                widget_config = json.dumps(widget_config)
            
            cursor.execute('''
                INSERT INTO ui_themes (
                    theme_name, theme_type, mode, primary_color, secondary_color,
                    accent_color, background_color, surface_color, text_color,
                    nav_bar_color, status_bar_color, button_style, icon_style,
                    font_family, animation_speed, transition_effect, wallpaper_id,
                    widget_config, icon_pack_id, is_template, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                kwargs.get('theme_name'),
                kwargs.get('theme_type', 'custom'),
                kwargs.get('mode', 'dark'),
                kwargs.get('primary_color'),
                kwargs.get('secondary_color'),
                kwargs.get('accent_color'),
                kwargs.get('background_color'),
                kwargs.get('surface_color'),
                kwargs.get('text_color'),
                kwargs.get('nav_bar_color'),
                kwargs.get('status_bar_color'),
                kwargs.get('button_style', 'rounded'),
                kwargs.get('icon_style', 'modern'),
                kwargs.get('font_family', 'Roboto'),
                kwargs.get('animation_speed', 'normal'),
                kwargs.get('transition_effect', 'fade'),
                kwargs.get('wallpaper_id'),
                widget_config,
                kwargs.get('icon_pack_id'),
                kwargs.get('is_template', 0),
                kwargs.get('is_active', 0)
            ))
            
            return cursor.lastrowid
    
    def get_theme(self, theme_id: int) -> Optional[Dict[str, Any]]:
        """Get theme by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ui_themes WHERE id = ?', (theme_id,))
            row = cursor.fetchone()
            
            if row:
                theme = dict(row)
                if theme.get('widget_config'):
                    try:
                        theme['widget_config'] = json.loads(theme['widget_config'])
                    except:
                        pass
                return theme
            return None
    
    def get_all_themes(self) -> List[Dict[str, Any]]:
        """Get all themes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ui_themes ORDER BY is_template DESC, created_at DESC')
            rows = cursor.fetchall()
            
            themes = []
            for row in rows:
                theme = dict(row)
                if theme.get('widget_config'):
                    try:
                        theme['widget_config'] = json.loads(theme['widget_config'])
                    except:
                        pass
                themes.append(theme)
            
            return themes
    
    def update_theme(self, theme_id: int, **kwargs) -> bool:
        """Update theme."""
        with sqlite3.connect(self.db_path) as conn:
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['theme_name', 'mode', 'primary_color', 'secondary_color',
                          'accent_color', 'background_color', 'surface_color', 'text_color',
                          'nav_bar_color', 'status_bar_color', 'button_style', 'icon_style',
                          'font_family', 'animation_speed', 'transition_effect', 'wallpaper_id',
                          'widget_config', 'icon_pack_id', 'is_active']:
                    if key == 'widget_config' and isinstance(value, dict):
                        value = json.dumps(value)
                    updates.append(f'{key} = ?')
                    values.append(value)
            
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(theme_id)
                conn.execute(f'UPDATE ui_themes SET {", ".join(updates)} WHERE id = ?', values)
                return True
            
            return False
    
    def delete_theme(self, theme_id: int) -> bool:
        """Delete theme."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM ui_themes WHERE id = ? AND is_template = 0', (theme_id,))
            return cursor.rowcount > 0
    
    def set_active_theme(self, theme_id: int) -> bool:
        """Set active theme."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('UPDATE ui_themes SET is_active = 0')
            conn.execute('UPDATE ui_themes SET is_active = 1 WHERE id = ?', (theme_id,))
            conn.execute('INSERT INTO theme_history (theme_id, action) VALUES (?, ?)',
                        (theme_id, 'applied'))
            return True
    
    def create_wallpaper(self, **kwargs) -> int:
        """Create wallpaper record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO wallpapers (
                    wallpaper_name, file_path, thumbnail_path, original_width,
                    original_height, resized_width, resized_height, file_size_kb,
                    time_based, day_wallpaper_id, night_wallpaper_id,
                    slideshow_enabled, slideshow_interval
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                kwargs.get('wallpaper_name'),
                kwargs.get('file_path'),
                kwargs.get('thumbnail_path'),
                kwargs.get('original_width'),
                kwargs.get('original_height'),
                kwargs.get('resized_width', 2000),
                kwargs.get('resized_height', 1200),
                kwargs.get('file_size_kb'),
                kwargs.get('time_based', 0),
                kwargs.get('day_wallpaper_id'),
                kwargs.get('night_wallpaper_id'),
                kwargs.get('slideshow_enabled', 0),
                kwargs.get('slideshow_interval', 300)
            ))
            
            return cursor.lastrowid
    
    def get_all_wallpapers(self) -> List[Dict[str, Any]]:
        """Get all wallpapers."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM wallpapers ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def create_icon_pack(self, **kwargs) -> int:
        """Create icon pack."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            icon_data = kwargs.get('icon_data')
            if isinstance(icon_data, dict):
                icon_data = json.dumps(icon_data)
            
            cursor.execute('''
                INSERT INTO icon_packs (
                    pack_name, pack_style, icon_count, icon_data,
                    preview_path, is_custom
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                kwargs.get('pack_name'),
                kwargs.get('pack_style'),
                kwargs.get('icon_count', 0),
                icon_data,
                kwargs.get('preview_path'),
                kwargs.get('is_custom', 0)
            ))
            
            return cursor.lastrowid
    
    def get_all_icon_packs(self) -> List[Dict[str, Any]]:
        """Get all icon packs."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM icon_packs ORDER BY is_custom, pack_name')
            
            packs = []
            for row in cursor.fetchall():
                pack = dict(row)
                if pack.get('icon_data'):
                    try:
                        pack['icon_data'] = json.loads(pack['icon_data'])
                    except:
                        pass
                packs.append(pack)
            
            return packs
    
    def create_widget_theme(self, **kwargs) -> int:
        """Create widget theme."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            style_config = kwargs.get('style_config')
            if isinstance(style_config, dict):
                style_config = json.dumps(style_config)
            
            cursor.execute('''
                INSERT INTO widget_themes (
                    widget_type, widget_name, style_config, preview_image
                ) VALUES (?, ?, ?, ?)
            ''', (
                kwargs.get('widget_type'),
                kwargs.get('widget_name'),
                style_config,
                kwargs.get('preview_image')
            ))
            
            return cursor.lastrowid
    
    def get_widget_themes(self, widget_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get widget themes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if widget_type:
                cursor.execute('SELECT * FROM widget_themes WHERE widget_type = ?', (widget_type,))
            else:
                cursor.execute('SELECT * FROM widget_themes')
            
            widgets = []
            for row in cursor.fetchall():
                widget = dict(row)
                if widget.get('style_config'):
                    try:
                        widget['style_config'] = json.loads(widget['style_config'])
                    except:
                        pass
                widgets.append(widget)
            
            return widgets
    
    def get_theme_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get theme application history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT h.*, t.theme_name 
                FROM theme_history h
                JOIN ui_themes t ON h.theme_id = t.id
                ORDER BY h.applied_at DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
