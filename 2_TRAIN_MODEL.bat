@echo off
color 0B
title Training PPE Detection Model - RTX 2050

echo ================================================================================
echo PPE DETECTION MODEL TRAINING - RTX 2050 (4GB)
echo ================================================================================
echo.
echo Configuration:
echo   - GPU: NVIDIA GeForce RTX 2050 (4GB)
echo   - Model: YOLOv8n (nano - optimized for 4GB)
echo   - Epochs: 25 (mid-range - optimal balance)
echo   - Batch size: 8 (memory efficient)
echo   - Image size: 416 (optimized)
echo   - Training time: 25-40 minutes
echo   - Quality: GOOD (mAP50: 0.65-0.75)
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

REM Use python directly from venv (no need for activate.bat)
set PYTHON=venv\Scripts\python.exe

echo.
echo ================================================================================
echo Verifying Setup
echo ================================================================================
echo.

echo Checking Python version...
%PYTHON% --version

echo.
echo Checking PyTorch and GPU...
%PYTHON% -c "import torch; print('PyTorch:', torch.__version__); cuda = torch.cuda.is_available(); print('CUDA Available:', cuda); print('GPU:', torch.cuda.get_device_name(0) if cuda else 'CPU ONLY'); print('Memory:', f'{torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB' if cuda else 'N/A')"

echo.
echo Checking Ultralytics...
%PYTHON% -c "from ultralytics import YOLO; print('Ultralytics: OK')"

if errorlevel 1 (
    echo ERROR: Ultralytics not found!
    echo Installing ultralytics...
    %PYTHON% -m pip install ultralytics
)

echo.
echo ================================================================================
echo Starting Training
echo ================================================================================
echo.
echo Training will start in 5 seconds...
echo Press Ctrl+C to cancel
echo.
timeout /t 5

%PYTHON% train_model.py

cd ..

echo.
echo ================================================================================
echo TRAINING COMPLETE!
echo ================================================================================
echo.
echo Model location: backend\runs\detect\ppe_detection\weights\best.pt
echo Training plots: backend\runs\detect\ppe_detection\results.png
echo.
echo Your model is ready to use!
echo.
pause
