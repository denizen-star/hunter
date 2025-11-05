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
from app.services.ai_analyzer import AIAnalyzer


class JobProcessor:
    """Processes job descriptions and creates application folders"""
    
    def __init__(self):
        self.applications_dir = get_data_path('applications')
        ensure_dir_exists(self.applications_dir)
        self.ai_analyzer = AIAnalyzer()
    
    def _clean_job_description(self, job_description: str) -> str:
        """Remove LinkedIn metadata and clutter from job descriptions"""
        lines = job_description.split('\n')
        cleaned_lines = []
        
        # Skip LinkedIn metadata patterns
        skip_patterns = [
            'Skip to main content',
            'LinkedIn',
            'Jobs',
            'Clear text',
            'Sign in',
            'Join now',
            'Apply',
            'Save',
            'Use AI to assess',
            'Get AI-powered advice',
            'Am I a good fit',
            'Tailor my resume',
            'See who',
            'has hired for this role',
            'applicants',
            'days ago',
            'weeks ago',
            'months ago',
            'years ago',
            'More searches',
            'Explore collaborative articles',
            'Explore More',
            'Show less',
            'Show more',
            'Similar jobs',
            'People also viewed',
            'Similar Searches',
            'Open jobs',
            'Show less',
            'Show more'
        ]
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip lines that match skip patterns
            should_skip = False
            for pattern in skip_patterns:
                if pattern.lower() in line.lower():
                    should_skip = True
                    break
            
            # Skip lines that are just navigation elements
            if line in ['', ' ', '|', '-', '•']:
                should_skip = True
                
            # Skip lines that are very short (likely navigation elements)
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
        
        # Join back and clean up multiple newlines
        cleaned = '\n'.join(final_lines)
        cleaned = '\n'.join([line for line in cleaned.split('\n') if line.strip()])
        
        return cleaned

    def create_job_application(
        self,
        company: str,
        job_title: str,
        job_description: str,
        job_url: Optional[str] = None
    ) -> Application:
        """Create a new job application"""
        # Store raw job description for date extraction
        raw_job_description = job_description
        
        # Clean the job description to remove LinkedIn metadata
        cleaned_job_description = self._clean_job_description(job_description)
        
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
        
        # Save raw job description (original input)
        raw_job_desc_filename = f"{timestamp}-{company}-{job_title}-raw.txt"
        raw_job_desc_path = folder_path / raw_job_desc_filename
        write_text_file(raw_job_description, raw_job_desc_path)
        application.raw_job_description_path = raw_job_desc_path
        
        # Parallelize AI calls: extract comprehensive job details and extract job details
        print("  → Extracting job details (parallel AI calls)...")
        from concurrent.futures import ThreadPoolExecutor
        
        def extract_comprehensive():
            try:
                return self.ai_analyzer.extract_comprehensive_job_details(
                    cleaned_job_description, 
                    raw_job_description
                )
            except Exception as e:
                print(f"  ⚠ Warning: Could not extract structured job details: {e}")
                return cleaned_job_description
        
        def extract_details():
            try:
                return self.ai_analyzer.extract_job_details(raw_job_description)
            except Exception as e:
                print(f"  ⚠ Warning: Could not extract job details: {e}")
                return {
                    'posted_date': 'N/A',
                    'salary_range': 'N/A',
                    'location': 'N/A',
                    'hiring_manager': 'N/A'
                }
        
        structured_job_description = cleaned_job_description
        job_details = {
            'posted_date': 'N/A',
            'salary_range': 'N/A',
            'location': 'N/A',
            'hiring_manager': 'N/A'
        }
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            comprehensive_future = executor.submit(extract_comprehensive)
            details_future = executor.submit(extract_details)
            
            # Wait for both to complete
            structured_job_description = comprehensive_future.result()
            job_details = details_future.result()
        
        # Save structured job description
        job_desc_filename = f"{timestamp}-{company}-{job_title}.md"
        job_desc_path = folder_path / job_desc_filename
        write_text_file(structured_job_description, job_desc_path)
        application.job_description_path = job_desc_path
        
        # Set job details from parallel extraction
        application.posted_date = job_details.get('posted_date', 'N/A')
        application.salary_range = job_details.get('salary_range', 'N/A')
        application.location = job_details.get('location', 'N/A')
        application.hiring_manager = job_details.get('hiring_manager', 'N/A')
        print(f"  ✓ Posted date: {application.posted_date}")
        print(f"  ✓ Salary range: {application.salary_range}")
        print(f"  ✓ Location: {application.location}")
        print(f"  ✓ Hiring manager: {application.hiring_manager}")
        
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
                        # Calculate and set contact count
                        application.contact_count = application.calculate_contact_count()
                        applications.append(application)
                    except Exception as e:
                        print(f"Error loading application from {folder_path}: {e}")
        
        # Sort by created_at descending
        applications.sort(key=lambda x: x.created_at, reverse=True)
        return applications
    
    def get_application_by_id(self, app_id: str) -> Optional[Application]:
        """Get an application by ID"""
        applications = self.list_all_applications()
        application = next((app for app in applications if app.id == app_id), None)
        if application:
            # Ensure contact count is calculated
            application.contact_count = application.calculate_contact_count()
        return application
    
    def update_application_status(
        self,
        application: Application,
        status: str,
        notes: Optional[str] = None
    ) -> None:
        """Update application status with optional notes"""
        application.status = status
        application.status_updated_at = get_est_now()
        
        # If status is rejected, clean up unnecessary files
        if status.lower() == 'rejected':
            self._cleanup_rejected_application_files(application)
        
        # Always create status update file (even without notes)
        timestamp = format_datetime_for_filename()
        updates_dir = application.folder_path / "updates"
        ensure_dir_exists(updates_dir)
        
        # Create HTML status update file
        status_filename = f"{timestamp}-{status}.html"
        status_path = updates_dir / status_filename
        
        # Format the timestamp for display
        display_timestamp = application.status_updated_at.strftime('%B %d, %Y %I:%M %p EST')
        
        # Create HTML content (notes are now HTML formatted from rich text editor)
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
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 4px solid #28a745;
        }}
        .application-info h3 {{
            color: #28a745;
            font-size: 18px;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        .info-content {{
            display: grid;
            gap: 8px;
        }}
        .info-item {{
            font-size: 14px;
            color: #333;
        }}
        .info-item strong {{
            color: #555;
            font-weight: 600;
        }}
        .update-info {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #2196f3;
        }}
        .update-item {{
            font-size: 14px;
            color: #333;
            margin-bottom: 5px;
        }}
        .update-item strong {{
            color: #1976d2;
            font-weight: 600;
        }}
        .notes-content h4 {{
            color: #ff9800;
            font-size: 16px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .notes-text {{
            background-color: #fff3e0;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #ff9800;
            font-size: 14px;
            line-height: 1.6;
        }}
        .notes-text p {{
            margin: 0 0 10px 0;
        }}
        .notes-text p:last-child {{
            margin-bottom: 0;
        }}
        .notes-text ul, .notes-text ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .notes-text blockquote {{
            margin: 10px 0;
            padding: 10px 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }}
        .notes-text code {{
            background-color: #f1f3f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        .notes-text pre {{
            background-color: #f1f3f4;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        .notes-text a {{
            color: #007bff;
            text-decoration: none;
        }}
        .notes-text a:hover {{
            text-decoration: underline;
        }}
        .notes-text img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
            <h3>📋 Application Information</h3>
            <div class="info-content">
                <div class="info-item">
                    <strong>Company:</strong> {application.company}
                </div>
                <div class="info-item">
                    <strong>Position:</strong> {application.job_title}
                </div>
                <div class="info-item">
                    <strong>Application ID:</strong> {application.id}
                </div>
                <div class="info-item">
                    <strong>Current Status:</strong> <span class="status-badge status-{status.lower().replace(' ', '-')}">{status}</span>
                </div>
            </div>
        </div>
        
        <div class="notes-section">
            <h3>📝 Status Update Details</h3>
            <div class="update-info">
                <div class="update-item">
                    <strong>Status Change:</strong> {status}
                </div>
                <div class="update-item">
                    <strong>Updated On:</strong> {display_timestamp}
                </div>
            </div>
            {f'<div class="notes-content"><h4>📋 Additional Notes</h4><div class="notes-text">{notes}</div></div>' if notes else '<div class="no-notes">No additional notes provided for this status update.</div>'}
        </div>
    </div>
</body>
</html>"""
        
        write_text_file(html_content, status_path)
        
        # Recalculate contact count after status update
        application.contact_count = application.calculate_contact_count()
        
        # Update metadata
        self._save_application_metadata(application)
        
        # Regenerate summary to include the new update
        self._regenerate_summary(application)
    
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
    
    def update_job_details(
        self,
        application: Application,
        salary_range: Optional[str] = None,
        location: Optional[str] = None,
        hiring_manager: Optional[str] = None
    ) -> None:
        """Update job details for an application"""
        updated = False
        
        if salary_range is not None:
            application.salary_range = salary_range
            updated = True
            
        if location is not None:
            application.location = location
            updated = True
            
        if hiring_manager is not None:
            application.hiring_manager = hiring_manager
            updated = True
        
        if updated:
            # Update the status_updated_at timestamp
            application.status_updated_at = get_est_now()
            
        # Recalculate contact count after status update
        application.contact_count = application.calculate_contact_count()
        
        # Save updated metadata
        self._save_application_metadata(application)
        
        if updated:
            # Regenerate summary to reflect changes
            self._regenerate_summary(application)
            
            print(f"  ✓ Job details updated for {application.company} - {application.job_title}")

    def _regenerate_summary(self, application: Application) -> None:
        """Regenerate summary HTML with updated status and timeline"""
        try:
            from app.services.document_generator import DocumentGenerator
            from app.models.qualification import QualificationAnalysis
            
            # Load qualifications from file
            if not application.qualifications_path or not application.qualifications_path.exists():
                print("Warning: Cannot regenerate summary - qualifications file not found")
                return
            
            qual_content = read_text_file(application.qualifications_path)
            
            # Parse match score from qualifications file
            match_score = application.match_score if application.match_score else 0.0
            
            # Create a basic QualificationAnalysis object
            qualifications = QualificationAnalysis(
                match_score=match_score,
                features_compared=0,
                strong_matches=[],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis=qual_content
            )
            
            # Regenerate summary
            doc_generator = DocumentGenerator()
            doc_generator.generate_summary_page(application, qualifications)
            
            print(f"  ✓ Summary regenerated with latest updates")
            
        except Exception as e:
            print(f"Warning: Could not regenerate summary: {e}")

    def _cleanup_rejected_application_files(self, application: Application) -> None:
        """Clean up files for rejected applications, keeping only essential files"""
        if not application.folder_path or not application.folder_path.exists():
            return
        
        print(f"  → Cleaning up files for rejected application: {application.company} - {application.job_title}")
        
        # Files to delete for rejected applications
        files_to_delete = []
        
        # Raw Entry Tab files
        if application.raw_job_description_path and application.raw_job_description_path.exists():
            files_to_delete.append(application.raw_job_description_path)
        
        # Research Tab files
        if application.hiring_manager_intros_path and application.hiring_manager_intros_path.exists():
            files_to_delete.append(application.hiring_manager_intros_path)
        if application.recruiter_intros_path and application.recruiter_intros_path.exists():
            files_to_delete.append(application.recruiter_intros_path)
        if application.research_path and application.research_path.exists():
            files_to_delete.append(application.research_path)
        
        # Qualifications Analysis Tab files
        if application.qualifications_path and application.qualifications_path.exists():
            files_to_delete.append(application.qualifications_path)
        
        # Cover Letter Tab files
        if application.cover_letter_path and application.cover_letter_path.exists():
            files_to_delete.append(application.cover_letter_path)
        
        # Customized Resume Tab files
        if application.custom_resume_path and application.custom_resume_path.exists():
            files_to_delete.append(application.custom_resume_path)
        
        # Summary Tab files
        if application.summary_path and application.summary_path.exists():
            files_to_delete.append(application.summary_path)
        
        # Also look for any additional files that match patterns
        folder_path = application.folder_path
        for file_path in folder_path.iterdir():
            if file_path.is_file():
                filename = file_path.name.lower()
                # Delete files that match patterns for tabs we want to remove
                if any(pattern in filename for pattern in [
                    '-qualifications.md',
                    '-cover-letter.html',
                    '-resume.md',
                    '-summary-',
                    '-hiring-manager-intros.md',
                    '-recruiter-intros.md',
                    '-intro.md',
                    '-raw.txt'
                ]):
                    if file_path not in files_to_delete:
                        files_to_delete.append(file_path)
        
        # Delete the identified files
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1
                    print(f"    ✓ Deleted: {file_path.name}")
            except Exception as e:
                print(f"    ⚠ Could not delete {file_path.name}: {e}")
        
        # Clear the file paths from application metadata
        application.raw_job_description_path = None
        application.hiring_manager_intros_path = None
        application.recruiter_intros_path = None
        application.research_path = None
        application.qualifications_path = None
        application.cover_letter_path = None
        application.custom_resume_path = None
        application.summary_path = None
        
        # Save updated metadata
        self._save_application_metadata(application)
        
        # Regenerate summary page with remaining content
        print(f"  → Regenerating summary page with remaining content...")
        try:
            from app.services.document_generator import DocumentGenerator
            from app.models.qualification import QualificationAnalysis
            
            # Create a minimal QualificationAnalysis object for rejected applications
            qualifications = QualificationAnalysis(
                match_score=0.0,  # No match score for rejected apps
                features_compared=0,
                strong_matches=[],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis="Application was rejected - detailed analysis removed during cleanup."
            )
            
            # Generate new summary page
            doc_generator = DocumentGenerator()
            doc_generator.generate_summary_page(application, qualifications)
            
            # Save updated metadata with new summary path
            self._save_application_metadata(application)
            
            print(f"    ✓ Summary page regenerated")
        except Exception as e:
            print(f"    ⚠ Warning: Could not regenerate summary page: {e}")
        
        print(f"  ✓ Cleanup complete: {deleted_count} files deleted")
        print(f"  ✓ Kept essential files: job description, application metadata, and updates")
        print(f"  ✓ Summary page regenerated with remaining content")

