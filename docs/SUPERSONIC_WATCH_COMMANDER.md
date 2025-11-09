# 🛰️ SonicBuilder Supersonic — Watch & Commander System

**Complete automation suite for live development with file watch, smart diff, system tray, and audio feedback**

---

## 📦 System Overview

The Watch & Commander System provides **7 specialized tools** for continuous development:

### 🔍 **File Watchers** (3 tools)
- `supersonic_watch_secure_build.py` — Full auto-rebuild on any change
- `supersonic_watch_smartdiff.py` — Smart-diff selective rebuilds
- `supersonic_commander_watch.py` — Unified CLI commander

### 🖥️ **System Tray Commanders** (3 tools)
- `supersonic_tray_commander.py` — Basic tray control
- `supersonic_tray_commander_color.py` — Color-coded status indicators
- `supersonic_tray_commander_audio.py` — Audio feedback integration

### 🎧 **Audio Engine** (1 tool)
- `supersonic_audio_engine.py` — Modular sound cue system

---

## 🔍 File Watch System

### 1. Basic Watch — Full Auto-Rebuild

Monitors for any file change and triggers complete rebuild.

**File:** `builders/supersonic_watch_secure_build.py`

**Usage:**
```bash
pip install watchdog
python builders/supersonic_watch_secure_build.py
```

**Features:**
- ✅ Monitors all SonicBuilder files
- ✅ 10-second cooldown between builds
- ✅ Automatic secure build chain trigger
- ✅ Ignores temp files (.swp, .tmp, ~)

**Watches:**
- `SonicBuilder/` directory
- All builder scripts
- `sonicbuilder.config.json`

**When to Use:**
- Continuous integration testing
- Full system validation
- Initial development setup

---

### 2. Smart-Diff Watch — Selective Rebuilds

Intelligent watcher that only rebuilds what changed.

**File:** `builders/supersonic_watch_smartdiff.py`

**Usage:**
```bash
python builders/supersonic_watch_smartdiff.py
```

**Smart Triggers:**
```
File Changed                          → Action Triggered
─────────────────────────────────────────────────────────
make_supersonic_dashboard_v3.py       → Rebuild dashboard
make_supersonic_fieldcard.py          → Rebuild single card
make_supersonic_fieldcard_double.py   → Rebuild double card
make_supersonic_fieldkit.py           → Repackage field kit
make_supersonic_release_secure.py     → Regenerate manifests
sonicbuilder.config.json              → Full rebuild
SonicBuilder/docs/*                   → Repackage field kit
```

**Benefits:**
- ⚡ Faster rebuilds (only what changed)
- 🎯 Targeted testing
- 💰 Saves CPU cycles

---

### 3. Commander Watch — Unified Control

CLI commander with smart/full modes.

**File:** `builders/supersonic_commander_watch.py`

**Usage:**
```bash
# Smart-Diff Mode (default)
python builders/supersonic_commander_watch.py --smart

# Full-Auto Mode
python builders/supersonic_commander_watch.py --full
```

**Flags:**
- `--smart` or `-s` — Smart-diff mode
- `--full` or `-f` — Full auto-rebuild mode

**Features:**
- ✅ Colorized console output
- ✅ Mode indicator banner
- ✅ 5-second cooldown
- ✅ Real-time timestamps
- ✅ Graceful shutdown (Ctrl-C)

**Console Output:**
```
🚀  SONICBUILDER SUPERSONIC COMMANDER  🚀
=========================================
Mode: SMART-DIFF 🧠
Press Ctrl-C to exit.

🛰️  Change detected (18:42:15): make_supersonic_dashboard_v3.py
[18:42:15] ⚙️  Dashboard v3 (QR) → python builders/make_supersonic_dashboard_v3.py
✅ Dashboard v3 (QR) complete.
```

---

## 🔔 Desktop Notifications

Add visual desktop alerts to any watcher.

**File:** `builders/supersonic_commander_watch_notify.py`

**Usage:**
```bash
pip install plyer
python builders/supersonic_commander_watch_notify.py --smart
```

**Notifications:**
- 🧑‍✈️ **Commander Online** — Startup notification
- ✅ **Build Complete** — Successful build
- ❌ **Build Failed** — Failed build with error code
- 🛑 **Commander Offline** — Shutdown notification

**Cross-Platform:**
- **Windows:** Native toast notifications
- **macOS:** Notification Center
- **Linux:** libnotify/notify-send

---

## 🖥️ System Tray Commander

Run builds from your system tray with visual control.

### Basic Tray Commander

**File:** `builders/supersonic_tray_commander.py`

**Usage:**
```bash
pip install pystray Pillow plyer
python builders/supersonic_tray_commander.py
```

**Menu Actions:**
- 🚀 **Run Full Secure Build** — Execute complete build chain
- 🧠 **Run Smart-Diff Build** — Execute smart-diff build
- ⏸️ **Pause / Resume Watcher** — Toggle auto-rebuild
- 📁 **Open Docs Folder** — Launch docs in file manager
- 🛑 **Quit Commander** — Stop tray application

