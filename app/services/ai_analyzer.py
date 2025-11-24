"""AI analysis service using Ollama"""
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import requests
from app.models.qualification import QualificationAnalysis
from app.utils.prompts import get_prompt
from app.utils.simple_tech_extractor import SimpleTechExtractor

# Import enhanced analyzer for improved performance
try:
    from app.services.enhanced_qualifications_analyzer import EnhancedQualificationsAnalyzer
    ENHANCED_ANALYZER_AVAILABLE = True
except ImportError:
    ENHANCED_ANALYZER_AVAILABLE = False


class AIAnalyzer:
    """AI-powered analysis and generation using Ollama"""
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.timeout = 600  # 10 minutes timeout for longer responses
        self.tech_extractor = SimpleTechExtractor()  # Initialize simple tech extractor
        
        # Initialize enhanced analyzer if available
        if ENHANCED_ANALYZER_AVAILABLE:
            self.enhanced_analyzer = EnhancedQualificationsAnalyzer()
            print("✅ Enhanced Qualifications Analyzer loaded - using preliminary matching + focused AI analysis")
        else:
            self.enhanced_analyzer = None
            print("⚠️ Enhanced Qualifications Analyzer not available - using standard AI analysis")
    
    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_available_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []
    
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Make a call to Ollama API"""
        if not self.check_connection():
            raise ConnectionError(
                "Cannot connect to Ollama. Please ensure Ollama is running:\n"
                "  1. Install: brew install ollama\n"
                "  2. Start: ollama serve\n"
                "  3. Pull model: ollama pull llama3"
            )
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 10000,  # Increased to 10000 tokens for large documents
                "num_ctx": 10000  # Context window for processing large job descriptions
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out. The model might be taking too long to respond.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    def analyze_qualifications(self, job_description: str, resume_content: str) -> QualificationAnalysis:
        """Analyze how well the resume matches the job description"""
        
        # Use enhanced analyzer if available (preliminary matching + focused AI)
        if self.enhanced_analyzer:
            print("🚀 Using Enhanced Qualifications Analyzer (Preliminary Matching + Focused AI)")
            return self.enhanced_analyzer.analyze_qualifications_enhanced(job_description, resume_content)
        
        # Fallback to original method if enhanced analyzer not available
        print("⚠️ Using Standard AI Analysis (Enhanced analyzer not available)")
        return self._analyze_qualifications_original(job_description, resume_content)
    
    def _analyze_qualifications_original(self, job_description: str, resume_content: str) -> QualificationAnalysis:
        """Original qualifications analysis method (fallback)"""
        # Use cached technologies from resume manager if available
        from app.services.resume_manager import ResumeManager
        resume_manager = ResumeManager()
        cached_tech_list = resume_manager.get_technology_list()
        
        if cached_tech_list:
            # Use cached technologies for comparison
            tech_comparison = self._compare_with_cached_technologies(job_description, cached_tech_list)
        else:
            # Fallback to extracting from resume content
            tech_comparison = self.tech_extractor.compare_technologies(job_description, resume_content)
        
        # Format technology information for the AI using simple format
        tech_summary = f"Technologies Required: {tech_comparison['total_required']}, Technologies Matched: {tech_comparison['match_count']}, Technologies Missing: {tech_comparison['missing_count']}, Match Score: {tech_comparison['score']}%"
        
        # Build simple lists for display
        matched_techs = tech_comparison['matched']
        missing_techs = tech_comparison['missing']
        
        # Get the AI prompt with pre-computed technology matches
        prompt = get_prompt(
            'qualification_analysis',
            job_description=job_description,
            resume_content=resume_content,
            tech_summary=tech_summary,
            tech_table="",  # We'll use simple format instead
            matched_technologies=', '.join(matched_techs) if matched_techs else 'None',
            missing_technologies=', '.join(missing_techs) if missing_techs else 'None'
        )
        
        response = self._call_ollama(prompt)
        
        # Parse the response to extract structured data
        analysis = self._parse_qualification_response(response, tech_comparison)
        return analysis
    
    def _parse_qualification_response(self, response: str, tech_comparison: Dict = None) -> QualificationAnalysis:
        """Parse AI response into QualificationAnalysis object"""
        # Extract match score
        match_score = 0.0
        score_match = re.search(r'Match Score:?\s*(\d+)', response, re.IGNORECASE)
        if score_match:
            match_score = float(score_match.group(1))
        
        # Extract features compared count
        features_compared = 0
        features_match = re.search(r'Features Compared:?\s*(\d+)', response, re.IGNORECASE)
        if features_match:
            features_compared = int(features_match.group(1))
        
        # Use pre-computed technology matches instead of extracting from AI response
        if tech_comparison:
            matched_techs = tech_comparison['matched']
            missing_techs = tech_comparison['missing']
        else:
            # Fallback to extracting from response if tech_comparison not provided
            matched_techs = []
            missing_techs = []
        
        # Extract strong skill matches (non-technology)
        strong_matches = []
        strong_section = re.search(r'Strong Matches:?\s*([^\n]+)', response, re.IGNORECASE)
        if strong_section:
            strong_matches = [s.strip() for s in strong_section.group(1).split(',')]
        
        # Combine strong skill matches with matched technologies
        all_strong_matches = strong_matches + matched_techs
        
        # Extract missing skills (non-technology)
        missing_skills = []
        missing_section = re.search(r'Missing Skills:?\s*([^\n]+)', response, re.IGNORECASE)
        if missing_section:
            missing_skills = [s.strip() for s in missing_section.group(1).split(',')]
        
        # Combine missing skills with missing technologies
        all_missing_skills = missing_skills + missing_techs
        
        # Extract soft skills (simplified)
        soft_skills = []
        soft_section = re.search(r'## Soft Skills Alignment(.*?)(?=##|$)', response, re.DOTALL | re.IGNORECASE)
        if soft_section:
            soft_lines = soft_section.group(1).strip().split('\n')
            for line in soft_lines:
                if line.strip() and not line.strip().startswith('#'):
                    soft_skills.append({'skill': line.strip(), 'demonstrated': '✓' in line or 'yes' in line.lower()})
        
        # Extract recommendations
        recommendations = []
        rec_section = re.search(r'## Recommendations(.*?)(?=##|$)', response, re.DOTALL | re.IGNORECASE)
        if rec_section:
            rec_lines = rec_section.group(1).strip().split('\n')
            for line in rec_lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove leading numbers or dashes
                    rec = re.sub(r'^\d+\.?\s*|-\s*', '', line)
                    if rec:
                        recommendations.append(rec)
        
        return QualificationAnalysis(
            match_score=match_score,
            features_compared=features_compared,
            strong_matches=all_strong_matches[:10] if all_strong_matches else [],
            missing_skills=all_missing_skills[:10] if all_missing_skills else [],
            partial_matches=[],
            soft_skills=soft_skills,
            recommendations=recommendations[:5] if recommendations else [],
            detailed_analysis=response
        )
    def generate_cover_letter(
        self, 
        qualifications: QualificationAnalysis, 
        company: str,
        job_title: str,
        candidate_name: str,
        research_content: str = None
    ) -> str:
        """Generate a cover letter based on qualifications analysis"""
        # Select 50% of soft skills
        soft_skills_list = [s['skill'] for s in qualifications.soft_skills[:len(qualifications.soft_skills)//2 + 1]]
        soft_skills_str = '\n- '.join(soft_skills_list) if soft_skills_list else "Leadership, Communication, Problem Solving"
        
        # Extract strong matches and missing skills for cleaner prompt
        strong_matches_str = ', '.join(qualifications.strong_matches) if qualifications.strong_matches else "Technical expertise, Data analysis, Project management"
        missing_skills_str = ', '.join(qualifications.missing_skills) if qualifications.missing_skills else "None identified"
        
        # Format research section for prompt
        if research_content:
            research_section = f"""COMPANY RESEARCH:
{research_content}

