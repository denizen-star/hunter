#!/usr/bin/env python3
"""Regenerate all application summaries with updated technology matching"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.services.dashboard_generator import DashboardGenerator


def main():
    print("=" * 80)
    print("Regenerating All Application Summaries")
    print("=" * 80)
    print()
    
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    dashboard_generator = DashboardGenerator()
    
    # Get all applications
    applications = job_processor.list_all_applications()
    
    if not applications:
        print("No applications found.")
        return
    
    print(f"Found {len(applications)} applications to regenerate.\n")
    
    success_count = 0
    error_count = 0
    
    for i, app in enumerate(applications, 1):
        try:
            print(f"[{i}/{len(applications)}] Processing: {app.company} - {app.job_title}")
            
            # Load qualification analysis
            from app.models.qualification import QualificationAnalysis
            from app.utils.file_utils import read_text_file
            
            if not app.qualifications_path or not app.qualifications_path.exists():
                print(f"  ⚠️  Skipping: No qualification analysis found")
                continue
            
            qual_content = read_text_file(app.qualifications_path)
            
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
            doc_generator.generate_summary_page(app, qualifications)
            
            print(f"  ✓ Successfully regenerated summary")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1
    
    # Regenerate dashboard
    print("\nRegenerating dashboard...")
    dashboard_generator.generate_index_page()
    print("  ✓ Dashboard regenerated")
    
    print()
    print("=" * 80)
    print(f"Summary: {success_count} successful, {error_count} errors")
    print("=" * 80)


if __name__ == "__main__":
    main()

