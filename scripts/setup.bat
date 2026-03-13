@echo off
REM NetGuard Setup Script for Windows
echo =========================================
echo   NetGuard - Network Attack Detection
echo   Setup Script
echo =========================================

REM Check Python version
echo 🔍 Checking Python version...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo ✅ Found Python
) else (
    echo ❌ Python not found. Please install Python 3.8 or higher
    exit /b 1
)

REM Check Node.js version
echo 🔍 Checking Node.js version...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    node --version
    echo ✅ Found Node.js
) else (
    echo ❌ Node.js not found. Please install Node.js 16 or higher
    exit /b 1
)

REM Setup Backend
echo.
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment
echo    Creating virtual environment...
python -m venv venv

REM Install Python dependencies
echo    Installing Python dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Train ML model
echo    Training ML model...
python models\train_model.py

REM Create logs directory
mkdir logs 2>nul

cd ..

echo ✅ Backend setup complete!
echo.

REM Setup Frontend
echo 📦 Setting up Frontend...
cd frontend

REM Install Node dependencies
echo    Installing Node dependencies...
call npm install

cd ..

echo ✅ Frontend setup complete!
echo.

REM Create sample data directory
mkdir sample_data 2>nul

echo =========================================
echo ✅ Setup Complete!
echo.
echo To start NetGuard:
echo   scripts\run_dev.bat
echo.
echo Or manually:
echo   Backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload --port 8000
echo   Frontend: cd frontend ^&^& npm run dev
echo.
echo Access the application:
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo =========================================
