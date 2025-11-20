#!/usr/bin/env python3
"""
Delete intro message files for Valon application to allow regeneration with updated prompts.
"""
from pathlib import Path
from app.services.job_processor import JobProcessor
from app.utils.file_utils import read_text_file

def regenerate_valon_intros():
    """Delete intro message files for Valon application"""
    print("🔍 Searching for Valon application...")
    
    job_processor = JobProcessor()
    
    # Get all applications
    applications = job_processor.list_all_applications()
    
    # Find Valon application
    valon_app = None
    for app in applications:
        if app.company.lower() == "valon":
            valon_app = app
            break
    
    if not valon_app:
        print("❌ Valon application not found.")
        return
    
    print(f"\n📋 Found Valon application:")
    print(f"  - Company: {valon_app.company}")
    print(f"  - Job Title: {valon_app.job_title}")
    print(f"  - ID: {valon_app.id}")
    print(f"  - Folder: {valon_app.folder_path}")
    
    # Delete intro message files
    deleted = []
    
    if valon_app.hiring_manager_intros_path and valon_app.hiring_manager_intros_path.exists():
        valon_app.hiring_manager_intros_path.unlink()
        deleted.append("hiring-manager-intros.md")
        print(f"  ✓ Deleted: {valon_app.hiring_manager_intros_path.name}")
    
    if valon_app.recruiter_intros_path and valon_app.recruiter_intros_path.exists():
        valon_app.recruiter_intros_path.unlink()
        deleted.append("recruiter-intros.md")
        print(f"  ✓ Deleted: {valon_app.recruiter_intros_path.name}")
    
    # Clear the paths in the application object
    valon_app.hiring_manager_intros_path = None
    valon_app.recruiter_intros_path = None
    
    # Save updated metadata
    job_processor._save_application_metadata(valon_app)
    
    if deleted:
        print(f"\n✅ Successfully deleted {len(deleted)} intro message file(s).")
        print("   The generate buttons should now appear on the Valon application page.")
        print("   Click them to regenerate with the updated prompts.")
    else:
        print("\n⚠️  No intro message files found to delete.")
        print("   The generate buttons should already be visible.")

if __name__ == "__main__":
    regenerate_valon_intros()

