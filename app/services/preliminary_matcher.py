#!/usr/bin/env python3
"""
Preliminary Skills Matcher - Reduces AI load by doing initial matching
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from app.utils.file_utils import read_text_file

class PreliminaryMatcher:
    """Preliminary matching system to reduce AI load"""
    
    def __init__(self):
        self.skills_yaml_path = Path("/Users/kervinleacock/Documents/Development/hunter/data/resumes/skills.yaml")
        self.job_skills_path = Path("/Users/kervinleacock/Documents/Development/hunter/Jobdescr-General Skils.md")
        self.candidate_skills = {}
        self.job_skills = {}
        self.load_skills_data()
    
    def load_skills_data(self):
        """Load both skills files"""
        # Load candidate skills
        with open(self.skills_yaml_path, 'r') as f:
            skills_data = yaml.safe_load(f)
            self.candidate_skills = skills_data.get('skills', {})
        
        # Load job skills from markdown
        job_skills_content = read_text_file(self.job_skills_path)
        self.job_skills = self._parse_job_skills_markdown(job_skills_content)
    
    def _parse_job_skills_markdown(self, content: str) -> Dict[str, List[str]]:
        """Parse job skills from markdown file"""
        skills = {
            'technical_skills': [],
            'soft_skills': [],
            'tools_technologies': [],
            'experience_requirements': [],
            'education_certifications': []
        }
        
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('## Technical Skills'):
                current_section = 'technical_skills'
            elif line.startswith('## Soft Skills'):
                current_section = 'soft_skills'
            elif line.startswith('## Tools Technologies'):
                current_section = 'tools_technologies'
            elif line.startswith('## Experience Requirements'):
                current_section = 'experience_requirements'
            elif line.startswith('## Education Certifications'):
                current_section = 'education_certifications'
            elif line.startswith('- ') and current_section:
                skill = line[2:].strip()
                if skill and skill not in skills[current_section]:
                    skills[current_section].append(skill)
        
        return skills
    
    def normalize_skill_name(self, skill: str) -> str:
        """Normalize skill names for better matching"""
        # Convert to lowercase and remove extra spaces
        skill = skill.lower().strip()
        
        # Skip invalid skills early
        invalid_patterns = [
            r'^etc\.\)?$',  # "etc.)" or "etc."
            r'^\)$',        # Just ")"
            r'^\d+\)?$',    # Just numbers
            r'^[^a-zA-Z]+$', # No letters
            r'^.{1,2}$'     # Too short (1-2 characters)
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, skill, re.IGNORECASE):
                return ""  # Return empty string for invalid skills
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            'experience with', 'knowledge of', 'proficiency in', 'expertise in',
            'strong', 'excellent', 'advanced', 'basic', 'working knowledge of',
            'familiarity with', 'hands-on experience with', 'demonstrated expertise in'
        ]
        
        for prefix in prefixes_to_remove:
            if skill.startswith(prefix):
                skill = skill[len(prefix):].strip()
                break
        
        # Remove parenthetical information
        if '(' in skill and ')' in skill:
            skill = skill.split('(')[0].strip()
        
        # Remove common suffixes
        suffixes_to_remove = ['experience', 'knowledge', 'skills', 'expertise', 'proficiency']
        for suffix in suffixes_to_remove:
            if skill.endswith(suffix):
                skill = skill[:-len(suffix)].strip()
                break
        
        return skill
    
    def find_skill_matches(self, job_description: str) -> Dict[str, any]:
        """Find matches between job description and candidate skills"""
        
        # Normalize job description
        job_desc_lower = job_description.lower()
        
        # Initialize results
        matches = {
            'exact_matches': [],
            'partial_matches': [],
            'missing_skills': [],
            'unmatched_job_skills': [],
            'match_score': 0.0,
            'total_required': 0,
            'matched_count': 0,
            'missing_count': 0,
            'match_details': {}
        }
        
        # Extract job skills first
        job_skills_found = self._extract_job_skills_from_description(job_description)
        
        # Check each candidate skill against job description
        matched_skills = set()
        for skill_name, skill_data in self.candidate_skills.items():
            skill_normalized = self.normalize_skill_name(skill_name)
            
            # Skip invalid or empty skills
            if not skill_normalized:
                continue
                
            skill_variations = [skill_normalized] + skill_data.get('variations_found', [])
            
            # Check for exact matches
            exact_match = False
            partial_match = False
            
            for variation in skill_variations:
                if variation and variation in job_desc_lower:
                    exact_match = True
                    matched_skills.add(skill_name)
                    break
                elif variation and self._is_partial_match(variation, job_desc_lower):
                    partial_match = True
                    matched_skills.add(skill_name)
            
            if exact_match:
                # Find which job skill this matches
                matched_job_skill = self._find_matched_job_skill(skill_name, skill_normalized, job_skills_found)
                matches['exact_matches'].append({
                    'skill': skill_name,
                    'job_skill': matched_job_skill,
                    'category': skill_data.get('category', 'Unknown'),
                    'source': skill_data.get('source', 'Unknown')
                })
            elif partial_match:
                # Find which job skill this matches
                matched_job_skill = self._find_matched_job_skill(skill_name, skill_normalized, job_skills_found)
                matches['partial_matches'].append({
                    'skill': skill_name,
                    'job_skill': matched_job_skill,
                    'category': skill_data.get('category', 'Unknown'),
                    'source': skill_data.get('source', 'Unknown')
                })
        
        # Find unmatched candidate skills
        for skill_name, skill_data in self.candidate_skills.items():
            if skill_name not in matched_skills:
                matches['missing_skills'].append({
                    'skill': skill_name,
                    'category': skill_data.get('category', 'Unknown'),
                    'source': skill_data.get('source', 'Unknown')
                })
        
        # Find job skills that don't match candidate skills
        for job_skill in job_skills_found:
            if not self._is_skill_matched(job_skill, matched_skills):
                matches['unmatched_job_skills'].append(job_skill)
        
        # Calculate match score based on job requirements, not candidate skills
        total_job_skills = len(job_skills_found)
        exact_count = len(matches['exact_matches'])
        partial_count = len(matches['partial_matches'])
        
        # Calculate how many job skills are matched by candidate
        matched_job_skills = 0
        for job_skill in job_skills_found:
            if self._is_skill_matched(job_skill, matched_skills):
                matched_job_skills += 1
        
        matches['total_required'] = total_job_skills if total_job_skills > 0 else len(self.candidate_skills)
        matches['matched_count'] = exact_count + partial_count
        matches['missing_count'] = matches['total_required'] - matched_job_skills
        
        # Calculate match score based on job requirements with overqualification bonus
        if total_job_skills > 0:
            base_score = (matched_job_skills / total_job_skills) * 100
            
            # Apply overqualification bonus - if candidate has significantly more skills than required
            total_candidate_skills = len(self.candidate_skills)
            overqualification_ratio = total_candidate_skills / total_job_skills if total_job_skills > 0 else 1
            
            # If candidate is overqualified (has 2x+ more skills than required)
            if overqualification_ratio >= 2.0:
                # Apply significant overqualification bonus
                if overqualification_ratio >= 4.0:  # 4x+ overqualified
                    overqualification_bonus = 35  # 35% bonus for highly overqualified
                elif overqualification_ratio >= 3.0:  # 3x+ overqualified
                    overqualification_bonus = 25  # 25% bonus for very overqualified
                else:  # 2x+ overqualified
                    overqualification_bonus = 15  # 15% bonus for overqualified
                
                base_score = min(100, base_score + overqualification_bonus)
            
            matches['match_score'] = round(base_score, 2)
        else:
            # Fallback to candidate skills if no job skills found
            total_skills = len(self.candidate_skills)
            if total_skills > 0:
                matches['match_score'] = round((exact_count + (partial_count * 0.5)) / total_skills * 100, 2)
        
        return matches
    
    def _extract_job_skills_from_description(self, job_description: str) -> List[str]:
        """Extract skills mentioned in job description"""
        job_skills = []
        job_desc_lower = job_description.lower()
        
        # Extract skills from specific sections of job description
        sections_to_check = [
            "required qualifications and skills",
            "must-have technical skills",
            "must-have soft skills",
            "preferred qualifications",
            "key responsibilities and duties"
        ]
        
        # Check against known job skills patterns (only exact matches to avoid noise)
        for category, skills in self.job_skills.items():
            for skill in skills:
                skill_normalized = self.normalize_skill_name(skill)
                if skill_normalized and skill_normalized in job_desc_lower:
                    job_skills.append(skill)
        
        # Also extract specific skills mentioned in the job description
        specific_skills = [
            "python", "sql", "tableau", "power bi", "looker", "excel", "sheets",
            "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "terraform",
            "snowflake", "bigquery", "spark", "hadoop", "kafka", "airflow",
            "machine learning", "ai", "data science", "data engineering",
            "business intelligence", "analytics", "etl", "data warehousing",
            "leadership", "management", "team", "mentoring", "coaching",
            "strategy", "strategic", "business intelligence", "analytics", "forecasting",
            "pricing", "modeling", "financial", "budget", "planning"
        ]
        
        for skill in specific_skills:
            if skill in job_desc_lower and skill not in [s.lower() for s in job_skills]:
                job_skills.append(skill.title())
        
        # Filter out invalid skills and clean up the list
        filtered_skills = []
        invalid_patterns = [
            r'^etc\.\)?$',  # "etc.)" or "etc."
            r'^\)$',        # Just ")"
            r'^\d+\)?$',    # Just numbers
            r'^[^a-zA-Z]+$', # No letters
            r'^.{1,2}$',    # Too short (1-2 characters)
            r'^tools and technologies:$',  # Section headers
            r'^experience in$',  # Incomplete phrases
            r'^bonus\)?$',  # Bonus items
            r'^not specified\)?$',  # Placeholder text
            r'^\d+\+ years',  # Years of experience without skill
            r'^.{50,}$',     # Too long (more than 50 characters)
            r'^.*experience.*$',  # Phrases about experience
            r'^.*years.*$',  # Phrases about years
            r'^.*degree.*$',  # Phrases about degrees
            r'^.*bachelor.*$',  # Phrases about bachelor's
            r'^.*master.*$',  # Phrases about master's
            r'^.*minimum.*$',  # Phrases about minimum requirements
            r'^.*preferred.*$',  # Phrases about preferred qualifications
        ]
        
        for skill in job_skills:
            skill_clean = skill.strip()
            is_valid = True
            
            for pattern in invalid_patterns:
                if re.match(pattern, skill_clean, re.IGNORECASE):
                    is_valid = False
                    break
            
            # Additional validation - must have meaningful content and be reasonable length
            if (is_valid and 
                len(skill_clean) > 3 and 
                len(skill_clean) < 50 and 
                skill_clean not in filtered_skills and
                not any(word in skill_clean.lower() for word in ['experience', 'years', 'degree', 'minimum', 'preferred', 'bachelor', 'master'])):
                filtered_skills.append(skill_clean)
        
        # CRITICAL: Deduplicate and consolidate similar skills
        consolidated_skills = self._consolidate_similar_skills(filtered_skills)
        
        return consolidated_skills
    
    def _is_skill_matched(self, job_skill: str, matched_skills: set) -> bool:
        """Check if a job skill matches any candidate skill"""
        job_skill_normalized = self.normalize_skill_name(job_skill)
        
        # Define skill equivalence mappings
        skill_equivalences = {
            'aws lake formation': ['aws', 'lake formation', 'data lake', 'data warehousing'],
            'amazon kinesis': ['aws', 'kinesis', 'streaming', 'data streaming'],
            'budget management': ['financial management', 'budget', 'financial', 'management', 'leadership'],
            'financial management': ['budget management', 'financial', 'budget', 'management', 'leadership'],
            'product strategy': ['strategy', 'strategic', 'product', 'business strategy', 'planning'],
            'data engineering': ['data warehousing', 'etl', 'data pipeline', 'data processing'],
            'cloud platforms': ['aws', 'azure', 'gcp', 'cloud'],
        }
        
        for candidate_skill in matched_skills:
            candidate_skill_normalized = self.normalize_skill_name(candidate_skill)
            
            # Direct match
            if (job_skill_normalized == candidate_skill_normalized or 
                job_skill_normalized in candidate_skill_normalized or
                candidate_skill_normalized in job_skill_normalized):
                return True
            
            # Check for skill equivalences
            if job_skill_normalized in skill_equivalences:
                for equivalent in skill_equivalences[job_skill_normalized]:
                    if equivalent in candidate_skill_normalized:
                        return True
            
            # Check reverse equivalences
            for skill_key, equivalents in skill_equivalences.items():
                if job_skill_normalized in equivalents and skill_key in candidate_skill_normalized:
                    return True
                    
        return False
    
    def _is_partial_match(self, skill: str, job_desc: str) -> bool:
        """Check for partial matches using fuzzy logic"""
        # Split skill into words
        skill_words = skill.split()
        
        # If skill is a single word, check if it appears in job description
        if len(skill_words) == 1:
            return skill in job_desc
        
        # For multi-word skills, check if most words appear
        matches = sum(1 for word in skill_words if word in job_desc)
        return matches >= len(skill_words) * 0.6  # 60% of words must match
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract specific requirements from job description"""
        requirements = {
            'technical_skills': [],
            'soft_skills': [],
            'tools_technologies': [],
            'experience_requirements': [],
            'education_certifications': []
        }
        
        job_desc_lower = job_description.lower()
        
        # Check against known job skills patterns
        for category, skills in self.job_skills.items():
            for skill in skills:
                skill_normalized = self.normalize_skill_name(skill)
                if skill_normalized in job_desc_lower or self._is_partial_match(skill_normalized, job_desc_lower):
                    requirements[category].append(skill)
        
        return requirements
    
    def generate_preliminary_analysis(self, job_description: str) -> Dict[str, any]:
        """Generate preliminary analysis to reduce AI load"""
        
        # Find matches
        matches = self.find_skill_matches(job_description)
        
        # Extract requirements
        requirements = self.extract_job_requirements(job_description)
        
        # Generate summary
        analysis = {
            'preliminary_match_score': matches['match_score'],
            'exact_matches': matches['exact_matches'],
            'partial_matches': matches['partial_matches'],
            'missing_skills': matches['missing_skills'],
            'job_requirements': requirements,
            'match_summary': {
                'total_candidate_skills': matches['total_required'],
                'matched_skills': matches['matched_count'],
                'missing_skills_count': matches['missing_count'],
                'match_percentage': matches['match_score']
            },
            'ai_focus_areas': self._identify_ai_focus_areas(matches, requirements)
        }
        
        return analysis
    
    def _identify_ai_focus_areas(self, matches: Dict, requirements: Dict) -> List[str]:
        """Identify areas where AI should focus its analysis"""
        focus_areas = []
        
        # If match score is low, focus on missing skills
        if matches['match_score'] < 50:
            focus_areas.append("Low match score - focus on skill gaps and alternatives")
        
        # If there are many partial matches, focus on context
        if len(matches['partial_matches']) > len(matches['exact_matches']):
            focus_areas.append("Many partial matches - focus on context and relevance")
        
        # If specific categories are missing, focus on those
        missing_categories = set()
        for match in matches['exact_matches']:
            missing_categories.add(match['category'])
        
        if 'Programming Languages' not in missing_categories:
            focus_areas.append("Programming language requirements")
        
        if 'Cloud Platforms' not in missing_categories:
            focus_areas.append("Cloud platform requirements")
        
        return focus_areas
    
    def create_ai_prompt_context(self, job_description: str) -> str:
        """Create context for AI analysis based on preliminary matching"""
        
        analysis = self.generate_preliminary_analysis(job_description)
        
        context = f"""
PRELIMINARY MATCHING ANALYSIS:
- Match Score: {analysis['preliminary_match_score']}%
- Exact Matches: {len(analysis['exact_matches'])}
- Partial Matches: {len(analysis['partial_matches'])}
- Missing Skills: {analysis['match_summary']['missing_skills_count']}
- Unmatched Job Skills: {len(analysis.get('unmatched_job_skills', []))}

EXACT MATCHES FOUND:
{self._format_matches(analysis['exact_matches'])}

PARTIAL MATCHES FOUND:
{self._format_matches(analysis['partial_matches'])}

UNMATCHED JOB SKILLS (Skills from job description not found in candidate resume):
{self._format_unmatched_skills(analysis.get('unmatched_job_skills', []))}

AI FOCUS AREAS:
{chr(10).join(f"- {area}" for area in analysis['ai_focus_areas'])}

Please focus your analysis on the areas above and provide detailed insights on:
1. How well the candidate's experience aligns with the job requirements
2. Specific examples of relevant experience from the resume
3. Analysis of unmatched job skills and whether candidate has equivalent experience
4. Recommendations for addressing any skill gaps
5. Overall fit assessment based on the preliminary matching results
"""
        
        return context
    
    def _format_matches(self, matches: List[Dict]) -> str:
        """Format matches for display"""
        if not matches:
            return "None"
        
        formatted = []
        for match in matches:
            formatted.append(f"- {match['skill']} ({match['category']})")
        
        return "\n".join(formatted)
    
    def _format_unmatched_skills(self, unmatched_skills: List[str]) -> str:
        """Format unmatched skills for display"""
        if not unmatched_skills:
            return "None"
        
        formatted = []
        for skill in unmatched_skills:
            formatted.append(f"- {skill}")
        
        return "\n".join(formatted)
    
    def _consolidate_similar_skills(self, skills: list) -> list:
        """Consolidate similar skills to avoid duplicates and inflated counts"""
        consolidated = []
        skill_groups = {
            # BI Tools consolidation
            'tableau': ['tableau', 'bi tools', 'bi tool expertise', 'bi platforms'],
            'power bi': ['power bi', 'powerbi'],
            'looker': ['looker'],
            'sql': ['sql'],
            
            # Cloud platforms
            'aws': ['aws', 'amazon web services'],
            'azure': ['azure', 'microsoft azure'],
            'gcp': ['gcp', 'google cloud', 'google cloud platform'],
            'cloud': ['cloud', 'cloud platforms', 'cloud-based', 'cloud data platforms'],
            
            # Data engineering
            'spark': ['spark', 'apache spark'],
            'hadoop': ['hadoop', 'apache hadoop'],
            'airflow': ['airflow', 'data orchestration', 'orchestration'],
            'etl': ['etl', 'extract transform load'],
            'data warehousing': ['data warehousing', 'data warehouse'],
            
            # Analytics and BI
            'business intelligence': ['business intelligence', 'bi', 'bi platforms'],
            'data analytics': ['data analytics', 'analytics'],
            'data science': ['data science'],
            'machine learning': ['machine learning', 'ml'],
            
            # Leadership and management
            'leadership': ['leadership', 'team leadership'],
            'management': ['management', 'team management', 'project management'],
            'strategy': ['strategy', 'strategic', 'strategic planning'],
            
            # Programming
            'python': ['python'],
        }
        
        # Track which skills have been consolidated
        used_skills = set()
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Skip if already used
            if skill_lower in used_skills:
                continue
                
            # Check if this skill belongs to a group
            found_group = False
            for group_name, group_members in skill_groups.items():
                for member in group_members:
                    if member in skill_lower or skill_lower in member:
                        # Use the canonical name
                        if group_name not in [s.lower() for s in consolidated]:
                            consolidated.append(group_name)
                        used_skills.add(skill_lower)
                        used_skills.add(member)
                        found_group = True
                        break
                if found_group:
                    break
            
            # If not in any group and not already used, add as-is
            if not found_group and skill_lower not in used_skills:
                consolidated.append(skill_lower)
                used_skills.add(skill_lower)
        
        return consolidated
    
    def _find_matched_job_skill(self, candidate_skill: str, candidate_skill_normalized: str, job_skills: list) -> str:
        """Find which job skill matches a candidate skill"""
        # First try to find exact matches by checking if the candidate skill matches any job skill
        for job_skill in job_skills:
            job_skill_normalized = self.normalize_skill_name(job_skill)
            
            # Check for exact matches
            if candidate_skill_normalized == job_skill_normalized:
                return job_skill
            
            # Check for substring matches (exact match logic)
            if (candidate_skill_normalized in job_skill_normalized or 
                job_skill_normalized in candidate_skill_normalized):
                return job_skill
        
        # If no exact match, try to find the best partial match using word overlap
        best_match = None
        best_score = 0
        
        for job_skill in job_skills:
            job_skill_normalized = self.normalize_skill_name(job_skill)
            
            # Calculate word overlap score
            candidate_words = set(candidate_skill_normalized.split())
            job_words = set(job_skill_normalized.split())
            
            if candidate_words and job_words:
                overlap = len(candidate_words & job_words)
                total_words = len(candidate_words | job_words)
                score = overlap / total_words if total_words > 0 else 0
                
                if score > best_score and score > 0.3:  # At least 30% overlap
                    best_score = score
                    best_match = job_skill
        
        return best_match if best_match else candidate_skill

if __name__ == "__main__":
    matcher = PreliminaryMatcher()
    
    # Test with a sample job description
    sample_job = """
    We are looking for a Senior Data Engineer with experience in:
    - Python and SQL
    - AWS cloud platforms
    - Data warehousing and ETL processes
    - Team leadership and project management
    - Business intelligence tools like Tableau
    """
    
    analysis = matcher.generate_preliminary_analysis(sample_job)
    print("Preliminary Analysis Results:")
    print(f"Match Score: {analysis['preliminary_match_score']}%")
    print(f"Exact Matches: {len(analysis['exact_matches'])}")
    print(f"Partial Matches: {len(analysis['partial_matches'])}")
    print(f"AI Focus Areas: {analysis['ai_focus_areas']}")
