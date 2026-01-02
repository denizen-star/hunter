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
        
        # PERFORMANCE: Pre-compute these sets once at initialization instead of on every match
        # This avoids expensive nested set comprehensions during validation
        self._candidate_skills_lower_cache = {skill.lower() for skill in self.preliminary_matcher.candidate_skills.keys()}
        self._known_technologies_lower_cache = {tech.lower() for tech in self.preliminary_matcher.tech_extractor.TECHNOLOGIES.keys()}
        # Pre-compute which candidate skills are technologies (avoids O(n*m) check on every match)
        self._candidate_technologies_lower_cache = {
            skill.lower() for skill in self._candidate_skills_lower_cache
            if skill.lower() in self._known_technologies_lower_cache
        }
    
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
        # Reuse the existing matcher instance (it's stateless, so no state issues)
        preliminary_analysis = self.preliminary_matcher.generate_preliminary_analysis(job_description)
        
        # Step 2: Create focused AI prompt based on preliminary results
        from app.utils.message_logger import log_message
        log_message(46, "🤖 Creating focused AI analysis prompt...")
        ai_context = self.preliminary_matcher.create_ai_prompt_context(job_description, preliminary_analysis)
        
        # Step 3: Run AI analysis with focused prompt
        log_message(47, "🧠 Running AI analysis with preliminary context...")
        ai_analysis = self._run_focused_ai_analysis(
            job_description, 
            resume_content, 
            preliminary_analysis,
            ai_context
        )
        
        # Step 4: Combine preliminary and AI results
        print("📊 Combining preliminary and AI analysis results...")
        combined_analysis = self._combine_analyses(preliminary_analysis, ai_analysis, job_description, resume_content)
        
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

IMPORTANT: Be GENEROUS in recognizing skills and experience. Look for equivalent or related skills that demonstrate the same capabilities. For example:
- "AWS experience" covers AWS Lake Formation, Kinesis, etc.
- "Data engineering" covers data warehousing, ETL, pipelines, etc.
- "Leadership" covers team management, budget management, financial oversight, etc.
- "Strategy" covers product strategy, business strategy, planning, etc.
- "Cloud platforms" covers AWS, Azure, GCP and their specific services

## Skills Match Summary
- Match Score: [percentage as a number, e.g., 85 - be generous for overqualified candidates]
- Features Compared: [total number of features/skills analyzed]
- Strong Matches: [list of strong matches from preliminary analysis + equivalent skills found]
- Missing Skills: [ONLY list skills that are genuinely absent - be very conservative here]
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
CRITICAL: ONLY list skills that are in the "UNMATCHED JOB SKILLS" section from the preliminary matching results above.
DO NOT add skills that are not explicitly listed in the preliminary unmatched skills.
DO NOT infer or extrapolate skills - only use what the preliminary matcher actually found in the job description.

If there are no unmatched skills listed in the preliminary results, write "None" for each category.

### Technical Skills Not Matched
- [ONLY list technical skills from preliminary unmatched list that are missing from resume]

### Leadership Skills Not Matched
- [ONLY list leadership skills from preliminary unmatched list that are missing from resume]

### Business Skills Not Matched
- [ONLY list business skills from preliminary unmatched list that are missing from resume]

