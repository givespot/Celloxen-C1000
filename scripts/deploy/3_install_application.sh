#!/bin/bash
# Script 3: Install Application
# Clones repository, sets up Python environment, installs dependencies

set -e

echo "=== Celloxen Application Installation ==="

APP_DIR="/var/www/celloxen"
REPO_URL="${REPO_URL:-https://github.com/givespot/Celloxen-C1000.git}"
BRANCH="${BRANCH:-main}"

# Change to celloxen user
if [ "$(whoami)" != "celloxen" ]; then
    echo "Switching to celloxen user..."
    sudo -u celloxen bash "$0" "$@"
    exit $?
fi

cd $APP_DIR

echo "[1/6] Cloning/updating repository..."
if [ -d "$APP_DIR/.git" ]; then
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    git clone -b $BRANCH $REPO_URL .
fi

echo "[2/6] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[3/6] Upgrading pip..."
pip install --upgrade pip wheel setuptools

echo "[4/6] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
fi

echo "[5/6] Loading environment variables..."
if [ -f "/etc/celloxen/database.env" ]; then
    export $(cat /etc/celloxen/database.env | xargs)
fi

echo "[6/6] Running database migrations..."
if [ -f "backend/alembic.ini" ]; then
    cd backend
    alembic upgrade head
    cd ..
fi

echo ""
echo "=== Application installation complete ==="
echo "Next: Run 4_configure_nginx.sh"