Use this research information to personalize the cover letter with specific details about the company's mission, recent news, products/services, market position, and challenges. Reference this information naturally to demonstrate genuine interest and alignment."""
        else:
            research_section = "COMPANY RESEARCH: Not available. Focus on general company interest and alignment."
        
        prompt = get_prompt(
            'cover_letter',
            strong_matches=strong_matches_str,
            missing_skills=missing_skills_str,
            soft_skills=soft_skills_str,
            company=company,
            job_title=job_title,
            research_section=research_section
        )
        
        cover_letter = self._call_ollama(prompt)
        
        # Remove any placeholder name variations and ensure actual name is used
        cover_letter = cover_letter.replace('[Name]', candidate_name)
        cover_letter = cover_letter.replace('[Your Name]', candidate_name)
        cover_letter = cover_letter.replace('[YOUR NAME]', candidate_name)
        cover_letter = cover_letter.replace('[your name]', candidate_name)
        cover_letter = cover_letter.replace('[Your Actual Name]', candidate_name)
        cover_letter = cover_letter.replace('[YOUR ACTUAL NAME]', candidate_name)
        cover_letter = cover_letter.replace('[Your Full Name]', candidate_name)
        
        contact_replacement = '917.670.0693 or leacock.kervin@gmail.com'
        cover_letter = cover_letter.replace('[Your Contact Information]', contact_replacement)
        cover_letter = cover_letter.replace('[YOUR CONTACT INFORMATION]', contact_replacement)
        cover_letter = cover_letter.replace('[Contact Information]', contact_replacement)
        
        # Remove any signature block so the standardized block can be appended downstream
        signature_pattern = re.compile(r'\n\s*Sincerely[^\n]*?(?:\n.*)?$', re.IGNORECASE | re.DOTALL)
        
        return cover_letter
    
    def scan_and_improve_cover_letter(self, cover_letter: str) -> str:
        """Scan cover letter for grammar issues and remove repetitive phrases"""
        scan_prompt = f"""You are an expert editor reviewing a cover letter. Your task is to:

1. Review the cover letter for grammatical errors and fix them
2. Identify and remove repetitive phrases or redundant language
3. Ensure the letter flows naturally and maintains its professional tone
4. Keep all the original content and meaning - only improve clarity and remove repetition
5. Do NOT change the structure, salutation, or closing format
6. Do NOT add new content - only refine what exists
7. CRITICAL: Remove any references to "current role", "current position", "current job", or similar phrases. When such references exist, either:
   - Replace with a specific company name from the resume, OR
   - Replace with company size/type reference (e.g., "at a Fortune 500 company"), OR
   - Remove the reference entirely and focus on achievements and skills

COVER LETTER TO REVIEW:
{cover_letter}

Return the improved cover letter with:
- All grammatical errors corrected
- Repetitive phrases removed or rephrased
- All "current role/position/job" references removed or replaced as specified above
- Natural flow maintained
- Original meaning and structure preserved

Start directly with the salutation and return the complete improved letter."""
        
        try:
            improved_letter = self._call_ollama(scan_prompt)
            # Ensure the candidate name is preserved if it was in the original
            # Extract name from original if it exists
            original_name_match = re.search(r'Sincerely,\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', cover_letter, re.MULTILINE)
            if original_name_match:
                original_name = original_name_match.group(1)
                # Ensure the improved version has the name
                improved_letter = re.sub(
                    r'Sincerely,\s*\n\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                    f'Sincerely,\n{original_name}',
                    improved_letter,
                    flags=re.MULTILINE
                )
            return improved_letter
        except Exception as e:
            print(f"  ⚠️ Warning: Cover letter scan failed: {e}. Using original version.")
            return cover_letter
        cover_letter = re.sub(signature_pattern, '', cover_letter).strip()
        
        # Clean up stray placeholder brackets that might remain
        cover_letter = cover_letter.replace('[Your Actual Name]', candidate_name)
        cover_letter = cover_letter.replace('[Your Contact Information]', contact_replacement)
        cover_letter = cover_letter.replace('[Your Name]', candidate_name)
        cover_letter = cover_letter.strip()
        
        return cover_letter
    
    def rewrite_resume(self, original_resume: str, qualifications: QualificationAnalysis) -> str:
        """Rewrite resume bullets based on qualifications analysis"""
        prompt = get_prompt(
            'resume_rewrite',
            original_resume=original_resume,
            qualifications=qualifications.detailed_analysis
        )
        
        rewritten_resume = self._call_ollama(prompt)
        return rewritten_resume
    
    def generate_next_steps(
        self,
        company: str,
        job_title: str,
        qualifications: QualificationAnalysis
    ) -> str:
        """Generate summary with next steps"""
        prompt = get_prompt(
            'summary_generation',
            company=company,
            job_title=job_title,
            match_score=qualifications.match_score,
            qualifications_summary=f"Strong Matches: {', '.join(qualifications.strong_matches)}\nMissing Skills: {', '.join(qualifications.missing_skills)}"
        )
        
        next_steps = self._call_ollama(prompt)
        return next_steps
    
    def extract_job_details(self, job_description: str) -> dict:
        """Extract salary range, location, hiring manager, and posted date from job description"""
        prompt = f"""Extract the following information from this job description. If any information is not found, respond with the default value.

JOB DESCRIPTION:
{job_description}

Please extract and format as follows:
- Salary Range: [extract salary range or return "$0"]
- Location: [extract location or return "N/A"]
- Hiring Manager: [extract hiring manager name if mentioned or return "N/A"]
- Posted Date: [extract when the job was posted (e.g., "2 days ago", "1 week ago", "October 14, 2024") or return "N/A"]

Be specific and only extract information that is explicitly stated."""
        
        response = self._call_ollama(prompt)
        
        # Parse response
        salary_range = "$0"
        location = "N/A"
        hiring_manager = "N/A"
        posted_date = "N/A"
        
        # Extract salary
        salary_match = re.search(r'Salary Range:?\s*([^\n]+)', response, re.IGNORECASE)
        if salary_match:
            salary_range = salary_match.group(1).strip()
            if not salary_range or salary_range.lower() in ['not found', 'not mentioned', 'n/a']:
                salary_range = "$0"
        
        # Extract location
        location_match = re.search(r'Location:?\s*([^\n]+)', response, re.IGNORECASE)
        if location_match:
            location = location_match.group(1).strip()
            if not location or location.lower() in ['not found', 'not mentioned', 'n/a', 'na']:
                location = "N/A"
        
        # If location is N/A, check job description for remote indicators
        if location.upper() == "N/A" and job_description:
            job_desc_lower = job_description.lower()
            # Check for remote patterns
            remote_patterns = [
                r'\bremote\b', r'\bwork from home\b', r'\bwfh\b',
                r'\bvirtual\b', r'\banywhere\b', r'\bdistributed\b'
            ]
            for pattern in remote_patterns:
                if re.search(pattern, job_desc_lower, re.IGNORECASE):
                    location = "Remote"
                    break
        
        # Extract hiring manager
        manager_match = re.search(r'Hiring Manager:?\s*([^\n]+)', response, re.IGNORECASE)
        if manager_match:
            hiring_manager = manager_match.group(1).strip()
            if not hiring_manager or hiring_manager.lower() in ['not found', 'not mentioned']:
                hiring_manager = "N/A"
        
        # Extract posted date
        posted_match = re.search(r'Posted Date:?\s*([^\n]+)', response, re.IGNORECASE)
        if posted_match:
            posted_date = posted_match.group(1).strip()
            if not posted_date or posted_date.lower() in ['not found', 'not mentioned']:
                posted_date = "N/A"
        
        return {
            'salary_range': salary_range,
            'location': location,
            'hiring_manager': hiring_manager,
            'posted_date': posted_date
        }
    
    def extract_comprehensive_job_details(self, job_description: str, raw_job_description: str = None) -> str:
        """
        Extract comprehensive job details and return formatted markdown.
        
        Args:
            job_description: Cleaned job description text
            raw_job_description: Original raw job description (used to extract posting date)
        
        Returns:
            Formatted markdown with structured job details
        """
        from datetime import datetime, timedelta
        
        # Extract posting date from raw description if available
        posted_date = "Not specified"
        if raw_job_description:
            posted_date = self._extract_posting_date(raw_job_description)
        
        # Use AI to extract all structured information
        prompt = get_prompt('job_description_extraction', job_description=job_description)
        extracted_info = self._call_ollama(prompt)
        
        # Format the final markdown with posting date header
        formatted_markdown = f"""# Job Description Details

**Posted Date:** {posted_date}

---

{extracted_info}
"""
        
        return formatted_markdown
    
    def _compare_with_cached_technologies(self, job_description: str, cached_tech_list: List[str]) -> Dict[str, any]:
        """Compare job description technologies with cached resume technologies"""
        # Extract technologies from job description
        job_techs = set(self.tech_extractor.extract_technologies(job_description))
        
        # Use cached technologies as resume technologies
        resume_techs = set(cached_tech_list)
        
        # Calculate matches
        matched = job_techs & resume_techs
        missing = job_techs - resume_techs
        additional = resume_techs - job_techs
        
        # Calculate simple score
        total_required = len(job_techs)
        match_count = len(matched)
        score = int((match_count / total_required * 100)) if total_required > 0 else 0
        
        return {
            'job_technologies': sorted(list(job_techs)),
            'resume_technologies': sorted(list(resume_techs)),
            'matched': sorted(list(matched)),
            'missing': sorted(list(missing)),
            'additional': sorted(list(additional)),
            'total_required': total_required,
            'match_count': match_count,
            'missing_count': len(missing),
            'score': score
        }
    
    def _extract_posting_date(self, raw_text: str) -> str:
        """
        Extract posting date from raw job description text and calculate actual date.
        Handles formats like "4 days ago", "2 weeks ago", "1 month ago", etc.
        
        Returns date in MM/DD/YYYY format.
        """
        from datetime import datetime, timedelta
        
        # Look for posting date patterns
        patterns = [
            (r'(\d+)\s+days?\s+ago', 'days'),
            (r'(\d+)\s+weeks?\s+ago', 'weeks'),
            (r'(\d+)\s+months?\s+ago', 'months'),
            (r'(\d+)\s+years?\s+ago', 'years'),
            (r'(\d+)\s+hours?\s+ago', 'hours'),
            (r'(\d+)\s+minutes?\s+ago', 'minutes'),
        ]
        
        today = datetime.now()
        
        for pattern, unit in patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                
                if unit == 'days':
                    posted_date = today - timedelta(days=value)
                elif unit == 'weeks':
                    posted_date = today - timedelta(weeks=value)
                elif unit == 'months':
                    posted_date = today - timedelta(days=value * 30)  # Approximate
                elif unit == 'years':
                    posted_date = today - timedelta(days=value * 365)  # Approximate
                elif unit == 'hours':
                    posted_date = today - timedelta(hours=value)
                elif unit == 'minutes':
                    posted_date = today - timedelta(minutes=value)
                else:
                    posted_date = today
                
                return posted_date.strftime('%m/%d/%Y')
        
        # If no pattern matched, return today's date
        return today.strftime('%m/%d/%Y')
    
    def generate_hiring_manager_intros(
        self, 
        qualifications: QualificationAnalysis,
        company: str,
        job_title: str,
        candidate_name: str,
        research_content: str = None
    ) -> str:
        """Generate hiring manager intro messages (3 versions)"""
        # Extract strong matches for cleaner prompt
        strong_matches_str = ', '.join(qualifications.strong_matches[:5]) if qualifications.strong_matches else "Technical expertise, Data analysis, Project management"
        
        # Format research section for prompt
        if research_content:
            research_section = f"""COMPANY RESEARCH:
{research_content}

Use this research information to personalize the intro messages with specific details about the company's mission, recent news, products/services, challenges, or key personnel. Reference this information naturally within character limits to demonstrate genuine interest and alignment."""
        else:
            research_section = "COMPANY RESEARCH: Not available. Focus on general company interest and alignment."
        
        prompt = get_prompt(
            'hiring_manager_intro',
            company=company,
            job_title=job_title,
            match_score=qualifications.match_score,
            strong_matches=strong_matches_str,
            candidate_name=candidate_name,
            research_section=research_section
        )
        
        intro_messages = self._call_ollama(prompt)
        return intro_messages
    
    def generate_recruiter_intros(
        self, 
        qualifications: QualificationAnalysis,
        company: str,
        job_title: str,
        candidate_name: str,
        research_content: str = None
    ) -> str:
        """Generate recruiter intro messages (3 versions, non-technical)"""
        # Extract strong matches for cleaner prompt, avoiding technical jargon
        strong_matches_str = ', '.join(qualifications.strong_matches[:5]) if qualifications.strong_matches else "Business expertise, Data analysis, Project management"
        
        # Format research section for prompt (use business language)
        if research_content:
            research_section = f"""COMPANY RESEARCH:
{research_content}

Use this research information to personalize the intro messages with specific details about the company's mission, recent news, products/services, or market position. Express these details in business language (avoid technical jargon). Reference this information naturally within character limits to demonstrate genuine interest and alignment."""
        else:
            research_section = "COMPANY RESEARCH: Not available. Focus on general company interest and alignment in business terms."
        
        prompt = get_prompt(
            'recruiter_intro',
            company=company,
            job_title=job_title,
            match_score=qualifications.match_score,
            strong_matches=strong_matches_str,
            candidate_name=candidate_name,
            research_section=research_section
        )
        
        intro_messages = self._call_ollama(prompt)
        return intro_messages

