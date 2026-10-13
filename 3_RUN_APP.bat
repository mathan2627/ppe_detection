@echo off
color 0B
title Running PPE Detection Application

echo ================================================================================
echo PPE DETECTION APPLICATION
echo ================================================================================
echo.
echo Starting Flask application...
echo.
echo The application will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if virtual environment exists
if not exist "backend\venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run: 1_INSTALL_EVERYTHING.bat first
    echo.
    pause
    exit /b 1
)

echo Using virtual environment...
cd backend

REM Use python directly from venv
set PYTHON=venv\Scripts\python.exe

echo Starting Flask server...
echo.
%PYTHON% app.py

cd ..
pause
