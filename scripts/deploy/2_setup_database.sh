#!/bin/bash
# Script 2: Setup Database
# Creates PostgreSQL database and user for Celloxen

set -e

echo "=== Celloxen Database Setup ==="

# Configuration
DB_NAME="${DB_NAME:-celloxen_db}"
DB_USER="${DB_USER:-celloxen_user}"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 32)}"

# Check if running as root or postgres user
if [ "$EUID" -ne 0 ] && [ "$(whoami)" != "postgres" ]; then
    echo "Please run as root (sudo) or postgres user"
    exit 1
fi

echo "[1/4] Creating database user..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "User may already exist"

echo "[2/4] Creating database..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || echo "Database may already exist"

echo "[3/4] Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "[4/4] Saving credentials..."
cat > /etc/celloxen/database.env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
EOF

chmod 600 /etc/celloxen/database.env
chown celloxen:celloxen /etc/celloxen/database.env

echo ""
echo "=== Database setup complete ==="
echo "Credentials saved to /etc/celloxen/database.env"
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""
echo "Next: Run 3_install_application.sh"
