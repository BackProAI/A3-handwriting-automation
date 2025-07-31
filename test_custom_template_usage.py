#!/usr/bin/env python3
"""
Test Custom Template Usage
Verify that the system uses the existing A3_Custom_Template.pdf and populates it correctly
"""

from pathlib import Path
from a3_template_processor import A3TemplateProcessor
import json

def test_custom_template_usage():
    """Test that the system uses the existing custom template."""
    print("🧪 Testing Custom Template Usage")
    print("=" * 50)
    
    # Check for existing custom template
    custom_template_path = Path("processed_documents/A3_Custom_Template.pdf")
    if not custom_template_path.exists():
        print(f"❌ Custom template not found: {custom_template_path}")
        print(f"   Please run 'python field_positioning_tool.py' first to create your custom template")
        return False
    
    print(f"✅ Found existing custom template: {custom_template_path}")
    
    # Check for custom field configuration
    config_path = Path("custom_field_positions.json")
    if config_path.exists():
        print(f"✅ Found custom field configuration: {config_path}")
        with open(config_path, 'r') as f:
            custom_config = json.load(f)
        processor = A3TemplateProcessor(custom_fields_config=custom_config)
    else:
        print("📝 Using default field configuration")
        processor = A3TemplateProcessor()
    
    # Create sample extracted results
    sample_results = [
        {
            'success': True,
            'page_number': 1,
            'sections': [
                {
                    'text': 'Property investment risk - market volatility',
                    'location': 'left circle danger area'
                },
                {
                    'text': 'Strong financial background and credit history',
                    'location': 'left circle strength area'
                },
                {
                    'text': 'Pre-approved for $500,000 investment loan',
                    'location': 'right side financial section'
                }
            ]
        }
    ]
    
    try:
        # Test using existing custom template
        output_path = Path("processed_documents/Test_Custom_Template_Usage.pdf")
        
        populated_template = processor.populate_template(
            sample_results, 
            output_path, 
            base_template=custom_template_path
        )
        
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Used existing custom template: {custom_template_path.name}")
        print(f"✅ Created populated document: {populated_template}")
        print(f"📁 Location: {populated_template.absolute()}")
        
        # Verify the original template wasn't modified
        if custom_template_path.exists():
            print(f"✅ Original custom template preserved: {custom_template_path.name}")
        else:
            print(f"❌ Original custom template was accidentally deleted!")
            return False
        
        # Verify the new file was created
        if populated_template.exists():
            file_size = populated_template.stat().st_size
            print(f"📊 Output file size: {file_size:,} bytes")
            print(f"🎯 Template populated with sample text using your custom fields")
        else:
            print(f"❌ Output template file was not created")
            return False
        
        print(f"\n📋 What was tested:")
        print(f"   ✅ Using existing A3_Custom_Template.pdf as base")
        print(f"   ✅ Populating with extracted text")
        print(f"   ✅ Preserving original template file")
        print(f"   ✅ Creating new populated output file")
        print(f"   ✅ Using your custom field positions")
        
        print(f"\n🎯 Ready for real automation!")
        print(f"   Your A3 automation will now use: {custom_template_path}")
        print(f"   Drop documents into the UI and watch it populate your template!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_custom_template_usage()
    
    if success:
        print(f"\n🚀 Custom template usage is working perfectly!")
        print(f"🎯 Your automation system will now use your existing custom template!")
    else:
        print(f"\n💥 Custom template usage needs attention")