### Domain Expertise Not Matched
- [ONLY list domain expertise from preliminary unmatched list that are missing from resume]

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
        
        # Extract match score (but we'll ignore it - we use preliminary score instead)
        # This is kept for logging/debugging purposes only
        import re
        score_match = re.search(r'Match Score:\s*(\d+(?:\.\d+)?)', response)
        if score_match:
            # Store AI score but we won't use it - preliminary matcher is source of truth
            analysis['match_score'] = float(score_match.group(1))
        else:
            analysis['match_score'] = 0.0
        
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
    
    def _validate_technology_match(
        self, 
        tech_name: str, 
        job_technologies_lower: set, 
        candidate_skills_lower: set,
        candidate_technologies_lower: set,
        known_technologies_lower: set
    ) -> bool:
        """
        Validate that a technology should be marked as a strong match.
        
        Rules:
        1. Technology must be mentioned in job description
        2. Technology must exist in candidate's skills (from cached skills.yaml)
        
        This prevents false positives like Power BI appearing as a match
        when it's only in the JD, not the candidate's resume.
        
        Args:
            tech_name: Technology name to validate (lowercase)
            job_technologies_lower: Set of technologies found in JD (lowercase)
            candidate_skills_lower: Set of all candidate skills (lowercase)
            candidate_technologies_lower: Set of candidate technologies (lowercase)
            known_technologies_lower: Set of all known technology names (lowercase)
            
        Returns:
            True if technology should be marked as strong match, False otherwise
        """
        # Must be a recognized technology
        if tech_name not in known_technologies_lower:
            return False
        
        # Must be mentioned in job description
        if tech_name not in job_technologies_lower:
            return False
        
        # Must exist in candidate skills (from cached skills.yaml)
        # Check direct match first (fast set lookup)
        if tech_name in candidate_skills_lower or tech_name in candidate_technologies_lower:
            return True
        
        # PERFORMANCE: Only do substring matching if direct match fails
        # Check if any candidate skill contains the technology (for variations)
        # e.g., "Power BI" might match "Microsoft Power BI" in skills
        # Use words instead of full string to speed up matching
        tech_words = set(tech_name.split())
        if len(tech_words) > 1:  # Multi-word technologies
            # Check if most words appear in any candidate skill
            for candidate_skill in candidate_skills_lower:
                candidate_words = set(candidate_skill.split())
                # If 50%+ words match, consider it a match
                if len(tech_words & candidate_words) >= (len(tech_words) * 0.5):
                    return True
        else:  # Single word - use substring check only
            if any(tech_name in candidate_skill or candidate_skill in tech_name 
                   for candidate_skill in candidate_skills_lower):
                return True
        
        return False
    
    def _combine_analyses(self, preliminary_analysis: Dict, ai_analysis: Dict, job_description: str, resume_content: str = "") -> QualificationAnalysis:
        """Combine preliminary and AI analysis results"""
        
        # TRUST PRELIMINARY MATCHER SCORE as source of truth
        # AI scores can be inconsistent, so we prioritize the preliminary matcher which uses
        # exact, validated matching against known skills
        
        # FORCE PRELIMINARY SCORE - NO EXCEPTIONS
        # Get score from preliminary analysis (the ONLY reliable source)
        prelim_score_raw = preliminary_analysis.get('preliminary_match_score', None)
        prelim_score_from_summary = None
        if 'match_summary' in preliminary_analysis:
            prelim_score_from_summary = preliminary_analysis['match_summary'].get('match_percentage', None)
        
        # Use the first available score
        final_prelim_score = prelim_score_raw if prelim_score_raw is not None else prelim_score_from_summary
        
        if final_prelim_score is None:
            # Last resort: recalculate from match data
            exact_count = len(preliminary_analysis.get('exact_matches', []))
            partial_count = len(preliminary_analysis.get('partial_matches', []))
            unmatched_count = len(preliminary_analysis.get('unmatched_job_skills', []))
            total_skills = exact_count + unmatched_count
            if total_skills > 0:
                final_prelim_score = (exact_count / total_skills) * 100
            else:
                final_prelim_score = 0.0
        
        # COMPLETELY IGNORE AI SCORE - IT'S UNRELIABLE
        ai_score = ai_analysis.get('match_score', 0.0)
        
        # FORCE: Use preliminary score, no matter what
        match_score_final = float(final_prelim_score)
        match_score = match_score_final
        
        # Safety check: Warn if scores differ significantly
        if abs(final_prelim_score - ai_score) > 5 and final_prelim_score > 0:
            print(f"⚠️  WARNING: Score mismatch detected! Preliminary={final_prelim_score}%, AI={ai_score}%, USING PRELIMINARY={match_score_final}%")
        
        # Combine missing skills from both preliminary analysis and AI analysis
        ai_missing_skills = ai_analysis.get('missing_skills', [])
        preliminary_unmatched = preliminary_analysis.get('unmatched_job_skills', [])
        
        # VALIDATION: Trust preliminary matcher as the source of truth
        # Only use preliminary unmatched skills to avoid AI hallucinations
        # The AI tends to add specific skills (like "Stakeholder Management") when
        # only generic terms (like "management") appear in the job description
        
        # Use preliminary unmatched skills as the base (these are actually from the job)
        missing_skills = preliminary_unmatched.copy()
        
        # Only add AI skills if they EXACTLY match preliminary unmatched (avoid specifc -> generic)
        for ai_skill in ai_missing_skills:
            ai_skill_lower = ai_skill.lower().strip()
            # Only add if exact match (case-insensitive)
            if ai_skill_lower not in [s.lower() for s in missing_skills]:
                # Check for exact match in preliminary
                if any(ai_skill_lower == pre_skill.lower().strip() for pre_skill in preliminary_unmatched):
                    missing_skills.append(ai_skill)
        
        # For backward compatibility, extract simple lists from preliminary_analysis
        # These will be deprecated in favor of using preliminary_analysis directly
        strong_matches = [match.get('skill', '') for match in preliminary_analysis.get('exact_matches', [])]
        partial_matches = [match.get('skill', '') for match in preliminary_analysis.get('partial_matches', [])]
        partial_matches.extend(ai_analysis.get('partial_matches', []))
        
        # Soft skills are a subset of exact matches by category
        soft_skills = []
        for match in preliminary_analysis.get('exact_matches', []):
            if match.get('category', '') in ['Leadership', 'Communication', 'Strategic Thinking', 'Problem Solving']:
                soft_skills.append({
                    'skill': match.get('skill', ''),
                    'category': match.get('category', ''),
                    'match_level': 'Strong Match'
                })
        
        # Combine recommendations
        recommendations = ai_analysis.get('recommendations', [])
        
        # Sanitize AI's detailed_analysis to replace any Match Score mentions with the correct preliminary score
        # This prevents confusion from conflicting scores in the text
        import re
        ai_detailed = ai_analysis.get('detailed_analysis', '')
        # Replace any "Match Score: X%" patterns with the correct preliminary score
        ai_detailed = re.sub(
            r'Match Score:\s*\d+(?:\.\d+)?%?',
            f'Match Score: {match_score:.0f}% (using preliminary matcher score)',
            ai_detailed,
            flags=re.IGNORECASE
        )
        
        # Remove unwanted sections from AI detailed analysis
        # Remove: SKILL MAPPING, Skills Match Summary, Skills Analysis by Category, Unmatched Skills Analysis
        sections_to_remove = [
            r'##?\s*SKILL MAPPING.*?(?=##|\*\*|$)',
            r'##?\s*Skills Match Summary.*?(?=##|\*\*|$)',
            r'##?\s*Skills Analysis by Category.*?(?=##|\*\*|$)',
            r'##?\s*Unmatched Skills Analysis.*?(?=##|\*\*|$)',
        ]
        for pattern in sections_to_remove:
            ai_detailed = re.sub(pattern, '', ai_detailed, flags=re.DOTALL | re.IGNORECASE)
        
        # Create detailed analysis - keep only Recommendations and Overall Assessment
        detailed_analysis = f"""
PRELIMINARY MATCHING RESULTS:
- Match Score: {match_score:.0f}% (Source: Preliminary Matcher - validated skill matching)
- Exact Matches: {len(preliminary_analysis.get('exact_matches', []))}
- Partial Matches: {len(preliminary_analysis.get('partial_matches', []))}
- AI Focus Areas: {', '.join(preliminary_analysis.get('ai_focus_areas', []))}

{ai_detailed}
"""
        
        return QualificationAnalysis(
            match_score=match_score,
            features_compared=ai_analysis.get('features_compared', len(strong_matches) + len(missing_skills)),
            strong_matches=strong_matches,
            missing_skills=missing_skills,
            partial_matches=partial_matches,
            soft_skills=soft_skills,
            recommendations=recommendations,
            detailed_analysis=detailed_analysis,
            preliminary_analysis=preliminary_analysis  # Store as single source of truth
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
    from app.utils.message_logger import log_message
    log_message(80, f"Enhanced Analysis Complete!")
    log_message(81, f"Match Score: {result.match_score}%")
    log_message(82, f"Strong Matches: {len(result.strong_matches)}")
    log_message(83, f"Missing Skills: {len(result.missing_skills)}")
    log_message(84, f"Recommendations: {len(result.recommendations)}")
