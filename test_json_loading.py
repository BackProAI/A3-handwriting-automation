#!/usr/bin/env python3
"""
Test Script: Which JSON File Controls Output PDF Text Placement
This script demonstrates exactly which JSON file is loaded and used
when placing extracted text into the output PDF boxes.
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

def test_json_file_loading():
    """Test which JSON files are loaded for output PDF generation."""
    
    print("🧪 JSON FILE LOADING TEST")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Check which files exist
    print("📂 STEP 1: Checking JSON File Locations")
    print("-" * 40)
    
    files_to_check = [
        "custom_field_position.json",  # Old root location
        "custom_field_positions.json",  # Old root location (plural)
        "A3_templates/custom_field_position.json",  # New correct location
        "A3_templates/custom_field_positions.json",  # Alternative name
        "a3_section_config.json",  # Old root location
        "A3_templates/a3_section_config.json"  # New correct location
    ]
    
    existing_files = []
    for file_path in files_to_check:
        path = Path(file_path)
        exists = path.exists()
        print(f"  {'✅' if exists else '❌'} {file_path}")
        if exists:
            existing_files.append(path)
    
    print()
    
    # Test 2: Simulate A3SectionedProcessor initialization
    print("🔧 STEP 2: Simulating A3SectionedProcessor Initialization")
    print("-" * 40)
    
    # This is the exact path from line 51 in a3_sectioned_automation.py
    custom_config_path = Path("A3_templates/custom_field_position.json")
    
    print(f"📍 Looking for: {custom_config_path}")
    print(f"📁 Full path: {custom_config_path.absolute()}")
    print(f"🔍 File exists: {'✅ YES' if custom_config_path.exists() else '❌ NO'}")
    
    if custom_config_path.exists():
        print(f"📊 File size: {custom_config_path.stat().st_size} bytes")
        print(f"📅 Last modified: {datetime.fromtimestamp(custom_config_path.stat().st_mtime)}")
        
        # Load and analyze the JSON
        try:
            with open(custom_config_path, 'r') as f:
                config_data = json.load(f)
            
            print()
            print("📋 STEP 3: Analyzing JSON Content")
            print("-" * 40)
            
            # Count fields per page
            page1_fields = len(config_data.get("page_1", []))
            page2_fields = len(config_data.get("page_2", []))
            total_fields = page1_fields + page2_fields
            
            print(f"📄 Page 1 fields: {page1_fields}")
            print(f"📄 Page 2 fields: {page2_fields}")
            print(f"🎯 Total output fields: {total_fields}")
            
            print()
            print("🔤 Field Names (First 5 examples):")
            field_count = 0
            for page_key in ["page_1", "page_2"]:
                if page_key in config_data:
                    for field in config_data[page_key]:
                        if field_count < 5:
                            field_name = field.get('name', 'Unknown')
                            rect = field.get('rect', [0, 0, 0, 0])
                            fontsize = field.get('fontsize', 'Unknown')
                            print(f"  📝 '{field_name}' - Font: {fontsize}pt - Position: {rect[:2]}")
                            field_count += 1
                        
            if total_fields > 5:
                print(f"  ... and {total_fields - 5} more fields")
                
        except Exception as e:
            print(f"❌ Error reading JSON: {e}")
    
    print()
    
    # Test 3: Show the actual code path
    print("💻 STEP 4: Code Execution Path")
    print("-" * 40)
    print("This is the exact sequence when processing a document:")
    print()
    print("1. 📍 a3_sectioned_automation.py:51")
    print(f"   custom_config_path = Path('A3_templates/custom_field_position.json')")
    print()
    print("2. 🔍 a3_sectioned_automation.py:52-56")
    print("   if custom_config_path.exists():")
    print("       custom_config = self._load_custom_config(custom_config_path)")
    print("       self.template_processor = A3TemplateProcessor(custom_fields_config=custom_config)")
    print()
    print("3. 📝 a3_sectioned_automation.py:110")
    print("   widget.field_value = text_to_populate  # ← TEXT PLACED HERE")
    print()
    print("4. 💾 a3_sectioned_automation.py:111")
    print("   widget.update()  # ← PDF FIELD UPDATED")
    
    print()
    print("🎯 CONCLUSION")
    print("=" * 60)
    if custom_config_path.exists():
        print(f"✅ OUTPUT PDF TEXT PLACEMENT IS CONTROLLED BY:")
        print(f"📁 {custom_config_path.absolute()}")
        print()
        print("🔧 This file defines:")
        print("   • Where each text box appears (coordinates)")
        print("   • Size of each text box (width & height)")
        print("   • Font size for text")
        print("   • Field names that link to OCR sections")
    else:
        print("❌ CUSTOM FIELD CONFIGURATION NOT FOUND!")
        print("   The system will use default field positions")
    
    print()
    print("🧪 Test completed successfully!")

if __name__ == "__main__":
    test_json_file_loading()
