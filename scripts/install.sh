#!/bin/bash
set -e

echo "🏥 Installing Celloxen Health Portal..."
echo "======================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)" 
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl ufw

# Create celloxen user
echo "👤 Creating celloxen system user..."
useradd -r -m -s /bin/bash celloxen 2>/dev/null || echo "User already exists"

# Setup Python environment
echo "🐍 Setting up Python environment..."
sudo -u celloxen python3 -m venv /home/celloxen/venv
sudo -u celloxen /home/celloxen/venv/bin/pip install --upgrade pip
sudo -u celloxen /home/celloxen/venv/bin/pip install -r backend/requirements.txt

# Setup PostgreSQL
echo "🗄️ Configuring PostgreSQL database..."
sudo -u postgres psql << 'PSQL'
DROP DATABASE IF EXISTS celloxen_portal;
DROP USER IF EXISTS celloxen_user;
CREATE USER celloxen_user WITH PASSWORD 'CelloxenSecure2025';
CREATE DATABASE celloxen_portal OWNER celloxen_user;
GRANT ALL PRIVILEGES ON DATABASE celloxen_portal TO celloxen_user;
PSQL

# Import database schema
echo "📊 Importing database schema..."
PGPASSWORD=CelloxenSecure2025 psql -U celloxen_user -d celloxen_portal -h localhost -f database/schema.sql
PGPASSWORD=CelloxenSecure2025 psql -U celloxen_user -d celloxen_portal -h localhost -f database/seed_data.sql

# Setup backend service
echo "⚙️ Setting up backend service..."
cat > /etc/systemd/system/celloxen-backend.service << 'SERVICE'
[Unit]
Description=Celloxen Health Portal Backend
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=root
WorkingDirectory=/var/www/celloxen-portal/backend
Environment=PATH=/home/celloxen/venv/bin
ExecStart=/home/celloxen/venv/bin/python -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5000 --workers 1
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

# Setup Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/celloxen-portal << 'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name celloxen.com www.celloxen.com;
    root /var/www/celloxen-portal/frontend;
    index index.html;

    # Frontend files
    location / {
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
        proxy_connect_timeout 90;
        proxy_send_timeout 90;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
NGINX

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/celloxen-portal /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# Setup firewall
echo "🔥 Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp  
ufw allow 443/tcp
ufw --force enable

# Enable and start services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable celloxen-backend
systemctl start celloxen-backend
systemctl enable nginx
systemctl restart nginx

# Verify services
echo "✅ Verifying installation..."
sleep 3
systemctl is-active --quiet celloxen-backend && echo "✅ Backend service running" || echo "❌ Backend service failed"
systemctl is-active --quiet nginx && echo "✅ Nginx running" || echo "❌ Nginx failed"
curl -s http://localhost:5000/health > /dev/null && echo "✅ API responding" || echo "❌ API not responding"

echo ""
echo "🎉 Installation complete!"
echo "======================================"
echo "🌐 Access your portal at: http://your-domain.com"
echo "🔑 Default login: admin@celloxen.com / password123"
echo "📁 Project files: /var/www/celloxen-portal"
echo "📝 Logs: journalctl -u celloxen-backend -f"
echo ""
echo "Next steps:"
echo "1. Configure your domain name"
echo "2. Setup SSL certificate (Let's Encrypt)"
echo "3. Test all functionality"
echo "4. Begin assessment system development"
