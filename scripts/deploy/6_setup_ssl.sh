#!/bin/bash
# Script 6: Setup SSL
# Configures Let's Encrypt SSL certificates

set -e

echo "=== Celloxen SSL Setup ==="

DOMAIN="${DOMAIN:-celloxen.com}"
EMAIL="${EMAIL:-admin@celloxen.com}"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

echo "[1/3] Obtaining SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL

echo "[2/3] Setting up auto-renewal..."
cat > /etc/cron.d/certbot-renewal << EOF
0 0,12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

echo "[3/3] Testing SSL configuration..."
nginx -t && systemctl reload nginx

echo ""
echo "=== SSL setup complete ==="
echo "Site available at: https://$DOMAIN"
echo ""
echo "Certificate will auto-renew before expiry"
echo ""
echo "Next: Run 7_setup_backup.sh"
