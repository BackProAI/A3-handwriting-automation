@echo off
echo Creating A3 Document Automation Desktop Launcher...
echo ================================================

:: Get current directory
set CURRENT_DIR=%cd%

:: Set desktop path
set DESKTOP=%USERPROFILE%\Desktop

:: Check if main_launcher.py exists
if not exist "main_launcher.py" (
    echo ❌ Error: main_launcher.py not found!
    echo Please run this script from the A3_handtotext folder.
    echo.
    pause
    exit /b 1
)

:: Create desktop shortcut using PowerShell
echo 🔧 Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\A3 Document Automation.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%CURRENT_DIR%\main_launcher.py\"'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.IconLocation = 'python.exe,0'; $Shortcut.Description = 'A3 Document Automation - Handwriting OCR System'; $Shortcut.Save()"

:: Check if shortcut was created
if exist "%DESKTOP%\A3 Document Automation.lnk" (
    echo ✅ Desktop shortcut created successfully!
    echo 📍 Location: %DESKTOP%\A3 Document Automation.lnk
    echo.
    echo 🚀 You can now launch A3 Automation from your desktop!
    echo    Double-click "A3 Document Automation" on your desktop.
) else (
    echo ❌ Failed to create desktop shortcut.
    echo.
    echo 📝 Manual instructions:
    echo 1. Right-click on your desktop
    echo 2. New → Shortcut
    echo 3. Location: python "%CURRENT_DIR%\main_launcher.py"
    echo 4. Name: A3 Document Automation
)

echo.
echo 📋 What's Next:
echo 1. Double-click the new desktop shortcut
echo 2. The A3 launcher will open
echo 3. Click "Launch A3 Automation" to start processing documents
echo.
pause