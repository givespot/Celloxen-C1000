#!/bin/bash
# Script 4: Configure Nginx
# Sets up Nginx as reverse proxy for the application

set -e

echo "=== Celloxen Nginx Configuration ==="

DOMAIN="${DOMAIN:-celloxen.com}"
APP_DIR="/var/www/celloxen"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

echo "[1/4] Creating Nginx configuration..."
cat > /etc/nginx/sites-available/celloxen << EOF
upstream celloxen_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Redirect HTTP to HTTPS (uncomment after SSL setup)
    # return 301 https://\$server_name\$request_uri;

    root $APP_DIR/frontend;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias $APP_DIR/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Frontend files
    location / {
        try_files \$uri \$uri/ /index.html;
        expires 1h;
    }

    # API proxy
    location /api/ {
        proxy_pass http://celloxen_backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        proxy_buffering off;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://celloxen_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://celloxen_backend/api/v1/health;
        access_log off;
    }

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

echo "[2/4] Enabling site..."
ln -sf /etc/nginx/sites-available/celloxen /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "[3/4] Testing Nginx configuration..."
nginx -t

echo "[4/4] Reloading Nginx..."
systemctl reload nginx

echo ""
echo "=== Nginx configuration complete ==="
echo "Site available at: http://$DOMAIN"
echo ""
echo "Next: Run 5_configure_supervisor.sh"
