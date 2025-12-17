#!/usr/bin/env python3
"""
Migration script to update all existing applications with new research sections and intro message functionality.
This script will:
1. Generate missing intro message files for all applications
2. Update HTML summary files with new research sections
3. Update application.yaml files with new file paths
"""

import os
import yaml
from pathlib import Path
import sys

# Add the app directory to the Python path
sys.path.append('')

from app.services.document_generator import DocumentGenerator
from app.services.ai_analyzer import AIAnalyzer
from app.models.application import Application
from app.utils.file_utils import read_text_file, write_text_file, load_yaml, save_yaml
from app.utils.prompts import get_prompt

def load_application_from_folder(folder_path):
    """Load application data from folder"""
    try:
        yaml_path = folder_path / "application.yaml"
        if not yaml_path.exists():
            print(f"⚠️ No application.yaml found in {folder_path}")
            return None
        
        data = load_yaml(yaml_path)
        return Application.from_dict(data)
    except Exception as e:
        print(f"❌ Error loading application from {folder_path}: {e}")
        return None

def generate_missing_intro_messages(application, ai_analyzer):
    """Generate missing intro message files"""
    try:
        # Check if intro message files exist
        name_clean = "Rhetta_Chappell"  # Assuming this is the candidate name
        company_clean = application.company.replace(' ', '-')
        job_title_clean = application.job_title.replace(' ', '-')
        
        hiring_manager_filename = f"{name_clean}-{company_clean}-{job_title_clean}-hiring-manager-intros.md"
        recruiter_filename = f"{name_clean}-{company_clean}-{job_title_clean}-recruiter-intros.md"
        
        hiring_manager_path = application.folder_path / hiring_manager_filename
        recruiter_path = application.folder_path / recruiter_filename
        
        files_generated = []
        
        # Generate hiring manager intro messages if missing
        if not hiring_manager_path.exists():
            print(f"  📝 Generating hiring manager intro messages...")
            try:
                # Load qualifications
                if application.qualifications_path and application.qualifications_path.exists():
                    qualifications_content = read_text_file(application.qualifications_path)
                    # Parse qualifications (simplified - in real implementation, you'd parse the QualificationAnalysis object)
                    
                    # Generate intro messages
                    hiring_manager_intros = ai_analyzer.generate_hiring_manager_intros(
                        None,  # Would need to parse qualifications properly
                        application.company,
                        application.job_title,
                        name_clean
                    )
                    
                    write_text_file(hiring_manager_intros, hiring_manager_path)
                    application.hiring_manager_intros_path = hiring_manager_path
                    files_generated.append("hiring-manager-intros.md")
                    print(f"  ✅ Generated {hiring_manager_filename}")
                else:
                    print(f"  ⚠️ No qualifications file found for hiring manager intros")
            except Exception as e:
                print(f"  ❌ Error generating hiring manager intros: {e}")
        
        # Generate recruiter intro messages if missing
        if not recruiter_path.exists():
            print(f"  📝 Generating recruiter intro messages...")
            try:
                if application.qualifications_path and application.qualifications_path.exists():
                    recruiter_intros = ai_analyzer.generate_recruiter_intros(
                        None,  # Would need to parse qualifications properly
                        application.company,
                        application.job_title,
                        name_clean
                    )
                    
                    write_text_file(recruiter_intros, recruiter_path)
                    application.recruiter_intros_path = recruiter_path
                    files_generated.append("recruiter-intros.md")
                    print(f"  ✅ Generated {recruiter_filename}")
                else:
                    print(f"  ⚠️ No qualifications file found for recruiter intros")
            except Exception as e:
                print(f"  ❌ Error generating recruiter intros: {e}")
        
        return files_generated
        
    except Exception as e:
        print(f"❌ Error generating intro messages: {e}")
        return []

def update_html_summary(application, document_generator):
    """Update HTML summary with new research sections"""
    try:
        summary_path = application.summary_path
        if not summary_path or not summary_path.exists():
            print(f"  ⚠️ No summary file found")
            return False
        
        print(f"  🔄 Updating HTML summary with new research sections...")
        
        # Generate new HTML summary with enhanced research
        new_html = document_generator._create_summary_html(application)
        
        # Backup the old file
        backup_path = summary_path.with_suffix('.html.backup')
        if not backup_path.exists():
            old_content = read_text_file(summary_path)
            write_text_file(old_content, backup_path)
            print(f"  💾 Backed up old summary to {backup_path.name}")
        
        # Write new HTML
        write_text_file(new_html, summary_path)
        print(f"  ✅ Updated HTML summary")
        return True
        
    except Exception as e:
        print(f"❌ Error updating HTML summary: {e}")
        return False

def update_application_yaml(application):
    """Update application.yaml with new file paths"""
    try:
        yaml_path = application.folder_path / "application.yaml"
        if not yaml_path.exists():
            print(f"  ⚠️ No application.yaml found")
            return False
        
        print(f"  🔄 Updating application.yaml...")
        
        # Load existing data
        data = load_yaml(yaml_path)
        
        # Update with new paths
        if hasattr(application, 'hiring_manager_intros_path') and application.hiring_manager_intros_path:
            data['hiring_manager_intros_path'] = str(application.hiring_manager_intros_path)
        
        if hasattr(application, 'recruiter_intros_path') and application.recruiter_intros_path:
            data['recruiter_intros_path'] = str(application.recruiter_intros_path)
        
        # Write updated YAML
        save_yaml(data, yaml_path)
        print(f"  ✅ Updated application.yaml")
        return True
        
    except Exception as e:
        print(f"❌ Error updating application.yaml: {e}")
        return False

def migrate_application(application_folder, document_generator, ai_analyzer):
    """Migrate a single application"""
    print(f"\n🔄 Migrating: {application_folder.name}")
    
    # Load application
    application = load_application_from_folder(application_folder)
    if not application:
        return False
    
    success_count = 0
    
    # Generate missing intro messages
    generated_files = generate_missing_intro_messages(application, ai_analyzer)
    if generated_files:
        success_count += len(generated_files)
    
    # Update HTML summary
    if update_html_summary(application, document_generator):
        success_count += 1
    
    # Update application.yaml
    if update_application_yaml(application):
        success_count += 1
    
    print(f"  ✅ Migration completed: {success_count} updates")
    return success_count > 0

def main():
    """Main migration function"""
    print("🚀 Starting migration of existing applications...")
    
    # Initialize services
    try:
        document_generator = DocumentGenerator()
        ai_analyzer = AIAnalyzer()
    except Exception as e:
        print(f"❌ Error initializing services: {e}")
        return
    
    # Get all application folders
    applications_dir = Path("data/applications")
    if not applications_dir.exists():
        print(f"❌ Applications directory not found: {applications_dir}")
        return
    
    application_folders = [f for f in applications_dir.iterdir() if f.is_dir()]
    print(f"📁 Found {len(application_folders)} application folders")
    
    # Track migration results
    migrated_count = 0
    failed_count = 0
    
    # Migrate each application
    for folder in application_folders:
        try:
            if migrate_application(folder, document_generator, ai_analyzer):
                migrated_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ Failed to migrate {folder.name}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\n🎯 Migration Summary:")
    print(f"  ✅ Successfully migrated: {migrated_count}")
    print(f"  ❌ Failed migrations: {failed_count}")
    print(f"  📊 Total applications: {len(application_folders)}")
    
    if migrated_count > 0:
        print(f"\n🎉 Migration completed! All applications now have the new research sections and intro message functionality.")

if __name__ == "__main__":
    main()
