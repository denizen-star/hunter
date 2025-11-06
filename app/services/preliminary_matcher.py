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
        # Performance optimization: Cache normalized candidate skills
        self._normalized_candidate_skills_cache = {}
        self._normalized_candidate_skills_set = set()
        self.load_skills_data()
        self._build_normalization_cache()
    
    def load_skills_data(self):
        """Load both skills files"""
        # Load candidate skills
        with open(self.skills_yaml_path, 'r') as f:
            skills_data = yaml.safe_load(f)
            self.candidate_skills = skills_data.get('skills', {})
        
        # Load job skills from markdown
        job_skills_content = read_text_file(self.job_skills_path)
        self.job_skills = self._parse_job_skills_markdown(job_skills_content)
    
    def _build_normalization_cache(self):
        """Initialize empty cache - normalize lazily as needed"""
        self._normalized_candidate_skills_cache = {}
        self._normalized_candidate_skills_set = set()
    
    def _get_normalized_skill(self, skill_name: str) -> str:
        """Get normalized skill from cache, or normalize and cache if not present"""
        if skill_name in self._normalized_candidate_skills_cache:
            return self._normalized_candidate_skills_cache[skill_name]
        
        # Normalize and cache
        normalized = self.normalize_skill_name(skill_name)
        if normalized:
            self._normalized_candidate_skills_cache[skill_name] = normalized
            self._normalized_candidate_skills_set.add(normalized)
        return normalized or ""
    
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
                if not variation:
                    continue
                
                # Use word boundary matching to avoid false positives (e.g., "ase" matching "base")
                # For single-character skills, use special validation
                if len(variation) == 1:
                    # Single-character skills need special handling (e.g., "R" should not match "R&D")
                    if self._is_valid_single_char_match(variation, job_description):
                        exact_match = True
                        matched_skills.add(skill_name)
                        break
                else:
                    # Multi-character skills: use word boundary matching
                    pattern = r'\b' + re.escape(variation) + r'\b'
                    if re.search(pattern, job_desc_lower):
                        exact_match = True
                        matched_skills.add(skill_name)
                        break
                    elif self._is_partial_match(variation, job_desc_lower):
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
        # Use two-phase matching: fast check against matched_skills first, then fallback to all candidate skills
        matched_job_skills = 0
        unmatched_job_skills_list = []
        all_candidate_skill_names = set(self.candidate_skills.keys())
        
        for job_skill in job_skills_found:
            # Phase 1: Quick check against skills already found in job description
            if self._is_skill_matched(job_skill, matched_skills):
                matched_job_skills += 1
            # Phase 2: If not found, check against ALL candidate skills (for cases like "strategy" -> "Business Strategy")
            elif self._is_skill_matched(job_skill, all_candidate_skill_names):
                matched_job_skills += 1
            else:
                unmatched_job_skills_list.append(job_skill)
        
        # Store unmatched job skills
        matches['unmatched_job_skills'] = unmatched_job_skills_list
        
        # Calculate match score based on job requirements, not candidate skills
        total_job_skills = len(job_skills_found)
        exact_count = len(matches['exact_matches'])
        partial_count = len(matches['partial_matches'])
        
        matches['total_required'] = total_job_skills if total_job_skills > 0 else len(self.candidate_skills)
        matches['matched_count'] = matched_job_skills  # Use actual matched job skills count
        matches['missing_count'] = matches['total_required'] - matched_job_skills
        
        # Calculate match score based on job requirements with overqualification bonus
        # IMPORTANT: Extra candidate skills should NEVER count against the score
        # Being overqualified is a positive, not a negative
        if total_job_skills > 0:
            base_score = (matched_job_skills / total_job_skills) * 100
            
            # Check for CRITICAL missing requirements (education, domain expertise)
            # These should severely penalize the score regardless of other matches
            critical_requirements = []
            education_keywords = ['phd', 'doctorate', 'master', 'bachelor', 'degree', 'abd']
            domain_keywords = ['biology', 'chemistry', 'physics', 'mathematics', 'genetics', 'biochemistry', 'immunology', 'bioinformatics']
            
            for unmatched_skill in matches['unmatched_job_skills']:
                skill_lower = unmatched_skill.lower()
                is_education = any(edu in skill_lower for edu in education_keywords)
                is_domain = any(domain in skill_lower for domain in domain_keywords)
                if is_education or is_domain:
                    critical_requirements.append(unmatched_skill)
            
            # If critical requirements are missing, apply severe penalty
            if critical_requirements:
                # Each critical requirement is worth 30-50% penalty
                # Missing PhD alone should drop score significantly
                critical_penalty = min(70, len(critical_requirements) * 30)  # Cap at 70% penalty
                base_score = max(0, base_score - critical_penalty)
            
            # Check if candidate is overqualified (has significantly more skills than required)
            critical_skills_missing = len(matches['unmatched_job_skills'])
            total_candidate_skills = len(self.candidate_skills)
            overqualification_ratio = total_candidate_skills / total_job_skills if total_job_skills > 0 else 1
            
            # If overqualified (2x+ more skills), treat missing skills more leniently
            # BUT: Don't apply overqualification bonus if critical requirements are missing
            is_overqualified = overqualification_ratio >= 2.0 and not critical_requirements
            
            if is_overqualified:
                # Overqualified candidates get more generous treatment
                # Missing skills are less impactful when you have many more skills than required
                
                # Calculate missing skill penalty (reduced for overqualified candidates)
                if critical_skills_missing > 0:
                    # Distinguish between critical and nice-to-have skills
                    critical_penalty_skills = ['snowflake', 'bigquery', 'cloud', 'data engineering']
                    nice_to_have_skills = ['paid advertising', 'google ads', 'meta', 'advertising platforms', 'mentorship skills', 'problem-solving']
                    
                    critical_missing = sum(1 for skill in matches['unmatched_job_skills'] 
                                         if any(critical in skill.lower() for critical in critical_penalty_skills))
                    nice_to_have_missing = sum(1 for skill in matches['unmatched_job_skills'] 
                                             if any(nice in skill.lower() for nice in nice_to_have_skills))
                    
                    # Reduced penalties for overqualified candidates (50% reduction)
                    # Overqualification means you have many alternative skills that can compensate
                    penalty = (critical_missing * 1.5) + (nice_to_have_missing * 0.5)
                    penalty = min(10, penalty)  # Cap penalty at 10% for overqualified (vs 20% for others)
                    base_score = max(0, base_score - penalty)
                
                # Apply overqualification bonus if base score is decent (lowered threshold)
                # Overqualified candidates should be rewarded, not penalized
                if base_score >= 50:  # Lowered from 70% - being overqualified is valuable
                    if overqualification_ratio >= 4.0:  # 4x+ overqualified
                        overqualification_bonus = 15
                    elif overqualification_ratio >= 3.0:  # 3x+ overqualified
                        overqualification_bonus = 10
                    else:  # 2x+ overqualified
                        overqualification_bonus = 5
                    
                    base_score = min(100, base_score + overqualification_bonus)
            else:
                # Not overqualified - apply standard penalties for missing skills
                if critical_skills_missing > 0:
                    critical_penalty_skills = ['snowflake', 'bigquery', 'cloud', 'data engineering']
                    nice_to_have_skills = ['paid advertising', 'google ads', 'meta', 'advertising platforms', 'mentorship skills', 'problem-solving']
                    
                    critical_missing = sum(1 for skill in matches['unmatched_job_skills'] 
                                         if any(critical in skill.lower() for critical in critical_penalty_skills))
                    nice_to_have_missing = sum(1 for skill in matches['unmatched_job_skills'] 
                                             if any(nice in skill.lower() for nice in nice_to_have_skills))
                    
                    # Standard penalties for non-overqualified candidates
                    penalty = (critical_missing * 3) + (nice_to_have_missing * 1)
                    penalty = min(20, penalty)  # Cap penalty at 20%
                    base_score = max(0, base_score - penalty)
            
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
        
        # Check against known job skills patterns (use word boundaries to avoid false positives)
        # Only extract skills that are ACTUALLY mentioned in the job description
        for category, skills in self.job_skills.items():
            for skill in skills:
                skill_normalized = self.normalize_skill_name(skill)
                if skill_normalized:
                    # Extract the core skill name (remove parentheticals, qualifiers, etc.)
                    # e.g., "Cloud platform requirements" -> "cloud platform"
                    core_skill = skill_normalized
                    
                    # Remove parentheticals and qualifiers that might not be in JD
                    # e.g., "AWS (Amazon Web Services) experience (preferred)" -> "aws"
                    core_skill = re.sub(r'\s*\([^)]*\)', '', core_skill)  # Remove (parentheticals)
                    core_skill = re.sub(r'\s*experience.*$', '', core_skill, flags=re.IGNORECASE)  # Remove "experience" suffix
                    core_skill = re.sub(r'\s*\(preferred\)$', '', core_skill, flags=re.IGNORECASE)  # Remove "(preferred)"
                    core_skill = re.sub(r'\s*\(required\)$', '', core_skill, flags=re.IGNORECASE)  # Remove "(required)"
                    core_skill = re.sub(r'\s*requirements?$', '', core_skill, flags=re.IGNORECASE)  # Remove "requirements"
                    core_skill = core_skill.strip()
                    
                    # Only add if the CORE skill (or close variant) appears in JD with word boundaries
                    # This prevents "Cloud platform requirements" from matching if only "cloud" appears
                    if len(core_skill) > 2:  # Must have meaningful content
                        # Use word boundary matching for the core skill
                        pattern = r'\b' + re.escape(core_skill) + r'\b'
                        if re.search(pattern, job_desc_lower):
                            # Only add the skill if it's not already in the list
                            if skill not in job_skills:
                                job_skills.append(skill)
        
        # Extract education requirements (CRITICAL - these are often required)
        # Check both uppercase and lowercase versions
        education_patterns = [
            (r'\bph\.?d\.?\b', 'PhD'),
            (r'\bphd\b', 'PhD'),  # Also check lowercase
            (r'\bdoctorate\b', 'Doctorate'),
            (r'\bmaster\s+of\s+science\b', 'Master of Science'),
            (r'\bmaster\s+of\s+arts\b', 'Master of Arts'),
            (r'\bmaster\'?s?\s+degree\b', "Master's Degree"),
            (r'\bbachelor\s+of\s+science\b', 'Bachelor of Science'),
            (r'\bbachelor\s+of\s+arts\b', 'Bachelor of Arts'),
            (r'\bbachelor\'?s?\s+degree\b', "Bachelor's Degree"),
            (r'\babd\b', 'ABD (All But Dissertation)'),
        ]
        for pattern, skill_name in education_patterns:
            if re.search(pattern, job_description, re.IGNORECASE) and skill_name not in job_skills:
                job_skills.append(skill_name)
        
        # Extract domain expertise (biology, chemistry, physics, etc.)
        domain_patterns = [
            (r'\bmolecular\s+biology\b', 'Molecular Biology'),
            (r'\bgenetics\b', 'Genetics'),
            (r'\bbiochemistry\b', 'Biochemistry'),
            (r'\bimmunology\b', 'Immunology'),
            (r'\bcell\s+biology\b', 'Cell Biology'),
            (r'\bbioinformatics\b', 'Bioinformatics'),
            (r'\bbiochemistry\b', 'Biochemistry'),
            (r'\bbiotechnology\b', 'Biotechnology'),
            (r'\bbiology\b', 'Biology'),  # Check last to avoid false positives
            (r'\bchemistry\b', 'Chemistry'),
            (r'\bphysics\b', 'Physics'),
            (r'\bmathematics\b', 'Mathematics'),
            (r'\bstatistics\b', 'Statistics'),
            (r'\bcomputer\s+science\b', 'Computer Science'),
            (r'\bdata\s+science\b', 'Data Science'),
            (r'\bmachine\s+learning\b', 'Machine Learning'),
        ]
        for pattern, skill_name in domain_patterns:
            if re.search(pattern, job_desc_lower, re.IGNORECASE) and skill_name not in job_skills:
                job_skills.append(skill_name)
        
        # Extract research-related skills
        research_patterns = [
            (r'\bscientific\s+research\b', 'Scientific Research'),
            (r'\bresearch\s+experience\b', 'Research Experience'),
            (r'\bresearch\s+methodology\b', 'Research Methodology'),
            (r'\bexperimental\s+design\b', 'Experimental Design'),
            (r'\bexperimental\s+protocols\b', 'Experimental Protocols'),
            (r'\bresearch\b', 'Research'),  # Check last
        ]
        for pattern, skill_name in research_patterns:
            if re.search(pattern, job_desc_lower, re.IGNORECASE) and skill_name not in job_skills:
                job_skills.append(skill_name)
        
        # Also extract specific skills mentioned in the job description
        specific_skills = [
            "python", "sql", "tableau", "power bi", "looker", "excel", "sheets",
            "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "terraform",
            "snowflake", "bigquery", "spark", "hadoop", "kafka", "airflow",
            "machine learning", "ai", "data science", "data engineering",
            "business intelligence", "analytics", "etl", "data warehousing",
            "leadership", "management", "team", "mentoring", "coaching",
            "strategy", "strategic", "business intelligence", "analytics", "forecasting",
            "pricing", "modeling", "financial", "budget", "planning",
            # Add more specific data engineering tools
            "postgresql", "mysql", "oracle", "mongodb", "redis",
            "aws lake formation", "amazon kinesis", "amazon q",
            "paid advertising", "google ads", "meta", "amazon ads", "advertising platforms"
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
            r'^none specified',  # "None specified" placeholder
        ]
        
        for skill in job_skills:
            skill_clean = skill.strip()
            is_valid = True
            
            for pattern in invalid_patterns:
                if re.match(pattern, skill_clean, re.IGNORECASE):
                    is_valid = False
                    break
            
            # Additional validation - must have meaningful content and be reasonable length
            # AND verify the skill (or core part) actually appears in the job description
            # BUT: Don't filter out education/domain skills that we explicitly extracted
            is_education_skill = any(edu in skill_clean.lower() for edu in ['phd', 'doctorate', 'master', 'bachelor', 'abd'])
            is_domain_skill = any(domain in skill_clean.lower() for domain in ['biology', 'chemistry', 'physics', 'genetics', 'biochemistry', 'immunology', 'bioinformatics'])
            is_research_skill = any(research in skill_clean.lower() for research in ['research', 'experimental'])
            
            # Allow shorter skills if they're education/domain/research (PhD is 3 chars, so >= 3)
            min_length = 2 if (is_education_skill or is_domain_skill or is_research_skill) else 3
            
            if (is_valid and 
                len(skill_clean) >= min_length and 
                len(skill_clean) < 50 and 
                skill_clean not in filtered_skills and
                (is_education_skill or is_domain_skill or is_research_skill or 
                 not any(word in skill_clean.lower() for word in ['experience', 'years', 'minimum', 'preferred']))):
                
                # Final validation: Verify the skill actually appears in JD (not just similar words)
                # Extract core skill name (remove parentheticals, qualifiers)
                core_skill_for_validation = skill_clean.lower()
                core_skill_for_validation = re.sub(r'\s*\([^)]*\)', '', core_skill_for_validation)  # Remove parentheticals
                core_skill_for_validation = re.sub(r'\s*requirements?$', '', core_skill_for_validation, flags=re.IGNORECASE)
                core_skill_for_validation = core_skill_for_validation.strip()
                
                # Check if core skill appears in JD with word boundaries (more strict)
                if len(core_skill_for_validation) >= 3:
                    # For multi-word skills, require all words to appear
                    words = core_skill_for_validation.split()
                    if len(words) > 1:
                        # All words must appear (but not necessarily consecutively)
                        all_words_present = all(re.search(r'\b' + re.escape(word) + r'\b', job_desc_lower) for word in words if len(word) > 2)
                        if all_words_present:
                            filtered_skills.append(skill_clean)
                    else:
                        # Single word - check with word boundary
                        if re.search(r'\b' + re.escape(core_skill_for_validation) + r'\b', job_desc_lower):
                            filtered_skills.append(skill_clean)
        
        # CRITICAL: Deduplicate and consolidate similar skills
        consolidated_skills = self._consolidate_similar_skills(filtered_skills)
        
        return consolidated_skills
    
    def _is_skill_matched(self, job_skill: str, matched_skills: set) -> bool:
        """Check if a job skill matches any candidate skill (optimized with cache)"""
        if not job_skill or not job_skill.strip():
            return False
            
        job_skill_normalized = self.normalize_skill_name(job_skill)
        
        # If normalization returns empty/None, use lowercase original as fallback                                                                               
        if not job_skill_normalized:
            job_skill_normalized = job_skill.lower().strip()
        
        # Normalize hyphens and handle plurals for better matching
        job_skill_normalized = job_skill_normalized.replace('-', ' ').replace('_', ' ')
        job_skill_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_skill_normalized).strip()
        
        # Define skill equivalence mappings
        skill_equivalences = {
            'aws lake formation': ['aws', 'lake formation', 'data lake', 'data warehousing'],                                                                   
            'amazon kinesis': ['aws', 'kinesis', 'streaming', 'data streaming'],
            'amazon q': ['aws', 'ai', 'artificial intelligence', 'machine learning'],                                                                           
            'budget management': ['financial management', 'budget', 'financial', 'management', 'leadership'],                                                   
            'financial management': ['budget management', 'financial', 'budget', 'management', 'leadership'],                                                   
            'product strategy': ['strategy', 'strategic', 'product', 'business strategy', 'data strategy', 'planning'],                                                                                                                              
            'strategy': ['strategic', 'business strategy', 'data strategy', 'product strategy', 'planning'],                                                    
            'data strategy': ['strategy', 'strategic', 'product strategy', 'business strategy', 'planning'],
            'insights': ['insight', 'analytics', 'data insights', 'business insights'],                                                                         
            'data analytics': ['analytics', 'data analytics', 'product analytics', 'business analytics'],
            'analytics': ['data analytics', 'product analytics', 'business analytics', 'insights'],
            'data engineering': ['data warehousing', 'etl', 'data pipeline', 'data processing', 'pipelines', 'data pipelines', 'data engineering pipelines'],
            'pipelines': ['data engineering', 'data pipelines', 'data pipeline', 'etl', 'data processing'],
            'data pipelines': ['data engineering', 'pipelines', 'data pipeline', 'etl'],
            'modeling': ['data modeling', 'data models', 'modeling techniques', 'data model'],
            'data modeling': ['modeling', 'data models', 'modeling techniques', 'data model'],
            'communication': ['communication skills', 'excellent communication', 'strong communication', 'excellent communication skills', 'strong communication skills'],
            'communication skills': ['communication', 'excellent communication', 'strong communication'],
            'excellent communication skills': ['communication', 'communication skills', 'strong communication skills'],
            'strong communication skills': ['communication', 'communication skills', 'excellent communication skills'],
            'cloud platforms': ['aws', 'azure', 'gcp', 'cloud'],
            'snowflake': ['data warehousing', 'cloud data warehouse', 'analytics platform'],                                                                    
            'bigquery': ['data warehousing', 'cloud data warehouse', 'analytics platform'],                                                                     
            'paid advertising': ['advertising', 'digital marketing', 'google ads', 'meta', 'amazon ads'],                                                       
            'advertising platforms': ['paid advertising', 'digital marketing', 'google ads', 'meta', 'amazon ads'],
            'problem solving': ['problem-solving', 'problem-solving skills', 'problem solving skills'],
            'problem-solving': ['problem solving', 'problem-solving skills', 'problem solving skills'],
            'problem-solving skills': ['problem solving', 'problem-solving'],
        }
        
        # Performance optimization: Use lazy cache - normalize only when needed
        for candidate_skill in matched_skills:
            # Get normalized skill from cache (normalizes on first access, then caches)
            candidate_skill_normalized = self._get_normalized_skill(candidate_skill)
            
            if not candidate_skill_normalized:
                # Fallback: use candidate skill as-is
                candidate_skill_normalized = candidate_skill.lower().strip()
            
            # Normalize hyphens and handle plurals for candidate skill too
            candidate_skill_normalized = candidate_skill_normalized.replace('-', ' ').replace('_', ' ')
            candidate_skill_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', candidate_skill_normalized).strip()
            
            # Direct match (fast check)
            if (job_skill_normalized == candidate_skill_normalized or 
                job_skill_normalized in candidate_skill_normalized or
                candidate_skill_normalized in job_skill_normalized):
                return True
            
            # Check for skill equivalences (only if direct match failed)
            if job_skill_normalized in skill_equivalences:
                for equivalent in skill_equivalences[job_skill_normalized]:
                    if equivalent in candidate_skill_normalized:
                        return True
            
            # Check reverse equivalences (only if direct match failed)
            for skill_key, equivalents in skill_equivalences.items():
                if job_skill_normalized in equivalents and skill_key in candidate_skill_normalized:                                                             
                    return True
                    
        return False
    
    def _is_partial_match(self, skill: str, job_desc: str) -> bool:
        """Check for partial matches using fuzzy logic with word boundaries"""
        # Split skill into words
        skill_words = skill.split()
        job_desc_lower = job_desc.lower()
        
        # If skill is a single word, use word boundary matching to avoid false positives
        if len(skill_words) == 1:
            # Use word boundary to avoid matching substrings (e.g., "ase" in "base")
            if len(skill) <= 2:
                # For very short skills (1-2 chars), require exact word boundary match
                pattern = r'\b' + re.escape(skill) + r'\b'
                return bool(re.search(pattern, job_desc_lower))
            else:
                # For longer skills, allow word boundary match
                pattern = r'\b' + re.escape(skill) + r'\b'
                return bool(re.search(pattern, job_desc_lower))
        
        # For multi-word skills, check if most words appear with word boundaries
        matches = 0
        for word in skill_words:
            if len(word) > 2:  # Only check meaningful words (3+ chars)
                pattern = r'\b' + re.escape(word) + r'\b'
                if re.search(pattern, job_desc_lower):
                    matches += 1
        meaningful_words = [w for w in skill_words if len(w) > 2]
        if not meaningful_words:
            return False
        return matches >= len(meaningful_words) * 0.6  # 60% of meaningful words must match
    
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
            'unmatched_job_skills': matches['unmatched_job_skills'],  # Include unmatched job skills
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
            'data analytics': ['data analytics', 'analytics', 'product analytics'],
            'data science': ['data science'],
            'machine learning': ['machine learning', 'ml'],
            
            # Data Engineering
            'data engineering': ['data engineering', 'data engineering pipelines', 'data pipeline engineering'],
            'pipelines': ['pipelines', 'data pipelines', 'data pipeline', 'pipeline'],
            'data pipelines': ['data pipelines', 'pipelines', 'data pipeline'],
            
            # Modeling
            'modeling': ['modeling', 'data modeling', 'data models', 'modeling techniques'],
            'data modeling': ['data modeling', 'modeling', 'data models'],
            
            # Communication
            'communication': ['communication', 'communication skills', 'excellent communication', 'strong communication', 'excellent communication skills', 'strong communication skills'],
            'communication skills': ['communication skills', 'communication', 'excellent communication skills', 'strong communication skills'],
            
            # Leadership and management
            'leadership': ['leadership', 'team leadership'],
            'management': ['management', 'team management', 'project management'],
            'strategy': ['strategy', 'strategic', 'strategic planning', 'product strategy', 'data strategy', 'business strategy'],
            'problem solving': ['problem solving', 'problem-solving', 'problem-solving skills', 'problem solving skills'],
            
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
            # First normalize: remove hyphens, handle plurals, etc.
            skill_normalized = skill_lower.replace('-', ' ').replace('_', ' ')
            # Remove common suffixes like "skills", "experience", etc.
            skill_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', skill_normalized).strip()
            
            found_group = False
            for group_name, group_members in skill_groups.items():
                group_normalized = group_name.replace('-', ' ').replace('_', ' ')
                # Check against normalized skill
                for member in group_members:
                    member_normalized = member.replace('-', ' ').replace('_', ' ')
                    member_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', member_normalized).strip()
                    
                    # Check if normalized versions match
                    if (member_normalized in skill_normalized or 
                        skill_normalized in member_normalized or
                        member_normalized == skill_normalized):
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
