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
        
        # Resize state
        self.resizing = False
        self.resize_handle = None
        self.resize_section = None
        self.resize_handles = []
        self.drag_start_x = 0
        self.drag_start_y = 0
        
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
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Double-Button-1>", self.select_section)
        self.canvas.bind("<Button-3>", self.delete_section)  # Right click to delete
        self.canvas.bind("<Motion>", self.on_mouse_move)  # For cursor changes
        
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
• Click and drag to define new sections
• Click on existing sections to select
• Drag resize handles to adjust size
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
        """Load available field names from custom_field_position.json."""
        config_path = Path("A3_templates/custom_field_position.json")
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
            print("⚠️ No custom_field_position.json found - using generic field names")
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
    
    def on_click(self, event):
        """Handle mouse click - either start drawing or start resizing."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Check if clicking on a resize handle
        handle_info = self.get_resize_handle_at(x, y)
        if handle_info:
            self.start_resize(event, handle_info)
            return
        
        # Check if clicking inside an existing section
        section_info = self.get_section_at(x, y)
        if section_info:
            self.start_move_section(event, section_info)
            return
        
        # Otherwise, start drawing a new section
        self.start_section(event)
    
    def on_drag(self, event):
        """Handle mouse drag - either draw, resize, or move."""
        if self.resizing:
            self.resize_section_handle(event)
        elif self.drawing:
            self.draw_section(event)
    
    def on_release(self, event):
        """Handle mouse release - finish current operation."""
        if self.resizing:
            self.end_resize(event)
        elif self.drawing:
            self.end_section(event)
    
    def on_mouse_move(self, event):
        """Handle mouse movement for cursor changes."""
        if self.drawing or self.resizing:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Check if over a resize handle
        handle_info = self.get_resize_handle_at(x, y)
        if handle_info:
            cursor = self.get_resize_cursor(handle_info[1])
            self.canvas.configure(cursor=cursor)
        else:
            self.canvas.configure(cursor="crosshair")
    
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
        
        # Clear existing resize handles
        self.clear_resize_handles()
        
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
            
            # Create resize handles for this section
            self.create_resize_handles(section)
    
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
            initialdir="A3_templates",
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
    
    def create_resize_handles(self, section):
        """Create resize handles for a section."""
        if "canvas_id" not in section:
            return
        
        # Get section coordinates
        pdf_rect = section["rect"]
        x1 = pdf_rect[0] * self.canvas_scale
        y1 = pdf_rect[1] * self.canvas_scale
        x2 = pdf_rect[2] * self.canvas_scale
        y2 = pdf_rect[3] * self.canvas_scale
        
        handle_size = 6
        handles = {}
        
        # Create 8 resize handles (corners and edges)
        handle_positions = {
            'nw': (x1, y1),      # Top-left
            'n': ((x1+x2)/2, y1),  # Top-center
            'ne': (x2, y1),      # Top-right
            'e': (x2, (y1+y2)/2),  # Right-center
            'se': (x2, y2),      # Bottom-right
            's': ((x1+x2)/2, y2),  # Bottom-center
            'sw': (x1, y2),      # Bottom-left
            'w': (x1, (y1+y2)/2)   # Left-center
        }
        
        for handle_type, (hx, hy) in handle_positions.items():
            handle_id = self.canvas.create_rectangle(
                hx - handle_size//2, hy - handle_size//2,
                hx + handle_size//2, hy + handle_size//2,
                fill="white", outline="blue", width=1
            )
            handles[handle_type] = handle_id
        
        section["resize_handles"] = handles
        
        # Add to global handles list for easy lookup
        for handle_type, handle_id in handles.items():
            self.resize_handles.append((handle_id, handle_type, section))
    
    def clear_resize_handles(self):
        """Clear all resize handles."""
        for handle_id, _, _ in self.resize_handles:
            self.canvas.delete(handle_id)
        self.resize_handles = []
        
        # Clear handles from sections
        for page_key in self.sections:
            for section in self.sections[page_key]:
                if "resize_handles" in section:
                    del section["resize_handles"]
    
    def get_resize_handle_at(self, x, y):
        """Get resize handle at given coordinates."""
        for handle_id, handle_type, section in self.resize_handles:
            bbox = self.canvas.bbox(handle_id)
            if bbox and bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                return (section, handle_type, handle_id)
        return None
    
    def get_section_at(self, x, y):
        """Get section at given coordinates."""
        page_key = f"page_{self.current_page}"
        
        for section in self.sections[page_key]:
            rect = section["rect"]
            canvas_x1 = rect[0] * self.canvas_scale
            canvas_y1 = rect[1] * self.canvas_scale
            canvas_x2 = rect[2] * self.canvas_scale
            canvas_y2 = rect[3] * self.canvas_scale
            
            if canvas_x1 <= x <= canvas_x2 and canvas_y1 <= y <= canvas_y2:
                return section
        return None
    
    def get_resize_cursor(self, handle_type):
        """Get appropriate cursor for resize handle."""
        cursor_map = {
            'nw': 'top_left_corner',
            'n': 'top_side',
            'ne': 'top_right_corner',
            'e': 'right_side',
            'se': 'bottom_right_corner',
            's': 'bottom_side',
            'sw': 'bottom_left_corner',
            'w': 'left_side'
        }
        return cursor_map.get(handle_type, 'arrow')
    
    def start_resize(self, event, handle_info):
        """Start resizing a section."""
        self.resizing = True
        self.resize_section, self.resize_handle, _ = handle_info
        self.drag_start_x = self.canvas.canvasx(event.x)
        self.drag_start_y = self.canvas.canvasy(event.y)
        
        print(f"🔄 Started resizing section '{self.resize_section['name']}' using {self.resize_handle} handle")
    
    def start_move_section(self, event, section):
        """Start moving a section."""
        # For now, just select the section
        # Moving functionality can be added later if needed
        page_key = f"page_{self.current_page}"
        section_idx = self.sections[page_key].index(section)
        
        self.section_listbox.selection_clear(0, tk.END)
        self.section_listbox.selection_set(section_idx)
        self.highlight_section(None)
    
    def resize_section_handle(self, event):
        """Resize section by dragging handle."""
        if not self.resizing or not self.resize_section:
            return
        
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)
        
        # Get current section rect in PDF coordinates
        rect = self.resize_section["rect"]
        pdf_x1, pdf_y1, pdf_x2, pdf_y2 = rect
        
        # Convert mouse position to PDF coordinates
        pdf_mouse_x = current_x / self.canvas_scale
        pdf_mouse_y = current_y / self.canvas_scale
        
        # Update rectangle based on handle type
        if 'n' in self.resize_handle:  # Top edge
            pdf_y1 = pdf_mouse_y
        if 's' in self.resize_handle:  # Bottom edge
            pdf_y2 = pdf_mouse_y
        if 'w' in self.resize_handle:  # Left edge
            pdf_x1 = pdf_mouse_x
        if 'e' in self.resize_handle:  # Right edge
            pdf_x2 = pdf_mouse_x
        
        # Ensure minimum size
        min_size = 20 / self.canvas_scale
        if abs(pdf_x2 - pdf_x1) < min_size or abs(pdf_y2 - pdf_y1) < min_size:
            return
        
        # Ensure proper order
        if pdf_x1 > pdf_x2:
            pdf_x1, pdf_x2 = pdf_x2, pdf_x1
        if pdf_y1 > pdf_y2:
            pdf_y1, pdf_y2 = pdf_y2, pdf_y1
        
        # Update section rect
        self.resize_section["rect"] = [pdf_x1, pdf_y1, pdf_x2, pdf_y2]
        
        # Update canvas rectangle
        canvas_x1 = pdf_x1 * self.canvas_scale
        canvas_y1 = pdf_y1 * self.canvas_scale
        canvas_x2 = pdf_x2 * self.canvas_scale
        canvas_y2 = pdf_y2 * self.canvas_scale
        
        if "canvas_id" in self.resize_section:
            self.canvas.coords(self.resize_section["canvas_id"], 
                             canvas_x1, canvas_y1, canvas_x2, canvas_y2)
        
        # Update text position
        if "text_id" in self.resize_section:
            center_x = (canvas_x1 + canvas_x2) / 2
            center_y = (canvas_y1 + canvas_y2) / 2
            self.canvas.coords(self.resize_section["text_id"], center_x, center_y)
        
        # Update resize handles
        self.update_resize_handles(self.resize_section)
    
    def update_resize_handles(self, section):
        """Update positions of resize handles for a section."""
        if "resize_handles" not in section:
            return
        
        # Get section coordinates
        pdf_rect = section["rect"]
        x1 = pdf_rect[0] * self.canvas_scale
        y1 = pdf_rect[1] * self.canvas_scale
        x2 = pdf_rect[2] * self.canvas_scale
        y2 = pdf_rect[3] * self.canvas_scale
        
        handle_size = 6
        handle_positions = {
            'nw': (x1, y1),
            'n': ((x1+x2)/2, y1),
            'ne': (x2, y1),
            'e': (x2, (y1+y2)/2),
            'se': (x2, y2),
            's': ((x1+x2)/2, y2),
            'sw': (x1, y2),
            'w': (x1, (y1+y2)/2)
        }
        
        for handle_type, handle_id in section["resize_handles"].items():
            if handle_type in handle_positions:
                hx, hy = handle_positions[handle_type]
                self.canvas.coords(handle_id,
                                 hx - handle_size//2, hy - handle_size//2,
                                 hx + handle_size//2, hy + handle_size//2)
    
    def end_resize(self, event):
        """End resizing operation."""
        if self.resizing and self.resize_section:
            print(f"✅ Finished resizing section '{self.resize_section['name']}'")
            rect = self.resize_section["rect"]
            print(f"   New dimensions: ({rect[0]:.0f}, {rect[1]:.0f}, {rect[2]:.0f}, {rect[3]:.0f})")
        
        self.resizing = False
        self.resize_section = None
        self.resize_handle = None
        self.canvas.configure(cursor="crosshair")
    
    def run(self):
        """Start the application."""
        print("🎯 A3 Section Definition Tool started")
        print("📖 Instructions:")
        print("   1. Load your A3 template PDF")
        print("   2. Switch between pages")
        print("   3. Click and drag to define new sections")
        print("   4. Drag resize handles to adjust existing sections")
        print("   5. Name sections and map to fields")
        print("   6. Save section configuration")
        self.root.mainloop()

def main():
    """Main entry point."""
    app = A3SectionDefiner()
    app.run()

if __name__ == "__main__":
    main()