#!/usr/bin/env python3
"""
Enhanced Qualifications Analyzer - Integrates preliminary matching with AI analysis
"""

from app.models.qualification import QualificationAnalysis
from app.services.preliminary_matcher import PreliminaryMatcher
from typing import Dict, Optional
import requests

class EnhancedQualificationsAnalyzer:
    """Enhanced qualifications analyzer that reduces AI load through preliminary matching"""
    
    def __init__(self):
        self.preliminary_matcher = PreliminaryMatcher()
        self.model = "llama3"
        self.base_url = "http://localhost:11434"
        self.timeout = 600
    
    def _call_ollama(self, prompt: str) -> str:
        """Make a call to Ollama API"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out. The model might be taking too long to respond.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    def analyze_qualifications_enhanced(self, job_description: str, resume_content: str) -> QualificationAnalysis:
        """Enhanced qualifications analysis with preliminary matching"""
        
        # Step 1: Run preliminary matching
        print("🔍 Running preliminary skills matching...")
        preliminary_analysis = self.preliminary_matcher.generate_preliminary_analysis(job_description)
        
        # Step 2: Create focused AI prompt based on preliminary results
        print("🤖 Creating focused AI analysis prompt...")
        ai_context = self.preliminary_matcher.create_ai_prompt_context(job_description)
        
        # Step 3: Run AI analysis with focused prompt
        print("🧠 Running AI analysis with preliminary context...")
        ai_analysis = self._run_focused_ai_analysis(
            job_description, 
            resume_content, 
            preliminary_analysis,
            ai_context
        )
        
        # Step 4: Combine preliminary and AI results
        print("📊 Combining preliminary and AI analysis results...")
        combined_analysis = self._combine_analyses(preliminary_analysis, ai_analysis)
        
        return combined_analysis
    
    def _run_focused_ai_analysis(self, job_description: str, resume_content: str, 
                                preliminary_analysis: Dict, ai_context: str) -> Dict:
        """Run AI analysis with focused prompt based on preliminary results"""
        
        # Create focused prompt
        focused_prompt = f"""
You are a career advisor analyzing how well a candidate's resume matches a job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_content}

---
PRELIMINARY MATCHING RESULTS:
{ai_context}
---

Based on the preliminary matching results above, please provide a focused analysis in the following format:

## Skills Match Summary
- Match Score: [percentage as a number, e.g., 85]
- Features Compared: [total number of features/skills analyzed]
- Strong Matches: [list of strong matches from preliminary analysis]
- Missing Skills: [list of skills that are genuinely absent, focusing on the AI focus areas]
- Partial Matches: [list of partial matches that need context analysis]

## Skills Analysis by Category

### Technical Skills
| Skill | Job Requirement | Resume Evidence | Match Level |
| --- | --- | --- | --- |
| [Technical skill] | [Quote from job description] | [Quote from resume or "Not demonstrated"] | Strong Match / Partial Match / No Match |

### Leadership & Management Skills
| Skill | Job Requirement | Resume Evidence | Match Level |
| --- | --- | --- | --- |
| [Leadership skill] | [Quote from job description] | [Quote from resume or "Not demonstrated"] | Strong Match / Partial Match / No Match |

### Business & Strategy Skills
| Skill | Job Requirement | Resume Evidence | Match Level |
| --- | --- | --- | --- |
| [Business skill] | [Quote from job description] | [Quote from resume or "Not demonstrated"] | Strong Match / Partial Match / No Match |

### Domain Expertise
| Skill | Job Requirement | Resume Evidence | Match Level |
| --- | --- | --- | --- |
| [Domain skill] | [Quote from job description] | [Quote from resume or "Not demonstrated"] | Strong Match / Partial Match / No Match |

## Unmatched Skills Analysis
List skills from the job description that are NOT found in the candidate's resume:

### Technical Skills Not Matched
- [List technical skills from job that are missing from resume]

### Leadership Skills Not Matched
- [List leadership skills from job that are missing from resume]

### Business Skills Not Matched
- [List business skills from job that are missing from resume]

### Domain Expertise Not Matched
- [List domain expertise from job that are missing from resume]

## Recommendations
Provide specific recommendations based on the preliminary matching results:
1. [Recommendation to emphasize relevant experience]
2. [Recommendation to address gaps identified in preliminary matching]
3. [Recommendation for interview preparation]
4. [Additional recommendations based on AI focus areas]

