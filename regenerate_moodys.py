#!/usr/bin/env python3
"""Regenerate Moody's Corporation summary with fixed tab functionality"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.models.qualification import QualificationAnalysis
from app.utils.file_utils import read_text_file

def regenerate_moodys():
    print("Regenerating Moody's Corporation summary...")
    
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    
    # Find the Moody's application
    applications = job_processor.list_all_applications()
    moodys_app = None
    
    for app in applications:
        if "Moody" in app.company or "Moodys" in app.company:
            moodys_app = app
            break
    
    if not moodys_app:
        print("Moody's application not found!")
        return
    
    print(f"Found: {moodys_app.company} - {moodys_app.job_title}")
    
    # Load qualification analysis
    if not moodys_app.qualifications_path or not moodys_app.qualifications_path.exists():
        print("No qualification analysis found!")
        return
    
    qual_content = read_text_file(moodys_app.qualifications_path)
    
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
    doc_generator.generate_summary_page(moodys_app, qualifications)
    
    print("✓ Moody's Corporation summary regenerated successfully!")

if __name__ == "__main__":
    regenerate_moodys()









