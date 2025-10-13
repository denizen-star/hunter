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
    qualifications_path: Optional[Path] = None
    cover_letter_path: Optional[Path] = None
    custom_resume_path: Optional[Path] = None
    summary_path: Optional[Path] = None
    
    # Resume reference
    resume_used: str = "base_resume.md"
    
    # Additional metadata
    folder_path: Optional[Path] = None
    status_updated_at: Optional[datetime] = None
    match_score: Optional[float] = None
    job_url: Optional[str] = None
    
    def __post_init__(self):
        """Convert string paths to Path objects and strings to datetime objects"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        if isinstance(self.status_updated_at, str) and self.status_updated_at:
            self.status_updated_at = datetime.fromisoformat(self.status_updated_at)
        
        for field_name in ['job_description_path', 'qualifications_path', 'cover_letter_path', 
                          'custom_resume_path', 'summary_path', 'folder_path']:
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
            qualifications_path=data.get('qualifications_path'),
            cover_letter_path=data.get('cover_letter_path'),
            custom_resume_path=data.get('custom_resume_path'),
            summary_path=data.get('summary_path'),
            resume_used=data.get('resume_used', 'base_resume.md'),
            folder_path=data.get('folder_path'),
            status_updated_at=data.get('status_updated_at'),
            match_score=data.get('match_score'),
            job_url=data.get('job_url')
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
            'qualifications_path': str(self.qualifications_path) if self.qualifications_path else None,
            'cover_letter_path': str(self.cover_letter_path) if self.cover_letter_path else None,
            'custom_resume_path': str(self.custom_resume_path) if self.custom_resume_path else None,
            'summary_path': str(self.summary_path) if self.summary_path else None,
            'resume_used': self.resume_used,
            'folder_path': str(self.folder_path) if self.folder_path else None,
            'status_updated_at': self.status_updated_at.isoformat() if self.status_updated_at and isinstance(self.status_updated_at, datetime) else self.status_updated_at,
            'match_score': self.match_score,
            'job_url': self.job_url
        }
    
    def get_folder_name(self) -> str:
        """Generate folder name: <company>-<jobtitle>"""
        company = ''.join(c for c in self.company if c.isalnum() or c in ' -')
        job_title = ''.join(c for c in self.job_title if c.isalnum() or c in ' -')
        
        company = '-'.join(company.split())
        job_title = '-'.join(job_title.split())
        
        return f"{company}-{job_title}"