**Icon:** Cyan circle with "SB" label

---

### Color-Coded Tray Commander

**File:** `builders/supersonic_tray_commander_color.py`

**Status Colors:**
```
🟦 Cyan (Idle)     — Ready for commands
🟩 Green (Building) — Build in progress
🟨 Yellow (Paused)  — Auto-rebuild paused
🟥 Red (Failure)    — Last build failed
```

**Dynamic Feedback:**
Icon color changes in real-time based on build status.

---

### Audio-Enhanced Tray Commander

**File:** `builders/supersonic_tray_commander_audio.py`

**Sound Cues:**
```
Event              → Sound File
───────────────────────────────────────
Commander startup  → commander_online.mp3
Build start        → build_start.mp3
Build success      → build_success.mp3
Build failure      → build_fail.mp3
Watcher paused     → pause_on.mp3
Watcher resumed    → pause_off.mp3
Commander exit     → commander_offline.mp3
```

**Setup:**
1. Create `sounds/` directory
2. Add MP3 or WAV files
3. Commander plays cues automatically

---

## 🎧 Audio Engine

Modular sound system for all commander tools.

**File:** `builders/supersonic_audio_engine.py`

### API Usage

```python
from builders.supersonic_audio_engine import play

# Play event cues
play("start")      # Build started
play("success")    # Build succeeded
play("fail")       # Build failed
play("pause_on")   # Paused
play("pause_off")  # Resumed
play("online")     # Commander online
play("offline")    # Commander offline
```

### Sound Pack Structure

```
sounds/
 ├── build_start.mp3 (or .wav)
 ├── build_success.mp3 (or .wav)
 ├── build_fail.mp3 (or .wav)
 ├── pause_on.mp3 (or .wav)
 ├── pause_off.mp3 (or .wav)
 ├── commander_online.mp3 (or .wav)
 └── commander_offline.mp3 (or .wav)
```

### Features

- ✅ **Dual-format support:** MP3 + WAV fallback
- ✅ **Threaded playback:** Non-blocking
- ✅ **Cooldown system:** Prevents sound spam
- ✅ **Auto-fallback:** MP3 → WAV if missing
- ✅ **Silent mode:** Graceful degradation if sounds missing

### Testing

```bash
# Verify sound pack
python builders/supersonic_audio_engine.py

# Output:
🎧 Verifying Commander Mix Pro Suite pack…
[AudioEngine] All cues present.

▶️  Commander Mix Demo sequence:
 → start
 → success
 → fail
 → pause_on
 → pause_off
 → online
 → offline
✅ Demo complete.
```

---

## 📦 Complete Tool Summary

| Tool | Type | Features |
|------|------|----------|
| `supersonic_watch_secure_build.py` | Watcher | Full auto-rebuild |
| `supersonic_watch_smartdiff.py` | Watcher | Smart selective rebuild |
| `supersonic_commander_watch.py` | Commander CLI | Unified smart/full modes |
| `supersonic_commander_watch_notify.py` | Commander CLI | + Desktop notifications |
| `supersonic_tray_commander.py` | System Tray | Basic tray menu |
| `supersonic_tray_commander_color.py` | System Tray | + Color status |
| `supersonic_tray_commander_audio.py` | System Tray | + Audio feedback |
| `supersonic_audio_engine.py` | Audio | Modular sound engine |

**Total:** 8 development automation tools

---

## 🚀 Quick Start Workflows

### Continuous Development

```bash
# Terminal 1: Run smart-diff watch with notifications
pip install watchdog plyer
python builders/supersonic_commander_watch_notify.py --smart

# Work on your files...
# Builds trigger automatically when you save
```

### Background System Tray

```bash
# Run color-coded tray commander with audio
pip install pystray Pillow plyer
python builders/supersonic_tray_commander_audio.py

# Commander runs in system tray
# Right-click icon for menu
# Visual + audio feedback
```

### Testing Audio Pack

```bash
# Install playsound
pip install playsound

# Create sounds/ directory with audio files
mkdir -p sounds/

# Test audio engine
python builders/supersonic_audio_engine.py
```

---

## 🛠️ Installation

### Base Dependencies

```bash
pip install watchdog plyer pystray Pillow
```

### Optional (Audio)

```bash
pip install playsound
```

### Complete Install

```bash
pip install -r supersonic_requirements.txt
```

---

## 🎯 Use Cases

### 1. Solo Development
```bash
# Run smart watcher in terminal
python builders/supersonic_watch_smartdiff.py
```
- Edit builders
- Save file
- Auto-rebuild affected assets
- Immediate feedback

### 2. Team Environment
```bash
# Run tray commander with notifications
python builders/supersonic_tray_commander_color.py
```
- Visual status indicators
- Menu-driven builds
- Desktop notifications
- No terminal needed

### 3. Presentation/Demo
```bash
# Run audio-enhanced commander
python builders/supersonic_tray_commander_audio.py
```
- Audio cues for live coding
- Visual + sound feedback
- Professional presentation

