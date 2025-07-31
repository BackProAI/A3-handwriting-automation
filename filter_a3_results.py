#!/usr/bin/env python3
"""
A3 Document Results Filter
Filter GPT-4o OCR results for More4Life A3 documents based on content rules
"""

import re
from typing import Dict, List

class A3DocumentFilter:
    """Filter for More4Life A3 document OCR results."""
    
    def __init__(self):
        # Specific texts to remove from Page 1 (headers/labels)
        self.page1_remove_texts = [
            "DOS Conversation",
            "Dangers to be eliminated",
            "opportunities to be focused on & captured", 
            "Strengths to be reinforced & maximised",
            "More4Life Financial Services Pty Ltd ABN 68 126 525 737 AFSL No 316809\n225/20 Dale Street Brookvale NSW 2100 Tel 02 9939 0702 Fax 02 9939 0706\nEmail info@m4lfs.com.au Web www.m4lfs.com.au",
            "more4life FINANCIAL SERVICES",
            "money business leisure health family"
        ]
        
        # Additional patterns for company info (flexible matching)
        self.company_info_patterns = [
            r"More4Life Financial Services Pty Ltd",
            r"ABN \d+ \d+ \d+ \d+",
            r"AFSL No \d+",
            r"Dale Street Brookvale NSW",
            r"Tel \d+ \d+ \d+",
            r"Fax \d+ \d+ \d+",
            r"Email info@m4lfs\.com\.au",
            r"Web www\.m4lfs\.com\.au",
            r"more4life\s*FINANCIAL SERVICES",
        ]
        
        # Page 2 content categories to keep
        self.page2_keep_categories = [
            "goals", "goal", "now", "to do", "todo", "action"
        ]
    
    def should_remove_page1_text(self, text: str) -> bool:
        """Check if Page 1 text should be removed (exact header/label matches)."""
        text_clean = text.strip()
        
        # Check for exact matches (case insensitive)
        for remove_text in self.page1_remove_texts:
            if remove_text.lower() in text_clean.lower():
                return True
        
        # Check regex patterns for company info
        for pattern in self.company_info_patterns:
            if re.search(pattern, text_clean, re.IGNORECASE):
                return True
        
        return False
    
    def is_company_info(self, text: str) -> bool:
        """Check if text contains company contact information."""
        text_lower = text.lower()
        
        # Check for any company info patterns
        for pattern in self.company_info_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Additional checks for contact info
        if any(keyword in text_lower for keyword in [
            "financial services", "abn", "afsl", "brookvale", 
            "dale street", "info@m4lfs", "www.m4lfs"
        ]):
            return True
        
        return False
    
    def is_page2_relevant(self, text: str, location: str) -> bool:
        """Check if Page 2 content should be kept (GOALS/NOW/TO DO)."""
        combined_text = (text + " " + location).lower()
        
        # Look for goal-related content
        goal_indicators = [
            "goal", "goals", "now", "to do", "todo", "action",
            "-", "•", "accomplish", "achieve", "plan"
        ]
        
        # Check if it contains any goal indicators
        if any(indicator in combined_text for indicator in goal_indicators):
            return True
        
        # Additional check: if text starts with dash or bullet, likely a goal
        if re.match(r'^[-•*]\s*', text.strip()):
            return True
        
        return False
    
    def filter_page1_sections(self, sections: List[Dict]) -> List[Dict]:
        """Filter Page 1 sections based on location and content rules."""
        filtered_sections = []
        
        for section in sections:
            text = section.get('text', '').strip()
            location = section.get('location', '').lower()
            
            if not text:
                continue
            
            # Filter out left side content that's NOT inside circles
            if "left" in location and "inside circle" not in location:
                print(f"   🗑️  Filtered out left non-circle: {text[:50]}...")
                continue
            
            # Filter out bottom right company branding
            if "bottom right" in location and (
                "more4life" in text.lower() or
                "financial services" in text.lower() or
                "money business leisure health family" in text.lower()
            ):
                print(f"   🗑️  Filtered out bottom right branding: {text[:50]}...")
                continue
            
            # Filter out bottom center contact info
            if ("bottom center" in location or "bottom centre" in location) and (
                "more4life financial services pty ltd" in text.lower() or
                "abn" in text.lower() or
                "dale street brookvale" in text.lower() or
                "info@m4lfs" in text.lower()
            ):
                print(f"   🗑️  Filtered out bottom center contact: {text[:50]}...")
                continue
            
            # Keep everything else
            print(f"   ✅ Kept content: {text[:50]}...")
            filtered_sections.append(section)
        
        return filtered_sections
    
    def filter_page2_sections(self, sections: List[Dict]) -> List[Dict]:
        """Filter Page 2 sections to keep only GOALS/NOW/TO DO content."""
        filtered_sections = []
        
        for section in sections:
            text = section.get('text', '').strip()
            location = section.get('location', '').lower()
            
            if not text:
                continue
            
            # Filter out the "turn the page" instruction (anywhere on page 2)
            text_lower = text.lower()
            if ("now it is time to eliminate dangers" in text_lower or 
                "please turn the page to complete" in text_lower or
                ("turn the page" in text_lower and "complete" in text_lower)):
                print(f"   🗑️  Filtered out page instruction: {text[:50]}...")
                continue
            
            # Filter out top row category labels
            if "top" in location and text_lower.strip() in ["money", "business", "leisure", "health", "family"]:
                print(f"   🗑️  Filtered out top row label: {text[:50]}...")
                continue
            
            # Filter out empty GOALS/NOW/TO DO sections (labels with no content)
            text_clean = text.strip()
            if text_clean.upper() in ["GOALS", "NOW", "TO DO"]:
                print(f"   🗑️  Filtered out empty label: {text[:50]}...")
                continue
            
            # Check if it's relevant goal/action content
            if self.is_page2_relevant(text, location):
                print(f"   ✅ Kept goal content: {text[:50]}...")
                filtered_sections.append(section)
            else:
                print(f"   🗑️  Filtered out non-goal: {text[:50]}...")
        
        return filtered_sections
    
    def filter_results(self, results: List[Dict], page_number: int = None) -> List[Dict]:
        """Filter OCR results based on page number and content rules."""
        print(f"\n🔍 Filtering results for page {page_number}...")
        
        if page_number == 1:
            return self.filter_page1_sections(results)
        elif page_number == 2:
            return self.filter_page2_sections(results)
        else:
            # Unknown page, apply general filtering (remove company info)
            print("   ⚠️  Unknown page number, applying general filtering...")
            filtered = []
            for section in results:
                text = section.get('text', '').strip()
                if text and not self.is_company_info(text):
                    filtered.append(section)
            return filtered

