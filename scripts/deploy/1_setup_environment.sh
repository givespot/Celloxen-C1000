#!/bin/bash
# Script 1: Setup Environment
# Sets up the deployment environment with required dependencies

set -e

echo "=== Celloxen Environment Setup ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Update system packages
echo "[1/6] Updating system packages..."
apt-get update && apt-get upgrade -y

# Install required packages
echo "[2/6] Installing required packages..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    supervisor \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw

# Create application user
echo "[3/6] Creating application user..."
if ! id "celloxen" &>/dev/null; then
    useradd -m -s /bin/bash celloxen
    echo "User 'celloxen' created"
else
    echo "User 'celloxen' already exists"
fi

# Create application directories
echo "[4/6] Creating application directories..."
mkdir -p /var/www/celloxen
mkdir -p /var/log/celloxen
mkdir -p /etc/celloxen
chown -R celloxen:celloxen /var/www/celloxen
chown -R celloxen:celloxen /var/log/celloxen

# Setup firewall
echo "[5/6] Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Enable services
echo "[6/6] Enabling services..."
systemctl enable nginx
systemctl enable postgresql
systemctl enable redis-server
systemctl start postgresql
systemctl start redis-server

echo ""
echo "=== Environment setup complete ==="
echo "Next: Run 2_setup_database.sh"