### 4. CI/CD Testing
```bash
# Run full auto-watch
python builders/supersonic_watch_secure_build.py
```
- Complete validation on every change
- Catch integration issues early
- Full rebuild verification

---

## 🎨 Customization

### Change Cooldown

```python
# In any watcher file
COOLDOWN = 5  # seconds (default: 5-10)
```

### Add Custom Triggers

```python
# In supersonic_watch_smartdiff.py
TRIGGERS = {
    "my_custom_script.py": "Custom Action",
    # Add more...
}
```

### Custom Sound Pack

1. Create `sounds/` directory
2. Add your MP3/WAV files with standard names:
   - `build_start.mp3`
   - `build_success.mp3`
   - etc.
3. Audio engine auto-detects and plays

---

## 🔍 Troubleshooting

### Watch Not Triggering

**Symptom:** Files change but no rebuild

**Solutions:**
1. Check cooldown hasn't been hit (wait 5-10 seconds)
2. Verify file is in watched paths
3. Check console for "Change detected" message
4. Restart watcher

### Notifications Not Showing

**Symptom:** No desktop alerts

**Solutions:**
1. Install plyer: `pip install plyer`
2. Check OS notification permissions
3. Test with: `python -c "from plyer import notification; notification.notify('Test', 'Message')"`

### Audio Not Playing

**Symptom:** No sound cues

**Solutions:**
1. Install playsound: `pip install playsound`
2. Verify `sounds/` directory exists
3. Add MP3 or WAV files
4. Test: `python builders/supersonic_audio_engine.py`
5. Check system volume

### Tray Icon Not Appearing

**Symptom:** Commander runs but no tray icon

**Solutions:**
1. Install pystray: `pip install pystray Pillow`
2. Check system tray settings (Windows: hidden icons)
3. macOS: Check menu bar icons
4. Linux: Ensure tray support in DE

---

## 📊 Performance

### Resource Usage

| Tool | CPU | Memory | Disk I/O |
|------|-----|--------|----------|
| Watch (basic) | ~0.1% | ~20 MB | Low |
| Watch (smart) | ~0.1% | ~20 MB | Low |
| Commander CLI | ~0.1% | ~25 MB | Low |
| Tray (basic) | ~0.2% | ~30 MB | Low |
| Tray (audio) | ~0.2% | ~35 MB | Medium |

### Build Times

**Smart-Diff vs Full:**
- Dashboard only: **2-3 sec** (smart) vs **30+ sec** (full)
- Single card: **3-5 sec** (smart) vs **30+ sec** (full)
- Field kit: **5-8 sec** (smart) vs **30+ sec** (full)

**Recommendation:** Use smart-diff for development, full for releases.

---

## 🎉 Complete Example

### Development Session

```bash
# 1. Start tray commander with audio
pip install pystray Pillow plyer playsound
python builders/supersonic_tray_commander_audio.py

# ▶️  Commander startup sound plays
# 🟦 Cyan icon appears in tray

# 2. Edit a dashboard file
# Save changes...

# 3. Auto-rebuild triggers
# 🟩 Icon turns green
# 🎵 Build start sound
# ... building ...
# 🟦 Icon returns to cyan
# 🎵 Success sound
# 📢 Desktop notification: "✅ Build Complete"

# 4. Open docs from tray menu
# Right-click icon → Open Docs Folder

# 5. Manually trigger full build
# Right-click icon → Run Full Secure Build
# ... full chain executes ...

# 6. Exit
# Right-click icon → Quit Commander
# 🎵 Shutdown sound
# 📢 "🛑 Commander Offline"
```

---

## 📚 Documentation Structure

Complete watch & commander documentation:

1. **SUPERSONIC_WATCH_COMMANDER.md** (this file) — Main guide
2. **SUPERSONIC_PRESENTATION.md** — Presentation tools
3. **SUPERSONIC_TOOLS.md** — Core Supersonic tools
4. **SUPERSONIC_COMPLETE.md** — System overview

---

## 🔮 Advanced Tips

### Background Process (Linux/macOS)

```bash
# Run tray commander as background daemon
nohup python builders/supersonic_tray_commander_audio.py &

# Or use screen/tmux
screen -S supersonic
python builders/supersonic_tray_commander_audio.py
# Ctrl-A, D to detach
```

### Startup Integration

**Windows (Startup Folder):**
1. Create shortcut to `supersonic_tray_commander_audio.py`
2. Place in: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

**macOS (Login Items):**
1. System Preferences → Users & Groups → Login Items
2. Add Python script

**Linux (Autostart):**
```bash
# Create desktop entry
cat > ~/.config/autostart/supersonic-commander.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Supersonic Commander
Exec=python /path/to/builders/supersonic_tray_commander_audio.py
EOF
```

---

**Complete watch system with 8 specialized tools for live Supersonic development!** 🚀

---

**See Also:**
- Sound pack creation guide (coming soon)
- Custom trigger development
- Multi-project watch setups
