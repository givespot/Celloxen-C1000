#!/bin/bash
# CELLOXEN-C1000 BACKEND STARTUP SCRIPT

cd /var/www/Celloxen-C1000/backend

# Stop any existing instances
pkill -f "uvicorn.*simple_auth_main" 2>/dev/null || true
sleep 2

# Start backend
echo "Starting Celloxen-C1000 backend..."
nohup python3 -m uvicorn simple_auth_main:app \
    --host 0.0.0.0 \
    --port 5001 \
    --reload \
    > /var/log/celloxen-c1000-backend.log 2>&1 &

sleep 3

# Check if running
if ps aux | grep -v grep | grep "uvicorn.*simple_auth_main" > /dev/null; then
    echo "✅ Backend started successfully!"
    echo "Process ID: $(pgrep -f 'uvicorn.*simple_auth_main')"
    echo "Log file: /var/log/celloxen-c1000-backend.log"
else
    echo "❌ Backend failed to start - check logs"
    tail -30 /var/log/celloxen-c1000-backend.log
fi
