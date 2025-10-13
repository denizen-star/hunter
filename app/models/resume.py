"""Resume data model"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Resume:
    """Represents a resume"""
    
    full_name: str
    email: str
    phone: str
    linkedin: Optional[str] = None
    location: Optional[str] = None
    content: str = ""
    file_path: Optional[Path] = None
    version: str = "1.0"
    is_active: bool = True
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Resume':
        """Create Resume instance from dictionary"""
        return cls(
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            linkedin=data.get('linkedin'),
            location=data.get('location'),
            content=data.get('content', ''),
            file_path=Path(data['file_path']) if data.get('file_path') else None,
            version=data.get('version', '1.0'),
            is_active=data.get('is_active', True)
        )
    
    def to_dict(self) -> dict:
        """Convert Resume instance to dictionary"""
        return {
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'linkedin': self.linkedin,
            'location': self.location,
            'content': self.content,
            'file_path': str(self.file_path) if self.file_path else None,
            'version': self.version,
            'is_active': self.is_active
        }

