@echo off
echo Installing A3 Document Automation...
echo.

:: Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\A3_Automation
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy executable
copy "A3_Automation.exe" "%INSTALL_DIR%\A3_Automation.exe"

:: Create desktop shortcut
set DESKTOP=%USERPROFILE%\Desktop
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\A3 Automation.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\A3_Automation.exe'; $Shortcut.Save()"

echo.
echo ✅ Installation complete!
echo Desktop shortcut created.
echo.
pause