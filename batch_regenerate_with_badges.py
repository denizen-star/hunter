#!/usr/bin/env python3
"""Batch regenerate all application and networking contact pages with badge display"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.services.networking_processor import NetworkingProcessor
from app.services.networking_document_generator import NetworkingDocumentGenerator
from app.services.dashboard_generator import DashboardGenerator
from app.utils.file_utils import read_text_file


def regenerate_all_applications():
    """Regenerate all application summary pages with badge display"""
    print("=" * 80)
    print("REGENERATING ALL APPLICATION PAGES (with Badge Display)")
    print("=" * 80)
    print()
    
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    
    # Get all applications
    applications = job_processor.list_all_applications()
    
    if not applications:
        print("No applications found.")
        return 0, 0
    
    print(f"Found {len(applications)} applications to regenerate.\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, app in enumerate(applications, 1):
        try:
            print(f"[{i}/{len(applications)}] Processing: {app.company} - {app.job_title}")
            
            # Check if qualifications exist
            if not app.qualifications_path or not app.qualifications_path.exists():
                print(f"  ⚠️  Skipping: No qualification analysis found")
                skipped_count += 1
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
    
    print()
    print(f"Applications: {success_count} successful, {error_count} errors, {skipped_count} skipped")
    return success_count, error_count


def regenerate_all_networking_contacts():
    """Regenerate all networking contact summary pages with badge display"""
    print("=" * 80)
    print("REGENERATING ALL NETWORKING CONTACT PAGES (with Badge Display)")
    print("=" * 80)
    print()
    
    networking_processor = NetworkingProcessor()
    networking_doc_gen = NetworkingDocumentGenerator()
    
    # Get all contacts
    all_contacts = networking_processor.list_all_contacts()
    
    if not all_contacts:
        print("No networking contacts found.")
        return 0, 0
    
    print(f"Found {len(all_contacts)} networking contacts to regenerate.\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, contact in enumerate(all_contacts, 1):
        try:
            print(f"[{i}/{len(all_contacts)}] Processing: {contact.person_name} - {contact.company_name}")
            
            # Load match analysis if available
            match_analysis = ""
            if contact.match_analysis_path and contact.match_analysis_path.exists():
                match_analysis = read_text_file(contact.match_analysis_path)
            
            # Load messages if available (parse from text file back to dict)
            messages = {}
            if contact.messages_path and contact.messages_path.exists():
                messages_content = read_text_file(contact.messages_path)
                # Parse messages from formatted text file
                lines = messages_content.split('\n')
                current_section = None
                current_message = []
                
                for line in lines:
                    if 'INITIAL CONNECTION REQUEST' in line:
                        current_section = 'connection_request'
                        current_message = []
                    elif 'MEETING INVITATION MESSAGE' in line:
                        if current_section:
                            messages[current_section] = '\n'.join(current_message).strip()
                        current_section = 'meeting_invitation'
                        current_message = []
                    elif 'THANK YOU MESSAGE' in line:
                        if current_section:
                            messages[current_section] = '\n'.join(current_message).strip()
                        current_section = 'thank_you'
                        current_message = []
                    elif 'CONSULTING SERVICES OFFER' in line:
                        if current_section:
                            messages[current_section] = '\n'.join(current_message).strip()
                        current_section = 'consulting_offer'
                        current_message = []
                    elif current_section and line.strip() and not line.startswith('-') and 'Character count' not in line:
                        current_message.append(line)
                
                # Add last section
                if current_section:
                    messages[current_section] = '\n'.join(current_message).strip()
            
            # Load research content if available
            research_content = ""
            if contact.research_path and contact.research_path.exists():
                research_content = read_text_file(contact.research_path)
            
            # Regenerate summary page (this will now include badge display)
            networking_doc_gen.generate_summary_page(
                contact,
                match_analysis,
                messages,
                research_content
            )
            
            print(f"  ✓ Successfully regenerated summary with badges")
            success_count += 1
            
        except Exception as e:
            import traceback
            print(f"  ✗ Error: {e}")
            traceback.print_exc()
            error_count += 1
    
    print()
    print(f"Networking Contacts: {success_count} successful, {error_count} errors, {skipped_count} skipped")
    return success_count, error_count


def main():
    print()
    print("=" * 80)
    print("BATCH REGENERATION: Applications & Networking Contacts with Badges")
    print("=" * 80)
    print()
    
    # Regenerate all applications
    app_success, app_errors = regenerate_all_applications()
    
    print()
    print("-" * 80)
    print()
    
    # Regenerate all networking contacts
    contact_success, contact_errors = regenerate_all_networking_contacts()
    
    print()
    print("-" * 80)
    print()
    
    # Regenerate dashboard
    print("Regenerating dashboard...")
    try:
        dashboard_generator = DashboardGenerator()
        dashboard_generator.generate_index_page()
        print("  ✓ Dashboard regenerated")
    except Exception as e:
        print(f"  ✗ Error regenerating dashboard: {e}")
    
    print()
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Applications: {app_success} successful, {app_errors} errors")
    print(f"Networking Contacts: {contact_success} successful, {contact_errors} errors")
    print()
    print("All pages have been regenerated with the new badge display system!")
    print("=" * 80)


if __name__ == "__main__":
    main()
