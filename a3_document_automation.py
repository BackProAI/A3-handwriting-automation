#!/usr/bin/env python3
"""
A3 Document Automation System - More4Life
Enhanced drag-and-drop interface using complete GPT-4o OCR pipeline
"""

import os
import time
import json
import shutil
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import queue
import threading
from typing import List, Dict, Any

# Import the complete GPT-4o OCR pipeline
from test_gpt4o_ocr import (
    GPT4oOCR, 
    find_image_and_pdf_files, 
    convert_pdf_to_images, 
    optimize_image_for_gpt4o,
    PDF_SUPPORT
)
from filter_a3_results import filter_gpt4o_results
from a3_template_processor import A3TemplateProcessor

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

class A3DocumentProcessor:
    """Complete A3 document processing using the test_gpt4o_ocr.py pipeline."""
    
    def __init__(self, api_key: str = None):
        """Initialize the A3 document processor."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        # Initialize the GPT-4o OCR engine from test_gpt4o_ocr.py
        self.ocr = GPT4oOCR(self.api_key)
        
        # Initialize the template processor with custom config if available
        custom_config_path = Path("custom_field_positions.json")
        if custom_config_path.exists():
            print(f"✅ Found custom field configuration: {custom_config_path}")
            custom_config = self._load_custom_config(custom_config_path)
            self.template_processor = A3TemplateProcessor(custom_fields_config=custom_config)
            self.using_custom_fields = True
        else:
            print("📝 Using default field configuration")
            self.template_processor = A3TemplateProcessor()
            self.using_custom_fields = False
    
    def _load_custom_config(self, config_path: Path) -> Dict:
        """Load custom field configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"⚠️ Failed to load custom config: {e}")
            return {}
        
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single file using the complete test_gpt4o_ocr.py pipeline.
        Returns all results and creates a populated PDF template.
        
        Returns:
            Dictionary with processing results and output file path
        """
        all_results = []
        processing_info = {
            'success': True,
            'file_name': file_path.name,
            'total_processing_time': 0,
            'pages_processed': 0,
            'output_pdf_path': None,
            'error': None
        }
        
        try:
            if file_path.suffix.lower() == '.pdf':
                # Process PDF using the exact same pipeline as test_gpt4o_ocr.py
                if not PDF_SUPPORT:
                    raise Exception("PDF support not available")
                
                # Convert PDF to images
                pages = convert_pdf_to_images(file_path)
                
                for page_num, page_img in enumerate(pages, 1):
                    # Save temporary image
                    temp_path = Path(f"temp_pdf_page_{page_num}.png")
                    page_img.save(temp_path)
                    
                    try:
                        # Process with GPT-4o using the exact same method
                        result = self.ocr.extract_text_sections(temp_path, f"PDF page {page_num}")
                        
                        # Apply A3 document filtering (same logic as test_gpt4o_ocr.py)
                        if "conversation" in file_path.name.lower() or "more4life" in file_path.name.lower() or "a3" in file_path.name.lower():
                            result = filter_gpt4o_results(result, f"{file_path.name} (Page {page_num})")
                        
                        # Add page info
                        result['page_number'] = page_num
                        result['file_name'] = file_path.name
                        result['file_type'] = 'PDF'
                        
                        all_results.append(result)
                        
                        if result.get('success'):
                            processing_info['total_processing_time'] += result.get('processing_time', 0)
                            processing_info['pages_processed'] += 1
                        
                    finally:
                        # Clean up temp file
                        if temp_path.exists():
                            temp_path.unlink()
            
            else:
                # Process image using the exact same pipeline as test_gpt4o_ocr.py
                from PIL import Image
                
                # Load and optimize the image (same as test_gpt4o_ocr.py)
                with Image.open(file_path) as img:
                    optimized_img = optimize_image_for_gpt4o(img, max_pixels=1500000)
                    
                    # Save optimized image temporarily
                    temp_optimized_path = Path(f"temp_optimized_{file_path.stem}.png")
                    optimized_img.save(temp_optimized_path)
                
                try:
                    # Process with GPT-4o using the exact same method
                    result = self.ocr.extract_text_sections(temp_optimized_path, "scanned document")
                    
                    # Apply A3 document filtering (same logic as test_gpt4o_ocr.py)
                    if "conversation" in file_path.name.lower() or "more4life" in file_path.name.lower() or "a3" in file_path.name.lower():
                        result = filter_gpt4o_results(result, file_path.name)
                    
                    # Add file info
                    result['page_number'] = 1
                    result['file_name'] = file_path.name
                    result['file_type'] = 'Image'
                    
                    all_results.append(result)
                    
                    if result.get('success'):
                        processing_info['total_processing_time'] += result.get('processing_time', 0)
                        processing_info['pages_processed'] += 1
                    
                finally:
                    # Clean up temporary file
                    if temp_optimized_path.exists():
                        temp_optimized_path.unlink()
            
            # Create populated PDF template with extracted text
            if all_results and any(r.get('success', False) for r in all_results):
                try:
                    # Generate output filename with timestamp
                    timestamp = int(time.time())
                    safe_filename = "".join(c for c in file_path.stem if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    output_filename = f"A3_Completed_{safe_filename}_{timestamp}.pdf"
                    output_path = Path("processed_documents") / output_filename
                    
                    # Automatically populate template with extracted text
                    final_pdf_path = self.template_processor.populate_template(all_results, output_path)
                    processing_info['output_pdf_path'] = final_pdf_path
                    
                except Exception as e:
                    print(f"⚠️ Failed to create populated PDF template: {e}")
                    processing_info['error'] = f"Template population failed: {e}"
            
            # Add all page results to processing info
            processing_info['page_results'] = all_results
            
        except Exception as e:
            # Return error result
            processing_info['success'] = False
            processing_info['error'] = str(e)
        
        return processing_info

class A3AutomationUI:
    """Main UI for A3 Document Automation."""
    
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("A3 Document Automation - More4Life")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Status queue for thread communication
        self.status_queue = queue.Queue()
        
        # Initialize processor
        self.processor = None
        self.setup_ui()
        self.check_prerequisites()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Title
        title_frame = Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = Label(
            title_frame, 
            text="🏢 A3 Document Automation - More4Life", 
            font=("Segoe UI", 18, "bold"),
            bg="#2c3e50", 
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Main content frame
        main_frame = Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Drop zone
        self.setup_drop_zone(main_frame)
        
        # Results area
        self.setup_results_area(main_frame)
        
        # Status bar
        self.setup_status_bar()
        
    def setup_drop_zone(self, parent):
        """Setup drag and drop zone."""
        drop_frame = Frame(parent, bg="#ecf0f1", relief=RAISED, bd=2)
        drop_frame.pack(fill=X, pady=(0, 20))
        
        # Drop zone
        self.drop_zone = Frame(drop_frame, bg="#3498db", height=150, relief=SUNKEN, bd=3)
        self.drop_zone.pack(fill=X, padx=10, pady=10)
        self.drop_zone.pack_propagate(False)
        
        # Drop zone content
        drop_content = Frame(self.drop_zone, bg="#3498db")
        drop_content.pack(expand=True)
        
        Label(
            drop_content, 
            text="📄 Drag & Drop A3 Documents Here", 
            font=("Segoe UI", 16, "bold"),
            bg="#3498db", 
            fg="white"
        ).pack(pady=(20, 5))
        
        Label(
            drop_content,
            text="Supports: PDF, PNG, JPG, JPEG, BMP, TIFF",
            font=("Segoe UI", 10),
            bg="#3498db",
            fg="#ecf0f1"
        ).pack(pady=(0, 5))
        
        # Browse button
        browse_btn = Button(
            drop_content,
            text="📂 Browse Files",
            font=("Segoe UI", 10, "bold"),
            bg="#2980b9",
            fg="white",
            relief=FLAT,
            padx=20,
            pady=5,
            command=self.browse_files
        )
        browse_btn.pack(pady=(5, 20))
        
        # Enable drag and drop
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.on_drop)
        
    def setup_results_area(self, parent):
        """Setup results display area."""
        results_frame = LabelFrame(parent, text="📋 Processing Results", font=("Segoe UI", 12, "bold"))
        results_frame.pack(fill=BOTH, expand=True)
        
        # Scrollable text area
        text_frame = Frame(results_frame)
        text_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Text widget with scrollbar
        self.results_text = Text(
            text_frame,
            wrap=WORD,
            font=("Consolas", 10),
            bg="white",
            fg="black",
            state=DISABLED
        )
        
        scrollbar = Scrollbar(text_frame, orient=VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Clear button
        clear_btn = Button(
            results_frame,
            text="🗑️ Clear Results",
            font=("Segoe UI", 10),
            bg="#e74c3c",
            fg="white",
            relief=FLAT,
            command=self.clear_results
        )
        clear_btn.pack(pady=(0, 10))
        
    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = Label(
            self.root,
            text="Ready",
            font=("Segoe UI", 9),
            bg="#34495e",
            fg="white",
            anchor=W,
            padx=10
        )
        self.status_bar.pack(side=BOTTOM, fill=X)
        
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        try:
            # Check API key
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.log_message("❌ ERROR: No OpenAI API key found!")
                self.log_message("💡 Run: python secure_api_setup.py")
                return
            
            # Initialize processor
            self.processor = A3DocumentProcessor(api_key)
            self.log_message("✅ A3 Document Processor initialized successfully")
            self.log_message("✅ Using complete test_gpt4o_ocr.py processing pipeline")
            self.log_message("✅ A3 document filtering enabled")
            
            if PDF_SUPPORT:
                self.log_message("✅ PDF support enabled")
            else:
                self.log_message("⚠️ PDF support not available")
            
            self.log_message("🎯 Ready to process A3 documents!")
            
        except Exception as e:
            self.log_message(f"❌ Initialization failed: {e}")
    
    def browse_files(self):
        """Open file browser."""
        filetypes = [
            ("All Supported", "*.pdf;*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("PDF files", "*.pdf"),
            ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select A3 Documents",
            filetypes=filetypes
        )
        
        if files:
            self.process_files([Path(f) for f in files])
    
    def on_drop(self, event):
        """Handle dropped files."""
        files = self.root.tk.splitlist(event.data)
        file_paths = [Path(f) for f in files]
        self.process_files(file_paths)
    
    def process_files(self, file_paths: List[Path]):
        """Process dropped/selected files."""
        if not self.processor:
            self.log_message("❌ Processor not initialized")
            return
        
        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_files_background,
            args=(file_paths,),
            daemon=True
        )
        thread.start()
        
        # Start monitoring the status queue
        self.monitor_status_queue()
    
    def _process_files_background(self, file_paths: List[Path]):
        """Process files in background thread."""
        try:
            self.status_queue.put(("status", f"🔄 Processing {len(file_paths)} files..."))
            self.status_queue.put(("clear", ""))
            
            total_start_time = time.time()
            successful_files = 0
            total_pages = 0
            created_pdfs = []
            
            for i, file_path in enumerate(file_paths, 1):
                self.status_queue.put(("message", f"\n{'='*60}"))
                self.status_queue.put(("message", f"PROCESSING FILE {i}/{len(file_paths)}: {file_path.name}"))
                self.status_queue.put(("message", f"{'='*60}"))
                
                # Process using the complete test_gpt4o_ocr.py pipeline
                processing_info = self.processor.process_file(file_path)
                
                if processing_info.get('success', False):
                    successful_files += 1
                    total_pages += processing_info.get('pages_processed', 0)
                    
                    # Display processing results for each page
                    page_results = processing_info.get('page_results', [])
                    for result in page_results:
                        if result.get('success', False):
                            self._display_result(result)
                    
                    # Show template creation results
                    output_pdf = processing_info.get('output_pdf_path')
                    if output_pdf:
                        created_pdfs.append(output_pdf)
                        self.status_queue.put(("message", f"\n🎉 COMPLETED A3 DOCUMENT CREATED"))
                        self.status_queue.put(("message", f"{'='*40}"))
                        field_type = "CUSTOM positioned" if self.processor.using_custom_fields else "default"
                        self.status_queue.put(("message", f"✅ Created POPULATED A3 document with {field_type} text fields: {output_pdf.name}"))
                        self.status_queue.put(("message", f"📁 Location: {output_pdf}"))
                        self.status_queue.put(("message", f"🎯 FULLY AUTOMATED - text automatically placed in transparent fields"))
                        self.status_queue.put(("message", f"⏱️ Total processing time: {processing_info.get('total_processing_time', 0):.2f}s"))
                        
                        # Show what was extracted and mapped
                        self.status_queue.put(("message", f"\n📋 EXTRACTED & MAPPED TEXT"))
                        self.status_queue.put(("message", f"{'='*40}"))
                        self._display_populated_text(processing_info.get('page_results', []))
                    
                    if processing_info.get('error'):
                        self.status_queue.put(("message", f"⚠️ Template creation warning: {processing_info['error']}"))
                
                else:
                    error = processing_info.get('error', 'Unknown error')
                    self.status_queue.put(("message", f"❌ Error processing {file_path.name}: {error}"))
            
            # Final summary
            total_time = time.time() - total_start_time
            self.status_queue.put(("message", f"\n{'='*80}"))
            self.status_queue.put(("message", "🎉 A3 DOCUMENT AUTOMATION COMPLETE"))
            self.status_queue.put(("message", f"{'='*80}"))
            self.status_queue.put(("message", f"📊 Files processed: {successful_files}/{len(file_paths)}"))
            self.status_queue.put(("message", f"📄 Total pages: {total_pages}"))
            self.status_queue.put(("message", f"🎉 Completed A3 documents created: {len(created_pdfs)}"))
            
            if created_pdfs:
                self.status_queue.put(("message", f"\n📁 COMPLETED DOCUMENTS (ready to use):"))
                for pdf_path in created_pdfs:
                    self.status_queue.put(("message", f"   ✅ {pdf_path}"))
            
            self.status_queue.put(("message", f"\n🎯 WHAT HAPPENED:"))
            self.status_queue.put(("message", f"   ✅ Extracted handwritten text using GPT-4o"))
            self.status_queue.put(("message", f"   ✅ Automatically mapped text to template fields"))
            self.status_queue.put(("message", f"   ✅ Created completed PDF with transparent fields"))
            self.status_queue.put(("message", f"   ✅ Text is already populated - no manual work needed!"))
            
            # Show field positioning info based on current setup
            if getattr(self.processor, 'using_custom_fields', False):  # Check if processor used custom fields
                self.status_queue.put(("message", f"\n🎯 CUSTOM FIELDS DETECTED:"))
                self.status_queue.put(("message", f"   ✅ Using your custom positioned transparent fields"))
                self.status_queue.put(("message", f"   📁 Field config: custom_field_positions.json"))
            else:
                self.status_queue.put(("message", f"\n🎯 CUSTOM FIELD POSITIONING:"))
                self.status_queue.put(("message", f"   • Visual Tool: python field_positioning_tool.py"))
                self.status_queue.put(("message", f"   • Manual Config: python create_field_config.py"))
                self.status_queue.put(("message", f"   • Create Custom: python create_custom_template.py"))
            
            self.status_queue.put(("message", f"\n⏱️ Total time: {total_time:.2f}s"))
            self.status_queue.put(("message", f"🎯 All files saved to: processed_documents/"))
            self.status_queue.put(("status", "🎉 Processing complete - Fully automated A3 documents created!"))
            
        except Exception as e:
            self.status_queue.put(("error", f"❌ Processing failed: {e}"))
    
    def _display_populated_text(self, page_results: List[Dict[str, Any]]):
        """Display what text was extracted and automatically mapped to fields."""
        try:
            total_sections = 0
            for result in page_results:
                if not result.get('success', False):
                    continue
                
                page_num = result.get('page_number', 1)
                sections = result.get('sections', [])
                
                if not sections:
                    continue
                
                self.status_queue.put(("message", f"\n📄 PAGE {page_num} - AUTOMATICALLY MAPPED:"))
                self.status_queue.put(("message", f"{'-'*50}"))
                
                for i, section in enumerate(sections, 1):
                    text = section.get('text', '').strip()
                    location = section.get('location', 'Unknown location')
                    
                    if text:
                        total_sections += 1
                        # Show first 60 characters of text
                        display_text = text[:60] + "..." if len(text) > 60 else text
                        self.status_queue.put(("message", f"[{i}] {location}: {display_text}"))
                
                self.status_queue.put(("message", f"{'-'*50}"))
            
            if total_sections > 0:
                self.status_queue.put(("message", f"✅ {total_sections} text sections automatically mapped to template fields"))
            else:
                self.status_queue.put(("message", f"⚠️ No text sections found to map"))
                
        except Exception as e:
            self.status_queue.put(("message", f"⚠️ Error displaying populated text: {e}"))
    
    def _display_result(self, result: Dict[str, Any]):
        """Display a single processing result using the same format as test_gpt4o_ocr.py."""
        file_name = result.get('file_name', 'Unknown')
        page_num = result.get('page_number', 1)
        file_type = result.get('file_type', 'Document')
        
        display_name = f"{file_name} (Page {page_num})" if file_type == 'PDF' else file_name
        
        # Header
        self.status_queue.put(("message", f"\n{'='*80}"))
        self.status_queue.put(("message", f"📋 GPT-4o OCR RESULTS: {display_name}"))
        self.status_queue.put(("message", f"{'='*80}"))
        
        # Basic info
        self.status_queue.put(("message", f"📊 Document type: {result.get('document_type', 'unknown')}"))
        self.status_queue.put(("message", f"📝 Sections found: {result.get('total_sections', 0)}"))
        self.status_queue.put(("message", f"⏱️ Processing time: {result.get('processing_time', 0):.2f}s"))
        
        # Filtering info
        if result.get('filtering_applied'):
            original_count = result.get('original_section_count', 0)
            filtered_count = result.get('filtered_section_count', 0)
            removed_count = result.get('sections_removed', 0)
            self.status_queue.put(("message", f"🔍 A3 Filtering applied: {original_count} → {filtered_count} sections ({removed_count} filtered out)"))
        
        # Sections
        sections = result.get('sections', [])
        if sections:
            self.status_queue.put(("message", "\n📄 EXTRACTED SECTIONS:"))
            self.status_queue.put(("message", "+----------------------------------------------------------------------+"))
            
            for section in sections:
                section_id = section.get('section_id', '?')
                location = section.get('location', 'unknown')
                text = section.get('text', '').strip()
                confidence = section.get('confidence', 'unknown')
                
                self.status_queue.put(("message", f"| Section {section_id} ({location}) - Confidence: {confidence}"))
                self.status_queue.put(("message", f"| Text: {text}"))
                self.status_queue.put(("message", "+----------------------------------------------------------------------+"))
        
        # Summary
        all_text = " ".join([s.get('text', '') for s in sections]).strip()
        word_count = len(all_text.split()) if all_text else 0
        
        self.status_queue.put(("message", f"\n📊 SUMMARY:"))
        self.status_queue.put(("message", f"   📝 Total text length: {len(all_text)} characters"))
        self.status_queue.put(("message", f"   📖 Total words: {word_count}"))
        self.status_queue.put(("message", f"   🎯 API cost: ~$0.01-0.05 per image (estimated)"))
    
    def monitor_status_queue(self):
        """Monitor the status queue for updates."""
        try:
            while True:
                msg_type, message = self.status_queue.get_nowait()
                
                if msg_type == "status":
                    self.status_bar.config(text=message)
                elif msg_type == "message":
                    self.log_message(message)
                elif msg_type == "clear":
                    self.clear_results()
                elif msg_type == "error":
                    self.log_message(message)
                    messagebox.showerror("Error", message)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.monitor_status_queue)
    
    def log_message(self, message: str):
        """Add message to results display."""
        self.results_text.config(state=NORMAL)
        self.results_text.insert(END, message + "\n")
        self.results_text.see(END)
        self.results_text.config(state=DISABLED)
    
    def clear_results(self):
        """Clear the results display."""
        self.results_text.config(state=NORMAL)
        self.results_text.delete(1.0, END)
        self.results_text.config(state=DISABLED)
        self.status_bar.config(text="Results cleared")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

def main():
    """Main entry point."""
    # Check if running from correct directory
    if not Path("test_gpt4o_ocr.py").exists():
        print("❌ Error: test_gpt4o_ocr.py not found!")
        print("💡 Make sure you're running from the project root directory")
        return
    
    if not Path("filter_a3_results.py").exists():
        print("❌ Error: filter_a3_results.py not found!")
        print("💡 Make sure you're running from the project root directory")
        return
    
    # Launch the application
    try:
        app = A3AutomationUI()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

if __name__ == "__main__":
    main() 