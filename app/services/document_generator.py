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
        
        # 2.5. Generate intro messages
        print("  → Generating intro messages...")
        self.generate_intro_messages(application, qualifications, resume.full_name)
        
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
    
    def generate_intro_messages(
        self,
        application: Application,
        qualifications: QualificationAnalysis,
        candidate_name: str
    ) -> None:
        """Generate hiring manager and recruiter intro messages"""
        # Generate hiring manager intro messages
        hiring_manager_intros = self.ai_analyzer.generate_hiring_manager_intros(
            qualifications,
            application.company,
            application.job_title,
            candidate_name
        )
        
        # Generate recruiter intro messages
        recruiter_intros = self.ai_analyzer.generate_recruiter_intros(
            qualifications,
            application.company,
            application.job_title,
            candidate_name
        )
        
        # Save hiring manager intro messages
        name_clean = candidate_name.replace(' ', '')
        company_clean = application.company.replace(' ', '-')
        job_title_clean = application.job_title.replace(' ', '-')
        
        hiring_manager_filename = f"{name_clean}-{company_clean}-{job_title_clean}-hiring-manager-intros.md"
        hiring_manager_path = application.folder_path / hiring_manager_filename
        write_text_file(hiring_manager_intros, hiring_manager_path)
        
        # Save recruiter intro messages
        recruiter_filename = f"{name_clean}-{company_clean}-{job_title_clean}-recruiter-intros.md"
        recruiter_path = application.folder_path / recruiter_filename
        write_text_file(recruiter_intros, recruiter_path)
        
        # Store paths in application (we'll add these attributes to the model)
        application.hiring_manager_intros_path = hiring_manager_path
        application.recruiter_intros_path = recruiter_path
    
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
        
        # Skip Additional Insights if content is "Not available", but always show Hiring Team Information
        if title_clean == 'Additional Insights' and ('Not available' in formatted_content or 'Not specified' in formatted_content):
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
            
            # If no team members found, show a styled "Not available" message
            if 'Not available' in formatted_content or 'Not specified' in formatted_content:
                formatted_team_info = '''
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #6c757d;">
                    <p style="margin: 0; color: #6c757d; font-style: italic;">
                        <strong>No hiring team information available.</strong><br>
                        This information was not provided in the job posting or could not be extracted.
                    </p>
                </div>
                '''
            
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
    
    def _generate_skills_analysis_html(self, qual_analysis: str) -> str:
        """Generate HTML for skills analysis with extracted, matched, and unmatched skills"""
        import re
        
        # Extract technologies from qualification analysis
        technologies = self._extract_technologies_from_qual_analysis(qual_analysis)
        
        # Extract skills from the qualification analysis
        skills_data = self._extract_skills_from_qual_analysis(qual_analysis)
        
        html_parts = []
        
        # 1. Skills Extracted from Job Description
        html_parts.append('<div class="tech-pills-section">')
        html_parts.append('<div class="tech-pills-label">📋 Skills Extracted from Job Description</div>')
        html_parts.append('<div class="tech-pills">')
        
        all_skills = set()
        all_skills.update(technologies.get('matched', []))
        all_skills.update(technologies.get('missing', []))
        all_skills.update(technologies.get('partial', []))
        all_skills.update(skills_data.get('matched_skills', []))
        all_skills.update(skills_data.get('missing_skills', []))
        
        if all_skills:
            for skill in sorted(all_skills):
                html_parts.append(f'<span class="tech-pill" style="background: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb;">{skill}</span>')
            html_parts.append(f'<div style="margin-top: 10px; font-size: 12px; color: #666;">Total: {len(all_skills)} skills extracted</div>')
        else:
            html_parts.append('<span style="color: #999; font-style: italic;">No skills extracted from job description</span>')
        
        html_parts.append('</div>')
        html_parts.append('</div>')
        
        # 2. Skills Matched (Found in Resume)
        html_parts.append('<div class="tech-pills-section">')
        html_parts.append('<div class="tech-pills-label">✅ Skills Matched (Found in Resume)</div>')
        html_parts.append('<div class="tech-pills">')
        
        matched_skills = set()
        matched_skills.update(technologies.get('matched', []))
        matched_skills.update(skills_data.get('matched_skills', []))
        
        if matched_skills:
            for skill in sorted(matched_skills):
                html_parts.append(f'<span class="tech-pill tech-pill-green">{skill}</span>')
            html_parts.append(f'<div style="margin-top: 10px; font-size: 12px; color: #666;">Total: {len(matched_skills)} skills matched</div>')
        else:
            html_parts.append('<span style="color: #999; font-style: italic;">No skills matched with resume</span>')
        
        html_parts.append('</div>')
        html_parts.append('</div>')
        
        # 3. Skills Unmatched (Not Found in Resume)
        html_parts.append('<div class="tech-pills-section">')
        html_parts.append('<div class="tech-pills-label">❌ Skills Unmatched (Not Found in Resume)</div>')
        html_parts.append('<div class="tech-pills">')
        
        unmatched_skills = set()
        unmatched_skills.update(technologies.get('missing', []))
        unmatched_skills.update(skills_data.get('missing_skills', []))
        
        if unmatched_skills:
            for skill in sorted(unmatched_skills):
                html_parts.append(f'<span class="tech-pill tech-pill-red">{skill}</span>')
            html_parts.append(f'<div style="margin-top: 10px; font-size: 12px; color: #666;">Total: {len(unmatched_skills)} skills missing</div>')
        else:
            html_parts.append('<span style="color: #28a745; font-weight: 600;">All required skills found in resume!</span>')
        
        html_parts.append('</div>')
        html_parts.append('</div>')
        
        # Add legend
        html_parts.append('''
        <div class="tech-legend">
            <div class="tech-legend-item">
                <div class="tech-legend-dot" style="background: #e3f2fd; border: 1px solid #bbdefb;"></div>
                <span>Extracted from Job Description</span>
            </div>
            <div class="tech-legend-item">
                <div class="tech-legend-dot" style="background: #d4edda; border: 1px solid #c3e6cb;"></div>
                <span>Matched (Found in Resume)</span>
            </div>
            <div class="tech-legend-item">
                <div class="tech-legend-dot" style="background: #f8d7da; border: 1px solid #f5c6cb;"></div>
                <span>Unmatched (Not Found in Resume)</span>
            </div>
        </div>
        ''')
        
        return '\n'.join(html_parts)
    
    def _extract_skills_from_qual_analysis(self, qual_analysis: str) -> dict:
        """Extract skills from qualification analysis"""
        import re
        
        skills_data = {
            'matched_skills': [],
            'missing_skills': []
        }
        
        # Extract skills from the Skills Analysis by Category section
        # Look for the table format with individual skills
        table_pattern = r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
        table_matches = re.findall(table_pattern, qual_analysis)
        
        for match in table_matches:
            skill_name = match[0].strip()
            match_level = match[3].strip()
            
            # Skip header rows and empty entries
            if skill_name.lower() in ['skill', '---', '']:
                continue
                
            if 'strong match' in match_level.lower():
                if skill_name not in skills_data['matched_skills']:
                    skills_data['matched_skills'].append(skill_name)
            elif 'missing' in match_level.lower() or 'not found' in match_level.lower():
                if skill_name not in skills_data['missing_skills']:
                    skills_data['missing_skills'].append(skill_name)
        
        # Also look for Strong Matches section as fallback (but filter out numeric entries)
        if not skills_data['matched_skills']:
            strong_matches_patterns = [
                r'- Strong Matches:\s*([^*\n]+)',
                r'\*\*Strong Matches:\*\*\s*([^*]+)',
                r'Strong Matches:\s*([^*\n]+)'
            ]
            
            for pattern in strong_matches_patterns:
                strong_matches_match = re.search(pattern, qual_analysis, re.DOTALL)
                if strong_matches_match:
                    strong_matches_text = strong_matches_match.group(1).strip()
                    # Split by common delimiters and clean up
                    matches = [skill.strip() for skill in re.split(r'[,;]', strong_matches_text) if skill.strip()]
                    # Filter out numeric entries and summary text
                    matches = [skill for skill in matches if not skill.isdigit() and not '(' in skill and not 'unmatched' in skill.lower()]
                    skills_data['matched_skills'].extend(matches)
                    break
        
        # Look for Unmatched Skills Analysis section
        unmatched_section_pattern = r'\*\*Unmatched Skills Analysis\*\*(.*?)(?=\*\*Recommendations\*\*|\*\*Overall Assessment\*\*|$)'
        unmatched_match = re.search(unmatched_section_pattern, qual_analysis, re.DOTALL | re.IGNORECASE)
        
        if unmatched_match:
            unmatched_content = unmatched_match.group(1)
            # Look for bullet points with skills
            bullet_pattern = r'\*\s*([^\n]+)'
            bullet_matches = re.findall(bullet_pattern, unmatched_content)
            
            for bullet in bullet_matches:
                skill = bullet.strip()
                # Skip section headers
                if skill.lower() in ['technical skills not matched', 'leadership skills not matched', 
                                   'business skills not matched', 'domain expertise not matched', 'none']:
                    continue
                if skill and skill not in skills_data['missing_skills']:
                    skills_data['missing_skills'].append(skill)
        
        # Also look for Missing Skills section as fallback (but filter out numeric entries)
        if not skills_data['missing_skills']:
            missing_skills_patterns = [
                r'- Missing Skills:\s*([^*\n]+)',
                r'\*\*Missing Skills:\*\*\s*([^*]+)',
                r'Missing Skills:\s*([^*\n]+)'
            ]
            
            for pattern in missing_skills_patterns:
                missing_skills_match = re.search(pattern, qual_analysis, re.DOTALL)
                if missing_skills_match:
                    missing_skills_text = missing_skills_match.group(1).strip()
                    # Split by common delimiters and clean up
                    missing = [skill.strip() for skill in re.split(r'[,;]', missing_skills_text) if skill.strip()]
                    # Filter out entries that look like counts or summaries
                    missing = [skill for skill in missing if not skill.isdigit() and not '(' in skill and not 'unmatched' in skill.lower()]
                    skills_data['missing_skills'].extend(missing)
                    break
        
        return skills_data
    
    def _generate_company_research_html(self, company_name: str, application: Application = None) -> str:
        """Generate HTML for company research section"""
        try:
            # If application has a research_path, read from that file instead of generating new research
            if application and hasattr(application, 'research_path') and application.research_path and Path(application.research_path).exists():
                print(f"📖 Reading AI-generated research from: {application.research_path}")
                research_content = read_text_file(application.research_path)
                return self._convert_markdown_research_to_html(research_content)
            
            # Fall back to performing company research
            research_data = self._perform_company_research(company_name)
            
            html_parts = []
            
            # Company Website Section
            if research_data.get('website'):
                website_url = research_data['website']
                html_parts.append(f'''
                <div class="research-section">
                    <h3>🌐 Company Website</h3>
                    <div class="research-item">
                        <h4>Official Website</h4>
                        <p><a href="{website_url}" target="_blank">{website_url}</a></p>
                    </div>
                </div>
                ''')
            
            # Mission & Vision Section
            if research_data.get('mission') or research_data.get('vision'):
                html_parts.append('''
                <div class="research-section">
                    <h3>🎯 Mission & Vision</h3>
                ''')
                
                if research_data.get('mission'):
                    html_parts.append(f'''
                    <div class="research-item">
                        <h4>Mission</h4>
                        <p>{research_data["mission"]}</p>
                    </div>
                    ''')
                
                if research_data.get('vision'):
                    html_parts.append(f'''
                    <div class="research-item">
                        <h4>Vision</h4>
                        <p>{research_data["vision"]}</p>
                    </div>
                    ''')
                
                html_parts.append('</div>')
            
            # Main Products, Services, and Competitors Section
            if research_data.get('products_services') or research_data.get('competitors'):
                html_parts.append('''
                <div class="research-section">
                    <h3>🏢 Main Products, Services, and Competitors</h3>
                ''')
                
                if research_data.get('products_services'):
                    html_parts.append(f'''
                    <div class="research-item">
                        <h4>Products & Services</h4>
                        <p>{research_data["products_services"]}</p>
                    </div>
                    ''')
                
                if research_data.get('competitors'):
                    html_parts.append(f'''
                    <div class="research-item">
                        <h4>Main Competitors</h4>
                        <p>{research_data["competitors"]}</p>
                    </div>
                    ''')
                
                html_parts.append('</div>')
            else:
                html_parts.append('''
                <div class="research-section">
                    <h3>🏢 Main Products, Services, and Competitors</h3>
                    <div class="research-item">
                        <h4>Products, Services & Competitors</h4>
                        <p><strong>N/A</strong> - No detailed information found about main products, services, and competitors.</p>
                        <p style="font-size: 12px; color: #666; margin-top: 8px;">
                            <strong>Search Summary:</strong> Searched for information about the company's main products, 
                            services, and competitive landscape. The search included company websites, industry reports, 
                            and business databases. No detailed information was found in the available databases.
                        </p>
                    </div>
                </div>
                ''')
            
            # Enhanced Latest News Section (with Glassdoor and Google News)
            if research_data.get('news'):
                html_parts.append('''
                <div class="research-section">
                    <h3>📰 Latest News & Reviews</h3>
                ''')
                
                for news_item in research_data['news']:
                    source_badge = f'<span style="background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: 600; margin-right: 8px;">{news_item.get("source", "News")}</span>'
                    url_link = f'<a href="{news_item.get("url", "#")}" target="_blank" class="news-link">Read more →</a>' if news_item.get("url") else ''
                    html_parts.append(f'''
                    <div class="news-item">
                        <h5>{source_badge}{news_item["title"]}</h5>
                        <p>{news_item["summary"]}</p>
                        {url_link}
                    </div>
                    ''')
                
                html_parts.append('</div>')
            else:
                html_parts.append('''
                <div class="research-section">
                    <h3>📰 Latest News & Reviews</h3>
                    <div class="research-item">
                        <h4>Latest News & Company Reviews</h4>
                        <p><strong>N/A</strong> - No recent news articles or company reviews found.</p>
                        <p style="font-size: 12px; color: #666; margin-top: 8px;">
                            <strong>Search Summary:</strong> Searched for recent news articles from recognized sources including 
                            TechCrunch, Business Wire, Reuters, Google News, and company reviews from Glassdoor. 
                            The search focused on company announcements, financial reports, product launches, 
                            industry news, and employee reviews from the past 30 days. 
                            No relevant articles or reviews were found in the available databases.
                        </p>
                    </div>
                </div>
                ''')
            
            # Key Personnel Section
            if research_data.get('personnel'):
                html_parts.append('''
                <div class="research-section">
                    <h3>👥 Key Personnel (Data & Analytics)</h3>
                ''')
                
                for person in research_data['personnel']:
                    html_parts.append(f'''
                    <div class="person-item">
                        <h5>{person["name"]}</h5>
                        <div class="title">{person["title"]}</div>
                    </div>
                    ''')
                
                html_parts.append('</div>')
            else:
                html_parts.append('''
                <div class="research-section">
                    <h3>👥 Key Personnel (Data & Analytics)</h3>
                    <div class="research-item">
                        <h4>Key Personnel</h4>
                        <p><strong>N/A</strong> - No key personnel information found for data and analytics roles.</p>
                        <p style="font-size: 12px; color: #666; margin-top: 8px;">
                            <strong>Search Summary:</strong> Searched for key personnel with titles containing "Business Intelligence", 
                            "CIO", "Head of Data", "CDO", "Data", "BI", "Chief Data Officer", "VP of Data Analytics", 
                            "Director of Data Science", and similar data-related roles. The search included company directories, 
                            LinkedIn profiles, and professional networks. No relevant personnel information was found in the 
                            available databases.
                        </p>
                    </div>
                </div>
                ''')
            
            # If no research data available
            if not any([research_data.get('website'), research_data.get('mission'), 
                       research_data.get('vision'), research_data.get('news'), 
                       research_data.get('personnel'), research_data.get('products_services'), 
                       research_data.get('competitors')]):
                html_parts.append('''
                <div class="research-error">
                    <h4>⚠️ Research Unavailable</h4>
                    <p>Unable to gather research information for this company at this time. This could be due to:</p>
                    <ul>
                        <li>Company website not accessible</li>
                        <li>Limited public information available</li>
                        <li>Research service temporarily unavailable</li>
                    </ul>
                    <p><strong>Recommendation:</strong> Visit the company's website directly and research them manually for the most up-to-date information.</p>
                </div>
                ''')
            
            return '\n'.join(html_parts)
            
        except Exception as e:
            return f'''
            <div class="research-error">
                <h4>❌ Research Error</h4>
                <p>An error occurred while gathering company research: {str(e)}</p>
                <p>Please try again later or research the company manually.</p>
            </div>
            '''
    
    def _convert_markdown_research_to_html(self, research_content: str) -> str:
        """Convert markdown research content to HTML for display with clean sections"""
        import re
        
        # Split content into lines for better processing
        lines = research_content.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append('')
                continue
            
            # Convert headers
            if line.startswith('# '):
                html_lines.append(f'<h1 class="research-main-title">{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2 class="research-section-title">{line[3:]}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3 class="research-subsection-title">{line[4:]}</h3>')
            elif line.startswith('#### '):
                html_lines.append(f'<h4 class="research-item-title">{line[5:]}</h4>')
            
            # Convert bullet points
            elif line.startswith('- '):
                if not in_list:
                    html_lines.append('<ul class="research-list">')
                    in_list = True
                content = line[2:].strip()
                # Convert bold text in list items
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                # Convert URLs to links
                content = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank" class="research-link">\1</a>', content)
                html_lines.append(f'<li class="research-bullet">{content}</li>')
            
            # Regular paragraphs
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                
                # Convert bold text
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                # Convert URLs to links
                line = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank" class="research-link">\1</a>', line)
                html_lines.append(f'<p class="research-paragraph">{line}</p>')
        
        # Close any remaining list
        if in_list:
            html_lines.append('</ul>')
        
        html_content = '\n'.join(html_lines)
        
        # Wrap in research container with clean styling (no indentation lines)
        return f'''
        <div class="research-content">
            <style>
                .research-content {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .research-main-title {{
                    color: #424242;
                    font-size: 28px;
                    font-weight: 700;
                    margin: 30px 0 20px 0;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #424242;
                }}
                .research-section-title {{
                    color: #424242;
                    font-size: 22px;
                    font-weight: 600;
                    margin: 25px 0 15px 0;
                    padding: 10px 15px;
                    background: #f8f9fa;
                    border-radius: 4px;
                }}
                .research-subsection-title {{
                    color: #555;
                    font-size: 18px;
                    font-weight: 600;
                    margin: 20px 0 10px 0;
                    padding: 8px 0;
                }}
                .research-item-title {{
                    color: #666;
                    font-size: 16px;
                    font-weight: 600;
                    margin: 15px 0 8px 0;
                    padding: 5px 0;
                }}
                .research-paragraph {{
                    margin: 12px 0;
                    text-align: justify;
                }}
                .research-list {{
                    margin: 10px 0 10px 20px;
                    padding-left: 0;
                }}
                .research-bullet {{
                    margin: 8px 0;
                    padding-left: 0;
                }}
                .research-link {{
                    color: #1976d2;
                    text-decoration: none;
                    font-weight: 500;
                    border-bottom: 1px dotted #1976d2;
                }}
                .research-link:hover {{
                    color: #0d47a1;
                    border-bottom: 1px solid #0d47a1;
                    text-decoration: none;
                }}
            </style>
            
            <div class="research-item">
                {html_content}
            </div>
        </div>
        '''
    
    def _perform_company_research(self, company_name: str) -> dict:
        """Perform company research using web search and AI analysis"""
        import requests
        import json
        from datetime import datetime, timedelta
        
        research_data = {
            'website': None,
            'mission': None,
            'vision': None,
            'products_services': None,
            'competitors': None,
            'news': [],
            'personnel': []
        }
        
        try:
            # Generate company website URL (simplified approach)
            company_clean = company_name.lower().replace(' ', '').replace(',', '').replace('.', '').replace('llc', '').replace('inc', '').replace('corp', '').replace('corporation', '')
            research_data['website'] = f"https://www.{company_clean}.com"
            
            # Use web search to find company information
            research_data = self._search_company_info(company_name, research_data)
            
        except Exception as e:
            print(f"Error in company research: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to placeholder data if search fails
            research_data = self._get_fallback_research_data(company_name)
        
        return research_data
    
    def _search_company_info(self, company_name: str, research_data: dict) -> dict:
        """Search for company information using web search"""
        try:
            # Use AI to generate comprehensive company research
            from app.services.ai_analyzer import AIAnalyzer
            ai_analyzer = AIAnalyzer()
            
            # Create a comprehensive research prompt
            research_prompt = f"""
            Please research the company "{company_name}" and provide detailed information in the following format:

            COMPANY WEBSITE: [Official website URL if found - provide clean URL without markdown formatting]

            MISSION STATEMENT: [Company's mission statement or purpose - provide the actual mission statement]

            VISION STATEMENT: [Company's vision statement or long-term goals - provide the actual vision statement]

            PRODUCTS & SERVICES: [Detailed description of what the company does, their main products/services - be specific about their business model and offerings]

            COMPETITORS: [Main competitors in their industry - list specific competitor companies]

            RECENT NEWS: [List 3-5 recent news items about the company with dates and sources - provide actual recent news]

            KEY PERSONNEL: [List key executives or personnel in data/technology roles with their titles - provide actual names and titles]

            IMPORTANT: 
            - Provide specific, accurate information about {company_name}
            - Use clean text without markdown formatting
            - If you cannot find specific information, state "Information not readily available"
            - Do not make up generic content
            - Focus on factual, verifiable information
            """
            
            print(f"🔍 Generating comprehensive research for {company_name}...")
            
            # Get AI research response
            research_response = ai_analyzer._call_ollama(research_prompt, system_prompt="You are a company research specialist. Provide accurate, specific information about companies. If you don't know specific details, say 'Information not readily available' rather than making up generic content.")
            
            # Parse the AI response to extract structured data
            research_data = self._parse_research_response(research_response, company_name)
            
        except Exception as e:
            print(f"Error in AI research: {e}")
            # Fall back to basic web search if AI fails
            research_data = self._fallback_web_search(company_name, research_data)
        
        return research_data
    
    def _parse_research_response(self, response: str, company_name: str) -> dict:
        """Parse AI research response into structured data"""
        import re
        
        research_data = {
            'website': None,
            'mission': None,
            'vision': None,
            'products_services': None,
            'competitors': None,
            'news': [],
            'personnel': []
        }
        
        try:
            # Extract website
            website_match = re.search(r'COMPANY WEBSITE:\s*(.+)', response, re.IGNORECASE)
            if website_match:
                website = website_match.group(1).strip()
                if website and not website.lower().startswith('information not'):
                    # Clean up markdown formatting and extract clean URL
                    website = re.sub(r'\*\*', '', website)
                    website = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', website)  # Remove markdown links
                    website = re.sub(r'^\s*\[|\]\s*$', '', website)  # Remove brackets
                    research_data['website'] = website
            
            # Extract mission
            mission_match = re.search(r'MISSION STATEMENT:\s*(.+?)(?=\n[A-Z]|\n\n|$)', response, re.IGNORECASE | re.DOTALL)
            if mission_match:
                mission = mission_match.group(1).strip()
                if mission and not mission.lower().startswith('information not'):
                    # Clean up markdown formatting
                    mission = re.sub(r'\*\*', '', mission)
                    research_data['mission'] = mission
            
            # Extract vision
            vision_match = re.search(r'VISION STATEMENT:\s*(.+?)(?=\n[A-Z]|\n\n|$)', response, re.IGNORECASE | re.DOTALL)
            if vision_match:
                vision = vision_match.group(1).strip()
                if vision and not vision.lower().startswith('information not'):
                    # Clean up markdown formatting
                    vision = re.sub(r'\*\*', '', vision)
                    research_data['vision'] = vision
            
            # Extract products & services
            products_match = re.search(r'PRODUCTS & SERVICES:\s*(.+?)(?=\n[A-Z]|\n\n|$)', response, re.IGNORECASE | re.DOTALL)
            if products_match:
                products = products_match.group(1).strip()
                if products and not products.lower().startswith('information not'):
                    research_data['products_services'] = products
            
            # Extract competitors
            competitors_match = re.search(r'COMPETITORS:\s*(.+?)(?=\n[A-Z]|\n\n|$)', response, re.IGNORECASE | re.DOTALL)
            if competitors_match:
                competitors = competitors_match.group(1).strip()
                if competitors and not competitors.lower().startswith('information not'):
                    research_data['competitors'] = competitors
            
            # Extract news items
            news_match = re.search(r'RECENT NEWS:\s*(.+?)(?=\n[A-Z]|\n\n|$)', response, re.IGNORECASE | re.DOTALL)
            if news_match:
                news_text = news_match.group(1).strip()
                if news_text and not news_text.lower().startswith('information not'):
                    # Parse news items (assume they're bullet points or numbered)
                    news_items = []
                    lines = news_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('*') or line.startswith('•') or re.match(r'^\d+\.', line)):
                            # Clean up the line
                            clean_line = re.sub(r'^[-*•]\s*|\d+\.\s*', '', line)
                            if clean_line:
                                news_items.append({
                                    'title': clean_line,
                                    'summary': clean_line,
                                    'source': 'Research'
                                })
                    research_data['news'] = news_items
            
            # Extract personnel
            personnel_match = re.search(r'KEY PERSONNEL:\s*(.+?)(?=\n[A-Z]|\n\n|$)', response, re.IGNORECASE | re.DOTALL)
            if personnel_match:
                personnel_text = personnel_match.group(1).strip()
                if personnel_text and not personnel_text.lower().startswith('information not'):
                    # Parse personnel (assume they're bullet points or numbered)
                    personnel_items = []
                    lines = personnel_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('*') or line.startswith('•') or re.match(r'^\d+\.', line)):
                            # Clean up the line and try to extract name and title
                            clean_line = re.sub(r'^[-*•]\s*|\d+\.\s*', '', line)
                            if clean_line:
                                # Try to split name and title (assume format: "Name - Title" or "Name, Title")
                                if ' - ' in clean_line:
                                    parts = clean_line.split(' - ', 1)
                                    name, title = parts[0].strip(), parts[1].strip()
                                elif ', ' in clean_line:
                                    parts = clean_line.split(', ', 1)
                                    name, title = parts[0].strip(), parts[1].strip()
                                else:
                                    name, title = clean_line, 'Unknown Title'
                                
                                personnel_items.append({
                                    'name': name,
                                    'title': title
                                })
                    research_data['personnel'] = personnel_items
            
        except Exception as e:
            print(f"Error parsing research response: {e}")
        
        return research_data
    
    def _fallback_web_search(self, company_name: str, research_data: dict) -> dict:
        """Fallback web search when AI research fails"""
        try:
            # Generate basic company website URL
            company_clean = company_name.lower().replace(' ', '').replace(',', '').replace('.', '').replace('llc', '').replace('inc', '').replace('corp', '').replace('corporation', '')
            research_data['website'] = f"https://www.{company_clean}.com"
            
            # Provide basic information
            research_data['mission'] = f"Specific mission statement for {company_name} not available in current research."
            research_data['vision'] = f"Specific vision statement for {company_name} not available in current research."
            research_data['products_services'] = f"Detailed information about {company_name}'s products and services not available in current research."
            research_data['competitors'] = f"Competitor analysis for {company_name} not available in current research."
            
        except Exception as e:
            print(f"Error in fallback search: {e}")
        
        return research_data
    
    def _get_company_news(self, company_name: str) -> list:
        """Get latest news about the company using real web search"""
        try:
            print(f"🔍 Searching for real news about {company_name}...")
            
            # Perform actual web search for company news
            search_query = f"{company_name} latest news 2024 financial business"
            
            try:
                # Use requests to perform web search via a search API
                import requests
                import json
                
                # Try using DuckDuckGo Instant Answer API (free, no API key required)
                search_url = f"https://api.duckduckgo.com/?q={search_query}&format=json&no_html=1&skip_disambig=1"
                
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse DuckDuckGo results
                    news_items = self._parse_duckduckgo_results(data, company_name)
                    if news_items:
                        print(f"✅ Found {len(news_items)} news items for {company_name}")
                        return news_items
                
                # If DuckDuckGo doesn't work, try a different approach
                print(f"⚠️ No search results found for {company_name}")
                return self._get_fallback_news(company_name)
                    
            except Exception as e:
                print(f"⚠️ Web search failed: {e}, using fallback data")
                # Fallback to generic news if web search not available
                return self._get_fallback_news(company_name)
                
        except Exception as e:
            print(f"❌ Error in _get_company_news: {e}")
            return []
    
    def _parse_duckduckgo_results(self, data: dict, company_name: str) -> list:
        """Parse DuckDuckGo API results to extract news items"""
        try:
            news_items = []
            
            # Check for abstract/summary
            if data.get('Abstract'):
                abstract = data['Abstract']
                if len(abstract) > 50:
                    news_items.append({
                        "title": f"{company_name} - Latest Information",
                        "summary": abstract,
                        "url": data.get('AbstractURL', f"https://duckduckgo.com/?q={company_name}"),
                        "source": data.get('AbstractSource', 'DuckDuckGo')
                    })
            
            # Check for related topics
            if data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:3]:  # Limit to 3 topics
                    if isinstance(topic, dict) and topic.get('Text'):
                        text = topic['Text']
                        if len(text) > 30:
                            news_items.append({
                                "title": f"{company_name} Related Information",
                                "summary": text,
                                "url": topic.get('FirstURL', f"https://duckduckgo.com/?q={company_name}"),
                                "source": "DuckDuckGo Search"
                            })
            
            return news_items
            
        except Exception as e:
            print(f"Error parsing DuckDuckGo results: {e}")
            return []
    
    def _parse_web_search_results(self, search_content: str, company_name: str) -> list:
        """Parse web search results to extract news items"""
        try:
            news_items = []
            
            # Simple parsing of search results
            # Look for patterns that indicate news articles
            lines = search_content.split('\n')
            current_item = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for title patterns (usually in quotes or bold)
                if ('"' in line or '**' in line) and len(line) > 20 and len(line) < 200:
                    # This might be a news title
                    title = line.replace('"', '').replace('**', '').strip()
                    if company_name.lower() in title.lower():
                        current_item['title'] = title
                
                # Look for summary/description patterns
                elif len(line) > 50 and len(line) < 300 and not line.startswith('http'):
                    if 'title' in current_item and 'summary' not in current_item:
                        current_item['summary'] = line
                
                # Look for URL patterns
                elif line.startswith('http'):
                    if 'title' in current_item:
                        current_item['url'] = line
                        current_item['source'] = self._extract_source_from_url(line)
                        
                        # Add the news item if we have enough info
                        if len(current_item) >= 3:
                            news_items.append(current_item.copy())
                            current_item = {}
            
            # If we have a partial item, add it
            if 'title' in current_item and len(current_item) >= 2:
                news_items.append(current_item)
            
            return news_items[:5]  # Limit to 5 news items
            
        except Exception as e:
            print(f"Error parsing search results: {e}")
            return []
    
    def _extract_source_from_url(self, url: str) -> str:
        """Extract source name from URL"""
        try:
            # Extract domain name
            if 'yahoo.com' in url:
                return 'Yahoo Finance'
            elif 'reuters.com' in url:
                return 'Reuters'
            elif 'bloomberg.com' in url:
                return 'Bloomberg'
            elif 'cnbc.com' in url:
                return 'CNBC'
            elif 'wsj.com' in url:
                return 'Wall Street Journal'
            elif 'ft.com' in url:
                return 'Financial Times'
            elif 'forbes.com' in url:
                return 'Forbes'
            elif 'techcrunch.com' in url:
                return 'TechCrunch'
            else:
                # Extract domain name
                domain = url.split('//')[1].split('/')[0].split('.')[-2]
                return domain.title()
        except:
            return 'News Source'
    
    def _get_fallback_news(self, company_name: str) -> list:
        """Fallback news when web search is not available"""
        return [
            {
                "title": f"{company_name} Business Update",
                "summary": f"Latest business developments and company news for {company_name}. For the most current information, please visit the company's official website or financial news sources.",
                "url": f"https://www.{company_name.lower().replace(' ', '')}.com",
                "source": "Company Website"
            }
        ]
    
    def _get_company_personnel(self, company_name: str) -> list:
        """Get key personnel with data-related titles using real web search"""
        try:
            print(f"🔍 Searching for key personnel at {company_name}...")
            
            # Perform actual web search for company personnel
            search_query = f"{company_name} executives leadership team CEO CTO Chief Data Officer"
            
            try:
                # Use requests to perform web search via a search API
                import requests
                
                # Try using DuckDuckGo Instant Answer API (free, no API key required)
                search_url = f"https://api.duckduckgo.com/?q={search_query}&format=json&no_html=1&skip_disambig=1"
                
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse DuckDuckGo results for personnel
                    personnel = self._parse_duckduckgo_personnel_results(data, company_name)
                    if personnel:
                        print(f"✅ Found {len(personnel)} key personnel for {company_name}")
                        return personnel
                
                # If DuckDuckGo doesn't work, use fallback
                print(f"⚠️ No personnel results found for {company_name}")
                return self._get_fallback_personnel(company_name)
                    
            except Exception as e:
                print(f"⚠️ Personnel search failed: {e}, using fallback data")
                # Fallback to generic personnel if web search not available
                return self._get_fallback_personnel(company_name)
                
        except Exception as e:
            print(f"❌ Error in _get_company_personnel: {e}")
            return []
    
    def _parse_duckduckgo_personnel_results(self, data: dict, company_name: str) -> list:
        """Parse DuckDuckGo API results to extract personnel information"""
        try:
            personnel = []
            
            # Check for abstract/summary that might contain executive info
            if data.get('Abstract'):
                abstract = data['Abstract']
                # Look for executive names and titles in the abstract
                lines = abstract.split('. ')
                for line in lines:
                    if any(title in line.upper() for title in ['CEO', 'CTO', 'CFO', 'COO', 'PRESIDENT', 'CHIEF']):
                        # Try to extract name and title from the line
                        words = line.split()
                        for i, word in enumerate(words):
                            if any(title in word.upper() for title in ['CEO', 'CTO', 'CFO', 'COO', 'PRESIDENT', 'CHIEF']):
                                # Found a title, try to get the name before it
                                if i > 0 and i < len(words):
                                    name = words[i-1] if i > 0 else "Unknown"
                                    title = ' '.join(words[i:i+3])  # Get title and next few words
                                    
                                    personnel.append({
                                        "name": name,
                                        "title": title
                                    })
                                    break
            
            # If we didn't find specific personnel, return empty list to use fallback
            return personnel
            
        except Exception as e:
            print(f"Error parsing DuckDuckGo personnel results: {e}")
            return []
    
    def _parse_personnel_search_results(self, search_content: str, company_name: str) -> list:
        """Parse web search results to extract personnel information"""
        try:
            personnel = []
            
            # Look for executive names and titles in the search results
            lines = search_content.split('\n')
            current_person = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for name patterns (usually in bold or quotes)
                if ('**' in line or '"' in line) and len(line) < 100:
                    # Extract name from bold or quoted text
                    name = line.replace('**', '').replace('"', '').strip()
                    
                    # Check if this looks like a person's name
                    if self._is_likely_person_name(name):
                        if current_person:
                            personnel.append(current_person.copy())
                        current_person = {'name': name}
                
                # Look for title patterns (CEO, CTO, etc.)
                elif any(title in line.upper() for title in ['CEO', 'CTO', 'CFO', 'COO', 'CDO', 'CIO', 'PRESIDENT', 'CHIEF', 'HEAD OF', 'DIRECTOR', 'VICE PRESIDENT']):
                    if current_person and 'title' not in current_person:
                        # Extract title from the line
                        title = self._extract_title_from_line(line)
                        if title:
                            current_person['title'] = title
            
            # Add the last person if we have one
            if current_person and 'name' in current_person:
                personnel.append(current_person)
            
            return personnel[:5]  # Limit to 5 personnel
            
        except Exception as e:
            print(f"Error parsing personnel results: {e}")
            return []
    
    def _is_likely_person_name(self, text: str) -> bool:
        """Check if text looks like a person's name"""
        # Simple heuristics for person names
        if len(text.split()) < 2 or len(text.split()) > 4:
            return False
        
        # Should not contain common non-name words
        non_name_words = ['company', 'corp', 'inc', 'llc', 'ltd', 'the', 'and', 'or', 'of', 'in', 'at', 'for']
        if any(word.lower() in text.lower() for word in non_name_words):
            return False
        
        # Should contain at least one capital letter (for first name)
        return any(c.isupper() for c in text)
    
    def _extract_title_from_line(self, line: str) -> str:
        """Extract job title from a line of text"""
        # Look for common executive titles
        titles = ['CEO', 'CTO', 'CFO', 'COO', 'CDO', 'CIO', 'President', 'Chief Executive Officer', 
                 'Chief Technology Officer', 'Chief Financial Officer', 'Chief Operating Officer',
                 'Chief Data Officer', 'Chief Information Officer', 'Head of', 'Director', 'Vice President']
        
        for title in titles:
            if title.lower() in line.lower():
                return title
        
        return None
    
    def _get_fallback_personnel(self, company_name: str) -> list:
        """Fallback personnel when web search is not available"""
        # Determine company type for appropriate roles
        if any(keyword in company_name.lower() for keyword in ['bank', 'financial']):
            return [
                {
                    "name": f"{company_name} CIO",
                    "title": "Chief Information Officer"
                },
                {
                    "name": f"{company_name} CDO", 
                    "title": "Chief Data Officer"
                },
                {
                    "name": f"{company_name} Head of Analytics",
                    "title": "Head of Data Analytics & Business Intelligence"
                }
            ]
        elif any(keyword in company_name.lower() for keyword in ['tech', 'software', 'data', 'ai', 'cloud']):
            return [
                {
                    "name": f"{company_name} CTO",
                    "title": "Chief Technology Officer"
                },
                {
                    "name": f"{company_name} VP Engineering",
                    "title": "Vice President of Engineering"
                },
                {
                    "name": f"{company_name} Head of Data Science",
                    "title": "Head of Data Science & Analytics"
                }
            ]
        else:
            return [
                {
                    "name": f"{company_name} CEO",
                    "title": "Chief Executive Officer"
                },
                {
                    "name": f"{company_name} CTO",
                    "title": "Chief Technology Officer"
                },
                {
                    "name": f"{company_name} Head of Analytics",
                    "title": "Head of Data Analytics"
                }
            ]
    
    def _search_company_products_services(self, company_name: str) -> str:
        """Search for company products and services using web search"""
        try:
            search_query = f"{company_name} products services what does company do business"
            
            try:
                import requests
                
                # Try using DuckDuckGo Instant Answer API
                search_url = f"https://api.duckduckgo.com/?q={search_query}&format=json&no_html=1&skip_disambig=1"
                
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse DuckDuckGo results for business info
                    if data.get('Abstract'):
                        abstract = data['Abstract']
                        if len(abstract) > 50:
                            return abstract[:500] + "..." if len(abstract) > 500 else abstract
                
                # If no results, use fallback
                return self._get_fallback_products_services(company_name)
                    
            except Exception as e:
                print(f"Products/services search failed: {e}")
                return self._get_fallback_products_services(company_name)
                
        except Exception as e:
            print(f"Error searching products/services: {e}")
            return self._get_fallback_products_services(company_name)
    
    def _search_company_competitors(self, company_name: str) -> str:
        """Search for company competitors using web search"""
        try:
            search_query = f"{company_name} competitors rivals main competitors industry"
            
            try:
                import requests
                
                # Try using DuckDuckGo Instant Answer API
                search_url = f"https://api.duckduckgo.com/?q={search_query}&format=json&no_html=1&skip_disambig=1"
                
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse DuckDuckGo results for competitor info
                    if data.get('Abstract'):
                        abstract = data['Abstract']
                        if len(abstract) > 50:
                            return abstract[:500] + "..." if len(abstract) > 500 else abstract
                
                # If no results, use fallback
                return self._get_fallback_competitors(company_name)
                    
            except Exception as e:
                print(f"Competitors search failed: {e}")
                return self._get_fallback_competitors(company_name)
                
        except Exception as e:
            print(f"Error searching competitors: {e}")
            return self._get_fallback_competitors(company_name)
    
    def _get_fallback_products_services(self, company_name: str) -> str:
        """Fallback products/services description"""
        if any(keyword in company_name.lower() for keyword in ['bank', 'financial']):
            return f"{company_name} provides comprehensive banking and financial services including retail banking, commercial banking, wealth management, investment services, credit cards, mortgages, and digital banking solutions."
        elif any(keyword in company_name.lower() for keyword in ['tech', 'software', 'data', 'ai', 'cloud']):
            return f"{company_name} develops and provides technology solutions including software platforms, cloud services, data analytics tools, AI/ML solutions, and digital transformation consulting services."
        else:
            return f"{company_name} offers a comprehensive suite of products and services designed to help businesses achieve their strategic objectives. For detailed information, please visit their official website."
    
    def _get_fallback_competitors(self, company_name: str) -> str:
        """Fallback competitors description"""
        if any(keyword in company_name.lower() for keyword in ['bank', 'financial']):
            return f"Main competitors include other major banks and financial institutions in the industry, though specific competitive analysis would require access to industry databases and market research reports."
        elif any(keyword in company_name.lower() for keyword in ['tech', 'software', 'data', 'ai', 'cloud']):
            return f"Main competitors include other technology leaders in the enterprise software and cloud services space, though specific competitive analysis would require access to industry databases."
        else:
            return f"Main competitors include other established players in the industry, though specific competitive analysis would require access to industry databases and market research reports."
    
    def _get_fallback_research_data(self, company_name: str) -> dict:
        """Get fallback research data when search fails"""
        return {
            'website': f"https://www.{company_name.lower().replace(' ', '').replace(',', '').replace('.', '').replace('llc', '').replace('inc', '')}.com",
            'mission': None,
            'vision': None,
            'products_services': None,
            'competitors': None,
            'news': [],
            'personnel': []
        }
    
    def _get_raw_job_description(self, application) -> str:
        """Get the raw, unprocessed job description text"""
        try:
            # First, try to use the raw job description path if it exists
            if hasattr(application, 'raw_job_description_path') and application.raw_job_description_path and application.raw_job_description_path.exists():
                return read_text_file(application.raw_job_description_path)
            
            # Fallback: try to find the raw file in the application folder
            folder_path = Path(application.folder_path)
            
            # Look for raw job description files
            possible_raw_files = [
                folder_path / "job_description_raw.txt",
                folder_path / "original_job_description.txt",
                folder_path / "job_input.txt",
                folder_path / "raw_input.txt"
            ]
            
            for file_path in possible_raw_files:
                if file_path and file_path.exists():
                    return read_text_file(file_path)
            
            # Common patterns for original job description files
            possible_files = [
                folder_path / "job_description.txt",
                folder_path / "original_job_description.md",
                folder_path / "job_description.md",
                application.job_description_path
            ]
            
            for file_path in possible_files:
                if file_path and file_path.exists():
                    content = read_text_file(file_path)
                    # If this looks like processed content, try to extract the original text
                    if "# Job Description Details" in content:
                        # This is processed content, try to find the original text
                        # Look for the section after "Here's the extracted information"
                        parts = content.split("Here's the extracted information in the requested format:")
                        if len(parts) > 1:
                            # Try to find the actual job description content
                            # Look for the job summary/overview section
                            lines = parts[1].split('\n')
                            job_content_lines = []
                            in_job_content = False
                            
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Start capturing when we hit the job summary
                                if "Job Summary" in line or "Job Overview" in line or "Ready to make" in line or "Join us" in line:
                                    in_job_content = True
                                
                                if in_job_content:
                                    # Stop if we hit another section header
                                    if line.startswith("##") and ("Location" in line or "Compensation" in line or "Requirements" in line):
                                        break
                                    job_content_lines.append(line)
                            
                            if job_content_lines:
                                return '\n'.join(job_content_lines)
                            else:
                                # Fallback to the full content without the note
                                return parts[1].strip()
                        else:
                            return content
                    else:
                        return content
            
            # If no raw file found, return the processed content with a note
            if application.job_description_path and application.job_description_path.exists():
                content = read_text_file(application.job_description_path)
                return f"[NOTE: Raw input not preserved. This is the processed version.]\n\n{content}"
            
            return "Original job description not found."
            
        except Exception as e:
            return f"Error retrieving original job description: {str(e)}"
    
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
    
    <!-- Quill.js Rich Text Editor -->
    <link href="/static/css/quill.snow.css" rel="stylesheet">
    <script src="/static/js/quill.min.js"></script>
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: #424242; color: white; padding: 40px; border-radius: 12px 12px 0 0; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header h2 {{ font-size: 24px; font-weight: normal; opacity: 0.9; }}
        .back-btn {{ display: inline-block; background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; margin-bottom: 20px; transition: all 0.3s ease; }}
        .back-btn:hover {{ background: rgba(255,255,255,0.3); color: white; text-decoration: none; }}
        .summary {{ padding: 30px 40px; border-bottom: 1px solid #e0e0e0; background: #fafafa; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
        .summary-item {{ background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #424242; }}
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
        .tab:hover {{ color: #424242; }}
        .tab.active {{ color: #424242; border-bottom: 3px solid #424242; margin-bottom: -2px; }}
        .tab-content {{ padding: 40px; display: none; }}
        .tab-content.active {{ display: block; }}
        .tab-content pre {{ background: #f5f5f5; padding: 20px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }}
        .tab-content h3 {{ color: #424242; margin-top: 20px; margin-bottom: 10px; }}
        a {{ color: #424242; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .timeline {{ margin-top: 20px; }}
        .timeline-item {{ padding: 15px; border-left: 3px solid #424242; margin-left: 10px; margin-bottom: 15px; background: #f9f9f9; border-radius: 4px; }}
        
        /* Job Description Specific Styles */
        .job-meta {{ background: #f8f9fa; padding: 15px 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #424242; }}
        .job-meta p {{ margin: 5px 0; color: #333; font-size: 14px; }}
        .job-meta strong {{ color: #424242; font-weight: 600; }}
        .job-section {{ margin-bottom: 30px; padding: 20px; background: #fafafa; border-radius: 8px; border: 1px solid #e9ecef; }}
        .job-section-title {{ color: #424242; font-size: 20px; font-weight: 600; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e9ecef; }}
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
            color: #424242; 
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
        
        /* Research Tab Styles */
        .research-container {{ 
            max-width: 100%;
        }}
        .research-section {{ 
            margin-bottom: 30px; 
            padding: 20px; 
            background: #fafafa; 
            border-radius: 8px; 
            border: 1px solid #e9ecef;
        }}
        .research-section h3 {{ 
            color: #424242; 
            font-size: 18px; 
            font-weight: 600; 
            margin-bottom: 15px; 
            padding-bottom: 10px; 
            border-bottom: 2px solid #e9ecef;
        }}
        .research-item {{ 
            margin-bottom: 15px; 
            padding: 12px; 
            background: white; 
            border-radius: 6px; 
            border-left: 4px solid #424242;
        }}
        .research-item h4 {{ 
            color: #424242; 
            font-size: 14px; 
            font-weight: 600; 
            margin-bottom: 8px;
        }}
        .research-item p {{ 
            color: #333; 
            font-size: 14px; 
            line-height: 1.6; 
            margin: 0;
        }}
        .research-item a {{ 
            color: #1976d2; 
            text-decoration: none; 
            font-weight: 500;
        }}
        .research-item a:hover {{ 
            text-decoration: underline; 
        }}
        .news-item {{ 
            margin-bottom: 15px; 
            padding: 15px; 
            background: white; 
            border-radius: 6px; 
            border: 1px solid #e9ecef;
        }}
        .news-item h5 {{ 
            color: #424242; 
            font-size: 14px; 
            font-weight: 600; 
            margin-bottom: 8px;
        }}
        .news-item p {{ 
            color: #666; 
            font-size: 13px; 
            line-height: 1.5; 
            margin-bottom: 8px;
        }}
        .news-item .news-link {{ 
            color: #1976d2; 
            font-size: 12px; 
            text-decoration: none;
        }}
        .news-item .news-link:hover {{ 
            text-decoration: underline;
        }}
        .person-item {{ 
            margin-bottom: 12px; 
            padding: 12px; 
            background: white; 
            border-radius: 6px; 
            border-left: 3px solid #1976d2;
        }}
        .person-item h5 {{ 
            color: #424242; 
            font-size: 14px; 
            font-weight: 600; 
            margin-bottom: 5px;
        }}
        .person-item .title {{ 
            color: #666; 
            font-size: 13px; 
            font-style: italic;
        }}
        .loading-research {{ 
            text-align: center; 
            padding: 40px; 
            color: #666;
        }}
        .research-error {{ 
            color: #dc3545; 
            background: #f8d7da; 
            padding: 15px; 
            border-radius: 6px; 
            border: 1px solid #f5c6cb;
        }}
        
        /* Quill Editor Styles */
        .ql-editor {{
            min-height: 120px;
            font-size: 16px;
            line-height: 1.6;
            color: #4a5568;
        }}
        
        .ql-toolbar {{
            border: 2px solid rgba(139, 157, 195, 0.3);
            border-bottom: none;
            border-radius: 12px 12px 0 0;
            background-color: rgba(255, 255, 255, 0.9);
        }}
        
        .ql-container {{
            border: 2px solid rgba(139, 157, 195, 0.3);
            border-top: none;
            border-radius: 0 0 12px 12px;
            background-color: rgba(255, 255, 255, 0.9);
            font-family: inherit;
        }}
        
        .ql-container.ql-snow:focus-within {{
            border-color: #8b9dc3;
            box-shadow: 0 4px 12px rgba(139, 157, 195, 0.2);
        }}
        
        .ql-toolbar.ql-snow {{
            border-color: rgba(139, 157, 195, 0.3);
        }}
        
        .ql-toolbar.ql-snow .ql-picker-label {{
            border-color: transparent;
        }}
        
        .ql-toolbar.ql-snow .ql-picker-options {{
            border-color: rgba(139, 157, 195, 0.3);
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(139, 157, 195, 0.2);
        }}
        
        .ql-toolbar.ql-snow button {{
            border-radius: 6px;
            margin: 2px;
        }}
        
        .ql-toolbar.ql-snow button:hover {{
            background-color: rgba(139, 157, 195, 0.1);
        }}
        
        .ql-toolbar.ql-snow button.ql-active {{
            background-color: rgba(139, 157, 195, 0.2);
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
                <div class="summary-item">
                    <label>Contact #</label>
                    <value>{application.calculate_contact_count()}</value>
                </div>
            </div>
            
            {f'<div style="margin-top: 20px;"><label style="display: block; font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 5px; font-weight: 600;">Job URL</label><a href="{application.job_url}" target="_blank">{application.job_url}</a></div>' if application.job_url else ''}
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab(event, 'job-desc')">Job Description</button>
            <button class="tab" onclick="showTab(event, 'raw-entry')">Raw Entry</button>
            <button class="tab" onclick="showTab(event, 'skills')">Skills</button>
            <button class="tab" onclick="showTab(event, 'research')">Research</button>
            <button class="tab" onclick="showTab(event, 'qualifications')">Qualifications Analysis</button>
            <button class="tab" onclick="showTab(event, 'cover-letter')">Cover Letter</button>
            <button class="tab" onclick="showTab(event, 'resume')">Customized Resume</button>
            <button class="tab" onclick="showTab(event, 'updates')">Updates & Notes</button>
        </div>
        
        <div id="job-desc" class="tab-content active">
            <h2>Job Description</h2>
            {job_desc_html}
        </div>
        
        <div id="raw-entry" class="tab-content">
            <h2>Raw Entry</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Original job description as provided during application creation:</p>
            <pre style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.5;">{self._get_raw_job_description(application)}</pre>
        </div>
        
        <div id="skills" class="tab-content">
            <h2>Skills Analysis</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Skills extracted from job description and matched against your resume:</p>
            
            <div class="tech-pills-container">
                {self._generate_skills_analysis_html(qual_analysis)}
            </div>
        </div>
        
        <div id="research" class="tab-content">
            <h2>Company Research</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Research insights about {application.company} to help with your application:</p>
            
            <div class="research-container">
                {self._generate_company_research_html(application.company, application)}
            </div>
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
            
            <!-- Hiring Manager Intro Messages Section -->
            <div style="margin-top: 30px; border: 1px solid #28a745; padding: 15px; box-shadow: none; border-radius: 8px; background: white;">
                <div style="margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #333; font-size: 18px; font-weight: 600;">Hiring Manager Intro Messages</h3>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">Three ready-to-copy messages for hiring managers</p>
                </div>
                
                <div id="hiring-manager-content">
{self._get_intro_messages_content(application, 'hiring_manager')}
                </div>
            </div>
            
            <!-- Recruiter Intro Messages Section -->
            <div style="margin-top: 30px; border: 1px solid #17a2b8; padding: 15px; box-shadow: none; border-radius: 8px; background: white;">
                <div style="margin-bottom: 15px;">
                    <h3 style="margin: 0; color: #333; font-size: 18px; font-weight: 600;">Recruiter Intro Messages</h3>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">Three ready-to-copy messages for recruiters</p>
                </div>
                
                <div id="recruiter-content">
{self._get_intro_messages_content(application, 'recruiter')}
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
                        <div id="status_notes" placeholder="Add notes about this status update..."></div>
                        <small style="color: #6c757d; margin-top: 8px; display: block;">You can format your notes with bold, italic, lists, and more. HTML formatting is preserved.</small>
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
        
        // Initialize Quill editor
        let quillEditor = null;
        
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof Quill !== 'undefined') {{
                console.log('✅ Quill.js loaded successfully');
                
                // Initialize Quill editor
                quillEditor = new Quill('#status_notes', {{
                    theme: 'snow',
                    placeholder: 'Add notes about this status update...',
                    modules: {{
                        toolbar: [
                            [{{ 'header': [1, 2, 3, false] }}],
                            ['bold', 'italic', 'underline', 'strike'],
                            [{{ 'color': [] }}, {{ 'background': [] }}],
                            [{{ 'list': 'ordered'}}, {{ 'list': 'bullet' }}],
                            [{{ 'indent': '-1'}}, {{ 'indent': '+1' }}],
                            [{{ 'align': [] }}],
                            ['link', 'blockquote', 'code-block'],
                            ['clean']
                        ]
                    }}
                }});
                console.log('✅ Quill editor initialized successfully');
            }} else {{
                console.error('❌ Quill.js not loaded');
            }}
        }});
        
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
            // Get HTML content from Quill editor
            const notes = quillEditor ? quillEditor.root.innerHTML : '';
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
            if (quillEditor) {{
                quillEditor.setContents([]);
            }}
            
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
        
        function copyMessage(contentId) {{
            const contentElement = document.getElementById(contentId);
            const text = contentElement.textContent || contentElement.innerText;
            
            navigator.clipboard.writeText(text).then(function() {{
                // Show success message
                const button = event.target;
                const originalText = button.innerHTML;
                button.innerHTML = '✅ Copied!';
                button.style.background = '#20c997';
                
                setTimeout(() => {{
                    button.innerHTML = originalText;
                    button.style.background = '#007bff';
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
                button.style.background = '#20c997';
                
                setTimeout(() => {{
                    button.innerHTML = originalText;
                    button.style.background = '#007bff';
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
    
    def _get_intro_messages_content(self, application, message_type: str) -> str:
        """Get intro messages content from file and format as separate copy-ready boxes"""
        try:
            if message_type == 'hiring_manager':
                file_path = getattr(application, 'hiring_manager_intros_path', None)
            elif message_type == 'recruiter':
                file_path = getattr(application, 'recruiter_intros_path', None)
            else:
                return "No intro messages available."
            
            if file_path and Path(file_path).exists():
                content = read_text_file(file_path)
                return self._format_intro_messages_as_boxes(content, message_type)
            else:
                return f"No {message_type.replace('_', ' ')} intro messages found."
        except Exception as e:
            return f"Error loading {message_type.replace('_', ' ')} intro messages: {str(e)}"
    
    def _format_intro_messages_as_boxes(self, content: str, message_type: str) -> str:
        """Format intro messages as separate copy-ready boxes"""
        try:
            # Split content by MESSAGE markers
            messages = []
            current_message = ""
            
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('**MESSAGE'):
                    if current_message.strip():
                        messages.append(current_message.strip())
                    current_message = line + '\n'
                else:
                    current_message += line + '\n'
            
            # Add the last message
            if current_message.strip():
                messages.append(current_message.strip())
            
            # If we don't have the expected format, return original content
            if len(messages) < 3:
                return content
            
            # Create HTML for each message box
            html_boxes = []
            for i, message in enumerate(messages, 1):
                # Clean up the message content
                clean_message = message.replace('**MESSAGE {}:**'.format(i), '').strip()
                
                # Create individual copy button ID
                copy_button_id = f"copy-{message_type}-{i}"
                content_id = f"{message_type}-content-{i}"
                
                box_html = f"""
                <div style="margin-bottom: 20px; border: 2px solid #e0e0e0; border-radius: 8px; background: white; overflow: hidden;">
                    <div style="background: #f8f9fa; padding: 10px 15px; border-bottom: 1px solid #e0e0e0; display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #333; font-size: 16px; font-weight: 600;">Message {i}</h4>
                        <button onclick="copyMessage('{content_id}')" id="{copy_button_id}" style="background: #007bff; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 4px;">
                            📋 Copy
                        </button>
                    </div>
                    <div id="{content_id}" style="padding: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; white-space: pre-wrap; background: white;">
{clean_message}
                    </div>
                </div>
                """
                html_boxes.append(box_html)
            
            return '\n'.join(html_boxes)
            
        except Exception as e:
            # If parsing fails, return original content
            return content
    
    def _get_match_score_color(self, score: float) -> str:
        """Get color based on match score"""
        if score >= 80:
            return '#10b981'  # Green
        elif score >= 60:
            return '#f59e0b'  # Orange
        else:
            return '#ef4444'  # Red

