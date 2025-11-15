# SupersonicBuilder v3.0.0 - Quick Start Guide

**Get started with the ULTIMATE automotive retrofit system in 5 minutes!**

---

## 🚀 INSTANT START

### 1. Open SONIC Command Center

**The SONIC Command Center is your gateway to all 32 services.**

```bash
# Start the Command Center
python3 services/command_center/app.py
```

Then open your browser to: **http://localhost:5000**

**That's it!** You now have access to all features!

---

## 🎯 WHAT YOU SEE

### SONIC Command Center Dashboard

When you open port 5000, you'll see:

1. **Service Grid** - All 32 services organized by category
2. **Live Data Widgets** - Real-time data from your car:
   - Speed, RPM, Fuel (from CAN Bus)
   - Now Playing (from Media Center)
   - Climate Status
   - Tire Pressures
   - Battery %
   - And more!
3. **Quick Actions** - One-click shortcuts
4. **Search Bar** - Find any service instantly

### Categories:

**🔧 Hardware Tools (12 services)**
- CAN Bus Monitor
- Maestro RR2 Integration
- 360° Camera System
- Hardware Health Monitor
- PCB Designer
- AI Board Analyzer
- Installation Logger
- Digital Audio Path Optimizer
- Remote Diagnostics
- Wire Harness Calculator
- BOM Generator
- Quote Generator

**🎵 Premium Audio (4 services)**
- Advanced DSP Control
- Sound Stage Optimizer
- Audio Visualizer
- Bass Management

**🎨 Visual & Performance (3 services)**
- RGB Lighting Controller
- Theme Designer
- Performance Dashboard

**🤖 Smart Features (13 services)**
- Climate Control
- Voice Assistant
- Parking Assistant
- Driving Analytics
- Security System
- App Manager
- Media Center
- Navigation Overlay+
- TPMS Monitor
- Maintenance Reminder
- Fuel Economy Optimizer
- Wireless Charger Monitor
- Dash Cam Recorder

---

## ⚡ QUICK TASKS

### Task 1: Tune Your Audio (5 minutes)

**Goal:** Create studio-quality sound in your Sonic

1. Click **"Advanced DSP Control"** (Port 8100)
2. Select a preset: **"Rock"**, **"Jazz"**, or **"Car Audio"**
3. Or customize your own:
   - Adjust 31-band EQ
   - Set time alignment
   - Configure crossovers
4. Click **"Save Preset"** with your custom name
5. Done! Your audio is now AMAZING!

**Bonus:** Open **Sound Stage Optimizer** (Port 8200) and click **"AI Auto-Tune"** for AI-powered acoustic correction!

---

### Task 2: Set Up Voice Control (3 minutes)

**Goal:** Control everything with "Hey Sonic"

1. Click **"AI Voice Assistant"** (Port 8900)
2. Test wake word detection (says "Hey Sonic" and it activates)
3. Try commands:
   - "Play my rock playlist"
   - "Turn up the bass"
   - "Enable night mode lighting"
   - "What's my tire pressure?"
4. Create custom commands in the **Commands** tab
5. Done! You now have voice control!

---

### Task 3: Monitor Your Car (2 minutes)

**Goal:** See live data from your car

1. Already visible on SONIC Command Center!
2. Or click **"CAN Bus Monitor"** (Port 7000) for detailed data:
   - Real-time speed, RPM, fuel rate
   - Coolant temperature
   - Throttle position
   - And 20+ more parameters
3. Click **"Driving Analytics"** (Port 9200) to see:
   - Trip computer
   - Fuel economy
   - Driving score
4. Done! You're monitoring everything!

---

### Task 4: Set Up Security (3 minutes)

**Goal:** Protect your car with motion detection and GPS tracking

1. Click **"Security System"** (Port 9300)
2. Click **"Arm System"**
3. Set up geofence:
   - Enter home address
   - Set radius (e.g., 1 mile)
4. Configure alerts:
   - Enable SMS/email notifications
5. Done! Your car is now protected!

**Bonus:** The 360° cameras automatically record if motion is detected!

---

### Task 5: Customize Your Look (5 minutes)

**Goal:** Make the UI match your Sonic's interior

1. Click **"Theme Designer"** (Port 8600)
2. Choose a template:
   - **Modern Dark** (default)
   - **Sonic Blue** (matches factory blue accents!)
   - **Neon** (futuristic)
3. Or customize colors:
   - Pick primary color
   - Pick accent color
4. Upload a custom wallpaper (auto-resizes to 2000×1200)
5. Click **"Apply Theme"**
6. Done! Your UI looks incredible!

**Bonus:** Set up **RGB Lighting** (Port 8500) to match your theme colors!

---

## 🎛️ ADVANCED FEATURES

### Create a Voice Macro

**Example: "Night Mode" macro**

