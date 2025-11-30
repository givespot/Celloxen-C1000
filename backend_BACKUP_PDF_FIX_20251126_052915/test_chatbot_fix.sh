#!/bin/bash

echo "🤖 CHATBOT RESPONSIVENESS FIX"
echo "==============================="
echo ""

echo "STEP 1: Test Backend API"
echo "-------------------------"
echo "First, let's verify the backend is working..."
echo ""

# Test backend
systemctl status celloxen-backend

echo ""
echo "Testing chatbot session start..."

curl -X POST http://localhost:5001/api/v1/chatbot/sessions/start \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 18}' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "If this shows a session_id and greeting, the backend is working correctly."
echo ""

echo "STEP 2: Frontend Fix Location"
echo "------------------------------"
echo "The frontend file we need to fix is likely at:"
echo "/var/www/celloxen-portal-new/frontend/index.html"
echo ""
echo "Or it might be in:"
echo "/var/www/celloxen-portal/frontend/index.html"
echo ""

echo "Let's check both locations..."

if [ -f "/var/www/celloxen-portal-new/frontend/index.html" ]; then
    echo "✅ Found: /var/www/celloxen-portal-new/frontend/index.html"
    FRONTEND_PATH="/var/www/celloxen-portal-new/frontend/index.html"
else
    echo "❌ Not found: /var/www/celloxen-portal-new/frontend/index.html"
fi

if [ -f "/var/www/celloxen-portal/frontend/index.html" ]; then
    echo "✅ Found: /var/www/celloxen-portal/frontend/index.html"
    if [ -z "$FRONTEND_PATH" ]; then
        FRONTEND_PATH="/var/www/celloxen-portal/frontend/index.html"
    fi
else
    echo "❌ Not found: /var/www/celloxen-portal/frontend/index.html"
fi

if [ -n "$FRONTEND_PATH" ]; then
    echo ""
    echo "Using frontend file: $FRONTEND_PATH"
    echo ""
    
    echo "Searching for chatbot implementation..."
    grep -n "chatbot\|sendMessage\|processing your message" "$FRONTEND_PATH" | head -5
    
    echo ""
    echo "File size and location:"
    ls -lh "$FRONTEND_PATH"
else
    echo ""
    echo "❌ Could not find frontend file. Please check the correct path."
    echo ""
    echo "Let's check what's in /var/www/:"
    ls -la /var/www/
fi

