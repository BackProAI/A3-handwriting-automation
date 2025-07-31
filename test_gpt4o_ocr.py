#!/usr/bin/env python3
"""
GPT-4o Vision OCR Test Script
Alternative to TrOCR for better printed text recognition
"""

import os
import base64
import time
from pathlib import Path
from PIL import Image
import requests
from typing import List, Tuple
import json

# Add this import near the top with other imports
from filter_a3_results import filter_gpt4o_results

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded API key from secure .env file")
except ImportError:
    # Fallback: manually load .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded API key from .env file (manual)")
    else:
        print("⚠️  No .env file found, using environment variables")

# Optional PDF support
try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
    print("📄 PDF support enabled")
except ImportError:
    PDF_SUPPORT = False
    print("⚠️  PDF support not available (install pdf2image)")

class GPT4oOCR:
    def __init__(self, api_key: str = None):
        """Initialize GPT-4o OCR with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def encode_image(self, image_path: Path) -> str:
        """Encode image to base64 for API."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def extract_text_sections(self, image_path: Path, context: str = "document") -> dict:
        """Extract text using GPT-4o Vision with section awareness."""
        print(f"\n🔍 GPT-4o Vision OCR: {image_path}")
        
        # Encode image
        base64_image = self.encode_image(image_path)
        
        # Create prompt for section-aware OCR
        prompt = f"""You are an expert OCR system. Please analyze this {context} image and:

1. **IDENTIFY SECTIONS**: Find all distinct text sections/areas in the image
2. **EXTRACT TEXT**: For each section, extract the exact text you see
3. **NO HALLUCINATION**: Only return text that actually exists in the image
4. **PRESERVE LAYOUT**: Maintain the spatial relationship between sections

Format your response as JSON:
{{
    "sections": [
        {{
            "section_id": 1,
            "location": "description of where this text appears (e.g., 'top left', 'center', 'bottom right')",
            "text": "exact text found in this section",
            "confidence": "high/medium/low"
        }}
    ],
    "total_sections": number,
    "document_type": "printed/handwritten/mixed"
}}

Be extremely careful to only extract text that actually exists. Do not invent or hallucinate any content."""

        # API payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0  # Low temperature for accuracy
        }
        
        # Make API call
        start_time = time.time()
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            processing_time = time.time() - start_time
            
            # Extract the response content
            content = result['choices'][0]['message']['content']
            
            # Try to parse as JSON
            try:
                # First try direct JSON parsing
                json_content = json.loads(content)
                return {
                    'success': True,
                    'sections': json_content.get('sections', []),
                    'total_sections': json_content.get('total_sections', 0),
                    'document_type': json_content.get('document_type', 'unknown'),
                    'processing_time': processing_time,
                    'raw_response': content
                }
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                try:
                    # Look for JSON in markdown code blocks
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        json_content = json.loads(json_str)
                        return {
                            'success': True,
                            'sections': json_content.get('sections', []),
                            'total_sections': json_content.get('total_sections', 0),
                            'document_type': json_content.get('document_type', 'unknown'),
                            'processing_time': processing_time,
                            'raw_response': content
                        }
                    
                    # Try to find JSON without code blocks
                    json_match = re.search(r'(\{.*?\})', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        json_content = json.loads(json_str)
                        return {
                            'success': True,
                            'sections': json_content.get('sections', []),
                            'total_sections': json_content.get('total_sections', 0),
                            'document_type': json_content.get('document_type', 'unknown'),
                            'processing_time': processing_time,
                            'raw_response': content
                        }
                        
                except (json.JSONDecodeError, AttributeError):
                    pass
                
                # Final fallback: return raw text
                return {
                    'success': True,
                    'sections': [{'section_id': 1, 'location': 'full document', 'text': content, 'confidence': 'medium'}],
                    'total_sections': 1,
                    'document_type': 'unknown',
                    'processing_time': processing_time,
                    'raw_response': content
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }

def find_image_and_pdf_files(directory: Path = Path("test_images")) -> List[Path]:
    """Find all image and PDF files in the directory."""
    if not directory.exists():
        directory = Path(".")
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
    pdf_extensions = {'.pdf'}
    
    all_files = []
    
    # Find images (search both cases but use set to remove duplicates)
    for ext in image_extensions:
        all_files.extend(directory.glob(f"*{ext}"))
        all_files.extend(directory.glob(f"*{ext.upper()}"))
    
    # Find PDFs if supported
    if PDF_SUPPORT:
        for ext in pdf_extensions:
            all_files.extend(directory.glob(f"*{ext}"))
            all_files.extend(directory.glob(f"*{ext.upper()}"))
    
    # Remove duplicates by converting to set and back to list
    unique_files = list(set(all_files))
    
    return sorted(unique_files)

def optimize_image_for_gpt4o(image: Image.Image, max_pixels: int = 1500000) -> Image.Image:
    """Optimize image size for GPT-4o Vision API."""
    original_size = image.size
    original_pixels = original_size[0] * original_size[1]
    
    if original_pixels <= max_pixels:
        return image
    
    # Calculate scaling factor
    scale_factor = (max_pixels / original_pixels) ** 0.5
    new_width = int(original_size[0] * scale_factor)
    new_height = int(original_size[1] * scale_factor)
    
    print(f"   🔄 Optimizing: {original_size[0]}x{original_size[1]} → {new_width}x{new_height}")
    
    # Resize with high quality
    optimized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return optimized

def convert_pdf_to_images(pdf_path: Path) -> List[Image.Image]:
    """Convert PDF pages to PIL Images with optimization for GPT-4o."""
    if not PDF_SUPPORT:
        raise ImportError("PDF support not available")
    
    print(f"📄 Converting PDF to images: {pdf_path}")
    
    try:
        # Check for local Poppler first
        poppler_path = None
        if Path("poppler_config.py").exists():
            import poppler_config
            poppler_path = poppler_config.POPPLER_PATH
            print(f"   🔧 Using local Poppler: {poppler_path}")
    except:
        pass
    
    try:
        # Use lower DPI to reduce initial size
        pages = convert_from_path(
            pdf_path, 
            dpi=200,  # Reduced from 300 to limit initial size
            poppler_path=poppler_path
        )
        print(f"   ✅ Converted {len(pages)} pages from PDF")
        
        # Optimize each page for GPT-4o
        optimized_pages = []
        for i, page in enumerate(pages, 1):
            optimized_page = optimize_image_for_gpt4o(page, max_pixels=1500000)
            optimized_pages.append(optimized_page)
        
        print(f"   ✅ Optimized {len(optimized_pages)} pages for GPT-4o Vision")
        return optimized_pages
        
    except Exception as e:
        print(f"   ❌ PDF conversion failed: {e}")
        if "poppler" in str(e).lower():
            print("\n💡 SOLUTION: Install Poppler for Windows:")
            print("   Run: python install_poppler_windows.py")
        raise

def display_gpt4o_results(result: dict, file_name: str, doc_type: str = "Document"):
    """Display GPT-4o OCR results in a nice format."""
    print(f"\n{'='*80}")
    print(f"📋 GPT-4o OCR RESULTS: {file_name}")
    print(f"{'='*80}")
    
    if not result['success']:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        return
    
    # Header info
    print(f"📊 Document type: {result['document_type']}")
    print(f"📝 Sections found: {result['total_sections']}")
    print(f"⏱️  Processing time: {result['processing_time']:.2f}s")
    
    # Show filtering information if applied
    if result.get('filtering_applied'):
        original_count = result.get('original_section_count', 0)
        filtered_count = result.get('filtered_section_count', 0)
        removed_count = result.get('sections_removed', 0)
        print(f"🔍 A3 Filtering applied: {original_count} → {filtered_count} sections ({removed_count} filtered out)")
    
    # Display sections
    if result['sections']:
        print(f"\n📄 EXTRACTED SECTIONS:")
        print("+----------------------------------------------------------------------+")
        
        for section in result['sections']:
            section_id = section.get('section_id', '?')
            location = section.get('location', 'unknown')
            text = section.get('text', '').strip()
            confidence = section.get('confidence', 'unknown')
            
            print(f"| Section {section_id} ({location}) - Confidence: {confidence}")
            print(f"| Text: {text}")
            print("+----------------------------------------------------------------------+")
    
    # Summary
    all_text = " ".join([s.get('text', '') for s in result['sections']]).strip()
    word_count = len(all_text.split()) if all_text else 0
    
    print(f"\n📊 SUMMARY:")
    print(f"   📝 Total text length: {len(all_text)} characters")
    print(f"   📖 Total words: {word_count}")
    print(f"   🎯 API cost: ~$0.01-0.05 per image (estimated)")

def main():
    """Main function to test GPT-4o OCR."""
    print("🚀 GPT-4o Vision OCR Test")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OpenAI API key not found!")
        print("\n💡 SOLUTION:")
        print("   1. Get API key from: https://platform.openai.com/api-keys")
        print("   2. Set environment variable:")
        print("      PowerShell: $env:OPENAI_API_KEY = 'your-api-key-here'")
        print("      CMD: set OPENAI_API_KEY=your-api-key-here")
        return
    
    # Initialize GPT-4o OCR
    try:
        ocr = GPT4oOCR(api_key)
        print("✅ GPT-4o OCR initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GPT-4o OCR: {e}")
        return
    
    # Find test files
    test_files = find_image_and_pdf_files()
    
    if not test_files:
        print("❌ No test files found!")
        print("💡 Add images or PDFs to 'test_images' directory")
        return
    
    print(f"\n📁 Found {len(test_files)} files to process:")
    for i, file in enumerate(test_files, 1):
        print(f"   {i}. {file.name}")
    
    print(f"\n🔄 Processing files with GPT-4o Vision...")
    
    total_processing_time = 0
    
    for i, file_path in enumerate(test_files, 1):
        print(f"\n{'='*60}")
        print(f"PROCESSING FILE {i}/{len(test_files)}: {file_path.name}")
        print(f"{'='*60}")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                # Process PDF
                if not PDF_SUPPORT:
                    print("❌ PDF support not available, skipping...")
                    continue
                
                pages = convert_pdf_to_images(file_path)
                
                for page_num, page_img in enumerate(pages, 1):
                    # Save temporary image
                    temp_path = Path(f"temp_pdf_page_{page_num}.png")
                    page_img.save(temp_path)
                    
                    try:
                        # Process with GPT-4o
                        result = ocr.extract_text_sections(temp_path, f"PDF page {page_num}")
                        
                        # Apply A3 document filtering for More4Life documents
                        if "conversation" in file_path.name.lower() or "more4life" in file_path.name.lower() or "a3" in file_path.name.lower():
                            result = filter_gpt4o_results(result, f"{file_path.name} (Page {page_num})")
                        
                        display_gpt4o_results(result, f"{file_path.name} (Page {page_num})", "PDF Page")
                        
                        if result['success']:
                            total_processing_time += result['processing_time']
                    finally:
                        # Clean up temp file
                        if temp_path.exists():
                            temp_path.unlink()
            
            else:
                # Process image with optimization
                print(f"🖼️  Processing image: {file_path}")
                
                # Load and optimize the image
                with Image.open(file_path) as img:
                    optimized_img = optimize_image_for_gpt4o(img, max_pixels=1500000)
                    
                    # Save optimized image temporarily
                    temp_optimized_path = Path(f"temp_optimized_{file_path.stem}.png")
                    optimized_img.save(temp_optimized_path)
                
                try:
                    result = ocr.extract_text_sections(temp_optimized_path, "scanned document")
                    
                    # Apply A3 document filtering for More4Life documents
                    if "conversation" in file_path.name.lower() or "more4life" in file_path.name.lower() or "a3" in file_path.name.lower():
                        result = filter_gpt4o_results(result, file_path.name)
                    
                    display_gpt4o_results(result, file_path.name, "Image")
                    
                    if result['success']:
                        total_processing_time += result['processing_time']
                        
                finally:
                    # Clean up temporary file
                    if temp_optimized_path.exists():
                        temp_optimized_path.unlink()
        
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
    
    print(f"\n{'='*80}")
    print(f"🎉 GPT-4o OCR TESTING COMPLETE")
    print(f"{'='*80}")
    print(f"📊 Total files processed: {len(test_files)}")
    print(f"⏱️  Total processing time: {total_processing_time:.2f}s")
    print(f"🎯 Model: GPT-4o Vision (State-of-the-art OCR)")
    print(f"💡 Best for: Printed text, scanned documents, complex layouts")

if __name__ == "__main__":
    main() 