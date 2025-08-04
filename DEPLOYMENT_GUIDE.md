# 🚀 A3 Document Automation - Deployment Guide

This guide will help you deploy the A3 Document Automation system as a desktop application for more4life.

## 📋 Prerequisites

1. **Python 3.8+** installed on your development machine
2. **Git** for version control
3. **GitHub repository** set up for your project
4. **OpenAI API key** for GPT-4o integration

## 🔧 Setup Steps

### 1. Update Configuration

**Update GitHub Repository Info:**
```python
# In main_launcher.py, line 25:
self.github_repo = "your-username/A3_handtotext"  # ← UPDATE THIS

# In app_config.json:
"github_repo": "your-username/A3_handtotext",  # ← UPDATE THIS
"github_api_url": "https://api.github.com/repos/your-username/A3_handtotext/releases/latest"  # ← UPDATE THIS
```

### 2. Install Build Dependencies

```bash
pip install pyinstaller
pip install -r requirements.txt
```

### 3. Create Executable

```bash
# Run the build script
python build_executable.py

# Choose option 1 (Build executable)
```

This creates:
- `A3_Distribution/A3_Automation.exe` - The main executable
- `A3_Distribution/install_a3.bat` - Installation script
- `A3_Distribution/README.txt` - User instructions

### 4. Test the Executable

```bash
# Test the executable locally
cd A3_Distribution
A3_Automation.exe
```

## 🎯 Deployment Options

### Option A: Simple File Distribution

1. **Zip the Distribution folder:**
   ```bash
   # Create A3_Automation_v1.0.zip containing:
   # - A3_Automation.exe
   # - install_a3.bat  
   # - README.txt
   ```

2. **Share with users:**
   - Email the zip file
   - Users extract and run `install_a3.bat`
   - Creates desktop shortcut automatically

### Option B: GitHub Releases (RECOMMENDED)

1. **Create a GitHub Release:**
   ```bash
   # Tag your version
   git tag v1.0.0
   git push origin v1.0.0
   
   # Create release on GitHub with:
   # - Tag: v1.0.0
   # - Title: "A3 Document Automation v1.0.0"
   # - Attach: A3_Automation_v1.0.zip
   ```

2. **Auto-Update Setup:**
   - Users download initial version from GitHub
   - App automatically checks for new releases
   - Updates download and install automatically

### Option C: Network Deployment

1. **Place on shared network drive:**
   ```
   \\company-server\software\A3_Automation\
   ├── A3_Automation.exe
   ├── install_a3.bat
   └── README.txt
   ```

2. **Create deployment script:**
   ```batch
   @echo off
   echo Installing A3 Automation from network...
   copy "\\server\path\A3_Automation.exe" "%PROGRAMFILES%\A3_Automation\"
   ```

## 📱 User Installation Process

### For End Users (more4life staff):

1. **Download** the `A3_Automation_v1.0.zip` file
2. **Extract** to any folder (e.g., Desktop)
3. **Right-click** on `install_a3.bat` → "Run as administrator"
4. **Follow** the installation prompts
5. **Use** the desktop shortcut to launch

### First Launch:
- App checks for updates automatically
- Downloads latest templates from GitHub
- Ready to process documents!

## 🔄 Update Process

### For Developers (You):

1. **Make changes** to your code
2. **Update version** in `version.txt`:
   ```
   1.1.0
   ```
3. **Commit and push** changes:
   ```bash
   git add .
   git commit -m "Update to v1.1.0 - New features"
   git push origin main
   ```
4. **Create new release** on GitHub:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
5. **Build new executable** (optional):
   ```bash
   python build_executable.py
   ```

### For End Users:
- **Automatic**: App checks for updates on startup
- **Manual**: Click "Check for Updates" in launcher
- Updates download and install automatically

## 🛡️ Security Considerations

1. **API Keys:**
   - Store OpenAI API key in environment variable
   - Or use encrypted configuration file
   - Never hardcode in source code

2. **Code Signing:**
   - Consider code signing certificate for .exe files
   - Reduces Windows security warnings

3. **Network Access:**
   - App needs internet for:
     - OpenAI API calls
     - GitHub update checks
     - Template downloads

## 🐛 Troubleshooting

### Common Issues:

1. **"App not found" error:**
   - Check `a3_sectioned_automation.py` exists
   - Rebuild executable with all files included

2. **Update check fails:**
   - Verify GitHub repository URL
   - Check internet connection
   - Ensure repository is public

3. **OCR not working:**
   - Verify OpenAI API key is set
   - Check API key permissions
   - Ensure sufficient API credits

### Debug Mode:
```python
# In app_config.json, set:
"show_debug_info": true
```

## 📊 Monitoring Usage

### Analytics Options:

1. **Simple logging:**
   ```python
   # Add to main_launcher.py
   import logging
   logging.basicConfig(filename='app_usage.log', level=logging.INFO)
   ```

2. **GitHub download tracking:**
   - Monitor release download counts
   - Track update adoption rates

3. **Error reporting:**
   - Capture and log errors
   - Optional telemetry for improvements

## 🎉 Deployment Checklist

- [ ] Updated GitHub repository URLs in code
- [ ] Tested executable locally
- [ ] Created GitHub release with tagged version
- [ ] Tested auto-update functionality
- [ ] Created user documentation
- [ ] Prepared installation package
- [ ] Communicated deployment to users
- [ ] Set up monitoring/support process

## 📞 Support

After deployment, provide users with:
- **Installation guide** (README.txt)
- **Contact information** for support
- **Known issues** and solutions
- **Feature request** process

---

🚀 **Ready to deploy!** Follow these steps and your A3 automation will be running smoothly on more4life desktops.