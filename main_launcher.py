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
        
        # Create GUI
        self.setup_gui()
        
    def get_local_version(self):
        """Get current local version from version.txt"""
        version_file = Path(__file__).parent / "version.txt"
        if version_file.exists():
            return version_file.read_text().strip()
        return "1.0.0"  # Default version
    
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
        self.update_btn = ttk.Button(button_frame, text="Check for Updates", command=self.check_updates_threaded)
        self.update_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Launch button
        self.launch_btn = ttk.Button(button_frame, text="Launch A3 Automation", command=self.launch_app)
        self.launch_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Auto-update checkbox
        self.auto_update_var = tk.BooleanVar(value=False)  # Disabled until GitHub release exists
        auto_update_cb = ttk.Checkbutton(main_frame, text="Auto-check for updates on startup", 
                                        variable=self.auto_update_var)
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
            
            # Get latest release info from GitHub
            response = requests.get(self.github_api_url, timeout=10)
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
        """Compare version strings (simple comparison)"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        return version_tuple(version1) > version_tuple(version2)
    
    def download_and_install_update(self, release_data):
        """Download and install the update"""
        try:
            self.update_status("Downloading update...", "blue")
            self.show_progress(True)
            
            # Find the source code download URL
            download_url = release_data['zipball_url']
            
            # Create temp directory
            self.temp_dir.mkdir(exist_ok=True)
            
            # Download the update
            response = requests.get(download_url, stream=True)
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
                
                # Copy files (skip launcher itself to avoid conflicts)
                for item in source_dir.iterdir():
                    if item.name != "main_launcher.py":
                        dest = self.app_dir / item.name
                        if item.is_file():
                            shutil.copy2(item, dest)
                        elif item.is_dir():
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(item, dest)
                
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
        # Auto-check for updates on startup if enabled
        if self.auto_update_var.get():
            self.root.after(1000, self.check_updates_threaded)  # Check after 1 second
        
        self.root.mainloop()

if __name__ == "__main__":
    launcher = A3Launcher()
    launcher.run()