1. Go to Voice Assistant (Port 8900)
2. Click **"Macros"** tab
3. Create new macro:
   - Name: "Night Mode"
   - Actions:
     - Enable night lighting (RGB Lighting)
     - Set climate to 72°F (Climate Control)
     - Lower display brightness (Theme Designer)
     - Start relaxing playlist (Media Center)
4. Save macro
5. Now say: **"Hey Sonic, enable night mode"** and all 4 actions happen instantly!

---

### Set Up Music-Reactive Lighting

1. Go to **Audio Visualizer** (Port 8300)
2. Select a theme (e.g., **"Neon"**)
3. Go to **RGB Lighting** (Port 8500)
4. Select **"Bass Pulse"** mode
5. Adjust sensitivity slider to taste
6. Play music from **Media Center** (Port 9500)
7. **BOOM!** Your car's interior lights pulse with the bass!

---

### Plan Your Next Road Trip

1. Go to **Navigation Overlay+** (Port 9600)
2. Enter destination
3. Select route strategy:
   - **Fastest** - Highway, high speed
   - **Fuel-efficient** - Optimized for MPG
   - **Avoid tolls** - Save money
4. See fuel cost estimate (pulled from Fuel Optimizer)
5. Start navigation!

During trip:
- **Driving Analytics** (Port 9200) tracks your route
- **Fuel Optimizer** (Port 9900) gives real-time MPG tips
- **Dash Cam** (Port 10100) records the journey
- **Security System** (Port 9300) tracks GPS location

---

## 🔧 SERVICE PORTS REFERENCE

**Quick access to any service:**

### Hardware Tools (7000-7900)
- **7000** - CAN Bus Monitor
- **7100** - PCB Designer
- **7200** - Maestro RR2 Integration
- **7300** - 360° Camera System
- **7400** - Hardware Health Monitor
- **7500** - AI Board Analyzer
- **7600** - Installation Logger
- **7700** - Digital Audio Path Optimizer
- **7800** - Remote Diagnostics
- **7900** - Wire Harness Calculator

### Professional Tools (8080-8090)
- **8080** - BOM Generator
- **8090** - Quote Generator

### Audio & Visual (8100-8900)
- **8100** - Advanced DSP Control
- **8200** - Sound Stage Optimizer
- **8300** - Audio Visualizer
- **8400** - Bass Management
- **8500** - RGB Lighting
- **8600** - Theme Designer
- **8700** - Performance Dashboard
- **8800** - Climate Control
- **8900** - Voice Assistant

### Smart Features (9100-10100)
- **9100** - Parking Assistant
- **9200** - Driving Analytics
- **9300** - Security System
- **9400** - App Manager
- **9500** - Media Center
- **9600** - Navigation Overlay+
- **9700** - TPMS Monitor
- **9800** - Maintenance Reminder
- **9900** - Fuel Economy Optimizer
- **10000** - Wireless Charger Monitor
- **10100** - Dash Cam Recorder

### Command Center
- **5000** - SONIC Command Center (MAIN)

**Access any service:** `http://localhost:[PORT]`

---

## 🔌 HARDWARE INTEGRATION

### Required Hardware (for full functionality):

1. **EOENKK Android 15 Head Unit** (you have this!)
   - Snapdragon 8-core @ 2.0GHz
   - 12GB RAM, 256GB storage
   - QLED 2000×1200 display
   - Built-in DSP, 4×45W amp

2. **iDatalink Maestro RR2** (you have this!)
   - Steering wheel controls
   - Factory system integration
   - GMLAN CAN bus interface

3. **Optional Hardware:**
   - **ELM327 USB adapter** - For CAN Bus Monitor (Port 7000)
   - **4 cameras** - For 360° Camera System (Port 7300)
   - **WS2812B LED strips** - For RGB Lighting (Port 8500)
   - **Arduino/ESP32** - LED controller
   - **GPS module** - For Navigation/Security/Analytics

### Software-Only Mode:

**Good news!** All services work in **simulation mode** without hardware:
- CAN Bus Monitor generates mock vehicle data
- Camera System uses test images
- RGB Lighting simulates LED control
- Everything else uses simulated data

**You can test EVERYTHING right now, even without the car!**

---

## 🎯 TYPICAL WORKFLOWS

### Daily Use:

1. **Start car** → SONIC Command Center auto-opens on QLED display
2. **Glance at dashboard** → See speed, RPM, tire pressures, climate
3. **Say "Hey Sonic, play my driving playlist"** → Music starts (Media Center)
4. **Lights pulse with music** → RGB Lighting in Bass Pulse mode
5. **Drive with navigation** → Navigation Overlay+ shows speed limits, POI
6. **Park** → Parking Assistant guides you in, Security System arms automatically
7. **Check stats** → Driving Analytics shows trip summary, fuel economy tips

