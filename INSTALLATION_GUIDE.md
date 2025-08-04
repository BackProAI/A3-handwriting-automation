# 🚀 A3 Document Automation - Installation Guide

## 📦 You've Downloaded the ZIP File - Now What?

### **Quick Setup (2 minutes):**

1. **Extract the ZIP file** to any folder (e.g., `C:\A3_Automation\` or `~/A3_Automation/`)

2. **Create Desktop Launcher** - Choose ONE method:

   **🔴 Method 1 - Automatic (Windows):**
   ```
   Double-click: create_desktop_launcher.bat
   ```

   **🟡 Method 2 - PowerShell (Windows):**
   ```
   Right-click: create_desktop_launcher.ps1 → Run with PowerShell
   ```

   **🟢 Method 3 - Python (All Systems):**
   ```
   Double-click: install_desktop_app.py
   ```

3. **Done!** You'll have a desktop shortcut called **"A3 Document Automation"**

4. **Double-click the shortcut** to launch the app

---

## 🎯 What Each File Does:

| File | Purpose |
|------|---------|
| `main_launcher.py` | **Main application** - The launcher with auto-updates |
| `create_desktop_launcher.bat` | **Windows installer** - Creates desktop shortcut |
| `install_desktop_app.py` | **Universal installer** - Works on Windows/Mac/Linux |
| `a3_sectioned_automation.py` | **Core automation** - Document processing engine |
| `processed_documents/` | **Output folder** - Contains A3_Custom_Template.pdf |
| `.env` | **API configuration** - Pre-configured OpenAI key |

---

## 📋 System Requirements:

- ✅ **Python 3.8+** (usually pre-installed on most systems)
- ✅ **Internet connection** (for OCR processing and updates)
- ✅ **Windows 10+** / **macOS 10.14+** / **Linux Ubuntu 18+**

---

## 🔧 If Desktop Shortcut Doesn't Work:

### **Manual Method:**
1. **Right-click** on your desktop
2. **New** → **Shortcut**
3. **Location:** `python "C:\path\to\your\extracted\folder\main_launcher.py"`
4. **Name:** `A3 Document Automation`
5. **Click Finish**

### **Direct Launch Method:**
```bash
# Navigate to the extracted folder and run:
python main_launcher.py
```

---

## 🎮 How to Use:

1. **Launch** the desktop shortcut
2. **Launcher window opens** with version info and buttons
3. **Click "Launch A3 Automation"** 
4. **Select your handwritten document** (PDF or image)
5. **Magic happens!** Text is extracted and populated into A3_Custom_Template.pdf
6. **Find results** in the `processed_documents/` folder

---

## 🔄 Updates:

- **Automatic:** App checks GitHub for updates on startup
- **Manual:** Click "Check for Updates" in the launcher
- **Always latest:** Download fresh ZIP from GitHub

---

## ❓ Troubleshooting:

### **"Python not found" error:**
- Install Python from: https://python.org/downloads
- Make sure "Add to PATH" is checked during installation

### **"Permission denied" error:**
- Right-click script → "Run as administrator" 
- Or move folder to your user directory (not Program Files)

### **"API key not found" error:**
- The `.env` file should contain your OpenAI API key
- Check that it wasn't blocked by antivirus

### **Desktop shortcut not working:**
- Try the Python installer: `python install_desktop_app.py`
- Or run directly: `python main_launcher.py`

---

## 🎉 Features:

- ✅ **Automatic handwriting recognition** with GPT-4o
- ✅ **Custom PDF template population**
- ✅ **Desktop launcher with auto-updates**
- ✅ **Drag-and-drop document processing**
- ✅ **Page detection and reordering**
- ✅ **Field positioning tools**
- ✅ **Pre-configured API integration**

---

## 📞 Support:

- **Issues:** Check the GitHub repository issues page
- **Updates:** Download latest ZIP from GitHub releases
- **Questions:** Contact the development team

---

## 🚀 Ready to Process Documents!

**Your A3 Document Automation system is now ready to transform handwritten documents into structured digital text!**

### Next Steps:
1. **Click your desktop shortcut**
2. **Process your first document**
3. **Enjoy automated handwriting recognition!**

---

*Version: 1.0.2 | Last Updated: August 2025*