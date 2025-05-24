@echo off
echo ========================================
echo    FitGent 2.0 - GitHub Setup Script
echo ========================================
echo.

echo 1. Initializing Git repository...
git init

echo.
echo 2. Adding all files to Git...
git add .

echo.
echo 3. Creating initial commit...
git commit -m "Initial commit: FitGent 2.0 with smartwatch integration and AI health recommendations"

echo.
echo 4. Setting up main branch...
git branch -M main

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a new repository on GitHub named 'fitgent-2.0'
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_GITHUB_URL
echo 4. Run: git push -u origin main
echo.
echo Example:
echo git remote add origin https://github.com/yourusername/fitgent-2.0.git
echo git push -u origin main
echo.
echo ========================================
echo    Deployment URLs (after GitHub setup)
echo ========================================
echo.
echo Frontend (Vercel): https://fitgent-2.vercel.app
echo Backend (Railway): https://fitgent-backend.railway.app
echo.
echo Follow DEPLOYMENT.md for detailed deployment instructions!
echo.
pause
