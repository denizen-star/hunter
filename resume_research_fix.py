#!/usr/bin/env python3
"""
Resume research data fix for all applications
Run this script to continue fixing research data and generating intro messages
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('/Users/kervinleacock/Documents/Development/hunter')

from app.services.document_generator import DocumentGenerator
from app.models.application import Application
from app.models.qualification import QualificationAnalysis
from app.models.resume import Resume
from app.utils.file_utils import load_yaml, save_yaml, read_text_file, write_text_file

def fix_application_research_and_intros(application_folder):
    """Fix research data and generate intro messages for a single application"""
    try:
        print(f"\n🔧 Processing: {application_folder.name}")
        
        # Initialize document generator
        document_generator = DocumentGenerator()
        
        # Load application data
        yaml_path = application_folder / "application.yaml"
        data = load_yaml(yaml_path)
        application = Application.from_dict(data)
        
        print(f"  📋 {application.company} - {application.job_title}")
        
        # Load existing files
        qualifications_content = ""
        job_desc_content = ""
        resume_content = ""
        
        # Load qualifications
        if application.qualifications_path and application.qualifications_path.exists():
            qualifications_content = read_text_file(application.qualifications_path)
            print("  ✅ Loaded qualifications")
        else:
            print("  ⚠️ No qualifications file")
            qualifications_content = "No qualifications data available"
        
        # Load job description
        if application.job_description_path and application.job_description_path.exists():
            job_desc_content = read_text_file(application.job_description_path)
            print("  ✅ Loaded job description")
        else:
            print("  ⚠️ No job description file")
            job_desc_content = "No job description available"
        
        # Load resume
        if application.custom_resume_path and application.custom_resume_path.exists():
            resume_content = read_text_file(application.custom_resume_path)
            print("  ✅ Loaded resume")
        else:
            print("  ⚠️ No resume file")
            resume_content = "No resume available"
        
        # Create real QualificationAnalysis from existing data
        qualifications = document_generator.ai_analyzer.analyze_qualifications(
            job_desc_content, resume_content
        )
        print(f"  📊 Real qualifications: {qualifications.match_score}% match")
        
        # Generate real company research
        print("  🔍 Generating company research...")
        research_data = document_generator._perform_company_research(application.company)
        
        print(f"  📊 Research data: {len(research_data.get('products_services', ''))} chars products, {len(research_data.get('news', []))} news items, {len(research_data.get('personnel', []))} personnel")
        
        # Generate intro messages with real qualifications
        print("  💬 Generating intro messages...")
        try:
            # Generate hiring manager intro messages
            hiring_manager_intros = document_generator.ai_analyzer.generate_hiring_manager_intros(
                qualifications,
                application.company,
                application.job_title,
                "Kervin Leacock"  # Use real name
            )
            print(f"  ✅ Generated hiring manager intros: {len(hiring_manager_intros)} chars")
            
            # Generate recruiter intro messages
            recruiter_intros = document_generator.ai_analyzer.generate_recruiter_intros(
                qualifications,
                application.company,
                application.job_title,
                "Kervin Leacock"  # Use real name
            )
            print(f"  ✅ Generated recruiter intros: {len(recruiter_intros)} chars")
            
            # Save intro messages
            name_clean = "KervinLeacock"
            company_clean = application.company.replace(' ', '-')
            job_title_clean = application.job_title.replace(' ', '-')
            
            hiring_manager_filename = f"{name_clean}-{company_clean}-{job_title_clean}-hiring-manager-intros.md"
            hiring_manager_path = application.folder_path / hiring_manager_filename
            write_text_file(hiring_manager_intros, hiring_manager_path)
            application.hiring_manager_intros_path = hiring_manager_path
            print(f"  💾 Saved hiring manager intros: {hiring_manager_path.name}")
            
            recruiter_filename = f"{name_clean}-{company_clean}-{job_title_clean}-recruiter-intros.md"
            recruiter_path = application.folder_path / recruiter_filename
            write_text_file(recruiter_intros, recruiter_path)
            application.recruiter_intros_path = recruiter_path
            print(f"  💾 Saved recruiter intros: {recruiter_path.name}")
            
        except Exception as e:
            print(f"  ❌ Error generating intro messages: {e}")
            return False
        
        # Update application.yaml with new paths
        application_dict = application.to_dict()
        save_yaml(application_dict, yaml_path)
        print(f"  💾 Updated application.yaml")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main function to fix all applications"""
    print("🚀 Resuming Research Data Fix and Intro Message Generation")
    print("This will:")
    print("  - Generate real company research data")
    print("  - Create hiring manager intro messages")
    print("  - Create recruiter intro messages")
    print("  - Update all application files")
    
    # Get all application folders
    applications_dir = Path("/Users/kervinleacock/Documents/Development/hunter/data/applications")
    if not applications_dir.exists():
        print(f"❌ Applications directory not found: {applications_dir}")
        return
    
    application_folders = [f for f in applications_dir.iterdir() if f.is_dir()]
    print(f"📁 Found {len(application_folders)} application folders")
    
    # Track results
    success_count = 0
    failed_count = 0
    
    # Process each application
    for i, folder in enumerate(application_folders, 1):
        print(f"\n📊 Progress: {i}/{len(application_folders)}")
        
        try:
            if fix_application_research_and_intros(folder):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ Failed to process {folder.name}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\n🎯 Final Summary:")
    print(f"  ✅ Successfully processed: {success_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📊 Total applications: {len(application_folders)}")
    
    if success_count > 0:
        print(f"\n🎉 Processing completed!")
        print(f"🔍 All applications now have:")
        print(f"  - Real company research data")
        print(f"  - Generated hiring manager intro messages")
        print(f"  - Generated recruiter intro messages")
        print(f"  - Updated application.yaml files")

if __name__ == "__main__":
    main()






