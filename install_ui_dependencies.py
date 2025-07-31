#!/usr/bin/env python3
"""
Install UI Dependencies for A3 Document Automation
Installs all required packages for the drag-and-drop UI system
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package_name: str) -> bool:
    """Install a Python package using pip."""
    try:
        print(f"📦 Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        return False

def main():
    """Install all UI dependencies."""
    print("🚀 Installing A3 Document Automation UI Dependencies")
    print("=" * 60)
    
    # Required packages
    packages = [
        "tkinterdnd2>=0.3.0",    # Drag & drop GUI
        "python-docx>=0.8.11",   # Word document generation
        "PyMuPDF>=1.23.0",       # Enhanced PDF handling
        "pillow>=10.0.0",        # Image processing
        "requests>=2.31.0"       # OpenAI API calls
    ]
    
    print("📋 Installing the following packages:")
    for pkg in packages:
        print(f"   • {pkg}")
    print()
    
    # Install each package
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
        print()  # Add spacing
    
    print("=" * 60)
    print(f"📊 Installation Summary:")
    print(f"   ✅ Successful: {success_count}/{total_count}")
    print(f"   ❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 All dependencies installed successfully!")
        print("\n📋 Next steps:")
        print("   1. Set your OpenAI API key:")
        print("      PowerShell: $env:OPENAI_API_KEY = 'your-api-key-here'")
        print("   2. Run the automation system:")
        print("      python a3_document_automation.py")
        print("\n💡 The system will process handwritten documents and create:")
        print("   • Clean PDF versions with typed text")
        print("   • Editable Word documents")
        print("   • Handles both images and PDFs as input")
    else:
        print(f"\n⚠️  {total_count - success_count} packages failed to install")
        print("💡 Try installing them manually:")
        for package in packages:
            print(f"   pip install {package}")

if __name__ == "__main__":
    main() 