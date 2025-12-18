#!/usr/bin/env python3
"""Regenerate all networking contact summary pages with updated badges and menu"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.networking_processor import NetworkingProcessor
from app.services.networking_document_generator import NetworkingDocumentGenerator


def main():
    print("=" * 80)
    print("Regenerating All Networking Contact Summary Pages")
    print("=" * 80)
    print()
    
    networking_processor = NetworkingProcessor()
    doc_generator = NetworkingDocumentGenerator()
    
    # Get all contacts
    contacts = networking_processor.list_all_contacts()
    
    if not contacts:
        print("No networking contacts found.")
        return
    
    print(f"Found {len(contacts)} networking contacts to regenerate.\n")
    print("Processing in batches of 10...\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    # Process all contacts in batches of 10
    batch_size = 10
    total_batches = (len(contacts) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(contacts))
        batch_contacts = contacts[start_idx:end_idx]
        
        print(f"\n{'='*80}")
        print(f"Batch {batch_num + 1}/{total_batches} (Processing contacts {start_idx + 1}-{end_idx})")
        print(f"{'='*80}\n")
        
        batch_success = 0
        batch_error = 0
        batch_skipped = 0
        
        for i, contact in enumerate(batch_contacts, start_idx + 1):
            try:
                print(f"[{i}/{len(contacts)}] Processing: {contact.person_name} - {contact.company_name}")
                
                # Check if contact has required files
                if not contact.profile_path or not contact.profile_path.exists():
                    print(f"  ⚠️  Skipping: No profile file found")
                    skipped_count += 1
                    batch_skipped += 1
                    continue
                
                # Regenerate summary page
                if contact.match_analysis_path and contact.match_analysis_path.exists():
                    # Full AI contact - need to load match analysis and messages
                    from app.utils.file_utils import read_text_file
                    match_analysis = read_text_file(contact.match_analysis_path) if contact.match_analysis_path.exists() else ""
                    # Get messages and convert to dict format
                    messages_list = doc_generator._get_standard_networking_messages()
                    personalized_messages = [doc_generator._replace_message_placeholders(msg, contact) for msg in messages_list]
                    messages = {
                        'connection_request': personalized_messages[0] if len(personalized_messages) > 0 else '',
                        'meeting_invitation': personalized_messages[1] if len(personalized_messages) > 1 else '',
                        'thank_you': personalized_messages[2] if len(personalized_messages) > 2 else '',
                        'consulting_offer': personalized_messages[3] if len(personalized_messages) > 3 else ''
                    }
                    # Load research if available
                    research_content = ""
                    if contact.research_path and contact.research_path.exists():
                        research_content = read_text_file(contact.research_path)
                    doc_generator.generate_summary_page(contact, match_analysis, messages, research_content)
                    print(f"  ✓ Successfully regenerated full summary page")
                else:
                    # Simple contact - use generate_simple_summary_page
                    doc_generator.generate_simple_summary_page(contact)
                    print(f"  ✓ Successfully regenerated simple summary page")
                
                success_count += 1
                batch_success += 1
                
            except Exception as e:
                import traceback
                print(f"  ✗ Error: {e}")
                traceback.print_exc()
                error_count += 1
                batch_error += 1
        
        # Batch summary
        print(f"\nBatch {batch_num + 1} Summary: {batch_success} successful, {batch_error} errors, {batch_skipped} skipped")
    
    print()
    print("=" * 80)
    print(f"FINAL SUMMARY: {success_count} successful, {error_count} errors, {skipped_count} skipped")
    print("=" * 80)
    print()
    print("Note: All networking contact pages now include:")
    print("      - Updated badge display (single-line layout)")
    print("      - Shared menu navigation")
    print("      - Updated status names")


if __name__ == "__main__":
    main()
