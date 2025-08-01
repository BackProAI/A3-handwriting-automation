#!/usr/bin/env python3
"""
A3 Section Definition Tool
Visual tool to manually define OCR sections on A3 PDF templates
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io

class A3SectionDefiner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("A3 Section Definition Tool - Manual Sectioning")
        self.root.geometry("1400x900")
        
        # Section management
        self.sections = {"page_1": [], "page_2": []}
        self.current_page = 1
        self.pdf_document = None
        self.page_images = {}
        self.canvas_scale = 1.0
        
        # Drawing state
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        self.selected_section = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Load PDF button
        ttk.Button(toolbar, text="📄 Load A3 Template PDF", 
                  command=self.load_pdf).pack(side=tk.LEFT, padx=(0, 10))
        
        # Page navigation
        ttk.Label(toolbar, text="Page:").pack(side=tk.LEFT, padx=(10, 5))
        self.page_var = tk.StringVar(value="1")
        page_combo = ttk.Combobox(toolbar, textvariable=self.page_var, 
                                 values=["1", "2"], width=5, state="readonly")
        page_combo.pack(side=tk.LEFT, padx=(0, 10))
        page_combo.bind('<<ComboboxSelected>>', self.change_page)
        
        # Section count display
        self.section_count_var = tk.StringVar(value="Sections: 0")
        ttk.Label(toolbar, textvariable=self.section_count_var).pack(side=tk.LEFT, padx=(10, 5))
        
        # Save/Load buttons
        ttk.Button(toolbar, text="💾 Save Sections", 
                  command=self.save_sections).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(toolbar, text="📂 Load Sections", 
                  command=self.load_sections).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Canvas
        canvas_frame = ttk.LabelFrame(content_frame, text="📄 A3 Template (Click and drag to define sections)")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Canvas with scrollbars
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_container, bg="white", cursor="crosshair")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.start_section)
        self.canvas.bind("<B1-Motion>", self.draw_section)
        self.canvas.bind("<ButtonRelease-1>", self.end_section)
        self.canvas.bind("<Double-Button-1>", self.select_section)
        self.canvas.bind("<Button-3>", self.delete_section)  # Right click to delete
        
        # Right panel - Section management
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Section list
        list_frame = ttk.LabelFrame(right_panel, text="📋 Defined Sections")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 10))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.section_listbox = tk.Listbox(list_container, width=25)
        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.section_listbox.yview)
        self.section_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        self.section_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.section_listbox.bind('<<ListboxSelect>>', self.highlight_section)
        
        # Section properties
        props_frame = ttk.LabelFrame(right_panel, text="⚙️ Section Properties")
        props_frame.pack(fill=tk.X, pady=(0, 10))
        
        props_container = ttk.Frame(props_frame)
        props_container.pack(fill=tk.X, padx=10, pady=10)
        
        # Section name
        ttk.Label(props_container, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(props_container, textvariable=self.name_var, width=20)
        name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        name_entry.bind('<KeyRelease>', self.update_section_name)
        
        # Target field (for mapping)
        ttk.Label(props_container, text="Maps to Field:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.field_var = tk.StringVar()
        self.field_combo = ttk.Combobox(props_container, textvariable=self.field_var, width=17)
        self.field_combo.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2, padx=(5, 0))
        self.field_combo.bind('<<ComboboxSelected>>', self.update_target_field)
        
        # Grid configure
        props_container.columnconfigure(1, weight=1)
        
        # Action buttons
        action_frame = ttk.LabelFrame(right_panel, text="🛠️ Actions")
        action_frame.pack(fill=tk.X)
        
        action_container = ttk.Frame(action_frame)
        action_container.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(action_container, text="🗑️ Delete Selected", 
                  command=self.delete_selected_section).pack(fill=tk.X, pady=2)
        ttk.Button(action_container, text="🔄 Clear All Sections", 
                  command=self.clear_all_sections).pack(fill=tk.X, pady=2)
        
        # Instructions
        instr_frame = ttk.LabelFrame(right_panel, text="📖 Instructions")
        instr_frame.pack(fill=tk.X, pady=(10, 0))
        
        instructions = """
