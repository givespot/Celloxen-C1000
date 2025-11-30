#!/bin/bash
# Script 8: Health Check
# Performs comprehensive health check of all services

set -e

echo "=== Celloxen Health Check ==="
echo ""

DOMAIN="${DOMAIN:-localhost}"
ERRORS=0

check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo "[OK] $service is running"
        return 0
    else
        echo "[FAIL] $service is not running"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_port() {
    local port=$1
    local name=$2
    if netstat -tuln | grep -q ":$port "; then
        echo "[OK] $name (port $port) is listening"
        return 0
    else
        echo "[FAIL] $name (port $port) is not listening"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_url() {
    local url=$1
    local name=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 $url 2>/dev/null)
    if [ "$response" == "200" ]; then
        echo "[OK] $name is responding (HTTP $response)"
        return 0
    else
        echo "[FAIL] $name returned HTTP $response"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

echo "--- System Services ---"
check_service nginx
check_service postgresql
check_service redis-server
check_service supervisor

echo ""
echo "--- Network Ports ---"
check_port 80 "HTTP"
check_port 443 "HTTPS"
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"
check_port 8000 "Application"

echo ""
echo "--- Application Status ---"
supervisorctl status celloxen-all:* 2>/dev/null || echo "[WARN] Supervisor not configured"

echo ""
echo "--- HTTP Endpoints ---"
check_url "http://$DOMAIN/" "Frontend"
check_url "http://$DOMAIN/api/v1/health" "API Health"

echo ""
echo "--- Disk Usage ---"
df -h / | tail -1 | awk '{print "[INFO] Disk usage: " $5 " (" $4 " available)"}'

echo ""
echo "--- Memory Usage ---"
free -h | grep Mem | awk '{print "[INFO] Memory: " $3 " used / " $2 " total"}'

echo ""
echo "--- Recent Logs ---"
echo "Last 5 error log entries:"
tail -5 /var/log/celloxen/error.log 2>/dev/null || echo "No error log found"

echo ""
echo "=== Health Check Complete ==="
if [ $ERRORS -eq 0 ]; then
    echo "Status: ALL CHECKS PASSED"
    exit 0
else
    echo "Status: $ERRORS CHECK(S) FAILED"
    exit 1
fi
