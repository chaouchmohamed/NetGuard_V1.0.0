@echo off
REM NetGuard Development Runner for Windows
echo =========================================
echo   Starting NetGuard Development Server
echo =========================================

REM Start Backend
echo 🚀 Starting Backend server...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first
    exit /b 1
)

REM Activate virtual environment and start backend
start /B cmd /c "call venv\Scripts\activate && uvicorn main:app --reload --port 8000 --host 0.0.0.0"

cd ..

REM Wait a moment for backend to initialize
timeout /t 2 /nobreak >nul

REM Start Frontend
echo 🚀 Starting Frontend server...
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo ❌ Node modules not found. Please run setup.bat first
    exit /b 1
)

REM Start frontend
start /B cmd /c "npm run dev"

cd ..

echo.
echo ✅ NetGuard is running!
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
echo.

pause >nul

echo 🛑 Shutting down NetGuard...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo ✅ NetGuard stopped.
