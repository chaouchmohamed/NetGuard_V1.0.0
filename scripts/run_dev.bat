@echo off
echo =========================================
echo   Starting NetGuard Development Server
echo =========================================

:: ─── Check for admin privileges ───────────────────────────
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] This script requires Administrator privileges.
    echo Right-click run_dev.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: ─── Backend ───────────────────────────────────────────────
echo [*] Starting Backend server...
cd backend

if not exist "venv\" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first
    pause
    exit /b 1
)

:: Set interface — change this to match your adapter name
:: Run 'ipconfig' to find your adapter name (e.g. "Wi-Fi", "Ethernet")
if "%NETGUARD_INTERFACE%"=="" (
    set NETGUARD_INTERFACE=Wi-Fi
    echo [*] Using default interface: Wi-Fi
    echo     To change: set NETGUARD_INTERFACE=Ethernet ^&^& run_dev.bat
) else (
    echo [*] Using interface: %NETGUARD_INTERFACE%
)

echo [!] Backend requires Administrator rights for raw packet capture
start "NetGuard Backend" /B venv\Scripts\python.exe main.py

cd ..
timeout /t 2 /nobreak >nul

:: ─── Frontend ──────────────────────────────────────────────
echo [*] Starting Frontend server...
cd frontend

if not exist "node_modules\" (
    echo [ERROR] Node modules not found. Please run setup.bat first
    pause
    exit /b 1
)

start "NetGuard Frontend" /B npm run dev

cd ..

echo.
echo [OK] NetGuard is running!
echo    Frontend:  http://localhost:5173
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo    To use a specific interface:
echo    set NETGUARD_INTERFACE=Ethernet ^&^& run_dev.bat
echo.
echo Press Ctrl+C to stop all servers
echo.

:: Keep window open
:loop
timeout /t 5 /nobreak >nul
goto loop