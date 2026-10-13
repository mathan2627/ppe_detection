@echo off
echo ========================================
echo Fresh PPE Model Training (GPU)
echo ========================================
echo.

if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Run: fix_torchvision.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
cd backend
call venv\Scripts\activate.bat

echo.
echo Checking GPU...
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

echo.
echo ========================================
echo Starting Training...
echo ========================================
echo.
echo This will train on your new PPE dataset
echo Using GPU (RTX 3060 Ti)
echo Time: 5-10 minutes
echo.
pause

python train_ppe_fast.py

cd ..

echo.
echo ========================================
echo Training Complete!
echo ========================================
echo.
echo Model saved to: backend/runs/detect/ppe_detection/weights/best.pt
echo.
echo Next: Run start_venv.bat to test the model
echo.
pause
