#!/bin/bash
#
# Custom UI Theme Designer Service Startup Script
# Port: 8600
#

echo "Starting Custom UI Theme Designer Service..."
echo "Port: 8600"
echo "Service URL: http://localhost:8600"
echo "Health Check: http://localhost:8600/health"
echo ""

cd "$(dirname "$0")"
PORT=8600 python3 app.py
