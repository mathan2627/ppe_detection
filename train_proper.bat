@echo off
echo ========================================
echo Optimized PPE Model Training
echo ========================================
echo.
echo Configuration:
echo   - Epochs: 25-30 (MID-RANGE)
echo   - Model: YOLOv8s (good accuracy)
echo   - Time: 15-25 minutes on 8GB+ GPU
echo   - Quality: EXCELLENT for production
echo.

if not exist "backend\venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
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

echo.
echo ========================================
echo Checking Hardware...
echo ========================================
%PYTHON% -c "import torch; print('PyTorch:', torch.__version__); cuda = torch.cuda.is_available(); print('CUDA:', cuda); print('Device:', torch.cuda.get_device_name(0) if cuda else 'CPU'); print('Memory:', f'{torch.cuda.get_device_properties(0).total_memory/1024**3:.1f}GB' if cuda else 'N/A'); print(); print('Status:', 'READY FOR GPU TRAINING' if cuda and '+cu' in torch.__version__ else 'WARNING: CPU-only PyTorch detected')"

echo.
echo ========================================
echo Verifying Ultralytics...
echo ========================================
%PYTHON% -c "from ultralytics import YOLO; print('✓ Ultralytics installed and working')"

if errorlevel 1 (
    echo.
    echo ERROR: Ultralytics not found!
    echo Installing ultralytics...
    %PYTHON% -m pip install ultralytics
)

echo.
echo ========================================
echo Starting Optimized Training...
echo ========================================
echo.
echo This will train with:
echo   ✓ Mid-range epochs (25-30)
echo   ✓ Optimal balance of speed and accuracy
echo   ✓ No over-fitting
echo   ✓ Production-ready model
echo.
echo Estimated time: 15-25 minutes on 8GB+ GPU
echo.
pause

%PYTHON% train_ppe_proper.py

cd ..

echo.
echo ========================================
echo Training Complete!
echo ========================================
echo.
echo Model saved to: backend/runs/detect/ppe_detection/weights/best.pt
echo.
echo Next: Run your application to test the model
echo Check: backend/runs/detect/ppe_detection/ for training plots
echo.
pause
