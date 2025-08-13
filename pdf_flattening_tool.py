#!/usr/bin/env python3
"""
PDF Flattening Tool
Converts editable PDF form fields to permanent text, removing the ability to edit them.
Perfect for finalizing documents before distribution.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from pathlib import Path
import os
from typing import List, Optional

class PDFFlatteningTool:
    """Tool for flattening PDF form fields into permanent text."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📄 PDF Flattening Tool - Remove Editable Fields")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Data
        self.input_files: List[Path] = []
        self.output_folder: Optional[Path] = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Title
        title_frame = tk.Frame(self.root, bg="#34495e", height=80)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="📄 PDF Flattening Tool - Convert Editable Fields to Permanent Text", 
            font=("Segoe UI", 16, "bold"),
            bg="#34495e", 
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Description
        desc_frame = tk.LabelFrame(main_frame, text="ℹ️ What This Tool Does", font=("Segoe UI", 12, "bold"))
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, bg="#ecf0f1", relief=tk.FLAT)
        desc_text.pack(fill=tk.X, padx=10, pady=10)
        desc_text.insert(tk.END, 
            "This tool converts editable PDF form fields (blue text boxes) into permanent text that cannot be edited. "
            "Perfect for finalizing documents before sending to clients or archiving. The text will preserve multi-line "
            "formatting and word wrapping exactly as it appeared in the original fields. The blue field borders will "
            "disappear, leaving only clean, professional text."
        )
        desc_text.config(state=tk.DISABLED)
        
        # File selection
        self.setup_file_selection(main_frame)
        
        # Output options
        self.setup_output_options(main_frame)
        
        # Processing controls
        self.setup_processing_controls(main_frame)
        
        # Results area
        self.setup_results_area(main_frame)
    
    def setup_file_selection(self, parent):
        """Setup file selection area."""
        file_frame = tk.LabelFrame(parent, text="📁 Select PDF Files to Flatten", font=("Segoe UI", 12, "bold"))
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="📄 Add PDF Files",
            font=("Segoe UI", 10, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.add_files
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="📂 Add Folder",
            font=("Segoe UI", 10, "bold"),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.add_folder
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            btn_frame,
            text="🗑️ Clear List",
            font=("Segoe UI", 10),
            bg="#e74c3c",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.clear_files
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # File list
        list_frame = tk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Listbox with scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            height=8
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
    
    def setup_output_options(self, parent):
        """Setup output options."""
        output_frame = tk.LabelFrame(parent, text="📁 Output Settings", font=("Segoe UI", 12, "bold"))
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output folder selection
        folder_frame = tk.Frame(output_frame)
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(folder_frame, text="Output Folder:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        self.output_folder_var = tk.StringVar(value="Same as input files")
        self.output_label = tk.Label(
            folder_frame, 
            textvariable=self.output_folder_var,
            font=("Segoe UI", 9),
            fg="#7f8c8d",
            relief=tk.SUNKEN,
            padx=10,
            pady=5,
            bg="white"
        )
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Button(
            folder_frame,
            text="📂 Choose Folder",
            font=("Segoe UI", 9),
            bg="#95a5a6",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.choose_output_folder
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Naming options
        naming_frame = tk.Frame(output_frame)
        naming_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(naming_frame, text="File Naming:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        self.naming_var = tk.StringVar(value="suffix")
        
        tk.Radiobutton(
            naming_frame,
            text="Add '_flattened' suffix",
            variable=self.naming_var,
            value="suffix",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(20, 10))
        
        tk.Radiobutton(
            naming_frame,
            text="Overwrite original",
            variable=self.naming_var,
            value="overwrite",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT)
    
    def setup_processing_controls(self, parent):
        """Setup processing controls."""
        control_frame = tk.LabelFrame(parent, text="⚙️ Processing", font=("Segoe UI", 12, "bold"))
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_btn = tk.Button(
            btn_frame,
            text="🔧 Flatten PDFs",
            font=("Segoe UI", 12, "bold"),
            bg="#e67e22",
            fg="white",
            relief=tk.FLAT,
            padx=30,
            pady=10,
            command=self.process_files
        )
        self.process_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(btn_frame, mode='determinate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 0))
    
    def setup_results_area(self, parent):
        """Setup results display area."""
        results_frame = tk.LabelFrame(parent, text="📋 Processing Results", font=("Segoe UI", 12, "bold"))
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text area with scrollbar
        text_frame = tk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar_y = tk.Scrollbar(text_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_text = tk.Text(
            text_frame,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            font=("Consolas", 9),
            wrap=tk.NONE,
            state=tk.DISABLED
        )
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=self.results_text.yview)
        scrollbar_x.config(command=self.results_text.xview)
    
    def add_files(self):
        """Add PDF files to the processing list."""
        files = filedialog.askopenfilenames(
            title="Select PDF Files to Flatten",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        for file_path in files:
            path = Path(file_path)
            if path not in self.input_files:
                self.input_files.append(path)
        
        self.update_file_list()
    
    def add_folder(self):
        """Add all PDF files from a folder."""
        folder = filedialog.askdirectory(title="Select Folder Containing PDF Files")
        if folder:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("*.pdf"))
            
            for pdf_file in pdf_files:
                if pdf_file not in self.input_files:
                    self.input_files.append(pdf_file)
            
            self.update_file_list()
            self.log_message(f"Added {len(pdf_files)} PDF files from {folder}")
    
    def clear_files(self):
        """Clear the file list."""
        self.input_files.clear()
        self.update_file_list()
        self.log_message("File list cleared")
    
    def update_file_list(self):
        """Update the file listbox."""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.input_files:
            self.file_listbox.insert(tk.END, str(file_path))
    
    def choose_output_folder(self):
        """Choose output folder."""
        folder = filedialog.askdirectory(title="Choose Output Folder")
        if folder:
            self.output_folder = Path(folder)
            self.output_folder_var.set(str(self.output_folder))
        else:
            self.output_folder = None
            self.output_folder_var.set("Same as input files")
    
    def process_files(self):
        """Process all selected files."""
        if not self.input_files:
            messagebox.showwarning("No Files", "Please add some PDF files to process.")
            return
        
        self.process_btn.config(state=tk.DISABLED)
        self.clear_results()
        
        total_files = len(self.input_files)
        self.progress.config(maximum=total_files)
        
        success_count = 0
        error_count = 0
        
        self.log_message(f"🔧 Starting PDF flattening process...")
        self.log_message(f"📊 Processing {total_files} files")
        self.log_message("=" * 60)
        
        for i, input_file in enumerate(self.input_files):
            try:
                self.log_message(f"\n📄 Processing: {input_file.name}")
                
                # Determine output path
                if self.output_folder:
                    output_dir = self.output_folder
                else:
                    output_dir = input_file.parent
                
                if self.naming_var.get() == "overwrite":
                    output_path = output_dir / input_file.name
                else:
                    # Add suffix
                    stem = input_file.stem
                    output_path = output_dir / f"{stem}_flattened.pdf"
                
                # Flatten the PDF
                success = self.flatten_pdf(input_file, output_path)
                
                if success:
                    success_count += 1
                    self.log_message(f"✅ Success: {output_path.name}")
                else:
                    error_count += 1
                    self.log_message(f"❌ Failed: {input_file.name}")
                
            except Exception as e:
                error_count += 1
                self.log_message(f"❌ Error processing {input_file.name}: {str(e)}")
            
            # Update progress
            self.progress.config(value=i + 1)
            self.root.update()
        
        # Final summary
        self.log_message("\n" + "=" * 60)
        self.log_message(f"🏁 Processing Complete!")
        self.log_message(f"✅ Successful: {success_count}")
        self.log_message(f"❌ Failed: {error_count}")
        self.log_message(f"📊 Total: {total_files}")
        
        self.process_btn.config(state=tk.NORMAL)
        self.progress.config(value=0)
        
        if success_count > 0:
            messagebox.showinfo("Complete", f"Successfully flattened {success_count} PDF files!")
    
    def flatten_pdf(self, input_path: Path, output_path: Path) -> bool:
        """
        Flatten a PDF by converting form fields to permanent text.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open the PDF
            pdf_doc = fitz.open(input_path)
            
            field_count = 0
            
            # Process each page
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                # Get all form fields (widgets) on this page
                widgets = list(page.widgets())
                
                for widget in widgets:
                    field_count += 1
                    
                    # Get field properties
                    field_name = widget.field_name
                    field_value = widget.field_value or ""
                    field_rect = widget.rect
                    
                    if field_value.strip():  # Only process fields with content
                        # Get font info (with fallbacks)
                        font_size = getattr(widget, 'text_font_size', 12)
                        if font_size <= 0:
                            font_size = 12
                        
                        # Insert multi-line text preserving formatting
                        self.insert_multiline_text(
                            page, 
                            field_value, 
                            field_rect, 
                            font_size
                        )
                
                # Remove all form fields from this page
                for widget in widgets:
                    try:
                        widget.update()  # Ensure widget is current
                        page.delete_widget(widget)
                    except:
                        pass  # Continue if deletion fails
            
            # Save the flattened PDF
            pdf_doc.save(output_path)
            pdf_doc.close()
            
            self.log_message(f"   🔧 Flattened {field_count} form fields")
            return True
            
        except Exception as e:
            self.log_message(f"   ❌ Error: {str(e)}")
            return False
    
    def insert_multiline_text(self, page, text: str, rect: fitz.Rect, font_size: float):
        """
        Insert text with proper word wrapping and line breaks to match the original field formatting.
        
        Args:
            page: PDF page object
            text: Text to insert
            rect: Rectangle of the original field
            font_size: Font size to use
        """
        try:
            # Calculate available width (with some padding)
            available_width = rect.width - 6  # 3px padding on each side
            line_height = font_size * 1.2  # Standard line height multiplier
            
            # Split text into lines (handle existing line breaks)
            paragraphs = text.split('\n')
            
            # Starting position (with padding)
            current_y = rect.y0 + font_size + 3  # Start from top with padding
            x_pos = rect.x0 + 3  # Left padding
            
            for paragraph in paragraphs:
                if not paragraph.strip():
                    # Empty line - just add line spacing
                    current_y += line_height
                    continue
                
                # Word wrap this paragraph
                words = paragraph.split()
                current_line = ""
                
                for word in words:
                    # Test if adding this word would exceed the width
                    test_line = current_line + (" " if current_line else "") + word
                    
                    # More accurate text width calculation using PyMuPDF
                    try:
                        # Get text width using PyMuPDF's text measurement
                        text_width = fitz.get_text_length(test_line, fontsize=font_size)
                    except:
                        # Fallback: estimate width (avg char width = font_size * 0.6)
                        text_width = len(test_line) * font_size * 0.6
                    
                    if text_width <= available_width or not current_line:
                        # Word fits or it's the first word (must include even if too long)
                        current_line = test_line
                    else:
                        # Word doesn't fit, insert current line and start new one
                        if current_line:
                            page.insert_text(
                                fitz.Point(x_pos, current_y),
                                current_line,
                                fontsize=font_size,
                                color=(0, 0, 0)
                            )
                            current_y += line_height
                        
                        current_line = word
                
                # Insert the last line of this paragraph
                if current_line:
                    page.insert_text(
                        fitz.Point(x_pos, current_y),
                        current_line,
                        fontsize=font_size,
                        color=(0, 0, 0)
                    )
                    current_y += line_height
                
                # Add extra spacing between paragraphs
                current_y += line_height * 0.3
                
                # Check if we're getting close to the bottom of the field
                if current_y > rect.y1 - font_size:
                    break  # Stop if we're running out of space
                    
        except Exception as e:
            # Fallback: simple single-line insertion
            try:
                text_point = fitz.Point(rect.x0 + 3, rect.y0 + font_size + 3)
                page.insert_text(
                    text_point,
                    text.replace('\n', ' '),  # Replace line breaks with spaces
                    fontsize=font_size,
                    color=(0, 0, 0)
                )
            except:
                pass  # If even fallback fails, skip this field
    
    def log_message(self, message: str):
        """Add a message to the results area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.root.update()
    
    def clear_results(self):
        """Clear the results area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main entry point."""
    app = PDFFlatteningTool()
    app.run()

if __name__ == "__main__":
    main()
