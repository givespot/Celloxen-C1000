#!/bin/bash
# Script 9: Rollback
# Rolls back to a previous deployment version

set -e

echo "=== Celloxen Rollback ==="

APP_DIR="/var/www/celloxen"
BACKUP_DIR="/var/backups/celloxen"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# List available backups
echo "Available backups:"
echo ""
echo "Database backups:"
ls -la $BACKUP_DIR/database/*.sql.gz 2>/dev/null | tail -10 || echo "  No database backups found"
echo ""
echo "Application backups:"
ls -la $BACKUP_DIR/files/*.tar.gz 2>/dev/null | tail -10 || echo "  No application backups found"
echo ""

# Get user input
read -p "Enter backup date (YYYYMMDD_HHMMSS) or 'git' for git rollback: " BACKUP_DATE

if [ "$BACKUP_DATE" == "git" ]; then
    echo ""
    echo "Recent git commits:"
    cd $APP_DIR
    git log --oneline -10
    echo ""
    read -p "Enter commit hash to rollback to: " COMMIT_HASH

    echo ""
    echo "Rolling back to commit: $COMMIT_HASH"
    read -p "Are you sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Rollback cancelled"
        exit 0
    fi

    echo "[1/4] Stopping application..."
    supervisorctl stop celloxen-all:*

    echo "[2/4] Rolling back git..."
    sudo -u celloxen git checkout $COMMIT_HASH

    echo "[3/4] Installing dependencies..."
    sudo -u celloxen $APP_DIR/venv/bin/pip install -r requirements.txt

    echo "[4/4] Starting application..."
    supervisorctl start celloxen-all:*

else
    DB_BACKUP="$BACKUP_DIR/database/db_$BACKUP_DATE.sql.gz"
    APP_BACKUP="$BACKUP_DIR/files/app_$BACKUP_DATE.tar.gz"

    if [ ! -f "$DB_BACKUP" ] || [ ! -f "$APP_BACKUP" ]; then
        echo "Backup files not found for date: $BACKUP_DATE"
        exit 1
    fi

    echo ""
    echo "Will restore:"
    echo "  Database: $DB_BACKUP"
    echo "  Application: $APP_BACKUP"
    read -p "Are you sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Rollback cancelled"
        exit 0
    fi

    # Load database credentials
    source /etc/celloxen/database.env

    echo "[1/5] Stopping application..."
    supervisorctl stop celloxen-all:*

    echo "[2/5] Creating safety backup..."
    /usr/local/bin/celloxen-backup.sh

    echo "[3/5] Restoring database..."
    gunzip -c $DB_BACKUP | PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER $DB_NAME

    echo "[4/5] Restoring application files..."
    rm -rf $APP_DIR.old
    mv $APP_DIR $APP_DIR.old
    mkdir -p $APP_DIR
    tar -xzf $APP_BACKUP -C /var/www
    chown -R celloxen:celloxen $APP_DIR

    # Restore venv from old installation
    cp -r $APP_DIR.old/venv $APP_DIR/

    echo "[5/5] Starting application..."
    supervisorctl start celloxen-all:*
fi

echo ""
echo "=== Rollback complete ==="
echo "Run ./8_health_check.sh to verify"
