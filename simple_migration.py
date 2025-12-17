#!/usr/bin/env python3
"""
Simple migration script to add the new file path fields to existing application.yaml files.
This ensures all applications have the new fields for hiring_manager_intros_path and recruiter_intros_path.
"""

import os
from pathlib import Path
import sys

# Add the app directory to the Python path
sys.path.append('')

from app.utils.file_utils import load_yaml, save_yaml

def update_application_yaml(folder_path):
    """Update application.yaml with new file path fields"""
    try:
        yaml_path = folder_path / "application.yaml"
        if not yaml_path.exists():
            print(f"⚠️ No application.yaml found in {folder_path}")
            return False
        
        print(f"  🔄 Updating {folder_path.name}/application.yaml...")
        
        # Load existing data
        data = load_yaml(yaml_path)
        
        # Add new fields if they don't exist
        updated = False
        
        if 'hiring_manager_intros_path' not in data:
            data['hiring_manager_intros_path'] = None
            updated = True
        
        if 'recruiter_intros_path' not in data:
            data['recruiter_intros_path'] = None
            updated = True
        
        # Write updated YAML if changes were made
        if updated:
            save_yaml(data, yaml_path)
            print(f"  ✅ Updated application.yaml")
            return True
        else:
            print(f"  ℹ️ No updates needed")
            return True
        
    except Exception as e:
        print(f"❌ Error updating {folder_path.name}: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting simple migration to add new file path fields...")
    
    # Get all application folders
    applications_dir = Path("data/applications")
    if not applications_dir.exists():
        print(f"❌ Applications directory not found: {applications_dir}")
        return
    
    application_folders = [f for f in applications_dir.iterdir() if f.is_dir()]
    print(f"📁 Found {len(application_folders)} application folders")
    
    # Track migration results
    updated_count = 0
    failed_count = 0
    
    # Update each application
    for folder in application_folders:
        try:
            if update_application_yaml(folder):
                updated_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ Failed to update {folder.name}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\n🎯 Migration Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed updates: {failed_count}")
    print(f"  📊 Total applications: {len(application_folders)}")
    
    if updated_count > 0:
        print(f"\n🎉 Simple migration completed! All applications now have the new file path fields.")
        print(f"📝 Note: To generate the actual intro message files and update HTML summaries,")
        print(f"   you'll need to regenerate each application using the updated Hunter system.")

if __name__ == "__main__":
    main()

