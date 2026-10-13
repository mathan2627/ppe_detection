@echo off
echo ========================================
echo PPE Detection - Start (Virtual Env)
echo ========================================
echo.

if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found in backend
    echo Run: fix_torchvision.bat first
    pause
    exit /b 1
)

echo Starting Backend (with venv)...
start "Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && python app.py"

timeout /t 5

echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo System Running!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
pause
