@echo off
echo ========================================
echo Installing Dependencies
echo ========================================
echo.

echo [1/3] Installing Backend Dependencies...
cd backend
pip install flask flask-cors ultralytics opencv-python pymongo numpy Pillow reportlab
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo.

echo [2/3] Installing PyTorch (CPU version)...
pip install torch torchvision torchaudio
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)
cd ..
echo.

echo [3/3] Installing Frontend Dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next: Run start.bat to launch the system
echo.
echo NOTE: This installed CPU version of PyTorch
echo For GPU support, run: install_gpu.bat
echo.
pause
