#!/usr/bin/env python3
"""Regenerate application summaries in chunks, only if they need regeneration"""
import sys
import re
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.models.qualification import QualificationAnalysis
from app.utils.file_utils import read_text_file

def needs_regeneration(application) -> bool:
    """Check if application summary needs regeneration based on structure and recency"""
    if not application.summary_path or not application.summary_path.exists():
        return True
    
    try:
        html_content = read_text_file(application.summary_path)
        
        # Check if it has the new networking tab structure
        has_new_structure = 'id="networking-summary-container"' in html_content and \
                           'position: fixed' in html_content and \
                           'left: 180px' in html_content
        
        # Check if it has the old structure (needs migration)
        has_old_structure = 'id="networking-summary-container"' in html_content and \
                           ('height: calc(100vh' in html_content or \
                            'margin-top: 20px' in html_content)
        
        # If it has old structure or doesn't have new structure, needs regeneration
        if has_old_structure or not has_new_structure:
            return True
        
        # Check if it has the updated iframe structure with absolute positioning
        has_new_iframe = 'position: absolute' in html_content and \
                        'top: 0' in html_content and \
                        'left: 0' in html_content
        
        if not has_new_iframe:
            return True
        
        # CRITICAL: Check for the improved iframe creation method that fixes "Loading summary..." issue
        # Old code uses: summaryContent.innerHTML = `<iframe src="...`
        # New code uses: createElement('iframe') and appendChild
        has_loading_fix = 'createElement(\'iframe\')' in html_content or \
                         'appendChild(iframe)' in html_content or \
                         'createElement("iframe")' in html_content
        
        # Also check if it has the problematic pattern that causes "Loading summary..." to show
        has_problematic_pattern = 'summaryContent.innerHTML = `<iframe' in html_content or \
                                  'summaryContent.innerHTML = \'<iframe' in html_content
        
        # If it has the problematic pattern or doesn't have the fix, needs regeneration
        if has_problematic_pattern or not has_loading_fix:
            return True
        
        return False
    except Exception as e:
        print(f"  ⚠️  Error checking {application.company}: {e}")
        return True  # If we can't check, regenerate to be safe

def regenerate_batch(applications, start_idx=0, batch_size=10):
    """Regenerate a batch of applications"""
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    
    end_idx = min(start_idx + batch_size, len(applications))
    batch = applications[start_idx:end_idx]
    
    print(f"\n{'=' * 80}")
    print(f"Processing batch: Applications {start_idx + 1} to {end_idx} of {len(applications)}")
    print(f"{'=' * 80}\n")
    
    success_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, app in enumerate(batch, start_idx + 1):
        try:
            print(f"[{i}/{len(applications)}] Checking: {app.company} - {app.job_title}")
            
            # Check if regeneration is needed
            if not needs_regeneration(app):
                print(f"  ⏭️  Skipping: Already up to date")
                skipped_count += 1
                continue
            
            # Load qualification analysis
            if not app.qualifications_path or not app.qualifications_path.exists():
                print(f"  ⚠️  Skipping: No qualification analysis found")
                skipped_count += 1
                continue
            
            qual_content = read_text_file(app.qualifications_path)
            
            # Parse qualification analysis to get match score
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
    
    print(f"\n{'=' * 80}")
    print(f"Batch Summary:")
    print(f"  ✓ Regenerated: {success_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    print(f"  ✗ Errors: {error_count}")
    print(f"{'=' * 80}\n")
    
    return success_count, skipped_count, error_count

def main():
    print("=" * 80)
    print("Smart Regeneration: Application Summaries (in chunks of 10)")
    print("=" * 80)
    print()
    
    job_processor = JobProcessor()
    all_applications = job_processor.list_all_applications()
    
    if not all_applications:
        print("No applications found.")
        return
    
    # Filter to only active applications (exclude rejected)
    rejected_statuses = ['rejected']
    applications = [app for app in all_applications if app.status.lower() not in rejected_statuses]
    
    print(f"Found {len(all_applications)} total applications.")
    print(f"  Active applications: {len(applications)}")
    print(f"  Rejected applications (excluded): {len(all_applications) - len(applications)}\n")
    
    if not applications:
        print("No active applications found.")
        return
    
    # Check how many need regeneration
    print("Checking which applications need regeneration...")
    needs_regen = []
    for app in applications:
        if needs_regeneration(app):
            needs_regen.append(app)
    
    print(f"  {len(needs_regen)} applications need regeneration")
    print(f"  {len(applications) - len(needs_regen)} applications are up to date\n")
    
    if not needs_regen:
        print("All applications are up to date!")
        return
    
    # Prioritize: Show which ones have the "Loading summary..." issue
    print("Checking for 'Loading summary...' issue...")
    loading_issue_count = 0
    for app in needs_regen:
        try:
            if app.summary_path and app.summary_path.exists():
                html_content = read_text_file(app.summary_path)
                if 'summaryContent.innerHTML = `<iframe' in html_content or \
                   'summaryContent.innerHTML = \'<iframe' in html_content:
                    loading_issue_count += 1
        except:
            pass
    
    if loading_issue_count > 0:
        print(f"  ⚠️  {loading_issue_count} applications have the 'Loading summary...' issue and will be fixed\n")
    
    total_success = 0
    total_skipped = 0
    total_errors = 0
    
    # Process in batches of 10
    batch_size = 10
    for start_idx in range(0, len(needs_regen), batch_size):
        success, skipped, errors = regenerate_batch(needs_regen, start_idx, batch_size)
        total_success += success
        total_skipped += skipped
        total_errors += errors
        
        processed = min(start_idx + batch_size, len(needs_regen))
        if processed < len(needs_regen):
            # After first 40, prompt to continue
            if processed >= 40:
                try:
                    response = input(f"\nProcessed {processed} of {len(needs_regen)}. Continue with next batch? (y/n): ")
                    if response.lower() != 'y':
                        print("\nStopped by user.")
                        break
                except EOFError:
                    # Non-interactive environment, continue automatically
                    print(f"\nNon-interactive mode: Continuing with next batch...")
                    continue
            else:
                # First 40 batches, continue automatically
                print(f"\nProcessed {processed} of {len(needs_regen)}. Continuing automatically...")
    
    print("\n" + "=" * 80)
    print("Final Summary:")
    print(f"  ✓ Regenerated: {total_success}")
    print(f"  ⏭️  Skipped: {total_skipped}")
    print(f"  ✗ Errors: {total_errors}")
    print(f"  Total: {len(applications)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
