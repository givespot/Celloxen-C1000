#!/bin/bash
# Script 5: Configure Supervisor
# Sets up Supervisor to manage the application process

set -e

echo "=== Celloxen Supervisor Configuration ==="

APP_DIR="/var/www/celloxen"
WORKERS="${WORKERS:-4}"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

echo "[1/3] Creating Supervisor configuration..."
cat > /etc/supervisor/conf.d/celloxen.conf << EOF
[program:celloxen]
command=$APP_DIR/venv/bin/gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 backend.main:app
directory=$APP_DIR
user=celloxen
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/celloxen/error.log
stdout_logfile=/var/log/celloxen/access.log
environment=
    PATH="$APP_DIR/venv/bin",
    PYTHONPATH="$APP_DIR",
    ENV="production"

[program:celloxen-worker]
command=$APP_DIR/venv/bin/celery -A backend.celery_app worker --loglevel=info
directory=$APP_DIR
user=celloxen
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/celloxen/celery-error.log
stdout_logfile=/var/log/celloxen/celery.log
environment=
    PATH="$APP_DIR/venv/bin",
    PYTHONPATH="$APP_DIR"

[group:celloxen-all]
programs=celloxen,celloxen-worker
priority=999
EOF

echo "[2/3] Reloading Supervisor..."
supervisorctl reread
supervisorctl update

echo "[3/3] Starting application..."
supervisorctl start celloxen-all:*

echo ""
echo "=== Supervisor configuration complete ==="
echo ""
echo "Useful commands:"
echo "  supervisorctl status celloxen-all:*"
echo "  supervisorctl restart celloxen-all:*"
echo "  supervisorctl tail -f celloxen"
echo ""
echo "Next: Run 6_setup_ssl.sh"
