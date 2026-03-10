#!/bin/bash

# NetGuard Setup Script for Linux/Mac
echo "========================================="
echo "  NetGuard - Network Attack Detection"
echo "  Setup Script"
echo "========================================="

# Check Python version
echo "🔍 Checking Python version..."
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo "✅ Found $python_version"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Check Node.js version
echo "🔍 Checking Node.js version..."
if command -v node &>/dev/null; then
    node_version=$(node --version)
    echo "✅ Found Node.js $node_version"
else
    echo "❌ Node.js not found. Please install Node.js 16 or higher"
    exit 1
fi

# Setup Backend
echo ""
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
echo "   Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "   Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "   Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Train ML model
echo "   Training ML model..."
python models/train_model.py

# Create logs directory
mkdir -p logs

cd ..

echo "✅ Backend setup complete!"
echo ""

# Setup Frontend
echo "📦 Setting up Frontend..."
cd frontend

# Install Node dependencies
echo "   Installing Node dependencies..."
npm install

cd ..

echo "✅ Frontend setup complete!"
echo ""

# Create sample data directory
mkdir -p sample_data

echo "========================================="
echo "✅ Setup Complete!"
echo ""
echo "To start NetGuard:"
echo "  ./scripts/run_dev.sh"
echo ""
echo "Or manually:"
echo "  Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================="
