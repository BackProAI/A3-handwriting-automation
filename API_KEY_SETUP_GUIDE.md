# 🔐 OpenAI API Key Setup Guide for more4life Users

## 📋 What Each User Needs to Do:

### **Step 1: Get Your OpenAI API Key**
1. Go to: https://platform.openai.com/api-keys
2. Log in with your OpenAI account (or create one)
3. Click **"Create new secret key"**
4. Give it a name like "A3_Automation"
5. **Copy the key** (starts with "sk-...")
6. **⚠️ IMPORTANT**: Save this key somewhere safe - you can only see it once!

### **Step 2: Install A3 Automation**
1. Download `A3_Distribution.zip` from the GitHub release
2. Extract the files to any folder
3. Right-click `install_a3.bat` → **"Run as administrator"**
4. This creates a desktop shortcut "A3 Automation"

### **Step 3: Configure Your API Key**
1. **Double-click** the "A3 Automation" desktop shortcut
2. Click **"Launch A3 Automation"**
3. On first run, you'll be prompted to enter your API key
4. **Paste your API key** when prompted
5. The system will save it securely for future use

## 🎯 Alternative Manual Setup:

If the automatic setup doesn't work:

1. **Open PowerShell** (Start → type "PowerShell")
2. **Run this command** (replace YOUR_API_KEY with your actual key):
   ```
   [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "YOUR_API_KEY", "User")
   ```
3. **Close PowerShell** and restart A3 Automation

## ✅ Verify Setup:

Your API key is working correctly if:
- A3 Automation launches without errors
- You can process documents successfully
- Text is extracted and populated in templates

## 🆘 Troubleshooting:

**"No OpenAI API key found" error:**
- Restart your computer after setting the API key
- Try the manual PowerShell setup above
- Contact IT support if issues persist

**"Invalid API key" error:**
- Check you copied the full key (starts with "sk-")
- Ensure your OpenAI account has credits
- Try generating a new API key

## 💰 API Costs:

- GPT-4o costs approximately $0.01-0.03 per A3 document
- Recommended: Set up billing alerts on your OpenAI account
- Each user should monitor their individual usage

## 🔒 Security Notes:

- **Never share** your API key with others
- Each user should have their own API key
- Keys are stored securely on your local machine only
- Not transmitted or saved to any external servers

---

**Need Help?** Contact the development team or IT support.