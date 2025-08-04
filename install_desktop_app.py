#!/usr/bin/env python3
"""
A3 Document Automation - Desktop App Installer
Creates desktop shortcut and sets up the application for easy access
"""

import os
import sys
import platform
from pathlib import Path
import subprocess

def create_windows_shortcut():
    """Create desktop shortcut on Windows"""
    try:
        import win32com.client
        
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "A3 Document Automation.lnk"
        current_dir = Path(__file__).parent.absolute()
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{current_dir / "main_launcher.py"}"'
        shortcut.WorkingDirectory = str(current_dir)
        shortcut.IconLocation = f"{sys.executable},0"
        shortcut.Description = "A3 Document Automation - Handwriting OCR System"
        shortcut.save()
        
        return True, str(shortcut_path)
        
    except ImportError:
        # Fallback to PowerShell method
        try:
            desktop = Path.home() / "Desktop"
            current_dir = Path(__file__).parent.absolute()
            
            ps_command = f'''
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{desktop}\\A3 Document Automation.lnk")
            $Shortcut.TargetPath = "python"
            $Shortcut.Arguments = '"{current_dir}\\main_launcher.py"'
            $Shortcut.WorkingDirectory = "{current_dir}"
            $Shortcut.IconLocation = "python.exe,0"
            $Shortcut.Description = "A3 Document Automation - Handwriting OCR System"
            $Shortcut.Save()
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )
            
            shortcut_path = desktop / "A3 Document Automation.lnk"
            if shortcut_path.exists():
                return True, str(shortcut_path)
            else:
                return False, "PowerShell shortcut creation failed"
                
        except Exception as e:
            return False, f"PowerShell error: {str(e)}"
    
    except Exception as e:
        return False, f"Windows shortcut error: {str(e)}"

def create_mac_shortcut():
    """Create application shortcut on macOS"""
    try:
        desktop = Path.home() / "Desktop"
        app_path = desktop / "A3 Document Automation.app"
        current_dir = Path(__file__).parent.absolute()
        
        # Create .app bundle structure
        contents_dir = app_path / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        contents_dir.mkdir(parents=True, exist_ok=True)
        macos_dir.mkdir(exist_ok=True)
        resources_dir.mkdir(exist_ok=True)
        
        # Create Info.plist
        info_plist = contents_dir / "Info.plist"
        info_plist.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>A3_Document_Automation</string>
    <key>CFBundleIdentifier</key>
    <string>com.more4life.a3automation</string>
    <key>CFBundleName</key>
    <string>A3 Document Automation</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
</dict>
</plist>""")
        
        # Create executable script
        executable = macos_dir / "A3_Document_Automation"
        executable.write_text(f"""#!/bin/bash
cd "{current_dir}"
python3 main_launcher.py
""")
        executable.chmod(0o755)
        
        return True, str(app_path)
        
    except Exception as e:
        return False, f"macOS shortcut error: {str(e)}"

def create_linux_shortcut():
    """Create desktop shortcut on Linux"""
    try:
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "A3_Document_Automation.desktop"
        current_dir = Path(__file__).parent.absolute()
        
        desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=A3 Document Automation
Comment=Handwriting OCR System
Exec=python3 {current_dir}/main_launcher.py
Icon=applications-python
Path={current_dir}
Terminal=false
StartupNotify=true
Categories=Office;Utility;
"""
        
        shortcut_path.write_text(desktop_entry)
        shortcut_path.chmod(0o755)
        
        return True, str(shortcut_path)
        
    except Exception as e:
        return False, f"Linux shortcut error: {str(e)}"

def install_desktop_app():
    """Main installer function"""
    print("🚀 A3 Document Automation - Desktop App Installer")
    print("=" * 55)
    
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    if not (current_dir / "main_launcher.py").exists():
        print("❌ Error: main_launcher.py not found!")
        print("   Please run this script from the A3_handtotext folder.")
        input("\nPress Enter to exit...")
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("⚠️  Warning: Python 3.8+ recommended for best compatibility")
    
    print(f"📍 Current directory: {current_dir}")
    print(f"🐍 Python version: {sys.version}")
    print(f"💻 Operating system: {platform.system()}")
    print()
    
    # Create desktop shortcut based on OS
    print("🔧 Creating desktop shortcut...")
    
    system = platform.system()
    if system == "Windows":
        success, message = create_windows_shortcut()
    elif system == "Darwin":  # macOS
        success, message = create_mac_shortcut()
    elif system == "Linux":
        success, message = create_linux_shortcut()
    else:
        success = False
        message = f"Unsupported operating system: {system}"
    
    if success:
        print(f"✅ Desktop shortcut created successfully!")
        print(f"📍 Location: {message}")
        print()
        print("🎉 Installation Complete!")
        print()
        print("📋 What's Next:")
        print("1. Double-click the desktop shortcut")
        print("2. The A3 launcher will open")
        print("3. Click 'Launch A3 Automation' to start")
        print("4. Process your handwritten documents!")
        
        # Test the launcher
        print()
        test = input("🧪 Would you like to test the launcher now? (y/n): ").lower().strip()
        if test in ['y', 'yes']:
            print("🚀 Launching A3 Automation...")
            try:
                subprocess.Popen([sys.executable, str(current_dir / "main_launcher.py")])
                print("✅ Launcher started successfully!")
            except Exception as e:
                print(f"❌ Failed to launch: {e}")
        
        return True
        
    else:
        print(f"❌ Failed to create desktop shortcut: {message}")
        print()
        print("📝 Manual Setup Instructions:")
        print(f"1. Create a shortcut to: python \"{current_dir / 'main_launcher.py'}\"")
        print("2. Name it: A3 Document Automation")
        print("3. Place it on your desktop")
        print()
        print("🔄 Alternative: Run directly with:")
        print(f"   python \"{current_dir / 'main_launcher.py'}\"")
        
        return False

if __name__ == "__main__":
    try:
        install_desktop_app()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    finally:
        input("\nPress Enter to exit...")