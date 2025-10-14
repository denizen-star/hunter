"""AI analysis service using Ollama"""
import json
import re
from typing import Dict, List, Optional
import requests
from app.models.qualification import QualificationAnalysis
from app.utils.prompts import get_prompt


class AIAnalyzer:
    """AI-powered analysis and generation using Ollama"""
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.timeout = 600  # 10 minutes timeout for longer responses
    
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
        prompt = get_prompt(
            'qualification_analysis',
            job_description=job_description,
            resume_content=resume_content
        )
        
        response = self._call_ollama(prompt)
        
        # Parse the response to extract structured data
        analysis = self._parse_qualification_response(response)
        return analysis
    
    def _parse_qualification_response(self, response: str) -> QualificationAnalysis:
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
        
        # Extract strong matches
        strong_matches = []
        strong_section = re.search(r'Strong Matches:?\s*([^\n]+)', response, re.IGNORECASE)
        if strong_section:
            strong_matches = [s.strip() for s in strong_section.group(1).split(',')]
        
        # Extract missing skills
        missing_skills = []
        missing_section = re.search(r'Missing Skills:?\s*([^\n]+)', response, re.IGNORECASE)
        if missing_section:
            missing_skills = [s.strip() for s in missing_section.group(1).split(',')]
        
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
            strong_matches=strong_matches[:5] if strong_matches else [],
            missing_skills=missing_skills[:5] if missing_skills else [],
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
        candidate_name: str
    ) -> str:
        """Generate a cover letter based on qualifications analysis"""
        # Select 50% of soft skills
        soft_skills_list = [s['skill'] for s in qualifications.soft_skills[:len(qualifications.soft_skills)//2 + 1]]
        soft_skills_str = '\n- '.join(soft_skills_list) if soft_skills_list else "Leadership, Communication, Problem Solving"
        
        prompt = get_prompt(
            'cover_letter',
            qualifications=qualifications.detailed_analysis,
            soft_skills=soft_skills_str,
            company=company,
            job_title=job_title
        )
        
        cover_letter = self._call_ollama(prompt)
        
        # Replace placeholder name if exists
        cover_letter = cover_letter.replace('[Name]', candidate_name)
        
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
        """Extract salary range, location, and hiring manager from job description"""
        prompt = f"""Extract the following information from this job description. If any information is not found, respond with the default value.

JOB DESCRIPTION:
{job_description}

Please extract and format as follows:
- Salary Range: [extract salary range or return "$0"]
- Location: [extract location or return "N/A"]
- Hiring Manager: [extract hiring manager name if mentioned or return "N/A"]

Be specific and only extract information that is explicitly stated."""
        
        response = self._call_ollama(prompt)
        
        # Parse response
        salary_range = "$0"
        location = "N/A"
        hiring_manager = "N/A"
        
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
            if not location or location.lower() in ['not found', 'not mentioned']:
                location = "N/A"
        
        # Extract hiring manager
        manager_match = re.search(r'Hiring Manager:?\s*([^\n]+)', response, re.IGNORECASE)
        if manager_match:
            hiring_manager = manager_match.group(1).strip()
            if not hiring_manager or hiring_manager.lower() in ['not found', 'not mentioned']:
                hiring_manager = "N/A"
        
        return {
            'salary_range': salary_range,
            'location': location,
            'hiring_manager': hiring_manager
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

