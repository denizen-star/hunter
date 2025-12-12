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
        linkedin_url: Optional[str] = None
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
            status="To Research",
            status_updated_at=get_est_now()
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
        
        print(f"✓ Created networking contact: {person_name} at {company_name}")
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
        """Update contact status and create timeline entry"""
        old_status = contact.status
        contact.status = status
        contact.status_updated_at = get_est_now()
        
        # Create update file in updates folder
        if contact.folder_path:
            updates_dir = contact.folder_path / "updates"
            ensure_dir_exists(updates_dir)
            
            timestamp = format_datetime_for_filename()
            update_filename = f"{timestamp}-{status.replace(' ', '-')}.html"
            update_path = updates_dir / update_filename
            
            # Create simple update HTML
            update_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Status Update: {status}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }}
        .update {{ background: #f9fafb; border-left: 4px solid #3b82f6; padding: 16px; margin: 20px 0; }}
        .timestamp {{ color: #6b7280; font-size: 14px; }}
        .status {{ font-weight: 600; color: #1f2937; margin: 8px 0; }}
        .notes {{ margin-top: 12px; color: #374151; }}
    </style>
</head>
<body>
    <div class="update">
        <div class="timestamp">{contact.status_updated_at.strftime('%B %d, %Y at %I:%M %p EST')}</div>
        <div class="status">Status changed from "{old_status}" to "{status}"</div>
        {f'<div class="notes">{notes}</div>' if notes else ''}
    </div>
</body>
</html>"""
            write_text_file(update_html, update_path)
        
        # Save updated metadata
        self._save_contact_metadata(contact)
        print(f"✓ Updated contact status to: {status}")
    
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
                        # Extract notes if present (simple parsing)
                        notes = None
                        if '<div class="notes">' in content:
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

