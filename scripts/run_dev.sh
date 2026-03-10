#!/bin/bash

# NetGuard Development Runner
echo "========================================="
echo "  Starting NetGuard Development Server"
echo "========================================="

# Function to kill processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down NetGuard..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

# Start Backend
echo "🚀 Starting Backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first"
    exit 1
fi

# Activate virtual environment and start backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

cd ..

# Wait a moment for backend to initialize
sleep 2

# Start Frontend
echo "🚀 Starting Frontend server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Please run setup.sh first"
    exit 1
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ NetGuard is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
