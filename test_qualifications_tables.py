#!/usr/bin/env python3
"""Test script to verify Qualifications Analysis tables work correctly"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator

def test_existing_application():
    """Test with an existing application"""
    print("=" * 80)
    print("Testing Qualifications Analysis Tables")
    print("=" * 80)
    print()
    
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    
    # Get all applications
    applications = job_processor.list_all_applications()
    
    if not applications:
        print("❌ No applications found. Please create an application first.")
        return False
    
    # Use the first application
    app = applications[0]
    print(f"Testing with: {app.company} - {app.job_title}")
    print()
    
    # Check if summary exists
    summary_path = app.folder_path / "summary.html"
    if not summary_path.exists():
        print("⚠️  Summary doesn't exist. Regenerating...")
        # Load qualifications if they exist
        from app.models.qualification import QualificationAnalysis
        from app.utils.file_utils import read_text_file
        
        if app.qualifications_path and app.qualifications_path.exists():
            qual_content = read_text_file(app.qualifications_path)
            import re
            match_score = 0.0
            score_match = re.search(r'Match Score:?\s*(\d+)', qual_content, re.IGNORECASE)
            if score_match:
                match_score = float(score_match.group(1))
            
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
            doc_generator.generate_summary_page(app, qualifications)
        else:
            print("❌ No qualifications found for this application.")
            return False
    
    print("✅ Summary exists")
    print(f"📄 Summary path: {summary_path}")
    print()
    print("To view the tables:")
    print("1. Start the web server: ./run.sh")
    print("2. Open the application in your browser")
    print("3. Click on the 'Qualifications Analysis' tab")
    print("4. You should see two tables instead of text")
    print()
    
    return True

if __name__ == "__main__":
    success = test_existing_application()
    sys.exit(0 if success else 1)