def filter_gpt4o_results(ocr_results: Dict, document_name: str = "A3 Document") -> Dict:
    """
    Filter GPT-4o OCR results for A3 More4Life documents.
    
    Args:
        ocr_results: Dictionary containing OCR results with 'sections' key
        document_name: Name of document being processed
    
    Returns:
        Filtered OCR results dictionary
    """
    print(f"\n📋 Filtering OCR results for: {document_name}")
    
    if not ocr_results.get('success', True):
        print("❌ OCR failed, returning original results")
        return ocr_results
    
    sections = ocr_results.get('sections', [])
    if not sections:
        print("⚠️  No sections found to filter")
        return ocr_results
    
    # Determine page number from document name
    page_number = None
    if "page 1" in document_name.lower():
        page_number = 1
    elif "page 2" in document_name.lower():
        page_number = 2
    
    # Initialize filter
    filter_instance = A3DocumentFilter()
    
    # Apply filtering
    filtered_sections = filter_instance.filter_results(sections, page_number)
    
    # Create new results with filtered sections
    filtered_results = ocr_results.copy()
    filtered_results['sections'] = filtered_sections
    filtered_results['total_sections'] = len(filtered_sections)
    
    # Add filtering metadata
    original_count = len(sections)
    filtered_count = len(filtered_sections)
    filtered_results['filtering_applied'] = True
    filtered_results['original_section_count'] = original_count
    filtered_results['filtered_section_count'] = filtered_count
    filtered_results['sections_removed'] = original_count - filtered_count
    
    print(f"📊 Filtering complete: {original_count} → {filtered_count} sections ({filtered_count/original_count*100:.1f}% kept)")
    
    return filtered_results

