#!/usr/bin/env python3
"""
Script to re-process an existing application with the new comprehensive job description extraction
"""
import sys
from pathlib import Path
from app.services.ai_analyzer import AIAnalyzer
from app.services.document_generator import DocumentGenerator
from app.services.job_processor import JobProcessor
from app.utils.file_utils import read_text_file, write_text_file
from app.models.application import Application

def reprocess_application(application_path: str):
    """Re-process a specific application with new extraction"""
    
    app_path = Path(application_path)
    if not app_path.exists():
        print(f"❌ Application path does not exist: {app_path}")
        return False
    
    print(f"🔄 Re-processing application: {app_path.name}")
    print("=" * 60)
    
    # Initialize services
    ai_analyzer = AIAnalyzer()
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    
    # Check Ollama connection
    print("\n1. Checking Ollama connection...")
    if not ai_analyzer.check_connection():
        print("❌ Ollama is not running!")
        print("Please start Ollama: ollama serve")
        return False
    print("✓ Ollama connected")
    
    # Load application metadata
    metadata_path = app_path / "application.yaml"
    if not metadata_path.exists():
        print(f"❌ Application metadata not found: {metadata_path}")
        return False
    
    # Load the application
    from app.utils.file_utils import load_yaml
    metadata = load_yaml(metadata_path)
    metadata['folder_path'] = str(app_path)
    application = Application.from_dict(metadata)
    
    print(f"✓ Loaded application: {application.company} - {application.job_title}")
    
    # Read the original job description
    job_desc_path = app_path / f"{application.id}.md"
    if not job_desc_path.exists():
        # Try to find any .md file in the directory
        md_files = list(app_path.glob("*.md"))
        if md_files:
            job_desc_path = md_files[0]
        else:
            print(f"❌ Job description file not found in {app_path}")
            return False
    
    print(f"✓ Found job description: {job_desc_path.name}")
    
    # Read the raw job description
    raw_job_description = read_text_file(job_desc_path)
    print(f"✓ Read job description ({len(raw_job_description)} characters)")
    
    # Extract comprehensive job details
    print("\n2. Extracting comprehensive job details...")
    print("   (This may take a minute...)")
    
    try:
        # Clean the job description first
        cleaned_job_description = job_processor._clean_job_description(raw_job_description)
        
        # Extract structured details
        structured_job_description = ai_analyzer.extract_comprehensive_job_details(
            cleaned_job_description,
            raw_job_description
        )
        
        print("✓ Extraction successful!")
        
        # Save the new structured job description
        write_text_file(structured_job_description, job_desc_path)
        print(f"✓ Updated job description file: {job_desc_path.name}")
        
        # Regenerate the summary page
        print("\n3. Regenerating summary page...")
        
        # Load qualifications if they exist
        qualifications_path = app_path / f"{application.job_title.replace(' ', '').replace(',', '')}-Qualifications.md"
        if qualifications_path.exists():
            from app.models.qualification import QualificationAnalysis
            qual_content = read_text_file(qualifications_path)
            # Create a mock QualificationAnalysis object
            qualifications = QualificationAnalysis(
                match_score=85.0,  # Default score
                features_compared=10,
                strong_matches=[],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis=qual_content
            )
        else:
            # Create minimal qualifications
            from app.models.qualification import QualificationAnalysis
            qualifications = QualificationAnalysis(
                match_score=75.0,
                features_compared=5,
                strong_matches=[],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis="No qualifications analysis available"
            )
        
        # Generate new summary
        doc_generator.generate_summary_page(application, qualifications)
        print("✓ Summary page regenerated!")
        
        print("\n" + "=" * 60)
        print("✅ Application re-processed successfully!")
        print("=" * 60)
        print(f"📄 Updated files:")
        print(f"   - {job_desc_path.name}")
        print(f"   - Summary HTML file")
        print("\n🔄 Refresh your browser to see the new structured job description!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during re-processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reprocess_application.py <application_folder_path>")
        print("\nExample:")
        print("  python reprocess_application.py data/applications/Sunny-Life-Director")
        sys.exit(1)
    
    application_path = sys.argv[1]
    success = reprocess_application(application_path)
    sys.exit(0 if success else 1)
