# CI/CD Health Check Integration Guide

## Overview

SonicBuilder Supersonic now includes production-ready health endpoints for both services:

- **PDF Viewer** (port 5000): Main documentation server
- **Supersonic Commander** (port 8080): Control panel and operations console

## Health Endpoints

### PDF Viewer (serve_pdfs.py)

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/` | Root HTML page | HTTP 200 + HTML |
| `/health` | Simple health check | `OK` |

### Supersonic Commander (supersonic_settings_server.py)

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/` | Control panel HTML | HTTP 200 + HTML |
| `/healthz` | Liveness probe | JSON with uptime |
| `/readyz` | Readiness probe | JSON with checks |

## Health Check Script

Use the included `healthcheck.py` script:

```bash
# Basic usage
python healthcheck.py --host 127.0.0.1 --port 8080

# With custom retry settings
python healthcheck.py --host 127.0.0.1 --port 8080 --retries 60 --sleep 1

# Check specific endpoints
python healthcheck.py --host 127.0.0.1 --port 8080 --paths / /healthz /readyz
```

### Parameters

- `--host`: Server hostname (default: 127.0.0.1)
- `--port`: Server port (default: 8080)
- `--paths`: Endpoints to check (default: /, /healthz, /readyz)
- `--retries`: Number of retry attempts (default: 30)
- `--sleep`: Sleep between retries in seconds (default: 1.0)
- `--timeout`: HTTP request timeout (default: 3.0)

## Makefile Integration

Use the convenient Make target:

```bash
make supersonic-health
```

## GitHub Actions Example

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Start Supersonic Commander (background)
      run: |
        PORT=8080 python supersonic_settings_server.py &
        echo $! > server.pid
        sleep 2
    
    - name: Health check
      run: |
        python healthcheck.py --host 127.0.0.1 --port 8080 --retries 60 --sleep 1
    
    - name: Build PDFs
      run: |
        make build_dark
    
    - name: Stop server
      if: always()
      run: |
        kill $(cat server.pid) || true
```

## Docker Health Checks

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python healthcheck.py --host 127.0.0.1 --port 8080 --retries 3 || exit 1

CMD ["python", "supersonic_settings_server.py"]
```

## Kubernetes Liveness/Readiness Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: supersonic-commander
spec:
  containers:
  - name: app
    image: supersonic-commander:latest
    ports:
    - containerPort: 8080
    
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 3
    
    readinessProbe:
      httpGet:
        path: /readyz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
```

## Replit Autoscale Deployment

The PDF Viewer is configured for Autoscale deployment with production-ready Gunicorn server:

```bash
# Deployment configuration
Deployment Type: Autoscale
Run Command: gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 serve_pdfs:app

# Health check endpoint
GET / → Returns HTML (200 OK)
GET /health → Returns "OK"
```

### Deployment Verification

After deployment, verify health:

```bash
# Check deployed endpoint
curl https://your-app.repl.co/health
# Should return: OK

# Test from health script
python healthcheck.py --host your-app.repl.co --port 443 --retries 5
```

## Local Development

### Start both services:

```bash
# Terminal 1: PDF Viewer (port 5000)
gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 serve_pdfs:app

# Terminal 2: Supersonic Commander (port 8080)
PORT=8080 python supersonic_settings_server.py

# Terminal 3: Health checks
python healthcheck.py --host 127.0.0.1 --port 5000 --paths / /health
python healthcheck.py --host 127.0.0.1 --port 8080 --paths / /healthz /readyz
```

## Monitoring Integration

### Prometheus

```yaml
scrape_configs:
  - job_name: 'supersonic-commander'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/healthz'
    scrape_interval: 30s
```

### Datadog

```python
from datadog import statsd

response = requests.get('http://localhost:8080/healthz')
if response.status_code == 200:
    statsd.gauge('supersonic.health', 1)
else:
    statsd.gauge('supersonic.health', 0)
```

## Troubleshooting

### Health check fails

1. **Server not started**: Ensure the service is running
2. **Port conflict**: Check if the port is already in use
3. **Firewall**: Verify firewall rules allow the port
4. **Wrong host**: Use 127.0.0.1 for localhost, 0.0.0.0 for all interfaces

### Readiness check fails

Check the `/readyz` response for details:

```bash
curl http://localhost:8080/readyz | python -m json.tool
```

Example response:
```json
{
  "status": "ready",
  "checks": {
    "settings_loaded": true,
    "flask_app": true
  }
}
```

## Exit Codes

The `healthcheck.py` script returns:
- **0**: All health checks passed
- **1**: One or more health checks failed

Use this for CI/CD pipeline failure detection.

## Best Practices

1. **Always use health checks in CI/CD** to catch deployment issues early
2. **Set appropriate retry counts** based on your startup time
3. **Monitor all endpoints** (/, /healthz, /readyz) for comprehensive checks
4. **Use liveness probes** to detect crashes
5. **Use readiness probes** to detect when the app is ready to serve traffic
6. **Include timeouts** to prevent hanging health checks
7. **Log health check results** for debugging

## Summary

- ✅ Production-ready health endpoints on both services
- ✅ Automated health check script with retries
- ✅ Makefile integration for easy testing
- ✅ CI/CD examples for GitHub Actions, Docker, Kubernetes
- ✅ Replit Autoscale deployment ready
- ✅ Standards-compliant (liveness/readiness probes)

For questions or issues, check the logs:
```bash
# Check workflow logs
cat /tmp/logs/PDF_Viewer_*.log
cat /tmp/logs/Supersonic_Commander_*.log
```
