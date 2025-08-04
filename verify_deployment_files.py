#!/usr/bin/env python3
"""
Verify all essential files are present before building the executable
Run this before building to ensure nothing critical is missing
"""

from pathlib import Path
import json

def verify_deployment_files():
    """Check that all critical files exist for deployment"""
    
    print("🔍 Verifying A3 Deployment Files...")
    print("=" * 50)
    
    current_dir = Path(__file__).parent
    
    # Critical files and folders that MUST be included
    critical_items = [
        # Folders
        ("A3_templates/", "folder", "Templates and configurations"),
        ("processed_documents/", "folder", "Contains A3_Custom_Template.pdf (CRITICAL OUTPUT FILE)"),
        
        # Configuration files
        ("custom_field_positions.json", "file", "PDF field positions"),
        ("app_config.json", "file", "Application configuration"),
        ("version.txt", "file", "Version tracking"),
        
        # Core Python modules
        ("main_launcher.py", "file", "Main launcher with auto-update"),
        ("a3_template_processor.py", "file", "PDF template processor"),
        ("a3_sectioned_automation.py", "file", "Main automation application"),
        ("sectioned_gpt4o_ocr.py", "file", "GPT-4o OCR engine"),
        ("section_definition_tool.py", "file", "Section definition tool"),
        ("field_positioning_tool.py", "file", "Field positioning tool"),
        ("create_pdf_template.py", "file", "PDF template generator"),
        ("manual_page_order_tool.py", "file", "Manual page ordering"),
        
        # Build files
        ("build_executable.py", "file", "Executable build script"),
        ("requirements.txt", "file", "Python dependencies"),
    ]
    
    # Check each item
    all_present = True
    missing_items = []
    
    for item_path, item_type, description in critical_items:
        full_path = current_dir / item_path
        
        if item_type == "folder":
            exists = full_path.is_dir()
            symbol = "📁"
        else:
            exists = full_path.is_file()
            symbol = "📄"
        
        if exists:
            if item_type == "folder":
                # Count files in folder
                file_count = len(list(full_path.glob("*")))
                status_text = f"✅ {symbol} {item_path} ({file_count} files) - {description}"
            else:
                # Show file size
                size_kb = full_path.stat().st_size / 1024
                status_text = f"✅ {symbol} {item_path} ({size_kb:.1f} KB) - {description}"
        else:
            status_text = f"❌ {symbol} {item_path} - MISSING! - {description}"
            all_present = False
            missing_items.append(item_path)
        
        print(status_text)
    
    print("\n" + "=" * 50)
    
    # Special check for A3_Custom_Template.pdf
    template_file = current_dir / "processed_documents" / "A3_Custom_Template.pdf"
    if template_file.exists():
        size_mb = template_file.stat().st_size / (1024 * 1024)
        print(f"🎯 CRITICAL FILE CHECK: A3_Custom_Template.pdf ({size_mb:.1f} MB) ✅ FOUND")
    else:
        print("🚨 CRITICAL FILE CHECK: A3_Custom_Template.pdf ❌ MISSING!")
        all_present = False
        missing_items.append("processed_documents/A3_Custom_Template.pdf")
    
    # Check GitHub configuration
    print(f"\n🔗 GitHub Configuration:")
    try:
        with open(current_dir / "main_launcher.py", 'r') as f:
            content = f.read()
            if "BackProAI/A3-handwriting-automation" in content:
                print("✅ GitHub repo configured: BackProAI/A3-handwriting-automation")
            else:
                print("⚠️  GitHub repo may need updating in main_launcher.py")
    except:
        print("❌ Could not verify GitHub configuration")
    
    # Final verdict
    print(f"\n{'=' * 50}")
    if all_present:
        print("🎉 ALL CRITICAL FILES PRESENT!")
        print("✅ Ready to build executable with:")
        print("   python build_executable.py")
        print("\n🚀 Your deployment will include:")
        print("   - A3_Custom_Template.pdf (output template)")
        print("   - All configuration files")
        print("   - Complete automation system")
        print("   - Auto-update functionality")
        return True
    else:
        print("❌ MISSING FILES DETECTED!")
        print(f"   Missing: {', '.join(missing_items)}")
        print("\n🔧 Fix these issues before building:")
        for item in missing_items:
            print(f"   - Ensure {item} exists")
        return False

if __name__ == "__main__":
    success = verify_deployment_files()
    
    if success:
        print(f"\n{'=' * 50}")
        print("Next steps:")
        print("1. python build_executable.py")
        print("2. Test the executable in A3_Distribution/")
        print("3. Deploy to more4life team")
    else:
        print(f"\n{'=' * 50}")
        print("Please fix missing files before building executable.")