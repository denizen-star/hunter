"""Document generation service"""
import re
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
        
        # 2. Generate company research
        print("  → Generating company research...")
        self.generate_research(application)
        
        # 3. Generate cover letter
        print("  → Generating cover letter...")
        self.generate_cover_letter(application, qualifications, resume.full_name)
        
        # 3.5. Intro messages (deferred) - generated on demand from the Cover Letter tab
        print("  → Skipping intro messages (deferred; generate from Cover Letter tab if needed)")
        
        # 4. Customized resume (deferred) - generated on demand from the Resume tab
        print("  → Skipping customized resume (deferred; generate from Resume tab if needed)")
        
        # 5. Generate summary HTML page
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
        
        # Save text file (for backward compatibility)
        write_text_file(qualifications.detailed_analysis, qual_path)
        
        # Save JSON file with full QualificationAnalysis data (including preliminary_analysis)
        import json
        qual_json_path = application.folder_path / f"{job_title_clean}-Qualifications.json"
        with open(qual_json_path, 'w', encoding='utf-8') as f:
            json.dump(qualifications.to_dict(), f, indent=2, ensure_ascii=False)
        
        application.qualifications_path = qual_path
        application.match_score = qualifications.match_score
        
        return qualifications
    
    def _load_qualifications(self, application: Application) -> QualificationAnalysis:
        """Load qualifications from JSON file if available, otherwise parse from text file"""
        if not application.qualifications_path or not application.qualifications_path.exists():
            # Return empty qualifications if file doesn't exist
            return QualificationAnalysis(
                match_score=0.0,
                features_compared=0,
                strong_matches=[],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis="",
                preliminary_analysis=None
            )
        
        # Try to load from JSON file first (new format with preliminary_analysis)
        import json
        # Construct JSON path: replace .md extension with .json
        qual_json_path = application.qualifications_path.parent / (application.qualifications_path.stem + '.json')
        if qual_json_path.exists():
            try:
                with open(qual_json_path, 'r', encoding='utf-8') as f:
                    qual_data = json.load(f)
                    return QualificationAnalysis.from_dict(qual_data)
            except Exception as e:
                print(f"Warning: Could not load qualifications from JSON: {e}")
        
        # Fallback to text file parsing (old format)
        qual_content = read_text_file(application.qualifications_path)
        
        # Extract match score from text
        match_score = application.match_score if application.match_score else 0.0
        score_match = re.search(r'Match Score:?\s*(\d+)', qual_content, re.IGNORECASE)
        if score_match:
            match_score = float(score_match.group(1))
        
        # Create QualificationAnalysis object without preliminary_analysis (old format)
        return QualificationAnalysis(
            match_score=match_score,
            features_compared=0,
            strong_matches=[],
            missing_skills=[],
            partial_matches=[],
            soft_skills=[],
            recommendations=[],
            detailed_analysis=qual_content,
            preliminary_analysis=None  # Old format doesn't have this
        )
    
    def _load_research_content(self, application: Application) -> str:
        """Load research content from application if available"""
        if application.research_path and application.research_path.exists():
            try:
                return read_text_file(application.research_path)
            except Exception as e:
                print(f"  ⚠️ Warning: Could not load research file: {e}")
                return None
        return None
    
    def generate_cover_letter(
        self,
        application: Application,
        qualifications: QualificationAnalysis,
        candidate_name: str
    ) -> None:
        """Generate cover letter"""
        # Load research content if available
        research_content = self._load_research_content(application)
        
        cover_letter = self.ai_analyzer.generate_cover_letter(
            qualifications,
            application.company,
            application.job_title,
            candidate_name,
            research_content=research_content
        )
        
        # Insert compatibility text after "Dear Hiring Manager," using new format
        features_count = qualifications.features_compared if qualifications.features_compared > 0 else (len(qualifications.strong_matches) + len(qualifications.missing_skills))
        strong_matches_str = ', '.join(qualifications.strong_matches) if qualifications.strong_matches else 'core strengths'
        compatibility_text = f"\n\nMy profile shows a {qualifications.match_score:.0f}% compatibility score with the role, and {application.company} verified through weighted scoring methodology: Technical Skills (40%), Tools (30%), Experience (15%), and Soft Skills (10%) across {features_count} requirements. My strongest matched capabilities include {strong_matches_str}."
        
        if "Dear Hiring Manager," in cover_letter:
            # Insert after "Dear Hiring Manager," 
            cover_letter = cover_letter.replace("Dear Hiring Manager,", "Dear Hiring Manager," + compatibility_text)
        elif "Dear Hiring Manager" in cover_letter:
            # Handle case without comma
            cover_letter = cover_letter.replace("Dear Hiring Manager", "Dear Hiring Manager," + compatibility_text)
        
        # Remove the word "Scala" (case-insensitive) from cover letter - user prefers not to mention Scala
        # Use word boundaries to match only whole words, not parts of other words like "scalable"
        cover_letter = re.sub(r'\bScala\b', '', cover_letter, flags=re.IGNORECASE)
        # Clean up any double SPACES (but preserve newlines for paragraph breaks)
        cover_letter = re.sub(r'[ ]{2,}', ' ', cover_letter)  # Replace 2+ spaces with single space (only spaces, not newlines)
        cover_letter = re.sub(r'[ ]+([.,;:!?])', r'\1', cover_letter)  # Remove space before punctuation (only spaces, not newlines)
        # Clean up any triple+ newlines to double newlines (paragraph breaks)
        cover_letter = re.sub(r'\n{3,}', '\n\n', cover_letter)  # Normalize multiple newlines to double newlines
        
        # Remove any "current role/position/job" references as a backup cleanup
        # This catches any that might slip through the AI generation
        cover_letter = re.sub(r'\b(in|at|from)\s+my\s+current\s+(role|position|job|employer)\b', '', cover_letter, flags=re.IGNORECASE)
        cover_letter = re.sub(r'\bmy\s+current\s+(role|position|job|employer)\b', '', cover_letter, flags=re.IGNORECASE)
        cover_letter = re.sub(r'\bcurrent\s+(role|position|job)\b', '', cover_letter, flags=re.IGNORECASE)
        # Clean up any double spaces created by removals
        cover_letter = re.sub(r'[ ]{2,}', ' ', cover_letter)
        
        # Scan and improve the cover letter: fix grammar and remove repetitive phrases
        print("  → Scanning cover letter for grammar and repetitive phrases...")
        cover_letter = self.ai_analyzer.scan_and_improve_cover_letter(cover_letter)
        
        # Save to file
        name_clean = candidate_name.replace(' ', '')
        company_clean = application.company.replace(' ', '-')
        job_title_clean = application.job_title.replace(' ', '-')
        
        cover_letter_filename = f"{name_clean}-{company_clean}-{job_title_clean}-intro.md"
        cover_letter_path = application.folder_path / cover_letter_filename
        
        write_text_file(cover_letter, cover_letter_path)
        application.cover_letter_path = cover_letter_path
    
    def generate_research(self, application: Application) -> None:
        """Generate company research file for an application"""
        try:
            # Create a detailed, structured research prompt
            research_prompt = f"""You are a professional business researcher. Generate a comprehensive, company-specific research section for a job application.

COMPANY: {application.company}
JOB TITLE: {application.job_title}
JOB URL: {application.job_url if application.job_url else 'Not provided'}

Please provide a detailed, company-specific research section that follows this EXACT structure and format:

# Company Research: {application.company}

**Company Website:** https://www.{application.company.lower().replace(' ', '').replace(',', '').replace('-', '').replace('.', '')}.com

## Company Overview & Mission
- Provide a specific, accurate overview of {application.company}
- Include their actual mission statement and company values
- Mention their industry focus and market position
- Include company size, headquarters location, and key facts

## Recent News & Developments
- List 3-5 recent news items, developments, or announcements from {application.company}
- Include specific dates, achievements, partnerships, or expansions
- Focus on business-relevant news that shows company growth and direction

## Products & Services
- Detail the specific products and services that {application.company} offers
- Include their core business model and revenue streams
- Mention any unique or innovative offerings

## Market Position & Competitors
- Identify {application.company}'s main competitors in their industry
- Describe their competitive advantages and market position
- Include any industry rankings or recognition

# Role-Specific Research

## Key Personnel (Data & Analytics)
Research and identify key personnel at {application.company} who work in data, analytics, business intelligence, or technology roles. Include:
- Names and titles of key executives (CEO, CTO, VP of Data, Head of Analytics, etc.)
- Employees with leadership roles in Data, Business Intelligence, and Analytics
- Brief descriptions of their backgrounds and expertise
- Focus on people who would be relevant to a {application.job_title} role

## Key Challenges
- Specific challenges that {application.company} faces in data and analytics
- Industry-wide challenges that affect their business
- How a {application.job_title} role would address these challenges

## Why This Role/Company

### Career Alignment
- Specific reasons why this {application.job_title} role at {application.company} aligns with career goals
- How the role fits into the candidate's career progression
- Unique learning and growth opportunities

### Mission Resonance
- How {application.company}'s mission and values align with personal and professional goals
- Specific aspects of their culture and approach that are appealing
- How the candidate's values match the company's direction

### Unique Opportunities
- Specific opportunities this role offers that are unique to {application.company}
- Projects, technologies, or initiatives the candidate would work on
- Potential for impact and career advancement

# Research Sources
- List the specific sources used for this research
- Include company website, news articles, LinkedIn profiles, industry reports
- Note any limitations in publicly available information

IMPORTANT: 
1. Make this research specific to {application.company}, not generic
2. Use real information about the company, their industry, and their specific challenges and opportunities
3. Avoid generic statements that could apply to any company
4. Include actual URLs where possible
5. Use the EXACT heading structure shown above
6. Format as clean markdown with proper bullet points and sections

Format this as a professional research document that demonstrates thorough preparation and genuine interest in {application.company} specifically."""

            # Generate research content using AI
            print(f"  🤖 Generating structured research for {application.company}...")
            research_content = self.ai_analyzer._call_ollama(research_prompt)
            
            # Save to file
            company_clean = application.company.replace(' ', '-')
            job_title_clean = application.job_title.replace(' ', '-')
            research_filename = f"{company_clean}-{job_title_clean}-Research.md"
            research_path = application.folder_path / research_filename
            
            write_text_file(research_content, research_path)
            application.research_path = research_path
            print(f"  ✅ Research file generated: {research_path}")
            
        except Exception as e:
            print(f"  ❌ Error generating research file: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail the entire document generation if research fails
            # The Research tab will simply not appear
    
    def generate_intro_messages(
        self,
        application: Application,
        qualifications: QualificationAnalysis,
        candidate_name: str
    ) -> None:
        """Generate hiring manager and recruiter intro messages in parallel"""
        from concurrent.futures import ThreadPoolExecutor
        
        # Load research content if available
        research_content = self._load_research_content(application)
        
        def hm():
            return self.ai_analyzer.generate_hiring_manager_intros(
                qualifications,
                application.company,
                application.job_title,
                candidate_name,
                research_content=research_content
            )
        
        def rec():
            return self.ai_analyzer.generate_recruiter_intros(
                qualifications,
                application.company,
                application.job_title,
                candidate_name,
                research_content=research_content
            )
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            hm_future = executor.submit(hm)
            rec_future = executor.submit(rec)
            hiring_manager_intros = hm_future.result()
            recruiter_intros = rec_future.result()
        
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
            # Load qualifications (will use JSON if available, otherwise text)
            loaded_qualifications = self._load_qualifications(application)
            # Use provided qualifications if available (has preliminary_analysis), otherwise use loaded
            if qualifications.preliminary_analysis:
                # Use the provided qualifications (newly generated with preliminary_analysis)
                final_qualifications = qualifications
            else:
                # Use loaded qualifications (may have preliminary_analysis from JSON)
                final_qualifications = loaded_qualifications
            qual_content = final_qualifications.detailed_analysis
            cover_letter_content = read_text_file(application.cover_letter_path) if application.cover_letter_path else ""
            resume_content = read_text_file(application.custom_resume_path) if application.custom_resume_path else ""
            
            # Generate summary
            summary_html = self._create_summary_html(
                application,
                final_qualifications,
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
        
        # Special formatting for Job URL section
        if 'Job URL' in title_clean:
            if 'Not specified' in formatted_content:
                formatted_content = '''
                <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #6c757d;">
                    <p style="margin: 0; color: #6c757d; font-style: italic;">
                        <strong>Not specified</strong><br>
                        No job URL was provided in the job posting.
                    </p>
                </div>
                '''
            return f'''
        <div class="job-section">
            <h3 class="job-section-title">🔗 {title_clean}</h3>
            <div class="job-section-content">
                {formatted_content}
            </div>
        </div>
        '''
        
        # Special formatting for Other Information section
        if 'Other Information' in title_clean:
            return f'''
        <div class="job-section">
            <h3 class="job-section-title">ℹ️ {title_clean}</h3>
            <div class="job-section-content">
                {formatted_content}
            </div>
        </div>
        '''
        
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
    
    def _format_cover_letter_html(self, cover_letter_text: str) -> str:
        """Format cover letter text with proper paragraph breaks and HTML formatting"""
        if not cover_letter_text:
            return ''
        
        # Remove any residual signature or placeholder blocks before formatting
        cover_letter_text = re.sub(r'\n\s*Sincerely[^\n]*?(?:\n.*)?$', '', cover_letter_text, flags=re.IGNORECASE | re.DOTALL).strip()
        cover_letter_text = cover_letter_text.replace('[Your Contact Information]', '917.670.0693 or leacock.kervin@gmail.com')
        cover_letter_text = cover_letter_text.replace('[Your Actual Name]', 'Kervin Leacock')
        
        from html import escape
        
        # First, handle compatibility text that might be embedded with Dear Hiring Manager
        # Split by compatibility text first
        if 'Compatibility based on' in cover_letter_text and 'Dear Hiring Manager' in cover_letter_text:
            # Split at compatibility text
            parts = cover_letter_text.split('Compatibility based on', 1)
            if len(parts) == 2:
                before_compat = parts[0].strip()
                compat_and_after = 'Compatibility based on' + parts[1]
                
                # Extract methodology if present
                if 'Methodology:' in compat_and_after:
                    compat_parts = compat_and_after.split('Methodology:', 1)
                    compat_text = compat_parts[0].strip()
                    methodology_text = 'Methodology:' + compat_parts[1].strip()
                    after_methodology = methodology_text.split('\n\n', 1)
                    methodology_line = after_methodology[0].strip()
                    rest_of_letter = after_methodology[1].strip() if len(after_methodology) > 1 else ''
                else:
                    compat_parts = compat_and_after.split('\n\n', 1)
                    compat_text = compat_parts[0].strip()
                    methodology_line = ''
                    rest_of_letter = compat_parts[1].strip() if len(compat_parts) > 1 else ''
                
                # Process the parts before compatibility (should contain Dear Hiring Manager)
                paragraphs = []
                if before_compat:
                    # Split by newlines - empty lines indicate paragraph breaks
                    before_lines = before_compat.split('\n')
                    current_para = []
                    for line in before_lines:
                        line = line.strip()
                        if not line:
                            if current_para:
                                paragraphs.append(' '.join(current_para))
                                current_para = []
                        else:
                            current_para.append(line)
                    if current_para:
                        paragraphs.append(' '.join(current_para))
                
                # Add compatibility and methodology as separate paragraphs
                if compat_text:
                    paragraphs.append(compat_text)
                if methodology_line:
                    paragraphs.append(methodology_line)
                
                # Process rest of letter - apply intelligent paragraph splitting
                if rest_of_letter:
                    # First try splitting by double newlines
                    if '\n\n' in rest_of_letter:
                        rest_paragraphs = [p.strip() for p in rest_of_letter.split('\n\n') if p.strip()]
                    else:
                        # Split by single newlines
                        rest_lines = rest_of_letter.split('\n')
                        rest_paragraphs = []
                        current_para = []
                        for line in rest_lines:
                            line = line.strip()
                            if not line:
                                if current_para:
                                    rest_paragraphs.append(' '.join(current_para))
                                    current_para = []
                            else:
                                current_para.append(line)
                        if current_para:
                            rest_paragraphs.append(' '.join(current_para))
                    
                    # Apply intelligent splitting to rest paragraphs if they're too long
                    for rest_para in rest_paragraphs:
                        if len(rest_para) > 400:
                            # Try splitting by transition phrases
                            transition_patterns = [
                                r'(?<=\.)\s+(With [a-z]+ [a-z]+,)',
                                r'(?<=\.)\s+(My [a-z]+ [a-z]+)',
                                r'(?<=\.)\s+(I [a-z]+ [a-z]+)',
                                r'(?<=\.)\s+(In [a-z]+ [a-z]+)',
                                r'(?<=\.)\s+(Through [a-z]+ [a-z]+)',
                                r'(?<=\.)\s+(As [a-z]+ [a-z]+)',
                            ]
                            
                            split_found = False
                            for pattern in transition_patterns:
                                matches = list(re.finditer(pattern, rest_para, re.IGNORECASE))
                                if matches:
                                    # Split at all transition points
                                    split_points = [0] + [m.start() for m in matches] + [len(rest_para)]
                                    for i in range(len(split_points) - 1):
                                        part = rest_para[split_points[i]:split_points[i+1]].strip()
                                        if part and len(part) > 30:
                                            paragraphs.append(part)
                                    split_found = True
                                    break
                            
                            if not split_found:
                                # Split by sentences
                                sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', rest_para)
                                if len(sentences) > 1:
                                    current = []
                                    for sentence in sentences:
                                        sentence = sentence.strip()
                                        if sentence:
                                            current.append(sentence)
                                            if len(' '.join(current)) > 200 or len(current) >= 3:
                                                paragraphs.append(' '.join(current))
                                                current = []
                                    if current:
                                        paragraphs.append(' '.join(current))
                                else:
                                    paragraphs.append(rest_para)
                        else:
                            paragraphs.append(rest_para)
            else:
                # Fallback: regular processing
                paragraphs = []
                lines = cover_letter_text.strip().split('\n')
                current_paragraph = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        if current_paragraph:
                            paragraphs.append(' '.join(current_paragraph))
                            current_paragraph = []
                    else:
                        current_paragraph.append(line)
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
        else:
            # Regular paragraph detection: split by double newlines or single newlines after periods
            # First try splitting by double newlines
            if '\n\n' in cover_letter_text:
                paragraphs = [p.strip() for p in cover_letter_text.split('\n\n') if p.strip()]
            # If no double newlines, check if there are any newlines at all
            elif '\n' in cover_letter_text:
                # Try splitting by single newlines and detect paragraph boundaries
                paragraphs = []
                lines = cover_letter_text.strip().split('\n')
                current_paragraph = []
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        # Empty line = paragraph break
                        if current_paragraph:
                            paragraphs.append(' '.join(current_paragraph))
                            current_paragraph = []
                    elif line.endswith('.') and i < len(lines) - 1 and (not lines[i+1].strip() or lines[i+1].strip()[0].isupper()):
                        # End of sentence and next line is new paragraph or starts with capital
                        current_paragraph.append(line)
                        if len(current_paragraph) >= 3:  # Group 3+ sentences into paragraphs
                            paragraphs.append(' '.join(current_paragraph))
                            current_paragraph = []
                    else:
                        current_paragraph.append(line)
                
                # Add remaining paragraph
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
            else:
                # NO NEWLINES AT ALL - this is a continuous block, need to split intelligently
                # Split by transition phrases first
                paragraphs = []
                text = cover_letter_text.strip()
                
                # Try to find transition phrases that indicate new paragraphs
                transition_patterns = [
                    r'(?<=\.)\s+(With [a-z]+ [a-z]+,)',
                    r'(?<=\.)\s+(My [a-z]+ [a-z]+)',
                    r'(?<=\.)\s+(I [a-z]+ [a-z]+)',
                    r'(?<=\.)\s+(In [a-z]+ [a-z]+)',
                    r'(?<=\.)\s+(Through [a-z]+ [a-z]+)',
                    r'(?<=\.)\s+(As [a-z]+ [a-z]+)',
                    r'(?<=\.)\s+(Furthermore,)',
                    r'(?<=\.)\s+(Additionally,)',
                    r'(?<=\.)\s+(Moreover,)',
                ]
                
                split_found = False
                for pattern in transition_patterns:
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    if matches:
                        # Split at all transition points
                        split_points = [0] + [m.start() for m in matches] + [len(text)]
                        for i in range(len(split_points) - 1):
                            part = text[split_points[i]:split_points[i+1]].strip()
                            if part and len(part) > 30:
                                paragraphs.append(part)
                        split_found = True
                        break
                
                if not split_found:
                    # Fall back to splitting by sentences and grouping
                    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
                    if len(sentences) > 1:
                        current = []
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if sentence:
                                current.append(sentence)
                                # Group 2-3 sentences per paragraph
                                if len(' '.join(current)) > 200 or len(current) >= 3:
                                    paragraphs.append(' '.join(current))
                                    current = []
                        if current:
                            paragraphs.append(' '.join(current))
                    else:
                        # If we can't split by sentences, treat entire text as one paragraph
                        paragraphs = [text]
                
                # If we still have very long paragraphs, try to split them intelligently
                final_paragraphs = []
                for para in paragraphs:
                    # Very long paragraphs need to be split
                    if len(para) > 400:
                        # First try to split by common paragraph transition phrases
                        transition_patterns = [
                            r'(?<=\.)\s+(With [a-z]+ [a-z]+,)',
                            r'(?<=\.)\s+(My [a-z]+ [a-z]+)',
                            r'(?<=\.)\s+(I [a-z]+ [a-z]+)',
                            r'(?<=\.)\s+(In [a-z]+ [a-z]+)',
                            r'(?<=\.)\s+(Through [a-z]+ [a-z]+)',
                            r'(?<=\.)\s+(As [a-z]+ [a-z]+)',
                            r'(?<=\.)\s+(Furthermore,)',
                            r'(?<=\.)\s+(Additionally,)',
                            r'(?<=\.)\s+(Moreover,)',
                            r'(?<=\.)\s+(Therefore,)',
                            r'(?<=\.)\s+(However,)',
                        ]
                        
                        split_found = False
                        for pattern in transition_patterns:
                            matches = list(re.finditer(pattern, para, re.IGNORECASE))
                            if matches:
                                # Split at the first strong transition
                                split_point = matches[0].start()
                                first_part = para[:split_point].strip()
                                second_part = para[split_point:].strip()
                                if len(first_part) > 50:
                                    final_paragraphs.append(first_part)
                                final_paragraphs.append(second_part)
                                split_found = True
                                break
                        
                        if not split_found:
                            # Fall back to splitting by sentences
                            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', para)
                            if len(sentences) > 1:
                                current = []
                                for sentence in sentences:
                                    sentence = sentence.strip()
                                    if sentence:
                                        current.append(sentence)
                                        # Group 2-3 sentences per paragraph (shorter paragraphs look better)
                                        if len(' '.join(current)) > 200 or len(current) >= 3:
                                            final_paragraphs.append(' '.join(current))
                                            current = []
                                if current:
                                    final_paragraphs.append(' '.join(current))
                            else:
                                final_paragraphs.append(para)
                    elif len(para) > 300 and '. ' in para:
                        # Medium length paragraphs - split by sentences, group 2-3 sentences
                        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', para)
                        if len(sentences) > 3:
                            current = []
                            for sentence in sentences:
                                sentence = sentence.strip()
                                if sentence:
                                    current.append(sentence)
                                    if len(' '.join(current)) > 200 or len(current) >= 2:
                                        final_paragraphs.append(' '.join(current))
                                        current = []
                            if current:
                                final_paragraphs.append(' '.join(current))
                        else:
                            final_paragraphs.append(para)
                    else:
                        final_paragraphs.append(para)
                paragraphs = final_paragraphs
        
        # Format as HTML with proper paragraph tags
        formatted_parts = []
        for para in paragraphs:
            if para.strip():
                # Escape HTML special characters
                escaped_para = escape(para.strip())
                # Check if it's a salutation (starts with "Dear")
                if para.strip().startswith('Dear'):
                    formatted_parts.append(f'<p style="margin-bottom: 15px; font-size: 15px; line-height: 1.6;">{escaped_para}</p>')
                # Check if it's compatibility text
                elif para.strip().startswith('Compatibility based on'):
                    formatted_parts.append(f'<p style="margin-bottom: 15px; font-size: 15px; line-height: 1.6; font-weight: 500;">{escaped_para}</p>')
                # Check if it's methodology
                elif para.strip().startswith('Methodology:'):
                    formatted_parts.append(f'<p style="margin-bottom: 15px; font-size: 15px; line-height: 1.6; font-weight: 500;">{escaped_para}</p>')
                # Check if it's a closing (contains "Sincerely" or similar)
                elif para.strip().startswith('Sincerely') or para.strip().startswith('Best regards'):
                    formatted_parts.append(f'<p style="margin-top: 20px; margin-bottom: 5px; font-size: 15px; line-height: 1.6;">{escaped_para}</p>')
                # Regular paragraph
                else:
                    formatted_parts.append(f'<p style="margin-bottom: 15px; font-size: 15px; line-height: 1.6; text-align: justify;">{escaped_para}</p>')
        
        return '\n'.join(formatted_parts)
    
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
    
    def _parse_skill_requirement_status(self, job_description: str, skill: str) -> str:
        """Parse whether a skill is Required or Preferred from job description context"""
        import re
        
        job_desc_lower = job_description.lower()
        skill_lower = skill.lower()
        
        # Find all occurrences of the skill in the job description
        # Use word boundaries to avoid partial matches
        skill_pattern = r'\b' + re.escape(skill_lower) + r'\b'
        matches = list(re.finditer(skill_pattern, job_desc_lower))
        
        if not matches:
            return "Required"  # Default to Required if skill not found
        
        # Check context around each occurrence (50 characters before and after)
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(job_desc_lower), match.end() + 50)
            context = job_desc_lower[start:end]
            
            # Check for preferred indicators
            preferred_patterns = [
                r'preferred',
                r'nice to have',
                r'nice-to-have',
                r'bonus',
                r'plus',
                r'optional',
                r'would be nice'
            ]
            for pattern in preferred_patterns:
                if re.search(pattern, context, re.IGNORECASE):
                    return "Preferred"
            
            # Check for required indicators
            required_patterns = [
                r'required',
                r'must have',
                r'must-have',
                r'must',
                r'essential',
                r'necessary',
                r'need',
                r'required:'
            ]
            for pattern in required_patterns:
                if re.search(pattern, context, re.IGNORECASE):
                    return "Required"
        
        # Default to Required if no indicator found
        return "Required"
    
    def _generate_qualifications_tables_html(self, qualifications: QualificationAnalysis, application: Application) -> str:
        """Generate HTML tables for Qualifications Analysis section"""
        if not qualifications.preliminary_analysis:
            # Fallback to old format if preliminary_analysis not available
            return f'<pre>{qualifications.detailed_analysis}</pre>'
        
        prelim = qualifications.preliminary_analysis
        
        # Get job description for requirement parsing
        job_description = ""
        if application.job_description_path and application.job_description_path.exists():
            job_description = read_text_file(application.job_description_path)
        
        # Cache requirement status parsing to avoid repeated regex searches
        requirement_status_cache = {}
        
        # Build Table 1: Detailed skills table
        # Group matches by job_skill to avoid duplicates
        job_skills_map = {}  # job_skill -> list of matches
        
        # Process exact matches - SHOW ALL MATCHES, NO FILTERING
        for match in prelim.get('exact_matches', []):
            job_skill = match.get('job_skill', '')
            matched_skill = match.get('skill', '')  # This is the candidate skill
            
            if not job_skill or not matched_skill:
                continue
            
            category = match.get('category', 'Unknown')
            
            if job_skill not in job_skills_map:
                # Cache requirement status to avoid repeated parsing
                if job_skill not in requirement_status_cache:
                    requirement_status_cache[job_skill] = self._parse_skill_requirement_status(job_description, job_skill)
                
                job_skills_map[job_skill] = {
                    'requirement_status': requirement_status_cache[job_skill],
                    'matches': [],
                    'skill_category': category
                }
            
            # Add this match
            job_skills_map[job_skill]['matches'].append({
                'matched_with': matched_skill,
                'match_type': 'Strong',
                'category': category
            })
            # Update category if we have a better one
            if category != 'Unknown' and job_skills_map[job_skill]['skill_category'] == 'Unknown':
                job_skills_map[job_skill]['skill_category'] = category
        
        # Process partial matches - SHOW ALL MATCHES, NO FILTERING
        for match in prelim.get('partial_matches', []):
            job_skill = match.get('job_skill', '')
            matched_skill = match.get('skill', '')
            
            if not job_skill or not matched_skill:
                continue
            
            category = match.get('category', 'Unknown')
            
            if job_skill not in job_skills_map:
                # Cache requirement status to avoid repeated parsing
                if job_skill not in requirement_status_cache:
                    requirement_status_cache[job_skill] = self._parse_skill_requirement_status(job_description, job_skill)
                
                job_skills_map[job_skill] = {
                    'requirement_status': requirement_status_cache[job_skill],
                    'matches': [],
                    'skill_category': category
                }
            
            # Add this match
            job_skills_map[job_skill]['matches'].append({
                'matched_with': matched_skill,
                'match_type': 'Partial',
                'category': category
            })
            # Update category if we have a better one
            if category != 'Unknown' and job_skills_map[job_skill]['skill_category'] == 'Unknown':
                job_skills_map[job_skill]['skill_category'] = category
        
        # Process unmatched skills
        for job_skill in prelim.get('unmatched_job_skills', []):
            if not job_skill or job_skill in job_skills_map:
                continue  # Skip if already matched
            
            # Cache requirement status to avoid repeated parsing
            if job_skill not in requirement_status_cache:
                requirement_status_cache[job_skill] = self._parse_skill_requirement_status(job_description, job_skill)
            
            job_skills_map[job_skill] = {
                'requirement_status': requirement_status_cache[job_skill],
                'matches': [{
                    'matched_with': '----',
                    'match_type': 'No Match',
                    'category': 'Unknown'
                }],
                'skill_category': 'Unknown'
            }
        
        # Convert to table rows - one row per job skill, showing all matches
        table1_rows = []
        for job_skill, skill_data in sorted(job_skills_map.items()):
            matches = skill_data['matches']
            # If multiple matches, show the best match type first
            matches.sort(key=lambda x: {'Strong': 0, 'Partial': 1, 'No Match': 2}.get(x['match_type'], 3))
            
            # Count matches by type
            match_count = len([m for m in matches if m['match_type'] in ['Strong', 'Partial']])
            total_matches = len(matches)
            
            # Create one row per match (but grouped by job_skill)
            for i, match in enumerate(matches):
                table1_rows.append({
                    'job_skill': job_skill if i == 0 else '',  # Only show job skill in first row
                    'requirement_status': skill_data['requirement_status'] if i == 0 else '',
                    'match_count': match_count if i == 0 else '',  # Show count only in first row
                    'matched_with': match['matched_with'],
                    'match_type': match['match_type'],
                    'skill_category': match.get('category', skill_data['skill_category'])
                })
        
        # Build Table 2: Category summary
        category_stats = {}
        
        # Count unique job skills by category (not matches)
        unique_job_skills_by_category = {}
        for job_skill, skill_data in job_skills_map.items():
            category = skill_data['skill_category']
            if category not in unique_job_skills_by_category:
                unique_job_skills_by_category[category] = set()
            unique_job_skills_by_category[category].add(job_skill)
        
        # Count matched vs unmatched by category
        for job_skill, skill_data in job_skills_map.items():
            category = skill_data['skill_category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'matched': 0}
            
            category_stats[category]['total'] += 1
            # Check if this job skill has any match (Strong or Partial)
            has_match = any(m['match_type'] in ['Strong', 'Partial'] for m in skill_data['matches'])
            if has_match:
                category_stats[category]['matched'] += 1
        
        # Generate HTML for Table 1
        table1_html = """
        <div style="margin-bottom: 30px;">
            <h3 style="margin-bottom: 15px; color: #333; font-size: 18px;">Skills Matching Details</h3>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; font-size: 14px;">
                <thead>
                    <tr style="background: #f9fafb; border-bottom: 2px solid #e5e7eb;">
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Job Skill</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Skill Category</th>
                        <th style="padding: 12px; text-align: center; font-weight: 600; color: #374151;"># Matches</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Matched with</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Match Type</th>
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Category</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for row in table1_rows:
            match_type_color = {
                'Strong': '#10b981',
                'Partial': '#f59e0b',
                'No Match': '#ef4444'
            }.get(row['match_type'], '#6b7280')
            
            requirement_color = {
                'Required': '#ef4444',
                'Preferred': '#3b82f6'
            }.get(row['requirement_status'], '#6b7280')
            
            # Use rowspan styling for grouped rows (show job_skill only in first row)
            job_skill_cell = f"<td style=\"padding: 12px; color: #1f2937; font-weight: 500;\">{row['job_skill']}</td>" if row['job_skill'] else "<td style=\"padding: 12px;\"></td>"
            requirement_cell = f"<td style=\"padding: 12px;\"><span style=\"color: {requirement_color}; font-weight: 500;\">{row['requirement_status']}</span></td>" if row['requirement_status'] else "<td style=\"padding: 12px;\"></td>"
            match_count_cell = f"<td style=\"padding: 12px; text-align: center; color: #6b7280; font-weight: 500;\">{row['match_count']}</td>" if row['match_count'] != '' else "<td style=\"padding: 12px;\"></td>"
            
            table1_html += f"""
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        {job_skill_cell}
                        {requirement_cell}
                        {match_count_cell}
                        <td style="padding: 12px; color: #6b7280;">{row['matched_with']}</td>
                        <td style="padding: 12px;">
                            <span style="color: {match_type_color}; font-weight: 500;">{row['match_type']}</span>
                        </td>
                        <td style="padding: 12px; color: #6b7280;">{row['skill_category']}</td>
                    </tr>
            """
        
        table1_html += """
                </tbody>
            </table>
        </div>
        """
        
        # Generate HTML for Table 2
        table2_html = """
        <div>
            <h3 style="margin-bottom: 15px; color: #333; font-size: 18px;">Category Summary</h3>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; font-size: 14px;">
                <thead>
                    <tr style="background: #f9fafb; border-bottom: 2px solid #e5e7eb;">
                        <th style="padding: 12px; text-align: left; font-weight: 600; color: #374151;">Category</th>
                        <th style="padding: 12px; text-align: right; font-weight: 600; color: #374151;"># Job Skills</th>
                        <th style="padding: 12px; text-align: right; font-weight: 600; color: #374151;"># Matched Skills</th>
                        <th style="padding: 12px; text-align: right; font-weight: 600; color: #374151;">Match Ratio</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for category, stats in sorted(category_stats.items()):
            total = stats['total']
            matched = stats['matched']
            ratio = (matched / total * 100) if total > 0 else 0
            ratio_color = '#10b981' if ratio >= 75 else '#f59e0b' if ratio >= 50 else '#ef4444'
            
            table2_html += f"""
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px; color: #1f2937; font-weight: 500;">{category}</td>
                        <td style="padding: 12px; text-align: right; color: #6b7280;">{total}</td>
                        <td style="padding: 12px; text-align: right; color: #6b7280;">{matched}</td>
                        <td style="padding: 12px; text-align: right;">
                            <span style="color: {ratio_color}; font-weight: 500;">{ratio:.1f}%</span>
                        </td>
                    </tr>
            """
        
        table2_html += """
                </tbody>
            </table>
        </div>
        """
        
        return table1_html + table2_html
    
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
            # Don't set a fallback URL - let AI find the actual website
            # Only use a guessed URL if AI completely fails and we have no other option
            
            # Use web search to find company information
            research_data = self._search_company_info(company_name, research_data)
            
            # Only set a fallback URL if AI didn't find one AND we're using fallback data
            if not research_data.get('website'):
                # Try to generate a reasonable URL, but mark it as unverified
                company_clean = company_name.lower().replace(' ', '').replace(',', '').replace('.', '').replace('llc', '').replace('inc', '').replace('corp', '').replace('corporation', '')
                # Don't set it - let the display logic handle missing URLs gracefully
                # research_data['website'] = f"https://www.{company_clean}.com"
            
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
            
            # Look for timestamped raw files (new pattern)
            import glob
            raw_files = list(folder_path.glob("*-raw.txt"))
            if raw_files:
                # Get the most recent raw file
                raw_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                return read_text_file(raw_files[0])
            
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
    
    def _generate_checklist_html(self, application: Application) -> str:
        """Generate checklist HTML for the Hero section - matches sample design"""
        checklist_items = application.checklist_items or {}
        
        # Define checklist items with display names
        checklist_definitions = {
            "application_submitted": "Application Submitted",
            "linkedin_message_sent": "LinkedIn Message Sent",
            "contact_email_found": "Contact Email Found",
            "email_verified": "Email Verified",
            "email_sent": "Email Sent",
            "message_read": "Message Read",
            "profile_viewed": "Profile Viewed",
            "response_received": "Response Received",
            "followup_sent": "Follow-up Sent",
            "interview_scheduled": "Interview Scheduled",
            "interview_completed": "Interview Completed",
            "thank_you_sent": "Thank You Sent"
        }
        
        # Generate checklist items HTML
        checklist_items_html = []
        for key, display_name in checklist_definitions.items():
            checked = "checked" if checklist_items.get(key, False) else ""
            checklist_items_html.append(f'''
                <div class="checklist-item">
                    <input type="checkbox" id="checklist_{key}" {checked} onchange="updateChecklistItem('{key}', this.checked)">
                                        <label for="checklist_{key}">{display_name}</label>
                </div>
            ''')
        
        checklist_grid = '\n'.join(checklist_items_html)
        
        # Get latest completed item for pill display
        latest_item = application.get_latest_completed_checklist_item()
        checklist_definitions = {
            "application_submitted": "Application Submitted",
            "linkedin_message_sent": "LinkedIn Message Sent",
            "contact_email_found": "Contact Email Found",
            "email_verified": "Email Verified",
            "email_sent": "Email Sent",
            "message_read": "Message Read",
            "profile_viewed": "Profile Viewed",
            "response_received": "Response Received",
            "followup_sent": "Follow-up Sent",
            "interview_scheduled": "Interview Scheduled",
            "interview_completed": "Interview Completed",
            "thank_you_sent": "Thank You Sent"
        }
        latest_display = checklist_definitions.get(latest_item, "") if latest_item else ""
        
        return f'''
                    <div class="header-checklist">
        <div class="checklist-container">
            <div class="checklist-header" onclick="toggleChecklist()">
                                <div class="checklist-title">Checklist</div>
                                <button type="button" class="checklist-toggle" onclick="event.stopPropagation(); toggleChecklist()">
                                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                    </svg>
                                </button>
            </div>
                            <div class="checklist-pill" id="checklistPill" style="display: {'block' if latest_display else 'none'}; margin-top: var(--space-sm); padding: 4px 10px; background: #f3f4f6; color: #6b7280; border-radius: 12px; font-size: 11px; font-weight: 500;">{latest_display or ''}</div>
                            <div id="checklist-content" class="checklist-collapsed" style="margin-top: var(--space-sm);">
                <div class="checklist-grid">
                    {checklist_grid}
                                </div>
                </div>
            </div>
        </div>
        '''
    
    def _generate_badge_display(self, application: Application) -> str:
        """Generate badge display HTML for application hero section"""
        try:
            from app.services.badge_calculation_service import BadgeCalculationService
            
            badge_service = BadgeCalculationService()
            badge_data = badge_service.calculate_badges_for_application(
                application.id,
                application.company
            )
            
            # Define status progression order (for determining highest badge)
            status_progression = [
                'Ready to Connect',      # Deep Diver (+10)
                'Pending Reply',         # Profile Magnet (+3)
                'Connected - Initial',   # Qualified Lead (+15)
                'In Conversation',       # Conversation Starter (+20)
                'Meeting Scheduled',     # Scheduler Master (+30)
                'Meeting Complete',      # Rapport Builder (+50)
                'Strong Connection',     # Relationship Manager (+2, recurring)
                'Referral Partner'       # Super Connector (+100)
            ]
            
            # Status to badge mapping for progression
            status_to_badge_progression = {
                'Ready to Connect': 'deep_diver',
                'Pending Reply': 'profile_magnet',
                'Connected - Initial': 'qualified_lead',
                'In Conversation': 'conversation_starter',
                'Meeting Scheduled': 'scheduler_master',
                'Meeting Complete': 'rapport_builder',
                'Strong Connection': 'relationship_manager',
                'Referral Partner': 'super_connector'
            }
            
            # Get badge definitions for display (needed for both branches)
            badge_definitions = badge_service.badge_definitions
            
            if badge_data['contacts_count'] == 0:
                # No contacts - show the first badge to earn (Deep Diver)
                first_badge_id = 'deep_diver'
                first_badge_def = badge_definitions[first_badge_id]
                next_badge_item = {
                    'badge_id': first_badge_id,
                    'badge_def': first_badge_def,
                    'earned': False,
                    'count': 0,
                    'required': 1,
                    'points': first_badge_def['points'],
                    'progress': 0
                }
                next_badge_html = self._generate_badge_item_html(next_badge_item, False)
                earned_badges_html = []
                total_points = 0
            else:
                # Has contacts - find the highest badge achieved across all contacts
                from app.services.networking_processor import NetworkingProcessor
                networking_processor = NetworkingProcessor()
                all_contacts = networking_processor.list_all_contacts()
                
                # Filter contacts matching this application's company
                matched_contacts = [
                    c for c in all_contacts
                    if c.company_name.lower().strip() == application.company.lower().strip()
                ]
                
                # Status mapping for legacy statuses
                status_mapping = {
                    'Ready to Contact': 'Ready to Connect',
                    'Contacted - Sent': 'Pending Reply',
                    'Contacted - No Response': 'Pending Reply',
                    'Contacted - Replied': 'Connected - Initial',
                    'New Connection': 'Connected - Initial',
                    'Cold/Archive': 'Cold/Inactive',
                    'Action Pending - You': 'In Conversation',
                    'Action Pending - Them': 'In Conversation',
                    'Nurture (1-3 Mo.)': 'Strong Connection',
                    'Nurture (4-6 Mo.)': 'Strong Connection',
                    'Inactive/Dormant': 'Dormant'
                }
                
                # Find highest status across all contacts
                highest_status_index = -1
                highest_status = None
                
                for contact in matched_contacts:
                    normalized_status = status_mapping.get(contact.status, contact.status)
                    if normalized_status in status_progression:
                        status_index = status_progression.index(normalized_status)
                        if status_index > highest_status_index:
                            highest_status_index = status_index
                            highest_status = normalized_status
                
                # Get the highest badge achieved
                max_badge_html = ''
                if highest_status and highest_status in status_to_badge_progression:
                    max_badge_id = status_to_badge_progression[highest_status]
                    max_badge_def = badge_definitions[max_badge_id]
                    
                    # Calculate cumulative points up to this status
                    cumulative_points = 0
                    for i in range(highest_status_index + 1):
                        status_in_progression = status_progression[i]
                        badge_id_for_status = status_to_badge_progression.get(status_in_progression)
                        if badge_id_for_status:
                            badge_def_for_status = badge_definitions[badge_id_for_status]
                            cumulative_points += badge_def_for_status['points']
                    
                    max_badge_item = {
                        'badge_id': max_badge_id,
                        'badge_def': max_badge_def,
                        'earned': True,
                        'count': len([c for c in matched_contacts if status_mapping.get(c.status, c.status) == highest_status]),
                        'required': 1,
                        'points': max_badge_def['points'],
                        'progress': 100
                    }
                    max_badge_html = self._generate_badge_item_html(max_badge_item, True)
                    total_points = cumulative_points
                
                # Find next badge to earn (next in progression after highest)
                next_badge_html = ''
                if highest_status_index >= 0 and highest_status_index < len(status_progression) - 1:
                    next_status = status_progression[highest_status_index + 1]
                    next_badge_id = status_to_badge_progression.get(next_status)
                    if next_badge_id:
                        next_badge_def = badge_definitions[next_badge_id]
                        next_badge_item = {
                            'badge_id': next_badge_id,
                            'badge_def': next_badge_def,
                            'earned': False,
                            'count': 0,
                            'required': 1,
                            'points': next_badge_def['points'],
                            'progress': 0
                        }
                        next_badge_html = self._generate_badge_item_html(next_badge_item, False)
                elif highest_status_index == -1:
                    # No contacts have reached any badge status, show first badge
                    first_badge_id = 'deep_diver'
                    first_badge_def = badge_definitions[first_badge_id]
                    next_badge_item = {
                        'badge_id': first_badge_id,
                        'badge_def': first_badge_def,
                        'earned': False,
                        'count': 0,
                        'required': 1,
                        'points': first_badge_def['points'],
                        'progress': 0
                    }
                    next_badge_html = self._generate_badge_item_html(next_badge_item, False)
                
                earned_badges_html = [max_badge_html] if max_badge_html else []
                
            # Complete badge section HTML - horizontal layout: earned badges on left, next badge on right
            return f'''
            <div class="badge-section" style="padding: 12px; background: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; cursor: pointer;" onclick="toggleBadgeSection()">
                    <h3 style="margin: 0; font-size: 13px; font-weight: 600; color: #1f2937;">Networking Rewards</h3>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="font-size: 16px; font-weight: 700; color: #3b82f6; margin-left: 16px;">{total_points} pts</div>
                        <svg id="badge-toggle-icon" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #6b7280; transition: transform 0.3s ease;">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </div>
                </div>
                <div id="badge-grid-content" style="display: flex; gap: 12px; align-items: flex-start; max-height: 300px; overflow-y: auto;">
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; flex: 1;">
                        {''.join(earned_badges_html)}
                    </div>
                    {f'<div style="flex-shrink: 0;">{next_badge_html}</div>' if next_badge_html else ''}
                </div>
                <script>
                    let badgeSectionExpanded = true;
                    function toggleBadgeSection() {{
                        const content = document.getElementById('badge-grid-content');
                        const icon = document.getElementById('badge-toggle-icon');
                        if (!badgeSectionExpanded) {{
                            content.style.display = 'flex';
                            icon.style.transform = 'rotate(0deg)';
                            badgeSectionExpanded = true;
                        }} else {{
                            content.style.display = 'none';
                            icon.style.transform = 'rotate(180deg)';
                            badgeSectionExpanded = false;
                        }}
                    }}
                </script>
            </div>
            '''
        except Exception as e:
            print(f"Warning: Could not generate badge display: {e}")
            return ''
    
    def _generate_rewards_by_category_html(self, application: Application) -> str:
        """Generate rewards by category HTML for Rewards tab"""
        try:
            from app.services.badge_calculation_service import BadgeCalculationService
            
            badge_service = BadgeCalculationService()
            badge_data = badge_service.calculate_badges_for_application(
                application.id,
                application.company
            )
            
            if badge_data['contacts_count'] == 0:
                return '<p style="color: #6b7280; padding: 20px;">No networking contacts linked to this application yet.</p>'
            
            points_by_category = badge_data.get('points_by_category', {})
            total_points = badge_data['total_points']
            badges = badge_data['badges']
            
            # Group badges by category
            category_badges = {
                'prospecting': [],
                'outreach': [],
                'engagement': [],
                'nurture': []
            }
            
            for badge_id, badge_info in badges.items():
                if badge_id not in badge_service.badge_definitions:
                    continue
                
                badge_def = badge_service.badge_definitions[badge_id]
                phase = badge_def['phase']
                
                if badge_info['count'] > 0:
                    category_badges[phase].append({
                        'badge_id': badge_id,
                        'badge_def': badge_def,
                        'count': badge_info['count'],
                        'points': badge_info['points'],
                        'total_points': badge_info['points'] * badge_info['count'] if badge_def.get('recurring', False) else badge_info['points']
                    })
            
            # Category display names
            category_names = {
                'prospecting': 'Prospecting',
                'outreach': 'Outreach',
                'engagement': 'Engagement',
                'nurture': 'Nurture'
            }
            
            # Category colors
            category_colors = {
                'prospecting': {'color': '#3b82f6', 'bg_color': '#dbeafe'},
                'outreach': {'color': '#10b981', 'bg_color': '#d1fae5'},
                'engagement': {'color': '#f59e0b', 'bg_color': '#fef3c7'},
                'nurture': {'color': '#8b5cf6', 'bg_color': '#ede9fe'}
            }
            
            # Generate card HTML for each category
            category_cards = []
            for phase in ['prospecting', 'outreach', 'engagement', 'nurture']:
                category_points = points_by_category.get(phase, 0)
                phase_badges = category_badges[phase]
                badges_count = len(phase_badges)
                
                cat_colors = category_colors.get(phase, {'color': '#6b7280', 'bg_color': '#f3f4f6'})
                
                category_cards.append(f'''
                    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; position: relative; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);">
                        <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: {cat_colors['color']};"></div>
                        <div style="font-size: 13px; font-weight: 600; color: #1f2937; margin-bottom: 8px;">{category_names[phase]}</div>
                        <div style="font-size: 24px; font-weight: 700; color: {cat_colors['color']}; margin-bottom: 8px;">{category_points}</div>
                        <div style="font-size: 11px; color: #6b7280; margin-bottom: 8px;">points</div>
                        <div style="height: 1px; background: #e5e7eb; margin: 8px 0;"></div>
                        <div style="font-size: 12px; color: #6b7280;">Badges Earned</div>
                        <div style="font-size: 16px; font-weight: 600; color: #1f2937;">{badges_count}</div>
                    </div>
                ''')
            
            return f'''
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600; color: #1f2937;">Networking Rewards by Category</h2>
                    <div style="font-size: 18px; font-weight: 700; color: #3b82f6;">{total_points} pts</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                    {''.join(category_cards)}
                </div>
            </div>
            '''
        except Exception as e:
            print(f"Warning: Could not generate rewards by category: {e}")
            return f'<p style="color: #ef4444;">Error loading rewards: {str(e)}</p>'
    
    def _generate_badge_item_html(self, badge_data_item: dict, earned: bool) -> str:
        """Generate HTML for a single badge item"""
        badge_def = badge_data_item['badge_def']
        count = badge_data_item['count']
        required = badge_data_item['required']
        points = badge_data_item['points']
        progress = badge_data_item['progress']
        
        # Build tooltip with requirements
        tooltip_parts = [badge_def['description']]
        if 'trigger_status' in badge_def:
            tooltip_parts.append(f"Trigger: {badge_def['trigger_status']}")
        if required > 1:
            if 'time_window' in badge_def:
                tooltip_parts.append(f"Requires: {required} {badge_def['time_window']}s")
            else:
                tooltip_parts.append(f"Requires: {required} contacts")
        tooltip_text = " | ".join(tooltip_parts)
        
        badge_class = 'badge-unlocked' if earned else 'badge-locked'
        border_color = '#3b82f6' if earned else '#d1d5db'
        icon_color = '#3b82f6' if earned else '#9ca3af'
        points_color = '#10b981' if earned else '#9ca3af'
        
        return f'''
            <div class="badge-item {badge_class}" title="{tooltip_text}" style="padding: 10px; min-width: 160px; border: 2px solid {border_color}; border-radius: 8px; background: white; cursor: help;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div class="badge-icon" style="width: 24px; height: 24px; font-size: 16px; color: {icon_color}; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                        {'✓' if earned else '○'}
                    </div>
                    <div class="badge-info" style="flex: 1; min-width: 0;">
                        <div class="badge-name" style="font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #1f2937;">{badge_def['name']}</div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <div class="badge-progress" style="flex: 1; height: 6px; min-width: 50px; background: #e5e7eb; border-radius: 3px; overflow: hidden;">
                                <div class="badge-progress-fill" style="width: {progress}%; height: 100%; background: {'linear-gradient(90deg, #3b82f6, #10b981)' if earned else '#d1d5db'}; transition: width 0.3s ease;"></div>
                            </div>
                            <div class="badge-count" style="font-size: 11px; color: #6b7280; white-space: nowrap; font-weight: 500;">{count} contact{'s' if count != 1 else ''}</div>
                        </div>
                    </div>
                    <div class="badge-points" style="font-size: 13px; font-weight: 700; color: {points_color}; white-space: nowrap;">+{points}</div>
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
        
        # Generate status tags HTML
        status_tags = self._get_status_tags(application)
        status_tags_html = ''.join([f'                    <span class="status-pill tag {tag_class}">{tag_name}</span>\n' for tag_name, tag_class in status_tags])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{application.company} - {application.job_title}</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    
    <!-- Google Fonts - Poppins -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Quill.js Rich Text Editor -->
    <link href="/static/css/quill.snow.css" rel="stylesheet">
    <script src="/static/js/quill.min.js"></script>
    
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #fafafa;
            --bg-hover: #f9fafb;
            --bg-active: #f3f4f6;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --text-tertiary: #9ca3af;
            --border-primary: #e5e7eb;
            --border-light: #f3f4f6;
            --accent-blue: #3b82f6;
            --accent-blue-hover: #2563eb;
            --accent-blue-light: #eff6ff;
            --accent-green: #10b981;
            --font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-xs: 12px;
            --font-sm: 14px;
            --font-base: 16px;
            --font-lg: 18px;
            --font-xl: 20px;
            --font-2xl: 24px;
            --font-3xl: 32px;
            --font-medium: 500;
            --font-semibold: 600;
            --font-bold: 700;
            --space-xs: 4px;
            --space-sm: 8px;
            --space-md: 16px;
            --space-lg: 24px;
            --space-xl: 32px;
            --radius-sm: 6px;
            --radius-md: 8px;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.08);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            color: #2d3748;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        /* Sidebar - Smaller */
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 180px;
            height: 100vh;
            background: #ffffff;
            border-right: 1px solid #e5e7eb;
            z-index: 1000;
            padding: 20px 0;
            overflow-y: auto;
        }}
        
        .sidebar-header {{
            padding: 0 16px 16px 16px;
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 12px;
        }}
        
        .sidebar-header h3 {{
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin: 0;
        }}
        
        .sidebar-menu {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .sidebar-menu li {{
            margin: 0;
        }}
        
        .sidebar-menu a {{
            display: block;
            padding: 10px 16px;
            color: #6b7280;
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        
        .sidebar-menu a:hover {{
            background: #f9fafb;
            color: #1f2937;
            border-left-color: #3b82f6;
        }}
        
        .sidebar-menu a.active {{
            background: #f3f4f6;
            color: #1f2937;
            border-left-color: #3b82f6;
            font-weight: 600;
        }}
        
        /* Main Container */
        .container {{
            width: calc(100vw - 180px);
            margin-left: 0;
            min-height: 100vh;
            background: #fafafa;
            box-sizing: border-box;
        }}
        
        /* Header */
        .header {{
            background: #ffffff;
            border-bottom: 1px solid #e5e7eb;
            padding: 20px 32px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        
        .header-top > div:first-child {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
        }}
        
        .back-link {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #3b82f6;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: color 0.2s ease;
        }}
        
        .back-link:hover {{
            color: #2563eb;
        }}
        
        .header-actions {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        
        .btn {{
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            color: #1f2937;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .btn:hover {{
            background: #f9fafb;
            border-color: #d1d5db;
        }}
        
        .btn-primary {{
            background: #3b82f6;
            color: #ffffff;
            border-color: #3b82f6;
        }}
        
        .btn-primary:hover {{
            background: #2563eb;
            border-color: #2563eb;
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
        }}
        
        .header-subtitle {{
            font-size: 14px;
            color: #6b7280;
            margin-top: 4px;
        }}
        
        /* Content */
        .content {{
            padding: 32px;
            max-width: 100%;
        }}
        
        /* Application Header Card */
        .app-header-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .app-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #6b7280;
        }}
        
        .meta-icon {{
            width: 16px;
            height: 16px;
            color: #9ca3af;
        }}
        
        .tag {{
            font-size: 12px;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 12px;
            display: inline-block;
        }}
        
        .tag-green {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .tag-blue {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .tag-gray {{
            background: #f3f4f6;
            color: #4b5563;
        }}
        
        .tag-red {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .status-pill {{
            display: inline-flex;
            align-items: center;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .match-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
        }}
        
        .match-percentage {{
            font-size: 18px;
            font-weight: 700;
            line-height: 1;
        }}
        
        .match-score-label {{
            font-size: 12px;
            font-weight: 500;
            color: #6b7280;
        }}
        
        /* Two Column Layout */
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            width: 100%;
            max-width: 100%;
        }}
        
        @media (max-width: 968px) {{
            .two-column {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .content-section {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin: 0;
        }}
        
        .section-content {{
            color: #4b5563;
            line-height: 1.8;
        }}
        
        .section-content h3 {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            margin: 20px 0 12px 0;
        }}
        
        .section-content h3:first-child {{
            margin-top: 0;
        }}
        
        .section-content ul {{
            margin-left: 20px;
            margin-bottom: 12px;
        }}
        
        .section-content li {{
            margin-bottom: 8px;
        }}
        
        .timeline {{
            position: relative;
            padding-left: 40px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 8px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #e5e7eb;
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 32px;
            display: flex;
            align-items: flex-start;
            gap: 16px;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -32px;
            top: 4px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #3b82f6;
            border: 3px solid #ffffff;
            box-shadow: 0 0 0 2px #e5e7eb;
            z-index: 1;
        }}
        
        .timeline-date {{
            font-size: 13px;
            color: #6b7280;
            min-width: 140px;
            flex-shrink: 0;
        }}
        
        .timeline-content {{
            flex: 1;
            font-size: 14px;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .timeline-notes-content {{
            margin-left: 0 !important;
            padding-left: 0 !important;
        }}
        
        .timeline-notes-content p,
        .timeline-notes-content div,
        .timeline-notes-content ul,
        .timeline-notes-content ol,
        .timeline-notes-content li {{
            margin-left: 0 !important;
            padding-left: 0 !important;
        }}
        
        .timeline-description {{
            flex: 1;
        }}
        
        .timeline-status {{
            display: inline-block;
            font-size: 12px;
            font-weight: 500;
            padding: 4px 12px;
            border-radius: 16px;
            white-space: nowrap;
        }}
        
        /* Tabs Container */
        .tabs-container {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            overflow: hidden;
        }}
        
        .tabs-header {{
            display: flex;
            border-bottom: 1px solid #e5e7eb;
            background: #fafafa;
            overflow-x: auto;
        }}
        
        .tabs {{
            display: flex;
            border-bottom: 1px solid var(--border-primary);
            padding: 0 var(--space-xl);
            background: var(--bg-secondary);
            overflow-x: auto;
        }}
        
        .back-btn {{ 
            display: inline-block; 
            background: var(--bg-hover); 
            color: var(--text-primary); 
            padding: 10px var(--space-md); 
            border-radius: var(--radius-sm); 
            text-decoration: none; 
            margin-bottom: var(--space-lg); 
            transition: all 0.2s ease;
            border: 1px solid var(--border-primary);
            font-size: var(--font-sm);
            font-weight: var(--font-medium);
        }}
        .back-btn:hover {{ 
            background: var(--bg-active); 
            color: var(--text-primary); 
            text-decoration: none; 
        }}
        
        /* Checklist Styles */
        .checklist-container {{ 
            background: var(--bg-primary); 
            border-radius: var(--radius-md); 
            padding: 4px; 
        }}
        .checklist-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: var(--space-sm); 
            cursor: pointer; 
            padding: 4px;
            border-bottom: 1px solid var(--border-primary);
        }}
        .checklist-header:hover {{
            color: var(--text-primary);
        }}
        
        /* Badge Display Styles */
        .badge-section {{
            padding: 12px;
            background: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }}
        
        .badge-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 8px;
        }}
        
        .badge-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            transition: all 0.2s ease;
            min-height: auto;
        }}
        
        .badge-item:hover {{
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        
        .badge-locked {{
            opacity: 0.6;
        }}
        
        .badge-unlocked {{
            opacity: 1;
            border-color: #3b82f6;
        }}
        
        .badge-icon {{
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 700;
            color: #3b82f6;
            flex-shrink: 0;
        }}
        
        .badge-locked .badge-icon {{
            color: #9ca3af;
        }}
        
        .badge-info {{
            flex: 1;
            min-width: 0;
        }}
        
        .badge-name {{
            font-size: 12px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .badge-progress {{
            flex: 1;
            height: 4px;
            min-width: 40px;
            background: #e5e7eb;
            border-radius: 2px;
            overflow: hidden;
        }}
        
        .badge-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #10b981);
            transition: width 0.3s ease;
        }}
        
        .badge-locked .badge-progress-fill {{
            background: #d1d5db;
        }}
        
        .badge-count {{
            font-size: 10px;
            color: #6b7280;
            white-space: nowrap;
        }}
        
        .badge-points {{
            font-size: 12px;
            font-weight: 700;
            color: #10b981;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        
        .badge-locked .badge-points {{
            color: #9ca3af;
        }}
        
        .checklist-title {{ 
            font-size: var(--font-sm); 
            font-weight: var(--font-semibold); 
            letter-spacing: 0.3px; 
            color: var(--text-secondary);
        }}
        .checklist-toggle {{ 
            background: transparent; 
            border: none; 
            color: var(--text-secondary); 
            padding: 0;
            cursor: pointer; 
            font-size: var(--font-xs); 
            display: flex;
            align-items: center;
            gap: 4px;
            transition: color 0.2s ease;
        }}
        .checklist-toggle:hover {{ 
            color: var(--text-primary);
        }}
        .checklist-toggle svg {{
            width: 14px;
            height: 14px;
            transition: transform 0.2s ease;
        }}
        .checklist-toggle.expanded svg {{
            transform: rotate(180deg);
        }}
        .checklist-collapsed {{ display: none !important; }}
        .checklist-expanded {{ display: block; }}
        .checklist-pill {{ 
            display: inline-block; 
            background: var(--bg-active); 
            color: var(--text-secondary); 
            padding: 4px 10px; 
            border-radius: 12px; 
            font-size: var(--font-xs); 
            font-weight: var(--font-medium); 
            margin-top: var(--space-sm); 
        }}
        .checklist-grid {{ 
            display: grid; 
            grid-template-columns: 1fr; 
            gap: var(--space-sm); 
            margin-top: var(--space-sm); 
        }}
        .checklist-item {{ 
            display: flex; 
            align-items: center; 
            gap: var(--space-sm); 
            padding: var(--space-sm); 
            border-radius: var(--radius-sm); 
            transition: background 0.2s; 
        }}
        .checklist-item:hover {{ 
            background: var(--bg-hover); 
        }}
        .checklist-item label {{ 
            cursor: pointer; 
            user-select: none; 
        }}
        .checklist-item input[type="checkbox"] {{ 
            width: 16px; 
            height: 16px; 
            cursor: pointer; 
            accent-color: var(--accent-blue); 
        }}
        .checklist-item label {{ 
            font-size: var(--font-xs); 
            cursor: pointer; 
            flex: 1; 
            color: var(--text-primary);
            line-height: 1.4; 
        }}
        .checklist-item input[type="checkbox"]:checked + label {{ 
            font-weight: var(--font-medium); 
        }}
        .summary {{ 
            padding: var(--space-xl); 
            border-bottom: 1px solid var(--border-light); 
            background: var(--bg-secondary); 
        }}
        .summary-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: var(--space-lg); 
            margin-top: var(--space-lg); 
        }}
        .summary-item {{ 
            background: var(--bg-primary); 
            padding: var(--space-md); 
            border-radius: var(--radius-md); 
            border-left: 3px solid var(--accent-blue);
            box-shadow: var(--shadow-sm);
        }}
        .summary-item label {{ 
            display: block; 
            font-size: var(--font-xs); 
            text-transform: uppercase; 
            color: var(--text-secondary); 
            margin-bottom: 5px; 
            font-weight: var(--font-semibold); 
        }}
        .summary-item value {{ 
            display: block; 
            font-size: var(--font-base); 
            color: var(--text-primary); 
        }}
        .match-score {{ 
            font-size: var(--font-3xl); 
            font-weight: var(--font-bold); 
            color: {match_score_color}; 
            text-align: center; 
            padding: var(--space-lg); 
            background: var(--bg-primary); 
            border-radius: var(--radius-md);
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-sm);
            margin-bottom: var(--space-lg);
        }}
        .status-badge {{ 
            display: inline-block; 
            padding: 4px 10px; 
            border-radius: 12px; 
            font-size: var(--font-xs); 
            font-weight: var(--font-medium); 
            text-transform: capitalize; 
        }}
        .status-pending {{ background: #fef3c7; color: #92400e; }}
        .status-applied {{ background: #dbeafe; color: #1e40af; }}
        .status-contacted-someone {{ background: var(--bg-active); color: var(--text-secondary); }}
        .status-company-response {{ background: var(--accent-blue-light); color: #1e40af; }}
        .status-contacted-hiring-manager {{ background: var(--accent-blue-light); color: #1e40af; }}
        .status-scheduled-interview {{ background: #fef3c7; color: #92400e; }}
        .status-interviewed {{ background: #d1fae5; color: #065f46; }}
        .status-interview-notes {{ background: #d1fae5; color: #065f46; }}
        .status-interview-follow-up {{ background: #fce7f3; color: #9f1239; }}
        .status-offered {{ background: #d1fae5; color: #065f46; }}
        .status-rejected {{ background: #fee2e2; color: #991b1b; }}
        .status-accepted {{ background: #d1fae5; color: #065f46; }}
        .tabs {{ 
            display: flex; 
            border-bottom: 1px solid var(--border-primary); 
            padding: 0 var(--space-xl); 
            background: var(--bg-secondary); 
            overflow-x: auto;
        }}
        .tab {{ 
            padding: 14px var(--space-lg); 
            cursor: pointer; 
            border: none; 
            background: none; 
            font-size: var(--font-sm); 
            font-weight: var(--font-medium); 
            color: var(--text-secondary); 
            transition: all 0.2s; 
            font-family: var(--font-family);
            white-space: nowrap;
        }}
        .tab:hover {{ 
            color: var(--text-primary); 
            background: var(--bg-active);
        }}
        .tab.active {{ 
            color: var(--accent-blue); 
            border-bottom: 3px solid var(--accent-blue); 
            margin-bottom: -1px; 
            font-weight: var(--font-semibold);
        }}
        .tab-content {{ 
            padding: var(--space-xl); 
            display: none; 
        }}
        .tab-content.active {{ 
            display: block; 
        }}
        .tab-content pre {{ 
            background: var(--bg-secondary); 
            padding: var(--space-lg); 
            border-radius: var(--radius-md); 
            overflow-x: auto; 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            border: 1px solid var(--border-primary);
        }}
        .tab-content h3 {{ 
            color: var(--text-primary); 
            margin-top: var(--space-lg); 
            margin-bottom: var(--space-sm); 
            font-size: var(--font-lg);
            font-weight: var(--font-semibold);
        }}
        a {{ 
            color: var(--accent-blue); 
            text-decoration: none; 
        }}
        a:hover {{ 
            text-decoration: underline; 
        }}
        .timeline {{ 
            margin-top: var(--space-lg); 
        }}
        .timeline-item {{ 
            padding: var(--space-md); 
            border-left: 3px solid var(--accent-blue); 
            margin-left: var(--space-sm); 
            margin-bottom: var(--space-md); 
            background: var(--bg-secondary); 
            border-radius: var(--radius-sm);
        }}
        .timeline-item img {{ max-width: 100%; height: auto; border-radius: 6px; margin: 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        
        /* Job Description Specific Styles */
        .job-meta {{ 
            background: var(--bg-secondary); 
            padding: var(--space-md) var(--space-lg); 
            border-radius: var(--radius-md); 
            margin-bottom: var(--space-lg); 
            border-left: 3px solid var(--accent-blue);
            border: 1px solid var(--border-primary);
        }}
        .job-meta p {{ 
            margin: 5px 0; 
            color: var(--text-primary); 
            font-size: var(--font-sm); 
        }}
        .job-meta strong {{ 
            color: var(--text-primary); 
            font-weight: var(--font-semibold); 
        }}
        .job-section {{ 
            margin-bottom: var(--space-xl); 
            padding: var(--space-lg); 
            background: var(--bg-secondary); 
            border-radius: var(--radius-md); 
            border: 1px solid var(--border-primary);
        }}
        .job-section-title {{ 
            color: var(--text-primary); 
            font-size: var(--font-lg); 
            font-weight: var(--font-semibold); 
            margin-bottom: var(--space-md); 
            padding-bottom: var(--space-sm); 
            border-bottom: 1px solid var(--border-light); 
        }}
        .job-section-content {{ 
            color: var(--text-primary); 
            font-size: var(--font-base); 
            line-height: 1.7; 
        }}
        .job-section-content p {{ 
            margin: 10px 0; 
        }}
        .job-section-content ul {{ 
            margin: 10px 0 10px 20px; 
        }}
        .job-section-content li {{ 
            margin: 8px 0; 
            padding-left: 5px; 
        }}
        .job-section-content strong {{ 
            color: var(--text-primary); 
            font-weight: var(--font-semibold); 
        }}
        #job-desc h2 {{ 
            color: var(--text-primary); 
            font-size: var(--font-2xl); 
            margin-bottom: var(--space-lg); 
            font-weight: var(--font-semibold);
        }}
        
        /* Technology Pills Styles */
        .tech-pills-container {{ margin-top: 20px; }}
        .tech-pills-section {{ margin-bottom: 20px; }}
        .tech-pills-label {{ 
            font-size: var(--font-sm); 
            font-weight: var(--font-semibold); 
            color: var(--text-primary); 
            margin-bottom: var(--space-sm); 
            display: flex; 
            align-items: center; 
            gap: var(--space-sm);
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
            background: #d1fae5; 
            color: #065f46;
            border: 1px solid var(--accent-green);
        }}
        .tech-pill-yellow {{ 
            background: #fef3c7; 
            color: #92400e;
            border: 1px solid #f59e0b;
        }}
        .tech-pill-red {{ 
            background: #fee2e2; 
            color: #991b1b;
            border: 1px solid #ef4444;
        }}
        .tech-legend {{ 
            margin-top: var(--space-md); 
            padding: var(--space-md); 
            background: var(--bg-secondary); 
            border-radius: var(--radius-sm); 
            font-size: var(--font-xs); 
            color: var(--text-secondary);
            display: flex;
            gap: var(--space-lg);
            flex-wrap: wrap;
            border: 1px solid var(--border-primary);
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
            margin-bottom: var(--space-xl); 
            padding: var(--space-lg); 
            background: var(--bg-secondary); 
            border-radius: var(--radius-md); 
            border: 1px solid var(--border-primary);
        }}
        .research-section h3 {{ 
            color: var(--text-primary); 
            font-size: var(--font-lg); 
            font-weight: var(--font-semibold); 
            margin-bottom: var(--space-md); 
            padding-bottom: var(--space-sm); 
            border-bottom: 1px solid var(--border-light);
        }}
        .research-item {{ 
            margin-bottom: var(--space-md); 
            padding: var(--space-md); 
            background: var(--bg-primary); 
            border-radius: var(--radius-sm); 
            border-left: 3px solid var(--accent-blue);
            box-shadow: var(--shadow-sm);
        }}
        .research-item h4 {{ 
            color: var(--text-primary); 
            font-size: var(--font-sm); 
            font-weight: var(--font-semibold); 
            margin-bottom: var(--space-sm);
        }}
        .research-item p {{ 
            color: var(--text-primary); 
            font-size: var(--font-sm); 
            line-height: 1.6; 
            margin: 0;
        }}
        .research-item a {{ 
            color: var(--accent-blue); 
            text-decoration: none; 
            font-weight: var(--font-medium);
        }}
        .research-item a:hover {{ 
            text-decoration: underline; 
        }}
        .news-item {{ 
            margin-bottom: var(--space-md); 
            padding: var(--space-md); 
            background: var(--bg-primary); 
            border-radius: var(--radius-sm); 
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-sm);
        }}
        .news-item h5 {{ 
            color: var(--text-primary); 
            font-size: var(--font-sm); 
            font-weight: var(--font-semibold); 
            margin-bottom: var(--space-sm);
        }}
        .news-item p {{ 
            color: var(--text-secondary); 
            font-size: var(--font-xs); 
            line-height: 1.5; 
            margin-bottom: var(--space-sm);
        }}
        .news-item .news-link {{ 
            color: var(--accent-blue); 
            font-size: var(--font-xs); 
            text-decoration: none;
        }}
        .news-item .news-link:hover {{ 
            text-decoration: underline;
        }}
        .person-item {{ 
            margin-bottom: var(--space-sm); 
            padding: var(--space-md); 
            background: var(--bg-primary); 
            border-radius: var(--radius-sm); 
            border-left: 3px solid var(--accent-blue);
            box-shadow: var(--shadow-sm);
        }}
        .person-item h5 {{ 
            color: var(--text-primary); 
            font-size: var(--font-sm); 
            font-weight: var(--font-semibold); 
            margin-bottom: 5px;
        }}
        .person-item .title {{ 
            color: var(--text-secondary); 
            font-size: var(--font-xs); 
            font-style: italic;
        }}
        .loading-research {{ 
            text-align: center; 
            padding: var(--space-xl); 
            color: var(--text-secondary);
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
            font-size: 11pt !important;
            font-family: var(--font-family) !important;
            font-weight: 400 !important;
            line-height: 1.5 !important;
            color: var(--text-primary) !important;
            text-align: justify !important;
        }}
        
        /* Override any pasted content font styles */
        .ql-editor * {{
            font-family: var(--font-family) !important;
            font-size: 11pt !important;
            color: var(--text-primary) !important;
        }}
        
        .ql-editor p,
        .ql-editor div,
        .ql-editor span {{
            font-family: var(--font-family) !important;
            font-size: 11pt !important;
            color: var(--text-primary) !important;
            text-align: justify !important;
            line-height: 1.5 !important;
        }}
        
        /* Paragraph spacing and alignment */
        .ql-editor p {{
            margin-bottom: 0.5em !important;
            text-align: justify !important;
            line-height: 1.5 !important;
        }}
        
        /* Ensure all text elements use justified alignment */
        .ql-editor p[style*="text-align"],
        .ql-editor div[style*="text-align"],
        .ql-editor span[style*="text-align"] {{
            text-align: justify !important;
        }}
        
        .ql-toolbar {{
            border: 1px solid var(--border-primary);
            border-bottom: none;
            border-radius: var(--radius-md) var(--radius-md) 0 0;
            background-color: var(--bg-primary);
        }}
        
        .ql-container {{
            border: 1px solid var(--border-primary);
            border-top: none;
            border-radius: 0 0 var(--radius-md) var(--radius-md);
            background-color: var(--bg-primary);
            font-family: var(--font-family);
        }}
        
        .ql-container.ql-snow:focus-within {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px var(--accent-blue-light);
        }}
        
        .ql-toolbar.ql-snow {{
            border-color: var(--border-primary);
        }}
        
        .ql-toolbar.ql-snow .ql-picker-label {{
            border-color: transparent;
        }}
        
        .ql-toolbar.ql-snow .ql-picker-options {{
            border-color: var(--border-primary);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-md);
            background: var(--bg-primary);
        }}
        
        .ql-toolbar.ql-snow button {{
            border-radius: var(--radius-sm);
            margin: 2px;
        }}
        
        .ql-toolbar.ql-snow button:hover {{
            background-color: var(--bg-hover);
        }}
        
        .ql-toolbar.ql-snow button.ql-active {{
            background-color: var(--bg-active);
        }}
        
        /* Percentage Widget Styles */
        .percentage-widget-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .percentage-input-group {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .percentage-input-group label {{
            font-weight: 500;
            color: #4b5563;
            font-size: 13px;
        }}
        
        #percentage-input {{
            width: 60px;
            padding: 6px 10px;
            border: 2px solid #e5e7eb;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            text-align: center;
            transition: border-color 0.3s;
        }}
        
        #percentage-input:focus {{
            outline: none;
            border-color: #3b82f6;
        }}
        
        .percentage-progress-fill.green {{
            background: #3491B2;
        }}
        
        .percentage-progress-fill.orange {{
            background: #3491B2;
        }}
    </style>
</head>
<body>
    <!-- Sidebar Navigation - Injected by shared-menu.js -->
    
    <!-- Main Container -->
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-top">
                <div style="flex: 1;">
                    <a href="/dashboard" class="back-link" style="display: inline-block; margin-bottom: 8px;">
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                        </svg>
                        Back to Applications
                    </a>
                    <h1 style="margin: 0 0 4px 0;">{application.company} - {application.job_title}</h1>
                    <div class="header-subtitle">Application ID: {application.id}</div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 12px;">
                    <div class="header-actions">
                        <button class="btn" onclick="toggleFlag('{application.id}', {str(application.flagged).lower()})">
                            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path>
                            </svg>
                            Flag
                        </button>
                        <button class="btn btn-primary" onclick="const tabs = Array.from(document.querySelectorAll('.tab')); const updatesTab = tabs.find(t => t.textContent.includes('Updates') || t.textContent.includes('updates')); if (updatesTab) {{ showTab(updatesTab, 'updates'); }}">Update Status</button>
            </div>
                    
                <div style="margin-top: 16px; width: 100%;">
                    {self._generate_badge_display(application)}
                </div>
            </div>
        </div>
            </div>
            
        <!-- Content -->
        <div class="content">
            <!-- Application Header Card -->
            <div class="app-header-card">
                <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
{status_tags_html}                    <span class="match-pill">
                        <span class="match-percentage" data-score="{qualifications.match_score:.0f}" style="color: {match_score_color};">{qualifications.match_score:.0f}%</span>
                        <span class="match-score-label">Match Score</span>
                    </span>
                </div>
                <div class="app-meta" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <div class="meta-item">
                        <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        </svg>
                        <span>{job_details.get('location', 'N/A')}</span>
                </div>
                    <div class="meta-item">
                        <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span>{job_details.get('salary_range', '$0')}</span>
                </div>
                    <div class="meta-item">
                        <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <span>Applied: {format_for_display(application.created_at).split(',')[0]}</span>
                </div>
                    <div class="meta-item">
                        <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <span>Posted: {job_details.get('posted_date', 'N/A')}</span>
                </div>
                    <div class="meta-item">
                        <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                        </svg>
                        <span>Updated: {format_for_display(application.status_updated_at).split(',')[0]}</span>
                </div>
                    <div class="meta-item">
                        <svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                        <span>Contact #: {application.calculate_contact_count()}</span>
                </div>
                    {f'<div class="meta-item"><svg class="meta-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg><a href="{application.job_url}" target="_blank" style="color: #3b82f6; text-decoration: none;">View Job Posting</a></div>' if application.job_url else ''}
                </div>
            </div>
            
            <!-- Tabs Section -->
            <div class="tabs-container">
                <div class="tabs-header">
            <button type="button" class="tab active" onclick="showTab(this, 'job-desc')">JD</button>
            {self._generate_tab_button('raw-entry', 'Raw Entry', application.raw_job_description_path)}
            {self._generate_tab_button('skills', 'Skills', application.qualifications_path)}
            {self._generate_tab_button('research', 'Research', application.research_path or application.hiring_manager_intros_path)}
            {self._generate_tab_button('qualifications', 'Qualifications', application.qualifications_path)}
            {self._generate_tab_button('cover-letter', 'Cover Letter', application.cover_letter_path)}
            <button type="button" class="tab" onclick="showTab(this, 'resume')">Custom Resume</button>
            <button type="button" class="tab" onclick="showTab(this, 'networking')">Networking</button>
            <button type="button" class="tab" onclick="showTab(this, 'rewards')">Rewards</button>
            <button type="button" class="tab" onclick="showTab(this, 'updates')">Updates</button>
            <button type="button" class="tab" onclick="showTab(this, 'timeline')">Timeline</button>
        </div>
        
        <div id="job-desc" class="tab-content active">
            <h2>Job Description</h2>
            {job_desc_html}
            
            <!-- Qualifications Summary -->
            <div class="content-section" style="margin-top: 40px;">
                <div class="section-header">
                    <h2 class="section-title">Qualifications Summary</h2>
                </div>
                {self._generate_qualifications_summary_html(qualifications)}
            </div>
        </div>
        
        {self._generate_tab_content('raw-entry', 'Raw Entry', f'''
            <h2>Raw Entry</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Original job description as provided during application creation:</p>
            <pre style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.5;">{self._get_raw_job_description(application)}</pre>
        ''', application.raw_job_description_path)}
        
        {self._generate_tab_content('skills', 'Skills Analysis', f'''
            <h2>Skills Analysis</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Skills extracted from job description and matched against your resume:</p>
            
            <div class="tech-pills-container">
                {self._generate_skills_analysis_html(qual_analysis)}
            </div>
        ''', application.qualifications_path)}
        
        {self._generate_tab_content('research', 'Company Research', f'''
            <h2>Company Research</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Research insights about {application.company} to help with your application:</p>
            
            <div class="research-container">
                {self._generate_company_research_html(application.company, application)}
            </div>
        ''', application.research_path or application.hiring_manager_intros_path)}
        
        {self._generate_tab_content('qualifications', 'Qualifications Analysis', f'''
            <h2>Qualifications Analysis</h2>
            {self._generate_qualifications_tables_html(qualifications, application)}
        ''', application.qualifications_path)}
        
        {self._generate_tab_content('cover-letter', 'Cover Letter', f'''
            <h2>Cover Letter</h2>
            
            <!-- Analysis Summary Box (similar to the one from application creation) -->
            <div style="border: 1px solid #0099FF; padding: 15px; margin-bottom: 20px; box-shadow: none; border-radius: 8px; background: white;">
                <h3 style="color: #666; margin-bottom: 10px; font-size: 16px;">
                    Match Score: {qualifications.match_score:.0f}% - Application for {application.company} - {application.job_title}
                </h3>
                
                <!-- Introductory text before analysis summary -->
                <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #667eea;">
                    <p style="color: #333; font-size: 14px; line-height: 1.5; margin: 0;">
                        I reviewed our compatibility based on job posting, research and my experience with my proprietary ML Model and these are my findings:
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
                
                <!-- Methodology -->
                <div style="margin-bottom: 10px;">
                    <h4 style="color: #0099FF; margin-bottom: 5px; font-size: 12px; font-weight: 600;">Methodology</h4>
                    <p style="color: #666; font-size: 11px; line-height: 1.4;">
                        Our AI analyzes your resume against the job description using weighted scoring: 
                        Technical Skills (40%), Technologies/Tools (30%), Experience Level (15%), Soft Skills (10%), Other Factors (5%).
                    </p>
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
                
                <div id="cover-letter-content" style="background: #f5f5f5; padding: 30px 40px; border-radius: 8px; border: 1px solid #e0e0e0; font-family: Georgia, 'Times New Roman', serif; line-height: 1.6; max-height: 600px; overflow-y: auto; color: #333;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 30px; font-weight: 600;">
                        {application.job_title} - {application.company} - Intro
                    </div>
                    
                    {self._format_cover_letter_html(cover_letter)}
                    
                    <p style="margin-top: 30px; margin-bottom: 5px; font-size: 15px; line-height: 1.6;">Sincerely,</p>
                    <p style="margin-top: 5px; font-size: 15px; line-height: 1.6;">Kervin Leacock | 917.670.0693 | leacock.kervin@gmail.com</p>
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
        ''', application.cover_letter_path)}
        
        {self._generate_resume_tab_html(application, resume)}
        
        {self._generate_networking_tab_html(application)}
        
        <div id="updates" class="tab-content">
            <h2>Updates</h2>
            
            <!-- Update Status Form -->
            <div style="margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; border: 1px solid #e9ecef;">
                <form id="statusUpdateForm" onsubmit="submitStatusUpdate(event)">
                    <div style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center;">
                        <select id="new_status" required style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                            <option value="">-- Select Status --</option>
                            <option value="Pending">⏳ Pending</option>
                            <option value="Applied">✉️ Applied</option>
                            <option value="Contacted Someone">👥 Contacted Someone</option>
                            <option value="Company Response">🏢 Company Response</option>
                            <option value="Scheduled Interview">🗓️ Scheduled Interview</option>
                            <option value="Interview Notes">📝 Interview Notes</option>
                            <option value="Interview - Follow Up">🔁 Interview - Follow Up</option>
                            <option value="Offered">🎉 Offered</option>
                            <option value="Rejected">❌ Rejected</option>
                            <option value="Accepted">✅ Accepted</option>
                        </select>
                        <button type="button" onclick="copyStatusNotes(this)" style="background: #667eea; color: white; border: none; padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;">Copy</button>
                        <button type="button" id="clearTemplateBtn" style="background: #e9ecef; color: #333; border: none; padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;">Clear</button>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <div id="status_notes" placeholder="Add notes about this status update..."></div>
                    </div>
                    
                    <!-- Template Inserter -->
                    <div style="margin: 18px 0; padding: 12px; background: #ffffff; border: 1px dashed #cdd6e1; border-radius: 10px;">
                        <label for="template_selector" style="display: block; margin-bottom: 6px; font-weight: 600; color: #333;">
                            Insert from Template
                        </label>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <select id="template_selector" style="flex: 1; padding: 10px; border: 1px solid #d0d7de; border-radius: 8px; font-size: 14px; background: #f8fafc;">
                                <option value="">-- Select Template --</option>
                            </select>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                            <small style="color: #6c757d;">Selecting a template will populate the Notes editor. You can freely edit the text.</small>
                            <small id="status_notes_character_count" style="color: #6c757d; margin-left: 10px;">0 characters</small>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                        <button type="submit" id="updateStatusBtn" style="background: #d97706; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                            <span id="btnText">Update</span>
                        </button>
                        
                        <!-- Percentage Bar Widget -->
                        <div class="percentage-widget-container" id="percentage-widget-container" style="display: none; align-items: center; gap: 10px; width: 500px; background: white; padding: 12px; border-radius: 8px; border: 1px solid #e5e7eb;">
                            <div class="percentage-input-group" style="display: flex; align-items: center; gap: 6px; flex-shrink: 0;">
                                <label for="percentage-input" style="font-weight: 500; color: #4b5563; font-size: 13px;">%:</label>
                                <input type="number" id="percentage-input" min="0" max="100" value="75" step="1" style="width: 60px; padding: 6px 10px; border: 2px solid #e5e7eb; border-radius: 6px; font-size: 13px; font-weight: 600; text-align: center; transition: border-color 0.3s;">
                            </div>
                            <div id="percentage-bar-container" style="position: relative; flex: 1; height: 32px; display: flex; align-items: center; gap: 10px;">
                                <div class="percentage-progress-wrapper" style="position: relative; width: 100%; height: 32px; flex: 1;">
                                    <div class="percentage-progress-track" style="width: 100%; height: 100%; background: #f3f4f6; border-radius: 16px; position: relative; overflow: hidden;">
                                        <div class="percentage-progress-fill" id="percentage-progress-bar" style="height: 100%; border-radius: 16px; position: relative; transition: width 0.5s ease; width: 75%; background: #3491B2;"></div>
                                    </div>
                                </div>
                                <div class="percentage-text-display" id="percentage-text-display" style="font-size: 16px; font-weight: 600; color: #1f2937; min-width: 40px; text-align: right; flex-shrink: 0;">75%</div>
                            </div>
                        </div>
                    </div>
                </form>
                
                <div id="status-message" style="margin-top: 15px; padding: 10px; border-radius: 4px; display: none;"></div>
            </div>
                </div>
            </div>
        </div>
        
        {self._generate_timeline_tab_html(application)}
    </div>
    
    <script>
        // Application meta for this summary page
        const APPLICATION_ID = '{application.id}';
        const COMPANY = '{application.company}';
        const JOB_TITLE = '{application.job_title}';
        
        // Initialize Quill editor
        let quillEditor = null;
        let statusNotesCharacterCount = null;
        
        function updateStatusNotesCharacterCount() {{
            if (!statusNotesCharacterCount) {{
                return;
            }}
            
            if (!quillEditor) {{
                statusNotesCharacterCount.textContent = '0 characters';
                return;
            }}
            
            const text = quillEditor.getText();
            const normalizedText = text.endsWith('\\n') ? text.slice(0, -1) : text;
            const length = normalizedText.length;
            
            statusNotesCharacterCount.textContent = `${{length}} ${{length === 1 ? 'character' : 'characters'}}`;
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            statusNotesCharacterCount = document.getElementById('status_notes_character_count');
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
                            ['link', 'image', 'blockquote', 'code-block'],
                            ['clean']
                        ]
                    }}
                }});
                
                quillEditor.on('text-change', updateStatusNotesCharacterCount);
                updateStatusNotesCharacterCount();
                
                // Add image upload handler
                const toolbar = quillEditor.getModule('toolbar');
                toolbar.addHandler('image', function() {{
                    const input = document.createElement('input');
                    input.setAttribute('type', 'file');
                    input.setAttribute('accept', 'image/*');
                    input.click();
                    
                    input.onchange = async function() {{
                        const file = input.files[0];
                        if (file) {{
                            const formData = new FormData();
                            formData.append('image', file);
                            
                            try {{
                                showMessage('📤 Uploading image...', 'info');
                                
                                const response = await fetch('/api/upload-image', {{
                                    method: 'POST',
                                    body: formData
                                }});
                                
                                const result = await response.json();
                                
                                if (result.success) {{
                                    const range = quillEditor.getSelection();
                                    quillEditor.insertEmbed(range.index, 'image', result.url);
                                    showMessage('✅ Image uploaded successfully!', 'success');
                                }} else {{
                                    showMessage('❌ Failed to upload image: ' + result.error, 'error');
                                }}
                            }} catch (error) {{
                                console.error('Image upload error:', error);
                                showMessage('❌ Failed to upload image: ' + error.message, 'error');
                            }}
                        }}
                    }};
                }});
                
                // Add paste handler to normalize font styles to Montserrat 11px
                quillEditor.clipboard.addMatcher(Node.TEXT_NODE, function(node, delta) {{
                    // Remove any font-family or font-size attributes and normalize
                    const ops = [];
                    delta.ops.forEach(function(op) {{
                        if (op.attributes) {{
                            // Remove font-family and size attributes, they'll use the default
                            delete op.attributes['font-family'];
                            delete op.attributes['size'];
                        }}
                        ops.push(op);
                    }});
                    return {{ ops: ops }};
                }});
                
                quillEditor.clipboard.addMatcher(Node.ELEMENT_NODE, function(node, delta) {{
                    // Normalize all pasted elements
                    if (node.nodeName === 'P' || node.nodeName === 'DIV' || node.nodeName === 'SPAN') {{
                        const ops = [];
                        delta.ops.forEach(function(op) {{
                            if (op.attributes) {{
                                delete op.attributes['font-family'];
                                delete op.attributes['size'];
                            }}
                            ops.push(op);
                        }});
                        return {{ ops: ops }};
                    }}
                    return delta;
                }});
                
                // Additional paste normalization after paste event
                quillEditor.root.addEventListener('paste', function(e) {{
                    setTimeout(function() {{
                        const selection = quillEditor.getSelection();
                        if (selection) {{
                            // Get the content length that was pasted
                            const currentLength = quillEditor.getLength();
                            const pastedLength = currentLength - selection.index;
                            
                            if (pastedLength > 0) {{
                                // Normalize the pasted content to remove font formatting
                                quillEditor.formatText(selection.index, pastedLength, {{
                                    'font': false,
                                    'size': false
                                }}, 'api');
                            }}
                        }}
                    }}, 50);
                }}, true);
                
                console.log('✅ Quill editor initialized successfully');

                // Load templates and wire interactions
                loadTemplates();
                const selector = document.getElementById('template_selector');
                const clearBtn = document.getElementById('clearTemplateBtn');
                if (selector) {{
                    selector.addEventListener('change', onTemplateSelected);
                }}
                if (clearBtn) {{
                    clearBtn.addEventListener('click', function() {{
                        if (quillEditor) {{
                            quillEditor.setContents([]);
                            quillEditor.focus();
                            updateStatusNotesCharacterCount();
                        }}
                        const sel = document.getElementById('template_selector');
                        if (sel) {{ sel.value = ''; }}
                        
                        // Hide percentage widget when template is cleared
                        const widgetContainer = document.getElementById('percentage-widget-container');
                        if (widgetContainer) {{
                            widgetContainer.style.display = 'none';
                        }}
                    }});
                }}
            }} else {{
                console.error('❌ Quill.js not loaded');
            }}
        }});
        
        // Templates cache
        let templatesCache = [];
        
        async function loadTemplates() {{
            try {{
                const resp = await fetch('/api/templates');
                const data = await resp.json();
                if (!data.success) return;
                templatesCache = data.templates || [];
                const selector = document.getElementById('template_selector');
                if (!selector) return;
                
                // Define delivery method order
                const deliveryMethodOrder = [
                    'Cover Letter',
                    'LinkedIn Connection',
                    'Email',
                    'Other',
                    'Intro',
                    'LinkedIn Inmail',
                    'LinkedIn Message',
                    'Text',
                    'Phone'
                ];
                
                // Sort templates by delivery method order, then by title
                templatesCache.sort((a, b) => {{
                    const aMethod = a.delivery_method || '';
                    const bMethod = b.delivery_method || '';
                    const aIndex = deliveryMethodOrder.indexOf(aMethod);
                    const bIndex = deliveryMethodOrder.indexOf(bMethod);
                    
                    // If both have delivery methods, sort by order
                    if (aIndex !== -1 && bIndex !== -1) {{
                        if (aIndex !== bIndex) {{
                            return aIndex - bIndex;
                        }}
                    }} else if (aIndex !== -1) {{
                        return -1; // a comes first
                    }} else if (bIndex !== -1) {{
                        return 1; // b comes first
                    }}
                    
                    // Within same delivery method, sort by title
                    return (a.title || '').localeCompare(b.title || '');
                }});
                
                // Augment with intro message boxes from this page
                const introTemplates = collectIntroTemplates();
                for (const t of introTemplates) {{
                    templatesCache.push(t);
                }}
                
                // Re-sort after augmentation (same logic)
                templatesCache.sort((a, b) => {{
                    const aMethod = a.delivery_method || '';
                    const bMethod = b.delivery_method || '';
                    const aIndex = deliveryMethodOrder.indexOf(aMethod);
                    const bIndex = deliveryMethodOrder.indexOf(bMethod);
                    
                    if (aIndex !== -1 && bIndex !== -1) {{
                        if (aIndex !== bIndex) {{
                            return aIndex - bIndex;
                        }}
                    }} else if (aIndex !== -1) {{
                        return -1;
                    }} else if (bIndex !== -1) {{
                        return 1;
                    }}
                    
                    return (a.title || '').localeCompare(b.title || '');
                }});
                
                // Populate options with delivery method first
                selector.innerHTML = '<option value="">-- Select Template --</option>';
                for (const t of templatesCache) {{
                    const baseTitle = t.title || 'Template';
                    const method = t.delivery_method || '';
                    const label = method ? (method + ' - ' + baseTitle) : baseTitle;
                    const opt = document.createElement('option');
                    opt.value = t.id || ((t.title || '') + '|' + (t.delivery_method || ''));
                    opt.textContent = label;
                    selector.appendChild(opt);
                }}
            }} catch (e) {{
                console.warn('Failed to load templates', e);
            }}
        }}
        
        function collectIntroTemplates() {{
            const items = [];
            const textToHtml = (t) => {{
                if (!t) return '';
                return t
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/\\n/g, '<br>');
            }};
            // Add cover letter as a selectable template
            try {{
                const cl = document.getElementById('cover-letter-content');
                if (cl) {{
                    const content = textToHtml(cl.innerText || cl.textContent || '');
                    if (content && content.trim().length > 0) {{
                        const title = 'Cover Letter - ' + COMPANY + ' - ' + JOB_TITLE;
                        items.push({{ id: 'cover-letter', title: title, delivery_method: 'Cover Letter', content: content }});
                    }}
                }}
            }} catch (e) {{ /* ignore */ }}
            const sections = [
                {{ id: 'hiring-manager-content', prefix: 'Hiring Manager', method: 'Intro' }},
                {{ id: 'recruiter-content', prefix: 'Recruiter', method: 'Intro' }}
            ];
            for (const sec of sections) {{
                const container = document.getElementById(sec.id);
                if (!container) continue;
                const headers = container.querySelectorAll('h4');
                let idx = 0;
                headers.forEach(h => {{
                    const card = h.closest('div');
                    let content = '';
                    if (card && card.nextElementSibling) {{
                        content = textToHtml(card.nextElementSibling.innerText || card.nextElementSibling.textContent || '');
                    }}
                    const base = h.textContent ? h.textContent.trim() : 'Message';
                    const title = `${{sec.prefix}} - ${{base}}`;
                    const id = `intro:${{sec.method}}:${{++idx}}`;
                    items.push({{ id, title, delivery_method: sec.method, content }});
                }});
            }}
            return items;
        }}
        
        function onTemplateSelected(event) {{
            const value = event.target.value;
            
            // Show/hide percentage widget based on template selection
            const widgetContainer = document.getElementById('percentage-widget-container');
            if (widgetContainer) {{
                if (!value) {{
                    // No template selected, hide widget
                    widgetContainer.style.display = 'none';
                }} else {{
                    const match = templatesCache.find(t => (t.id && t.id === value) || (((t.title || '') + '|' + (t.delivery_method || '')) === value));
                    if (match && (match.delivery_method === 'Cover Letter' || match.id === 'cover-letter')) {{
                        // Cover letter template selected, show widget
                        widgetContainer.style.display = 'flex';
                    }} else {{
                        // Other template selected, hide widget
                        widgetContainer.style.display = 'none';
                    }}
                }}
            }}
            
            if (!value) return;
            const match = templatesCache.find(t => (t.id && t.id === value) || (((t.title || '') + '|' + (t.delivery_method || '')) === value));
            if (!match) return;
            const content = match.content || '';
            if (quillEditor) {{
                // Insert as HTML to preserve formatting; place caret at end
                quillEditor.clipboard.dangerouslyPasteHTML(content);
                quillEditor.focus();
                const len = quillEditor.getLength();
                quillEditor.setSelection(len, 0);
                
                // Normalize content to apply CSS styles (11pt, black, justified, 1.5 line-height)
                setTimeout(function() {{
                    if (quillEditor) {{
                        const editorLength = quillEditor.getLength();
                        if (editorLength > 1) {{
                            // Remove inline formatting that overrides CSS
                            quillEditor.formatText(0, editorLength - 1, {{
                                'font': false,
                                'size': false,
                                'color': false,
                                'align': false
                            }}, 'api');
                            
                            // Remove inline styles from HTML elements
                            const editorElement = quillEditor.root;
                            const allElements = editorElement.querySelectorAll('*');
                            allElements.forEach(function(el) {{
                                if (el.hasAttribute('style')) {{
                                    const style = el.getAttribute('style');
                                    const newStyle = style
                                        .replace(/font-size\s*:\s*[^;]+;?/gi, '')
                                        .replace(/font-family\s*:\s*[^;]+;?/gi, '')
                                        .replace(/color\s*:\s*[^;]+;?/gi, '')
                                        .replace(/text-align\s*:\s*[^;]+;?/gi, '')
                                        .replace(/line-height\s*:\s*[^;]+;?/gi, '');
                                    
                                    if (newStyle.trim()) {{
                                        el.setAttribute('style', newStyle.trim());
                                    }} else {{
                                        el.removeAttribute('style');
                                    }}
                                }}
                            }});
                        }}
                    }}
                }}, 100);
                
                updateStatusNotesCharacterCount();
            }}
        }}
        
        function showTab(button, tabId) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            const selectedContent = document.getElementById(tabId);
            if (selectedContent) {{
                selectedContent.classList.add('active');
            }}
            
            // Add active class to clicked tab
            button.classList.add('active');
        }}
        
        function toggleChecklist() {{
            const content = document.getElementById('checklist-content');
            const toggleButton = document.querySelector('.checklist-toggle');
            
            if (content.classList.contains('checklist-collapsed')) {{
                content.classList.remove('checklist-collapsed');
                content.classList.add('checklist-expanded');
                toggleButton.classList.add('expanded');
            }} else {{
                content.classList.remove('checklist-expanded');
                content.classList.add('checklist-collapsed');
                toggleButton.classList.remove('expanded');
            }}
        }}
        
        // Checklist functionality (legacy support)
        let checklistExpanded = false;
        
        function toggleChecklistLegacy() {{
            checklistExpanded = !checklistExpanded;
            const expanded = document.getElementById('checklistExpanded');
            const pill = document.getElementById('checklistPill');
            const toggle = document.getElementById('checklistToggle');
            
            if (checklistExpanded) {{
                expanded.classList.remove('checklist-collapsed');
                expanded.classList.add('checklist-expanded');
                pill.style.display = 'none';
                toggle.textContent = '▲';
            }} else {{
                expanded.classList.remove('checklist-expanded');
                expanded.classList.add('checklist-collapsed');
                updateChecklistPill();
                toggle.textContent = '▼';
            }}
        }}
        
        function updateChecklistPill() {{
            const pill = document.getElementById('checklistPill');
            // Return early if pill element doesn't exist (e.g., checklist section not present)
            if (!pill) {{
                return;
            }}
            
            const checkboxes = document.querySelectorAll('.checklist-item input[type="checkbox"]:checked');
            const checklistDefinitions = {{
                'application_submitted': 'Application Submitted',
                'linkedin_message_sent': 'LinkedIn Message Sent',
                'contact_email_found': 'Contact Email Found',
                'email_verified': 'Email Verified',
                'email_sent': 'Email Sent',
                'message_read': 'Message Read',
                'profile_viewed': 'Profile Viewed',
                'response_received': 'Response Received',
                'followup_sent': 'Follow-up Sent',
                'interview_scheduled': 'Interview Scheduled',
                'interview_completed': 'Interview Completed',
                'thank_you_sent': 'Thank You Sent'
            }};
            
            // Find the last checked item in order
            const order = ['application_submitted', 'linkedin_message_sent', 'contact_email_found', 
                          'email_verified', 'email_sent', 'message_read', 'profile_viewed', 
                          'response_received', 'followup_sent', 'interview_scheduled', 
                          'interview_completed', 'thank_you_sent'];
            
            let latestItem = null;
            for (let i = order.length - 1; i >= 0; i--) {{
                const checkbox = document.getElementById('checklist_' + order[i]);
                if (checkbox && checkbox.checked) {{
                    latestItem = checklistDefinitions[order[i]];
                    break;
                }}
            }}
            
            if (latestItem) {{
                pill.textContent = latestItem;
                pill.style.display = 'block';
            }} else {{
                pill.style.display = 'none';
            }}
        }}
        
        async function updateChecklistItem(itemKey, checked) {{
            try {{
                const response = await fetch(`/api/applications/${{APPLICATION_ID}}/checklist`, {{
                    method: 'PUT',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ checklist: {{ [itemKey]: checked }} }})
                }});
                
                const result = await response.json();
                if (result.success) {{
                    // Update the pill immediately
                    updateChecklistPill();
                    console.log('Checklist updated successfully');
                }} else {{
                    console.error('Failed to update checklist:', result.error);
                    // Revert checkbox
                    const checkbox = document.getElementById('checklist_' + itemKey);
                    if (checkbox) checkbox.checked = !checked;
                }}
            }} catch (error) {{
                console.error('Error updating checklist:', error);
                // Revert checkbox
                const checkbox = document.getElementById('checklist_' + itemKey);
                if (checkbox) checkbox.checked = !checked;
            }}
        }}
        
        // Initialize checklist state
        document.addEventListener('DOMContentLoaded', function() {{
            updateChecklistPill();
        }});
        
        async function submitStatusUpdate(event) {{
            event.preventDefault();
            
            const status = document.getElementById('new_status').value;
            // Get HTML content from Quill editor
            const notes = quillEditor ? quillEditor.root.innerHTML : '';
            const messageDiv = document.getElementById('status-message');
            const submitBtn = document.getElementById('updateStatusBtn');
            const btnText = document.getElementById('btnText');
            
            if (!status) {{
                showMessage('❌ Please select a status', 'error');
                return;
            }}
            
            // Check if this is a rejection BEFORE making the API call
            const isRejectedStatus = status.toLowerCase().trim() === 'rejected';
            
            // If rejecting, set a flag to prevent any reload attempts
            if (isRejectedStatus) {{
                window.__preventReload = true;
            }}
            
            // Clear form immediately
            document.getElementById('statusUpdateForm').reset();
            if (quillEditor) {{
                quillEditor.setContents([]);
                updateStatusNotesCharacterCount();
            }}
            
            // Show processing state
            submitBtn.disabled = true;
            submitBtn.style.background = '#d97706';
            submitBtn.style.cursor = 'not-allowed';
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
                    // Check if this was a rejection - redirect to dashboard instead of reloading
                    // Check redirect field, result status, or original status
                    const isRejected = isRejectedStatus || 
                                      result.redirect === 'dashboard' || 
                                      (result.status && result.status.toLowerCase().trim() === 'rejected');
                    
                    if (isRejected) {{
                        // Set flag to prevent any reload
                        window.__preventReload = true;
                        
                        // IMMEDIATELY redirect to dashboard - no delay, no reload, no other code execution
                        // Use replace to prevent back button from going to deleted page
                        window.location.replace('/dashboard');
                        return; // Exit immediately - prevent any other code from running
                    }}
                    
                    // Show success state
                    btnText.textContent = 'Updated!';
                    showMessage(`✅ Status updated to ${{status}} successfully!`, 'success');
                    
                    // Reload the page to show updated status and timeline
                    // Only reload if we're not preventing it
                    if (!window.__preventReload) {{
                        setTimeout(() => {{
                            window.location.reload();
                        }}, 2000);
                    }}
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
            const btnText = document.getElementById('btnText');
            
            submitBtn.disabled = false;
            submitBtn.style.background = '#d97706';
            submitBtn.style.cursor = 'pointer';
            btnText.textContent = 'Update';
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
        
        function copyStatusNotes(buttonElement) {{
            // Access the global quillEditor variable
            if (typeof quillEditor !== 'undefined' && quillEditor) {{
                // Get HTML content from Quill editor to preserve formatting
                const htmlContent = quillEditor.root.innerHTML;
                const textContent = quillEditor.getText();
                
                // Create a clipboard item with both HTML and plain text
                const clipboardItem = new ClipboardItem({{
                    'text/html': new Blob([htmlContent], {{ type: 'text/html' }}),
                    'text/plain': new Blob([textContent], {{ type: 'text/plain' }})
                }});
                
                navigator.clipboard.write([clipboardItem]).then(function() {{
                    // Show success message
                    const button = buttonElement || event.target;
                    const originalText = button.innerHTML;
                    button.innerHTML = '✅ Copied!';
                    button.style.background = '#28a745';
                    
                    setTimeout(() => {{
                        button.innerHTML = originalText;
                        button.style.background = '#667eea';
                    }}, 2000);
                }}).catch(function(err) {{
                    // Fallback: copy as HTML string
                    const textArea = document.createElement('textarea');
                    textArea.value = htmlContent;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    
                    // Show success message
                    const button = buttonElement || event.target;
                    const originalText = button.innerHTML;
                    button.innerHTML = '✅ Copied!';
                    button.style.background = '#28a745';
                    
                    setTimeout(() => {{
                        button.innerHTML = originalText;
                        button.style.background = '#667eea';
                    }}, 2000);
                }});
            }} else {{
                // Fallback if Quill editor is not available
                const notesElement = document.getElementById('status_notes');
                if (notesElement) {{
                    const htmlContent = notesElement.innerHTML;
                    const textArea = document.createElement('textarea');
                    textArea.value = htmlContent;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    
                    // Show success message
                    const button = buttonElement || event.target;
                    const originalText = button.innerHTML;
                    button.innerHTML = '✅ Copied!';
                    button.style.background = '#28a745';
                    
                    setTimeout(() => {{
                        button.innerHTML = originalText;
                        button.style.background = '#667eea';
                    }}, 2000);
                }}
            }}
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

        async function generateCustomResume() {{
            try {{
                const btn = document.getElementById('generateResumeBtn');
                if (btn) {{ btn.disabled = true; btn.textContent = 'Generating...'; btn.style.background = '#6c757d'; }}
                const resp = await fetch('/api/applications/' + APPLICATION_ID + '/generate-resume', {{ method: 'POST' }});
                const result = await resp.json();
                if (result && result.success) {{
                    // Reload to show resume tab content
                    window.location.reload();
                }} else {{
                    const errMsg = (result && result.error) ? result.error : 'Unknown error';
                    alert('Failed to generate resume: ' + errMsg);
                    if (btn) {{ btn.disabled = false; btn.textContent = 'Generate Customized Resume'; btn.style.background = '#10b981'; }}
                }}
            }} catch (e) {{
                alert('Failed to generate resume: ' + e.message);
                const btn = document.getElementById('generateResumeBtn');
                if (btn) {{ btn.disabled = false; btn.textContent = 'Generate Customized Resume'; btn.style.background = '#10b981'; }}
            }}
        }}
        
        async function generateIntroMessages(messageType) {{
            try {{
                const btnId = 'generate' + messageType.replace('_', '').split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('') + 'IntrosBtn';
                const btn = document.getElementById(btnId);
                if (btn) {{ btn.disabled = true; btn.textContent = 'Generating...'; btn.style.background = '#6c757d'; }}
                const resp = await fetch('/api/applications/' + APPLICATION_ID + '/generate-intros', {{ 
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ message_type: messageType }})
                }});
                const result = await resp.json();
                if (result && result.success) {{
                    // Reload to show intro messages content
                    window.location.reload();
                }} else {{
                    const errMsg = (result && result.error) ? result.error : 'Unknown error';
                    alert('Failed to generate intro messages: ' + errMsg);
                    if (btn) {{ btn.disabled = false; btn.textContent = 'Generate ' + messageType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Intro Messages'; btn.style.background = '#10b981'; }}
                }}
            }} catch (e) {{
                alert('Failed to generate intro messages: ' + e.message);
                const btnId = 'generate' + messageType.replace('_', '').split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('') + 'IntrosBtn';
                const btn = document.getElementById(btnId);
                if (btn) {{ btn.disabled = false; btn.textContent = 'Generate ' + messageType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Intro Messages'; btn.style.background = '#10b981'; }}
            }}
        }}
        
        // Function to determine match score color
        function getMatchScoreColor(score) {{
            if (score >= 80) return '#10b981'; // green
            if (score >= 60) return '#f59e0b'; // yellow
            return '#ef4444'; // red
        }}
        
        // Apply color on page load and initialize checklist pill
        document.addEventListener('DOMContentLoaded', function() {{
            const matchPercentage = document.querySelector('.match-percentage');
            if (matchPercentage) {{
                const score = parseInt(matchPercentage.getAttribute('data-score') || matchPercentage.textContent);
                matchPercentage.style.color = getMatchScoreColor(score);
            }}
            
            // Initialize checklist pill display
            if (typeof updateChecklistPill === 'function') {{
                updateChecklistPill();
            }}
            
            // Initialize percentage bar widget
            const percentageInput = document.getElementById('percentage-input');
            const progressBar = document.getElementById('percentage-progress-bar');
            const percentageText = document.getElementById('percentage-text-display');
            
            if (percentageInput && progressBar && percentageText) {{
                function updatePercentageBar() {{
                    const percentage = parseInt(percentageInput.value) || 0;
                    const clampedPercentage = Math.max(0, Math.min(100, percentage));
                    
                    progressBar.style.width = clampedPercentage + '%';
                    percentageText.textContent = clampedPercentage + '%';
                    
                    // Update color based on percentage
                    if (clampedPercentage > 70) {{
                        progressBar.className = 'percentage-progress-fill green';
                    }} else {{
                        progressBar.className = 'percentage-progress-fill orange';
                    }}
                }}
                
                percentageInput.addEventListener('input', updatePercentageBar);
                updatePercentageBar();
            }}
        }});
        async function showAIStatus() {{
            try {{
                const response = await fetch('/api/check-ollama');
                const data = await response.json();
                alert(`AI Status: ${{data.connected ? 'Connected' : 'Not Connected'}}\\nModel: ${{data.current_model || 'N/A'}}`);
            }} catch (error) {{
                console.error('AI Status Error:', error);
            }}
        }}
    </script>
    <!-- Shared Menu Injection -->
    <script src="/static/js/shared-menu.js"></script>
</body>
</html>"""
        return html
    
    def _status_to_class(self, status: str) -> str:
        """Convert a status label into a CSS-friendly class suffix."""
        if not status:
            return "unknown"
        return (
            status.strip()
            .lower()
            .replace("&", "and")
            .replace("/", "-")
            .replace("(", "")
            .replace(")", "")
            .replace("'", "")
            .replace(".", "")
            .replace(",", "")
            .replace(" - ", "-")
            .replace(" ", "-")
        )
    
    def _get_status_tags(self, application: Application) -> list:
        """Get status tags from application checklist and status"""
        tags = []
        checklist_items = application.checklist_items or {}
        status_lower = application.status.lower() if application.status else ""
        
        # Add tags based on checklist items
        if checklist_items.get("interview_completed") or checklist_items.get("interview_scheduled") or "interview" in status_lower:
            tags.append(("Interview Notes", "tag-green"))
        if checklist_items.get("thank_you_sent") or "thank" in status_lower:
            tags.append(("Thank You Sent", "tag-gray"))
        if checklist_items.get("response_received") or "company response" in status_lower or "contacted" in status_lower:
            tags.append(("Company Response", "tag-blue"))
        if checklist_items.get("email_sent"):
            tags.append(("Email Sent", "tag-gray"))
        
        # Add application status as a pill if it's not already covered by checklist items
        if application.status:
            status_display = application.status.replace('_', ' ').title()
            
            # Determine tag class based on status
            if "rejected" in status_lower:
                tag_class = "tag-red"
            elif "offered" in status_lower or "accepted" in status_lower:
                tag_class = "tag-green"
            elif "interview" in status_lower:
                tag_class = "tag-green"
            elif "applied" in status_lower:
                tag_class = "tag-blue"
            elif "pending" in status_lower:
                tag_class = "tag-gray"
            else:
                tag_class = "tag-blue"
            
            # Only add status tag if it's not already covered by checklist items
            # Check if status is already represented by existing tags
            # We only skip if the status is clearly represented by a more specific checklist tag
            status_already_represented = False
            for tag_name, _ in tags:
                tag_lower = tag_name.lower()
                # Only consider it represented if:
                # 1. Status contains "interview" and we have "Interview Notes" tag
                # 2. Status contains "company response" or "contacted" and we have "Company Response" tag  
                # 3. Status contains "thank" and we have "Thank You Sent" tag
                if (("interview" in status_lower and "interview" in tag_lower) or
                    (("company response" in status_lower or "contacted" in status_lower) and "company response" in tag_lower) or
                    ("thank" in status_lower and "thank" in tag_lower)):
                    status_already_represented = True
                    break
            
            # Always show the status pill unless it's clearly represented by a checklist tag
            # This ensures common statuses like "Pending", "Applied", "Rejected", "Offered" always show
            if not status_already_represented:
                tags.append((status_display, tag_class))
        
        return tags
    
    def _generate_qualifications_summary_html(self, qualifications: QualificationAnalysis) -> str:
        """Generate Qualifications Summary HTML for two-column layout"""
        # Use preliminary_analysis as single source of truth (same as Skills Matching Details table)
        strong_matches_html = ""
        partial_matches_html = ""
        
        if qualifications.preliminary_analysis:
            # Extract from preliminary_analysis - NO FILTERING, show all matches
            exact_matches = qualifications.preliminary_analysis.get('exact_matches', [])
            partial_matches = qualifications.preliminary_analysis.get('partial_matches', [])
            
            # Get unique matched skills - show ALL, no filtering
            strong_skills = set()
            for match in exact_matches:
                matched_skill = match.get('skill', '')
                if matched_skill:
                    strong_skills.add(matched_skill)
            
            if strong_skills:
                strong_matches_html = "<h3>Strong Matches</h3><ul>"
                for skill in sorted(list(strong_skills))[:5]:  # Limit to 5
                    strong_matches_html += f"<li>{skill}</li>"
                strong_matches_html += "</ul>"
            
            # Get unique partial match skills - show ALL, no filtering
            partial_skills = set()
            for match in partial_matches:
                matched_skill = match.get('skill', '')
                if matched_skill:
                    partial_skills.add(matched_skill)
            
            if partial_skills:
                partial_matches_html = "<h3>Partial Matches</h3><ul>"
                for skill in sorted(list(partial_skills))[:3]:  # Limit to 3
                    partial_matches_html += f"<li>{skill}</li>"
                partial_matches_html += "</ul>"
        else:
            # Fallback to old lists if preliminary_analysis not available
            if qualifications.strong_matches and len(qualifications.strong_matches) > 0:
                strong_matches_html = "<h3>Strong Matches</h3><ul>"
                for match in qualifications.strong_matches[:5]:
                    strong_matches_html += f"<li>{match}</li>"
                strong_matches_html += "</ul>"
            
            if hasattr(qualifications, 'partial_matches') and qualifications.partial_matches and len(qualifications.partial_matches) > 0:
                partial_matches_html = "<h3>Partial Matches</h3><ul>"
                for match in qualifications.partial_matches[:3]:
                    partial_matches_html += f"<li>{match}</li>"
                partial_matches_html += "</ul>"
        
        missing_skills_html = ""
        if qualifications.missing_skills and len(qualifications.missing_skills) > 0:
            missing_skills_html = "<h3>Missing Skills</h3><ul>"
            for skill in qualifications.missing_skills[:5]:  # Limit to 5
                missing_skills_html += f"<li>{skill}</li>"
            missing_skills_html += "</ul>"
        
        # If no content, show a message
        if not strong_matches_html and not partial_matches_html and not missing_skills_html:
            return """
                    <div class="section-content">
                        <p style="color: #6b7280; font-size: 14px;">Qualifications analysis not available yet.</p>
                    </div>
        """
        
        return f"""
                    <div class="section-content">
                        {strong_matches_html}
                        {partial_matches_html}
                        {missing_skills_html}
                    </div>
        """
    
    def _generate_timeline_html_for_summary(self, application: Application) -> str:
        """Generate Application Timeline HTML for two-column layout"""
        from app.services.job_processor import JobProcessor
        from datetime import datetime
        import re
        
        job_processor = JobProcessor()
        updates = job_processor.get_application_updates(application)
        
        # Collect all timeline items with datetime objects for sorting
        timeline_items = []
        
        # Add initial application creation
        timeline_items.append({
            'datetime': application.created_at,
            'display_date': format_for_display(application.created_at),
            'status': 'Application Created',
            'notes': None,
            'update_file': None,
            'update_type': 'application',
            'contact_name': None
        })
        
        # Add status updates with datetime objects
        import pytz
        est = pytz.timezone('America/Toronto')
        for update in updates:
            try:
                # Convert timestamp string to datetime object for sorting
                timestamp_str = update['timestamp']
                dt = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                # Make timezone-aware to match application.created_at
                if dt.tzinfo is None:
                    dt = est.localize(dt)
                timeline_items.append({
                    'datetime': dt,
                    'display_date': update['display_timestamp'],
                    'status': update['status'],
                    'notes': None,  # Will extract if needed
                    'update_file': update['file'],
                    'update_type': update.get('type', 'application'),
                    'contact_name': update.get('contact_name')
                })
            except Exception as e:
                print(f"Warning: Could not parse timestamp for update {update.get('file', 'unknown')}: {e}")
        
        # Sort by datetime descending (newest first)
        timeline_items.sort(key=lambda x: x['datetime'], reverse=True)
        
        # Limit to 10 items total
        timeline_items = timeline_items[:10]
        
        if len(timeline_items) == 1 and not updates:
            return '<div class="timeline"><p style="color: #6b7280; font-size: 14px;">No timeline entries yet.</p></div>'
        
        timeline_html = '<div class="timeline">'
        for item in timeline_items:
            # Determine tag class for status pill
            status_lower = item['status'].lower()
            if "interview" in status_lower:
                tag_class = "tag-green"
            elif "rejected" in status_lower:
                tag_class = "tag-red"
            elif "offered" in status_lower or "accepted" in status_lower:
                tag_class = "tag-green"
            elif "thank" in status_lower:
                tag_class = "tag-gray"
            else:
                tag_class = "tag-blue"
            
            # Determine icon based on update type
            update_type = item.get('update_type', 'application')
            icon = '🤝' if update_type == 'networking' else '💼'
            contact_name = item.get('contact_name')
            status_display = item['status']
            if contact_name and update_type == 'networking':
                status_display = f"{contact_name} - {status_display}"
            
            # Build status pill
            status_pill = f'<span class="tag {tag_class}" style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{icon} {status_display}</span>'
            
            timeline_html += f'''
                        <div class="timeline-item">
                            <div style="margin-bottom: 8px;">
                                {status_pill} - <span style="color: #666; font-size: 14px;">{item['display_date']}</span>
                            </div>
                        </div>
            '''
        timeline_html += '</div>'
        return timeline_html
    
    def _generate_updates_timeline(self, application: Application) -> str:
        """Generate HTML for status updates timeline"""
        from app.services.job_processor import JobProcessor
        from datetime import datetime
        import re
        
        job_processor = JobProcessor()
        updates = job_processor.get_application_updates(application)
        
        # Collect all timeline items with datetime objects for sorting
        timeline_items = []
        
        # Add initial application creation
        timeline_items.append({
            'datetime': application.created_at,
            'display_date': format_for_display(application.created_at),
            'status': 'Application Created',
            'update_file': None,
            'update_type': 'application',
            'contact_name': None
        })
        
        # Add status updates with datetime objects
        import pytz
        est = pytz.timezone('America/Toronto')
        for update in updates:
            try:
                # Convert timestamp string to datetime object for sorting
                timestamp_str = update['timestamp']
                dt = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                # Make timezone-aware to match application.created_at
                if dt.tzinfo is None:
                    dt = est.localize(dt)
                timeline_items.append({
                    'datetime': dt,
                    'display_date': update['display_timestamp'],
                    'status': update['status'],
                    'update_file': update['file'],
                    'update_type': update.get('type', 'application'),
                    'contact_name': update.get('contact_name')
                })
            except Exception as e:
                print(f"Warning: Could not parse timestamp for update {update.get('file', 'unknown')}: {e}")
        
        # Sort by datetime descending (newest first)
        timeline_items.sort(key=lambda x: x['datetime'], reverse=True)
        
        if not timeline_items:
            return ""
        
        timeline_html = ""
        for item in timeline_items:
            # Extract notes if this is an update item
            notes_text = ""
            if item['update_file']:
                try:
                    if Path(item['update_file']).exists():
                        html_content = read_text_file(Path(item['update_file']))
                        # Extract notes - handle both networking and regular updates
                        # Try new structure first (notes-text), then fallback to old structure (notes)
                        start_pattern = r'<div class="notes-text">'
                        start_match = re.search(start_pattern, html_content)
                        if not start_match:
                            # Fallback: try old networking structure with class="notes"
                            start_pattern = r'<div class="notes">'
                            start_match = re.search(start_pattern, html_content)
                        if start_match:
                            start_pos = start_match.end()
                            # Find the matching closing </div> by counting div depth
                            pos = start_pos
                            depth = 1
                            end_pos = None
                            
                            while pos < len(html_content):
                                # Find next <div or </div>
                                next_div_open = html_content.find('<div', pos)
                                next_div_close = html_content.find('</div>', pos)
                                
                                if next_div_close == -1:
                                    break
                                
                                # Check which comes first
                                if next_div_open != -1 and next_div_open < next_div_close:
                                    # Found opening div
                                    depth += 1
                                    pos = next_div_open + 4
                                else:
                                    # Found closing div
                                    depth -= 1
                                    if depth == 0:
                                        end_pos = next_div_close
                                        break
                                    pos = next_div_close + 6
                            
                            if end_pos:
                                notes_text = html_content[start_pos:end_pos].strip()
                            else:
                                # Fallback to simple regex
                                notes_match = re.search(r'<div class="notes-text">(.*?)</div>', html_content, re.DOTALL)
                                if notes_match:
                                    notes_text = notes_match.group(1).strip()
                        else:
                            # Fallback: try simple pattern
                            notes_match = re.search(r'<div class="notes-text">(.*?)</div>', html_content, re.DOTALL)
                            if notes_match:
                                notes_text = notes_match.group(1).strip()
                        
                        # Don't clean up HTML content - preserve images and formatting
                except Exception as e:
                    print(f"Warning: Could not extract content from {item['update_file']}: {e}")
            
            # Determine tag class for status pill
            status_lower = item['status'].lower()
            if "interview" in status_lower:
                tag_class = "tag-green"
            elif "rejected" in status_lower:
                tag_class = "tag-red"
            elif "offered" in status_lower or "accepted" in status_lower:
                tag_class = "tag-green"
            elif "thank" in status_lower:
                tag_class = "tag-gray"
            else:
                tag_class = "tag-blue"
            
            # Determine icon based on update type
            update_type = item.get('update_type', 'application')
            icon = '🤝' if update_type == 'networking' else '💼'
            contact_name = item.get('contact_name')
            status_display = item['status']
            if contact_name and update_type == 'networking':
                status_display = f"{contact_name} - {status_display}"
            
            # Build status pill HTML (rendered once)
            status_pill = f'<span class="tag {tag_class}" style="display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{icon} {status_display}</span>'
            
            # Build notes section
            notes_html = ""
            if notes_text and notes_text not in ["No additional notes", ""]:
                # Remove emoji from notes content if present
                notes_text = notes_text.replace('📝', '').strip()
                
                # Remove any inline styles that might add yellow background or borders
                notes_text = re.sub(r'style="[^"]*background[^"]*fff3e0[^"]*"', '', notes_text)
                notes_text = re.sub(r'style="[^"]*border[^"]*ff9800[^"]*"', '', notes_text)
                notes_text = re.sub(r'style="[^"]*background[^"]*#fff3e0[^"]*"', '', notes_text)
                notes_text = re.sub(r'style="[^"]*border[^"]*#ff9800[^"]*"', '', notes_text)
                
                # Handle HTML content (including images) - don't process URLs if content is already HTML
                if '<' in notes_text and '>' in notes_text:
                    # Content is already HTML, use as-is but clean up any remaining background styles
                    notes_display = notes_text
                else:
                    # Plain text, make URLs clickable
                    notes_display = re.sub(r'(https?://[^\s]+)', r'<a href="\1" target="_blank" style="color: #667eea; text-decoration: underline;">\1</a>', notes_text)
                
                notes_html = f'<div style="margin-top: 8px; font-size: 14px; color: #000; margin-left: 0; padding-left: 0;"><div style="margin-bottom: 4px; margin-left: 0; padding-left: 0;"><strong>Notes:</strong></div><div class="timeline-notes-content" style="margin-left: 0; padding-left: 0;">{notes_display}</div></div>'
            
            timeline_html += f"""
                <div class="timeline-item">
                    <div style="margin-bottom: 8px; white-space: nowrap;">
                        {status_pill} - <span style="color: #666; font-size: 14px;">{item['display_date']}</span>
                    </div>
                    {notes_html}
                </div>"""
        
        return timeline_html
    
    def _get_intro_messages_content(self, application, message_type: str) -> str:
        """Get intro messages content from file and format as separate copy-ready boxes, or show generate button"""
        try:
            if message_type == 'hiring_manager':
                file_path = getattr(application, 'hiring_manager_intros_path', None)
            elif message_type == 'recruiter':
                file_path = getattr(application, 'recruiter_intros_path', None)
            else:
                return "No intro messages available."
            
            if file_path and Path(file_path).exists():
                content = read_text_file(file_path)
                return self._format_intro_messages_as_boxes(content, message_type, application.company)
            else:
                # Show generate button if files don't exist
                message_type_display = message_type.replace('_', ' ').title()
                return f'''<div style="text-align: center; padding: 40px 20px; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dee2e6;">
                    <p style="color: #6c757d; margin-bottom: 20px; font-size: 14px;">
                        No {message_type_display} intro messages generated yet. Click the button below to generate them.
                    </p>
                    <button id="generate{message_type.replace('_', '').title()}IntrosBtn" onclick="generateIntroMessages('{message_type}')" style="background: #10b981; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">Generate {message_type_display} Intro Messages</button>
                </div>'''
        except Exception as e:
            return f"Error loading {message_type.replace('_', ' ')} intro messages: {str(e)}"
    
    def _format_intro_messages_as_boxes(self, content: str, message_type: str, company: str) -> str:
        """Format intro messages as separate copy-ready boxes
        - Skip any preamble like "Here are three versions..."
        - Remove metadata markers from copy: "**MESSAGE X:**", character count brackets, and generic closing lines
        - Title each box as: "<Company> - Message: <#> - <N> characters total"
        """
        try:
            import re
            # Collect only sections that start with a MESSAGE marker; drop any preamble
            messages = []
            current_message_lines = []
            in_message = False
            for raw_line in content.split('\n'):
                line = raw_line.rstrip('\n')
                if line.strip().startswith('**MESSAGE'):
                    if in_message and current_message_lines:
                        messages.append('\n'.join(current_message_lines).strip())
                        current_message_lines = []
                    in_message = True
                    current_message_lines.append(line)
                else:
                    if in_message:
                        current_message_lines.append(line)
            if in_message and current_message_lines:
                messages.append('\n'.join(current_message_lines).strip())
            
            # If we don't have the expected format, return original content
            if len(messages) < 3:
                return content
            
            # Create HTML for each message box
            html_boxes = []
            for i, message in enumerate(messages, 1):
                # Remove the MESSAGE header
                clean_message = re.sub(r"^\*\*MESSAGE\s+{}:\*\*\s*".format(i), "", message, flags=re.IGNORECASE).strip()
                # Remove any bracketed character metadata from the copy
                clean_message = re.sub(r"\[~?\d+\s*characters?[^\]]*\]", "", clean_message, flags=re.IGNORECASE).strip()
                # Also remove parenthetical character counts like "(276 characters)"
                clean_message = re.sub(r"\(\s*~?\d+\s*characters?[^\)]*\)", "", clean_message, flags=re.IGNORECASE)
                # Remove any trailing helper line like "Let me know if you'd like me to make any changes!"
                clean_message = re.sub(r"\n?\s*Let me know if you'd like me to make any changes!?\s*$", "", clean_message, flags=re.IGNORECASE)
                # Remove common instruction lines that sometimes appear in the body
                lines = [ln for ln in clean_message.split('\n') if not re.search(r"^\s*(each message is|uses the exact character counts|message\s*3\s*is\s*particularly|let me know if you'd like me to (?:make|adjust).*)\s*$", ln.strip(), flags=re.IGNORECASE)]
                # Also drop standalone lines that are just character counts in brackets/parentheses
                lines = [ln for ln in lines if not re.match(r"^\s*(?:\(\s*~?\d+\s*characters?[^\)]*\)|\[\s*~?\d+\s*characters?[^\]]*\])\s*$", ln.strip(), flags=re.IGNORECASE)]
                clean_message = "\n".join(lines).strip()
                # Compute actual character count as fallback (exclude newlines only)
                computed_chars = len(clean_message.replace('\n', ''))
                char_count = str(computed_chars)
                
                # Create individual copy button ID
                copy_button_id = f"copy-{message_type}-{i}"
                content_id = f"{message_type}-content-{i}"
                
                box_html = f"""
                <div style="margin-bottom: 20px; border: 2px solid #e0e0e0; border-radius: 8px; background: white; overflow: hidden;">
                    <div style="background: #f8f9fa; padding: 10px 15px; border-bottom: 1px solid #e0e0e0; display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #333; font-size: 16px; font-weight: 600;">{company} - Message: {i} - {char_count} characters total</h4>
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

    def _generate_tab_button(self, tab_id: str, tab_name: str, file_path) -> str:
        """Generate tab button HTML if file exists"""
        if file_path and Path(file_path).exists():
            return f'<button type="button" class="tab" onclick="showTab(this, \'{tab_id}\')">{tab_name}</button>'
        return ''

    def _generate_tab_content(self, tab_id: str, tab_name: str, content: str, file_path) -> str:
        """Generate tab content HTML if file exists"""
        if file_path and Path(file_path).exists():
            return f'<div id="{tab_id}" class="tab-content">\n{content}\n</div>'
        return ''

    def _generate_resume_tab_html(self, application: Application, resume: str) -> str:
        """Generate the resume tab HTML (show content or a generate button)."""
        try:
            if application.custom_resume_path and Path(application.custom_resume_path).exists():
                return f'''<div id="resume" class="tab-content">
            <h2>Customized Resume</h2>
            <pre>{resume}</pre>
        </div>'''
            else:
                return '''<div id="resume" class="tab-content">
            <h2>Customized Resume</h2>
            <div style="margin: 12px 0; padding: 12px; background: #fffbe6; border: 1px solid #ffe58f; border-radius: 6px; color: #8c6d1f;">
                No customized resume generated yet. Click the button below to generate one from your base resume and analysis.
            </div>
            <button id="generateResumeBtn" onclick="generateCustomResume()" style="background: #10b981; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">Generate Customized Resume</button>
        </div>'''
        except Exception:
            return ''
    
    def _generate_networking_tab_html(self, application: Application) -> str:
        """Generate the Networking tab HTML showing contacts matching the company"""
        from urllib.parse import quote
        company_encoded = quote(application.company)
        return f'''<div id="rewards" class="tab-content">
            <h2>Networking Rewards by Category</h2>
            {self._generate_rewards_by_category_html(application)}
        </div>
        
        <div id="networking" class="tab-content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0;">Networking Contacts</h2>
                <button id="create-contact-btn" onclick="showCreateContactForm()" style="padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600;">Create New Contact</button>
            </div>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Contacts at {application.company}:</p>
            <div id="networking-contacts-grid" class="contacts-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px;">
                <div style="text-align: center; padding: 40px; color: #6b7280;">Loading contacts...</div>
            </div>
            <div id="networking-summary-container" style="display: none; position: fixed; top: 0; left: 180px; right: 0; bottom: 0; background: white; z-index: 1000; flex-direction: column; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; flex-shrink: 0; background: white;">
                    <h3 id="networking-summary-title" style="margin: 0;">Contact Summary</h3>
                    <button onclick="closeNetworkingSummary()" style="padding: 8px 16px; background: #6b7280; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">Close Summary</button>
                </div>
                <div id="networking-summary-content" style="flex: 1; overflow: hidden; min-height: 0; position: relative;">
                    <div style="text-align: center; padding: 40px; color: #6b7280;">Loading summary...</div>
                </div>
            </div>
            <style>
                .contact-tile {{
                    background: white;
                    border-radius: 14px;
                    padding: 24px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    border: 2px solid transparent;
                    position: relative;
                }}
                .contact-tile:hover {{
                    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08);
                    transform: translateY(-4px);
                    border-color: rgba(59, 130, 246, 0.2);
                }}
                .contact-tile.timing-white {{ border-left: 4px solid #e5e7eb; }}
                .contact-tile.timing-green {{ border-left: 4px solid #10b981; }}
                .contact-tile.timing-yellow {{ border-left: 4px solid #f59e0b; }}
                .contact-tile.timing-red {{ border-left: 4px solid #ef4444; }}
                .contact-tile.timing-blue {{ border-left: 4px solid #3b82f6; }}
                .contact-tile.timing-gray {{ border-left: 4px solid #6b7280; }}
                .contact-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 12px;
                }}
                .contact-name {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #1f2937;
                    margin: 0;
                }}
                .match-score {{
                    font-size: 20px;
                    font-weight: 700;
                    color: #10b981;
                }}
                .contact-company {{
                    font-size: 15px;
                    color: #6b7280;
                    margin: 4px 0;
                    font-weight: 500;
                }}
                .contact-title {{
                    font-size: 14px;
                    color: #9ca3af;
                    margin: 4px 0;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: 600;
                    border-radius: 6px;
                    margin-top: 8px;
                    background: #f9fafb;
                    color: #6b7280;
                }}
                .next-step-section {{
                    margin-top: 16px;
                    padding: 12px;
                    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                    border-radius: 10px;
                    border-left: 4px solid #3b82f6;
                }}
                .next-step-label {{
                    font-size: 11px;
                    font-weight: 700;
                    text-transform: uppercase;
                    color: #1e40af;
                    letter-spacing: 0.5px;
                    margin-bottom: 6px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }}
                .next-step-label::before {{
                    content: '→';
                    font-size: 14px;
                    font-weight: 700;
                }}
                .next-step-text {{
                    font-size: 12px;
                    color: #1e3a8a;
                    line-height: 1.5;
                    font-weight: 500;
                }}
                .contact-dates {{
                    margin-top: 14px;
                    font-size: 13px;
                    color: #9ca3af;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }}
                .date-row {{
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }}
                .view-btn {{
                    width: 100%;
                    margin-top: 16px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 8px;
                    border: 1px solid #e5e7eb;
                    background: white;
                    color: #1f2937;
                    cursor: pointer;
                    transition: all 0.15s ease;
                }}
                .view-btn:hover {{
                    background: #f9fafb;
                    border-color: #3b82f6;
                    color: #3b82f6;
                }}
            </style>
            <script>
                async function loadNetworkingContacts() {{
                    try {{
                        const response = await fetch(`/api/applications/{application.id}/networking-contacts`);
                        const data = await response.json();
                        
                        const grid = document.getElementById('networking-contacts-grid');
                        if (!data.success || !data.contacts || data.contacts.length === 0) {{
                            grid.innerHTML = '<div style="text-align: center; padding: 40px; color: #6b7280; grid-column: 1 / -1;">No networking contacts found for {application.company}.</div>';
                            return;
                        }}
                        
                        grid.innerHTML = data.contacts.map(contact => {{
                            const matchScore = contact.match_score ? Math.round(contact.match_score) : 0;
                            const flagIcon = contact.flagged ? '⚐' : '⚑';
                            const flagClass = contact.flagged ? 'flagged' : '';
                            const nextStep = contact.next_step || 'Review contact status and determine next action';
                            const timingColor = contact.timing_color || 'white';
                            
                            return `
                                <div class="contact-tile timing-${{timingColor}}">
                                    <div class="contact-header">
                                        <h3 class="contact-name">${{escapeHtml(contact.person_name)}}</h3>
                                        <div style="display: flex; align-items: center; gap: 12px;">
                                            <span class="match-score">${{matchScore}}%</span>
                                            <span class="flag ${{flagClass}}" onclick="toggleContactFlag('${{contact.id}}', ${{!contact.flagged}})" style="cursor: pointer; font-size: 18px; opacity: ${{contact.flagged ? '1' : '0.3'}}; transition: opacity 0.15s ease;">${{flagIcon}}</span>
                                        </div>
                                    </div>
                                    <div class="contact-company">${{escapeHtml(contact.company_name)}}</div>
                                    ${{contact.job_title ? `<div class="contact-title">${{escapeHtml(contact.job_title)}}</div>` : ''}}
                                    <div class="status-badge">${{escapeHtml(contact.status)}}</div>
                                    <div class="next-step-section">
                                        <div class="next-step-label">Next Step</div>
                                        <div class="next-step-text">${{escapeHtml(nextStep)}}</div>
                                    </div>
                                    <div class="contact-dates">
                                        <div class="date-row">
                                            <span>📅</span>
                                            <span>Connected: ${{formatDate(contact.created_at)}}</span>
                                        </div>
                                        <div class="date-row">
                                            <span>🔄</span>
                                            <span>Updated: ${{formatDate(contact.status_updated_at || contact.created_at)}}</span>
                                        </div>
                                        ${{contact.days_since_update !== undefined ? `<div class="date-row"><span>⏰</span><span>${{contact.days_since_update}} days ago</span></div>` : ''}}
                                    </div>
                                    <button class="view-btn" onclick="viewContactSummary('${{contact.id}}', '${{escapeHtml(contact.person_name)}}')">View Summary</button>
                                </div>
                            `;
                        }}).join('');
                    }} catch (error) {{
                        console.error('Error loading networking contacts:', error);
                        document.getElementById('networking-contacts-grid').innerHTML = '<div style="text-align: center; padding: 40px; color: #ef4444; grid-column: 1 / -1;">Error loading contacts. Please refresh the page.</div>';
                    }}
                }}
                
                function escapeHtml(text) {{
                    if (!text) return '';
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                }}
                
                function formatDate(isoString) {{
                    if (!isoString) return 'N/A';
                    const date = new Date(isoString);
                    return date.toLocaleDateString('en-US', {{ 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric'
                    }});
                }}
                
                let currentViewState = 'contacts'; // 'contacts', 'summary', or 'create'
                
                async function viewContactSummary(contactId, contactName) {{
                    try {{
                        const response = await fetch(`/api/networking/contacts/${{contactId}}`);
                        const data = await response.json();
                        
                        if (data.success && data.contact) {{
                            const contact = data.contact;
                            const folderName = `${{contact.person_name.replace(/\\s+/g, '-')}}-${{contact.company_name.replace(/\\s+/g, '-')}}`;
                            const summaryFilename = `${{contact.person_name.replace(/\\s+/g, '-')}}-summary.html`;
                            const summaryUrl = `/networking/${{folderName}}/${{summaryFilename}}`;
                            
                            // Hide contacts grid and show summary container
                            document.getElementById('networking-contacts-grid').style.display = 'none';
                            document.getElementById('networking-summary-container').style.display = 'flex';
                            document.getElementById('networking-summary-title').textContent = `${{contactName}} - Summary`;
                            
                            // Update button state
                            const createBtn = document.getElementById('create-contact-btn');
                            createBtn.textContent = 'Create New Contact';
                            createBtn.onclick = showCreateContactForm;
                            
                            // Load summary content via iframe
                            const summaryContent = document.getElementById('networking-summary-content');
                            // Clear any existing content immediately (including "Loading summary...")
                            summaryContent.innerHTML = '';
                            // Then set iframe - this ensures no flash of old content
                            const iframe = document.createElement('iframe');
                            iframe.src = `${{summaryUrl}}`;
                            iframe.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;';
                            summaryContent.appendChild(iframe);
                            
                            currentViewState = 'summary';
                        }} else {{
                            alert('Could not load contact summary');
                        }}
                    }} catch (error) {{
                        console.error('Error loading contact summary:', error);
                        alert('Error loading contact summary');
                    }}
                }}
                
                function showCreateContactForm() {{
                    // Hide contacts grid and show summary container
                    document.getElementById('networking-contacts-grid').style.display = 'none';
                    document.getElementById('networking-summary-container').style.display = 'flex';
                    document.getElementById('networking-summary-title').textContent = 'Create New Contact';
                    
                    // Update button state
                    const createBtn = document.getElementById('create-contact-btn');
                    createBtn.textContent = 'Back to Contacts';
                    createBtn.onclick = showContactsGrid;
                    
                    // Load create form via iframe with company pre-filled
                    const summaryContent = document.getElementById('networking-summary-content');
                    // Clear any existing content immediately (including "Loading summary...")
                    summaryContent.innerHTML = '';
                    // Then create and append iframe - this ensures no flash of old content
                    const iframe = document.createElement('iframe');
                    iframe.src = '/new-networking-contact?company={company_encoded}';
                    iframe.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;';
                    summaryContent.appendChild(iframe);
                    
                    currentViewState = 'create';
                }}
                
                function showContactsGrid() {{
                    // Show contacts grid and hide summary container
                    document.getElementById('networking-contacts-grid').style.display = 'grid';
                    document.getElementById('networking-summary-container').style.display = 'none';
                    
                    // Update button state
                    const createBtn = document.getElementById('create-contact-btn');
                    createBtn.textContent = 'Create New Contact';
                    createBtn.onclick = showCreateContactForm;
                    
                    currentViewState = 'contacts';
                }}
                
                function closeNetworkingSummary() {{
                    showContactsGrid();
                }}
                
                // Listen for messages from iframe (e.g., when contact is created)
                window.addEventListener('message', function(event) {{
                    if (event.data && event.data.type === 'networking-contact-created') {{
                        // Contact was created in the iframe
                        // Reload contacts to show the new one
                        loadNetworkingContacts();
                        
                        // Optionally show the new contact's summary
                        if (event.data.summary_url) {{
                            setTimeout(() => {{
                                // Find the contact in the list and show its summary
                                // For now, just reload contacts and show success message
                                alert(`Contact ${{event.data.person_name}} at ${{event.data.company_name}} created successfully!`);
                            }}, 500);
                        }}
                    }}
                }});
                
                async function toggleContactFlag(contactId, flagged) {{
                    try {{
                        const response = await fetch(`/api/networking/contacts/${{contactId}}/flag`, {{
                            method: 'PUT',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ flagged: flagged }})
                        }});
                        
                        if (response.ok) {{
                            loadNetworkingContacts();
                        }}
                    }} catch (error) {{
                        console.error('Error toggling flag:', error);
                    }}
                }}
                
                // Load contacts when tab is shown
                document.addEventListener('DOMContentLoaded', function() {{
                    // Load immediately
                    loadNetworkingContacts();
                    
                    // Also load when networking tab is clicked
                    const networkingTab = document.querySelector('[onclick*="networking"]');
                    if (networkingTab) {{
                        networkingTab.addEventListener('click', function() {{
                            setTimeout(loadNetworkingContacts, 100);
                        }});
                    }}
                }});
            </script>
        </div>'''
    
    def _generate_timeline_tab_html(self, application: Application) -> str:
        """Generate the Timeline tab HTML showing all timeline entries with full formatting"""
        timeline_html = self._generate_updates_timeline(application)
        return f'''<div id="timeline" class="tab-content">
            <h2>Application Timeline</h2>
            <p style="color: #666; margin-bottom: 20px; font-size: 14px;">Complete history of this application:</p>
            <div class="timeline">
                {timeline_html}
            </div>
        </div>'''


