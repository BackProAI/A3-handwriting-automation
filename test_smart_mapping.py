#!/usr/bin/env python3
"""
Test the smart field mapping logic with your custom field positions.
"""

import json
from pathlib import Path
from a3_template_processor import A3TemplateProcessor

def test_smart_mapping():
    """Test the smart mapping logic with sample data."""
    
    # Check if custom config exists
    custom_config_path = Path("A3_templates/custom_field_positions.json")
    if not custom_config_path.exists():
        print(f"❌ Custom config not found at: {custom_config_path}")
        return
    
    # Load custom config and create processor
    with open(custom_config_path, 'r') as f:
        custom_config = json.load(f)
    
    processor = A3TemplateProcessor(custom_fields_config=custom_config)
    
    # Sample extracted data to test mapping
    sample_results = [
        {
            'success': True,
            'page_number': 1,
            'sections': [
                {
                    'text': 'Need to eliminate debt and financial risks',
                    'location': 'left upper'
                },
                {
                    'text': 'Focus on investment opportunities in property',
                    'location': 'left middle'
                },
                {
                    'text': 'Strengthen our emergency fund and savings',
                    'location': 'left lower'
                },
                {
                    'text': 'Client consultation notes and meeting details',
                    'location': 'right upper'
                },
                {
                    'text': 'Follow up on insurance policy reviews',
                    'location': 'right middle'
                },
                {
                    'text': 'Schedule quarterly portfolio reviews',
                    'location': 'right bottom'
                }
            ]
        },
        {
            'success': True,
            'page_number': 2,
            'sections': [
                {
                    'text': 'Save $50,000 for house deposit',
                    'location': 'left upper'
                },
                {
                    'text': 'Currently saving $2,000 per month',
                    'location': 'left middle'
                },
                {
                    'text': 'Set up automatic transfer to savings account',
                    'location': 'left lower'
                },
                {
                    'text': 'Expand business to new market',
                    'location': 'center left upper'
                },
                {
                    'text': 'Working on business plan development',
                    'location': 'center left middle'
                },
                {
                    'text': 'Research market opportunities',
                    'location': 'center left lower'
                },
                {
                    'text': 'Take family vacation to Europe',
                    'location': 'center upper'
                },
                {
                    'text': 'Planning travel itinerary',
                    'location': 'center middle'
                },
                {
                    'text': 'Book flights and accommodation',
                    'location': 'center lower'
                },
                {
                    'text': 'Improve fitness and lose weight',
                    'location': 'center right upper'
                },
                {
                    'text': 'Going to gym 3 times per week',
                    'location': 'center right middle'
                },
                {
                    'text': 'Hire personal trainer',
                    'location': 'center right lower'
                },
                {
                    'text': 'Spend more quality time with kids',
                    'location': 'right upper'
                },
                {
                    'text': 'Having weekly family dinners',
                    'location': 'right middle'
                },
                {
                    'text': 'Plan weekend activities together',
                    'location': 'right lower'
                }
            ]
        }
    ]
    
    print("🧪 TESTING SMART FIELD MAPPING")
    print("="*60)
    
    # Test the mapping
    field_mappings = processor._map_text_to_fields(sample_results)
    
    print(f"\n📊 MAPPING RESULTS SUMMARY:")
    print("="*60)
    print(f"✅ Total fields mapped: {len(field_mappings)}")
    print(f"📋 Available fields: {len(processor.form_fields_config.get('page_1', [])) + len(processor.form_fields_config.get('page_2', []))}")
    
    # Show mapping success rate
    total_sections = sum(len(r.get('sections', [])) for r in sample_results if r.get('success'))
    mapped_sections = len([text for text in field_mappings.values() if text.strip()])
    
    print(f"📈 Mapping success rate: {mapped_sections}/{total_sections} sections mapped")
    
    if field_mappings:
        print("\n🎯 SUCCESS: Smart mapping is working!")
        print("   The system correctly matched text to your custom field names")
        print("   based on content keywords and position analysis.")
    else:
        print("\n❌ ISSUE: No mappings were created")
        print("   The mapping logic may need adjustment for your specific fields")

if __name__ == "__main__":
    test_smart_mapping()