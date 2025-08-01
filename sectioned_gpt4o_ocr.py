#!/usr/bin/env python3
"""
Sectioned GPT-4o OCR System
Uses manually defined sections for 100% consistent OCR results
"""

import os
import json
import base64
import time
from pathlib import Path
from PIL import Image
import requests
from typing import Dict, List, Any, Tuple
import fitz  # PyMuPDF

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

class SectionedGPT4oOCR:
    """GPT-4o OCR with manual section definitions for consistent results."""
    
    def __init__(self, api_key: str = None, section_config_path: str = "a3_section_config.json"):
        """Initialize sectioned OCR with API key and section configuration."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Load section configuration
        self.section_config_path = Path(section_config_path)
        self.sections = self.load_section_config()
        
        # Reference template size (size sections were defined on)
        self.reference_template_size = None
        self.load_reference_template_size()
        
        print(f"✅ Sectioned GPT-4o OCR initialized")
        print(f"📂 Section config: {self.section_config_path}")
        if self.sections:
            total_sections = sum(len(self.sections[page]) for page in self.sections if not page.startswith("_"))
            print(f"🎯 Loaded {total_sections} predefined sections")
        if self.reference_template_size:
            print(f"📐 Reference template size: {self.reference_template_size[0]}x{self.reference_template_size[1]}")
    
    def load_section_config(self) -> Dict:
        """Load section definitions from JSON file."""
        if not self.section_config_path.exists():
            print(f"⚠️ Section config not found: {self.section_config_path}")
            print("💡 Create sections using: python section_definition_tool.py")
            return {}
        
        try:
            with open(self.section_config_path, 'r') as f:
                config = json.load(f)
            
            print(f"📖 Loaded section configuration from {self.section_config_path}")
            return config
            
        except Exception as e:
            print(f"❌ Failed to load section config: {e}")
            return {}
    
    def load_reference_template_size(self):
        """Load reference template size from config or detect from blank template."""
        # First, try to load from section config
        if self.sections and '_metadata' in self.sections:
            metadata = self.sections['_metadata']
            if 'reference_template_size' in metadata:
                self.reference_template_size = metadata['reference_template_size']
                return
        
        # If not in config, try to detect from blank A3 template
        template_candidates = [
            Path("A3_templates/More4Life A3 Goals - blank.pdf"),
            Path("processed_documents/A3_Custom_Template.pdf")
        ]
        
        # Add glob results
        template_dir = Path("A3_templates")
        if template_dir.exists():
            template_candidates.extend(template_dir.glob("*blank*.pdf"))
            template_candidates.extend(template_dir.glob("*template*.pdf"))
        
        for template_path in template_candidates:
            if template_path.exists():
                try:
                    self.reference_template_size = self.get_pdf_page_size(template_path)
                    print(f"📐 Detected reference template size from: {template_path.name}")
                    return
                except Exception as e:
                    continue
        
        # Fallback to A3 standard size at 2x zoom (same as processing)
        # A3 = 297 × 420 mm, at 300 DPI ≈ 3508 × 4961 pixels, at 2x zoom
        self.reference_template_size = (7016, 9922)  # A3 at 2x zoom
        print(f"⚠️ Using fallback A3 reference size: {self.reference_template_size[0]}x{self.reference_template_size[1]}")
    
    def get_pdf_page_size(self, pdf_path: Path) -> tuple:
        """Get the pixel size of first page of PDF at 2x zoom (same as processing)."""
        pdf_doc = fitz.open(pdf_path)
        page = pdf_doc[0]
        
        # Same 2x zoom as used in processing
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        
        size = (pix.width, pix.height)
        pdf_doc.close()
        return size
    
    def standardize_page_size(self, image: Image.Image) -> Image.Image:
        """Standardize page image to reference template size."""
        if not self.reference_template_size:
            return image
        
        current_size = image.size
        target_size = self.reference_template_size
        
        if current_size == target_size:
            print(f"   📐 Image already at reference size")
            return image
        
        print(f"   📐 Scaling from {current_size[0]}x{current_size[1]} to {target_size[0]}x{target_size[1]}")
        
        # Use high-quality resizing
        resized_image = image.resize(target_size, Image.Resampling.LANCZOS)
        return resized_image
    
    def encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64 for API."""
        import io
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def crop_section(self, image: Image.Image, rect: List[float]) -> Image.Image:
        """Crop image to specific section coordinates."""
        x1, y1, x2, y2 = rect
        
        # Ensure coordinates are within image bounds
        x1 = max(0, min(x1, image.width))
        y1 = max(0, min(y1, image.height))
        x2 = max(x1, min(x2, image.width))
        y2 = max(y1, min(y2, image.height))
        
        # Crop the image
        cropped = image.crop((int(x1), int(y1), int(x2), int(y2)))
        
        # Ensure minimum size
        if cropped.width < 50 or cropped.height < 50:
            print(f"⚠️ Section too small: {cropped.width}x{cropped.height}")
            return None
        
        return cropped
    
    def extract_text_from_section(self, section_image: Image.Image, section_name: str) -> Dict[str, Any]:
        """Extract text from a single section using GPT-4o."""
        print(f"   🔍 Processing section: {section_name}")
        
        # Encode image
        base64_image = self.encode_image(section_image)
        
        # Create focused prompt for single section text extraction
        prompt = f"""You are an expert OCR system specializing in handwritten text recognition. Analyze this cropped section from an A3 document form.

TASK: Extract ALL handwritten text that appears in this image section.

CRITICAL INSTRUCTIONS:
1. **HANDWRITTEN TEXT FOCUS**: This section likely contains handwritten text (cursive, print, or mixed)
2. **LOOK CAREFULLY**: Handwritten text may be light, faint, or low contrast - examine closely
3. **EXTRACT EVERYTHING**: Include partial words, crossed-out text, and marginal notes
4. **PRESERVE STRUCTURE**: Maintain line breaks, bullet points, and formatting
5. **NO HALLUCINATION**: Only return text that actually exists in the image
6. **CONTEXT CLUES**: This is from a goals/planning document - text may include goals, actions, thoughts

HANDWRITING RECOGNITION TIPS:
- Look for pen/pencil marks of any darkness level
- Check all areas of the section, including edges
- Consider cursive writing, print writing, and mixed styles
- Look for faint or light handwriting
- Include incomplete words if visible

Return the extracted text directly, no JSON formatting needed. If absolutely no text is visible after careful examination, return "NO_TEXT_FOUND"."""

        # API payload - simple text response
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0
        }
        
        try:
            start_time = time.time()
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content'].strip()
                
                # Handle empty results
                if not extracted_text or extracted_text == "NO_TEXT_FOUND":
                    print(f"       ⚪ No text found in section")
                    return {
                        "success": True,
                        "text": "",
                        "processing_time": processing_time,
                        "confidence": "low"
                    }
                
                print(f"       ✅ Extracted: '{extracted_text[:50]}{'...' if len(extracted_text) > 50 else ''}'")
                return {
                    "success": True,
                    "text": extracted_text,
                    "processing_time": processing_time,
                    "confidence": "high"
                }
            
            else:
                error_msg = f"API error {response.status_code}: {response.text}"
                print(f"       ❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "processing_time": processing_time
                }
        
        except Exception as e:
            error_msg = f"Request failed: {e}"
            print(f"       ❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "processing_time": 0
            }
    
    def process_page_sections(self, image: Image.Image, page_number: int) -> List[Dict[str, Any]]:
        """Process all sections for a specific page."""
        page_key = f"page_{page_number}"
        
        if page_key not in self.sections or not self.sections[page_key]:
            print(f"⚠️ No sections defined for page {page_number}")
            return []
        
        page_sections = self.sections[page_key]
        print(f"📄 Processing Page {page_number}: {len(page_sections)} sections")
        
        results = []
        
        for section in page_sections:
            section_name = section["name"]
            section_rect = section["rect"]
            target_field = section.get("target_field", "")
            
            print(f"\n   📍 Section: {section_name}")
            print(f"       📐 Coordinates: ({section_rect[0]:.0f}, {section_rect[1]:.0f}) → ({section_rect[2]:.0f}, {section_rect[3]:.0f})")
            print(f"       🎯 Target field: {target_field or 'Not mapped'}")
            
            # Crop section from image
            section_image = self.crop_section(image, section_rect)
            
            if section_image is None:
                print(f"       ❌ Failed to crop section")
                continue
            
            # Extract text from this section
            extraction_result = self.extract_text_from_section(section_image, section_name)
            
            # Build section result
            section_result = {
                "section_id": section["id"],
                "section_name": section_name,
                "target_field": target_field,
                "rect": section_rect,
                "text": extraction_result.get("text", ""),
                "success": extraction_result["success"],
                "processing_time": extraction_result.get("processing_time", 0),
                "confidence": extraction_result.get("confidence", "low")
            }
            
            if not extraction_result["success"]:
                section_result["error"] = extraction_result.get("error", "Unknown error")
            
            results.append(section_result)
        
        return results
    
    def process_document(self, document_path: Path) -> Dict[str, Any]:
        """Process entire document using sectioned approach."""
        print(f"\n🎯 SECTIONED GPT-4o OCR: {document_path}")
        print("="*80)
        
        if not self.sections:
            return {
                "success": False,
                "error": "No section configuration loaded",
                "results": []
            }
        
        try:
            total_start_time = time.time()
            all_results = []
            
            if document_path.suffix.lower() == '.pdf':
                # Process PDF
                print("📄 Processing PDF document...")
                
                pdf_doc = fitz.open(document_path)
                
                for page_num in range(min(2, len(pdf_doc))):  # Max 2 pages
                    page = pdf_doc[page_num]
                    
                    # Convert page to high-resolution image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convert to PIL Image
                    import io
                    img_data = pix.tobytes("png")
                    page_image = Image.open(io.BytesIO(img_data))
                    
                    print(f"\n📄 Processing PDF Page {page_num + 1}")
                    print(f"   📐 Original image size: {page_image.width}x{page_image.height}")
                    
                    # Standardize page size to match reference template
                    page_image = self.standardize_page_size(page_image)
                    print(f"   📐 Standardized image size: {page_image.width}x{page_image.height}")
                    
                    # Process sections for this page
                    page_results = self.process_page_sections(page_image, page_num + 1)
                    
                    # Add page info to results
                    for result in page_results:
                        result["page_number"] = page_num + 1
                        result["file_name"] = document_path.name
                        result["file_type"] = "PDF"
                    
                    all_results.extend(page_results)
                
                pdf_doc.close()
            
            else:
                # Process image
                print("🖼️ Processing image document...")
                
                with Image.open(document_path) as img:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    print(f"   📐 Original image size: {img.width}x{img.height}")
                    
                    # Standardize page size to match reference template
                    img = self.standardize_page_size(img)
                    print(f"   📐 Standardized image size: {img.width}x{img.height}")
                    
                    # Process sections (assume page 1 for images)
                    page_results = self.process_page_sections(img, 1)
                    
                    # Add file info to results
                    for result in page_results:
                        result["page_number"] = 1
                        result["file_name"] = document_path.name
                        result["file_type"] = "Image"
                    
                    all_results.extend(page_results)
            
            total_processing_time = time.time() - total_start_time
            
            # Summary
            successful_sections = [r for r in all_results if r["success"]]
            sections_with_text = [r for r in successful_sections if r["text"].strip()]
            
            print(f"\n🎉 SECTIONED OCR COMPLETE")
            print("="*50)
            print(f"📊 Total sections processed: {len(all_results)}")
            print(f"✅ Successful extractions: {len(successful_sections)}")
            print(f"📝 Sections with text: {len(sections_with_text)}")
            print(f"⏱️ Total processing time: {total_processing_time:.2f}s")
            
            return {
                "success": True,
                "file_name": document_path.name,
                "total_sections": len(all_results),
                "successful_sections": len(successful_sections),
                "sections_with_text": len(sections_with_text),
                "total_processing_time": total_processing_time,
                "results": all_results
            }
        
        except Exception as e:
            error_msg = f"Document processing failed: {e}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "results": []
            }