### Weekend Tuning Session:

1. **Open DSP Control** (Port 8100) → Adjust 31-band EQ
2. **Run Sound Stage Optimizer** (Port 8200) → Get AI recommendations
3. **Set up subwoofer** → Bass Management (Port 8400) for perfect bass
4. **Test with visualizer** → Audio Visualizer (Port 8300) shows frequency response
5. **Save preset** → "Weekend Cruising" saved!

### Installation/Upgrade:

1. **Use AI Board Analyzer** (Port 7500) → Identify ICs on new circuit board
2. **Design custom PCB** → PCB Designer (Port 7100) for signal conversion
3. **Generate BOM** → BOM Generator (Port 8080) lists all parts needed
4. **Calculate wire lengths** → Wire Harness Calculator (Port 7900)
5. **Log installation** → Installation Logger (Port 7600) tracks progress
6. **Monitor health** → Hardware Health Monitor (Port 7400) during testing

---

## 💡 PRO TIPS

### Tip 1: Use Keyboard Shortcuts
- **Search:** Type `/` to focus search bar
- **Settings:** Type `?` to open settings
- **Refresh:** Press `R` to refresh all services

### Tip 2: Create Custom Dashboards
In SONIC Command Center:
1. Click **Settings** (gear icon)
2. **Customize Layout**
3. Drag services to rearrange
4. Hide services you don't use
5. Save layout

### Tip 3: Export Your Settings
Most services have **Export** buttons:
- **DSP Control:** Export EQ settings → Import to head unit
- **Theme Designer:** Export theme → Share with friends
- **Voice Assistant:** Export macros → Backup
- **Driving Analytics:** Export trips → Analyze in Excel

### Tip 4: Check Health Endpoints
If a service isn't working:
1. Open `http://localhost:[PORT]/health`
2. Check `"status": "healthy"`
3. Look for error messages
4. Restart service if needed

### Tip 5: Use AI Features (Optional)
**If you have an Anthropic API key:**
1. Add `ANTHROPIC_API_KEY` to secrets
2. Get better AI features:
   - **Sound Stage Optimizer:** Better acoustic analysis
   - **AI Board Analyzer:** More accurate IC identification
   - **Parking Assistant:** Better object detection
   - **Voice Assistant:** Smarter command parsing

**Without API key:** All services still work with rule-based fallbacks!

---

## 🐛 TROUBLESHOOTING

### Service won't start?
```bash
# Check if port is in use
lsof -i :[PORT]

# Kill process on port
kill -9 [PID]

# Restart service
python3 services/[SERVICE_NAME]/app.py
```

### SONIC Command Center shows service offline?
1. Click **"Refresh All"** button
2. Check if service is running: `http://localhost:[PORT]/health`
3. Start service manually if needed

### CAN Bus not working?
1. Check if ELM327 adapter is connected
2. Go to CAN Bus Monitor (Port 7000)
3. Click **"Test Connection"**
4. If no adapter: Service runs in **simulation mode** (generates mock data)

### Audio Visualizer not showing music?
1. Make sure music is playing from Media Center (Port 9500)
2. Check audio input source in visualizer settings
3. Try test tone generator

### RGB Lighting not syncing with music?
1. Go to RGB Lighting (Port 8500)
2. Check **"Music Reactive"** mode is enabled
3. Verify Audio Visualizer (Port 8300) is running
4. Adjust sensitivity slider

---

## 📚 LEARN MORE

### Documentation:
- **Full Feature List:** `docs/FEATURES_v3.0.0.md`
- **Hardware Guide:** `docs/HARDWARE_GUIDE_v3.0.0.md` (coming soon)
- **API Documentation:** Each service has `README.md` in its folder

### Service-Specific Guides:
- **DSP Control:** `services/dsp/README.md`
- **Voice Assistant:** `services/voice/README.md`
- **Theme Designer:** `services/themes/README.md`
- **And 29 more!**

### Video Tutorials (Planned):
- Getting started with SONIC Command Center
- Audio tuning masterclass
- Voice command setup
- Security system configuration
- Custom theme creation

---

## 🎉 YOU'RE READY!

**You now have the ULTIMATE automotive retrofit system!**

**Next steps:**
1. ✅ Explore SONIC Command Center
2. ✅ Tune your audio with DSP Control
3. ✅ Set up voice commands
4. ✅ Customize your theme
5. ✅ Enable security system
6. ✅ Track your driving analytics
7. ✅ Show off your build to friends!

**When they see this, they'll say: "WOW! That's the coolest build I've ever seen!"** 🔥💥🚀

---

## 🤝 SUPPORT

**Questions? Issues? Suggestions?**

- Check service README files
- Review health endpoints
- Consult `docs/FEATURES_v3.0.0.md`

**This is YOUR build. Make it legendary!** 🏆
