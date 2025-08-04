#!/usr/bin/env python3
"""
Build script for creating A3 Document Automation executable
Run this script to create a standalone .exe file for distribution
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_executable():
    """Build the A3 Automation executable using PyInstaller"""
    
    print("🚀 Building A3 Document Automation Executable...")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path(__file__).parent
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")
    
    # Define paths and files to include
    main_file = "main_launcher.py"
    app_name = "A3_Automation"
    
    # Files and folders to include in the executable
    add_data = [
        ("A3_templates", "A3_templates"),
        ("processed_documents", "processed_documents"),  # ← CRITICAL: Contains A3_Custom_Template.pdf
        ("custom_field_positions.json", "."),
        ("app_config.json", "."),                        # ← App configuration settings
        ("version.txt", "."),
        ("a3_template_processor.py", "."),
        ("a3_sectioned_automation.py", "."),
        ("sectioned_gpt4o_ocr.py", "."),
        ("section_definition_tool.py", "."),
        ("field_positioning_tool.py", "."),
        ("create_pdf_template.py", "."),
        ("manual_page_order_tool.py", "."),              # ← Manual page ordering tool
        ("setup_api_key.py", "."),                       # ← API key setup script
    ]
    
    # Check if main file exists
    if not (current_dir / main_file).exists():
        print(f"❌ Main file {main_file} not found!")
        return False
    
    # Build PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",  # Use python -m PyInstaller instead of direct pyinstaller
        "--onefile",                    # Single executable file
        # "--windowed",                 # Commented out to show console for debugging
        "--name", app_name,             # Name of the executable
        "--icon", "icon.ico",           # App icon (if exists)
        "--clean",                      # Clean PyInstaller cache
    ]
    
    # Add data files
    for src, dst in add_data:
        if (current_dir / src).exists():
            cmd.extend(["--add-data", f"{src};{dst}"])
            print(f"📁 Including: {src}")
        else:
            print(f"⚠️  Warning: {src} not found, skipping...")
    
    # Add hidden imports for common modules
    hidden_imports = [
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "PIL",
        "fitz",
        "requests",
        "openai",
    ]
    
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])
    
    # Add main file
    cmd.append(main_file)
    
    print("\n🔨 Building executable...")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, cwd=current_dir, check=True)
        
        if result.returncode == 0:
            print("\n✅ Build successful!")
            
            # Check if executable was created
            exe_path = current_dir / "dist" / f"{app_name}.exe"
            if exe_path.exists():
                exe_size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
                print(f"📦 Executable created: {exe_path}")
                print(f"📏 Size: {exe_size:.1f} MB")
                
                # Create distribution folder
                dist_folder = current_dir / "A3_Distribution"
                if dist_folder.exists():
                    shutil.rmtree(dist_folder)
                dist_folder.mkdir()
                
                # Copy executable
                shutil.copy2(exe_path, dist_folder / f"{app_name}.exe")
                
                # Create installer batch file
                installer_content = f"""@echo off
echo Installing A3 Document Automation...
echo.

:: Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\\A3_Automation
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy executable
copy "{app_name}.exe" "%INSTALL_DIR%\\{app_name}.exe"

:: Create desktop shortcut
set DESKTOP=%USERPROFILE%\\Desktop
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\\A3 Automation.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\{app_name}.exe'; $Shortcut.Save()"

echo.
echo ✅ Installation complete!
echo Desktop shortcut created.
echo.
pause
"""
                
                installer_path = dist_folder / "install_a3.bat"
                installer_path.write_text(installer_content)
                
                # Create README
                readme_content = f"""# A3 Document Automation - Distribution Package

## Installation Instructions:

1. **Simple Installation:**
   - Double-click `install_a3.bat`
   - This will install the application and create a desktop shortcut

2. **Manual Installation:**
   - Copy `{app_name}.exe` to your desired location
   - Run the executable directly

## Features:
- Automatic document processing with GPT-4o OCR
- Custom PDF template generation
- Interactive field positioning
- Auto-update functionality

## System Requirements:
- Windows 10 or later
- Internet connection (for OCR and updates)
- OpenAI API key

## Support:
For support or issues, contact the development team.

Built on: {subprocess.run(['date', '/t'], capture_output=True, text=True, shell=True).stdout.strip()}
Version: {Path('version.txt').read_text().strip() if Path('version.txt').exists() else '1.0.0'}
"""
                
                readme_path = dist_folder / "README.txt"
                readme_path.write_text(readme_content)
                
                print(f"\n📁 Distribution package created: {dist_folder}")
                print(f"   - {app_name}.exe")
                print(f"   - install_a3.bat")
                print(f"   - README.txt")
                
                print(f"\n🎉 Ready for distribution!")
                print(f"Share the contents of '{dist_folder}' with your users.")
                
                return True
            else:
                print("❌ Executable not found after build")
                return False
        else:
            print("❌ Build failed")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def clean_build_files():
    """Clean up PyInstaller build files"""
    print("\n🧹 Cleaning up build files...")
    
    cleanup_dirs = ["build", "dist", "__pycache__"]
    cleanup_files = ["*.spec"]
    
    current_dir = Path(__file__).parent
    
    for dir_name in cleanup_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_name}/")
    
    # Remove .spec files
    for spec_file in current_dir.glob("*.spec"):
        spec_file.unlink()
        print(f"   Removed: {spec_file.name}")
    
    print("✅ Cleanup complete")

if __name__ == "__main__":
    print("A3 Document Automation - Build Script")
    print("====================================")
    
    # Ask user what to do
    while True:
        print("\nChoose an option:")
        print("1. Build executable")
        print("2. Clean build files")
        print("3. Build and clean")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            build_executable()
            break
        elif choice == "2":
            clean_build_files()
            break
        elif choice == "3":
            if build_executable():
                input("\nPress Enter to clean build files...")
                clean_build_files()
            break
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")