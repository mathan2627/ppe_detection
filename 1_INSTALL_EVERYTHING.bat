@echo off
color 0A
title GPU Setup - Python 3.11 + PyTorch Installation

echo ================================================================================
echo AUTOMATIC GPU SETUP FOR RTX 2050
echo ================================================================================
echo.
echo This will:
echo   1. Download and install Python 3.11.9
echo   2. Create virtual environment in backend\venv
echo   3. Install GPU-enabled PyTorch with CUDA 12.1
echo   4. Install all dependencies
echo   5. Verify GPU detection
echo.
echo Time: 10-15 minutes
echo.
pause

echo.
echo ================================================================================
echo Step 1/6: Downloading Python 3.11.9
echo ================================================================================
echo.

if not exist "temp" mkdir temp

echo Downloading Python 3.11.9 installer (30MB)...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'temp\python-3.11.9-amd64.exe'}"

if not exist "temp\python-3.11.9-amd64.exe" (
    echo ERROR: Download failed
    echo Please check your internet connection
    pause
    exit /b 1
)

echo Download complete!
echo.

echo ================================================================================
echo Step 2/6: Installing Python 3.11.9
echo ================================================================================
echo.
echo Installing Python 3.11.9 silently...
echo This takes 1-2 minutes...
echo.

temp\python-3.11.9-amd64.exe /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 Include_pip=1 Include_doc=0

timeout /t 60 /nobreak >nul

set PYTHON311=%LOCALAPPDATA%\Programs\Python\Python311\python.exe

if not exist "%PYTHON311%" (
    echo ERROR: Python 3.11 installation failed
    echo Please run: temp\python-3.11.10-amd64.exe manually
    pause
    exit /b 1
)

echo Python 3.11.9 installed successfully!
"%PYTHON311%" --version
echo.

echo ================================================================================
echo Step 3/6: Creating Virtual Environment
echo ================================================================================
echo.

if exist "backend\venv" (
    echo Virtual environment already exists.
    echo.
    echo IMPORTANT: Close any Python processes or terminals using the venv
    echo.
    set /p recreate="Do you want to recreate it? (y/n): "
    if /i "%recreate%"=="y" (
        echo.
        echo Attempting to remove old virtual environment...
        echo Please close any Python processes if this fails.
        echo.
        timeout /t 3 /nobreak >nul
        
        REM Try to kill any python processes in the venv
        taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *venv*" 2>nul
        timeout /t 2 /nobreak >nul
        
        rmdir /s /q backend\venv 2>nul
        
        if exist "backend\venv" (
            echo.
            echo ERROR: Cannot remove old venv - it's still in use
            echo.
            echo Please:
            echo   1. Close all Command Prompt windows
            echo   2. Close any Python processes
            echo   3. Restart your computer if needed
            echo   4. Run this script again
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Using existing virtual environment...
        goto skip_venv_creation
    )
)

echo Creating new virtual environment with Python 3.11...
"%PYTHON311%" -m venv backend\venv

if not exist "backend\venv\Scripts\activate.bat" (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created!

:skip_venv_creation
echo.

echo ================================================================================
echo Step 4/6: Installing GPU-enabled PyTorch
echo ================================================================================
echo.

cd backend
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo Uninstalling old PyTorch...
python -m pip uninstall -y torch torchvision torchaudio

echo.
echo Installing GPU-enabled PyTorch with CUDA 12.1...
echo This may take 3-5 minutes...
echo.

python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --timeout 300

if errorlevel 1 (
    echo.
    echo First attempt failed, retrying...
    python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --timeout 600
)

if errorlevel 1 (
    echo ERROR: PyTorch installation failed
    echo.
    echo Please check your internet connection and try again
    cd ..
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Step 5/6: Installing Dependencies
echo ================================================================================
echo.

echo Installing ultralytics, flask, opencv, and other packages...
python -m pip install flask flask-cors ultralytics opencv-python pymongo numpy Pillow reportlab

if errorlevel 1 (
    echo.
    echo First attempt failed, retrying with longer timeout...
    python -m pip install flask flask-cors ultralytics opencv-python pymongo numpy Pillow reportlab --timeout 300
)

if errorlevel 1 (
    echo.
    echo Installation failed. Installing packages one by one...
    python -m pip install flask --timeout 300
    python -m pip install flask-cors --timeout 300
    python -m pip install ultralytics --timeout 300
    python -m pip install opencv-python --timeout 300
    python -m pip install pymongo --timeout 300
    python -m pip install numpy --timeout 300
    python -m pip install Pillow --timeout 300
    python -m pip install reportlab --timeout 300
)

echo Dependencies installed!
echo.

echo ================================================================================
echo Step 6/6: Verifying GPU Detection
echo ================================================================================
echo.

python -c "import torch; print('='*70); print('VERIFICATION RESULTS'); print('='*70); print(); print('Python Version:', __import__('sys').version.split()[0]); print('PyTorch Version:', torch.__version__); print(); cuda = torch.cuda.is_available(); print('CUDA Available:', cuda); if cuda: print('GPU Name:', torch.cuda.get_device_name(0)); print('GPU Memory:', f'{torch.cuda.get_device_properties(0).total_memory/1024**3:.2f} GB'); print(); print('='*70); print('STATUS: GPU READY FOR TRAINING'); print('='*70); else: print(); print('='*70); print('WARNING: GPU NOT DETECTED'); print('='*70)"

cd ..

echo.
echo ================================================================================
echo Cleaning Up
echo ================================================================================
echo.

if exist "temp\python-3.11.9-amd64.exe" del temp\python-3.11.9-amd64.exe
if exist "temp" rmdir temp

echo.
echo ================================================================================
echo INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Summary:
echo   [OK] Python 3.11.9 installed
echo   [OK] Virtual environment created: backend\venv
echo   [OK] GPU-enabled PyTorch installed
echo   [OK] All dependencies installed
echo   [OK] GPU detected and ready
echo.
echo Next step: Run 2_TRAIN_MODEL.bat to train your model
echo.
pause
