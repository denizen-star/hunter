#!/usr/bin/env python3
"""Archive specific applications and set their status to rejected."""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List

from app.utils.file_utils import get_data_path, ensure_dir_exists, load_yaml, save_yaml


def update_application_status(application_folder: Path, status: str = "rejected") -> bool:
    """Update application status in application.yaml file.
    
    Args:
        application_folder: Path to the application folder
        status: Status to set (default: "rejected")
        
    Returns:
        True if successful, False otherwise
    """
    yaml_path = application_folder / "application.yaml"
    
    if not yaml_path.exists():
        print(f"  ⚠️  No application.yaml found in {application_folder.name}")
        return False
    
    try:
        metadata = load_yaml(yaml_path)
        metadata['status'] = status
        metadata['status_updated_at'] = datetime.now().isoformat()
        
        save_yaml(metadata, yaml_path)
        print(f"  ✅ Updated status to '{status}' for {application_folder.name}")
        return True
    except Exception as e:
        print(f"  ❌ Error updating {application_folder.name}: {e}")
        return False


def archive_application(application_folder: Path, archive_dir: Path) -> bool:
    """Move application folder to archive directory.
    
    Args:
        application_folder: Path to the application folder to archive
        archive_dir: Path to the archive directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        destination = archive_dir / application_folder.name
        
        # Check if destination already exists
        if destination.exists():
            print(f"  ⚠️  {destination.name} already exists in archive. Skipping...")
            return False
        
        shutil.move(str(application_folder), str(destination))
        print(f"  ✅ Archived {application_folder.name}")
        return True
    except Exception as e:
        print(f"  ❌ Error archiving {application_folder.name}: {e}")
        return False


def main():
    """Archive specific applications."""
    applications_dir = get_data_path('applications')
    archive_dir = get_data_path('applications_archived')
    
    # Ensure archive directory exists
    ensure_dir_exists(archive_dir)
    
    # Define the applications to archive by folder name patterns
    applications_to_archive = [
        "Peerspace-Head-of-Data-EngineeringSr-Manager-Data-Engineering",
        "Moodys-Corporation-Data-Engineering-Manager",
        "Block-Financial-Platform-Head-of-Data-Engineering"
    ]
    
    if not applications_dir.exists():
        print(f"❌ Applications directory not found: {applications_dir}")
        return
    
    updated_applications: List[str] = []
    archived_applications: List[str] = []
    errors: List[str] = []
    
    print("=" * 60)
    print("ARCHIVING SPECIFIC APPLICATIONS")
    print("=" * 60)
    print()
    
    # Process each application
    for folder_name in applications_to_archive:
        folder_path = applications_dir / folder_name
        
        if not folder_path.exists():
            print(f"⚠️  Application folder not found: {folder_name}")
            errors.append(f"{folder_name} - folder not found")
            continue
        
        if not folder_path.is_dir():
            print(f"⚠️  Not a directory: {folder_name}")
            errors.append(f"{folder_name} - not a directory")
            continue
        
        print(f"Processing: {folder_name}")
        
        # Update status to rejected
        if update_application_status(folder_path, "rejected"):
            updated_applications.append(folder_name)
        else:
            errors.append(f"{folder_name} - failed to update status")
            continue
        
        # Archive the application
        if archive_application(folder_path, archive_dir):
            archived_applications.append(folder_name)
        else:
            errors.append(f"{folder_name} - failed to archive")
    
    # Print summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Applications updated: {len(updated_applications)}")
    print(f"Applications archived: {len(archived_applications)}")
    print(f"Errors encountered: {len(errors)}")
    
    if updated_applications:
        print("\n✅ Updated applications:")
        for app in updated_applications:
            print(f"   - {app}")
    
    if archived_applications:
        print("\n✅ Archived applications:")
        for app in archived_applications:
            print(f"   - {app}")
    
    if errors:
        print("\n❌ Errors:")
        for error in errors:
            print(f"   - {error}")
    
    print(f"\nArchive location: {archive_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
