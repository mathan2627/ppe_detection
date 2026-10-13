@echo off
echo ========================================
echo Installing torchvision (Virtual Env)
echo ========================================
echo.

if exist "backend\venv\Scripts\activate.bat" (
    echo Using existing virtual environment in backend...
    cd backend
    call venv\Scripts\activate.bat
    echo.
    echo Installing torchvision in backend venv...
    pip install torchvision torchaudio
    cd ..
    echo.
    echo ========================================
    echo Done!
    echo ========================================
    echo.
    echo Torchvision installed in backend/venv
    echo Run: start_venv.bat
) else (
    echo Creating virtual environment in backend...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    echo.
    echo Installing GPU PyTorch with torchvision...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    echo.
    echo Installing other dependencies...
    pip install flask flask-cors ultralytics opencv-python pymongo numpy Pillow reportlab
    cd ..
    echo.
    echo ========================================
    echo Done!
    echo ========================================
    echo.
    echo Virtual environment created in backend/venv
    echo Run: start_venv.bat
)

echo.
pause
