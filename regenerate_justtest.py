#!/usr/bin/env python3
"""Regenerate JustTest application summary with updated networking view"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.models.qualification import QualificationAnalysis
from app.utils.file_utils import read_text_file

def regenerate_justtest():
    print("Regenerating JustTest application summary...")
    
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    
    # Find the JustTest application
    applications = job_processor.list_all_applications()
    justtest_app = None
    
    for app in applications:
        if "JustTest" in app.company or "JustTest" in str(app.folder_path):
            justtest_app = app
            break
    
    if not justtest_app:
        print("JustTest application not found!")
        return
    
    print(f"Found: {justtest_app.company} - {justtest_app.job_title}")
    
    # Load qualification analysis
    if not justtest_app.qualifications_path or not justtest_app.qualifications_path.exists():
        print("No qualification analysis found!")
        return
    
    qual_content = read_text_file(justtest_app.qualifications_path)
    
    # Parse qualification analysis to get match score
    import re
    match_score = 0.0
    score_match = re.search(r'Match Score:?\s*(\d+)', qual_content, re.IGNORECASE)
    if score_match:
        match_score = float(score_match.group(1))
    
    # Create QualificationAnalysis object
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
    
    # Regenerate summary page
    doc_generator.generate_summary_page(justtest_app, qualifications)
    
    print("✓ JustTest summary regenerated successfully!")
    print(f"  Summary file: {justtest_app.summary_path}")

if __name__ == "__main__":
    regenerate_justtest()
