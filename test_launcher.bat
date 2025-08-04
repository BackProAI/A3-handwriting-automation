@echo off
echo Testing A3 Launcher...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

:: Check if main_launcher.py exists
if not exist "main_launcher.py" (
    echo ❌ main_launcher.py not found!
    pause
    exit /b 1
)

:: Run the launcher
echo ✅ Starting A3 Launcher...
echo.
python main_launcher.py

echo.
echo Launcher closed.
pause