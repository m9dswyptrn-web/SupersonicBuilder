# Custom UI Theme Designer Service

Android Auto theme customization and dynamic wallpapers for 2000×1200 display.

## Port

**8600**

## Features

### Theme Customization
- ✅ Color scheme editor (primary, secondary, accent colors)
- ✅ Dark mode vs light mode support
- ✅ Sonic interior color presets
- ✅ Unlimited custom themes

### Android Auto Integration
- ✅ Navigation bar customization
- ✅ Status bar customization
- ✅ App icon styles (5 options)
- ✅ Button styles (4 options)
- ✅ Font selection (9 fonts)

### Dynamic Wallpapers
- ✅ Upload custom images (JPEG, PNG, WEBP, BMP)
- ✅ Auto-resize to 2000×1200 display
- ✅ Slideshow mode configuration
- ✅ Time-based wallpapers (day/night)

### Widget Customization
- ✅ Clock widget themes
- ✅ Weather widget styles
- ✅ Music player widget
- ✅ Quick settings appearance

### Icon Packs
- ✅ 3 pre-made icon sets
- ✅ Custom icon upload support
- ✅ Apply to all apps

### UI Animations
- ✅ Transition effects (fade, slide, zoom, flip)
- ✅ Animation speeds (slow, normal, fast, instant)

### Theme Templates
- ✅ Modern Dark
- ✅ Light Minimal
- ✅ Sonic Blue
- ✅ Neon
- ✅ Classic
- ✅ Import/Export themes as JSON

### Preview Mode
- ✅ Live preview before applying
- ✅ Visual comparison

### Web UI
- ✅ Interactive color picker
- ✅ Theme gallery
- ✅ Wallpaper uploader with drag & drop
- ✅ Live preview panel
- ✅ Export/import tools

## Quick Start

```bash
# Start the service
./start.sh

# Or manually
python3 app.py
```

## API Endpoints

### Health Check
```
GET /health
```

### Themes
```
GET    /api/themes              # List all themes
GET    /api/themes/<id>         # Get specific theme
POST   /api/themes              # Create new theme
PUT    /api/themes/<id>         # Update theme
DELETE /api/themes/<id>         # Delete theme
POST   /api/themes/<id>/apply   # Apply theme
GET    /api/themes/<id>/export  # Export theme as JSON
POST   /api/themes/import       # Import theme from JSON
POST   /api/themes/from-template # Create from template
POST   /api/themes/<id>/sonic-colors # Apply Sonic colors
```

### Wallpapers
```
GET  /api/wallpapers                  # List wallpapers
POST /api/wallpapers/upload           # Upload wallpaper
POST /api/wallpapers/<id>/slideshow   # Configure slideshow
POST /api/wallpapers/time-based       # Configure time-based
```

### Other
```
GET  /api/icon-packs   # List icon packs
POST /api/icon-packs   # Create icon pack
GET  /api/widgets      # List widget themes
POST /api/widgets      # Create widget theme
GET  /api/options      # Get customization options
POST /api/themes/compare # Compare two themes
GET  /api/history      # Theme application history
```

## Database Schema

The service uses the shared SuperSonic database (`supersonic/data/supersonic.db`) with the following tables:

- `ui_themes` - Theme configurations
- `wallpapers` - Wallpaper metadata and settings
- `icon_packs` - Icon pack definitions
- `widget_themes` - Widget styling configurations
- `theme_history` - Theme application history

## File Structure

```
services/themes/
├── app.py                 # Main Flask application
├── database.py            # Database interface
├── designer.py            # Theme design logic
├── wallpaper.py           # Wallpaper management
├── start.sh               # Startup script
├── uploads/               # Uploaded files
│   ├── wallpapers/        # Resized wallpapers (2000×1200)
│   └── thumbnails/        # Wallpaper thumbnails (400×240)
├── templates/
│   └── index.html         # Web UI
└── static/
    └── themes.js          # Frontend JavaScript
```

## Testing

The service has been tested with all major endpoints:

✅ Health check endpoint
✅ Theme CRUD operations
✅ Theme export/import
✅ Android Auto configuration generation
✅ Wallpaper management
✅ Icon packs
✅ Widget themes
✅ Customization options
✅ Theme history

## Default Themes

The service comes with 5 pre-built theme templates:

1. **Modern Dark** - Sleek dark theme with cyan accents
2. **Light Minimal** - Clean light theme with blue accents
3. **Sonic Blue** - Matches Chevrolet Sonic interior blue
4. **Neon** - Dark theme with neon green cyberpunk style
5. **Classic** - Traditional gray theme with orange accents

## Sonic Colors

Special color presets matching Chevrolet Sonic interior:

- Sonic Blue: `#0d47a1`
- Dashboard Blue: `#1565c0`
- Interior Accent: `#64b5f6`
- Sonic Gray: `#455a64`
- Sonic Black: `#212121`

## Dependencies

- Flask
- Flask-CORS
- Pillow (image processing)
- SQLite3 (built-in)

All dependencies are already installed.
