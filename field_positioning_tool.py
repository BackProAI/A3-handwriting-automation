#!/usr/bin/env python3
"""
Interactive Field Positioning Tool
Helps you position text fields exactly where you want them on your A3 template
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from pathlib import Path
import json
import io  # Add io import for BytesIO
from PIL import Image, ImageTk
from typing import Dict, List, Tuple

class FieldPositioningTool:
    """Interactive tool for positioning text fields on PDF templates."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("A3 Field Positioning Tool")
        self.root.geometry("1200x800")
        
        # Data
        self.pdf_path = None
        self.pdf_doc = None
        self.current_page = 0
        self.canvas_scale = 1.0
        self.fields = {"page_1": [], "page_2": []}
        self.current_field_name = ""
        self.selection_start = None
        self.selection_rect = None
        
        # Field editing state
        self.editing_field = None
        self.editing_field_index = None
        self.edit_mode = None  # 'move', 'resize_tl', 'resize_tr', 'resize_bl', 'resize_br', 'resize_t', 'resize_b', 'resize_l', 'resize_r'
        self.edit_start_pos = None
        self.edit_original_rect = None
        self.resize_handles = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (left side)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # PDF loader
        ttk.Label(control_frame, text="📄 PDF Template", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(control_frame, text="Load A3 Template", command=self.load_pdf).pack(fill=tk.X, pady=(0, 10))
        
        # Page navigation
        ttk.Label(control_frame, text="📖 Page Navigation", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        page_frame = ttk.Frame(control_frame)
        page_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(page_frame, text="Page 1", command=lambda: self.show_page(0)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(page_frame, text="Page 2", command=lambda: self.show_page(1)).pack(side=tk.LEFT)
        
        # Field creation
        ttk.Label(control_frame, text="➕ Add Text Field", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(control_frame, text="Field Name:").pack(anchor=tk.W)
        self.field_name_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.field_name_var, width=25).pack(fill=tk.X, pady=(0, 5))
        ttk.Label(control_frame, text="1. Enter field name\n2. Click and drag on PDF to create field", 
                 justify=tk.LEFT, foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        # Field list
        ttk.Label(control_frame, text="📋 Current Fields", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        # Fields listbox with scrollbar
        list_frame = ttk.Frame(control_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.fields_listbox = tk.Listbox(list_frame, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.fields_listbox.yview)
        self.fields_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.fields_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind field list selection
        self.fields_listbox.bind("<<ListboxSelect>>", self.on_field_list_select)
        
        # Field controls
        ttk.Button(control_frame, text="Delete Selected", command=self.delete_field).pack(fill=tk.X, pady=(0, 5))
        
        # Save/Load
        ttk.Label(control_frame, text="💾 Configuration", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        ttk.Button(control_frame, text="Save Field Positions", command=self.save_config).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(control_frame, text="Load Field Positions", command=self.load_config).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(control_frame, text="Create PDF Template", command=self.create_template).pack(fill=tk.X, pady=(10, 0))
        
        # Canvas (right side)
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(canvas_frame, text="🎯 PDF Template - Click and drag to create text fields", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=600, height=800)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas bindings
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
    def load_pdf(self):
        """Load a PDF template."""
        file_path = filedialog.askopenfilename(
            title="Select A3 Template PDF",
            filetypes=[("PDF files", "*.pdf")],
            initialdir="A3_templates"
        )
        
        if file_path:
            try:
                self.pdf_path = Path(file_path)
                self.pdf_doc = fitz.open(file_path)
                self.show_page(0)
                messagebox.showinfo("Success", f"Loaded PDF: {self.pdf_path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load PDF: {e}")
    
    def show_page(self, page_num: int):
        """Display a specific page of the PDF."""
        if not self.pdf_doc or page_num >= len(self.pdf_doc):
            return
        
        self.current_page = page_num
        page = self.pdf_doc[page_num]
        
        # Convert page to image
        mat = fitz.Matrix(2, 2)  # 2x zoom
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("ppm")
        
        # Convert to PIL Image and then to Tkinter
        pil_image = Image.open(io.BytesIO(img_data))
        self.canvas_scale = min(600 / pil_image.width, 800 / pil_image.height)
        
        display_width = int(pil_image.width * self.canvas_scale)
        display_height = int(pil_image.height * self.canvas_scale)
        
        pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        self.canvas_image = ImageTk.PhotoImage(pil_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Draw existing fields
        self.draw_existing_fields()
        self.update_fields_list()
    
    def draw_existing_fields(self):
        """Draw existing field rectangles on the canvas."""
        # Clear existing field graphics
        self.canvas.delete("field")
        self.canvas.delete("handle")
        self.resize_handles = []
        
        page_key = f"page_{self.current_page + 1}"
        if page_key in self.fields:
            for i, field in enumerate(self.fields[page_key]):
                rect = field["rect"]
                # Scale coordinates to canvas
                x1, y1, x2, y2 = [coord * self.canvas_scale * 2 for coord in rect]  # 2x for the zoom
                
                # Determine if this field is selected
                is_selected = (self.editing_field_index == i)
                outline_color = "blue" if is_selected else "red"
                outline_width = 3 if is_selected else 2
                
                # Draw field rectangle
                field_rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    outline=outline_color, 
                    width=outline_width,
                    fill="",
                    tags=("field", f"field_{i}")
                )
                
                # Draw field name
                self.canvas.create_text(
                    (x1 + x2) / 2, y1 - 15, 
                    text=field['name'], 
                    fill=outline_color,
                    font=("Arial", 10, "bold"),
                    tags=("field", f"field_{i}")
                )
                
                # Draw resize handles if this field is selected
                if is_selected:
                    self.draw_resize_handles(x1, y1, x2, y2, i)
    
    def draw_resize_handles(self, x1, y1, x2, y2, field_index):
        """Draw resize handles around a selected field."""
        handle_size = 8
        half_handle = handle_size // 2
        
        # Corner handles
        handles = [
            ("tl", x1 - half_handle, y1 - half_handle, x1 + half_handle, y1 + half_handle),  # Top-left
            ("tr", x2 - half_handle, y1 - half_handle, x2 + half_handle, y1 + half_handle),  # Top-right
            ("bl", x1 - half_handle, y2 - half_handle, x1 + half_handle, y2 + half_handle),  # Bottom-left
            ("br", x2 - half_handle, y2 - half_handle, x2 + half_handle, y2 + half_handle),  # Bottom-right
        ]
        
        # Edge handles
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        handles.extend([
            ("t", mid_x - half_handle, y1 - half_handle, mid_x + half_handle, y1 + half_handle),  # Top
            ("b", mid_x - half_handle, y2 - half_handle, mid_x + half_handle, y2 + half_handle),  # Bottom
            ("l", x1 - half_handle, mid_y - half_handle, x1 + half_handle, mid_y + half_handle),  # Left
            ("r", x2 - half_handle, mid_y - half_handle, x2 + half_handle, mid_y + half_handle),  # Right
        ])
        
        # Draw handles
        self.resize_handles = []
        for handle_type, hx1, hy1, hx2, hy2 in handles:
            handle_id = self.canvas.create_rectangle(
                hx1, hy1, hx2, hy2,
                fill="white",
                outline="blue",
                width=2,
                tags=("handle", f"handle_{handle_type}_{field_index}")
            )
            self.resize_handles.append({
                "id": handle_id,
                "type": handle_type,
                "field_index": field_index,
                "bounds": (hx1, hy1, hx2, hy2)
            })
    
    def on_canvas_click(self, event):
        """Handle canvas click for field creation or editing."""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Check if clicking on a resize handle
        handle_clicked = self.get_handle_at_position(canvas_x, canvas_y)
        if handle_clicked:
            self.start_field_resize(handle_clicked, canvas_x, canvas_y)
            return
        
        # Check if clicking on an existing field
        field_clicked = self.get_field_at_position(canvas_x, canvas_y)
        if field_clicked is not None:
            self.select_field(field_clicked)
            self.start_field_move(canvas_x, canvas_y)
            return
        
        # If not clicking on a field, start creating a new field
        if not self.field_name_var.get().strip():
            messagebox.showinfo("Info", "Please enter a field name first!")
            return
        
        self.start_field_creation(canvas_x, canvas_y)
    
    def get_handle_at_position(self, x, y):
        """Check if the position is over a resize handle."""
        for handle in self.resize_handles:
            hx1, hy1, hx2, hy2 = handle["bounds"]
            if hx1 <= x <= hx2 and hy1 <= y <= hy2:
                return handle
        return None
    
    def get_field_at_position(self, x, y):
        """Check if the position is over a field rectangle."""
        page_key = f"page_{self.current_page + 1}"
        if page_key not in self.fields:
            return None
        
        for i, field in enumerate(self.fields[page_key]):
            rect = field["rect"]
            # Scale coordinates to canvas
            x1, y1, x2, y2 = [coord * self.canvas_scale * 2 for coord in rect]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return i
        return None
    
    def select_field(self, field_index):
        """Select a field for editing."""
        self.editing_field_index = field_index
        page_key = f"page_{self.current_page + 1}"
        self.editing_field = self.fields[page_key][field_index]
        self.draw_existing_fields()
        
        # Update the field list selection
        self.fields_listbox.selection_clear(0, tk.END)
        self.fields_listbox.selection_set(field_index)
    
    def start_field_resize(self, handle, x, y):
        """Start resizing a field."""
        self.edit_mode = f"resize_{handle['type']}"
        self.edit_start_pos = (x, y)
        self.edit_original_rect = self.editing_field["rect"].copy()
        self.canvas.configure(cursor=self.get_resize_cursor(handle['type']))
    
    def start_field_move(self, x, y):
        """Start moving a field."""
        self.edit_mode = "move"
        self.edit_start_pos = (x, y)
        self.edit_original_rect = self.editing_field["rect"].copy()
        self.canvas.configure(cursor="fleur")
    
    def start_field_creation(self, x, y):
        """Start creating a new field."""
        self.edit_mode = "create"
        self.selection_start = (x, y)
        self.canvas.configure(cursor="crosshair")
    
    def get_resize_cursor(self, handle_type):
        """Get the appropriate cursor for resize handle."""
        cursors = {
            "tl": "top_left_corner",
            "tr": "top_right_corner", 
            "bl": "bottom_left_corner",
            "br": "bottom_right_corner",
            "t": "top_side",
            "b": "bottom_side",
            "l": "left_side",
            "r": "right_side"
        }
        return cursors.get(handle_type, "arrow")
        
    def on_canvas_drag(self, event):
        """Handle canvas drag for field creation or editing."""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        if self.edit_mode == "create":
            self.handle_field_creation_drag(canvas_x, canvas_y)
        elif self.edit_mode == "move":
            self.handle_field_move_drag(canvas_x, canvas_y)
        elif self.edit_mode and self.edit_mode.startswith("resize_"):
            self.handle_field_resize_drag(canvas_x, canvas_y)
    
    def handle_field_creation_drag(self, x, y):
        """Handle dragging during field creation."""
        if not self.selection_start:
            return
        
        # Remove previous selection rectangle
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # Draw new selection rectangle
        x1, y1 = self.selection_start
        self.selection_rect = self.canvas.create_rectangle(x1, y1, x, y, outline="blue", width=2)
    
    def handle_field_move_drag(self, x, y):
        """Handle dragging during field move."""
        if not self.edit_start_pos or not self.editing_field:
            return
        
        # Calculate movement delta
        start_x, start_y = self.edit_start_pos
        dx = (x - start_x) / (self.canvas_scale * 2)  # Convert to PDF coordinates
        dy = (y - start_y) / (self.canvas_scale * 2)
        
        # Update field position
        new_rect = [
            self.edit_original_rect[0] + dx,
            self.edit_original_rect[1] + dy,
            self.edit_original_rect[2] + dx,
            self.edit_original_rect[3] + dy
        ]
        
        self.editing_field["rect"] = new_rect
        self.draw_existing_fields()
    
    def handle_field_resize_drag(self, x, y):
        """Handle dragging during field resize."""
        if not self.edit_start_pos or not self.editing_field:
            return
        
        # Calculate movement delta
        start_x, start_y = self.edit_start_pos
        dx = (x - start_x) / (self.canvas_scale * 2)  # Convert to PDF coordinates
        dy = (y - start_y) / (self.canvas_scale * 2)
        
        # Get original rect
        orig_x1, orig_y1, orig_x2, orig_y2 = self.edit_original_rect
        
        # Apply resize based on handle type
        resize_type = self.edit_mode.replace("resize_", "")
        new_rect = [orig_x1, orig_y1, orig_x2, orig_y2]
        
        if "l" in resize_type:  # Left side
            new_rect[0] = orig_x1 + dx
        if "r" in resize_type:  # Right side
            new_rect[2] = orig_x2 + dx
        if "t" in resize_type:  # Top side
            new_rect[1] = orig_y1 + dy
        if "b" in resize_type:  # Bottom side
            new_rect[3] = orig_y2 + dy
        
        # Ensure minimum size
        min_size = 10 / (self.canvas_scale * 2)  # 10 pixels minimum in PDF coordinates
        if new_rect[2] - new_rect[0] < min_size:
            if "l" in resize_type:
                new_rect[0] = new_rect[2] - min_size
            else:
                new_rect[2] = new_rect[0] + min_size
        
        if new_rect[3] - new_rect[1] < min_size:
            if "t" in resize_type:
                new_rect[1] = new_rect[3] - min_size
            else:
                new_rect[3] = new_rect[1] + min_size
        
        self.editing_field["rect"] = new_rect
        self.draw_existing_fields()
    
    def on_canvas_release(self, event):
        """Handle canvas release for field creation or editing."""
        if self.edit_mode == "create":
            self.finish_field_creation(event)
        elif self.edit_mode in ["move"] or (self.edit_mode and self.edit_mode.startswith("resize_")):
            self.finish_field_edit()
        
        # Reset state
        self.edit_mode = None
        self.edit_start_pos = None
        self.edit_original_rect = None
        self.canvas.configure(cursor="arrow")
    
    def finish_field_creation(self, event):
        """Finish creating a new field."""
        if not self.selection_start:
            return
        
        current_pos = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        
        # Calculate field rectangle in PDF coordinates
        x1, y1 = self.selection_start
        x2, y2 = current_pos
        
        # Convert to PDF coordinates (undo canvas scaling and zoom)
        pdf_x1 = min(x1, x2) / (self.canvas_scale * 2)
        pdf_y1 = min(y1, y2) / (self.canvas_scale * 2)
        pdf_x2 = max(x1, x2) / (self.canvas_scale * 2)
        pdf_y2 = max(y1, y2) / (self.canvas_scale * 2)
        
        # Only create field if it has reasonable size
        if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
            field_name = self.field_name_var.get().strip()
            if field_name:
                self.add_field(field_name, [pdf_x1, pdf_y1, pdf_x2, pdf_y2])
                self.field_name_var.set("")  # Clear field name
        
        # Clean up
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.selection_start = None
        self.selection_rect = None
    
    def finish_field_edit(self):
        """Finish editing a field."""
        # Update the field list to reflect changes
        self.update_fields_list()
        print(f"✅ Updated field: {self.editing_field['name']}")
    
    def on_canvas_motion(self, event):
        """Handle mouse motion for cursor changes."""
        if self.edit_mode:  # Don't change cursor during editing
            return
        
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Check if over a resize handle
        handle = self.get_handle_at_position(canvas_x, canvas_y)
        if handle:
            cursor = self.get_resize_cursor(handle['type'])
            self.canvas.configure(cursor=cursor)
            return
        
        # Check if over a field
        field_index = self.get_field_at_position(canvas_x, canvas_y)
        if field_index is not None:
            self.canvas.configure(cursor="fleur")  # Move cursor
            return
        
        # Default cursor
        self.canvas.configure(cursor="arrow")
    
    def add_field(self, name: str, rect: List[float]):
        """Add a field to the current page."""
        page_key = f"page_{self.current_page + 1}"
        
        # Check if field name already exists
        existing_names = [f["name"] for f in self.fields.get(page_key, [])]
        if name in existing_names:
            messagebox.showwarning("Warning", f"Field '{name}' already exists on this page!")
            return
        
        field = {
            "name": name,
            "rect": rect,
            "type": "text",
            "multiline": True,
            "fontsize": 10
        }
        
        if page_key not in self.fields:
            self.fields[page_key] = []
        
        self.fields[page_key].append(field)
        self.draw_existing_fields()
        self.update_fields_list()
        
        messagebox.showinfo("Success", f"Added field '{name}' to {page_key}")
    
    def on_field_list_select(self, event):
        """Handle field list selection."""
        selection = self.fields_listbox.curselection()
        if selection:
            field_index = selection[0]
            self.select_field(field_index)
    
    def update_fields_list(self):
        """Update the fields listbox."""
        self.fields_listbox.delete(0, tk.END)
        
        page_key = f"page_{self.current_page + 1}"
        if page_key in self.fields:
            for field in self.fields[page_key]:
                self.fields_listbox.insert(tk.END, f"{field['name']} ({field['rect'][0]:.0f},{field['rect'][1]:.0f} → {field['rect'][2]:.0f},{field['rect'][3]:.0f})")
    
    def delete_field(self):
        """Delete the selected field."""
        if self.editing_field_index is None:
            messagebox.showinfo("Info", "Please select a field to delete!")
            return
        
        page_key = f"page_{self.current_page + 1}"
        
        if page_key in self.fields and self.editing_field_index < len(self.fields[page_key]):
            field_name = self.fields[page_key][self.editing_field_index]["name"]
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Delete field '{field_name}'?"):
                del self.fields[page_key][self.editing_field_index]
                
                # Clear selection
                self.editing_field_index = None
                self.editing_field = None
                
                self.draw_existing_fields()
                self.update_fields_list()
                messagebox.showinfo("Success", f"Deleted field '{field_name}'")
    
    def save_config(self):
        """Save field configuration to JSON file."""
        if not self.fields["page_1"] and not self.fields["page_2"]:
            messagebox.showwarning("Warning", "No fields to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Field Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="custom_field_positions.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.fields, f, indent=2)
                messagebox.showinfo("Success", f"Saved field configuration to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def load_config(self):
        """Load field configuration from JSON file."""
        file_path = filedialog.askopenfilename(
            title="Load Field Configuration",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.fields = json.load(f)
                self.draw_existing_fields()
                self.update_fields_list()
                messagebox.showinfo("Success", f"Loaded field configuration from:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def create_template(self):
        """Create a PDF template with the positioned fields."""
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Please load a PDF template first!")
            return
        
        if not self.fields["page_1"] and not self.fields["page_2"]:
            messagebox.showwarning("Warning", "No fields defined! Please add some text fields first.")
            return
        
        try:
            from a3_template_processor import A3TemplateProcessor
            
            # Save current config temporarily
            temp_config_path = Path("temp_field_config.json")
            with open(temp_config_path, 'w') as f:
                json.dump(self.fields, f, indent=2)
            
            # Create template with custom fields
            processor = A3TemplateProcessor(self.pdf_path)
            output_path = Path("processed_documents/A3_Custom_Template.pdf")
            template_path = processor.create_template_with_custom_fields(temp_config_path, output_path)
            
            # Clean up temp file
            if temp_config_path.exists():
                temp_config_path.unlink()
            
            messagebox.showinfo("Success", f"Created PDF template with your custom fields:\n{template_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create template: {e}")
    
    def run(self):
        """Run the positioning tool."""
        self.root.mainloop()
        
        # Clean up
        if self.pdf_doc:
            self.pdf_doc.close()

def main():
    """Run the field positioning tool."""
    print("🎯 Starting A3 Field Positioning Tool")
    print("=" * 40)
    
    try:
        tool = FieldPositioningTool()
        tool.run()
    except Exception as e:
        print(f"❌ Error running positioning tool: {e}")

if __name__ == "__main__":
    import io
    main()