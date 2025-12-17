#!/usr/bin/env python3
"""Regenerate all application summaries with badge display"""
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
    print("Regenerating All Application Summaries (with Badge Display)")
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
            
            # Use the document generator's internal method to load qualifications
            # This handles both JSON and text file formats
            if not app.qualifications_path or not app.qualifications_path.exists():
                print(f"  ⚠️  Skipping: No qualification analysis found")
                continue
            
            # Load qualifications using the document generator's method
            qualifications = doc_generator._load_qualifications(app)
            
            # Regenerate summary page (this will now include badge display)
            doc_generator.generate_summary_page(app, qualifications)
            
            print(f"  ✓ Successfully regenerated summary with badges")
            success_count += 1
            
        except Exception as e:
            import traceback
            print(f"  ✗ Error: {e}")
            traceback.print_exc()
            error_count += 1
    
    # Regenerate dashboard
    print("\nRegenerating dashboard...")
    dashboard_generator.generate_index_page()
    print("  ✓ Dashboard regenerated")
    
    print()
    print("=" * 80)
    print(f"Summary: {success_count} successful, {error_count} errors")
    print("=" * 80)
    print()
    print("Note: Badge display will only appear for applications that have")
    print("      networking contacts linked by company name match.")


if __name__ == "__main__":
    main()

