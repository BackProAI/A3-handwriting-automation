#!/usr/bin/env python3
"""
Create PDF Template from JSON Field Positions
Takes a blank PDF and adds form fields based on JSON configuration
"""

import json
import fitz  # PyMuPDF
from pathlib import Path
import sys

def create_template_from_json(blank_pdf_path, json_config_path, output_path):
    """Create a PDF template with form fields from JSON configuration."""
    
    print(f"🎯 Creating PDF template from JSON configuration")
    print(f"📄 Blank PDF: {blank_pdf_path}")
    print(f"📋 JSON config: {json_config_path}")
    print(f"💾 Output: {output_path}")
    print("=" * 50)
    
    # Load JSON configuration
    try:
        with open(json_config_path, 'r') as f:
            field_config = json.load(f)
        print(f"✅ Loaded field configuration")
    except Exception as e:
        print(f"❌ Failed to load JSON config: {e}")
        return None
    
    # Open blank PDF
    try:
        doc = fitz.open(blank_pdf_path)
        print(f"✅ Opened blank PDF ({len(doc)} pages)")
    except Exception as e:
        print(f"❌ Failed to open PDF: {e}")
        return None
    
    total_fields = 0
    
    # Process each page
    for page_key, fields in field_config.items():
        if not fields:
            continue
            
        page_num = int(page_key.split('_')[1]) - 1  # Convert "page_1" to 0
        
        if page_num >= len(doc):
            print(f"⚠️ Skipping {page_key} - page doesn't exist in PDF")
            continue
            
        page = doc[page_num]
        print(f"📄 Processing {page_key}: {len(fields)} fields")
        
        for field in fields:
            try:
                # Create form field
                rect = fitz.Rect(field["rect"])
                
                # Create the field widget
                widget = fitz.Widget()
                widget.field_name = field["name"]
                widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                widget.rect = rect
                widget.field_flags = fitz.PDF_TX_FIELD_IS_MULTILINE
                
                # Make field transparent (no borders, no fill)
                widget.fill_color = None
                widget.border_color = None
                widget.border_width = 0
                
                # Set text properties
                widget.text_fontsize = field.get("fontsize", 10)
                widget.text_color = (0, 0, 0)  # Black text
                
                # Add widget to page
                annot = page.add_widget(widget)
                annot.update()
                
                total_fields += 1
                print(f"   ✅ Added field: {field['name']}")
                
            except Exception as e:
                print(f"   ❌ Failed to add field {field['name']}: {e}")
    
    # Save the template
    try:
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save PDF
        doc.save(str(output_path))
        doc.close()
        
        print("=" * 50)
        print(f"🎉 SUCCESS!")
        print(f"📊 Total fields added: {total_fields}")
        print(f"💾 Template saved: {output_path}")
        print(f"📝 The template now has invisible form fields ready for population!")
        
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Failed to save template: {e}")
        doc.close()
        return None

def main():
    """Main function with default paths."""
    
    # Default paths
    blank_pdf = "A3_templates/More4Life A3 Goals - blank.pdf"
    json_config = "A3_templates/custom_field_position.json"  # Your saved config (correct path)
    output_pdf = "processed_documents/A3_Custom_Template.pdf"
    
    # Check if files exist
    if not Path(blank_pdf).exists():
        print(f"❌ Blank PDF not found: {blank_pdf}")
        print("💡 Please check the path to your blank A3 template")
        return
    
    if not Path(json_config).exists():
        print(f"❌ JSON config not found: {json_config}")
        print("💡 Please save your field positions first using the field positioning tool")
        return
    
    # Create template
    result = create_template_from_json(blank_pdf, json_config, output_pdf)
    
    if result:
        print(f"\n🚀 Next steps:")
        print(f"   1. Your template is ready: {result}")
        print(f"   2. Run a3_sectioned_automation.py to use it")
        print(f"   3. Drag handwritten documents to populate the fields automatically")
    else:
        print(f"\n❌ Template creation failed!")

if __name__ == "__main__":
    main()