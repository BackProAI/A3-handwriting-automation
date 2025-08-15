#!/usr/bin/env python3
"""
A3 Document Automation - Main Launcher with Auto-Update
Checks for updates from GitHub and launches the main application
"""

import os
import sys
import json
import requests
import zipfile
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import shutil
from datetime import datetime, timedelta
import threading
import time

class A3Launcher:
    def __init__(self):
        self.app_name = "A3 Document Automation"
        self.github_repo = "BackProAI/A3-handwriting-automation"  # UPDATE THIS with your actual repo
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.current_version = self.get_local_version()
        self.app_dir = Path(__file__).parent
        self.temp_dir = self.app_dir / "temp_update"
        
        # GitHub authentication
        self.github_token = self.get_github_token()
        
        # Create GUI
        self.setup_gui()
        
    def get_local_version(self):
        """Get current local version from version.txt"""
        version_file = Path(__file__).parent / "version.txt"
        if version_file.exists():
            try:
                # Try UTF-8 first, then fallback to other encodings
                for encoding in ['utf-8', 'utf-8-sig', 'latin-1']:
                    try:
                        return version_file.read_text(encoding=encoding).strip()
                    except UnicodeDecodeError:
                        continue
                # If all encodings fail, return default
                return "1.0.0"
            except Exception:
                return "1.0.0"
        return "1.0.0"  # Default version
    
    def get_github_token(self):
        """Get GitHub Personal Access Token for API authentication"""
        # Try to get token from .env file first
        env_file = self.app_dir / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('GITHUB_TOKEN='):
                            token = line.split('=', 1)[1].strip()
                            if token:
                                return token
            except Exception as e:
                print(f"Error reading GitHub token from .env: {e}")
        
        # Try environment variable
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            return token
        
        # If no token found, prompt user to add it
        return None
    
    def get_auth_headers(self):
        """Get authentication headers for GitHub API"""
        if self.github_token:
            return {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        return {'Accept': 'application/vnd.github.v3+json'}
    
    def setup_gui(self):
        """Create the launcher GUI"""
        self.root = tk.Tk()
        self.root.title(f"{self.app_name} - Launcher")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text=self.app_name, font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Version info
        version_label = ttk.Label(main_frame, text=f"Current Version: {self.current_version}")
        version_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to launch", foreground="green")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Progress bar (hidden initially)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        self.progress.grid_remove()  # Hide initially
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Check for updates button
        if self.github_token:
            self.update_btn = ttk.Button(button_frame, text="Check for Updates", command=self.check_updates_threaded)
        else:
            self.update_btn = ttk.Button(button_frame, text="Updates: No Token", state='disabled')
        self.update_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Launch button
        self.launch_btn = ttk.Button(button_frame, text="Launch A3 Automation", command=self.launch_app)
        self.launch_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Auto-update checkbox
        self.auto_update_var = tk.BooleanVar(value=bool(self.github_token))
        if self.github_token:
            auto_update_text = "Auto-check for updates on startup"
            checkbox_state = 'normal'
        else:
            auto_update_text = "Auto-updates require GitHub token"
            checkbox_state = 'disabled'
        
        auto_update_cb = ttk.Checkbutton(main_frame, text=auto_update_text, 
                                        variable=self.auto_update_var, state=checkbox_state)
        auto_update_cb.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
        
    def show_progress(self, show=True):
        """Show/hide progress bar"""
        if show:
            self.progress.grid()
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.grid_remove()
        self.root.update()
        
    def check_updates_threaded(self):
        """Check for updates in a separate thread"""
        self.update_btn.config(state='disabled')
        self.launch_btn.config(state='disabled')
        
        thread = threading.Thread(target=self.check_for_updates)
        thread.daemon = True
        thread.start()
        
    def check_for_updates(self):
        """Check GitHub for latest release"""
        try:
            self.update_status("Checking for updates...", "blue")
            self.show_progress(True)
            
            # Get authentication headers
            headers = self.get_auth_headers()
            
            # Get latest release info from GitHub with authentication
            response = requests.get(self.github_api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')
            
            if self.is_newer_version(latest_version, self.current_version):
                self.show_progress(False)
                self.update_status(f"Update available: v{latest_version}", "orange")
                
                # Ask user if they want to update
                result = messagebox.askyesno(
                    "Update Available", 
                    f"A new version is available!\n\n"
                    f"Current: v{self.current_version}\n"
                    f"Latest: v{latest_version}\n\n"
                    f"Would you like to download and install the update?"
                )
                
                if result:
                    self.download_and_install_update(release_data)
                else:
                    self.update_status("Update skipped", "orange")
            else:
                self.update_status("You have the latest version!", "green")
                self.show_progress(False)
                
        except requests.RequestException as e:
            self.show_progress(False)
            self.update_status("Failed to check for updates", "red")
            messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{str(e)}")
        except Exception as e:
            self.show_progress(False)
            self.update_status("Update check error", "red")
            messagebox.showerror("Error", f"Unexpected error during update check:\n{str(e)}")
        finally:
            self.update_btn.config(state='normal')
            self.launch_btn.config(state='normal')
            
    def is_newer_version(self, version1, version2):
        """Compare version strings (robust comparison)"""
        def version_tuple(v):
            try:
                # Clean version string and split
                clean_v = ''.join(c for c in str(v) if c.isdigit() or c == '.')
                parts = clean_v.split('.')
                # Convert to integers, pad with zeros if needed
                return tuple(int(part) if part.isdigit() else 0 for part in parts[:3])
            except (ValueError, TypeError):
                # If parsing fails, return a default tuple
                return (0, 0, 0)
        
        try:
            return version_tuple(version1) > version_tuple(version2)
        except Exception:
            # If comparison fails, assume no update needed
            return False
    
    def download_and_install_update(self, release_data):
        """Download and install the update"""
        try:
            self.update_status("Downloading update...", "blue")
            self.show_progress(True)
            
            # Find the source code download URL
            download_url = release_data['zipball_url']
            
            # Create temp directory
            self.temp_dir.mkdir(exist_ok=True)
            
            # Download the update with authentication
            headers = self.get_auth_headers()
            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()
            
            zip_path = self.temp_dir / "update.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.update_status("Installing update...", "blue")
            
            # Extract the update
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Find the extracted folder (GitHub creates a folder with repo name)
            extracted_folders = [d for d in self.temp_dir.iterdir() if d.is_dir()]
            if extracted_folders:
                source_dir = extracted_folders[0]
                
                # Copy files (skip launcher itself and problematic folders to avoid conflicts)
                skip_items = {"main_launcher.py", ".github", ".git", "__pycache__", ".pytest_cache"}
                for item in source_dir.iterdir():
                    if item.name not in skip_items:
                        dest = self.app_dir / item.name
                        try:
                            if item.is_file():
                                shutil.copy2(item, dest)
                            elif item.is_dir():
                                if dest.exists():
                                    shutil.rmtree(dest)
                                shutil.copytree(item, dest)
                        except PermissionError as e:
                            print(f"Skipping {item.name} due to permission error: {e}")
                            continue  # Skip this item and continue with others
                
                # Update version file
                new_version = release_data['tag_name'].lstrip('v')
                version_file = self.app_dir / "version.txt"
                version_file.write_text(new_version)
                
                self.current_version = new_version
                
                # Clean up
                shutil.rmtree(self.temp_dir)
                
                self.show_progress(False)
                self.update_status(f"Updated to v{new_version}!", "green")
                
                messagebox.showinfo("Update Complete", 
                                  f"Successfully updated to v{new_version}!\n\n"
                                  f"The application will now restart.")
                
                # Restart the launcher
                self.restart_launcher()
            else:
                raise Exception("Could not find extracted update files")
                
        except Exception as e:
            self.show_progress(False)
            self.update_status("Update failed", "red")
            messagebox.showerror("Update Failed", f"Failed to install update:\n{str(e)}")
            
            # Clean up on failure
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
    
    def restart_launcher(self):
        """Restart the launcher"""
        self.root.quit()
        os.execv(sys.executable, ['python'] + sys.argv)
    
    def _ensure_configurations_updated(self):
        """Ensure both JSON configurations and PDF template are up-to-date."""
        try:
            self.update_status("Checking configuration files...", "blue")
            
            # Check paths
            section_config_path = self.app_dir / "A3_templates" / "a3_section_config.json"
            field_config_path = self.app_dir / "A3_templates" / "custom_field_position.json"
            template_path = self.app_dir / "processed_documents" / "A3_Custom_Template.pdf"
            
            # Check if configurations exist
            if not section_config_path.exists():
                self.update_status("Warning: Section configuration missing", "orange")
                messagebox.showwarning(
                    "Configuration Missing",
                    "Section configuration not found!\n\n"
                    "You'll need to create sections using 'Define Sections' tool first."
                )
                return
            
            if not field_config_path.exists():
                self.update_status("Warning: Field configuration missing", "orange")
                messagebox.showwarning(
                    "Configuration Missing", 
                    "Field position configuration not found!\n\n"
                    "Default field positions will be used."
                )
                return
            
            # Check if template needs updating
            field_modified = field_config_path.stat().st_mtime
            template_exists = template_path.exists()
            
            should_regenerate = False
            
            if not template_exists:
                should_regenerate = True
                reason = "Template PDF not found"
            else:
                template_modified = template_path.stat().st_mtime
                if field_modified > template_modified:
                    should_regenerate = True
                    reason = "Field configuration updated"
            
            if should_regenerate:
                self.update_status(f"Updating template ({reason})...", "blue")
                self._regenerate_template_launcher()
            
            self.update_status("Configuration check complete", "green")
            
        except Exception as e:
            print(f"Warning: Failed to check configurations: {e}")
            self.update_status("Configuration check failed", "orange")
    
    def _regenerate_template_launcher(self):
        """Regenerate the PDF template from the launcher."""
        try:
            # Import and call the template creation function
            import sys
            import importlib.util
            
            # Load create_custom_template module
            spec = importlib.util.spec_from_file_location(
                "create_custom_template", 
                self.app_dir / "create_custom_template.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Call the template creation function
            success = module.create_custom_template()
            
            if success:
                print("✅ PDF template successfully updated!")
            else:
                print("⚠️ Failed to regenerate PDF template")
                messagebox.showwarning(
                    "Template Update Failed",
                    "Could not update PDF template.\n\n"
                    "The application will use the existing template."
                )
                
        except Exception as e:
            print(f"⚠️ Error regenerating template: {e}")
            messagebox.showwarning(
                "Template Update Error", 
                f"Error updating PDF template:\n{str(e)}\n\n"
                f"The application will use the existing template."
            )
    
    def launch_app(self):
        """Launch the main A3 application"""
        try:
            self.update_status("Launching A3 Automation...", "blue")
            
            # Check if main app exists
            main_app = self.app_dir / "a3_sectioned_automation.py"
            if not main_app.exists():
                messagebox.showerror("App Not Found", 
                                   "Main application file not found!\n\n"
                                   "Please check for updates or reinstall the application.")
                return
            
            # Ensure JSON configurations are updated before launching
            self._ensure_configurations_updated()
            
            # Launch the main application
            subprocess.Popen([sys.executable, str(main_app)], 
                           cwd=str(self.app_dir))
            
            # Close launcher
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror("Launch Failed", f"Failed to launch application:\n{str(e)}")
            self.update_status("Launch failed", "red")
    
    def run(self):
        """Run the launcher"""
        # Auto-check for updates on startup if enabled and token available
        if self.github_token and self.auto_update_var.get():
            self.root.after(1000, self.check_updates_threaded)  # Check after 1 second
        
        self.root.mainloop()

if __name__ == "__main__":
    launcher = A3Launcher()
    launcher.run()