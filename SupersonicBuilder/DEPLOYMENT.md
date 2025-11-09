# Supersonic Commander Deployment Guide

This guide covers deploying the Supersonic Commander Control Panel to various platforms.

## 🚀 Quick Deploy Options

### 1. **Replit (Current Environment)**

The system is already configured and running on Replit on port 5000.

**To run:**
```bash
make supersonic-serve
# or
python supersonic_settings_server.py
```

**Replit Configuration:**
- The `.replit` file configures the environment
- Port 5000 is automatically exposed
- All 4 workflows can run simultaneously

---

### 2. **Heroku Deployment**

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Deploy Steps:**
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-supersonic-commander

# Add buildpacks
heroku buildpacks:add --index 1 heroku/python

# Deploy
git push heroku main

# Open app
heroku open
```

**Files Used:**
- `Procfile` - Defines web dyno with gunicorn
- `requirements.txt` - Python dependencies

**Port Configuration:**
Heroku automatically sets `$PORT` environment variable, which gunicorn binds to.

---

### 3. **Render Deployment**

**Prerequisites:**
- Render account connected to your GitHub repo

**Deploy Steps:**

**Option A: Docker (Recommended)**
1. Push code to GitHub
2. Go to Render Dashboard
3. Click "New +" → "Web Service"
4. Connect your repo
5. Render auto-detects `render.yaml`
6. Click "Create Web Service"

**Option B: Native Python**
1. In `render.yaml`, comment out `runtime: docker`
2. Uncomment `buildCommand` and `startCommand`
3. Follow Option A steps

**Files Used:**
- `render.yaml` - Service configuration
- `Dockerfile` - Container definition (if using Docker)
- `requirements.txt` - Python dependencies

**Health Check:**
- Path: `/` (control panel homepage)
- Expected: 200 OK

---

### 4. **Docker Deployment (Self-Hosted)**

**Prerequisites:**
- Docker installed

**Build and Run:**
```bash
# Build image
docker build -t supersonic-commander .

# Run container
docker run -p 5055:5055 supersonic-commander

# Or with custom port
docker run -p 8080:5055 -e PORT=5055 supersonic-commander
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  supersonic:
    build: .
    ports:
      - "5055:5055"
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    volumes:
      - ./docs:/app/docs
    restart: unless-stopped
```

**Files Used:**
- `Dockerfile` - Multi-stage build with TTS support
- `.dockerignore` - Excludes unnecessary files from image

---

### 5. **Generic VPS/Cloud (Ubuntu)**

**Prerequisites:**
- Ubuntu 20.04+ server
- Python 3.11+
- Nginx (optional, for reverse proxy)

**Setup Steps:**
```bash
# Clone repo
git clone https://github.com/your-repo/sonic-builder.git
cd sonic-builder

# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn supersonic_settings_server:app \
  --bind 0.0.0.0:5055 \
  --workers 2 \
  --threads 4 \
  --timeout 120 \
  --daemon

# Or use systemd service (see below)
```

**Systemd Service (`/etc/systemd/system/supersonic.service`):**
```ini
[Unit]
Description=Supersonic Commander Control Panel
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/supersonic-commander
Environment="PATH=/opt/supersonic-commander/venv/bin"
Environment="FLASK_ENV=production"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/supersonic-commander/venv/bin/gunicorn \
  supersonic_settings_server:app \
  --bind 0.0.0.0:5055 \
  --workers 2 \
  --threads 4 \
  --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable supersonic
sudo systemctl start supersonic
sudo systemctl status supersonic
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5055 | Port for web server |
| `FLASK_ENV` | production | Flask environment |
| `PYTHONUNBUFFERED` | 1 | Disable Python buffering |
| `SUP_VOICE_PACK` | FlightOps | Default voice pack |

### Port Configuration

- **Development (Replit):** Port 5000
- **Production (Heroku/Render):** Uses `$PORT` environment variable
- **Docker:** Default 5055, configurable via `PORT` env var

---

## 🎙️ Voice System (TTS)

The system uses **pyttsx3** for text-to-speech, which requires audio drivers.

**Platform Support:**

| Platform | TTS Support | Notes |
|----------|-------------|-------|
| Replit | ✅ Yes | Works with browser audio |
| Heroku | ⚠️  Limited | No audio drivers, falls back to console |
| Render | ⚠️  Limited | No audio drivers in container, falls back to console |
| Docker | ✅ Yes | If host has audio drivers (with `--device /dev/snd`) |
| VPS | ✅ Yes | Install espeak: `apt-get install libespeak-ng1` |

**Fallback Behavior:**
If TTS initialization fails, the system gracefully falls back to console output:
```
🔊 [TTS disabled] Mission complete. All systems nominal.
```

---

## 🛡️ Production Checklist

Before deploying to production:

- [ ] Review and update `supersonic_settings.json`
- [ ] Set `advanced_tools: false` in settings (hide dangerous operations)
- [ ] Configure environment variables
- [ ] Test health check endpoint (`/`)
- [ ] Verify audit logging works (`docs/_ops_log.txt`)
- [ ] Test rollback functionality with backup
- [ ] Set up monitoring/alerting
- [ ] Configure reverse proxy (Nginx) if needed
- [ ] Enable HTTPS/SSL
- [ ] Set up automated backups of `docs/` directory

---

## 🔒 Security Recommendations

1. **Use HTTPS** - Always serve over SSL in production
2. **Environment Secrets** - Use platform secret management (Heroku Config Vars, Render Environment Variables)
3. **Backup Strategy** - Regularly backup `docs/` directory and `docs/_ops_log.txt`
4. **Access Control** - Add authentication layer for production (not included by default)
5. **Rate Limiting** - Consider adding rate limiting to API endpoints

---

## 📊 Monitoring

### Health Check

All platforms should monitor:
- **Endpoint:** `GET /`
- **Expected:** 200 OK
- **Timeout:** 5 seconds

### Logs

**Heroku:**
```bash
heroku logs --tail --app your-supersonic-commander
```

**Render:**
- View logs in Render Dashboard

**Docker:**
```bash
docker logs -f container-id
```

### Metrics to Monitor

- Response time on `/api/rebuild-status`, `/api/deploy-status`
- Disk usage in `docs/` directory
- Memory usage (workflow processes)
- Audit log growth rate

---

## 🆘 Troubleshooting

### Issue: Workflows not running

**Solution:** Platform may not support background processes. Use external scheduler or move to VPS.

### Issue: TTS initialization failed

**Solution:** Expected on Heroku/Render. System falls back to console output. No action needed.

### Issue: Port binding error

**Solution:** Check `$PORT` environment variable is set correctly.

### Issue: Static files not loading

**Solution:** Verify Flask static folder configuration in `supersonic_settings_server.py`.

---

## 📚 Additional Resources

- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Render Deploy Guide](https://render.com/docs/deploy-flask)
- [Docker Python Best Practices](https://docs.docker.com/language/python/build-images/)
- [Gunicorn Documentation](https://docs.gunicorn.org/en/stable/)

---

**Need Help?** Open an issue in the GitHub repository.