def display_sectioned_results(processing_result: Dict[str, Any]):
    """Display results from sectioned OCR processing."""
    if not processing_result["success"]:
        print(f"❌ Processing failed: {processing_result.get('error', 'Unknown error')}")
        return
    
    results = processing_result["results"]
    
    print(f"\n{'='*80}")
    print(f"📋 SECTIONED OCR RESULTS: {processing_result['file_name']}")
    print(f"{'='*80}")
    
    # Group by page
    pages = {}
    for result in results:
        page_num = result["page_number"]
        if page_num not in pages:
            pages[page_num] = []
        pages[page_num].append(result)
    
    for page_num in sorted(pages.keys()):
        page_results = pages[page_num]
        print(f"\n📄 PAGE {page_num}")
        print("-" * 60)
        
        for result in page_results:
            section_name = result["section_name"]
            text = result["text"].strip()
            target_field = result["target_field"]
            success = result["success"]
            
            status_icon = "✅" if success and text else "⚪" if success else "❌"
            field_info = f" → {target_field}" if target_field else ""
            
            print(f"{status_icon} {section_name}{field_info}")
            
            if text:
                # Show first 100 chars of text
                display_text = text[:100] + "..." if len(text) > 100 else text
                print(f"   Text: {display_text}")
            elif success:
                print(f"   Text: (empty)")
            else:
                error = result.get("error", "Unknown error")
                print(f"   Error: {error}")
            
            print()
    
    # Summary
    print(f"📊 SUMMARY:")
    print(f"   📝 Total sections: {processing_result['total_sections']}")
    print(f"   ✅ Successful: {processing_result['successful_sections']}")
    print(f"   📄 With text: {processing_result['sections_with_text']}")
    print(f"   ⏱️ Processing time: {processing_result['total_processing_time']:.2f}s")

def main():
    """Test the sectioned OCR system."""
    print("🎯 Sectioned GPT-4o OCR Test")
    print("="*50)
    
    # Initialize OCR
    try:
        ocr = SectionedGPT4oOCR()
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Find test files
    test_dir = Path("test_images")
    if test_dir.exists():
        files = list(test_dir.glob("*.pdf")) + list(test_dir.glob("*.png")) + list(test_dir.glob("*.jpg"))
        
        if files:
            print(f"📁 Found {len(files)} test files:")
            for i, file in enumerate(files, 1):
                print(f"   {i}. {file.name}")
            
            # Process first file
            test_file = files[0]
            print(f"\n🔄 Testing with: {test_file}")
            
            result = ocr.process_document(test_file)
            display_sectioned_results(result)
        else:
            print("⚠️ No test files found in test_images/")
    else:
        print("⚠️ test_images/ directory not found")
    
    print(f"\n💡 Usage:")
    print(f"   1. Define sections: python section_definition_tool.py")
    print(f"   2. Test OCR: python sectioned_gpt4o_ocr.py")
    print(f"   3. Use in automation: import and use SectionedGPT4oOCR class")

if __name__ == "__main__":
    main()