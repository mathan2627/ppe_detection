@echo off
echo ========================================
echo Push to GitHub
echo ========================================
echo.

echo [1/5] Adding remote...
git remote add origin https://github.com/MRdivine17/PO1-PPE-DETECTION.git 2>nul
if %errorlevel% neq 0 (
    echo Remote already exists, updating...
    git remote set-url origin https://github.com/MRdivine17/PO1-PPE-DETECTION.git
)

echo.
echo [2/5] Adding files...
git add .

echo.
echo [3/5] Committing...
git commit -m "Initial commit: PPE Detection System"

echo.
echo [4/5] Setting branch to main...
git branch -M main

echo.
echo [5/5] Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done!
echo ========================================
echo.
echo Repository: https://github.com/MRdivine17/PO1-PPE-DETECTION
echo.
pause
