#!/bin/bash

echo "==================================="
echo "NetGuard Status Check"
echo "==================================="

# Check if backend is running
if lsof -ti:8000 > /dev/null; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend is NOT running"
fi

# Check if frontend is running
if lsof -ti:5173 > /dev/null; then
    echo "✅ Frontend is running on port 5173"
else
    echo "❌ Frontend is NOT running"
fi

# Test backend health
cd ~/Documents/netguard/backend
source venv/bin/activate
python3 -c "import requests; 
try:
    r = requests.get('http://localhost:8000/health', timeout=2)
    print(f'✅ Backend health: {r.json()}')
except:
    print('❌ Cannot connect to backend')" 2>/dev/null

echo "==================================="
