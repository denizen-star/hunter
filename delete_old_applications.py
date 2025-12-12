#!/usr/bin/env python3
"""
Delete all applications created before October 1st, 2025
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil
from app.services.job_processor import JobProcessor

def delete_applications_before_date(cutoff_date_str: str = "2025-10-01"):
    """Delete all applications created before the specified date"""
    
    # Parse cutoff date
    cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d")
    cutoff_date = cutoff_date.replace(tzinfo=timezone(timedelta(hours=-4)))  # EST
    
    print(f"Looking for applications created before {cutoff_date_str}...")
    
    # Initialize job processor
    job_processor = JobProcessor()
    
    # Get all applications
    applications = job_processor.list_all_applications()
    
    # Find applications to delete
    to_delete = []
    for app in applications:
        app_created_at = app.created_at.replace(tzinfo=timezone(timedelta(hours=-4)))
        if app_created_at < cutoff_date:
            to_delete.append(app)
    
    print(f"\nFound {len(to_delete)} applications to delete:")
    print("-" * 80)
    
    for app in to_delete:
        created_str = app.created_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {app.company} - {app.job_title} (created: {created_str})")
    
    print("-" * 80)
    
    if not to_delete:
        print("\nNo applications found before the cutoff date.")
        return
    
    # Confirm deletion
    print(f"\nThis will DELETE {len(to_delete)} application(s) and all their data!")
    response = input("Type 'DELETE' to confirm: ")
    
    if response != "DELETE":
        print("Deletion cancelled.")
        return
    
    # Delete applications
    deleted_count = 0
    failed_count = 0
    
    print("\nDeleting applications...")
    for app in to_delete:
        try:
            if app.folder_path and app.folder_path.exists():
                shutil.rmtree(app.folder_path)
                print(f"  ✓ Deleted: {app.company} - {app.job_title}")
                deleted_count += 1
            else:
                print(f"  ⚠ Folder not found: {app.company} - {app.job_title}")
                failed_count += 1
        except Exception as e:
            print(f"  ✗ Error deleting {app.company}: {e}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print(f"Deletion complete!")
    print(f"  Successfully deleted: {deleted_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 80)

if __name__ == "__main__":
    delete_applications_before_date("2025-10-01")
