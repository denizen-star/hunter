#!/usr/bin/env python3
"""Archive rejected applications to test dashboard performance improvement.

This script moves all application folders with 'rejected' status from
data/applications/ to data/applications_archived/ to reduce the number
of applications the dashboard needs to process on each load.
"""

import shutil
from pathlib import Path
from typing import List

from app.utils.file_utils import get_data_path, ensure_dir_exists, load_yaml


def is_rejected_application(application_folder: Path) -> bool:
    """Check if an application folder has rejected status.
    
    Args:
        application_folder: Path to the application folder
        
    Returns:
        True if the application has rejected status, False otherwise
    """
    yaml_path = application_folder / "application.yaml"
    
    if not yaml_path.exists():
        return False
    
    try:
        metadata = load_yaml(yaml_path)
        status = metadata.get('status', '').strip().lower()
        return status == 'rejected'
    except Exception as e:
        print(f"Error reading {yaml_path}: {e}")
        return False


def archive_rejected_applications() -> None:
    """Move all rejected applications to archive directory."""
    applications_dir = get_data_path('applications')
    archive_dir = get_data_path('applications_archived')
    
    # Create archive directory if it doesn't exist
    ensure_dir_exists(archive_dir)
    
    if not applications_dir.exists():
        print(f"Applications directory not found: {applications_dir}")
        return
    
    moved_applications: List[str] = []
    errors: List[str] = []
    
    # Iterate through all folders in applications directory
    for folder_path in applications_dir.iterdir():
        if not folder_path.is_dir():
            continue
        
        # Skip hidden files/directories
        if folder_path.name.startswith('.'):
            continue
        
        # Check if this application is rejected
        if is_rejected_application(folder_path):
            try:
                # Move the entire folder to archive
                destination = archive_dir / folder_path.name
                
                # Check if destination already exists
                if destination.exists():
                    print(f"Warning: {destination} already exists. Skipping {folder_path.name}")
                    errors.append(f"{folder_path.name} - destination already exists")
                    continue
                
                shutil.move(str(folder_path), str(destination))
                moved_applications.append(folder_path.name)
                print(f"Moved: {folder_path.name}")
                
            except Exception as e:
                error_msg = f"{folder_path.name} - {str(e)}"
                print(f"Error moving {folder_path.name}: {e}")
                errors.append(error_msg)
    
    # Print summary
    print("\n" + "="*60)
    print("ARCHIVE SUMMARY")
    print("="*60)
    print(f"Total applications moved: {len(moved_applications)}")
    print(f"Errors encountered: {len(errors)}")
    
    if moved_applications:
        print("\nMoved applications:")
        for app in sorted(moved_applications):
            print(f"  - {app}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    print(f"\nArchive location: {archive_dir}")
    print("="*60)


if __name__ == "__main__":
    archive_rejected_applications()
