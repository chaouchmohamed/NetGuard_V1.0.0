#!/bin/bash

echo "========================================="
echo "  Starting NetGuard Development Server"
echo "========================================="

cleanup() {
    echo ""
    echo "🛑 Shutting down NetGuard..."
    sudo kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# ─── Backend ───────────────────────────────────────────────
echo "🚀 Starting Backend server..."
cd backend

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first"
    exit 1
fi

source venv/bin/activate

# Auto-detect network interface if not already set
if [ -z "$NETGUARD_INTERFACE" ]; then
    NETGUARD_INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
    echo "📡 Auto-detected interface: $NETGUARD_INTERFACE"
else
    echo "📡 Using interface: $NETGUARD_INTERFACE"
fi

VENV_PYTHON=$(pwd)/venv/bin/python

echo "⚠️  Backend requires sudo for raw packet capture (scapy)"
NETGUARD_INTERFACE=$NETGUARD_INTERFACE sudo -E "$VENV_PYTHON" main.py &
BACKEND_PID=$!

cd ..
sleep 2

# ─── Frontend ──────────────────────────────────────────────
echo "🚀 Starting Frontend server..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Please run setup.sh first"
    exit 1
fi

npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ NetGuard is running!"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "   To use a specific interface:"
echo "   NETGUARD_INTERFACE=eth0 ./scripts/run_dev.sh"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

wait $BACKEND_PID $FRONTEND_PID