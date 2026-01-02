"""Networking contact processing service"""
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.networking_contact import NetworkingContact
from app.utils.file_utils import (
    get_data_path, ensure_dir_exists,
    load_yaml, save_yaml, write_text_file, read_text_file
)
from app.utils.datetime_utils import get_est_now, format_datetime_for_filename
from app.services.activity_log_service import ActivityLogService


class NetworkingProcessor:
    """Processes networking contacts and manages contact folders"""
    
    def __init__(self):
        # #region agent log
        # Debug logging disabled - .cursor directory has special protections
        # import json
        # with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
        #     f.write(json.dumps({"location":"networking_processor.py:__init__","message":"NetworkingProcessor initializing","data":{},"timestamp":__import__('time').time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"B"}) + '\n')
        # #endregion
        
        # Create networking folder under main data directory
        data_dir = get_data_path('.')
        self.networking_dir = data_dir / 'networking'
        
        # #region agent log
        # Debug logging disabled - .cursor directory has special protections
        # with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
        #     f.write(json.dumps({"location":"networking_processor.py:__init__","message":"Networking directory path","data":{"path":str(self.networking_dir)},"timestamp":__import__('time').time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"B"}) + '\n')
        # #endregion
        
        ensure_dir_exists(self.networking_dir)
        self.activity_log = ActivityLogService()
        
        # #region agent log
        # Debug logging disabled - .cursor directory has special protections
        # with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
        #     f.write(json.dumps({"location":"networking_processor.py:__init__","message":"NetworkingProcessor initialized successfully","data":{},"timestamp":__import__('time').time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"B"}) + '\n')
        # #endregion
    
    def _clean_profile_details(self, profile_text: str) -> str:
        """Remove LinkedIn metadata and clutter from profile details"""
        lines = profile_text.split('\n')
        cleaned_lines = []
        
        # Skip LinkedIn metadata patterns (similar to job description cleaning)
        skip_patterns = [
            'Skip to main content',
            'LinkedIn',
            'Sign in',
            'Join now',
            'Connect',
            'Follow',
            'Message',
            'More',
            'About',
            'Activity',
            'Experience',
            'Education',
            'Show all',
            'Show less',
            'connections',
            'followers',
            'Mutual connections'
        ]
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Skip lines that match skip patterns
            should_skip = False
            for pattern in skip_patterns:
                # Only skip if the line is EXACTLY the pattern (not if pattern appears in longer text)
                if line.lower() == pattern.lower():
                    should_skip = True
                    break
            
            # Skip very short lines (likely navigation)
            if len(line) <= 3:
                should_skip = True
            
            if not should_skip:
                cleaned_lines.append(line)
        
        # Remove duplicate consecutive lines
        final_lines = []
        prev_line = ""
        for line in cleaned_lines:
            if line != prev_line:
                final_lines.append(line)
                prev_line = line
        
        cleaned = '\n'.join(final_lines)
        return cleaned
    
    def create_networking_contact(
        self,
        person_name: str,
        company_name: str,
        profile_details: str,
        job_title: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        requires_ai_processing: bool = True
    ) -> NetworkingContact:
        """Create a new networking contact"""
        # Store raw profile for future reference
        raw_profile = profile_details
        
        # Clean the profile details
        cleaned_profile = self._clean_profile_details(profile_details)
        
        # Generate contact ID
        timestamp = format_datetime_for_filename()
        contact_id = f"{timestamp}-{person_name}-{company_name}"
        
        # Create contact object
        contact = NetworkingContact(
            id=contact_id,
            person_name=person_name,
            company_name=company_name,
            job_title=job_title,
            linkedin_url=linkedin_url,
            created_at=get_est_now(),
            status="Found Contact",
            status_updated_at=get_est_now(),
            requires_ai_processing=requires_ai_processing
        )
        
        # Create contact folder
        folder_name = contact.get_folder_name()
        folder_path = self.networking_dir / folder_name
        ensure_dir_exists(folder_path)
        contact.folder_path = folder_path
        
        # Create updates subfolder
        updates_dir = folder_path / "updates"
        ensure_dir_exists(updates_dir)
        
        # Save raw profile
        raw_profile_filename = f"{timestamp}-{person_name}-raw.txt"
        raw_profile_path = folder_path / raw_profile_filename
        write_text_file(raw_profile, raw_profile_path)
        contact.raw_profile_path = raw_profile_path
        
        # Save cleaned profile (markdown formatted)
        profile_filename = f"{timestamp}-{person_name}-profile.md"
        profile_path = folder_path / profile_filename
        write_text_file(cleaned_profile, profile_path)
        contact.profile_path = profile_path
        
        # Save metadata
        self._save_contact_metadata(contact)
        
        # Log activity
        try:
            self.activity_log.log_networking_contact_created(
                contact_id=contact.id,
                person_name=contact.person_name,
                company_name=contact.company_name,
                job_title=contact.job_title,
                created_at=contact.created_at,
                status=contact.status,
                match_score=contact.match_score
            )
        except Exception as e:
            print(f"Warning: Could not log networking contact creation activity: {e}")
        
        from app.utils.message_logger import log_message
        log_message(32, f"✓ Created networking contact: {person_name} at {company_name}")
        return contact
    
    def list_all_contacts(self) -> List[NetworkingContact]:
        """List all networking contacts"""
        contacts = []
        
        if not self.networking_dir.exists():
            return contacts
        
        for folder in self.networking_dir.iterdir():
            if folder.is_dir():
                metadata_file = folder / 'metadata.yaml'
                if metadata_file.exists():
                    try:
                        metadata = load_yaml(metadata_file)
                        contact = NetworkingContact.from_dict(metadata)
                        contacts.append(contact)
                    except Exception as e:
                        print(f"Warning: Could not load contact from {folder.name}: {e}")
        
        # Sort by created_at descending (newest first)
        contacts.sort(key=lambda x: x.created_at, reverse=True)
        return contacts
    
    def get_contact_by_id(self, contact_id: str) -> Optional[NetworkingContact]:
        """Get a specific contact by ID"""
        contacts = self.list_all_contacts()
        for contact in contacts:
            if contact.id == contact_id:
                return contact
        return None
    
    def update_contact_status(
        self,
        contact: NetworkingContact,
        status: str,
        notes: Optional[str] = None
    ) -> None:
        """Update contact status and create status update HTML file"""
        old_status = contact.status
        contact.status = status
        contact.status_updated_at = get_est_now()
        
        # Save updated metadata
        self._save_contact_metadata(contact)
        
        # Create status update HTML file (similar to application updates)
        if contact.folder_path:
            timestamp = format_datetime_for_filename()
            updates_dir = contact.folder_path / "updates"
            ensure_dir_exists(updates_dir)
            
            # Create HTML status update file
            # Sanitize status for filename
            status_filename = status.replace("/", "-").replace(" ", "-")
            status_filename = f"{timestamp}-{status_filename}.html"
            status_path = updates_dir / status_filename
            
            # Format the timestamp for display
            from app.utils.datetime_utils import format_for_display
            display_timestamp = format_for_display(contact.status_updated_at)
            
            # Create HTML content (notes are HTML formatted from rich text editor)
            status_class = (
                status.strip()
                .lower()
                .replace("&", "and")
                .replace("/", "-")
                .replace("(", "")
                .replace(")", "")
                .replace("'", "")
                .replace(".", "")
                .replace(",", "")
                .replace(" - ", "-")
                .replace(" ", "-")
            )
            
            notes_html = ""
            if notes and notes.strip():
                notes_html = f"""
                <div class="notes">
                    <h3>Notes:</h3>
                    <div class="notes-text">{notes}</div>
                </div>
                """
            
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Status Update: {status} - {contact.person_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            color: #1f2937;
        }}
        .status-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            background: #3b82f6;
            color: white;
        }}
        .timestamp {{
            color: #6b7280;
            font-size: 14px;
            margin-top: 10px;
        }}
        .contact-info {{
            margin-bottom: 20px;
        }}
        .info-item {{
            margin-bottom: 10px;
        }}
        .info-item strong {{
            color: #1f2937;
        }}
        .notes {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
        }}
        .notes h3 {{
            margin: 0 0 10px 0;
            color: #1f2937;
        }}
        .notes-text {{
            color: #4b5563;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Status Update: {status}</h1>
            <span class="status-badge status-{status_class}">{status}</span>
            <div class="timestamp">{display_timestamp}</div>
        </div>
        
        <div class="contact-info">
            <h3>📋 Contact Information</h3>
            <div class="info-item">
                <strong>Name:</strong> {contact.person_name}
            </div>
            <div class="info-item">
                <strong>Company:</strong> {contact.company_name}
            </div>
            <div class="info-item">
                <strong>Job Title:</strong> {contact.job_title or 'N/A'}
            </div>
            <div class="info-item">
                <strong>Previous Status:</strong> {old_status or 'N/A'}
            </div>
            <div class="info-item">
                <strong>New Status:</strong> {status}
            </div>
        </div>
        {notes_html}
    </div>
</body>
</html>
"""
            write_text_file(html_content, status_path)
            print(f"✓ Created status update file: {status_path}")
        
        # Invalidate contact count cache (includes badge data) when status changes
        try:
            from app.services.contact_count_cache import ContactCountCache
            contact_cache = ContactCountCache()
            contact_cache.invalidate_cache()
        except Exception as e:
            print(f"Warning: Could not invalidate contact count cache: {e}")
        
        # Trigger badge calculation
        try:
            from app.services.badge_calculation_service import BadgeCalculationService
            badge_service = BadgeCalculationService()
            badge_service.update_badge_cache(
                contact.id,
                old_status,
                status
            )
        except Exception as e:
            print(f"Warning: Could not update badge cache: {e}")
        
        # Regenerate contact summary to update badges
        try:
            from app.services.networking_document_generator import NetworkingDocumentGenerator
            doc_generator = NetworkingDocumentGenerator()
            
            # Always try to regenerate if summary exists, even with minimal data
            # This ensures badges are updated when status changes
            if contact.summary_path:
                # Try to load existing data for regeneration
                match_analysis = "No match analysis available."
                messages = {}
                research_content = ""
                
                try:
                    if contact.match_analysis_path and contact.match_analysis_path.exists():
                        from app.utils.file_utils import read_text_file
                        match_analysis = read_text_file(contact.match_analysis_path)
                except Exception as e:
                    print(f"  Note: Could not load match analysis: {e}")
                
                try:
                    if contact.messages_path and contact.messages_path.exists():
                        from app.utils.file_utils import read_text_file
                        # Messages file exists but we'll use empty dict for now
                        # The summary page can work without parsed messages
                        messages = {}
                except Exception as e:
                    print(f"  Note: Could not load messages: {e}")
                
                try:
                    if contact.research_path and contact.research_path.exists():
                        from app.utils.file_utils import read_text_file
                        research_content = read_text_file(contact.research_path)
                except Exception as e:
                    print(f"  Note: Could not load research: {e}")
                
                # Regenerate summary with updated badges (works even with minimal data)
                doc_generator.generate_summary_page(
                    contact,
                    match_analysis,
                    messages,
                    research_content
                )
                from app.utils.message_logger import log_message
                log_message(34, f"✓ Regenerated contact summary with updated badges")
        except Exception as e:
            print(f"Warning: Could not regenerate contact summary: {e}")
            import traceback
            traceback.print_exc()
        
        # Log activity
        try:
            self.activity_log.log_networking_status_changed(
                contact_id=contact.id,
                person_name=contact.person_name,
                company_name=contact.company_name,
                old_status=old_status,
                new_status=status,
                updated_at=contact.status_updated_at,
                notes=notes
            )
        except Exception as e:
            print(f"Warning: Could not log networking status change activity: {e}")
        
        from app.utils.message_logger import log_message
        log_message(33, f"✓ Updated contact status to: {status}")
    
    def update_contact_details(
        self,
        contact: NetworkingContact,
        email: Optional[str] = None,
        location: Optional[str] = None,
        job_title: Optional[str] = None,
        _email_provided: bool = False,
        _location_provided: bool = False,
        _job_title_provided: bool = False
    ) -> None:
        """Update contact details
        
        The _*_provided flags indicate whether the field was explicitly provided in the request,
        allowing us to distinguish between "not provided" and "explicitly set to None/empty"
        """
        if _email_provided:
            contact.email = email if email else None
        if _location_provided:
            contact.location = location if location else None
        if _job_title_provided:
            contact.job_title = job_title if job_title else None
        
        contact.status_updated_at = get_est_now()
        self._save_contact_metadata(contact)
        print(f"✓ Updated contact details: email={contact.email}, location={contact.location}, job_title={contact.job_title}")
    
    def get_contact_updates(self, contact: NetworkingContact) -> List[dict]:
        """Get all status updates for a contact"""
        updates = []
        
        if not contact.folder_path:
            return updates
        
        updates_dir = contact.folder_path / "updates"
        if not updates_dir.exists():
            return updates
        
        for update_file in sorted(updates_dir.iterdir(), reverse=True):
            if update_file.is_file() and update_file.suffix == '.html':
                # Parse filename: YYYYMMDDHHMMSS-Status.html
                filename_parts = update_file.stem.split('-', 1)
                if len(filename_parts) == 2:
                    timestamp_str = filename_parts[0]
                    status = filename_parts[1].replace('-', ' ')
                    
                    # Read file content for notes
                    try:
                        content = read_text_file(update_file)
                        # Extract notes if present (improved parsing)
                        notes = None
                        if '<div class="notes-text">' in content:
                            start = content.find('<div class="notes-text">') + len('<div class="notes-text">')
                            end = content.find('</div>', start)
                            notes = content[start:end].strip()
                        elif '<div class="notes">' in content:
                            # Fallback for old format
                            start = content.find('<div class="notes">') + len('<div class="notes">')
                            end = content.find('</div>', start)
                            notes = content[start:end].strip()
                        
                        updates.append({
                            'timestamp': timestamp_str,
                            'status': status,
                            'notes': notes,
                            'file_path': str(update_file)
                        })
                    except Exception as e:
                        print(f"Warning: Could not read update file {update_file}: {e}")
        
        return updates
    
    def _save_contact_metadata(self, contact: NetworkingContact) -> None:
        """Save contact metadata to YAML file"""
        if not contact.folder_path:
            return
        
        metadata_path = contact.folder_path / 'metadata.yaml'
        metadata = contact.to_dict()
        save_yaml(metadata, metadata_path)

