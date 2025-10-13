"""Document generation service"""
from pathlib import Path
from app.models.application import Application
from app.models.qualification import QualificationAnalysis
from app.services.resume_manager import ResumeManager
from app.services.ai_analyzer import AIAnalyzer
from app.utils.file_utils import write_text_file, read_text_file
from app.utils.datetime_utils import format_datetime_for_filename, format_for_display


class DocumentGenerator:
    """Generates and saves all required documents"""
    
    def __init__(self):
        self.resume_manager = ResumeManager()
        self.ai_analyzer = AIAnalyzer()
    
    def generate_all_documents(self, application: Application) -> None:
        """Generate all documents for an application"""
        print(f"Generating documents for {application.company} - {application.job_title}...")
        
        # Load resume and job description
        resume = self.resume_manager.get_resume_for_job(application)
        job_description = read_text_file(application.job_description_path)
        
        # 1. Generate qualifications analysis (with feature extraction)
        print("  → Analyzing qualifications and extracting features...")
        qualifications = self.generate_qualifications(
            application, job_description, resume.content
        )
        
        # 2. Generate cover letter
        print("  → Generating cover letter...")
        self.generate_cover_letter(application, qualifications, resume.full_name)
        
        # 3. Generate customized resume
        print("  → Generating customized resume...")
        self.generate_custom_resume(application, qualifications, resume.content)
        
        # 4. Generate summary HTML page
        print("  → Generating summary page...")
        self.generate_summary_page(application, qualifications)
        
        print("  ✓ All documents generated successfully!")
    
    def generate_qualifications(
        self,
        application: Application,
        job_description: str,
        resume_content: str
    ) -> QualificationAnalysis:
        """Generate qualifications analysis with feature extraction"""
        # Get analysis from AI
        qualifications = self.ai_analyzer.analyze_qualifications(
            job_description, resume_content
        )
        
        # Save to file
        job_title_clean = ''.join(c for c in application.job_title if c.isalnum() or c in ' -')
        job_title_clean = job_title_clean.replace(' ', '')
        
        qual_filename = f"{job_title_clean}-Qualifications.md"
        qual_path = application.folder_path / qual_filename
        
        write_text_file(qualifications.detailed_analysis, qual_path)
        application.qualifications_path = qual_path
        application.match_score = qualifications.match_score
        
        return qualifications
    
    def generate_cover_letter(
        self,
        application: Application,
        qualifications: QualificationAnalysis,
        candidate_name: str
    ) -> None:
        """Generate cover letter"""
        cover_letter = self.ai_analyzer.generate_cover_letter(
            qualifications,
            application.company,
            application.job_title,
            candidate_name
        )
        
        # Save to file
        name_clean = candidate_name.replace(' ', '')
        company_clean = application.company.replace(' ', '-')
        job_title_clean = application.job_title.replace(' ', '-')
        
        cover_letter_filename = f"{name_clean}-{company_clean}-{job_title_clean}-intro.md"
        cover_letter_path = application.folder_path / cover_letter_filename
        
        write_text_file(cover_letter, cover_letter_path)
        application.cover_letter_path = cover_letter_path
    
    def generate_custom_resume(
        self,
        application: Application,
        qualifications: QualificationAnalysis,
        original_resume: str
    ) -> None:
        """Generate customized resume"""
        custom_resume = self.ai_analyzer.rewrite_resume(
            original_resume, qualifications
        )
        
        # Save to file
        resume = self.resume_manager.load_base_resume()
        name_clean = resume.full_name.replace(' ', '')
        company_clean = application.company.replace(' ', '-')
        job_title_clean = application.job_title.replace(' ', '-')
        
        resume_filename = f"{name_clean}-{company_clean}-{job_title_clean}-Resume.md"
        resume_path = application.folder_path / resume_filename
        
        write_text_file(custom_resume, resume_path)
        application.custom_resume_path = resume_path
    
    def generate_summary_page(
        self,
        application: Application,
        qualifications: QualificationAnalysis
    ) -> None:
        """Generate HTML summary page for the application"""
        # Extract salary and location from job description
        job_description = read_text_file(application.job_description_path)
        job_details = self.ai_analyzer.extract_job_details(job_description)
        
        # Load all documents
        job_desc_content = read_text_file(application.job_description_path)
        qual_content = read_text_file(application.qualifications_path) if application.qualifications_path else ""
        cover_letter_content = read_text_file(application.cover_letter_path) if application.cover_letter_path else ""
        resume_content = read_text_file(application.custom_resume_path) if application.custom_resume_path else ""
        
        # Generate summary
        summary_html = self._create_summary_html(
            application,
            qualifications,
            job_details,
            job_desc_content,
            qual_content,
            cover_letter_content,
            resume_content
        )
        
        # Save summary
        timestamp = format_datetime_for_filename()
        company_clean = application.company.replace(' ', '-')
        job_title_clean = application.job_title.replace(' ', '-')
        
        summary_filename = f"{timestamp}-Summary-{company_clean}-{job_title_clean}.html"
        summary_path = application.folder_path / summary_filename
        
        write_text_file(summary_html, summary_path)
        application.summary_path = summary_path
    
    def _create_summary_html(
        self,
        application: Application,
        qualifications: QualificationAnalysis,
        job_details: dict,
        job_desc: str,
        qual_analysis: str,
        cover_letter: str,
        resume: str
    ) -> str:
        """Create HTML summary page"""
        match_score_color = self._get_match_score_color(qualifications.match_score)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{application.company} - {application.job_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px 12px 0 0; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header h2 {{ font-size: 24px; font-weight: normal; opacity: 0.9; }}
        .summary {{ padding: 30px 40px; border-bottom: 1px solid #e0e0e0; background: #fafafa; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
        .summary-item {{ background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .summary-item label {{ display: block; font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 5px; font-weight: 600; }}
        .summary-item value {{ display: block; font-size: 16px; color: #333; }}
        .match-score {{ font-size: 48px; font-weight: bold; color: {match_score_color}; text-align: center; padding: 20px; background: white; border-radius: 8px; }}
        .status-badge {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 600; text-transform: capitalize; }}
        .status-pending {{ background: #fff3cd; color: #856404; }}
        .status-applied {{ background: #d1ecf1; color: #0c5460; }}
        .status-interviewed {{ background: #d4edda; color: #155724; }}
        .status-offered {{ background: #c3e6cb; color: #155724; }}
        .status-rejected {{ background: #f8d7da; color: #721c24; }}
        .tabs {{ display: flex; border-bottom: 2px solid #e0e0e0; padding: 0 40px; background: #fafafa; }}
        .tab {{ padding: 15px 25px; cursor: pointer; border: none; background: none; font-size: 16px; font-weight: 500; color: #666; transition: all 0.3s; }}
        .tab:hover {{ color: #667eea; }}
        .tab.active {{ color: #667eea; border-bottom: 3px solid #667eea; margin-bottom: -2px; }}
        .tab-content {{ padding: 40px; display: none; }}
        .tab-content.active {{ display: block; }}
        .tab-content pre {{ background: #f5f5f5; padding: 20px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }}
        .tab-content h3 {{ color: #667eea; margin-top: 20px; margin-bottom: 10px; }}
        a {{ color: #667eea; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .timeline {{ margin-top: 20px; }}
        .timeline-item {{ padding: 15px; border-left: 3px solid #667eea; margin-left: 10px; margin-bottom: 15px; background: #f9f9f9; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{application.company}</h1>
            <h2>{application.job_title}</h2>
        </div>
        
        <div class="summary">
            <h2 style="margin-bottom: 20px; color: #333;">Summary</h2>
            
            <div class="match-score">
                {qualifications.match_score:.0f}% Match
            </div>
            
            <div class="summary-grid">
                <div class="summary-item">
                    <label>Status</label>
                    <value><span class="status-badge status-{application.status}">{application.status}</span></value>
                </div>
                <div class="summary-item">
                    <label>Salary Range</label>
                    <value>{job_details.get('salary_range', '$0')}</value>
                </div>
                <div class="summary-item">
                    <label>Location</label>
                    <value>{job_details.get('location', 'N/A')}</value>
                </div>
                <div class="summary-item">
                    <label>Hiring Manager</label>
                    <value>{job_details.get('hiring_manager', 'N/A')}</value>
                </div>
                <div class="summary-item">
                    <label>Applied</label>
                    <value>{format_for_display(application.created_at)}</value>
                </div>
                <div class="summary-item">
                    <label>Last Updated</label>
                    <value>{format_for_display(application.status_updated_at)}</value>
                </div>
            </div>
            
            {f'<div style="margin-top: 20px;"><label style="display: block; font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 5px; font-weight: 600;">Job URL</label><a href="{application.job_url}" target="_blank">{application.job_url}</a></div>' if application.job_url else ''}
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab(event, 'job-desc')">Job Description</button>
            <button class="tab" onclick="showTab(event, 'qualifications')">Qualifications Analysis</button>
            <button class="tab" onclick="showTab(event, 'cover-letter')">Cover Letter</button>
            <button class="tab" onclick="showTab(event, 'resume')">Customized Resume</button>
            <button class="tab" onclick="showTab(event, 'updates')">Updates & Notes</button>
        </div>
        
        <div id="job-desc" class="tab-content active">
            <h2>Job Description</h2>
            <pre>{job_desc}</pre>
        </div>
        
        <div id="qualifications" class="tab-content">
            <h2>Qualifications Analysis</h2>
            <pre>{qual_analysis}</pre>
        </div>
        
        <div id="cover-letter" class="tab-content">
            <h2>Cover Letter</h2>
            <pre>{cover_letter}</pre>
        </div>
        
        <div id="resume" class="tab-content">
            <h2>Customized Resume</h2>
            <pre>{resume}</pre>
        </div>
        
        <div id="updates" class="tab-content">
            <h2>Updates & Notes</h2>
            <div class="timeline">
                <div class="timeline-item">
                    <strong>{format_for_display(application.created_at)}</strong> - Application Created
                </div>
                {self._generate_updates_timeline(application)}
            </div>
        </div>
    </div>
    
    <script>
        function showTab(event, tabId) {{
            // Hide all tab contents
            var contents = document.getElementsByClassName('tab-content');
            for (var i = 0; i < contents.length; i++) {{
                contents[i].classList.remove('active');
            }}
            
            // Remove active class from all tabs
            var tabs = document.getElementsByClassName('tab');
            for (var i = 0; i < tabs.length; i++) {{
                tabs[i].classList.remove('active');
            }}
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }}
    </script>
</body>
</html>"""
        return html
    
    def _generate_updates_timeline(self, application: Application) -> str:
        """Generate HTML for status updates timeline"""
        from app.services.job_processor import JobProcessor
        
        job_processor = JobProcessor()
        updates = job_processor.get_application_updates(application)
        
        if not updates:
            return ""
        
        timeline_html = ""
        for update in reversed(updates):  # Show newest first
            timeline_html += f"""
                <div class="timeline-item">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 8px;">
                        <strong style="color: #667eea;">{update['status']}</strong>
                        <span style="color: #666; font-size: 14px;">{update['display_timestamp']}</span>
                    </div>
                    <a href="{update['relative_url']}" target="_blank" style="color: #667eea; text-decoration: none; font-size: 14px;">
                        View Details →
                    </a>
                </div>"""
        
        return timeline_html
    
    def _get_match_score_color(self, score: float) -> str:
        """Get color based on match score"""
        if score >= 80:
            return '#10b981'  # Green
        elif score >= 60:
            return '#f59e0b'  # Orange
        else:
            return '#ef4444'  # Red

