#!/usr/bin/env python3
"""Regenerate Danika Okerstrom (Elastic) networking contact with full AI processing"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.networking_processor import NetworkingProcessor
from app.services.networking_document_generator import NetworkingDocumentGenerator
from app.services.resume_manager import ResumeManager
from app.services.ai_analyzer import AIAnalyzer

def regenerate_danika():
    """Regenerate Danika Okerstrom contact with full AI processing"""
    print("=" * 80)
    print("Regenerating Danika Okerstrom (Elastic) Contact")
    print("=" * 80)
    print()
    
    # Initialize services
    networking_processor = NetworkingProcessor()
    doc_generator = NetworkingDocumentGenerator()
    resume_manager = ResumeManager()
    ai_analyzer = AIAnalyzer()
    
    # Contact ID from metadata
    contact_id = "20251214203720-Danika Okerstrom-Elastic"
    
    # Load contact
    contact = networking_processor.get_contact_by_id(contact_id)
    
    if not contact:
        print(f"❌ Contact not found: {contact_id}")
        return False
    
    print(f"✓ Found contact: {contact.person_name} at {contact.company_name}")
    
    # Check Ollama connection
    if not ai_analyzer.check_connection():
        print("❌ Cannot connect to Ollama. Please ensure Ollama is running.")
        return False
    
    print("✓ Ollama connection verified")
    
    # Load resume
    try:
        resume = resume_manager.load_base_resume()
        print("✓ Resume loaded")
    except FileNotFoundError:
        print("❌ Base resume not found. Please create a resume first.")
        return False
    
    # Upgrade to full AI processing if needed
    if not contact.requires_ai_processing:
        print("⚠ Upgrading simple contact to full AI processing...")
        contact.requires_ai_processing = True
    
    # Regenerate all documents
    print("\n🔄 Generating all documents (this will take 5-6 minutes)...")
    print("   - Match analysis")
    print("   - AI research")
    print("   - Message templates")
    print("   - Summary page")
    print()
    
    try:
        doc_generator.generate_all_documents(contact, resume.content)
        
        # Save updated metadata
        networking_processor._save_contact_metadata(contact)
        
        print()
        print("=" * 80)
        print("✅ Successfully regenerated contact!")
        print("=" * 80)
        print(f"   Contact: {contact.person_name} at {contact.company_name}")
        print(f"   Match Score: {contact.match_score:.1f}%")
        
        if contact.summary_path:
            folder_name = contact.folder_path.name
            summary_filename = contact.summary_path.name
            summary_url = f"/networking/{folder_name}/{summary_filename}"
            print(f"   Summary URL: {summary_url}")
            print(f"   View at: http://localhost:51003{summary_url}")
        
        return True
        
    except Exception as e:
        import traceback
        print()
        print("=" * 80)
        print("❌ Error during regeneration:")
        print("=" * 80)
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = regenerate_danika()
    sys.exit(0 if success else 1)

