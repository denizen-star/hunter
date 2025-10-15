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
        try:
            # Use stored job details from application.yaml instead of re-extracting
            job_details = {
                'salary_range': application.salary_range or 'N/A',
                'location': application.location or 'N/A', 
                'hiring_manager': application.hiring_manager or 'N/A',
                'posted_date': application.posted_date or 'N/A'
            }
            
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
            
            # Save summary - reuse existing file if it exists, otherwise create new one
            if application.summary_path and Path(application.summary_path).exists():
                # Update existing summary file
                summary_path = Path(application.summary_path)
                print(f"✓ Updating existing summary page: {summary_path.name}")
            else:
                # Create new summary file with timestamp
                timestamp = format_datetime_for_filename()
                company_clean = application.company.replace(' ', '-')
                job_title_clean = application.job_title.replace(' ', '-')
                
                summary_filename = f"{timestamp}-Summary-{company_clean}-{job_title_clean}.html"
                summary_path = application.folder_path / summary_filename
                print(f"✓ Creating new summary page: {summary_filename}")
            
            write_text_file(summary_html, summary_path)
            application.summary_path = summary_path
            
        except Exception as e:
            print(f"✗ Error generating summary page: {e}")
            raise
    
    def _parse_job_description_markdown(self, job_desc: str) -> str:
        """Parse structured job description markdown and convert to formatted HTML"""
        import re
        
        # Convert markdown to HTML with custom styling for job description
        html_parts = []
        
        # Split by headers
        lines = job_desc.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check for headers
            if line.startswith('# '):
                if current_section and current_content:
                    html_parts.append(self._format_job_section(current_section, '\n'.join(current_content)))
                current_section = line[2:].strip()
                current_content = []
            elif line.startswith('## '):
                if current_section and current_content:
                    html_parts.append(self._format_job_section(current_section, '\n'.join(current_content)))
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_section and current_content:
            html_parts.append(self._format_job_section(current_section, '\n'.join(current_content)))
        
        return '\n'.join(html_parts)
    
    def _format_job_section(self, title: str, content: str) -> str:
        """Format a job description section with appropriate styling"""
        import re
        
        content = content.strip()
        if not content or content == '---':
            return ''
        
        # Extract section number if present (e.g., "1. Job Title" -> "Job Title")
        title_clean = re.sub(r'^\d+\.\s*', '', title)
        
        # Format content - handle markdown bold formatting
        formatted_content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
        
        # Handle bullet points
        if '- ' in formatted_content or '* ' in formatted_content:
            lines = formatted_content.split('\n')
            ul_items = []
            regular_text = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    ul_items.append(f'<li>{line[2:]}</li>')
                elif line:
                    regular_text.append(line)
            
            formatted_content = ''
            if regular_text:
                formatted_content += '<p>' + '<br>'.join(regular_text) + '</p>'
            if ul_items:
                formatted_content += '<ul>' + ''.join(ul_items) + '</ul>'
        else:
            # Replace double newlines with paragraph breaks
            paragraphs = formatted_content.split('\n\n')
            formatted_content = '<p>' + '</p><p>'.join(p.replace('\n', '<br>') for p in paragraphs if p.strip()) + '</p>'
        
        # Special styling for certain sections
        if 'Posted Date' in title or title_clean == 'Job Description Details':
            return f'<div class="job-meta">{formatted_content}</div>'
        
        # Skip sections if content is "Not available"
        if title_clean in ['Additional Insights', 'Hiring Team Information'] and ('Not available' in formatted_content or 'Not specified' in formatted_content):
            return ''
        
        # Special formatting for Additional Insights section (use standard styling)
        if 'Additional Insights' in title_clean:
            return f'''
        <div class="job-section">
            <h3 class="job-section-title">📊 {title_clean}</h3>
            <div class="job-section-content">
                {formatted_content}
            </div>
        </div>
        '''
        
        # Special formatting for Hiring Team Information section (use standard styling)
        if 'Hiring Team Information' in title_clean:
            # Parse and format hiring team information
            formatted_team_info = self._format_hiring_team_info(formatted_content)
            return f'''
        <div class="job-section">
            <h3 class="job-section-title">👥 {title_clean}</h3>
            <div class="job-section-content">
                {formatted_team_info}
            </div>
        </div>
        '''
        
        return f'''
        <div class="job-section">
            <h3 class="job-section-title">{title_clean}</h3>
            <div class="job-section-content">
                {formatted_content}
            </div>
        </div>
        '''
    
    def _extract_technologies_from_qual_analysis(self, qual_analysis: str) -> dict:
        """Extract technologies from qualification analysis using the actual format"""
        import re
        
        technologies = {
            'matched': [],
            'missing': [],
            'partial': []
        }
        
        # Find the Technologies & Tools section - include Critical Missing Technologies too
        tech_section_match = re.search(
            r'\*\*Technologies & Tools\*\*.*?(?=\*\*Soft Skills\*\*|\*\*Recommendations\*\*|\Z)',
            qual_analysis,
            re.DOTALL
        )
        
        if not tech_section_match:
            return technologies
        
        tech_section = tech_section_match.group(0)
        
        # Parse the new format: "- Technology: ✓" or "- Technology: ✗"
        # Look for patterns like "- Python: ✓" or "- MySQL: ✗"
        lines = tech_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('**') or line.startswith('|'):
                continue
            
            # Match pattern: "- Technology: ✓" or "* Technology: ✓ MATCHED"
            # Try both formats
            match = re.search(r'[-*]\s+([^:]+):\s*([✓✗⚠])', line)
            if match:
                tech_name = match.group(1).strip()
                symbol = match.group(2).strip()
                
                # Also check for MATCHED/MISSING/PARTIAL keywords
                if 'MATCHED' in line or symbol == '✓':
                    technologies['matched'].append(tech_name)
                elif 'MISSING' in line or symbol == '✗':
                    technologies['missing'].append(tech_name)
                elif 'PARTIAL' in line or symbol == '⚠':
                    technologies['partial'].append(tech_name)
        
        return technologies
    
    def _generate_tech_pills_html(self, technologies: dict) -> str:
        """Generate HTML for technology pills"""
        html_parts = []
        
        # Matched Technologies (Green Pills)
        if technologies.get('matched'):
            html_parts.append('<div class="tech-pills-section">')
            html_parts.append('<div class="tech-pills-label">✅ Matched Technologies (Found in Resume)</div>')
            html_parts.append('<div class="tech-pills">')
            for tech in technologies['matched']:
                html_parts.append(f'<span class="tech-pill tech-pill-green">{tech}</span>')
            html_parts.append('</div>')
            html_parts.append('</div>')
        
        # Partial Match Technologies (Yellow Pills)
        if technologies.get('partial'):
            html_parts.append('<div class="tech-pills-section">')
            html_parts.append('<div class="tech-pills-label">⚠️ Partial Match (Inferred/Related Experience)</div>')
            html_parts.append('<div class="tech-pills">')
            for tech in technologies['partial']:
                html_parts.append(f'<span class="tech-pill tech-pill-yellow">{tech}</span>')
            html_parts.append('</div>')
            html_parts.append('</div>')
        
        # Missing Technologies (Red Pills)
        if technologies.get('missing'):
            html_parts.append('<div class="tech-pills-section">')
            html_parts.append('<div class="tech-pills-label">❌ Missing Technologies (Not Found in Resume)</div>')
            html_parts.append('<div class="tech-pills">')
            for tech in technologies['missing']:
                html_parts.append(f'<span class="tech-pill tech-pill-red">{tech}</span>')
            html_parts.append('</div>')
            html_parts.append('</div>')
        
        # If no technologies found
        if not technologies.get('matched') and not technologies.get('missing') and not technologies.get('partial'):
            html_parts.append('<div style="color: #999; font-style: italic;">No specific technologies mentioned in job description.</div>')
        
        return '\n'.join(html_parts)
    
    def _generate_strong_matches_html(self, strong_matches: list) -> str:
        """Generate HTML for strong matches pills"""
        if not strong_matches:
            return '<span style="color: #999; font-style: italic;">No strong matches identified</span>'
        
        html_parts = []
        for match in strong_matches[:5]:  # Limit to top 5
            match_clean = match.strip()
            if match_clean:
                html_parts.append(
                    f'<span style="display: inline-block; background: #d4edda; color: #666; padding: 2px 6px; border-radius: 8px; font-size: 10px; margin: 1px; border: 1px solid #c3e6cb; box-shadow: none;">{match_clean}</span>'
                )
        
        return ''.join(html_parts)
    
    def _generate_missing_skills_html(self, missing_skills: list) -> str:
        """Generate HTML for missing skills pills"""
        if not missing_skills:
            return '<span style="color: #28a745; font-weight: 600;">No missing skills identified!</span>'
        
        html_parts = []
        for skill in missing_skills[:5]:  # Limit to top 5
            skill_clean = skill.strip()
            if skill_clean:
                html_parts.append(
                    f'<span style="display: inline-block; background: #f8d7da; color: #666; padding: 2px 6px; border-radius: 8px; font-size: 10px; margin: 1px; border: 1px solid #f5c6cb; box-shadow: none;">{skill_clean}</span>'
                )
        
        return ''.join(html_parts)
    
    def _format_hiring_team_info(self, content: str) -> str:
        """Format hiring team information into structured display"""
        import re
        
        # Look for the pattern: Name | Position at Company | Connection: X degree | Role: Y
        team_members = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.lower() in ['not available', 'not specified']:
                continue
                
            # Check if line contains hiring team info
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    name = parts[0]
                    position = parts[1] if len(parts) > 1 else ""
                    connection = parts[2] if len(parts) > 2 else ""
                    role = parts[3] if len(parts) > 3 else ""
                    
                    # Extract connection degree
                    degree_match = re.search(r'(\d+)(st|nd|rd|th)', connection, re.IGNORECASE)
                    degree = degree_match.group(0) if degree_match else ""
                    
                    # Extract role
                    role_match = re.search(r'Role:\s*([^|]+)', role, re.IGNORECASE)
                    role_text = role_match.group(1).strip() if role_match else role.strip()
                    
                    team_members.append({
                        'name': name,
                        'position': position,
                        'degree': degree,
                        'role': role_text
                    })
        
        if not team_members:
            return content  # Return original if no structured data found
        
        # Format as cards
        html_parts = []
        for member in team_members:
            degree_color = "#10b981" if member['degree'] in ['1st', '2nd'] else "#f59e0b"
            role_color = "#3b82f6" if member['role'].lower() == 'job poster' else "#6366f1"
            
            html_parts.append(f'''
            <div style="display: flex; align-items: center; gap: 15px; padding: 12px; background: white; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #1f2937; font-size: 16px;">{member['name']}</div>
                    <div style="color: #6b7280; font-size: 14px; margin-top: 2px;">{member['position']}</div>
                </div>
                <div style="display: flex; gap: 10px; align-items: center;">
                    {f'<span style="background: {degree_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{member["degree"]}</span>' if member['degree'] else ''}
                    {f'<span style="background: {role_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600;">{member["role"]}</span>' if member['role'] else ''}
                </div>
            </div>
            ''')
        
        return ''.join(html_parts)
    
    def _generate_technologies_section_html(self, technologies: dict) -> str:
        """Generate Technologies section HTML using the same format as other sections"""
        if not technologies.get('matched') and not technologies.get('missing') and not technologies.get('partial'):
            # If no technologies are found, show a message indicating no specific technologies mentioned
            return '''
        <div class="job-section">
            <h3 class="job-section-title">💻 Technologies & Skills Match</h3>
            <div class="job-section-content">
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                    <p style="margin: 0; color: #666; font-style: italic;">
                        <strong>No specific technologies mentioned in job description.</strong><br>
                        This job focuses on analytical skills and business intelligence rather than specific technical tools.
                    </p>
                </div>
            </div>
        </div>
        '''
        
        # Create content for the section
        content_parts = []
        
        # Add matched technologies
        if technologies.get('matched'):
            content_parts.append('<div class="tech-pills-section">')
            content_parts.append('<div class="tech-pills-label">✅ Matched Technologies (Found in Resume)</div>')
            content_parts.append('<div class="tech-pills">')
            for tech in technologies['matched']:
                content_parts.append(f'<span class="tech-pill tech-pill-green">{tech}</span>')
            content_parts.append('</div>')
            content_parts.append('</div>')
        
        # Add partial match technologies
        if technologies.get('partial'):
            content_parts.append('<div class="tech-pills-section">')
            content_parts.append('<div class="tech-pills-label">⚠️ Partial Match (Inferred/Related Experience)</div>')
            content_parts.append('<div class="tech-pills">')
            for tech in technologies['partial']:
                content_parts.append(f'<span class="tech-pill tech-pill-yellow">{tech}</span>')
            content_parts.append('</div>')
            content_parts.append('</div>')
        
        # Add missing technologies
        if technologies.get('missing'):
            content_parts.append('<div class="tech-pills-section">')
            content_parts.append('<div class="tech-pills-label">❌ Missing Technologies (Not Found in Resume)</div>')
            content_parts.append('<div class="tech-pills">')
            for tech in technologies['missing']:
                content_parts.append(f'<span class="tech-pill tech-pill-red">{tech}</span>')
            content_parts.append('</div>')
            content_parts.append('</div>')
        
        # Add legend
        content_parts.append('<div class="tech-legend">')
        content_parts.append('<div class="tech-legend-item">')
        content_parts.append('<div class="tech-legend-dot" style="background: #d4edda; border: 1px solid #c3e6cb;"></div>')
        content_parts.append('<span>✅ Match (Found in Resume)</span>')
        content_parts.append('</div>')
        content_parts.append('<div class="tech-legend-item">')
        content_parts.append('<div class="tech-legend-dot" style="background: #fff3cd; border: 1px solid #ffeaa7;"></div>')
        content_parts.append('<span>⚠️ Partial (Inferred/Related)</span>')
        content_parts.append('</div>')
        content_parts.append('<div class="tech-legend-item">')
        content_parts.append('<div class="tech-legend-dot" style="background: #f8d7da; border: 1px solid #f5c6cb;"></div>')
        content_parts.append('<span>❌ Missing (Not in Resume)</span>')
        content_parts.append('</div>')
        content_parts.append('</div>')
        
        formatted_content = '\n'.join(content_parts)
        
        # Use the same format as other sections
        return f'''
        <div class="job-section">
            <h3 class="job-section-title">💻 Technologies & Skills Match</h3>
            <div class="job-section-content">
                {formatted_content}
            </div>
        </div>
        '''
    
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
        
        # Parse job description markdown into formatted HTML
        job_desc_html = self._parse_job_description_markdown(job_desc)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{application.company} - {application.job_title}</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px 12px 0 0; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header h2 {{ font-size: 24px; font-weight: normal; opacity: 0.9; }}
        .back-btn {{ display: inline-block; background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; margin-bottom: 20px; transition: all 0.3s ease; }}
        .back-btn:hover {{ background: rgba(255,255,255,0.3); color: white; text-decoration: none; }}
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
        
        /* Job Description Specific Styles */
        .job-meta {{ background: #f8f9fa; padding: 15px 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #667eea; }}
        .job-meta p {{ margin: 5px 0; color: #333; font-size: 14px; }}
        .job-meta strong {{ color: #667eea; font-weight: 600; }}
        .job-section {{ margin-bottom: 30px; padding: 20px; background: #fafafa; border-radius: 8px; border: 1px solid #e9ecef; }}
        .job-section-title {{ color: #667eea; font-size: 20px; font-weight: 600; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e9ecef; }}
        .job-section-content {{ color: #333; font-size: 15px; line-height: 1.7; }}
        .job-section-content p {{ margin: 10px 0; }}
        .job-section-content ul {{ margin: 10px 0 10px 20px; }}
        .job-section-content li {{ margin: 8px 0; padding-left: 5px; }}
        .job-section-content strong {{ color: #555; font-weight: 600; }}
        #job-desc h2 {{ color: #333; font-size: 28px; margin-bottom: 25px; }}
        
        /* Technology Pills Styles */
        .tech-pills-container {{ margin-top: 20px; }}
        .tech-pills-section {{ margin-bottom: 20px; }}
        .tech-pills-label {{ 
            font-size: 14px; 
            font-weight: 600; 
            color: #667eea; 
            margin-bottom: 10px; 
            display: flex; 
            align-items: center; 
            gap: 8px;
        }}
        .tech-pills {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 8px;
        }}
        .tech-pill {{ 
            display: inline-block; 
            padding: 6px 14px; 
            border-radius: 20px; 
            font-size: 13px; 
            font-weight: 500;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .tech-pill:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .tech-pill-green {{ 
            background: #d4edda; 
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .tech-pill-yellow {{ 
            background: #fff3cd; 
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        .tech-pill-red {{ 
            background: #f8d7da; 
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .tech-legend {{ 
            margin-top: 15px; 
            padding: 12px; 
            background: #f8f9fa; 
            border-radius: 6px; 
            font-size: 12px; 
            color: #666;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .tech-legend-item {{ 
            display: flex; 
            align-items: center; 
            gap: 6px;
        }}
        .tech-legend-dot {{ 
            width: 12px; 
            height: 12px; 
            border-radius: 50%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
            <h1>{application.company}</h1>
            <h2>{application.job_title}</h2>
            <div style="margin-top: 15px;">
                <span class="status-badge status-{application.status.lower()}" style="font-size: 16px; padding: 8px 20px;">{application.status}</span>
            </div>
        </div>
        
        <div class="summary">
            <h2 style="margin-bottom: 20px; color: #333;">Summary</h2>
            
            <div class="match-score">
                {qualifications.match_score:.0f}% Match
            </div>
            
            <div class="summary-grid">
                <div class="summary-item">
                    <label>Status</label>
                    <value><span class="status-badge status-{application.status.lower()}">{application.status}</span></value>
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
                    <label>Posted Date</label>
                    <value>{job_details.get('posted_date', 'N/A')}</value>
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
            {job_desc_html}
        </div>
        
        <div id="qualifications" class="tab-content">
            <h2>Qualifications Analysis</h2>
            <pre>{qual_analysis}</pre>
        </div>
        
        <div id="cover-letter" class="tab-content">
            <h2>Cover Letter</h2>
            
            <!-- Analysis Summary Box (similar to the one from application creation) -->
            <div style="border: 1px solid #0099FF; padding: 15px; margin-bottom: 20px; box-shadow: none; border-radius: 8px; background: white;">
                <h3 style="color: #666; margin-bottom: 10px; font-size: 16px;">
                    Match Score: {qualifications.match_score:.0f}% - Application for {application.company} - {application.job_title}
                </h3>
                
                <!-- Introductory text before analysis summary -->
                <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #667eea;">
                    <p style="color: #333; font-size: 14px; line-height: 1.5; margin: 0;">
                        Yes, I've checked our compatibility based on job posting against my experience with my proprietary ML Model and these are my findings:
                    </p>
                </div>
                
                <!-- Methodology -->
                <div style="margin-bottom: 10px;">
                    <h4 style="color: #0099FF; margin-bottom: 5px; font-size: 12px; font-weight: 600;">Methodology</h4>
                    <p style="color: #666; font-size: 11px; line-height: 1.4;">
                        Our AI analyzes your resume against the job description using weighted scoring: 
                        Technical Skills (40%), Technologies/Tools (30%), Experience Level (15%), Soft Skills (10%), Other Factors (5%).
                    </p>
                </div>
                
                <!-- Features Compared -->
                <div style="margin-bottom: 10px;">
                    <h4 style="color: #0099FF; margin-bottom: 5px; font-size: 12px; font-weight: 600;">Features Compared</h4>
                    <p style="color: #666; font-size: 11px;">
                        {len(qualifications.strong_matches) + len(qualifications.missing_skills)} individual skills, technologies, and requirements analyzed
                    </p>
                </div>
                
                <!-- Strong Matches -->
                <div style="margin-bottom: 10px;">
                    <h4 style="color: #0099FF; margin-bottom: 5px; font-size: 12px; font-weight: 600;">Strong Matches</h4>
                    <div style="color: #666; font-size: 11px;">
                        {self._generate_strong_matches_html(qualifications.strong_matches)}
                    </div>
                </div>
                
                <!-- Missing Skills -->
                <div style="margin-bottom: 10px;">
                    <h4 style="color: #0099FF; margin-bottom: 5px; font-size: 12px; font-weight: 600;">Missing Skills</h4>
                    <div style="color: #666; font-size: 11px;">
                        {self._generate_missing_skills_html(qualifications.missing_skills)}
                    </div>
                </div>
            </div>
            
            <!-- Cover Letter Content with Copy Button -->
            <div style="position: relative;">
                <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #333;">Cover Letter Content</h3>
                    <button onclick="copyCoverLetter()" style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                        📋 Copy Cover Letter
                    </button>
                </div>
                
                <h4 style="margin: 0 0 15px 0; color: #333; font-size: 18px; font-weight: 600;">**Cover Letter**</h4>
                
                <div id="cover-letter-content" style="background: #f5f5f5; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-height: 500px; overflow-y: auto;">
{application.job_title} - {application.company} - Intro

{cover_letter}

Yes, I've checked our compatibility based on job posting against my experience with my proprietary ML Model and these are my findings:

Match Score: {qualifications.match_score:.0f}% - Application for {application.company} - {application.job_title}

Methodology: Weighted scoring: Technical Skills (40%), Technologies/Tools (30%), Experience Level (15%), Soft Skills (10%), Other Factors (5%).
Features Compared: {len(qualifications.strong_matches) + len(qualifications.missing_skills)} individual skills, technologies, and requirements analyzed
Strong Matches: {', '.join(qualifications.strong_matches[:5]) if qualifications.strong_matches else 'No strong matches identified'}
Missing Skills: {', '.join(qualifications.missing_skills[:5]) if qualifications.missing_skills else 'No missing skills identified'}


Sincerely,
Kervin Leacock | 305.306.3514 | kervin.leacock@yahoo.com
                </div>
            </div>
        </div>
        
        <div id="resume" class="tab-content">
            <h2>Customized Resume</h2>
            <pre>{resume}</pre>
        </div>
        
        <div id="updates" class="tab-content">
            <h2>Updates & Notes</h2>
            <div style="margin-bottom: 20px; padding: 15px; background: #f0f8ff; border-left: 4px solid #667eea; border-radius: 4px;">
                <strong style="color: #667eea;">Current Status:</strong> 
                <span class="status-badge status-{application.status.lower()}" style="margin-left: 10px;">{application.status}</span>
                <div style="margin-top: 8px; font-size: 14px; color: #666;">
                    Last Updated: {format_for_display(application.status_updated_at)}
                </div>
            </div>
            
            <!-- Update Status Form -->
            <div style="margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
                <h3 style="color: #667eea; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                    <span style="width: 20px; height: 20px; background: linear-gradient(45deg, #28a745, #dc3545, #007bff); border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 10px; font-weight: bold;">📊</span>
                    </span>
                    Update Status
                </h3>
                
                <form id="statusUpdateForm" onsubmit="submitStatusUpdate(event)">
                    <div style="margin-bottom: 15px;">
                        <label for="new_status" style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">New Status</label>
                        <select id="new_status" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                            <option value="">-- Select Status --</option>
                            <option value="Pending">⏳ Pending</option>
                            <option value="Applied">✉️ Applied</option>
                            <option value="Contacted Someone">👥 Contacted Someone</option>
                            <option value="Contacted Hiring Manager">👔 Contacted Hiring Manager</option>
                            <option value="Interviewed">🎤 Interviewed</option>
                            <option value="Offered">🎉 Offered</option>
                            <option value="Rejected">❌ Rejected</option>
                            <option value="Accepted">✅ Accepted</option>
                        </select>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label for="status_notes" style="display: block; margin-bottom: 5px; font-weight: 600; color: #333;">Notes (Optional)</label>
                        <textarea id="status_notes" placeholder="Add notes about this status update..." style="width: 100%; min-height: 80px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; resize: vertical; font-family: inherit;"></textarea>
                    </div>
                    
                    <button type="submit" id="updateStatusBtn" style="background: #fd7e14; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; justify-content: center; transition: all 0.3s;">
                        <span id="btnIcon" style="color: white; font-size: 12px;">📊</span>
                        <span id="btnText">Update Status</span>
                    </button>
                </form>
                
                <div id="status-message" style="margin-top: 15px; padding: 10px; border-radius: 4px; display: none;"></div>
            </div>
            
            <div class="timeline">
                <div class="timeline-item">
                    <strong>{format_for_display(application.created_at)}</strong> - Application Created
                </div>
                {self._generate_updates_timeline(application)}
            </div>
        </div>
    </div>
    
    <script>
        // Application ID for this summary page
        const APPLICATION_ID = '{application.id}';
        
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
        
        async function submitStatusUpdate(event) {{
            event.preventDefault();
            
            const status = document.getElementById('new_status').value;
            const notes = document.getElementById('status_notes').value;
            const messageDiv = document.getElementById('status-message');
            const submitBtn = document.getElementById('updateStatusBtn');
            const btnIcon = document.getElementById('btnIcon');
            const btnText = document.getElementById('btnText');
            
            if (!status) {{
                showMessage('❌ Please select a status', 'error');
                return;
            }}
            
            // Clear form immediately
            document.getElementById('statusUpdateForm').reset();
            
            // Show processing state
            submitBtn.disabled = true;
            submitBtn.style.background = '#6c757d';
            submitBtn.style.cursor = 'not-allowed';
            btnIcon.textContent = '⏳';
            btnText.textContent = 'Processing...';
            
            // Show processing message
            showMessage('⏳ Updating status...', 'processing');
            
            try {{
                const response = await fetch(`/api/applications/${{APPLICATION_ID}}/status`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        status: status,
                        notes: notes || null
                    }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    // Show success state
                    btnIcon.textContent = '✅';
                    btnText.textContent = 'Updated!';
                    showMessage(`✅ Status updated to ${{status}} successfully!`, 'success');
                    
                    // Reload the page to show updated status and timeline
                    setTimeout(() => {{
                        window.location.reload();
                    }}, 2000);
                }} else {{
                    // Reset button state on error
                    resetButtonState();
                    showMessage(`❌ Error: ${{result.error}}`, 'error');
                }}
            }} catch (error) {{
                // Reset button state on error
                resetButtonState();
                showMessage(`❌ Error: ${{error.message}}`, 'error');
            }}
        }}
        
        function resetButtonState() {{
            const submitBtn = document.getElementById('updateStatusBtn');
            const btnIcon = document.getElementById('btnIcon');
            const btnText = document.getElementById('btnText');
            
            submitBtn.disabled = false;
            submitBtn.style.background = '#fd7e14';
            submitBtn.style.cursor = 'pointer';
            btnIcon.textContent = '📊';
            btnText.textContent = 'Update Status';
        }}
        
        function showMessage(message, type) {{
            const messageDiv = document.getElementById('status-message');
            messageDiv.textContent = message;
            messageDiv.style.display = 'block';
            
            if (type === 'success') {{
                messageDiv.style.backgroundColor = '#d4edda';
                messageDiv.style.color = '#155724';
                messageDiv.style.border = '1px solid #c3e6cb';
            }} else if (type === 'error') {{
                messageDiv.style.backgroundColor = '#f8d7da';
                messageDiv.style.color = '#721c24';
                messageDiv.style.border = '1px solid #f5c6cb';
            }} else if (type === 'processing') {{
                messageDiv.style.backgroundColor = '#d1ecf1';
                messageDiv.style.color = '#0c5460';
                messageDiv.style.border = '1px solid #bee5eb';
            }}
            
            // Hide message after 5 seconds (except for processing which will be replaced)
            if (type !== 'processing') {{
                setTimeout(() => {{
                    messageDiv.style.display = 'none';
                }}, 5000);
            }}
        }}
        
        function copyCoverLetter() {{
            const coverLetterContent = document.getElementById('cover-letter-content');
            const text = coverLetterContent.textContent || coverLetterContent.innerText;
            
            navigator.clipboard.writeText(text).then(function() {{
                // Show success message
                const button = event.target;
                const originalText = button.innerHTML;
                button.innerHTML = '✅ Copied!';
                button.style.background = '#28a745';
                
                setTimeout(() => {{
                    button.innerHTML = originalText;
                    button.style.background = '#667eea';
                }}, 2000);
            }}).catch(function(err) {{
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                // Show success message
                const button = event.target;
                const originalText = button.innerHTML;
                button.innerHTML = '✅ Copied!';
                button.style.background = '#28a745';
                
                setTimeout(() => {{
                    button.innerHTML = originalText;
                    button.style.background = '#667eea';
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>"""
        return html
    
    def _generate_updates_timeline(self, application: Application) -> str:
        """Generate HTML for status updates timeline"""
        from app.services.job_processor import JobProcessor
        import re
        
        job_processor = JobProcessor()
        updates = job_processor.get_application_updates(application)
        
        if not updates:
            return ""
        
        timeline_html = ""
        for update in reversed(updates):  # Show newest first
            # Extract content from the HTML file
            app_id = ""
            notes_text = ""
            
            try:
                if Path(update['file']).exists():
                    html_content = read_text_file(Path(update['file']))
                    
                    # Extract Application ID
                    app_id_match = re.search(r'<strong>Application ID:</strong>\s*([^<]+)', html_content)
                    if app_id_match:
                        app_id = app_id_match.group(1).strip()
                    
                    # Extract notes text
                    notes_match = re.search(r'<div class="notes-text">([^<]*(?:<[^>]+>[^<]*)*?)</div>', html_content, re.DOTALL)
                    if notes_match:
                        notes_text = notes_match.group(1).strip()
                        # Clean up the notes text
                        notes_text = re.sub(r'\s+', ' ', notes_text).strip()
                        
            except Exception as e:
                print(f"Warning: Could not extract content from {update['file']}: {e}")
            
            # Build status badge HTML
            status_class = f"status-{update['status'].lower()}"
            status_badge = f'<span class="status-badge" style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase; background: #d1ecf1; color: #0c5460; margin-left: 10px;">{update["status"]}</span>'
            
            # Build content sections
            content_parts = []
            
            if app_id:
                content_parts.append(f'<div style="margin-top: 8px; padding: 8px; background: #f8f9fa; border-radius: 4px; font-size: 13px; color: #666;"><strong>Application ID:</strong> {app_id}</div>')
            
            if notes_text and notes_text not in ["No additional notes", ""]:
                # Make URLs clickable
                notes_with_links = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank" style="color: #667eea; text-decoration: underline;">\1</a>', notes_text)
                content_parts.append(f'<div style="margin-top: 8px; padding: 12px; background: #fff3e0; border-left: 3px solid #ff9800; border-radius: 4px; font-size: 14px; color: #000; white-space: pre-wrap;"><strong>📝 Notes:</strong><br>{notes_with_links}</div>')
            
            content_html = "".join(content_parts)
            
            timeline_html += f"""
                <div class="timeline-item">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <strong style="color: #667eea;">{update['status']}</strong>
                            {status_badge}
                        </div>
                        <span style="color: #666; font-size: 14px;">{update['display_timestamp']}</span>
                    </div>
                    {content_html}
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

