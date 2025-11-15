# SONIC COMMAND CENTER 🚀

The unified master dashboard integrating all 30+ services into one stunning interface optimized for the 2000×1200 QLED display.

## Features ✨

### Service Discovery & Monitoring
- **32 Services Discovered**: Automatically detects all SONIC services
- **Real-time Health Monitoring**: Green/yellow/red status indicators
- **4 Categories**: Hardware Tools, Premium Audio, Visual Upgrades, Smart Features
- **Quick Access**: Click to open any service in a new tab

### Live Data Widgets 📊
- **CAN Bus**: Real-time speed, RPM, fuel level, coolant temperature
- **Media Center**: Now playing with track info
- **Climate Control**: Inside/outside temperature, AC status
- **TPMS**: All 4 tire pressures with visual grid
- **Wireless Charger**: Battery percentage with animated bar
- **Security**: Armed status, door locks, active events
- **Maintenance**: Upcoming service reminders
- **Dashcam**: Recording status and storage usage
- **Performance**: CPU, memory, disk usage

### User Interface 🎨
- **Stunning Dark Theme**: Optimized for night driving
- **Light Theme**: Available via theme toggle
- **Gradient Backgrounds**: Beautiful blue/cyan gradients
- **Smooth Animations**: Hover effects, pulse animations
- **Touch-Friendly**: Large buttons, swipe gestures
- **Responsive**: Works on desktop, tablet, mobile
- **2000×1200 Optimized**: Perfect for QLED display

### Quick Actions ⚡
- Refresh All Services
- View System Alerts
- Search Services
- Toggle Theme
- Configure Settings

### Search & Navigation 🔍
- Real-time search across all services
- Instant results with descriptions
- Click to open service

### Settings Panel ⚙️
- Theme selection (Dark/Light)
- Show/hide offline services
- Enable/disable animations
- Auto-refresh interval (3s to 30s)
- Temperature unit (°F/°C)
- Persistent storage

### Database Storage 💾
- User preferences saved to SQLite
- Dashboard layouts
- Favorite services
- System alerts
- Quick actions

## Architecture 🏗️

```
services/command_center/
├── app.py                 # Main Flask application (Port 5000)
├── database.py           # SQLite database for preferences
├── discovery.py          # Service discovery & health checking
├── integrations.py       # Live data from all services
├── templates/
│   └── index.html       # Stunning dashboard UI
└── static/
    ├── dashboard.js     # Interactive JavaScript
    └── dashboard.css    # Beautiful styling & animations
```

## API Endpoints 🔌

### Services
- `GET /api/services/all` - List all services
- `GET /api/services/categories` - Services grouped by category
- `GET /api/services/<id>` - Get service details

### Health Monitoring
- `GET /health` - Command Center health
- `GET /api/health/all` - Check all service health
- `GET /api/health/<id>` - Check specific service

### Live Widgets
- `GET /api/widgets/data` - Get all widget data

### Preferences
- `GET /api/preferences` - Get all preferences
- `POST /api/preferences` - Save preferences

### Layouts
- `GET /api/layouts` - Get all layouts
- `GET /api/layouts/active` - Get active layout
- `POST /api/layouts` - Save layout

### Alerts
- `GET /api/alerts` - Get active alerts
- `POST /api/alerts` - Add alert
- `POST /api/alerts/<id>/acknowledge` - Acknowledge alert

### Search
- `GET /api/search?q=<query>` - Search services

### System
- `GET /api/system/status` - Comprehensive system status
- `POST /api/actions/refresh-all` - Refresh all services

## Running the Command Center 🚀

### Manual Start
```bash
cd services/command_center
python3 app.py
```

### As Workflow
Add to workflows with:
- Name: "SONIC Command Center"
- Command: `python3 services/command_center/app.py`
- Output Type: `webview`
- Port: `5000`

### Access
Open in browser: http://localhost:5000

## Service Categories 📦

### Hardware Tools (12 services)
- CAN Bus Monitor (7000)
- Maestro RR2 (7200)
- Camera System (7300)
- System Health (7400)
- Data Logger (7600)
- Audio Path Designer (7700)
- Remote Diagnostics (7800)
- Wire Harness (7900)
- PCB Designer (7100)
- AI Board Analyzer (7500)
- BOM Generator (5052)
- Quote System (5053)

### Premium Audio (4 services)
- DSP Control (8100)
- Sound Stage (8200)
- Audio Visualizer (8300)
- Bass Management (8400)

### Visual Upgrades (3 services)
- RGB Lighting (8500)
- Theme Designer (8600)
- Performance Dashboard (8700)

### Smart Features (13 services)
- Climate Control (8800)
- Voice Assistant (8900)
- Parking Assistant (9100)
- Analytics Dashboard (9200)
- Security System (9300)
- App Manager (9400)
- Media Center (9500)
- Navigation (9600)
- TPMS Monitor (9700)
- Maintenance Tracker (9800)
- Fuel Optimizer (9900)
- Wireless Charger (10000)
- Dash Cam (10100)

## Testing ✅

All endpoints tested and verified:
- ✓ Health endpoint responding
- ✓ 32 services discovered
- ✓ 4 categories organized
- ✓ Live widget data from 9 services
- ✓ Preferences system working
- ✓ Dashboard UI loads successfully
- ✓ Search functionality
- ✓ Settings panel
- ✓ Alert system

## Technologies Used 🛠️

- **Backend**: Flask, SQLite
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: CSS Grid, Flexbox, Custom Properties
- **Animations**: CSS Animations, Transitions
- **Integration**: REST APIs, JSON
- **Database**: SQLite with Python DB API

## Key Features Implemented ✨

1. ✅ Service Discovery (32 services)
2. ✅ Health Monitoring (real-time status)
3. ✅ Live Data Widgets (9 widget types)
4. ✅ Quick Actions Panel
5. ✅ Search Functionality
6. ✅ Settings Panel
7. ✅ Alert System
8. ✅ Theme Support (Dark/Light)
9. ✅ Database Storage
10. ✅ Responsive Design
11. ✅ Touch-Friendly Interface
12. ✅ Auto-Refresh
13. ✅ Category Organization
14. ✅ Beautiful Gradients & Animations

## Performance 🚀

- Auto-refresh every 5 seconds (configurable)
- Efficient API calls with caching
- Smooth animations with CSS transforms
- Optimized for 2000×1200 resolution
- Touch-friendly 44px minimum tap targets

---

**Built with ❤️ for the SONIC QLED Display**
**THE ultimate command center for your vehicle! 🔥**
