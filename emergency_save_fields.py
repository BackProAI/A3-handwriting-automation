#!/usr/bin/env python3
"""
Emergency Field Save Tool
Quick way to save field positions if the GUI tool has issues
"""

import json
from pathlib import Path

def emergency_save():
    """Emergency save - manually enter your field data here if needed."""
    
    # If you have field data from the GUI tool that you don't want to lose,
    # you can manually enter it here in this format:
    
    emergency_fields = {
        "page_1": [
            # Example field - replace with your actual field data
            # {
            #     "name": "field_name_here",
            #     "rect": [x1, y1, x2, y2],  # coordinates from your GUI tool
            #     "type": "text",
            #     "multiline": True,
            #     "fontsize": 10
            # }
        ],
        "page_2": [
            # Add your page 2 fields here
        ]
    }
    
    # If you have no fields to enter manually, this will create a backup of any existing config
    config_path = Path("custom_field_positions.json")
    backup_path = Path("custom_field_positions_backup.json")
    
    try:
        if config_path.exists():
            # Backup existing config
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            
            with open(backup_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            
            print(f"✅ Backed up existing configuration to: {backup_path}")
        
        # Save emergency fields (or create new file)  
        if emergency_fields["page_1"] or emergency_fields["page_2"]:
            with open(config_path, 'w') as f:
                json.dump(emergency_fields, f, indent=2)
            print(f"✅ Saved emergency field configuration to: {config_path}")
        else:
            print("📝 No emergency fields defined in this script.")
            print("   Edit this script to add your field data if needed.")
        
        print(f"\n📋 Field Configuration Location:")
        print(f"   Primary: {config_path.absolute()}")
        if backup_path.exists():
            print(f"   Backup:  {backup_path.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during emergency save: {e}")
        return False

if __name__ == "__main__":
    print("🚨 Emergency Field Configuration Save")
    print("=" * 40)
    emergency_save()