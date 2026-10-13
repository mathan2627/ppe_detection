@echo off
echo ========================================
echo PPE Detection System - Start
echo ========================================
echo.

echo Starting Backend...
start "Backend" cmd /k "cd backend && python app.py"

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
echo PPE Detection: Helmet, Vest, Boots, Mask, Gloves, Shoes, Goggles, Glasses, Apron
echo Normal Detection: 80 common objects
echo.
pause
