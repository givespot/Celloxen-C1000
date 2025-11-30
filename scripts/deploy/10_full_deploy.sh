#!/bin/bash
# Script 10: Full Deploy
# One-command deployment script that runs all steps

set -e

echo "=========================================="
echo "    Celloxen Full Deployment Script"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
export DOMAIN="${DOMAIN:-celloxen.com}"
export EMAIL="${EMAIL:-admin@celloxen.com}"
export DB_NAME="${DB_NAME:-celloxen_db}"
export DB_USER="${DB_USER:-celloxen_user}"
export BRANCH="${BRANCH:-main}"
export WORKERS="${WORKERS:-4}"

echo "Configuration:"
echo "  Domain: $DOMAIN"
echo "  Email: $EMAIL"
echo "  Database: $DB_NAME"
echo "  Branch: $BRANCH"
echo "  Workers: $WORKERS"
echo ""

read -p "Continue with deployment? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

START_TIME=$(date +%s)

echo ""
echo "=========================================="
echo "Step 1/8: Setting up environment..."
echo "=========================================="
bash $SCRIPT_DIR/1_setup_environment.sh

echo ""
echo "=========================================="
echo "Step 2/8: Setting up database..."
echo "=========================================="
bash $SCRIPT_DIR/2_setup_database.sh

echo ""
echo "=========================================="
echo "Step 3/8: Installing application..."
echo "=========================================="
bash $SCRIPT_DIR/3_install_application.sh

echo ""
echo "=========================================="
echo "Step 4/8: Configuring Nginx..."
echo "=========================================="
bash $SCRIPT_DIR/4_configure_nginx.sh

echo ""
echo "=========================================="
echo "Step 5/8: Configuring Supervisor..."
echo "=========================================="
bash $SCRIPT_DIR/5_configure_supervisor.sh

echo ""
echo "=========================================="
echo "Step 6/8: Setting up SSL..."
echo "=========================================="
read -p "Setup SSL now? (yes/no): " SETUP_SSL
if [ "$SETUP_SSL" == "yes" ]; then
    bash $SCRIPT_DIR/6_setup_ssl.sh
else
    echo "Skipping SSL setup (run 6_setup_ssl.sh later)"
fi

echo ""
echo "=========================================="
echo "Step 7/8: Setting up backups..."
echo "=========================================="
bash $SCRIPT_DIR/7_setup_backup.sh

echo ""
echo "=========================================="
echo "Step 8/8: Running health check..."
echo "=========================================="
bash $SCRIPT_DIR/8_health_check.sh

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo "    Deployment Complete!"
echo "=========================================="
echo ""
echo "Duration: $DURATION seconds"
echo "URL: http://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  Check status: supervisorctl status celloxen-all:*"
echo "  View logs: tail -f /var/log/celloxen/error.log"
echo "  Restart: supervisorctl restart celloxen-all:*"
echo "  Backup: /usr/local/bin/celloxen-backup.sh"
echo "  Rollback: $SCRIPT_DIR/9_rollback.sh"
echo ""
echo "=========================================="