## Overall Assessment
Provide an overall assessment considering both the preliminary matching results and your detailed analysis.
"""
        
        # Get AI response
        response = self._call_ollama(focused_prompt)
        
        # Parse the response
        return self._parse_ai_response(response)
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured data"""
        analysis = {
            'match_score': 0.0,
            'features_compared': 0,
            'strong_matches': [],
            'missing_skills': [],
            'partial_matches': [],
            'soft_skills': [],
            'recommendations': [],
            'detailed_analysis': response
        }
        
        # Extract match score
        import re
        score_match = re.search(r'Match Score:\s*(\d+)', response)
        if score_match:
            analysis['match_score'] = float(score_match.group(1))
        
        # Extract features compared
        features_match = re.search(r'Features Compared:\s*(\d+)', response)
        if features_match:
            analysis['features_compared'] = int(features_match.group(1))
        
        # Extract strong matches
        strong_matches_section = self._extract_section(response, 'Strong Matches:')
        if strong_matches_section:
            analysis['strong_matches'] = self._parse_list_items(strong_matches_section)
        
        # Extract missing skills
        missing_skills_section = self._extract_section(response, 'Missing Skills:')
        if missing_skills_section:
            analysis['missing_skills'] = self._parse_list_items(missing_skills_section)
        
        # Extract partial matches
        partial_matches_section = self._extract_section(response, 'Partial Matches:')
        if partial_matches_section:
            analysis['partial_matches'] = self._parse_list_items(partial_matches_section)
        
        # Extract recommendations
        recommendations_section = self._extract_section(response, '## Recommendations')
        if recommendations_section:
            analysis['recommendations'] = self._parse_list_items(recommendations_section)
        
        return analysis
    
    def _extract_section(self, text: str, section_header: str) -> str:
        """Extract a specific section from text"""
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if line.strip().startswith(section_header):
                in_section = True
                continue
            elif line.startswith('##') and in_section:
                break
            elif in_section:
                section_content.append(line)
        
        return '\n'.join(section_content)
    
    def _parse_list_items(self, text: str) -> list:
        """Parse list items from text"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())
            elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. '):
                items.append(line[3:].strip())
        
        return items
    
    def _combine_analyses(self, preliminary_analysis: Dict, ai_analysis: Dict) -> QualificationAnalysis:
        """Combine preliminary and AI analysis results"""
        
        # Use AI match score if available, otherwise use preliminary score
        match_score = ai_analysis.get('match_score', preliminary_analysis.get('preliminary_match_score', 0.0))
        
        # Combine strong matches
        strong_matches = []
        for match in preliminary_analysis.get('exact_matches', []):
            strong_matches.append(match['skill'])
        strong_matches.extend(ai_analysis.get('strong_matches', []))
        
        # Combine missing skills
        missing_skills = ai_analysis.get('missing_skills', [])
        
        # Combine partial matches
        partial_matches = []
        for match in preliminary_analysis.get('partial_matches', []):
            partial_matches.append(match['skill'])
        partial_matches.extend(ai_analysis.get('partial_matches', []))
        
        # Create soft skills list
        soft_skills = []
        for match in preliminary_analysis.get('exact_matches', []):
            if match['category'] in ['Leadership', 'Communication', 'Strategic Thinking', 'Problem Solving']:
                soft_skills.append({
                    'skill': match['skill'],
                    'category': match['category'],
                    'match_level': 'Strong Match'
                })
        
        # Combine recommendations
        recommendations = ai_analysis.get('recommendations', [])
        
        # Create detailed analysis
        detailed_analysis = f"""
PRELIMINARY MATCHING RESULTS:
- Match Score: {preliminary_analysis.get('preliminary_match_score', 0)}%
- Exact Matches: {len(preliminary_analysis.get('exact_matches', []))}
- Partial Matches: {len(preliminary_analysis.get('partial_matches', []))}
- AI Focus Areas: {', '.join(preliminary_analysis.get('ai_focus_areas', []))}

{ai_analysis.get('detailed_analysis', '')}
"""
        
        return QualificationAnalysis(
            match_score=match_score,
            features_compared=ai_analysis.get('features_compared', len(strong_matches) + len(missing_skills)),
            strong_matches=strong_matches,
            missing_skills=missing_skills,
            partial_matches=partial_matches,
            soft_skills=soft_skills,
            recommendations=recommendations,
            detailed_analysis=detailed_analysis
        )

if __name__ == "__main__":
    # Test the enhanced analyzer
    analyzer = EnhancedQualificationsAnalyzer()
    
    sample_job = """
    We are looking for a Senior Data Engineer with experience in:
    - Python and SQL programming
    - AWS cloud platforms and services
    - Data warehousing and ETL processes
    - Team leadership and project management
    - Business intelligence tools like Tableau and Power BI
    - Machine learning and data science experience
    """
    
    sample_resume = """
    Kervin Leacock - Data Analytics Professional
    - 15+ years experience in data analytics and business intelligence
    - Python, SQL, R programming languages
    - AWS, Docker, Kubernetes experience
    - Data warehousing, data lakes, data mesh
    - Tableau, Qlik, Business Objects
    - Team leadership and project management
    - Product management experience
    """
    
    result = analyzer.analyze_qualifications_enhanced(sample_job, sample_resume)
    print(f"Enhanced Analysis Complete!")
    print(f"Match Score: {result.match_score}%")
    print(f"Strong Matches: {len(result.strong_matches)}")
    print(f"Missing Skills: {len(result.missing_skills)}")
    print(f"Recommendations: {len(result.recommendations)}")
