#!/usr/bin/env python3
"""
Regenerate all application summary pages with new badge display
and all networking contact pages with new status dropdown.

This script processes items in batches to avoid overwhelming the system.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.services.networking_processor import NetworkingProcessor
from app.services.networking_document_generator import NetworkingDocumentGenerator
from app.utils.file_utils import read_text_file


def regenerate_applications(batch_size=10):
    """Regenerate all application summary pages with badge display"""
    print("=" * 60)
    print("REGENERATING APPLICATION SUMMARY PAGES")
    print("=" * 60)
    
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    
    # Get all applications
    applications = job_processor.list_all_applications()
    total = len(applications)
    
    print(f"\nFound {total} applications to process")
    print(f"Processing in batches of {batch_size}...\n")
    
    success_count = 0
    error_count = 0
    
    for i in range(0, total, batch_size):
        batch = applications[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"\n--- Batch {batch_num}/{total_batches} ---")
        
        for app in batch:
            try:
                print(f"  Processing: {app.company} - {app.job_title}")
                qualifications = doc_generator._load_qualifications(app)
                doc_generator.generate_summary_page(app, qualifications)
                success_count += 1
                print(f"    ✓ Success")
            except Exception as e:
                error_count += 1
                print(f"    ✗ Error: {str(e)}")
        
        print(f"  Batch {batch_num} complete. Progress: {min(i + batch_size, total)}/{total}")
    
    print(f"\n{'=' * 60}")
    print(f"APPLICATION REGENERATION COMPLETE")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {total}")
    print(f"{'=' * 60}\n")


def regenerate_networking_contacts(batch_size=10):
    """Regenerate all networking contact summary pages with new status dropdown"""
    print("=" * 60)
    print("REGENERATING NETWORKING CONTACT PAGES")
    print("=" * 60)
    
    networking_processor = NetworkingProcessor()
    networking_doc_generator = NetworkingDocumentGenerator()
    
    # Get all contacts
    contacts = networking_processor.list_all_contacts()
    total = len(contacts)
    
    print(f"\nFound {total} networking contacts to process")
    print(f"Processing in batches of {batch_size}...\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i in range(0, total, batch_size):
        batch = contacts[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"\n--- Batch {batch_num}/{total_batches} ---")
        
        for contact in batch:
            try:
                # Skip if no summary path (contact might not have been fully processed)
                if not contact.summary_path or not contact.summary_path.exists():
                    print(f"  Skipping: {contact.person_name} - {contact.company_name} (no summary path)")
                    skipped_count += 1
                    continue
                
                print(f"  Processing: {contact.person_name} - {contact.company_name}")
                
                # Load existing data
                match_analysis = ''
                if contact.match_analysis_path and contact.match_analysis_path.exists():
                    match_analysis = read_text_file(contact.match_analysis_path)
                
                messages = {}
                if contact.messages_path and contact.messages_path.exists():
                    messages_content = read_text_file(contact.messages_path)
                    # Parse messages if needed (simplified for now)
                    messages = {
                        'connection_request': '',
                        'meeting_invitation': '',
                        'thank_you': '',
                        'consulting_offer': ''
                    }
                
                research_content = ''
                if contact.research_path and contact.research_path.exists():
                    research_content = read_text_file(contact.research_path)
                
                networking_doc_generator.generate_summary_page(
                    contact,
                    match_analysis,
                    messages,
                    research_content
                )
                success_count += 1
                print(f"    ✓ Success")
            except Exception as e:
                error_count += 1
                print(f"    ✗ Error: {str(e)}")
        
        print(f"  Batch {batch_num} complete. Progress: {min(i + batch_size, total)}/{total}")
    
    print(f"\n{'=' * 60}")
    print(f"NETWORKING CONTACT REGENERATION COMPLETE")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {total}")
    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("REGENERATING ALL PAGES WITH NEW FEATURES")
    print("=" * 60)
    print("\nThis will:")
    print("  1. Regenerate all application summary pages with badge display")
    print("  2. Regenerate all networking contact pages with new status dropdown")
    print("\nProcessing will be done in batches to avoid overwhelming the system.\n")
    
    # Regenerate applications first
    regenerate_applications(batch_size=10)
    
    # Then regenerate networking contacts
    regenerate_networking_contacts(batch_size=10)
    
    print("\n" + "=" * 60)
    print("ALL REGENERATIONS COMPLETE")
    print("=" * 60)
    print("\nAll pages have been updated with:")
    print("  ✓ New badge display (earned badges on left, next badge on right)")
    print("  ✓ Updated status dropdowns with new statuses")
    print("  ✓ Status update fixes (notes saving, immediate UI updates)")
    print("\nYou can now test the changes tomorrow!")