# Example usage function
def test_filter():
    """Test the filtering system with sample data."""
    print("🧪 Testing A3 Document Filter")
    print("=" * 40)
    
    # Test Page 1 (location-based filtering)
    page1_results = {
        'success': True,
        'sections': [
            {
                'section_id': 1,
                'location': 'top left',
                'text': 'DOS Conversation',
                'confidence': 'high'
            },
            {
                'section_id': 2,
                'location': 'middle left',
                'text': 'Dangers to be eliminated',
                'confidence': 'high'
            },
            {
                'section_id': 3,
                'location': 'middle left, inside circle',
                'text': '- Getting back into the property market\n- Not earning enough to support lifestyle',
                'confidence': 'medium'
            },
            {
                'section_id': 4,
                'location': 'middle right',
                'text': '- Borrow up to $625,000 with monthly repayments',
                'confidence': 'medium'
            },
            {
                'section_id': 5,
                'location': 'bottom center',
                'text': 'More4Life Financial Services Pty Ltd ABN 68 126 525 737\nDale Street Brookvale NSW',
                'confidence': 'high'
            },
            {
                'section_id': 6,
                'location': 'bottom right',
                'text': 'more4life FINANCIAL SERVICES',
                'confidence': 'high'
            }
        ],
        'total_sections': 6
    }
    
    # Test Page 2 (goal filtering + page instruction removal + top row labels + empty labels)
    page2_results = {
        'success': True,
        'sections': [
            {
                'section_id': 1,
                'location': 'top left',
                'text': 'money',
                'confidence': 'high'
            },
            {
                'section_id': 2,
                'location': 'top center left',
                'text': 'business',
                'confidence': 'high'
            },
            {
                'section_id': 3,
                'location': 'second row left',
                'text': 'GOALS\n-look at purchasing property',
                'confidence': 'high'
            },
            {
                'section_id': 4,
                'location': 'second row center',
                'text': 'GOALS',
                'confidence': 'high'
            },
            {
                'section_id': 5,
                'location': 'third row left',
                'text': 'NOW\n-Actively looking at strategy role',
                'confidence': 'high'
            },
            {
                'section_id': 6,
                'location': 'fourth row center',
                'text': 'TO DO',
                'confidence': 'high'
            },
            {
                'section_id': 7,
                'location': 'fourth row right',
                'text': 'TO DO\n-make time for exercise',
                'confidence': 'high'
            },
            {
                'section_id': 8,
                'location': 'bottom',
                'text': 'Now it is time to eliminate dangers ...\nPlease turn the page to complete',
                'confidence': 'high'
            }
        ],
        'total_sections': 8
    }
    
    # Test Page 1 filtering
    print("\n" + "="*50)
    filtered_page1 = filter_gpt4o_results(page1_results, "Test Page 1")
    print(f"Page 1 - Original: {len(page1_results['sections'])} → Filtered: {len(filtered_page1['sections'])}")
    
    # Test Page 2 filtering
    print("\n" + "="*50)
    filtered_page2 = filter_gpt4o_results(page2_results, "Test Page 2")
    print(f"Page 2 - Original: {len(page2_results['sections'])} → Filtered: {len(filtered_page2['sections'])}")
    
    print("\nPage 2 kept sections:")
    for section in filtered_page2['sections']:
        print(f"  ✅ {section['text'][:60]}...")

if __name__ == "__main__":
    test_filter() 