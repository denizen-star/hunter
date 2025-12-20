#!/usr/bin/env python3
"""
Create test data by copying JustAnswer application and networking contact,
renaming company to "JustTest" for testing purposes.
"""

import shutil
import sys
from pathlib import Path
import re
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.file_utils import read_text_file, write_text_file, load_yaml, save_yaml

def replace_in_file(file_path: Path, old_text: str, new_text: str):
    """Replace text in a file"""
    if not file_path.exists():
        return
    
    content = read_text_file(file_path)
    # Replace all occurrences
    content = content.replace(old_text, new_text)
    write_text_file(content, file_path)

def copy_and_rename_application():
    """Copy JustAnswer application and rename to JustTest"""
    source_dir = Path("data/applications/JustAnswer-Senior-Manager-Analytics")
    dest_dir = Path("data/applications/JustTest-Senior-Manager-Analytics")
    
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return False
    
    if dest_dir.exists():
        print(f"Warning: Destination directory already exists: {dest_dir}")
        response = input("Delete and recreate? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(dest_dir)
        else:
            print("Skipping application copy.")
            return False
    
    print(f"Copying application from {source_dir} to {dest_dir}...")
    shutil.copytree(source_dir, dest_dir)
    
    # Replace "JustAnswer" with "JustTest" in all files
    replacements = [
        ("JustAnswer", "JustTest"),
        ("justanswer", "justtest"),  # lowercase
        ("JUSTANSWER", "JUSTTEST"),  # uppercase
    ]
    
    # Process all files in the directory
    for file_path in dest_dir.rglob("*"):
        if file_path.is_file():
            # Skip binary files (images, etc.)
            try:
                for old, new in replacements:
                    replace_in_file(file_path, old, new)
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
    
    # Update folder_path in application.yaml
    yaml_path = dest_dir / "application.yaml"
    if yaml_path.exists():
        metadata = load_yaml(yaml_path)
        metadata['folder_path'] = str(dest_dir)
        # Update all path fields
        for key in metadata:
            if isinstance(metadata[key], str) and 'JustAnswer' in metadata[key]:
                metadata[key] = metadata[key].replace('JustAnswer', 'JustTest')
        save_yaml(metadata, yaml_path)
    
    print(f"✓ Application copied and renamed successfully!")
    return True

def copy_and_rename_networking_contact():
    """Copy Jason Ballengee networking contact and rename company to JustTest"""
    source_dir = Path("data/networking/Jason-Ballengee-JustAnswer")
    dest_dir = Path("data/networking/Jason-Ballengee-JustTest")
    
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return False
    
    if dest_dir.exists():
        print(f"Warning: Destination directory already exists: {dest_dir}")
        response = input("Delete and recreate? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(dest_dir)
        else:
            print("Skipping networking contact copy.")
            return False
    
    print(f"Copying networking contact from {source_dir} to {dest_dir}...")
    shutil.copytree(source_dir, dest_dir)
    
    # Replace "JustAnswer" with "JustTest" in all files
    replacements = [
        ("JustAnswer", "JustTest"),
        ("justanswer", "justtest"),  # lowercase
        ("JUSTANSWER", "JUSTTEST"),  # uppercase
    ]
    
    # Process all files in the directory
    for file_path in dest_dir.rglob("*"):
        if file_path.is_file():
            # Skip binary files (images, etc.)
            try:
                for old, new in replacements:
                    replace_in_file(file_path, old, new)
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
    
    # Update metadata.yaml
    yaml_path = dest_dir / "metadata.yaml"
    if yaml_path.exists():
        metadata = load_yaml(yaml_path)
        metadata['folder_path'] = str(dest_dir)
        metadata['company_name'] = 'JustTest'
        metadata['id'] = metadata['id'].replace('JustAnswer', 'JustTest')
        # Update all path fields
        for key in metadata:
            if isinstance(metadata[key], str) and 'JustAnswer' in metadata[key]:
                metadata[key] = metadata[key].replace('JustAnswer', 'JustTest')
        save_yaml(metadata, yaml_path)
    
    print(f"✓ Networking contact copied and renamed successfully!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Creating JustTest test data from JustAnswer entries")
    print("=" * 60)
    print()
    
    app_success = copy_and_rename_application()
    print()
    contact_success = copy_and_rename_networking_contact()
    print()
    
    if app_success and contact_success:
        print("=" * 60)
        print("✓ Test data created successfully!")
        print("=" * 60)
        print("\nTest data locations:")
        print("  Application: data/applications/JustTest-Senior-Manager-Analytics/")
        print("  Networking:  data/networking/Jason-Ballengee-JustTest/")
    else:
        print("=" * 60)
        print("⚠ Some operations failed. Please check the output above.")
        print("=" * 60)


