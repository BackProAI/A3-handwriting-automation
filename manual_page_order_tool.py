#!/usr/bin/env python3
"""
Manual Page Order Tool
For testing and forcing page order when automatic detection fails
"""

import sys
from pathlib import Path
from a3_sectioned_automation import A3SectionedProcessor

def test_manual_page_order(pdf_path: Path, order: str):
    """Test processing with manual page order override"""
    
    print("🔧 MANUAL PAGE ORDER TEST")
    print("=" * 50)
    print(f"📄 Document: {pdf_path}")
    print(f"🎯 Forced Order: {order.upper()}")
    
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return False
    
    try:
        # Initialize processor
        processor = A3SectionedProcessor()
        
        # Process with manual override
        if order.lower() == "reversed":
            print(f"\n🔄 Processing with REVERSED page order...")
            print(f"   📄 Physical Page 1 → Logical Page 2")
            print(f"   📄 Physical Page 2 → Logical Page 1")
        else:
            print(f"\n✅ Processing with NORMAL page order...")
            print(f"   📄 Physical Page 1 → Logical Page 1")
            print(f"   📄 Physical Page 2 → Logical Page 2")
        
        # Override the OCR processor's page detection
        original_process = processor.sectioned_ocr.process_document
        
        def override_process_document(doc_path):
            return original_process(doc_path, manual_page_order=order)
        
        processor.sectioned_ocr.process_document = override_process_document
        
        # Process the document
        result_info = processor.process_file(pdf_path)
        
        if result_info and result_info.get('success', False):
            result_path = result_info.get('output_pdf_path') or result_info.get('output_path')
            sections_with_text = result_info.get('sections_with_text', 0)
            sections_processed = result_info.get('sections_processed', 0)
            
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Processed document: {result_path}")
            print(f"📊 Sections with content: {sections_with_text}/{sections_processed}")
            print(f"📁 Check the output to verify page order is correct")
            return True
        else:
            error_msg = result_info.get('error', 'Unknown error') if result_info else 'No result returned'
            print(f"\n❌ Processing failed: {error_msg}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main entry point"""
    
    if len(sys.argv) < 3:
        print("🔧 MANUAL PAGE ORDER TOOL")
        print("=" * 40)
        print(f"📖 Usage:")
        print(f"   python manual_page_order_tool.py <pdf_path> <order>")
        print(f"   ")
        print(f"📋 Parameters:")
        print(f"   pdf_path: Path to PDF document")
        print(f"   order:    'normal' or 'reversed'")
        print(f"   ")
        print(f"💡 Examples:")
        print(f"   # Process with normal page order")
        print(f"   python manual_page_order_tool.py \"document.pdf\" normal")
        print(f"   ")
        print(f"   # Process with reversed page order")
        print(f"   python manual_page_order_tool.py \"document.pdf\" reversed")
        print(f"   ")
        print(f"🎯 Use Cases:")
        print(f"   • When automatic detection fails")
        print(f"   • When you know pages are scanned in wrong order")
        print(f"   • For testing different page configurations")
        return
    
    pdf_path = Path(sys.argv[1])
    order = sys.argv[2]
    
    if order.lower() not in ['normal', 'reversed']:
        print(f"❌ Invalid order: {order}")
        print(f"   Must be 'normal' or 'reversed'")
        return
    
    # Run the test
    success = test_manual_page_order(pdf_path, order)
    
    if success:
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Check the output document")
        print(f"   2. Verify fields are populated in correct positions")
        print(f"   3. If wrong, try the opposite order:")
        print(f"      python manual_page_order_tool.py \"{pdf_path}\" {'normal' if order.lower() == 'reversed' else 'reversed'}")
    else:
        print(f"\n💡 TROUBLESHOOTING:")
        print(f"   • Check file path is correct")
        print(f"   • Ensure PDF is readable")
        print(f"   • Try the opposite order if detection seems wrong")

if __name__ == "__main__":
    main()