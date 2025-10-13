"""Job processing service"""
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from app.models.application import Application
from app.utils.file_utils import (
    get_data_path, ensure_dir_exists,
    load_yaml, save_yaml, write_text_file, read_text_file
)
from app.utils.datetime_utils import get_est_now, format_datetime_for_filename


class JobProcessor:
    """Processes job descriptions and creates application folders"""
    
    def __init__(self):
        self.applications_dir = get_data_path('applications')
        ensure_dir_exists(self.applications_dir)
    
    def create_job_application(
        self,
        company: str,
        job_title: str,
        job_description: str,
        job_url: Optional[str] = None
    ) -> Application:
        """Create a new job application"""
        # Generate application ID
        timestamp = format_datetime_for_filename()
        app_id = f"{timestamp}-{company}-{job_title}"
        
        # Create application object
        application = Application(
            id=app_id,
            company=company,
            job_title=job_title,
            created_at=get_est_now(),
            status="pending",
            job_url=job_url,
            status_updated_at=get_est_now()
        )
        
        # Create application folder
        folder_name = application.get_folder_name()
        folder_path = self.applications_dir / folder_name
        ensure_dir_exists(folder_path)
        application.folder_path = folder_path
        
        # Create updates subfolder
        updates_dir = folder_path / "updates"
        ensure_dir_exists(updates_dir)
        
        # Save job description
        job_desc_filename = f"{timestamp}-{company}-{job_title}.md"
        job_desc_path = folder_path / job_desc_filename
        write_text_file(job_description, job_desc_path)
        application.job_description_path = job_desc_path
        
        # Save application metadata
        self._save_application_metadata(application)
        
        return application
    
    def _save_application_metadata(self, application: Application) -> None:
        """Save application metadata to YAML file"""
        metadata_path = application.folder_path / "application.yaml"
        metadata = application.to_dict()
        save_yaml(metadata, metadata_path)
    
    def list_all_applications(self) -> List[Application]:
        """List all job applications"""
        applications = []
        
        if not self.applications_dir.exists():
            return applications
        
        for folder_path in self.applications_dir.iterdir():
            if folder_path.is_dir():
                metadata_path = folder_path / "application.yaml"
                if metadata_path.exists():
                    try:
                        metadata = load_yaml(metadata_path)
                        metadata['folder_path'] = str(folder_path)
                        application = Application.from_dict(metadata)
                        applications.append(application)
                    except Exception as e:
                        print(f"Error loading application from {folder_path}: {e}")
        
        # Sort by created_at descending
        applications.sort(key=lambda x: x.created_at, reverse=True)
        return applications
    
    def get_application_by_id(self, app_id: str) -> Optional[Application]:
        """Get an application by ID"""
        applications = self.list_all_applications()
        return next((app for app in applications if app.id == app_id), None)
    
    def update_application_status(
        self,
        application: Application,
        status: str,
        notes: Optional[str] = None
    ) -> None:
        """Update application status with optional notes"""
        application.status = status
        application.status_updated_at = get_est_now()
        
        # Save notes if provided
        if notes:
            timestamp = format_datetime_for_filename()
            updates_dir = application.folder_path / "updates"
            ensure_dir_exists(updates_dir)
            
            note_filename = f"{timestamp}-{status}.md"
            note_path = updates_dir / note_filename
            
            note_content = f"""# Status Update: {status}
**Date**: {application.status_updated_at.strftime('%B %d, %Y %I:%M %p EST')}

## Notes
{notes}
"""
            write_text_file(note_content, note_path)
        
        # Update metadata
        self._save_application_metadata(application)
    
    def get_application_updates(self, application: Application) -> List[dict]:
        """Get all status updates for an application"""
        updates = []
        updates_dir = application.folder_path / "updates"
        
        if not updates_dir.exists():
            return updates
        
        for update_file in sorted(updates_dir.iterdir()):
            if update_file.is_file() and update_file.suffix == '.md':
                content = read_text_file(update_file)
                # Extract timestamp from filename
                timestamp_str = update_file.stem.split('-')[0]
                status = '-'.join(update_file.stem.split('-')[1:])
                
                updates.append({
                    'timestamp': timestamp_str,
                    'status': status,
                    'content': content,
                    'file': str(update_file)
                })
        
        return updates

