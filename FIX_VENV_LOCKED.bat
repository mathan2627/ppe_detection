@echo off
color 0C
title Fix Locked Virtual Environment

echo ================================================================================
echo FIX LOCKED VIRTUAL ENVIRONMENT
echo ================================================================================
echo.
echo This will help fix the "file is being used" error
echo.
pause

echo.
echo Step 1: Closing Python processes...
echo.

REM Kill any python processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

echo Done.
echo.

echo Step 2: Waiting for processes to close...
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Attempting to remove locked venv...
echo.

if exist "backend\venv" (
    rmdir /s /q backend\venv 2>nul
    
    if exist "backend\venv" (
        echo.
        echo ERROR: Still cannot remove venv
        echo.
        echo Please:
        echo   1. Close ALL Command Prompt windows
        echo   2. Close ALL Python applications
        echo   3. Restart your computer
        echo   4. Run 1_INSTALL_EVERYTHING.bat again
        echo.
    ) else (
        echo.
        echo SUCCESS: Old venv removed!
        echo.
        echo Now run: 1_INSTALL_EVERYTHING.bat
        echo.
    )
) else (
    echo.
    echo No venv found. You can run: 1_INSTALL_EVERYTHING.bat
    echo.
)

pause
