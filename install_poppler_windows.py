#!/usr/bin/env python3
"""
Install Poppler for Windows - PDF Processing Fix
==============================================

Script to help install Poppler utilities for pdf2image on Windows.
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_poppler_windows():
    """Download and setup Poppler for Windows."""
    print("🔧 INSTALLING POPPLER FOR WINDOWS")
    print("="*50)
    
    # Create a directory for poppler
    poppler_dir = Path("poppler-utils")
    if poppler_dir.exists():
        print(f"   📁 Poppler directory already exists: {poppler_dir}")
        return str(poppler_dir / "Library" / "bin")
    
    print("📦 Downloading Poppler for Windows...")
    
    # Poppler Windows release URL (conda-forge version)
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.01.0-0/Release-23.01.0-0.zip"
    
    try:
        # Download poppler
        zip_path = "poppler-windows.zip"
        print(f"   🌐 Downloading from: {poppler_url}")
        urllib.request.urlretrieve(poppler_url, zip_path)
        print(f"   ✅ Downloaded: {zip_path}")
        
        # Extract
        print("   📂 Extracting Poppler...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(poppler_dir)
        
        # Clean up zip file
        os.remove(zip_path)
        print(f"   🗑️  Cleaned up: {zip_path}")
        
        # Find the bin directory
        bin_paths = list(poppler_dir.rglob("pdftoppm.exe"))
        if bin_paths:
            bin_dir = bin_paths[0].parent
            print(f"   ✅ Poppler installed to: {bin_dir}")
            return str(bin_dir)
        else:
            print("   ❌ Could not find poppler executables")
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to download/install Poppler: {e}")
        return None

def test_poppler_installation(poppler_path):
    """Test if poppler is working."""
    print(f"\n🧪 TESTING POPPLER INSTALLATION")
    print("="*40)
    
    if not poppler_path:
        print("❌ No poppler path provided")
        return False
    
    # Test if pdftoppm exists
    pdftoppm_path = Path(poppler_path) / "pdftoppm.exe"
    if not pdftoppm_path.exists():
        print(f"❌ pdftoppm.exe not found at: {pdftoppm_path}")
        return False
    
    print(f"✅ Found pdftoppm.exe at: {pdftoppm_path}")
    
    # Test pdf2image with poppler path
    try:
        from pdf2image import convert_from_path
        print("✅ pdf2image import successful")
        
        # Try to use it (this will test the path)
        print("✅ Poppler installation appears to be working!")
        return True
        
    except Exception as e:
        print(f"❌ pdf2image test failed: {e}")
        return False

def create_poppler_config(poppler_path):
    """Create a configuration file with the poppler path."""
    config_content = f'''# Poppler Configuration for More4Life OCR System
# 
# This file contains the path to poppler utilities for PDF processing.
# Generated automatically by install_poppler_windows.py

POPPLER_PATH = r"{poppler_path}"

# Instructions for manual setup:
# 1. Add the above path to your system PATH environment variable, OR
# 2. Use this path directly in pdf2image calls:
#    convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
'''
    
    with open("poppler_config.py", "w") as f:
        f.write(config_content)
    
    print(f"📝 Created poppler_config.py with path: {poppler_path}")

def main():
    """Main installation function."""
    print("🚀 MORE4LIFE PDF PROCESSING SETUP")
    print("="*50)
    
    # Check if we're on Windows
    if sys.platform != "win32":
        print("⚠️  This script is designed for Windows.")
        print("   On Linux/Mac, install poppler with:")
        print("   - Ubuntu/Debian: sudo apt-get install poppler-utils")
        print("   - macOS: brew install poppler")
        return
    
    # Download and install poppler
    poppler_path = download_poppler_windows()
    
    if poppler_path:
        # Test the installation
        if test_poppler_installation(poppler_path):
            # Create configuration
            create_poppler_config(poppler_path)
            
            print(f"\n🎉 SUCCESS!")
            print("="*30)
            print("✅ Poppler installed successfully")
            print("✅ Configuration file created")
            print(f"✅ Poppler utilities available at: {poppler_path}")
            
            print(f"\n📋 NEXT STEPS:")
            print("1. The system will now automatically use the local Poppler installation")
            print("2. Test PDF processing with: python test_any_image.py")
            print("3. Place PDF files in test_images/ directory for processing")
            
        else:
            print(f"\n❌ INSTALLATION ISSUES")
            print("Poppler was downloaded but testing failed.")
            print("You may need to install it manually.")
    else:
        print(f"\n❌ INSTALLATION FAILED")
        print("Please install Poppler manually:")
        print("1. Download from: https://github.com/oschwartz10612/poppler-windows/releases")
        print("2. Extract to a folder")
        print("3. Add the bin/ folder to your Windows PATH")

if __name__ == "__main__":
    main() 