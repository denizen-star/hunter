#!/usr/bin/env python3
"""Regenerate Jeanne Sanchez contact summary to fix JavaScript errors"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.networking_processor import NetworkingProcessor
from app.services.networking_document_generator import NetworkingDocumentGenerator
from app.utils.file_utils import read_text_file

def regenerate_jeanne_sanchez():
    """Regenerate Jeanne Sanchez's contact summary"""
    print("Regenerating Jeanne Sanchez contact summary...")
    
    networking_processor = NetworkingProcessor()
    doc_generator = NetworkingDocumentGenerator()
    
    # Find Jeanne Sanchez contact
    all_contacts = networking_processor.list_all_contacts()
    jeanne = None
    
    for contact in all_contacts:
        if "Jeanne Sanchez" in contact.person_name and "PicnicHealth" in contact.company_name:
            jeanne = contact
            break
    
    if not jeanne:
        print("Jeanne Sanchez contact not found!")
        return
    
    print(f"Found: {jeanne.person_name} - {jeanne.company_name}")
    print(f"Status: {jeanne.status}")
    
    # Load existing data for regeneration
    match_analysis = "No match analysis available."
    messages = {}
    research_content = ""
    
    try:
        if jeanne.match_analysis_path and jeanne.match_analysis_path.exists():
            match_analysis = read_text_file(jeanne.match_analysis_path)
            print("  ✓ Loaded match analysis")
    except Exception as e:
        print(f"  Note: Could not load match analysis: {e}")
    
    try:
        if jeanne.messages_path and jeanne.messages_path.exists():
            # Messages file exists but we'll use empty dict
            messages = {}
            print("  ✓ Loaded messages path")
    except Exception as e:
        print(f"  Note: Could not load messages: {e}")
    
    try:
        if jeanne.research_path and jeanne.research_path.exists():
            research_content = read_text_file(jeanne.research_path)
            print("  ✓ Loaded research")
    except Exception as e:
        print(f"  Note: Could not load research: {e}")
    
    # Regenerate summary with fixed JavaScript
    print("\n  → Regenerating summary page with fixed JavaScript...")
    doc_generator.generate_summary_page(
        jeanne,
        match_analysis,
        messages,
        research_content
    )
    
    print(f"\n✓ Successfully regenerated Jeanne Sanchez's summary!")
    print(f"  Summary path: {jeanne.summary_path}")
    print("\nThe JavaScript error should now be fixed. Please refresh the page.")

if __name__ == "__main__":
    regenerate_jeanne_sanchez()


