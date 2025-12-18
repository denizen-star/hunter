#!/usr/bin/env python3
"""
Fix JustTest application files - rename files and regenerate summary
"""

import sys
from pathlib import Path
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.application import Application
from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.utils.file_utils import load_yaml, save_yaml, read_text_file, write_text_file

def rename_files_in_directory(directory: Path):
    """Rename all files containing 'JustAnswer' to 'JustTest'"""
    renamed_count = 0
    for file_path in directory.rglob("*"):
        if file_path.is_file() and "JustAnswer" in file_path.name:
            new_name = file_path.name.replace("JustAnswer", "JustTest")
            new_path = file_path.parent / new_name
            print(f"  Renaming: {file_path.name} → {new_name}")
            file_path.rename(new_path)
            renamed_count += 1
    return renamed_count

def regenerate_summary(application: Application):
    """Regenerate the summary HTML file"""
    print(f"\n🔄 Regenerating summary HTML for {application.company}...")
    
    try:
        # Load required data
        job_processor = JobProcessor()
        document_generator = DocumentGenerator()
        
        # Load qualifications
        if application.qualifications_path and application.qualifications_path.exists():
            qual_content = read_text_file(application.qualifications_path)
            # Parse qualifications (simplified - we'll use the existing content)
            from app.models.qualification import QualificationAnalysis
            # Create a basic QualificationAnalysis from the content
            # Extract match score if available
            import re
            match_score_match = re.search(r'Match Score:?\s*(\d+(?:\.\d+)?)', qual_content, re.IGNORECASE)
            match_score = float(match_score_match.group(1)) if match_score_match else application.match_score or 0.0
            
            qualifications = QualificationAnalysis(
                match_score=match_score,
                features_compared=0,
                strong_matches=[],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis=qual_content
            )
        else:
            print("  ⚠️ No qualifications file found, using basic analysis")
            from app.models.qualification import QualificationAnalysis
            qualifications = QualificationAnalysis(
                match_score=application.match_score or 0.0,
                features_compared=0,
                strong_matches=[],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis=""
            )
        
        # Load job description
        if application.job_description_path and application.job_description_path.exists():
            job_desc = read_text_file(application.job_description_path)
        else:
            print("  ⚠️ No job description file found")
            job_desc = ""
        
        # Load cover letter
        if application.cover_letter_path and application.cover_letter_path.exists():
            cover_letter = read_text_file(application.cover_letter_path)
        else:
            cover_letter = ""
        
        # Load resume
        from app.services.resume_manager import ResumeManager
        resume_manager = ResumeManager()
        try:
            resume = resume_manager.get_resume_for_job(application)
            resume_content = resume.content
        except:
            print("  ⚠️ Could not load resume, using empty content")
            resume_content = ""
        
        # Job details dict
        job_details = {
            'location': application.location or 'N/A',
            'salary_range': application.salary_range or 'N/A',
            'hiring_manager': application.hiring_manager or 'N/A',
            'posted_date': application.posted_date or 'N/A'
        }
        
        # Generate summary HTML
        summary_html = document_generator._create_summary_html(
            application,
            qualifications,
            job_details,
            job_desc,
            qual_content if application.qualifications_path and application.qualifications_path.exists() else "",
            cover_letter,
            resume_content
        )
        
        # Save summary
        if application.summary_path:
            write_text_file(summary_html, application.summary_path)
            print(f"  ✅ Summary regenerated: {application.summary_path.name}")
        else:
            # Create summary path
            from app.utils.datetime_utils import format_datetime_for_filename
            timestamp = format_datetime_for_filename()
            summary_filename = f"{timestamp}-Summary-{application.company}-{application.job_title.replace(', ', '-').replace(' ', '-')}.html"
            summary_path = application.folder_path / summary_filename
            write_text_file(summary_html, summary_path)
            application.summary_path = summary_path
            print(f"  ✅ Summary created: {summary_path.name}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error regenerating summary: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Fixing JustTest Application Files")
    print("=" * 60)
    
    app_dir = Path("data/applications/JustTest-Senior-Manager-Analytics")
    
    if not app_dir.exists():
        print(f"❌ Application directory not found: {app_dir}")
        return
    
    # Load application
    yaml_path = app_dir / "application.yaml"
    if not yaml_path.exists():
        print(f"❌ application.yaml not found")
        return
    
    metadata = load_yaml(yaml_path)
    metadata['folder_path'] = str(app_dir)
    application = Application.from_dict(metadata)
    
    print(f"\n📁 Application: {application.company} - {application.job_title}")
    print(f"   ID: {application.id}")
    
    # Step 1: Rename files
    print("\n1️⃣ Renaming files...")
    renamed = rename_files_in_directory(app_dir)
    print(f"   ✅ Renamed {renamed} files")
    
    # Step 2: Update application.yaml with new paths
    print("\n2️⃣ Updating application.yaml paths...")
    # Reload to get updated file paths
    for file_path in app_dir.rglob("*"):
        if file_path.is_file():
            filename = file_path.name
            if "JustTest" in filename:
                # Update paths in metadata
                if "raw.txt" in filename and "raw" in filename.lower():
                    application.raw_job_description_path = file_path
                elif filename.endswith(".md") and "raw" not in filename.lower() and "qualifications" not in filename.lower():
                    if "intro" in filename.lower():
                        if "hiring" in filename.lower():
                            application.hiring_manager_intros_path = file_path
                        elif "recruiter" in filename.lower():
                            application.recruiter_intros_path = file_path
                        else:
                            application.cover_letter_path = file_path
                    elif "qualifications" in filename.lower():
                        application.qualifications_path = file_path
                    else:
                        application.job_description_path = file_path
                elif filename.endswith(".html") and "summary" in filename.lower():
                    application.summary_path = file_path
    
    # Save updated metadata
    metadata = application.to_dict()
    save_yaml(metadata, yaml_path)
    print("   ✅ application.yaml updated")
    
    # Step 3: Regenerate summary
    print("\n3️⃣ Regenerating summary HTML...")
    success = regenerate_summary(application)
    
    if success:
        # Update summary_path in metadata again
        metadata = application.to_dict()
        save_yaml(metadata, yaml_path)
        print("   ✅ Summary regeneration complete")
    
    print("\n" + "=" * 60)
    print("✅ JustTest application files fixed!")
    print("=" * 60)
    print(f"\n📄 Summary file: {application.summary_path.name if application.summary_path else 'N/A'}")

if __name__ == "__main__":
    main()

