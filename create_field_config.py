#!/usr/bin/env python3
"""
Create Field Configuration Tool
Generates a customizable JSON file for text field positions
"""

from pathlib import Path
import json
from a3_template_processor import A3TemplateProcessor

def create_default_config():
    """Create a default field configuration file that can be easily edited."""
    print("📝 Creating Default Field Configuration")
    print("=" * 50)
    
    try:
        # Initialize processor to get default config
        processor = A3TemplateProcessor()
        
        # Save default configuration
        config_path = Path("custom_field_positions.json")
        saved_path = processor.save_custom_fields_config(config_path)
        
        if saved_path:
            print(f"\n✅ Created field configuration file: {config_path}")
            print(f"📁 Location: {config_path.absolute()}")
            
            print(f"\n📋 CUSTOMIZE YOUR FIELDS:")
            print(f"1. Open: {config_path}")
            print(f"2. Edit the 'rect' coordinates: [x1, y1, x2, y2]")
            print(f"3. Add/remove fields as needed")
            print(f"4. Change field names to match your needs")
            
            print(f"\n📏 COORDINATE SYSTEM:")
            print(f"- [x1, y1] = Top-left corner of text field")
            print(f"- [x2, y2] = Bottom-right corner of text field")
            print(f"- Origin (0,0) is at top-left of PDF page")
            print(f"- Units are in PDF points (72 points = 1 inch)")
            
            print(f"\n🎯 EXAMPLE FIELD:")
            print(f'   "name": "danger_main_circle",')
            print(f'   "rect": [50, 200, 280, 300],  // x1, y1, x2, y2')
            print(f'   "type": "text",')
            print(f'   "multiline": true,')
            print(f'   "fontsize": 10')
            
            print(f"\n🚀 CREATE TEMPLATE:")
            print(f"After editing, run:")
            print(f"python create_custom_template.py")
            
            return True
        else:
            print("❌ Failed to create configuration file")
            return False
            
    except Exception as e:
        print(f"❌ Error creating configuration: {e}")
        return False

def main():
    """Main function."""
    success = create_default_config()
    
    if success:
        print(f"\n🎉 Configuration file ready for customization!")
        print(f"📝 Edit the coordinates to position fields exactly where you want them.")
    else:
        print(f"\n💥 Failed to create configuration file.")

if __name__ == "__main__":
    main()