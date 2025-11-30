#!/bin/bash
# Script 7: Setup Backup
# Configures automated backups for database and files

set -e

echo "=== Celloxen Backup Setup ==="

BACKUP_DIR="/var/backups/celloxen"
RETENTION_DAYS=30

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

echo "[1/3] Creating backup directories..."
mkdir -p $BACKUP_DIR/{database,files,logs}
chown -R celloxen:celloxen $BACKUP_DIR

echo "[2/3] Creating backup script..."
cat > /usr/local/bin/celloxen-backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/var/backups/celloxen"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Load database credentials
source /etc/celloxen/database.env

echo "Starting backup: $DATE"

# Database backup
echo "Backing up database..."
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/database/db_$DATE.sql.gz

# Application files backup
echo "Backing up application files..."
tar -czf $BACKUP_DIR/files/app_$DATE.tar.gz -C /var/www celloxen --exclude='venv' --exclude='__pycache__' --exclude='.git'

# Logs backup
echo "Backing up logs..."
tar -czf $BACKUP_DIR/logs/logs_$DATE.tar.gz -C /var/log celloxen

# Cleanup old backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

# Calculate sizes
DB_SIZE=$(du -sh $BACKUP_DIR/database/db_$DATE.sql.gz | cut -f1)
APP_SIZE=$(du -sh $BACKUP_DIR/files/app_$DATE.tar.gz | cut -f1)

echo "Backup complete!"
echo "  Database: $DB_SIZE"
echo "  Application: $APP_SIZE"
echo "  Location: $BACKUP_DIR"
EOF

chmod +x /usr/local/bin/celloxen-backup.sh

echo "[3/3] Setting up cron job..."
cat > /etc/cron.d/celloxen-backup << EOF
# Daily backup at 2 AM
0 2 * * * root /usr/local/bin/celloxen-backup.sh >> /var/log/celloxen/backup.log 2>&1
EOF

echo ""
echo "=== Backup setup complete ==="
echo ""
echo "Manual backup: sudo /usr/local/bin/celloxen-backup.sh"
echo "Backup location: $BACKUP_DIR"
echo "Retention: $RETENTION_DAYS days"
echo ""
echo "Next: Run 8_health_check.sh"
