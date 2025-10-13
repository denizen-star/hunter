"""Resume management service"""
from pathlib import Path
from typing import Optional
from app.models.resume import Resume
from app.utils.file_utils import (
    get_data_path, ensure_dir_exists, 
    load_yaml, save_yaml, read_text_file, write_text_file
)


class ResumeManager:
    """Manages base and custom resumes"""
    
    def __init__(self):
        self.resumes_dir = get_data_path('resumes')
        ensure_dir_exists(self.resumes_dir)
        self.base_resume_path = self.resumes_dir / 'base_resume.md'
        self.base_resume_metadata_path = self.resumes_dir / 'base_resume.yaml'
    
    def load_base_resume(self) -> Resume:
        """Load the base resume"""
        if not self.base_resume_path.exists():
            raise FileNotFoundError("Base resume not found. Please create one first.")
        
        content = read_text_file(self.base_resume_path)
        
        # Load metadata if exists
        metadata = {}
        if self.base_resume_metadata_path.exists():
            metadata = load_yaml(self.base_resume_metadata_path)
        
        return Resume(
            full_name=metadata.get('full_name', ''),
            email=metadata.get('email', ''),
            phone=metadata.get('phone', ''),
            linkedin=metadata.get('linkedin'),
            location=metadata.get('location'),
            content=content,
            file_path=self.base_resume_path,
            version=metadata.get('version', '1.0'),
            is_active=metadata.get('is_active', True)
        )
    
    def save_base_resume(self, resume: Resume) -> None:
        """Save the base resume"""
        # Save content
        write_text_file(resume.content, self.base_resume_path)
        
        # Save metadata
        metadata = {
            'full_name': resume.full_name,
            'email': resume.email,
            'phone': resume.phone,
            'linkedin': resume.linkedin,
            'location': resume.location,
            'version': resume.version,
            'is_active': resume.is_active
        }
        save_yaml(metadata, self.base_resume_metadata_path)
    
    def create_base_resume_template(self) -> None:
        """Create a base resume template"""
        template_content = """# Your Name

## Contact Information
- Email: your.email@example.com
- Phone: +1-XXX-XXX-XXXX
- LinkedIn: linkedin.com/in/yourprofile
- Location: City, State

## Professional Summary
Brief summary of your professional background and key strengths (2-3 sentences).

## Experience

### Job Title | Company Name
*Month Year - Present*

- Accomplishment or responsibility with quantifiable results
- Another key achievement demonstrating skills and impact
- Technical skills used or leadership responsibilities

### Previous Job Title | Previous Company
*Month Year - Month Year*

- Key accomplishment showing growth and impact
- Project or initiative you led or contributed to
- Technologies, tools, or methodologies used

## Education

### Degree Name | University Name
*Year Graduated*

- Relevant coursework or honors
- GPA (if strong and recent)

## Skills

**Technical Skills:** List your technical skills, programming languages, tools, etc.

**Soft Skills:** Communication, Leadership, Problem Solving, etc.

## Certifications & Awards
- Certification Name (Year)
- Award or Recognition (Year)
"""
        
        template_metadata = {
            'full_name': 'Your Name',
            'email': 'your.email@example.com',
            'phone': '+1-XXX-XXX-XXXX',
            'linkedin': 'linkedin.com/in/yourprofile',
            'location': 'City, State',
            'version': '1.0',
            'is_active': True
        }
        
        write_text_file(template_content, self.base_resume_path)
        save_yaml(template_metadata, self.base_resume_metadata_path)
    
    def save_custom_resume(self, job_id: str, content: str, folder_path: Path) -> Path:
        """Save a custom resume for a specific job"""
        custom_resume_path = folder_path / f"custom_resume_{job_id}.md"
        write_text_file(content, custom_resume_path)
        return custom_resume_path
    
    def get_resume_for_job(self, application) -> Resume:
        """Get the resume to use for a job (custom or base)"""
        if application.custom_resume_path and application.custom_resume_path.exists():
            content = read_text_file(application.custom_resume_path)
            base_resume = self.load_base_resume()
            base_resume.content = content
            base_resume.file_path = application.custom_resume_path
            return base_resume
        else:
            return self.load_base_resume()

