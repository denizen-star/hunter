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
        
        # Always create status update file (even without notes)
        timestamp = format_datetime_for_filename()
        updates_dir = application.folder_path / "updates"
        ensure_dir_exists(updates_dir)
        
        # Create HTML status update file
        status_filename = f"{timestamp}-{status}.html"
        status_path = updates_dir / status_filename
        
        # Format the timestamp for display
        display_timestamp = application.status_updated_at.strftime('%B %d, %Y %I:%M %p EST')
        
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Status Update: {status} - {application.company}</title>
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
            margin-bottom: 30px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .status-pending {{ background-color: #fff3cd; color: #856404; }}
        .status-applied {{ background-color: #d1ecf1; color: #0c5460; }}
        .status-contacted-someone {{ background-color: #d4edda; color: #155724; }}
        .status-contacted-hiring-manager {{ background-color: #cce5ff; color: #004085; }}
        .status-interviewed {{ background-color: #f8d7da; color: #721c24; }}
        .status-offered {{ background-color: #d1ecf1; color: #0c5460; }}
        .status-rejected {{ background-color: #f8d7da; color: #721c24; }}
        .status-accepted {{ background-color: #d4edda; color: #155724; }}
        .timestamp {{
            color: #6c757d;
            font-size: 14px;
            margin-top: 10px;
        }}
        .notes-section {{
            margin-top: 20px;
        }}
        .notes-content {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
            white-space: pre-wrap;
        }}
        .no-notes {{
            color: #6c757d;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }}
        .application-info {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #007bff;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../{application.folder_path.name}-Summary-{application.company}-{application.job_title}.html" class="back-link">← Back to Application Summary</a>
        
        <div class="header">
            <h1>Status Update: {status}</h1>
            <span class="status-badge status-{status.lower().replace(' ', '-')}">{status}</span>
            <div class="timestamp">{display_timestamp}</div>
        </div>
        
        <div class="application-info">
            <strong>Application:</strong> {application.company} - {application.job_title}<br>
            <strong>Application ID:</strong> {application.id}
        </div>
        
        <div class="notes-section">
            <h3>Update Details</h3>
            {f'<div class="notes-content">{notes}</div>' if notes else '<div class="no-notes">No additional notes provided for this status update.</div>'}
        </div>
    </div>
</body>
</html>"""
        
        write_text_file(html_content, status_path)
        
        # Update metadata
        self._save_application_metadata(application)
    
    def get_application_updates(self, application: Application) -> List[dict]:
        """Get all status updates for an application"""
        updates = []
        updates_dir = application.folder_path / "updates"
        
        if not updates_dir.exists():
            return updates
        
        for update_file in sorted(updates_dir.iterdir()):
            if update_file.is_file() and update_file.suffix == '.html':
                # Extract timestamp and status from filename
                # Format: YYYYMMDDHHMMSS-Status.html
                filename_parts = update_file.stem.split('-', 1)
                if len(filename_parts) == 2:
                    timestamp_str = filename_parts[0]
                    status = filename_parts[1]
                    
                    # Format timestamp for display
                    try:
                        # Convert filename timestamp to datetime
                        from datetime import datetime
                        dt = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                        display_timestamp = dt.strftime('%B %d, %Y %I:%M %p EST')
                    except:
                        display_timestamp = timestamp_str
                    
                    updates.append({
                        'timestamp': timestamp_str,
                        'display_timestamp': display_timestamp,
                        'status': status,
                        'file': str(update_file),
                        'relative_url': f"/applications/{application.folder_path.name}/updates/{update_file.name}"
                    })
        
        return updates

