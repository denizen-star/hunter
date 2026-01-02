#!/usr/bin/env python3
"""
Regenerate qualifications analysis for National Audubon Society application
with updated Job Engine V2 and critical requirements logic
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.services.resume_manager import ResumeManager

def reprocess_audubon_qualifications():
    """Regenerate qualifications analysis for Audubon application"""
    from app.utils.message_logger import log_message
    log_message(89, "🔄 Regenerating qualifications for National Audubon Society application...")
    print("=" * 80)
    
    # Initialize services
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    resume_manager = ResumeManager()
    
    # Find the Audubon application
    applications = job_processor.list_all_applications()
    audubon_app = None
    
    for app in applications:
        if "Audubon" in app.company and "Data Strategy" in app.job_title:
            audubon_app = app
            break
    
    if not audubon_app:
        print("❌ National Audubon Society application not found!")
        return False
    
    from app.utils.message_logger import log_message
    log_message(90, f"✓ Found application: {audubon_app.company} - {audubon_app.job_title}")
    print(f"  Folder: {audubon_app.folder_path}")
    
    # Load job description and resume
    if not audubon_app.job_description_path or not audubon_app.job_description_path.exists():
        print("❌ Job description file not found!")
        return False
    
    job_description = read_text_file(audubon_app.job_description_path)
    resume = resume_manager.get_resume_for_job(audubon_app)
    
    log_message(91, f"✓ Loaded job description ({len(job_description)} characters)")
    log_message(92, f"✓ Loaded resume ({len(resume.content)} characters)")
    
    # Regenerate qualifications analysis
    log_message(93, "\n📊 Regenerating qualifications analysis with Job Engine V2...")
    print("   (This will use the updated matching logic with critical requirements checking)")
    
    try:
        qualifications = doc_generator.generate_qualifications(
            audubon_app,
            job_description,
            resume.content
        )
        
        print(f"\n✅ Qualifications regenerated successfully!")
        print(f"   Match Score: {qualifications.match_score}%")
        print(f"   Features Compared: {qualifications.features_compared}")
        print(f"   Strong Matches: {len(qualifications.strong_matches)}")
        print(f"   Missing Skills: {len(qualifications.missing_skills)}")
        
        # Regenerate summary page with new qualifications
        from app.utils.message_logger import log_message
        log_message(95, "\n📄 Regenerating summary page...")
        doc_generator.generate_summary_page(audubon_app, qualifications)
        log_message(96, "✅ Summary page regenerated!")
        
        # Update application metadata
        job_processor._save_application_metadata(audubon_app)
        log_message(97, "✅ Application metadata updated!")
        
        print("\n" + "=" * 80)
        print("🎉 Reprocessing complete!")
        print("=" * 80)
        print(f"📁 Application folder: {audubon_app.folder_path}")
        print(f"📊 New Match Score: {qualifications.match_score}%")
        print("\n🔄 Refresh your browser to see the updated match score!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during reprocessing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from app.utils.file_utils import read_text_file
    success = reprocess_audubon_qualifications()
    sys.exit(0 if success else 1)