• Load your A3 template PDF
• Switch between Page 1 and Page 2
• Click and drag to define sections
• Double-click to select/edit sections
• Right-click to delete sections
• Name each section descriptively
• Map sections to template fields
• Save sections configuration
        """
        
        ttk.Label(instr_frame, text=instructions, justify=tk.LEFT, 
                 wraplength=200, font=("Segoe UI", 8)).pack(padx=10, pady=10)
        
        # Load field options from custom config if available
        self.load_field_options()
        
    def load_field_options(self):
        """Load available field names from custom_field_positions.json."""
        config_path = Path("custom_field_positions.json")
        field_options = []
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Extract field names from both pages
                for page_key in ["page_1", "page_2"]:
                    if page_key in config:
                        for field in config[page_key]:
                            field_name = field.get('name', '')
                            if field_name and field_name not in field_options:
                                field_options.append(field_name)
                
                # Sort alphabetically
                field_options.sort()
                self.field_combo['values'] = field_options
                
                print(f"✅ Loaded {len(field_options)} field options from custom config")
                
            except Exception as e:
                print(f"⚠️ Could not load field options: {e}")
        else:
            print("⚠️ No custom_field_positions.json found - using generic field names")
            self.field_combo['values'] = ["text_field_1", "text_field_2", "text_field_3"]
    
    def load_pdf(self):
        """Load PDF template."""
        file_path = filedialog.askopenfilename(
            title="Select A3 Template PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.pdf_document = fitz.open(file_path)
            self.page_images = {}
            
            # Convert pages to images
            for page_num in range(min(2, len(self.pdf_document))):  # Max 2 pages
                page = self.pdf_document[page_num]
                
                # Render at high resolution for better quality
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image
                pil_image = Image.open(io.BytesIO(img_data))
                self.page_images[page_num + 1] = pil_image
            
            print(f"✅ Loaded PDF with {len(self.page_images)} pages")
            
            # Update page combo
            available_pages = list(self.page_images.keys())
            self.page_var.set(str(available_pages[0]))
            page_combo = None
            for child in self.root.winfo_children():
                if hasattr(child, 'winfo_children'):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Frame):
                            for widget in grandchild.winfo_children():
                                if isinstance(widget, ttk.Combobox) and 'page' in str(widget):
                                    widget['values'] = [str(p) for p in available_pages]
                                    break
            
            # Display first page
            self.display_page(available_pages[0])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {e}")
    
    def display_page(self, page_num):
        """Display a specific page on the canvas."""
        if page_num not in self.page_images:
            return
        
        self.current_page = page_num
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get page image
        pil_image = self.page_images[page_num]
        
        # Scale image to fit canvas (with reasonable max size)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:  # Canvas is rendered
            # Calculate scaling to fit canvas
            scale_x = min(800, canvas_width) / pil_image.width
            scale_y = min(600, canvas_height) / pil_image.height
            self.canvas_scale = min(scale_x, scale_y, 1.0)  # Don't scale up
        else:
            self.canvas_scale = 0.5  # Default scaling
        
        # Resize image
        new_width = int(pil_image.width * self.canvas_scale)
        new_height = int(pil_image.height * self.canvas_scale)
        display_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.photo_image = ImageTk.PhotoImage(display_image)
        
        # Add to canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        
        # Update canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Draw existing sections for this page
        self.draw_existing_sections()
        
        # Update section list
        self.update_section_list()
        
        print(f"📄 Displaying page {page_num} (scale: {self.canvas_scale:.2f})")
    
    def change_page(self, event=None):
        """Change to selected page."""
        try:
            page_num = int(self.page_var.get())
            if page_num in self.page_images:
                self.display_page(page_num)
        except ValueError:
            pass
    
    def start_section(self, event):
        """Start drawing a new section."""
        self.drawing = True
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # Create temporary rectangle
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2, fill="", stipple="gray50"
        )
    
    def draw_section(self, event):
        """Update section rectangle while dragging."""
        if self.drawing and self.current_rect:
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            # Update rectangle coordinates
            self.canvas.coords(self.current_rect, 
                             self.start_x, self.start_y, 
                             current_x, current_y)
    
    def end_section(self, event):
        """Finish drawing section and save it."""
        if not self.drawing or not self.current_rect:
            return
        
        self.drawing = False
        
        # Get final coordinates
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        # Ensure minimum size
        if abs(end_x - self.start_x) < 20 or abs(end_y - self.start_y) < 20:
            self.canvas.delete(self.current_rect)
            self.current_rect = None
            return
        
        # Convert to PDF coordinates (unscale)
        pdf_x1 = min(self.start_x, end_x) / self.canvas_scale
        pdf_y1 = min(self.start_y, end_y) / self.canvas_scale
        pdf_x2 = max(self.start_x, end_x) / self.canvas_scale
        pdf_y2 = max(self.start_y, end_y) / self.canvas_scale
        
        # Create section data
        page_key = f"page_{self.current_page}"
        section_id = len(self.sections[page_key]) + 1
        
        section = {
            "id": section_id,
            "name": f"Section_{self.current_page}_{section_id}",
            "page": self.current_page,
            "rect": [pdf_x1, pdf_y1, pdf_x2, pdf_y2],  # [x1, y1, x2, y2]
            "target_field": "",
            "canvas_id": self.current_rect
        }
        
        self.sections[page_key].append(section)
        
        # Update display
        self.update_section_list()
        self.current_rect = None
        
        print(f"✅ Created section: {section['name']} at ({pdf_x1:.0f}, {pdf_y1:.0f}, {pdf_x2:.0f}, {pdf_y2:.0f})")
    
    def draw_existing_sections(self):
        """Draw all existing sections for current page."""
        page_key = f"page_{self.current_page}"
        
        for section in self.sections[page_key]:
            # Convert PDF coordinates back to canvas coordinates
            pdf_rect = section["rect"]
            canvas_x1 = pdf_rect[0] * self.canvas_scale
            canvas_y1 = pdf_rect[1] * self.canvas_scale
            canvas_x2 = pdf_rect[2] * self.canvas_scale
            canvas_y2 = pdf_rect[3] * self.canvas_scale
            
            # Create rectangle
            canvas_id = self.canvas.create_rectangle(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                outline="blue", width=2, fill="", stipple="gray25"
            )
            
            # Add label
            center_x = (canvas_x1 + canvas_x2) / 2
            center_y = (canvas_y1 + canvas_y2) / 2
            
            text_id = self.canvas.create_text(
                center_x, center_y,
                text=section["name"],
                fill="blue",
                font=("Arial", 8, "bold")
            )
            
            # Update section with canvas IDs
            section["canvas_id"] = canvas_id
            section["text_id"] = text_id
    
    def update_section_list(self):
        """Update the section listbox."""
        self.section_listbox.delete(0, tk.END)
        
        page_key = f"page_{self.current_page}"
        sections = self.sections[page_key]
        
        for section in sections:
            field_info = f" → {section['target_field']}" if section['target_field'] else ""
            display_text = f"{section['name']}{field_info}"
            self.section_listbox.insert(tk.END, display_text)
        
        # Update count
        total_sections = sum(len(self.sections[page]) for page in self.sections)
        self.section_count_var.set(f"Sections: {total_sections} (Page {self.current_page}: {len(sections)})")
    
    def highlight_section(self, event):
        """Highlight selected section."""
        selection = self.section_listbox.curselection()
        if not selection:
            return
        
        page_key = f"page_{self.current_page}"
        section_idx = selection[0]
        
        if section_idx < len(self.sections[page_key]):
            section = self.sections[page_key][section_idx]
            
            # Update properties
            self.name_var.set(section["name"])
            self.field_var.set(section.get("target_field", ""))
            
            self.selected_section = section
            
            # Highlight on canvas
            if "canvas_id" in section:
                self.canvas.itemconfig(section["canvas_id"], outline="green", width=3)
    
    def select_section(self, event):
        """Select section by double-clicking on canvas."""
        # Find which section was clicked
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        page_key = f"page_{self.current_page}"
        
        for i, section in enumerate(self.sections[page_key]):
            rect = section["rect"]
            canvas_x1 = rect[0] * self.canvas_scale
            canvas_y1 = rect[1] * self.canvas_scale
            canvas_x2 = rect[2] * self.canvas_scale
            canvas_y2 = rect[3] * self.canvas_scale
            
            if canvas_x1 <= x <= canvas_x2 and canvas_y1 <= y <= canvas_y2:
                # Select this section
                self.section_listbox.selection_clear(0, tk.END)
                self.section_listbox.selection_set(i)
                self.highlight_section(None)
                break
    
    def delete_section(self, event):
        """Delete section by right-clicking."""
        # Find which section was clicked
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        page_key = f"page_{self.current_page}"
        
        for i, section in enumerate(self.sections[page_key]):
            rect = section["rect"]
            canvas_x1 = rect[0] * self.canvas_scale
            canvas_y1 = rect[1] * self.canvas_scale
            canvas_x2 = rect[2] * self.canvas_scale
            canvas_y2 = rect[3] * self.canvas_scale
            
            if canvas_x1 <= x <= canvas_x2 and canvas_y1 <= y <= canvas_y2:
                # Delete this section
                if messagebox.askyesno("Confirm Delete", f"Delete section '{section['name']}'?"):
                    # Remove from canvas
                    if "canvas_id" in section:
                        self.canvas.delete(section["canvas_id"])
                    if "text_id" in section:
                        self.canvas.delete(section["text_id"])
                    
                    # Remove from data
                    self.sections[page_key].pop(i)
                    
                    # Update display
                    self.update_section_list()
                    print(f"🗑️ Deleted section: {section['name']}")
                break
    
    def delete_selected_section(self):
        """Delete currently selected section."""
        selection = self.section_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a section to delete.")
            return
        
        page_key = f"page_{self.current_page}"
        section_idx = selection[0]
        
        if section_idx < len(self.sections[page_key]):
            section = self.sections[page_key][section_idx]
            
            if messagebox.askyesno("Confirm Delete", f"Delete section '{section['name']}'?"):
                # Remove from canvas
                if "canvas_id" in section:
                    self.canvas.delete(section["canvas_id"])
                if "text_id" in section:
                    self.canvas.delete(section["text_id"])
                
                # Remove from data
                self.sections[page_key].pop(section_idx)
                
                # Update display
                self.update_section_list()
                print(f"🗑️ Deleted section: {section['name']}")
    
    def clear_all_sections(self):
        """Clear all sections for current page."""
        if not messagebox.askyesno("Confirm Clear", f"Clear all sections on Page {self.current_page}?"):
            return
        
        page_key = f"page_{self.current_page}"
        
        # Clear from canvas
        for section in self.sections[page_key]:
            if "canvas_id" in section:
                self.canvas.delete(section["canvas_id"])
            if "text_id" in section:
                self.canvas.delete(section["text_id"])
        
        # Clear from data
        self.sections[page_key] = []
        
        # Update display
        self.update_section_list()
        print(f"🗑️ Cleared all sections on Page {self.current_page}")
    
    def update_section_name(self, event=None):
        """Update selected section name."""
        if self.selected_section and self.name_var.get():
            old_name = self.selected_section["name"]
            self.selected_section["name"] = self.name_var.get()
            
            # Update canvas text
            if "text_id" in self.selected_section:
                self.canvas.itemconfig(self.selected_section["text_id"], text=self.selected_section["name"])
            
            # Update list
            self.update_section_list()
            print(f"✏️ Renamed section: '{old_name}' → '{self.selected_section['name']}'")
    
    def update_target_field(self, event=None):
        """Update selected section target field."""
        if self.selected_section:
            self.selected_section["target_field"] = self.field_var.get()
            self.update_section_list()
            print(f"🎯 Mapped section '{self.selected_section['name']}' → field '{self.field_var.get()}'")
    
    def save_sections(self):
        """Save section configuration to JSON file."""
        if not any(self.sections[page] for page in self.sections):
            messagebox.showwarning("No Sections", "No sections defined to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Section Configuration",
            defaultextension=".json",
            initialfile="a3_section_config.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Prepare data for saving (remove canvas IDs)
            save_data = {}
            for page_key in self.sections:
                save_data[page_key] = []
                for section in self.sections[page_key]:
                    clean_section = {
                        "id": section["id"],
                        "name": section["name"],
                        "page": section["page"],
                        "rect": section["rect"],
                        "target_field": section.get("target_field", "")
                    }
                    save_data[page_key].append(clean_section)
            
            # Add metadata
            save_data["_metadata"] = {
                "version": "1.0",
                "description": "A3 OCR Section Configuration",
                "total_sections": sum(len(save_data[page]) for page in save_data if not page.startswith("_"))
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"💾 Saved {save_data['_metadata']['total_sections']} sections to: {file_path}")
            messagebox.showinfo("Success", f"Sections saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sections: {e}")
    
    def load_sections(self):
        """Load section configuration from JSON file."""
        file_path = filedialog.askopenfilename(
            title="Load Section Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing sections
            for page_key in self.sections:
                self.sections[page_key] = []
            
            # Load sections
            for page_key in ["page_1", "page_2"]:
                if page_key in data:
                    self.sections[page_key] = data[page_key]
            
            # Update display
            self.display_page(self.current_page)
            
            total_sections = sum(len(self.sections[page]) for page in self.sections)
            print(f"📂 Loaded {total_sections} sections from: {file_path}")
            messagebox.showinfo("Success", f"Loaded {total_sections} sections")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sections: {e}")
    
    def run(self):
        """Start the application."""
        print("🎯 A3 Section Definition Tool started")
        print("📖 Instructions:")
        print("   1. Load your A3 template PDF")
        print("   2. Switch between pages")
        print("   3. Click and drag to define sections")
        print("   4. Name sections and map to fields")
        print("   5. Save section configuration")
        self.root.mainloop()

def main():
    """Main entry point."""
    app = A3SectionDefiner()
    app.run()

if __name__ == "__main__":
    main()