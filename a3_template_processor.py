#!/usr/bin/env python3
"""
A3 Template Processor
Creates interactive PDF templates with form fields and populates them with extracted text
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json
import time

class A3TemplateProcessor:
    """Processes A3 templates by adding form fields and populating them."""
    
    def __init__(self, template_path: Path = None, custom_fields_config: Dict = None):
        """Initialize with the blank template."""
        self.template_path = template_path or Path("A3_templates/More4Life A3 Goals - blank.pdf")
        self.form_fields_config = custom_fields_config or self._get_default_form_fields_config()
        
    def _get_default_form_fields_config(self) -> Dict[str, List[Dict]]:
        """Define where form fields should be placed on each page."""
        return {
            "page_1": [
                # Circle content areas (left side)
                {"name": "dangers_content", "rect": [50, 200, 280, 300], "type": "text", "multiline": True},
                {"name": "opportunities_content", "rect": [50, 350, 280, 450], "type": "text", "multiline": True},
                {"name": "strengths_content", "rect": [50, 500, 280, 600], "type": "text", "multiline": True},
                
                # Right side content areas
                {"name": "financial_info", "rect": [320, 200, 550, 300], "type": "text", "multiline": True},
                {"name": "career_plans", "rect": [320, 350, 550, 450], "type": "text", "multiline": True},
                {"name": "additional_notes", "rect": [320, 500, 550, 600], "type": "text", "multiline": True},
            ],
            "page_2": [
                # Money column
                {"name": "money_goals", "rect": [50, 150, 160, 250], "type": "text", "multiline": True},
                {"name": "money_now", "rect": [50, 300, 160, 400], "type": "text", "multiline": True},
                {"name": "money_todo", "rect": [50, 450, 160, 550], "type": "text", "multiline": True},
                
                # Business column
                {"name": "business_goals", "rect": [170, 150, 280, 250], "type": "text", "multiline": True},
                {"name": "business_now", "rect": [170, 300, 280, 400], "type": "text", "multiline": True},
                {"name": "business_todo", "rect": [170, 450, 280, 550], "type": "text", "multiline": True},
                
                # Leisure column
                {"name": "leisure_goals", "rect": [290, 150, 400, 250], "type": "text", "multiline": True},
                {"name": "leisure_now", "rect": [290, 300, 400, 400], "type": "text", "multiline": True},
                {"name": "leisure_todo", "rect": [290, 450, 400, 550], "type": "text", "multiline": True},
                
                # Health column
                {"name": "health_goals", "rect": [410, 150, 520, 250], "type": "text", "multiline": True},
                {"name": "health_now", "rect": [410, 300, 520, 400], "type": "text", "multiline": True},
                {"name": "health_todo", "rect": [410, 450, 520, 550], "type": "text", "multiline": True},
                
                # Family column
                {"name": "family_goals", "rect": [530, 150, 640, 250], "type": "text", "multiline": True},
                {"name": "family_now", "rect": [530, 300, 640, 400], "type": "text", "multiline": True},
                {"name": "family_todo", "rect": [530, 450, 640, 550], "type": "text", "multiline": True},
            ]
        }
    
    def create_template_with_form_fields(self, output_path: Path = None) -> Path:
        """Create a template with interactive form fields."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        
        output_path = output_path or Path("processed_documents/A3_template_with_fields.pdf")
        output_path.parent.mkdir(exist_ok=True)
        
        # Open the blank template
        doc = fitz.open(self.template_path)
        
        try:
            # Add form fields to each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_key = f"page_{page_num + 1}"
                
                if page_key in self.form_fields_config:
                    for field_config in self.form_fields_config[page_key]:
                        self._add_form_field(page, field_config)
            
            # Save the template with form fields
            doc.save(str(output_path))
            print(f"✅ Created template with form fields: {output_path}")
            return output_path
            
        finally:
            doc.close()
    
    def _add_form_field(self, page: fitz.Page, field_config: Dict):
        """Add a single form field to a page with transparent/seamless appearance."""
        try:
            field_name = field_config["name"]
            rect = fitz.Rect(field_config["rect"])
            
            # Create text widget with transparent appearance
            widget = fitz.Widget()
            widget.field_name = field_name
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_flags = fitz.PDF_TX_FIELD_IS_MULTILINE if field_config.get("multiline") else 0
            widget.rect = rect
            widget.text_font = "helv"
            widget.text_fontsize = field_config.get("fontsize", 10)
            
            # Transparent/seamless appearance
            widget.fill_color = None  # No background fill
            widget.border_color = None  # No border
            widget.border_width = 0  # No border width
            
            # Text appearance
            widget.text_color = (0, 0, 0)  # Black text
            
            # Add the widget to the page
            page.add_widget(widget)
            
        except Exception as e:
            print(f"⚠️ Failed to add form field {field_config.get('name', 'unknown')}: {e}")
    
    def create_empty_template(self, output_path: Path = None) -> Path:
        """Create a template with empty text fields ready for manual population."""
        if not output_path:
            timestamp = int(time.time())
            output_path = Path(f"processed_documents/A3_Empty_Template_{timestamp}.pdf")
        
        output_path.parent.mkdir(exist_ok=True)
        
        # Just create and return the template with empty form fields
        return self.create_template_with_form_fields(output_path)
    
    def populate_template(self, extracted_results: List[Dict[str, Any]], output_path: Path = None, base_template: Path = None) -> Path:
        """Use existing template and automatically populate it with extracted text."""
        if not output_path:
            timestamp = int(time.time())
            output_path = Path(f"processed_documents/A3_Populated_{timestamp}.pdf")
        
        output_path.parent.mkdir(exist_ok=True)
        
        # Use existing template if provided, otherwise create new one
        if base_template and base_template.exists():
            template_with_fields = base_template
            print(f"✅ Using existing template: {template_with_fields}")
        else:
            # Fallback: create new template with form fields
            template_with_fields = self.create_template_with_form_fields()
            print(f"📝 Created new template: {template_with_fields}")
        
        # Open the template with form fields
        doc = fitz.open(template_with_fields)
        
        try:
            # Map extracted text to form fields
            field_mappings = self._map_text_to_fields(extracted_results)
            
            print(f"🎯 Populating {len(field_mappings)} fields with extracted text...")
            
            # Populate the form fields
            populated_count = 0
            for field_name, text_content in field_mappings.items():
                if text_content.strip():
                    try:
                        # Find and populate the field
                        for page_num in range(len(doc)):
                            page = doc[page_num]
                            widgets = page.widgets()
                            
                            for widget in widgets:
                                if widget.field_name == field_name:
                                    widget.field_value = text_content.strip()
                                    widget.update()
                                    populated_count += 1
                                    print(f"   ✅ {field_name}: {text_content[:50]}...")
                                    break
                    except Exception as e:
                        print(f"⚠️ Failed to populate field {field_name}: {e}")
            
            print(f"✅ Successfully populated {populated_count} fields")
            
            # Save the completed document
            doc.save(str(output_path))
            print(f"📁 Saved populated template: {output_path}")
            
            # Clean up temporary template (only if we created it, not if it's the base template)
            if not base_template or template_with_fields != base_template:
                try:
                    if template_with_fields.exists():
                        template_with_fields.unlink()
                except Exception as cleanup_error:
                    print(f"⚠️ Could not clean up temporary template: {cleanup_error}")
            
            return output_path
            
        finally:
            doc.close()
    
    def _map_text_to_fields(self, extracted_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """Map extracted text sections to appropriate form fields."""
        field_mappings = {}
        
        # Get available field names from the current configuration
        available_fields = {}
        for page_key, fields in self.form_fields_config.items():
            for field in fields:
                available_fields[field['name']] = page_key
        
        print(f"\n🎯 SMART FIELD MAPPING")
        print(f"{'='*50}")
        print(f"📋 Available fields: {list(available_fields.keys())}")
        
        for result in extracted_results:
            if not result.get('success', False):
                continue
                
            page_num = result.get('page_number', 1)
            sections = result.get('sections', [])
            
            print(f"\n📄 Processing Page {page_num} with {len(sections)} sections")
            
            if page_num == 1:
                # Page 1 mapping - try intelligent mapping to available fields
                page_mappings = self._map_page1_sections(sections, available_fields)
                field_mappings.update(page_mappings)
            elif page_num == 2:
                # Page 2 mapping - try intelligent mapping to available fields
                page_mappings = self._map_page2_sections(sections, available_fields)
                field_mappings.update(page_mappings)
        
        print(f"\n✅ FINAL FIELD MAPPINGS:")
        print(f"{'='*50}")
        for field_name, text in field_mappings.items():
            print(f"🎯 {field_name}: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        return field_mappings
    
    def _map_page1_sections(self, sections: List[Dict], available_fields: Dict[str, str] = None) -> Dict[str, str]:
        """Map Page 1 sections to form fields using intelligent field matching."""
        mappings = {}
        available_fields = available_fields or {}
        
        for i, section in enumerate(sections):
            text = section.get('text', '').strip()
            location = section.get('location', '').lower()
            
            if not text:
                continue
            
            print(f"  📝 Section {i+1}: '{text[:50]}...' at '{location}'")
            
            # Try to find the best matching field for this text
            best_field = self._find_best_field_match(text, location, available_fields, page=1)
            
            if best_field:
                print(f"     ✅ Matched to field: '{best_field}'")
                if best_field in mappings:
                    mappings[best_field] += '\n' + text
                else:
                    mappings[best_field] = text
            else:
                # Fallback to generic mapping if no specific field found
                generic_field = self._get_generic_page1_field(available_fields)
                if generic_field:
                    print(f"     🔄 Using fallback field: '{generic_field}'")
                    if generic_field in mappings:
                        mappings[generic_field] += '\n' + text
                    else:
                        mappings[generic_field] = text
                else:
                    print(f"     ❌ No field match found - text will be skipped")
        
        return mappings
    
    def _map_page2_sections(self, sections: List[Dict], available_fields: Dict[str, str] = None) -> Dict[str, str]:
        """Map Page 2 sections to form fields using intelligent field matching."""
        mappings = {}
        available_fields = available_fields or {}
        
        for i, section in enumerate(sections):
            text = section.get('text', '').strip()
            location = section.get('location', '').lower()
            
            if not text:
                continue
            
            print(f"  📝 Section {i+1}: '{text[:50]}...' at '{location}'")
            
            # Try to find the best matching field for this text
            best_field = self._find_best_field_match(text, location, available_fields, page=2)
            
            if best_field:
                print(f"     ✅ Matched to field: '{best_field}'")
                if best_field in mappings:
                    mappings[best_field] += '\n' + text
                else:
                    mappings[best_field] = text
            else:
                # Fallback to generic mapping if no specific field found
                generic_field = self._get_generic_page2_field(available_fields)
                if generic_field:
                    print(f"     🔄 Using fallback field: '{generic_field}'")
                    if generic_field in mappings:
                        mappings[generic_field] += '\n' + text
                    else:
                        mappings[generic_field] = text
                else:
                    print(f"     ❌ No field match found - text will be skipped")
        
        return mappings
    
    def _find_best_field_match(self, text: str, location: str, available_fields: Dict[str, str], page: int) -> str:
        """Find the best matching field name for given text and location using sophisticated mapping."""
        text_lower = text.lower()
        location_lower = location.lower()
        
        if page == 1:
            return self._match_page1_field(text_lower, location_lower, available_fields)
        elif page == 2:
            return self._match_page2_field(text_lower, location_lower, available_fields)
        
        return None
    
    def _match_page1_field(self, text_lower: str, location_lower: str, available_fields: Dict[str, str]) -> str:
        """Match Page 1 text to specific field names based on content and position."""
        
        # Check for specific content matches first
        if any(keyword in text_lower for keyword in ['danger', 'eliminate', 'risk', 'threat', 'avoid', 'prevent']):
            for field_name in available_fields.keys():
                if 'danger' in field_name.lower() and 'eliminate' in field_name.lower():
                    return field_name
        
        if any(keyword in text_lower for keyword in ['opportunit', 'focus', 'capture', 'chance', 'potential']):
            for field_name in available_fields.keys():
                if 'opportunit' in field_name.lower() and 'focus' in field_name.lower():
                    return field_name
        
        if any(keyword in text_lower for keyword in ['strength', 'reinforce', 'maximi', 'strong', 'advantage']):
            for field_name in available_fields.keys():
                if 'strength' in field_name.lower() and 'reinforce' in field_name.lower():
                    return field_name
        
        # Position-based matching for right-side fields
        if any(pos in location_lower for pos in ['right', 'center right', 'middle right']):
            # Try to match to specific right-side fields based on vertical position
            if any(pos in location_lower for pos in ['top', 'upper', 'high']):
                for field_name in available_fields.keys():
                    if field_name.lower() == 'right_mid':
                        return field_name
            elif any(pos in location_lower for pos in ['middle', 'center', 'mid']):
                for field_name in available_fields.keys():
                    if field_name.lower() == 'right_belowmid':
                        return field_name
            elif any(pos in location_lower for pos in ['bottom', 'lower', 'down']):
                for field_name in available_fields.keys():
                    if field_name.lower() == 'right_bottom':
                        return field_name
        
        # Check for More4Life signature/branding
        if any(keyword in text_lower for keyword in ['more4life', 'm4lfs', 'brookvale', 'dale street']):
            for field_name in available_fields.keys():
                if 'more4life' in field_name.lower():
                    return field_name
        
        return None
    
    def _match_page2_field(self, text_lower: str, location_lower: str, available_fields: Dict[str, str]) -> str:
        """Match Page 2 text to specific field names based on content and position."""
        
        # Category-based matching (money, business, leisure, health, family)
        category = None
        if any(keyword in text_lower for keyword in ['money', 'financial', 'finance', '$', 'dollar', 'cash', 'income', 'salary']):
            category = 'money'
        elif any(keyword in text_lower for keyword in ['business', 'work', 'career', 'job', 'company', 'office']):
            category = 'business'
        elif any(keyword in text_lower for keyword in ['leisure', 'hobby', 'fun', 'vacation', 'travel', 'entertainment']):
            category = 'leisure'
        elif any(keyword in text_lower for keyword in ['health', 'fitness', 'medical', 'doctor', 'exercise', 'diet']):
            category = 'health'
        elif any(keyword in text_lower for keyword in ['family', 'child', 'kids', 'spouse', 'parent', 'home']):
            category = 'family'
        
        if category:
            # Determine if it's GOALS, NOW, or TO DO based on content
            field_type = None
            if any(keyword in text_lower for keyword in ['goal', 'want', 'wish', 'dream', 'aim', 'target']):
                field_type = 'goals'
            elif any(keyword in text_lower for keyword in ['now', 'current', 'today', 'present', 'doing']):
                field_type = 'now'
            elif any(keyword in text_lower for keyword in ['todo', 'to do', 'action', 'plan', 'next', 'will']):
                field_type = 'todo'
            
            # Try to match based on position if content doesn't give clear indication
            if not field_type:
                if any(pos in location_lower for pos in ['top', 'upper', 'first']):
                    field_type = 'goals'
                elif any(pos in location_lower for pos in ['middle', 'center']):
                    field_type = 'now'
                elif any(pos in location_lower for pos in ['bottom', 'lower', 'last']):
                    field_type = 'todo'
            
            # Find the exact field name
            if field_type:
                target_field = f"{category}_{field_type}"
                for field_name in available_fields.keys():
                    if field_name.lower() == target_field:
                        return field_name
        
        # Position-based fallback matching for columns
        if any(pos in location_lower for pos in ['left', 'first column']):
            # Money column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'money_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'money_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'money_todo'
        elif any(pos in location_lower for pos in ['center left', 'second column']):
            # Business column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'business_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'business_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'business_todo'
        elif any(pos in location_lower for pos in ['center', 'middle column', 'third column']):
            # Leisure column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'leisure_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'leisure_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'leisure_todo'
        elif any(pos in location_lower for pos in ['center right', 'fourth column']):
            # Health column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'health_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'health_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'health_todo'
        elif any(pos in location_lower for pos in ['right', 'last column', 'fifth column']):
            # Family column
            if any(pos in location_lower for pos in ['top', 'upper']):
                return 'family_goals'
            elif any(pos in location_lower for pos in ['middle', 'center']):
                return 'family_now'
            elif any(pos in location_lower for pos in ['bottom', 'lower']):
                return 'family_todo'
        
        return None
    
    def _get_generic_page1_field(self, available_fields: Dict[str, str]) -> str:
        """Get a generic field for Page 1 content that doesn't match specific fields."""
        # Look for generic fields like 'notes', 'additional', 'other', etc.
        for field_name in available_fields.keys():
            if any(keyword in field_name.lower() for keyword in ['note', 'additional', 'other', 'general', 'misc']):
                return field_name
        
        # If no generic field, return the first available Page 1 field
        page1_fields = [name for name, page in available_fields.items() if page == 'page_1']
        return page1_fields[0] if page1_fields else None
    
    def _get_generic_page2_field(self, available_fields: Dict[str, str]) -> str:
        """Get a generic field for Page 2 content that doesn't match specific fields."""
        # Return the first available Page 2 field
        page2_fields = [name for name, page in available_fields.items() if page == 'page_2']
        return page2_fields[0] if page2_fields else None
    
    def save_custom_fields_config(self, config_path: Path = None):
        """Save the current field configuration to a JSON file for customization."""
        config_path = config_path or Path("custom_field_positions.json")
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.form_fields_config, f, indent=2)
            print(f"✅ Saved field configuration to: {config_path}")
            print(f"📝 Edit this file to customize field positions")
            return config_path
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return None
    
    def load_custom_fields_config(self, config_path: Path = None) -> Dict:
        """Load custom field configuration from a JSON file."""
        config_path = config_path or Path("custom_field_positions.json")
        
        try:
            if not config_path.exists():
                print(f"⚠️ Config file not found: {config_path}")
                return self._get_default_form_fields_config()
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Loaded custom field configuration from: {config_path}")
            return config
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return self._get_default_form_fields_config()
    
    def create_template_with_custom_fields(self, config_path: Path = None, output_path: Path = None) -> Path:
        """Create a template using custom field positions from a JSON file."""
        custom_config = self.load_custom_fields_config(config_path)
        
        # Temporarily use custom config
        original_config = self.form_fields_config
        self.form_fields_config = custom_config
        
        try:
            template_path = self.create_template_with_form_fields(output_path)
            return template_path
        finally:
            # Restore original config
            self.form_fields_config = original_config

def test_template_processor():
    """Test the template processor."""
    print("🧪 Testing A3 Template Processor")
    print("=" * 40)
    
    processor = A3TemplateProcessor()
    
    # Test creating template with form fields
    try:
        template_path = processor.create_template_with_form_fields()
        print(f"✅ Successfully created template with form fields")
        
        # Test with sample data
        sample_results = [
            {
                'success': True,
                'page_number': 1,
                'sections': [
                    {'text': 'Getting back into property market', 'location': 'left circle danger'},
                    {'text': 'Borrow up to $625,000', 'location': 'right center'}
                ]
            },
            {
                'success': True,
                'page_number': 2,
                'sections': [
                    {'text': 'GOALS\n-Save for house deposit', 'location': 'second row left'},
                    {'text': 'NOW\n-Looking at properties', 'location': 'third row left'}
                ]
            }
        ]
        
        output_path = processor.populate_template(sample_results)
        print(f"✅ Successfully created populated template: {output_path}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    import time
    test_template_processor() 