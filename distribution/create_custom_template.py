#!/usr/bin/env python3
"""
Create Custom Template Tool
Uses your custom field configuration to create a PDF template
"""

from pathlib import Path
from a3_template_processor import A3TemplateProcessor
import json

def create_custom_template():
    """Create a PDF template using custom field positions."""
    print("🎯 Creating Custom A3 Template")
    print("=" * 40)
    
    # Check for custom configuration
    config_path = Path("custom_field_positions.json")
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print(f"📝 Run 'python create_field_config.py' first to create the configuration file")
        return False
    
    try:
        # Load and display configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Loaded configuration from: {config_path}")
        
        # Count fields
        page1_fields = len(config.get("page_1", []))
        page2_fields = len(config.get("page_2", []))
        total_fields = page1_fields + page2_fields
        
        print(f"📊 Field Summary:")
        print(f"   Page 1: {page1_fields} fields")
        print(f"   Page 2: {page2_fields} fields")
        print(f"   Total: {total_fields} fields")
        
        if total_fields == 0:
            print(f"⚠️ No fields defined in configuration!")
            return False
        
        # Create template processor
        template_path = Path("A3_templates/More4Life A3 Goals - blank.pdf")
        if not template_path.exists():
            print(f"❌ Template not found: {template_path}")
            return False
        
        processor = A3TemplateProcessor(template_path)
        
        # Create custom template
        output_path = Path("processed_documents/A3_Custom_Template.pdf")
        final_template = processor.create_template_with_custom_fields(config_path, output_path)
        
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Created custom A3 template: {final_template}")
        print(f"📁 Location: {final_template.absolute()}")
        
        print(f"\n🎯 Template Features:")
        print(f"- {total_fields} transparent text fields")
        print(f"- Custom positioning based on your configuration")
        print(f"- Seamless appearance (no borders or backgrounds)")
        print(f"- Multi-line text support")
        print(f"- Ready for copy/paste workflow")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Open: {final_template}")
        print(f"2. Run A3 automation to extract text from your documents")
        print(f"3. Copy extracted text from the UI")
        print(f"4. Click on areas in the PDF to find text fields")
        print(f"5. Paste text into the appropriate fields")
        print(f"6. Save your completed A3 document")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        return False

def main():
    """Main function."""
    success = create_custom_template()
    
    if success:
        print(f"\n🚀 Your custom A3 template is ready!")
    else:
        print(f"\n💥 Failed to create custom template.")

if __name__ == "__main__":
    main()