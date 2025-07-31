# 🎯 Field Positioning Tool Guide

## 🔥 **Custom Text Field Positioning**

Create **transparent text fields** positioned **exactly where you want them** on your A3 template!

## 🚀 **Quick Start**

### **1. Launch the Tool**
```powershell
python field_positioning_tool.py
```

### **2. Load Your Template**
- Click **"Load A3 Template"**
- Select: `A3_templates/More4Life A3 Goals - blank.pdf`

### **3. Position Fields**
1. **Enter field name** (e.g., "danger_circle", "goals_money")
2. **Click and drag** on the PDF to create a text field rectangle
3. **Repeat** for all areas where you want text fields

### **4. Save Configuration**
- Click **"Save Field Positions"**
- Save as: `custom_field_positions.json`

### **5. Create Template**
- Click **"Create PDF Template"**
- Get your custom template in `processed_documents/`

## 📊 **Features**

### **🎯 Visual Positioning**
- **Live PDF preview** - see exactly where you're placing fields
- **Click and drag** to define field boundaries
- **Red rectangles** show existing fields
- **Blue rectangles** show field being created

### **📄 Page Support**
- **Page 1 & Page 2** navigation
- **Different fields** for each page
- **Independent positioning** per page

### **🛠️ Field Management**
- **Add fields** by name and position
- **Delete fields** from the list
- **Real-time preview** of all fields
- **Coordinate display** for precision

### **💾 Configuration**
- **Save/Load** field positions as JSON
- **Reusable configurations** for different templates
- **Share configurations** with others

## 🎯 **Field Naming Examples**

### **Page 1 Fields:**
```
- danger_circle_1
- danger_circle_2  
- opportunity_main
- strength_top
- financial_right
- career_notes
- additional_info
```

### **Page 2 Fields:**
```
- money_goals
- money_now  
- money_todo
- business_goals
- business_now
- business_todo
- leisure_goals
- health_now
- family_todo
```

## 📁 **File Output**

### **Configuration File:**
```json
{
  "page_1": [
    {
      "name": "danger_circle_1",
      "rect": [45, 180, 275, 220],
      "type": "text",
      "multiline": true,
      "fontsize": 10
    }
  ],
  "page_2": [
    {
      "name": "money_goals", 
      "rect": [50, 150, 160, 200],
      "type": "text",
      "multiline": true,
      "fontsize": 10
    }
  ]
}
```

### **PDF Template:**
- **Transparent text fields** at your exact positions
- **No visible borders** or backgrounds
- **Professional appearance**
- **Ready for copy/paste workflow**

## 🎨 **Seamless Integration**

### **✅ What You Get:**
- **Invisible text fields** - blend perfectly with PDF
- **Exact positioning** - place fields precisely where needed
- **Custom layouts** - match your specific document design
- **Professional results** - clean, seamless appearance

### **🔧 Technical Details:**
- **Transparent background** (`fill_color = None`)
- **No borders** (`border_width = 0`)
- **Black text** on transparent background
- **Multi-line support** for longer content
- **Clickable fields** for editing

## 💡 **Pro Tips**

### **🎯 Positioning Strategy:**
1. **Start with main areas** (circles, boxes, lines)
2. **Create fields slightly larger** than text areas
3. **Use descriptive names** for easy identification
4. **Test positioning** with sample text

### **📏 Coordinate System:**
- **Origin (0,0)** is top-left corner
- **X increases** going right
- **Y increases** going down
- **Units** are in PDF points (72 points = 1 inch)

### **🔄 Workflow Integration:**
1. **Position fields** with this tool
2. **Save configuration** 
3. **Run A3 automation** to extract text
4. **Open custom template** 
5. **Copy/paste** extracted text into positioned fields

## 🎉 **Result**

**Perfect A3 templates** with:
- ✅ **Exact field positioning**
- ✅ **Transparent, seamless appearance** 
- ✅ **Custom layouts** for any design
- ✅ **Professional results**

Your text fields will be **completely invisible** until you click on them - creating a **seamless, professional appearance**! 🚀✨