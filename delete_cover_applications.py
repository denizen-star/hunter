#!/usr/bin/env python3
"""
Delete all applications with "cover" in company name.
Removes from dashboards and folders in the drive.
"""
import shutil
from pathlib import Path
from typing import List
from app.services.job_processor import JobProcessor
from app.services.dashboard_generator import DashboardGenerator
from app.models.application import Application


def delete_cover_applications() -> None:
    """Delete all applications with 'cover' in company name"""
    print("🔍 Searching for all applications with 'cover' in company name...")
    
    job_processor = JobProcessor()
    dashboard_generator = DashboardGenerator()
    
    # Get all applications
    applications = job_processor.list_all_applications()
    
    # Filter applications with "cover" in company name (case-insensitive)
    cover_apps_to_delete: List[Application] = []
    
    for app in applications:
        company_lower = app.company.lower()
        if "cover" in company_lower:
            cover_apps_to_delete.append(app)
    
    if not cover_apps_to_delete:
        print("✓ No applications with 'cover' in company name found.")
        return
    
    print(f"\n📋 Found {len(cover_apps_to_delete)} application(s) with 'cover' in company name to delete:")
    for app in cover_apps_to_delete:
        print(f"  - {app.company} - {app.job_title} (ID: {app.id})")
        print(f"    Created: {app.created_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"    Folder: {app.folder_path}")
    
    # Show what will be deleted
    print(f"\n⚠️  WARNING: This will permanently delete {len(cover_apps_to_delete)} application(s) and their folders.")
    print("   This includes:")
    print("   - Application folders")
    print("   - All files within those folders")
    print("   - Dashboard entries")
    print("\n🗑️  Proceeding with deletion...")
    
    # Delete application folders
    deleted_count = 0
    failed_count = 0
    
    for app in cover_apps_to_delete:
        if app.folder_path and app.folder_path.exists():
            try:
                print(f"\n🗑️  Deleting: {app.company} - {app.job_title}")
                print(f"   Folder: {app.folder_path}")
                
                # Remove the entire folder and all its contents
                shutil.rmtree(app.folder_path)
                print(f"   ✓ Successfully deleted folder")
                deleted_count += 1
                
            except Exception as e:
                print(f"   ❌ Error deleting {app.folder_path}: {e}")
                failed_count += 1
        else:
            print(f"\n⚠️  Folder not found for: {app.company} - {app.job_title}")
            print(f"   Expected: {app.folder_path}")
            failed_count += 1
    
    # Regenerate dashboard to remove deleted applications
    if deleted_count > 0:
        print(f"\n🔄 Regenerating dashboard...")
        try:
            dashboard_generator.generate_index_page()
            print("   ✓ Dashboard regenerated successfully")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not regenerate dashboard: {e}")
    
    # Summary
    print(f"\n🎯 Deletion Summary:")
    print(f"   ✅ Successfully deleted: {deleted_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📊 Total processed: {len(cover_apps_to_delete)}")
    
    if deleted_count > 0:
        print(f"\n✓ Applications with 'cover' in company name deleted from:")
        print(f"   - Application folders")
        print(f"   - Dashboard")


if __name__ == "__main__":
    delete_cover_applications()







