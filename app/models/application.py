"""Job application data model"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Application:
    """Represents a job application"""
    
    id: str
    company: str
    job_title: str
    created_at: datetime
    status: str = "pending"
    
    # File paths
    job_description_path: Optional[Path] = None
    raw_job_description_path: Optional[Path] = None
    qualifications_path: Optional[Path] = None
    cover_letter_path: Optional[Path] = None
    custom_resume_path: Optional[Path] = None
    summary_path: Optional[Path] = None
    hiring_manager_intros_path: Optional[Path] = None
    recruiter_intros_path: Optional[Path] = None
    research_path: Optional[Path] = None
    
    # Resume reference
    resume_used: str = "base_resume.md"
    
    # Additional metadata
    folder_path: Optional[Path] = None
    status_updated_at: Optional[datetime] = None
    match_score: Optional[float] = None
    job_url: Optional[str] = None
    posted_date: Optional[str] = None
    
    # Job details
    salary_range: Optional[str] = None
    location: Optional[str] = None
    hiring_manager: Optional[str] = None
    
    # Contact tracking
    contact_count: Optional[int] = None
    
    # Flagging
    flagged: bool = False
    
    # Checklist tracking
    checklist_items: Optional[dict] = None
    
    def __post_init__(self):
        """Convert string paths to Path objects and strings to datetime objects"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        if isinstance(self.status_updated_at, str) and self.status_updated_at:
            self.status_updated_at = datetime.fromisoformat(self.status_updated_at)
        
        for field_name in ['job_description_path', 'raw_job_description_path', 'qualifications_path', 'cover_letter_path', 
                          'custom_resume_path', 'summary_path', 'hiring_manager_intros_path', 'recruiter_intros_path', 'research_path', 'folder_path']:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, Path(value))
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Application':
        """Create Application instance from dictionary"""
        return cls(
            id=data['id'],
            company=data['company'],
            job_title=data['job_title'],
            created_at=data['created_at'],
            status=data.get('status', 'pending'),
            job_description_path=data.get('job_description_path'),
            raw_job_description_path=data.get('raw_job_description_path'),
            qualifications_path=data.get('qualifications_path'),
            cover_letter_path=data.get('cover_letter_path'),
            custom_resume_path=data.get('custom_resume_path'),
            summary_path=data.get('summary_path'),
            hiring_manager_intros_path=data.get('hiring_manager_intros_path'),
            recruiter_intros_path=data.get('recruiter_intros_path'),
            research_path=data.get('research_path'),
            resume_used=data.get('resume_used', 'base_resume.md'),
            folder_path=data.get('folder_path'),
            status_updated_at=data.get('status_updated_at'),
            match_score=data.get('match_score'),
            job_url=data.get('job_url'),
            posted_date=data.get('posted_date'),
            salary_range=data.get('salary_range'),
            location=data.get('location'),
            hiring_manager=data.get('hiring_manager'),
            contact_count=data.get('contact_count'),
            flagged=data.get('flagged', False),
            checklist_items=data.get('checklist_items')
        )
    
    def to_dict(self) -> dict:
        """Convert Application instance to dictionary"""
        return {
            'id': self.id,
            'company': self.company,
            'job_title': self.job_title,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'status': self.status,
            'job_description_path': str(self.job_description_path) if self.job_description_path else None,
            'raw_job_description_path': str(self.raw_job_description_path) if self.raw_job_description_path else None,
            'qualifications_path': str(self.qualifications_path) if self.qualifications_path else None,
            'cover_letter_path': str(self.cover_letter_path) if self.cover_letter_path else None,
            'custom_resume_path': str(self.custom_resume_path) if self.custom_resume_path else None,
            'summary_path': str(self.summary_path) if self.summary_path else None,
            'hiring_manager_intros_path': str(self.hiring_manager_intros_path) if self.hiring_manager_intros_path else None,
            'recruiter_intros_path': str(self.recruiter_intros_path) if self.recruiter_intros_path else None,
            'research_path': str(self.research_path) if self.research_path else None,
            'resume_used': self.resume_used,
            'folder_path': str(self.folder_path) if self.folder_path else None,
            'status_updated_at': self.status_updated_at.isoformat() if self.status_updated_at and isinstance(self.status_updated_at, datetime) else self.status_updated_at,
            'match_score': self.match_score,
            'job_url': self.job_url,
            'posted_date': self.posted_date,
            'salary_range': self.salary_range,
            'location': self.location,
            'hiring_manager': self.hiring_manager,
            'contact_count': self.contact_count,
            'flagged': self.flagged,
            'checklist_items': self.checklist_items
        }
    
    def get_folder_name(self) -> str:
        """Generate folder name: <company>-<jobtitle>"""
        company = ''.join(c for c in self.company if c.isalnum() or c in ' -')
        job_title = ''.join(c for c in self.job_title if c.isalnum() or c in ' -')
        
        company = '-'.join(company.split())
        job_title = '-'.join(job_title.split())
        
        return f"{company}-{job_title}"
    
    def calculate_contact_count(self) -> int:
        """Calculate contact count from status updates (including legacy labels)"""
        if not self.folder_path:
            return 0
            
        updates_dir = self.folder_path / "updates"
        if not updates_dir.exists():
            return 0
        
        contact_count = 0
        for update_file in updates_dir.iterdir():
            if update_file.is_file() and update_file.suffix == '.html':
                # Extract status from filename
                # Format: YYYYMMDDHHMMSS-Status.html
                filename_parts = update_file.stem.split('-', 1)
                if len(filename_parts) == 2:
                    status = filename_parts[1]
                    if status in ['Contacted Someone', 'Contacted Hiring Manager', 'Company Response']:
                        contact_count += 1
        
        return contact_count
    
    def get_latest_completed_checklist_item(self) -> Optional[str]:
        """Get the latest completed checklist item key for pill display"""
        if not self.checklist_items:
            return None
        
        # Define order of checklist items
        checklist_order = [
            "application_submitted",
            "linkedin_message_sent",
            "contact_email_found",
            "email_verified",
            "email_sent",
            "message_read",
            "profile_viewed",
            "response_received",
            "followup_sent",
            "interview_scheduled",
            "interview_completed",
            "thank_you_sent"
        ]
        
        # Find the last completed item in order
        for item_key in reversed(checklist_order):
            if self.checklist_items.get(item_key, False):
                return item_key
        
        return None

