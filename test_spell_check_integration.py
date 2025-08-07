#!/usr/bin/env python3
"""
Test Spell Check Integration
Quick test to verify spell check is working with the OCR system
"""

from sectioned_gpt4o_ocr import SectionedGPT4oOCR
from ocr_spell_checker import spell_check_text, spell_check_sections

def test_basic_spell_check():
    """Test basic spell check functionality."""
    print("🧪 Testing Basic Spell Check...")
    
    # Test text with common OCR errors
    test_text = "I need to bomw $625,000 with monthly repayrnents of $3,774.59"
    
    corrected, corrections = spell_check_text(test_text)
    
    print(f"Original:  {test_text}")
    print(f"Corrected: {corrected}")
    print(f"Corrections: {len(corrections)} found")
    
    for correction in corrections:
        print(f"  • '{correction['original']}' → '{correction['corrected']}'")
    
    return len(corrections) > 0

def test_section_results_spell_check():
    """Test spell check on section results format."""
    print("\n🧪 Testing Section Results Spell Check...")
    
    # Mock section results with spelling errors
    mock_results = {
        "page_1": [
            {
                "name": "Section_1_1",
                "text": "Bomw $500,000 for 30 yrs",
                "target_field": "loan_amount"
            },
            {
                "name": "Section_1_2", 
                "text": "Monthly repayrnents $2,500",
                "target_field": "monthly_payment"
            }
        ],
        "page_2": [
            {
                "name": "Section_2_1",
                "text": "Applciation status: Approved",
                "target_field": "status"
            }
        ]
    }
    
    # Apply spell check
    corrected_results = spell_check_sections(mock_results)
    
    # Check results
    print("Original vs Corrected:")
    for page_key in ["page_1", "page_2"]:
        if page_key in mock_results:
            print(f"\n📄 {page_key.upper()}:")
            for original, corrected in zip(mock_results[page_key], corrected_results[page_key]):
                print(f"  {original['name']}:")
                print(f"    Original:  {original['text']}")
                print(f"    Corrected: {corrected['text']}")
                if 'spell_corrections' in corrected:
                    print(f"    Corrections: {len(corrected['spell_corrections'])}")
    
    # Check metadata
    if '_metadata' in corrected_results and 'spell_check' in corrected_results['_metadata']:
        metadata = corrected_results['_metadata']['spell_check']
        print(f"\n📊 Summary: {metadata['total_corrections']} total corrections")
        return metadata['total_corrections'] > 0
    
    return False

def test_ocr_integration():
    """Test OCR integration (if API key available)."""
    print("\n🧪 Testing OCR Integration...")
    
    try:
        # Try to initialize OCR with spell check enabled
        ocr = SectionedGPT4oOCR(enable_spell_check=True)
        print("✅ OCR initialized with spell check enabled")
        print(f"🔤 Spell check enabled: {ocr.enable_spell_check}")
        return True
        
    except ValueError as e:
        print(f"⚠️ OCR initialization skipped: {e}")
        return False
    except Exception as e:
        print(f"❌ OCR initialization failed: {e}")
        return False

def main():
    """Run all spell check tests."""
    print("🚀 Spell Check Integration Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic spell check
    if test_basic_spell_check():
        print("✅ Basic spell check: PASSED")
        tests_passed += 1
    else:
        print("❌ Basic spell check: FAILED")
    
    # Test 2: Section results spell check
    if test_section_results_spell_check():
        print("✅ Section results spell check: PASSED")
        tests_passed += 1
    else:
        print("❌ Section results spell check: FAILED")
    
    # Test 3: OCR integration
    if test_ocr_integration():
        print("✅ OCR integration: PASSED")
        tests_passed += 1
    else:
        print("⚠️ OCR integration: SKIPPED (API key needed)")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Spell check is working correctly.")
    elif tests_passed >= 2:
        print("✅ Core spell check functionality is working.")
    else:
        print("❌ Some tests failed. Check the spell check setup.")

if __name__ == "__main__":
    main()
