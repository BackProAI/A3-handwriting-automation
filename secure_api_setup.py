#!/usr/bin/env python3
"""
Secure OpenAI API Key Setup
Helps users securely configure their API key for the A3 automation system
"""

import os
import subprocess
import sys
from pathlib import Path
import getpass

def clear_powershell_history():
    """Clear PowerShell command history to remove exposed API key."""
    try:
        print("🧹 Clearing PowerShell command history...")
        
        # Clear current session history
        subprocess.run([
            "powershell", "-Command", 
            "Clear-History; Remove-Item (Get-PSReadlineOption).HistorySavePath"
        ], shell=True, capture_output=True)
        
        print("✅ PowerShell history cleared")
        return True
    except Exception as e:
        print(f"⚠️  Could not clear PowerShell history: {e}")
        return False

def create_env_file():
    """Create a secure .env file for API key storage."""
    env_file = Path(".env")
    
    if env_file.exists():
        response = input("📁 .env file already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("❌ Setup cancelled")
            return False
    
    # Get API key securely (won't show in terminal)
    print("\n🔐 Enter your OpenAI API key (input will be hidden):")
    api_key = getpass.getpass("API Key: ").strip()
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
        proceed = input("Continue anyway? (y/n): ").lower()
        if proceed != 'y':
            return False
    
    # Create .env file content
    env_content = f"""# OpenAI API Configuration
# This file is automatically ignored by git for security
OPENAI_API_KEY={api_key}

# Security Notes:
# - This file is excluded from version control
# - Keep this file secure and private
# - Never share this file or its contents
# - Rotate your API key if compromised
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        # Set restrictive permissions (owner read/write only)
        if os.name != 'nt':  # Unix/Linux/Mac
            os.chmod(env_file, 0o600)
        
        print(f"✅ Secure .env file created: {env_file.absolute()}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def update_gitignore():
    """Ensure .env is in .gitignore for security."""
    gitignore_file = Path(".gitignore")
    
    # Read existing .gitignore
    existing_content = ""
    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            existing_content = f.read()
    
    # Check if .env is already ignored
    if ".env" in existing_content:
        print("✅ .env already in .gitignore")
        return True
    
    # Add .env to .gitignore
    try:
        with open(gitignore_file, 'a') as f:
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write('\n# Environment variables (API keys, secrets)\n')
            f.write('.env\n')
            f.write('*.env\n')
        
        print("✅ Added .env to .gitignore for security")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not update .gitignore: {e}")
        return False

def update_applications():
    """Update applications to use .env file."""
    print("\n🔧 Updating applications to use secure .env loading...")
    
    # Files to update
    files_to_update = [
        "a3_document_automation.py",
        "test_gpt4o_ocr.py"
    ]
    
    env_loading_code = '''
# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    # dotenv not installed, try to load manually
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
'''
    
    updated_files = []
    
    for file_path in files_to_update:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check if already updated
                if "load_dotenv" in content or ".env" in content:
                    print(f"✅ {file_path} already configured for .env")
                    continue
                
                # Find the import section and add env loading
                lines = content.split('\n')
                insert_index = 0
                
                # Find a good place to insert (after imports)
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_index = i + 1
                    elif line.strip() == '' and insert_index > 0:
                        insert_index = i
                        break
                
                # Insert the env loading code
                lines.insert(insert_index, env_loading_code)
                
                # Write back
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                updated_files.append(file_path)
                print(f"✅ Updated {file_path} for secure .env loading")
                
            except Exception as e:
                print(f"⚠️  Could not update {file_path}: {e}")
    
    return len(updated_files) > 0

def install_dotenv():
    """Install python-dotenv for secure environment loading."""
    try:
        print("📦 Installing python-dotenv for secure environment management...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
        print("✅ python-dotenv installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Could not install python-dotenv, will use manual loading")
        return False

def verify_setup():
    """Verify the secure setup is working."""
    print("\n🔍 Verifying secure setup...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    
    # Try to load the API key
    try:
        # Try with dotenv first
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Manual loading
            with open(".env") as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            # Show partial key for verification (hide most of it)
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"✅ API key loaded successfully: {masked_key}")
            return True
        else:
            print("❌ API key not found in environment")
            return False
            
    except Exception as e:
        print(f"❌ Failed to verify setup: {e}")
        return False

def security_recommendations():
    """Display security recommendations."""
    print("\n🛡️  SECURITY RECOMMENDATIONS:")
    print("=" * 50)
    print("✅ API key is now stored in .env file (not in terminal history)")
    print("✅ .env file is excluded from version control")
    print("✅ Applications load key automatically from .env")
    print("✅ PowerShell history cleared")
    print()
    print("🔒 ADDITIONAL SECURITY STEPS:")
    print("1. Never share your .env file")
    print("2. Add .env to any cloud storage ignore lists")
    print("3. Rotate your API key if you suspect compromise")
    print("4. Monitor your OpenAI usage at: https://platform.openai.com/usage")
    print("5. Set usage limits in your OpenAI account")
    print()
    print("⚠️  IF YOUR KEY WAS COMPROMISED:")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Delete the old key")
    print("3. Create a new key")
    print("4. Update your .env file with the new key")

def main():
    """Main security setup function."""
    print("🔐 OpenAI API Key Security Setup")
    print("=" * 40)
    print("This tool will help you securely configure your API key")
    print()
    
    # Step 1: Clear PowerShell history
    clear_powershell_history()
    
    # Step 2: Install dotenv for secure loading
    install_dotenv()
    
    # Step 3: Create secure .env file
    if not create_env_file():
        print("❌ Failed to create secure .env file")
        return
    
    # Step 4: Update .gitignore
    update_gitignore()
    
    # Step 5: Update applications
    update_applications()
    
    # Step 6: Verify setup
    if verify_setup():
        print("\n🎉 SECURE SETUP COMPLETE!")
        security_recommendations()
        
        print("\n🚀 NEXT STEPS:")
        print("1. You can now safely run: python a3_document_automation.py")
        print("2. Your API key will be loaded automatically from .env")
        print("3. No need to set environment variables manually")
        
    else:
        print("\n❌ Setup verification failed")
        print("Please check the steps above and try again")

if __name__ == "__main__":
    main() 