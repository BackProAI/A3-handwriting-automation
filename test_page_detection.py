#!/usr/bin/env python3
"""
Test Page Detection System
Demonstrates automatic page order detection and correction
"""

import fitz  # PyMuPDF
from pathlib import Path
from sectioned_gpt4o_ocr import SectionedGPT4oOCR
import sys

def test_page_detection(pdf_path: Path):
    """Test the page detection system on a PDF"""
    
    print("🧪 PAGE DETECTION TEST")
    print("=" * 50)
    print(f"📄 Testing: {pdf_path}")
    
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return False
    
    try:
        # Initialize the OCR processor
        ocr = SectionedGPT4oOCR()
        
        # Open PDF for direct analysis
        pdf_doc = fitz.open(pdf_path)
        print(f"📖 PDF has {len(pdf_doc)} page(s)")
        
        if len(pdf_doc) < 2:
            print("⚠️ Single page document - no page detection needed")
            pdf_doc.close()
            return True
        
        # Show raw text from each page for manual verification
        print(f"\n📝 RAW TEXT ANALYSIS:")
        print("=" * 30)
        
        for page_num in range(min(2, len(pdf_doc))):
            page = pdf_doc[page_num]
            page_text = page.get_text()
            
            print(f"\n🔍 PHYSICAL PAGE {page_num + 1} Content Preview:")
            print("-" * 40)
            
            # Show actual text length and content
            print(f"   Text Length: {len(page_text)} characters")
            
            if len(page_text.strip()) == 0:
                print(f"   ⚠️ NO TEXT EXTRACTED - May be scanned image")
                # Try alternative text extraction
                try:
                    text_dict = page.get_text("dict")
                    print(f"   📊 Found {len(text_dict.get('blocks', []))} text blocks")
                except:
                    print(f"   ❌ Alternative extraction failed")
            else:
                # Show first 300 characters with proper formatting
                preview = page_text[:300].replace('\n', ' ').strip()
                if preview:
                    print(f"   Preview: {preview}...")
                else:
                    print(f"   Preview: [Empty or whitespace only]")
            
            # Show key indicators with more detailed search
            text_lower = page_text.lower()
            
            page1_indicators = []
            page1_keywords = ['danger', 'eliminate', 'risk', 'threat', 'opportunit', 'focus', 'capture', 'strength', 'reinforce', 'maximi', 'grateful', 'appreciate']
            for keyword in page1_keywords:
                if keyword in text_lower:
                    page1_indicators.append(keyword)
            
            page2_indicators = []  
            page2_keywords = ['goal', 'money', 'financial', 'health', 'family', 'business', 'leisure', 'now', 'current', 'todo', 'action']
            for keyword in page2_keywords:
                if keyword in text_lower:
                    page2_indicators.append(keyword)
            
            print(f"   Page 1 Indicators: {page1_indicators}")
            print(f"   Page 2 Indicators: {page2_indicators}")
            
            # Show some sample lines for manual verification
            lines = [line.strip() for line in page_text.split('\n') if line.strip()]
            if lines:
                print(f"   Sample Lines ({len(lines)} total):")
                for i, line in enumerate(lines[:5]):  # Show first 5 lines
                    print(f"      {i+1}: {line[:60]}{'...' if len(line) > 60 else ''}")
            else:
                print(f"   ⚠️ No readable lines found")
        
        # Test the detection system
        print(f"\n🤖 AUTOMATED DETECTION:")
        print("=" * 30)
        
        correct_order = ocr.detect_and_reorder_pages(pdf_doc)
        
        print(f"\n📋 FINAL RESULT:")
        print(f"   Detected Order: {correct_order}")
        
        if correct_order == [0, 1]:
            print(f"   ✅ Pages are in CORRECT order")
        elif correct_order == [1, 0]:
            print(f"   🔄 Pages need to be SWAPPED")
            print(f"   📄 Physical Page 1 → Logical Page 2")
            print(f"   📄 Physical Page 2 → Logical Page 1")
        
        pdf_doc.close()
        
        print(f"\n✅ Page detection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Test page detection with sample documents"""
    
    if len(sys.argv) > 1:
        # Test specific file
        pdf_path = Path(sys.argv[1])
        test_page_detection(pdf_path)
    else:
        # Test with sample files
        test_files = [
            Path("test_images/DOS Conversation.pdf"),
            # Add more test files here
        ]
        
        print("🚀 TESTING PAGE DETECTION SYSTEM")
        print("=" * 60)
        
        for test_file in test_files:
            if test_file.exists():
                print(f"\n{'='*20} TESTING {test_file.name} {'='*20}")
                test_page_detection(test_file)
            else:
                print(f"\n⚠️ Test file not found: {test_file}")
        
        print(f"\n🎯 USAGE:")
        print(f"   Test specific file: python test_page_detection.py <path_to_pdf>")
        print(f"   Example: python test_page_detection.py 'test_images/my_document.pdf'")

if __name__ == "__main__":
    main()