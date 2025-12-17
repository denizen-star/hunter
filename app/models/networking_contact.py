"""Networking contact data model"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List


@dataclass
class NetworkingContact:
    """Represents a professional networking contact"""
    
    id: str
    person_name: str
    company_name: str
    created_at: datetime
    status: str = "To Research"
    
    # Optional fields
    job_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    
    # File paths
    profile_path: Optional[Path] = None
    raw_profile_path: Optional[Path] = None
    summary_path: Optional[Path] = None
    research_path: Optional[Path] = None
    match_analysis_path: Optional[Path] = None
    messages_path: Optional[Path] = None
    
    # Metadata
    folder_path: Optional[Path] = None
    status_updated_at: Optional[datetime] = None
    match_score: Optional[float] = None
    last_interaction_type: Optional[str] = None
    
    # Calendar and tracking
    follow_up_reminder_date: Optional[datetime] = None
    calendar_invite_generated: bool = False
    contact_count: Optional[int] = None
    
    # Flagging
    flagged: bool = False
    
    # AI Processing flag
    requires_ai_processing: bool = True
    
    # Checklist tracking (if needed later)
    checklist_items: Optional[dict] = None
    
    def __post_init__(self):
        """Convert string paths to Path objects and strings to datetime objects"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        if isinstance(self.status_updated_at, str) and self.status_updated_at:
            self.status_updated_at = datetime.fromisoformat(self.status_updated_at)
        
        if isinstance(self.follow_up_reminder_date, str) and self.follow_up_reminder_date:
            self.follow_up_reminder_date = datetime.fromisoformat(self.follow_up_reminder_date)
        
        # Convert path fields
        for field_name in ['profile_path', 'raw_profile_path', 'summary_path', 'research_path',
                          'match_analysis_path', 'messages_path', 'folder_path']:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, Path(value))
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NetworkingContact':
        """Create NetworkingContact instance from dictionary"""
        return cls(
            id=data['id'],
            person_name=data['person_name'],
            company_name=data['company_name'],
            created_at=data['created_at'],
            status=data.get('status', 'To Research'),
            job_title=data.get('job_title'),
            linkedin_url=data.get('linkedin_url'),
            email=data.get('email'),
            location=data.get('location'),
            profile_path=data.get('profile_path'),
            raw_profile_path=data.get('raw_profile_path'),
            summary_path=data.get('summary_path'),
            research_path=data.get('research_path'),
            match_analysis_path=data.get('match_analysis_path'),
            messages_path=data.get('messages_path'),
            folder_path=data.get('folder_path'),
            status_updated_at=data.get('status_updated_at'),
            match_score=data.get('match_score'),
            last_interaction_type=data.get('last_interaction_type'),
            follow_up_reminder_date=data.get('follow_up_reminder_date'),
            calendar_invite_generated=data.get('calendar_invite_generated', False),
            contact_count=data.get('contact_count'),
            flagged=data.get('flagged', False),
            requires_ai_processing=data.get('requires_ai_processing', True),
            checklist_items=data.get('checklist_items')
        )
    
    def to_dict(self) -> dict:
        """Convert NetworkingContact instance to dictionary"""
        # Ensure checklist_items is a simple dict or None (not a complex nested structure)
        checklist_items = self.checklist_items
        if checklist_items is not None and not isinstance(checklist_items, dict):
            checklist_items = None
        
        return {
            'id': self.id,
            'person_name': self.person_name,
            'company_name': self.company_name,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'status': self.status,
            'job_title': self.job_title,
            'linkedin_url': self.linkedin_url,
            'email': self.email,
            'location': self.location,
            'profile_path': str(self.profile_path) if self.profile_path else None,
            'raw_profile_path': str(self.raw_profile_path) if self.raw_profile_path else None,
            'summary_path': str(self.summary_path) if self.summary_path else None,
            'research_path': str(self.research_path) if self.research_path else None,
            'match_analysis_path': str(self.match_analysis_path) if self.match_analysis_path else None,
            'messages_path': str(self.messages_path) if self.messages_path else None,
            'folder_path': str(self.folder_path) if self.folder_path else None,
            'status_updated_at': self.status_updated_at.isoformat() if self.status_updated_at and isinstance(self.status_updated_at, datetime) else self.status_updated_at,
            'match_score': self.match_score,
            'last_interaction_type': self.last_interaction_type,
            'follow_up_reminder_date': self.follow_up_reminder_date.isoformat() if self.follow_up_reminder_date and isinstance(self.follow_up_reminder_date, datetime) else self.follow_up_reminder_date,
            'calendar_invite_generated': self.calendar_invite_generated,
            'contact_count': self.contact_count,
            'flagged': self.flagged,
            'requires_ai_processing': self.requires_ai_processing,
            'checklist_items': checklist_items
        }
    
    def get_folder_name(self) -> str:
        """Generate folder name: <person_name>-<company_name>"""
        person = ''.join(c for c in self.person_name if c.isalnum() or c in ' -')
        company = ''.join(c for c in self.company_name if c.isalnum() or c in ' -')
        
        person = '-'.join(person.split())
        company = '-'.join(company.split())
        
        return f"{person}-{company}"
    
    def calculate_contact_count(self) -> int:
        """Calculate contact count from status updates"""
        if not self.folder_path:
            return 0
            
        updates_dir = self.folder_path / "updates"
        if not updates_dir.exists():
            return 0
        
        contact_count = 0
        # Updated status names for new system
        contact_statuses = [
            'Pending Reply',
            'Connected - Initial',
            'In Conversation',
            'Meeting Scheduled',
            'Meeting Complete',
            # Legacy status names for backward compatibility
            'Contacted - Sent',
            'Contacted - Replied',
            'Contacted---Sent',
            'Contacted---Replied'
        ]
        
        for update_file in updates_dir.iterdir():
            if update_file.is_file() and update_file.suffix == '.html':
                # Extract status from filename: YYYYMMDDHHMMSS-Status.html
                filename_parts = update_file.stem.split('-', 1)
                if len(filename_parts) == 2:
                    status = filename_parts[1]
                    if any(contact_status in status for contact_status in contact_statuses):
                        contact_count += 1
        
        return contact_count
    
    def get_days_since_update(self) -> int:
        """Calculate days since last status update"""
        if not self.status_updated_at:
            # If never updated, use creation date
            update_date = self.created_at
        else:
            update_date = self.status_updated_at
        
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone(timedelta(hours=-4)))  # EST
        
        # Ensure update_date has timezone info
        if update_date.tzinfo is None:
            update_date = update_date.replace(tzinfo=timezone(timedelta(hours=-4)))
        
        delta = now - update_date
        return delta.days
    
    def get_timing_color_class(self) -> str:
        """Get CSS color class based on timing since last update"""
        days = self.get_days_since_update()
        
        # Check if contact is in Cold/Inactive or Dormant status first
        if self.status in ['Cold/Inactive', 'Dormant']:
            return 'gray'
        
        # Legacy status support
        if self.status == 'Cold/Archive':
            return 'gray'
        
        # Strong Connection (Nurture) statuses get blue
        if self.status == 'Strong Connection':
            if 60 <= days <= 90:
                return 'blue'
            elif days > 90:
                return 'gray'
        
        # Legacy Nurture statuses support
        if 'Nurture' in self.status:
            if 60 <= days <= 90:
                return 'blue'
            elif days > 90:
                return 'gray'
        
        # General timing colors
        if days < 7:
            return 'white'
        elif 8 <= days <= 15:
            return 'green'
        elif 15 < days <= 30:
            return 'yellow'
        elif 30 < days <= 60:
            return 'red'
        elif 60 < days <= 90:
            return 'blue'
        else:  # > 90 days
            return 'gray'
    
    def get_next_step(self) -> str:
        """Get the next action step based on current status"""
        # Workflow mapping: status -> next action (new status system)
        next_steps = {
            # PROSPECTING phase
            'To Research': 'Research their background, company, or recent activity to personalize your message',
            'Ready to Connect': 'Send the initial connection request or message',
            
            # OUTREACH phase
            'Pending Reply': 'Set a follow-up reminder. Wait 5-7 business days for a response',
            'Connected - Initial': 'Log the reply, craft a response, and propose a specific next step',
            'Cold/Inactive': 'Move to Cold list for occasional contact (3-6 months)',
            
            # ENGAGEMENT phase
            'In Conversation': 'Keep the conversation moving toward a scheduled call or meeting',
            'Meeting Scheduled': 'Prepare for the meeting, send confirmation/agenda',
            'Meeting Complete': 'Send a thank-you note within 24 hours',
            
            # NURTURE phase
            'Strong Connection': 'Set a specific date for your next check-in',
            'Referral Partner': 'Prioritize providing value and seek ways to help them',
            'Dormant': 'Look for an opportunity to genuinely re-engage',
            
            # Legacy status support (for backward compatibility during migration)
            'Ready to Contact': 'Send the initial connection request or message',
            'Contacted - Sent': 'Set a follow-up reminder. Wait 5-7 business days for a response',
            'Contacted---Sent': 'Set a follow-up reminder. Wait 5-7 business days for a response',
            'Contacted - Replied': 'Log the reply, craft a response, and propose a specific next step',
            'Contacted---Replied': 'Log the reply, craft a response, and propose a specific next step',
            'Contacted - No Response': 'Send a second, polite follow-up message',
            'Contacted---No Response': 'Send a second, polite follow-up message',
            'Cold/Archive': 'Move to Cold list for occasional contact (3-6 months)',
            'Action Pending - You': 'Complete your committed action and update status',
            'Action Pending---You': 'Complete your committed action and update status',
            'Action Pending - Them': 'Set a reminder to follow up on their committed action',
            'Action Pending---Them': 'Set a reminder to follow up on their committed action',
            'New Connection': 'Schedule a light, value-add check-in in 1-2 months',
            'Nurture (1-3 Mo.)': 'Set a specific date for your next check-in',
            'Nurture (4-6 Mo.)': 'Schedule a reminder to reach out in 4-6 months',
            'Inactive/Dormant': 'Look for an opportunity to genuinely re-engage'
        }
        
        return next_steps.get(self.status, 'Review contact status and determine next action')