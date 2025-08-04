#!/usr/bin/env python3
"""
GitHub Token Setup for A3 Document Automation
Helps users configure their GitHub Personal Access Token for auto-updates
"""

import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

def setup_github_token():
    """Interactive GitHub token setup"""
    
    print("🔑 A3 Document Automation - GitHub Token Setup")
    print("=" * 55)
    
    env_file = Path(".env")
    
    # Check if .env exists and has a token
    current_token = None
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('GITHUB_TOKEN='):
                        current_token = line.split('=', 1)[1].strip()
                        if current_token and current_token != 'your_github_token_here':
                            print(f"✅ GitHub token already configured")
                            print(f"   Token: {current_token[:8]}...{current_token[-4:]}")
                            replace = input("\nReplace existing token? (y/n): ").lower().strip()
                            if replace not in ['y', 'yes']:
                                print("Token setup cancelled.")
                                return True
                        break
        except Exception as e:
            print(f"⚠️  Error reading .env file: {e}")
    
    # Instructions for getting the token
    print("\n📋 How to get your GitHub Personal Access Token:")
    print("   1. Go to: https://github.com/settings/tokens")
    print("   2. Click 'Generate new token (classic)'")
    print("   3. Description: 'A3 Automation Auto-Update Access'")
    print("   4. Expiration: 'No expiration' (or 1 year)")
    print("   5. Select scope: ✅ repo (Full control of private repositories)")
    print("   6. Click 'Generate token'")
    print("   7. Copy the token (starts with 'ghp_')")
    
    # Create GUI for token input
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Get token from user
    token = simpledialog.askstring(
        "GitHub Personal Access Token",
        "Enter your GitHub Personal Access Token:\n\n" +
        "Get it from: https://github.com/settings/tokens\n" +
        "Required permission: repo (private repositories)",
        show='*'  # Hide the token like a password
    )
    
    if not token:
        messagebox.showinfo("Setup Cancelled", "GitHub token setup cancelled.")
        root.destroy()
        return False
    
    # Validate token format
    if not token.startswith('ghp_'):
        result = messagebox.askyesno(
            "Invalid Format", 
            f"GitHub tokens usually start with 'ghp_'.\n" +
            f"Your token starts with '{token[:4]}'.\n\n" +
            f"Continue anyway?"
        )
        if not result:
            root.destroy()
            return False
    
    # Save to .env file
    try:
        # Read existing .env content
        env_content = ""
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # Update or add GitHub token
        lines = env_content.split('\n') if env_content else []
        token_found = False
        
        for i, line in enumerate(lines):
            if line.startswith('GITHUB_TOKEN='):
                lines[i] = f"GITHUB_TOKEN={token}"
                token_found = True
                break
        
        if not token_found:
            # Add token to end of file
            if lines and lines[-1]:  # Add blank line if file doesn't end with one
                lines.append('')
            lines.append(f"GITHUB_TOKEN={token}")
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        messagebox.showinfo(
            "Setup Complete", 
            "✅ GitHub token saved successfully!\n\n" +
            "Auto-update functionality is now enabled.\n" +
            "The launcher will check for updates from your private repository."
        )
        
        print("✅ GitHub token configured successfully")
        print("🔄 Restart the launcher to use auto-updates")
        return True
        
    except Exception as e:
        messagebox.showerror("Setup Failed", f"Could not save GitHub token:\n{str(e)}")
        print(f"❌ Error saving token: {e}")
        return False
    
    finally:
        root.destroy()

if __name__ == "__main__":
    try:
        result = setup_github_token()
        if result:
            print("\n🎉 GitHub token setup complete!")
            print("   Restart the A3 launcher to enable auto-updates.")
        else:
            print("\n❌ GitHub token setup failed.")
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    finally:
        input("\nPress Enter to exit...")