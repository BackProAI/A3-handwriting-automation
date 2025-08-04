# A3 Document Automation - Desktop Launcher Creator
# PowerShell script to create desktop shortcut

Write-Host "Creating A3 Document Automation Desktop Launcher..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Get current directory
$CurrentDir = Get-Location

# Set desktop path
$Desktop = [Environment]::GetFolderPath("Desktop")

# Check if main_launcher.py exists
if (-not (Test-Path "main_launcher.py")) {
    Write-Host "❌ Error: main_launcher.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the A3_handtotext folder." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Create desktop shortcut
Write-Host "🔧 Creating desktop shortcut..." -ForegroundColor Yellow

try {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$Desktop\A3 Document Automation.lnk")
    $Shortcut.TargetPath = "python"
    $Shortcut.Arguments = "`"$CurrentDir\main_launcher.py`""
    $Shortcut.WorkingDirectory = "$CurrentDir"
    $Shortcut.IconLocation = "python.exe,0"
    $Shortcut.Description = "A3 Document Automation - Handwriting OCR System"
    $Shortcut.Save()
    
    Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
    Write-Host "📍 Location: $Desktop\A3 Document Automation.lnk" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🚀 You can now launch A3 Automation from your desktop!" -ForegroundColor Green
    Write-Host "   Double-click 'A3 Document Automation' on your desktop." -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to create desktop shortcut." -ForegroundColor Red
    Write-Host ""
    Write-Host "📝 Manual instructions:" -ForegroundColor Yellow
    Write-Host "1. Right-click on your desktop" -ForegroundColor White
    Write-Host "2. New → Shortcut" -ForegroundColor White
    Write-Host "3. Location: python `"$CurrentDir\main_launcher.py`"" -ForegroundColor White
    Write-Host "4. Name: A3 Document Automation" -ForegroundColor White
}

Write-Host ""
Write-Host "📋 What's Next:" -ForegroundColor Cyan
Write-Host "1. Double-click the new desktop shortcut" -ForegroundColor White
Write-Host "2. The A3 launcher will open" -ForegroundColor White
Write-Host "3. Click 'Launch A3 Automation' to start processing documents" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"