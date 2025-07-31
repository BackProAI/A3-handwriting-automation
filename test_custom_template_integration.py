#!/usr/bin/env python3
"""
Test Custom Template Integration
Verify that the A3 automation system uses custom positioned fields
"""

from pathlib import Path
from a3_document_automation import A3DocumentProcessor
import os

def test_custom_template_integration():
    """Test if the automation system detects and uses custom fields."""
    print("🧪 Testing Custom Template Integration")
    print("=" * 50)
    
    # Check for custom field configuration
    temp_config = Path("custom_field_positions.json")
    custom_template = Path("processed_documents/A3_Custom_Template.pdf")
    
    print(f"📋 Configuration Files:")
    print(f"   Custom config: {temp_config} {'✅ EXISTS' if temp_config.exists() else '❌ MISSING'}")
    print(f"   Custom template: {custom_template} {'✅ EXISTS' if custom_template.exists() else '❌ MISSING'}")
    
    if not temp_config.exists():
        print(f"\n⚠️ Custom field configuration not found!")
        print(f"   Run 'python field_positioning_tool.py' to create custom fields")
        return False
    
    try:
        # Test processor initialization
        # Mock API key for testing (won't actually call API)
        os.environ['OPENAI_API_KEY'] = 'test-key-for-testing'
        processor = A3DocumentProcessor()
        
        print(f"\n🎯 Processor Configuration:")
        print(f"   Using custom fields: {'✅ YES' if processor.using_custom_fields else '❌ NO'}")
        
        if processor.using_custom_fields:
            print(f"   ✅ SUCCESS: System will use your custom positioned fields!")
            print(f"   📝 When you run the automation, it will:")
            print(f"      • Extract text using GPT-4o OCR")
            print(f"      • Create templates with YOUR positioned fields")
            print(f"      • Generate copy-friendly text for manual population")
            
            if custom_template.exists():
                print(f"   📁 Existing custom template will be copied and reused")
            else:
                print(f"   🔧 New templates will be created with your field positions")
        else:
            print(f"   ❌ System will use default field positions")
            print(f"   💡 Make sure custom_field_positions.json contains your custom fields")
        
        return processor.using_custom_fields
        
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def main():
    """Main function."""
    success = test_custom_template_integration()
    
    if success:
        print(f"\n🎉 SUCCESS: Your custom template integration is working!")
        print(f"📋 Next Steps:")
        print(f"   1. Run: python a3_document_automation.py")
        print(f"   2. Drop your A3 documents to process")
        print(f"   3. Get templates with YOUR positioned fields")
        print(f"   4. Copy/paste the extracted text into your custom fields")
    else:
        print(f"\n💥 ISSUE: Custom template integration not working")
        print(f"📝 To fix:")
        print(f"   1. Run: python field_positioning_tool.py")
        print(f"   2. Position your fields and save configuration")
        print(f"   3. Create custom template")
        print(f"   4. Then run the automation system")

if __name__ == "__main__":
    main()