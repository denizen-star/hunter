#!/usr/bin/env python3
"""
Preliminary Skills Matcher - Reduces AI load by doing initial matching
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from app.utils.file_utils import read_text_file
from app.utils.skill_normalizer import SkillNormalizer
from app.utils.simple_tech_extractor import SimpleTechExtractor

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
        # Initialize advanced skill normalizer
        self.skill_normalizer = SkillNormalizer()
        # Initialize technology extractor (comprehensive 157+ technologies)
        self.tech_extractor = SimpleTechExtractor()
        # Load skill equivalency mappings
        self.skill_equivalencies = self._load_skill_equivalencies()
        self.load_skills_data()
        self._build_normalization_cache()
    
    def load_skills_data(self):
        """Load both skills files"""
        # Load candidate skills
        with open(self.skills_yaml_path, 'r') as f:
            skills_data = yaml.safe_load(f)
            self.candidate_skills = skills_data.get('skills', {})
        
        # Load job skills from markdown (optional file)
        if self.job_skills_path.exists():
            job_skills_content = read_text_file(self.job_skills_path)
            self.job_skills = self._parse_job_skills_markdown(job_skills_content)
        else:
            # If file doesn't exist, use empty dict (job skills are optional)
            print(f"⚠️ Warning: Job skills file not found: {self.job_skills_path}")
            print(f"   Continuing without job skills database. The file is optional.")
            self.job_skills = {}
    
    def _build_normalization_cache(self):
        """Initialize empty cache - normalize lazily as needed"""
        self._normalized_candidate_skills_cache = {}
        self._normalized_candidate_skills_set = set()
    
    def _load_skill_equivalencies(self) -> Dict[str, List[str]]:
        """Load skill equivalency mappings from YAML file"""
        equivalencies_path = Path(__file__).parent.parent.parent / "data" / "config" / "skill_equivalencies.yaml"
        if equivalencies_path.exists():
            try:
                with open(equivalencies_path, 'r') as f:
                    data = yaml.safe_load(f)
                    return data.get('equivalencies', {})
            except Exception as e:
                print(f"⚠️  Warning: Could not load skill equivalencies: {e}")
                return {}
        return {}
    
    def _get_normalized_skill(self, skill_name: str) -> str:
        """Get normalized skill from cache, or normalize and cache if not present"""
        if skill_name in self._normalized_candidate_skills_cache:
            return self._normalized_candidate_skills_cache[skill_name]
        
        # Normalize using advanced SkillNormalizer
        normalized_result = self.skill_normalizer.normalize(skill_name, fuzzy=True)
        normalized = normalized_result.lower() if normalized_result else ""
        if normalized:
            self._normalized_candidate_skills_cache[skill_name] = normalized
            self._normalized_candidate_skills_set.add(normalized)
        return normalized
    
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
        """
        Normalize skill names for better matching (DEPRECATED - uses SkillNormalizer internally).
        This method is kept for backward compatibility but now uses the advanced SkillNormalizer.
        
        Args:
            skill: Skill name to normalize
            
        Returns:
            Normalized skill name (lowercase) or empty string if not found
        """
        # Use advanced SkillNormalizer
        normalized_result = self.skill_normalizer.normalize(skill, fuzzy=True)
        if normalized_result:
            return normalized_result.lower()
        return ""
    
    def find_skill_matches(self, job_description: str) -> Dict[str, any]:
        """Find matches between job description and candidate skills"""
        
        # Normalize job description
        job_desc_lower = job_description.lower()
        
        # Check if Job Engine V2 is enabled and get V2 data
        v2_config = self._load_job_engine_v2_config()
        frequent_skills = {}
        critical_requirements = {}
        
        if v2_config.get('enabled', False):
            if v2_config.get('phases', {}).get('phase_1_frequency_analysis', {}).get('enabled', False):
                frequent_skills = self._extract_frequent_skills(job_description)
            if v2_config.get('phases', {}).get('phase_1_critical_requirements', {}).get('enabled', False):
                critical_requirements = self._identify_critical_requirements(job_description)
        
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
            'match_details': {},
            'frequent_skills': frequent_skills,  # V2: Frequency data
            'critical_requirements': critical_requirements  # V2: Critical requirements
        }
        
        # Extract job skills first
        job_skills_found = self._extract_job_skills_from_description(job_description)
        
        # Check each candidate skill against job description
        matched_skills = set()
        for skill_name, skill_data in self.candidate_skills.items():
            # Get normalized form for later validation (but don't use it for primary search)
            skill_normalized = self._get_normalized_skill(skill_name)
            
            # Skip invalid or empty skills
            if not skill_normalized:
                continue
            
            # CRITICAL: Search using ORIGINAL skill name + variations, NOT normalized form
            # This prevents "power-bi" from searching for "business intelligence" in the job description
            skill_variations = [skill_name.lower()] + skill_data.get('variations_found', [])
            
            # Check for exact matches
            exact_match = False
            partial_match = False
            matched_variation = None
            
            for variation in skill_variations:
                if not variation:
                    continue
                
                # Use word boundary matching to avoid false positives (e.g., "ase" matching "base")
                # For single-character skills, use special validation
                if len(variation) == 1:
                    # Single-character skills need special handling (e.g., "R" should not match "R&D")
                    if self._is_valid_single_char_match(variation, job_description):
                        exact_match = True
                        matched_variation = variation
                        matched_skills.add(skill_name)
                        break
                else:
                    # Multi-character skills: use word boundary matching
                    pattern = r'\b' + re.escape(variation) + r'\b'
                    if re.search(pattern, job_desc_lower):
                        exact_match = True
                        matched_variation = variation
                        matched_skills.add(skill_name)
                        break
                    elif self._is_partial_match(variation, job_desc_lower):
                        partial_match = True
                        matched_variation = variation
                        matched_skills.add(skill_name)
            
            if exact_match:
                # Find which job skill this matches
                matched_job_skill = self._find_matched_job_skill(skill_name, skill_normalized, job_skills_found)
                
                # CRITICAL: Validate the match is semantically valid
                # This prevents false positives from normalization
                if matched_job_skill:
                    job_skill_normalized = self._get_normalized_skill(matched_job_skill)
                    
                    # Validate the match before adding it
                    if self._validate_skill_match(skill_name, skill_normalized, 
                                                  matched_job_skill, job_skill_normalized):
                        matches['exact_matches'].append({
                            'skill': skill_name,
                            'job_skill': matched_job_skill,
                            'category': skill_data.get('category', 'Unknown'),
                            'source': skill_data.get('source', 'Unknown')
                        })
                    # If validation fails, silently skip (it's a false positive)
                
            elif partial_match:
                # Find which job skill this matches
                matched_job_skill = self._find_matched_job_skill(skill_name, skill_normalized, job_skills_found)
                
                # Validate partial matches too
                if matched_job_skill:
                    job_skill_normalized = self._get_normalized_skill(matched_job_skill)
                    
                    if self._validate_skill_match(skill_name, skill_normalized, 
                                                  matched_job_skill, job_skill_normalized):
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
            # Check if this job skill was already matched in the first pass (candidate -> job)
            already_matched = False
            for exact_match in matches['exact_matches']:
                if exact_match.get('job_skill', '').lower() == job_skill.lower():
                    already_matched = True
                    matched_job_skills += 1
                    break
            if already_matched:
                continue
            for partial_match in matches['partial_matches']:
                if partial_match.get('job_skill', '').lower() == job_skill.lower():
                    already_matched = True
                    matched_job_skills += 1
                    break
            if already_matched:
                continue
            
            # Phase 1: Quick check against skills already found in job description
            if self._is_skill_matched(job_skill, matched_skills):
                matched_job_skills += 1
                # Find the matching candidate skill and categorize as exact or partial
                matched_candidate_skill = self._find_exact_candidate_skill(job_skill, matched_skills)
                if matched_candidate_skill:
                    self._add_match_if_not_duplicate(job_skill, matched_candidate_skill, matches)
            # Phase 2: If not found, check against ALL candidate skills (for cases like "strategy" -> "Business Strategy")
            # This also checks equivalencies (e.g., "Data Engineering" -> "ETL", "Data Pipelines")
            elif self._is_skill_matched(job_skill, all_candidate_skill_names):
                matched_job_skills += 1
                # Find the matching candidate skill and categorize as exact or partial
                matched_candidate_skill = self._find_exact_candidate_skill(job_skill, all_candidate_skill_names)
                if matched_candidate_skill:
                    self._add_match_if_not_duplicate(job_skill, matched_candidate_skill, matches)
            # Phase 3: Check equivalencies in reverse - if job skill has equivalents, check if candidate has those equivalents
            elif self._check_equivalency_match(job_skill, all_candidate_skill_names):
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
            # Use V2 critical requirements if available, otherwise fall back to pattern matching
            critical_requirements_list = []
            
            if matches.get('critical_requirements') and any(matches['critical_requirements'].values()):
                # Use V2 critical requirements data
                for category, items in matches['critical_requirements'].items():
                    for item in items:
                        if item.get('is_critical', False):
                            skill_name = item.get('skill', '')
                            # Check if this critical skill is missing AND candidate doesn't meet the requirement
                            if skill_name and skill_name not in [m['skill'] for m in matches['exact_matches']]:
                                # Check if candidate actually meets the requirement (e.g., 15+ years meets 10+ years)
                                meets_requirement = False
                                if category == 'years_experience':
                                    meets_requirement = self._check_candidate_meets_requirement('years_experience', skill_name)
                                elif category == 'education':
                                    meets_requirement = self._check_candidate_meets_requirement('education', skill_name)
                                
                                # Only add to penalty list if candidate doesn't meet the requirement
                                if not meets_requirement:
                                    critical_requirements_list.append(skill_name)
            else:
                # Fall back to V1 pattern matching
                education_keywords = ['phd', 'doctorate', 'master', 'bachelor', 'degree', 'abd']
                # Only scientific domain expertise that's truly required (not common data science skills)
                # Mathematics/Statistics are standard for analytics roles - treat as regular skills
                domain_keywords = ['biology', 'chemistry', 'physics', 'genetics', 'biochemistry', 'immunology', 'bioinformatics', 'molecular biology']
                
                for unmatched_skill in matches['unmatched_job_skills']:
                    skill_lower = unmatched_skill.lower()
                    is_education = any(edu in skill_lower for edu in education_keywords)
                    is_domain = any(domain in skill_lower for domain in domain_keywords)
                    if is_education or is_domain:
                        critical_requirements_list.append(unmatched_skill)
            
            # If critical requirements are missing, apply severe penalty
            if critical_requirements_list:
                # Each critical requirement is worth 30-50% penalty
                # Missing PhD alone should drop score significantly
                critical_penalty = min(70, len(critical_requirements_list) * 30)  # Cap at 70% penalty
                base_score = max(0, base_score - critical_penalty)
            
            # V2: Apply frequency-based weighting if available
            if matches.get('frequent_skills') and frequent_skills:
                # Weight high-frequency skills more heavily
                # Skills mentioned more frequently are more important
                max_frequency = max(frequent_skills.values()) if frequent_skills.values() else 1
                frequency_weight = 1.0
                
                # Check if unmatched skills include high-frequency terms
                for unmatched_skill in matches['unmatched_job_skills']:
                    skill_lower = unmatched_skill.lower()
                    # Check if this skill or its components appear frequently
                    for freq_skill, freq_count in frequent_skills.items():
                        if freq_skill in skill_lower or skill_lower in freq_skill:
                            # High-frequency missing skills get additional penalty
                            frequency_penalty = (freq_count / max_frequency) * 5  # Up to 5% additional penalty
                            base_score = max(0, base_score - frequency_penalty)
                            break
            
            # Check if candidate is overqualified (has significantly more skills than required)
            # FIX: Only count truly critical missing skills, not all unmatched skills
            # Critical skills are: education requirements (PhD, degree, etc.) and domain expertise (biology, chemistry, etc.)
            critical_skills_missing_list = []
            education_keywords = ['phd', 'doctorate', 'master', 'bachelor', 'degree', 'abd']
            domain_keywords = ['biology', 'chemistry', 'physics', 'genetics', 'biochemistry', 'immunology', 'bioinformatics', 'molecular biology']
            
            for unmatched_skill in matches['unmatched_job_skills']:
                skill_lower = unmatched_skill.lower()
                is_education = any(edu in skill_lower for edu in education_keywords)
                is_domain = any(domain in skill_lower for domain in domain_keywords)
                if is_education or is_domain:
                    critical_skills_missing_list.append(unmatched_skill)
            
            critical_skills_missing = len(critical_skills_missing_list)
            total_unmatched_skills = len(matches['unmatched_job_skills'])
            non_critical_unmatched = total_unmatched_skills - critical_skills_missing
            
            # Debug logging to investigate the issue
            if total_unmatched_skills > 0:
                print(f"🔍 Match Score Debug: total_unmatched={total_unmatched_skills}, critical_missing={critical_skills_missing}, non_critical={non_critical_unmatched}")
                if critical_skills_missing > 0:
                    print(f"   Critical missing: {critical_skills_missing_list}")
                if non_critical_unmatched > 0:
                    non_critical_skills = [s for s in matches['unmatched_job_skills'] if s not in critical_skills_missing_list]
                    print(f"   Non-critical missing: {non_critical_skills[:5]}...")  # Show first 5
            
            total_candidate_skills = len(self.candidate_skills)
            overqualification_ratio = total_candidate_skills / total_job_skills if total_job_skills > 0 else 1
            
            # If overqualified (2x+ more skills), treat missing skills more leniently
            # BUT: Don't apply overqualification bonus if critical requirements are missing
            is_overqualified = overqualification_ratio >= 2.0 and not critical_requirements
            
            if is_overqualified:
                # Overqualified candidates get more generous treatment
                # Missing skills are less impactful when you have many more skills than required
                
                # Calculate missing skill penalty (reduced for overqualified candidates)
                # Note: This uses different "critical" skills (technical) than education/domain critical skills
                if total_unmatched_skills > 0:
                    # Distinguish between critical technical skills and nice-to-have skills
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
                # BUT: Never give 100% if there are unmatched skills - cap at 95%
                if base_score >= 50:  # Lowered from 70% - being overqualified is valuable
                    if overqualification_ratio >= 4.0:  # 4x+ overqualified
                        overqualification_bonus = 10  # Reduced from 15
                    elif overqualification_ratio >= 3.0:  # 3x+ overqualified
                        overqualification_bonus = 7  # Reduced from 10
                    else:  # 2x+ overqualified
                        overqualification_bonus = 5
                    
                    base_score = base_score + overqualification_bonus
                    
                    # FIX: Only cap at 95% if CRITICAL skills are missing (education, domain expertise)
                    # Allow up to 100% if only non-critical skills are missing
                    # This prevents 100% scores when critical requirements are missing, but allows
                    # perfect scores when only minor/nice-to-have skills are missing
                    if critical_skills_missing > 0:
                        base_score = min(95, base_score)
                        print(f"   ⚠️  Capping at 95% due to {critical_skills_missing} critical missing skill(s)")
                    else:
                        base_score = min(100, base_score)
                        if non_critical_unmatched > 0:
                            print(f"   ✅ Allowing up to 100% despite {non_critical_unmatched} non-critical missing skill(s)")
            else:
                # Not overqualified - apply standard penalties for missing skills
                # Only apply penalties if there are unmatched skills (critical or non-critical)
                if total_unmatched_skills > 0:
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
                
                # FIX: Only cap at 95% if CRITICAL skills are missing (education, domain expertise)
                # Allow up to 100% if only non-critical skills are missing
                if critical_skills_missing > 0:
                    base_score = min(95, base_score)
                    print(f"   ⚠️  Capping at 95% due to {critical_skills_missing} critical missing skill(s)")
                else:
                    base_score = min(100, base_score)
                    if non_critical_unmatched > 0:
                        print(f"   ✅ Allowing up to 100% despite {non_critical_unmatched} non-critical missing skill(s)")
            
            matches['match_score'] = round(base_score, 2)
        else:
            # Fallback to candidate skills if no job skills found
            total_skills = len(self.candidate_skills)
            if total_skills > 0:
                matches['match_score'] = round((exact_count + (partial_count * 0.5)) / total_skills * 100, 2)
        
        return matches
    
    def _load_job_engine_v2_config(self) -> Dict:
        """Load Job Engine V2 configuration from YAML file"""
        config_path = Path(__file__).parent.parent.parent / "data" / "config" / "job_engine_v2.yaml"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return config.get('job_engine_v2', {})
            except Exception as e:
                print(f"⚠️  Warning: Could not load Job Engine V2 config: {e}")
                return {'enabled': False, 'console_logging': True, 'phases': {}}
        return {'enabled': False, 'console_logging': True, 'phases': {}}
    
    def _log_engine_status(self, config: Dict) -> None:
        """Log which engine and phases are active"""
        if not config.get('console_logging', True):
            return
        
        from app.utils.message_logger import log_message
        print("🚀 Job Engine V2 Active")
        phases = config.get('phases', {})
        for phase_key, phase_config in phases.items():
            status = "✅" if phase_config.get('enabled', False) else "❌"
            desc = phase_config.get('description', phase_key)
            # Map phase descriptions to message IDs
            message_id = None
            if 'Frequency Analysis' in desc:
                message_id = 51
            elif 'Critical Requirements' in desc:
                message_id = 52
            elif 'Hard Skills' in desc:
                message_id = 53
            log_message(message_id, f"   {desc}: {status}")
    
    def _extract_job_skills_v1(self, job_description: str) -> List[str]:
        """Extract skills using Job Engine V1 (legacy method) - extracted for fallback"""
        # This is the original V1 logic extracted for backward compatibility
        return self._extract_job_skills_from_description_v1_impl(job_description)
    
    def _extract_job_skills_via_ai(self, job_description: str) -> List[str]:
        """
        Extract ALL skills from job description using AI.
        This extracts both predefined and domain-specific skills that may not be in the database.
        
        Returns:
            List of extracted skills (strings)
        """
        try:
            from app.services.ai_analyzer import AIAnalyzer
            from app.utils.prompts import get_prompt
            
            ai_analyzer = AIAnalyzer()
            
            # Get the AI extraction prompt
            prompt = get_prompt('job_skill_extraction', job_description=job_description)
            
            # Call AI to extract skills
            response = ai_analyzer._call_ollama(prompt)
            
            # Parse the response - extract skills from lines
            extracted_skills = []
            job_desc_lower = job_description.lower()
            
            # Clean response - remove common meta-text patterns
            response = re.sub(r'(?:here is|below is|following are).*?skills?:?\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'extracted.*?skills?:?\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'list of skills?:?\s*', '', response, flags=re.IGNORECASE)
            
            for line in response.split('\n'):
                line = line.strip()
                # Skip empty lines and lines that are clearly meta-text
                if not line:
                    continue
                # Skip lines that are clearly explanations or meta-text
                if any(meta in line.lower() for meta in ['here is', 'below is', 'following', 'extracted', 'list of skills', 'return format', 'format:', 'example:', 'job description:']):
                    continue
                # Skip markdown headers and formatting
                if line.startswith('#') or line.startswith('*') or line.startswith('-') or line.startswith('|'):
                    continue
                # Remove numbering if present (e.g., "1. Python" -> "Python")
                line = re.sub(r'^\d+[\.\)]\s*', '', line)
                # Remove bullet points and other prefixes
                line = re.sub(r'^[-*••]\s*', '', line)
                # Remove colons at end (e.g., "Skills:" -> "Skills")
                line = re.sub(r':\s*$', '', line)
                line = line.strip()
                # Must be at least 2 characters and not be common stop words
                if line and len(line) > 1 and line.lower() not in ['skills', 'requirements', 'qualifications', 'responsibilities']:
                    # Validate that it looks like a skill name (not a sentence)
                    if len(line) <= 80 and not line.endswith('.'):  # Skills are usually short, not sentences
                        # CRITICAL: Validate that the skill is actually mentioned in the job description
                        # This prevents AI from hallucinating skills that aren't in the JD
                        skill_words = line.lower().split()
                        # Extract key words (2+ characters) from the skill
                        key_words = [w for w in skill_words if len(w) > 1]
                        if key_words:
                            # Check if at least 50% of key words appear in the job description
                            matching_words = sum(1 for word in key_words if re.search(r'\b' + re.escape(word) + r'\b', job_desc_lower))
                            if matching_words >= max(1, len(key_words) * 0.5):  # At least 50% match or at least 1 word for short skills
                                extracted_skills.append(line)
            
            return extracted_skills
            
        except Exception as e:
            # If AI extraction fails, return empty list (fallback to pattern-based extraction)
            print(f"⚠️  Warning: AI skill extraction failed: {e}")
            return []
    
    def _extract_job_skills_from_description_v1_impl(self, job_description: str) -> List[str]:
        """V1 implementation - original extraction logic"""
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
                # Use advanced SkillNormalizer
                normalized_result = self.skill_normalizer.normalize(skill, fuzzy=True)
                skill_normalized = normalized_result.lower() if normalized_result else ""
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
        
        # Extract data-related skills from context (even if exact phrase not mentioned)
        # If job mentions "data engineers" or "data engineering" → extract "Data Engineering"
        if (re.search(r'\bdata\s+engineers?\b', job_desc_lower, re.IGNORECASE) or 
            re.search(r'\bdata\s+engineering\b', job_desc_lower, re.IGNORECASE)) and 'Data Engineering' not in job_skills:
            job_skills.append('Data Engineering')
        
        # If job mentions "strategy" in data context → extract "Data Strategy"
        if (re.search(r'\bstrategy\b', job_desc_lower, re.IGNORECASE) and 
            (re.search(r'\bdata\b', job_desc_lower, re.IGNORECASE) or 
             re.search(r'\bml\s+initiatives\b', job_desc_lower, re.IGNORECASE) or
             re.search(r'\bdata\s+platforms?\b', job_desc_lower, re.IGNORECASE) or
             re.search(r'\bdata\s+products?\b', job_desc_lower, re.IGNORECASE)) and 
            'Data Strategy' not in job_skills):
            job_skills.append('Data Strategy')
        
        # Extract Program Management (often paired with Data Strategy or in job titles)
        if re.search(r'\bprogram\s+management\b', job_desc_lower, re.IGNORECASE) and 'Program Management' not in job_skills:
            job_skills.append('Program Management')
        
        # If job mentions "BI tools", "visualization", or "data visualization" → extract "Data Visualization"
        if ((re.search(r'\bbi\s+tools?\b', job_desc_lower, re.IGNORECASE) or 
             re.search(r'\bvisualization\b', job_desc_lower, re.IGNORECASE) or
             re.search(r'\bdata\s+visualization\b', job_desc_lower, re.IGNORECASE) or
             re.search(r'\breporting\b', job_desc_lower, re.IGNORECASE)) and 
            'Data Visualization' not in job_skills):
            job_skills.append('Data Visualization')
        
        # Extract data governance and management skills
        if re.search(r'\bdata\s+governance\b', job_desc_lower, re.IGNORECASE) and 'Data Governance' not in job_skills:
            job_skills.append('Data Governance')
        
        # Extract governance when mentioned in data context
        if (re.search(r'\bgovernance\b', job_desc_lower, re.IGNORECASE) and 
            re.search(r'\bdata\b', job_desc_lower, re.IGNORECASE) and
            'Data Governance' not in job_skills):
            # Check if governance appears near data (within 100 characters)
            governance_matches = list(re.finditer(r'\bgovernance\b', job_desc_lower, re.IGNORECASE))
            data_matches = list(re.finditer(r'\bdata\b', job_desc_lower, re.IGNORECASE))
            for gov_match in governance_matches:
                for data_match in data_matches:
                    if abs(gov_match.start() - data_match.start()) < 100:
                        job_skills.append('Data Governance')
                        break
                if 'Data Governance' in job_skills:
                    break
        
        if re.search(r'\bdata\s+management\b', job_desc_lower, re.IGNORECASE) and 'Data Management' not in job_skills:
            job_skills.append('Data Management')
        
        if re.search(r'\bdata\s+quality\b', job_desc_lower, re.IGNORECASE) and 'Data Quality' not in job_skills:
            job_skills.append('Data Quality')
        
        if re.search(r'\bdata\s+privacy\b', job_desc_lower, re.IGNORECASE) and 'Data Privacy' not in job_skills:
            job_skills.append('Data Privacy')
        
        if re.search(r'\bdata\s+security\b', job_desc_lower, re.IGNORECASE) and 'Data Security' not in job_skills:
            job_skills.append('Data Security')
        
        if re.search(r'\bdata\s+stewardship\b', job_desc_lower, re.IGNORECASE) and 'Data Stewardship' not in job_skills:
            job_skills.append('Data Stewardship')
        
        if re.search(r'\bdata\s+partnerships?\b', job_desc_lower, re.IGNORECASE) and 'Data Partnerships' not in job_skills:
            job_skills.append('Data Partnerships')
        
        if re.search(r'\bdata\s+standards\b', job_desc_lower, re.IGNORECASE) and 'Data Standards' not in job_skills:
            job_skills.append('Data Standards')
        
        # Extract compliance and regulatory skills
        if re.search(r'\bcompliance\b', job_desc_lower, re.IGNORECASE) and 'Compliance' not in job_skills:
            job_skills.append('Compliance')
        
        if re.search(r'\bregulatory\s+requirements?\b', job_desc_lower, re.IGNORECASE) and 'Regulatory Requirements' not in job_skills:
            job_skills.append('Regulatory Requirements')
        
        if re.search(r'\bregulatory\s+compliance\b', job_desc_lower, re.IGNORECASE) and 'Regulatory Compliance' not in job_skills:
            job_skills.append('Regulatory Compliance')
        
        # Extract risk management
        if re.search(r'\brisk\s+management\b', job_desc_lower, re.IGNORECASE) and 'Risk Management' not in job_skills:
            job_skills.append('Risk Management')
        
        # Extract stakeholder management
        if re.search(r'\bstakeholder\s+management\b', job_desc_lower, re.IGNORECASE) and 'Stakeholder Management' not in job_skills:
            job_skills.append('Stakeholder Management')
        
        if re.search(r'\bstakeholder\s+engagement\b', job_desc_lower, re.IGNORECASE) and 'Stakeholder Engagement' not in job_skills:
            job_skills.append('Stakeholder Engagement')
        
        # Extract leadership and management skills
        if re.search(r'\bengineering\s+management\b', job_desc_lower, re.IGNORECASE) and 'Engineering Management' not in job_skills:
            job_skills.append('Engineering Management')
        
        if re.search(r'\bcoaching\b', job_desc_lower, re.IGNORECASE) and 'Coaching' not in job_skills:
            job_skills.append('Coaching')
        
        if re.search(r'\bperformance\s+management\b', job_desc_lower, re.IGNORECASE) and 'Performance Management' not in job_skills:
            job_skills.append('Performance Management')
        
        if re.search(r'\bhiring\b', job_desc_lower, re.IGNORECASE) and 'Hiring' not in job_skills:
            job_skills.append('Hiring')
        
        if re.search(r'\btalent\s+acquisition\b', job_desc_lower, re.IGNORECASE) and 'Talent Acquisition' not in job_skills:
            job_skills.append('Talent Acquisition')
        
        # Extract strategy and decision-making
        if re.search(r'\barchitectural\s+decisions?\b', job_desc_lower, re.IGNORECASE) and 'Architectural Decision Making' not in job_skills:
            job_skills.append('Architectural Decision Making')
        
        if re.search(r'\bprioritization\b', job_desc_lower, re.IGNORECASE) and 'Prioritization' not in job_skills:
            job_skills.append('Prioritization')
        
        # Extract financial management
        if re.search(r'\bcost\s+management\b', job_desc_lower, re.IGNORECASE) and 'Cost Management' not in job_skills:
            job_skills.append('Cost Management')
        
        if re.search(r'\bfinops\b', job_desc_lower, re.IGNORECASE) and 'FinOps' not in job_skills:
            job_skills.append('FinOps')
        
        # Extract communication and collaboration
        if re.search(r'\bexecutive\s+communication\b', job_desc_lower, re.IGNORECASE) and 'Executive Communication' not in job_skills:
            job_skills.append('Executive Communication')
        
        if re.search(r'\bincident\s+management\b', job_desc_lower, re.IGNORECASE) and 'Incident Management' not in job_skills:
            job_skills.append('Incident Management')
        
        if re.search(r'\broot\s+cause\s+analysis\b', job_desc_lower, re.IGNORECASE) and 'Root Cause Analysis' not in job_skills:
            job_skills.append('Root Cause Analysis')
        
        if re.search(r'\bgo-to-market\b', job_desc_lower, re.IGNORECASE) and 'Go-To-Market' not in job_skills:
            job_skills.append('Go-To-Market')
        
        if re.search(r'\bgtm\b', job_desc_lower, re.IGNORECASE) and 'GTM' not in job_skills and 'Go-To-Market' not in job_skills:
            job_skills.append('GTM')
        
        # Extract risk management
        if re.search(r'\brisk\s+mitigation\b', job_desc_lower, re.IGNORECASE) and 'Risk Mitigation' not in job_skills:
            job_skills.append('Risk Mitigation')
        
        # Extract metadata management
        if re.search(r'\bmetadata\s+management\b', job_desc_lower, re.IGNORECASE) and 'Metadata Management' not in job_skills:
            job_skills.append('Metadata Management')
        
        # Extract data product
        if re.search(r'\bdata\s+product\b', job_desc_lower, re.IGNORECASE) and 'Data Product' not in job_skills:
            job_skills.append('Data Product')
        
        # Extract data infrastructure and platform
        if re.search(r'\bdata\s+infrastructure\b', job_desc_lower, re.IGNORECASE) and 'Data Infrastructure' not in job_skills:
            job_skills.append('Data Infrastructure')
        
        if re.search(r'\bdata\s+platform\b', job_desc_lower, re.IGNORECASE) and 'Data Platform' not in job_skills:
            job_skills.append('Data Platform')
        
        # Extract observability
        if re.search(r'\bobservability\b', job_desc_lower, re.IGNORECASE) and 'Observability' not in job_skills:
            job_skills.append('Observability')
        
        # Extract distributed systems
        if re.search(r'\bdistributed\s+systems?\b', job_desc_lower, re.IGNORECASE) and 'Distributed Systems' not in job_skills:
            job_skills.append('Distributed Systems')
        
        # Extract schema design
        if re.search(r'\bschema\s+design\b', job_desc_lower, re.IGNORECASE) and 'Schema Design' not in job_skills:
            job_skills.append('Schema Design')
        
        # Extract data modeling (more specific than just "modeling")
        if re.search(r'\bdata\s+modeling\b', job_desc_lower, re.IGNORECASE) and 'Data Modeling' not in job_skills:
            job_skills.append('Data Modeling')
        
        # Extract product vision
        if re.search(r'\bproduct\s+vision\b', job_desc_lower, re.IGNORECASE) and 'Product Vision' not in job_skills:
            job_skills.append('Product Vision')
        
        # Extract business insights
        if re.search(r'\bbusiness\s+insights?\b', job_desc_lower, re.IGNORECASE) and 'Business Insights' not in job_skills:
            job_skills.append('Business Insights')
        
        # Extract data manipulation
        if re.search(r'\bdata\s+manipulation\b', job_desc_lower, re.IGNORECASE) and 'Data Manipulation' not in job_skills:
            job_skills.append('Data Manipulation')
        
        # Extract "translate complex data" capability
        if re.search(r'\btranslate.*?complex.*?data\b', job_desc_lower, re.IGNORECASE) and 'Translate Complex Data' not in job_skills:
            job_skills.append('Translate Complex Data')
        
        # Extract "actionable" - capability to provide actionable insights
        if re.search(r'\bactionable\b', job_desc_lower, re.IGNORECASE) and 'Actionable Insights' not in job_skills:
            job_skills.append('Actionable Insights')
        
        # Extract "data engineering roles" or data engineering experience
        if re.search(r'\bdata\s+engineering\s+roles?\b', job_desc_lower, re.IGNORECASE) and 'Data Engineering Roles' not in job_skills:
            job_skills.append('Data Engineering Roles')
        
        # Extract excellent communication skills
        if re.search(r'\bexcellent\s+communication\s+skills?\b', job_desc_lower, re.IGNORECASE) and 'Excellent Communication Skills' not in job_skills:
            job_skills.append('Excellent Communication Skills')
        
        # Extract stakeholder engagement/influence
        if re.search(r'\bstakeholder.*?(?:engagement|influence|communication)\b', job_desc_lower, re.IGNORECASE) and 'Stakeholder Engagement' not in job_skills:
            job_skills.append('Stakeholder Engagement')
        
        # Extract "engage and influence stakeholders"
        if re.search(r'\bengage.*?influence.*?stakeholder\b', job_desc_lower, re.IGNORECASE) and 'Stakeholder Engagement' not in job_skills:
            job_skills.append('Stakeholder Engagement')
        
        # Extract data engineering processes
        if re.search(r'\bingestion\b', job_desc_lower, re.IGNORECASE) and 'Data Ingestion' not in job_skills:
            job_skills.append('Data Ingestion')
        
        if re.search(r'\btransformation\b', job_desc_lower, re.IGNORECASE) and 'Data Transformation' not in job_skills:
            job_skills.append('Data Transformation')
        
        if re.search(r'\benrichment\b', job_desc_lower, re.IGNORECASE) and 'Data Enrichment' not in job_skills:
            job_skills.append('Data Enrichment')
        
        if re.search(r'\betl\b', job_desc_lower, re.IGNORECASE) and 'ETL' not in job_skills:
            job_skills.append('ETL')
        
        if re.search(r'\belt\b', job_desc_lower, re.IGNORECASE) and 'ELT' not in job_skills:
            job_skills.append('ELT')
        
        if re.search(r'\bdata\s+pipelines?\b', job_desc_lower, re.IGNORECASE) and 'Data Pipeline' not in job_skills:
            job_skills.append('Data Pipeline')
        
        if re.search(r'\bpipelines?\b', job_desc_lower, re.IGNORECASE) and 'Pipeline' not in job_skills and 'Data Pipeline' not in job_skills:
            job_skills.append('Pipeline')
        
        # Extract database types
        # Check for "relational database" or "relational" in context of databases/systems
        if (re.search(r'\brelational\s+(database|databases|systems?)\b', job_desc_lower, re.IGNORECASE) or
            (re.search(r'\brelational\b', job_desc_lower, re.IGNORECASE) and 
             re.search(r'\b(database|databases|systems?|mpp|nosql)\b', job_desc_lower, re.IGNORECASE))) and 'Relational Database' not in job_skills:
            job_skills.append('Relational Database')
        
        # Extract automation
        if re.search(r'\bautomation\b', job_desc_lower, re.IGNORECASE) and 'Automation' not in job_skills:
            job_skills.append('Automation')
        
        # Extract certifications mentioned
        if re.search(r'\bdm-bok\b', job_desc_lower, re.IGNORECASE) and 'DM-BOK' not in job_skills:
            job_skills.append('DM-BOK')
        
        if re.search(r'\bcdmp\b', job_desc_lower, re.IGNORECASE) and 'CDMP' not in job_skills:
            job_skills.append('CDMP')
        
        # Extract MBA if mentioned
        if re.search(r'\bmba\b', job_desc_lower, re.IGNORECASE) and 'MBA' not in job_skills:
            job_skills.append('MBA')
        
        # Extract database/system types
        if re.search(r'\bnosql\b', job_desc_lower, re.IGNORECASE) and 'NoSQL' not in job_skills:
            job_skills.append('NoSQL')
        
        if re.search(r'\bmpp\b', job_desc_lower, re.IGNORECASE) and 'MPP' not in job_skills:
            job_skills.append('MPP')
        
        # Extract technologies using SimpleTechExtractor (comprehensive 157+ technologies)
        # This replaces the hardcoded list and ensures consistency across the codebase
        extracted_technologies = self.tech_extractor.extract_technologies(job_description)
        for tech in extracted_technologies:
            # Normalize technology using SkillNormalizer to get canonical name
            normalized_tech = self.skill_normalizer.normalize(tech, fuzzy=True)
            # Use canonical name if found, otherwise use original
            tech_to_add = normalized_tech if normalized_tech else tech
            
            # Add technology if not already in job_skills (case-insensitive check)
            tech_lower = tech_to_add.lower()
            if tech_to_add not in job_skills and tech_lower not in [s.lower() for s in job_skills]:
                job_skills.append(tech_to_add)
            
            # For compound technology names like "Apache Airflow", also add the core technology
            # This ensures "airflow" is extracted even if "Apache Airflow" gets filtered
            if 'apache' in tech_lower:
                core_tech = tech_lower.replace('apache', '').strip()
                if core_tech and core_tech not in [s.lower() for s in job_skills]:
                    # Capitalize first letter for consistency
                    core_tech_capitalized = core_tech.capitalize()
                    job_skills.append(core_tech_capitalized)
        
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
            # BUT: Don't filter out education/domain/research/data skills that we explicitly extracted
            is_education_skill = any(edu in skill_clean.lower() for edu in ['phd', 'doctorate', 'master', 'bachelor', 'abd', 'mba'])
            is_domain_skill = any(domain in skill_clean.lower() for domain in ['biology', 'chemistry', 'physics', 'genetics', 'biochemistry', 'immunology', 'bioinformatics'])
            is_research_skill = any(research in skill_clean.lower() for research in ['research', 'experimental'])
            is_data_skill = any(data_term in skill_clean.lower() for data_term in [
                'data governance', 'data management', 'data quality', 'data privacy', 'data security',
                'data stewardship', 'data partnerships', 'data standards', 'data engineering', 'data strategy',
                'data visualization', 'data product', 'data infrastructure', 'data platform', 'data modeling',
                'data ingestion', 'data transformation', 'data enrichment', 'data pipeline', 'pipeline',
                'metadata management', 'observability', 'distributed systems', 'schema design',
                'etl', 'elt', 'relational database', 'automation',
                'compliance', 'regulatory',
                'risk management', 'risk mitigation', 'stakeholder management', 'stakeholder engagement',
                'engineering management', 'coaching', 'performance management', 'hiring', 'talent acquisition',
                'architectural decision making', 'prioritization', 'cost management', 'finops',
                'executive communication', 'incident management', 'root cause analysis', 'go-to-market', 'gtm',
                'dm-bok', 'cdmp'
            ])
            
            # Allow shorter skills if they're education/domain/research/data (PhD is 3 chars, so >= 3)
            min_length = 2 if (is_education_skill or is_domain_skill or is_research_skill or is_data_skill) else 3
            
            if (is_valid and 
                len(skill_clean) >= min_length and 
                len(skill_clean) < 50 and 
                skill_clean not in filtered_skills and
                (is_education_skill or is_domain_skill or is_research_skill or is_data_skill or 
                 not any(word in skill_clean.lower() for word in ['experience', 'years', 'minimum', 'preferred']))):
                
                # Final validation: Verify the skill actually appears in JD (not just similar words)
                # Extract core skill name (remove parentheticals, qualifiers)
                core_skill_for_validation = skill_clean.lower()
                core_skill_for_validation = re.sub(r'\s*\([^)]*\)', '', core_skill_for_validation)  # Remove parentheticals
                core_skill_for_validation = re.sub(r'\s*requirements?$', '', core_skill_for_validation, flags=re.IGNORECASE)
                core_skill_for_validation = core_skill_for_validation.strip()
                
                # Check if core skill appears in JD with word boundaries (more strict)
                # BUT: Skip validation for data/education/domain/research skills we explicitly extracted
                if is_data_skill or is_education_skill or is_domain_skill or is_research_skill:
                    # Trust these skills - we extracted them because they appeared in JD
                    filtered_skills.append(skill_clean)
                elif len(core_skill_for_validation) >= 3:
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
    
    def _extract_job_skills_from_description(self, job_description: str) -> List[str]:
        """
        Extract skills mentioned in job description using hybrid approach.
        Uses AI extraction (comprehensive) + pattern-based extraction (predefined skills) + normalization.
        Supports both Job Engine V1 (legacy) and Job Engine V2 (advanced) based on configuration.
        """
        job_skills = []
        
        # Step 1: AI-based extraction (extracts ALL skills, including domain-specific)
        # BUT: Validate that skills are actually in the JD before adding them
        from app.utils.message_logger import log_message
        job_desc_lower = job_description.lower()
        ai_extracted_skills = self._extract_job_skills_via_ai(job_description)
        if ai_extracted_skills and len(ai_extracted_skills) > 0:
            print(f"🤖 AI extracted {len(ai_extracted_skills)} candidate skills from job description")
            
            # CRITICAL: Validate that each AI-extracted skill is actually mentioned in the JD
            # This prevents AI from hallucinating skills from previous extractions
            validated_ai_skills = []
            for skill in ai_extracted_skills:
                # Normalize skill for validation
                normalized = self.skill_normalizer.normalize(skill, fuzzy=True)
                skill_to_check = normalized.lower() if normalized else skill.lower()
                
                # Extract key words from skill (2+ characters)
                skill_words = skill_to_check.split()
                key_words = [w for w in skill_words if len(w) > 2]
                
                if key_words:
                    # Validate: at least 50% of key words must appear in JD, OR the full skill phrase appears
                    matching_words = sum(1 for word in key_words if re.search(r'\b' + re.escape(word) + r'\b', job_desc_lower))
                    full_phrase_match = re.search(r'\b' + re.escape(skill_to_check) + r'\b', job_desc_lower, re.IGNORECASE)
                    
                    if full_phrase_match or matching_words >= max(1, len(key_words) * 0.5):
                        # Skill is validated - normalize and add
                        if normalized:
                            validated_ai_skills.append(normalized)
                        else:
                            validated_ai_skills.append(skill)
            
            if validated_ai_skills:
                print(f"✓ Validated {len(validated_ai_skills)}/{len(ai_extracted_skills)} AI-extracted skills against JD")
                job_skills.extend(validated_ai_skills)
        
        # Check if Job Engine V2 is enabled
        v2_config = self._load_job_engine_v2_config()
        
        if not v2_config.get('enabled', False):
            # Use V1 (legacy) engine for pattern-based extraction
            if v2_config.get('console_logging', True):
                print("⚙️  Job Engine V1 Active (Legacy)")
            v1_skills = self._extract_job_skills_v1(job_description)
            job_skills.extend(v1_skills)
            
            # Deduplicate and consolidate similar skills
            job_skills = self._consolidate_similar_skills(job_skills)
            return job_skills
        
        # Job Engine V2 is enabled - log status
        if v2_config.get('console_logging', True):
            self._log_engine_status(v2_config)
        
        # Start V2 extraction
        job_desc_lower = job_description.lower()
        
        # NEW: Step 2c.0 - Frequency Analysis (Word Cloud) - Phase 1.1
        frequent_skills = {}
        if v2_config.get('phases', {}).get('phase_1_frequency_analysis', {}).get('enabled', False):
            if v2_config.get('console_logging', True):
                log_message(67, "📊 Job Engine V2 - Phase 1.1: Frequency Analysis active")
            frequent_skills = self._extract_frequent_skills(job_description)
        
        # NEW: Step 2c.1 - Critical Requirements (Highlighting, not blocking) - Phase 1.2
        critical_requirements = {}
        if v2_config.get('phases', {}).get('phase_1_critical_requirements', {}).get('enabled', False):
            if v2_config.get('console_logging', True):
                log_message(68, "🎯 Job Engine V2 - Phase 1.2: Critical Requirements Highlighting active")
            critical_requirements = self._identify_critical_requirements(job_description)
        
        # NEW: Step 2c.2 - Hard Skills from Sections - Phase 2.1
        hard_skills = []
        if v2_config.get('phases', {}).get('phase_2_hard_skills', {}).get('enabled', False):
            if v2_config.get('console_logging', True):
                log_message(69, "🔧 Job Engine V2 - Phase 2.1: Hard Skills Extraction active")
            hard_skills = self._extract_hard_skills_from_sections(job_description)
        
        # Continue with existing V1 logic (always run for compatibility)
        # This ensures all existing patterns still work
        v1_skills = self._extract_job_skills_from_description_v1_impl(job_description)
        job_skills.extend(v1_skills)
        
        # Add V2-specific skills (from hard skills extraction)
        for skill in hard_skills:
            if skill not in job_skills:
                job_skills.append(skill)
        
        # Note: frequency_skills and critical_requirements are used in find_skill_matches()
        # for weighting and penalties, not for skill extraction
        
        # Deduplicate and consolidate
        consolidated_skills = self._consolidate_similar_skills(job_skills)
        
        return consolidated_skills
    
    def _extract_frequent_skills(self, job_description: str, min_frequency: int = 2) -> Dict[str, int]:
        """
        Extract skills by frequency analysis (Word Cloud approach).
        Only counts frequencies of known skills from taxonomy and job skills database.
        Identifies most important requirements by counting repetitions of actual skills.
        
        Args:
            job_description: Full job description text
            min_frequency: Minimum number of mentions to include (default: 2)
        
        Returns:
            Dictionary mapping skill -> frequency count (only for known skills)
        """
        # Build set of all known skills from taxonomy and job skills database
        known_skills_set = set()
        
        # Load skills from taxonomy (canonical names + aliases)
        taxonomy_path = Path(__file__).parent.parent.parent / "data" / "config" / "skill_normalization.yaml"
        if taxonomy_path.exists():
            try:
                with open(taxonomy_path, 'r') as f:
                    taxonomy_data = yaml.safe_load(f)
                    skills_data = taxonomy_data.get('skills', {})
                    for skill_key, skill_info in skills_data.items():
                        # Add canonical name
                        canonical = skill_info.get('canonical', skill_key)
                        if isinstance(canonical, str):
                            known_skills_set.add(canonical.lower())
                        # Add all aliases
                        aliases = skill_info.get('aliases', [])
                        for alias in aliases:
                            if isinstance(alias, str):
                                known_skills_set.add(alias.lower())
            except Exception as e:
                print(f"⚠️  Warning: Could not load skills taxonomy: {e}")
        
        # Load skills from job skills markdown
        if self.job_skills_path.exists():
            job_skills_content = read_text_file(self.job_skills_path)
            for category, skills in self.job_skills.items():
                for skill in skills:
                    # Normalize skill name
                    normalized = self.skill_normalizer.normalize(skill, fuzzy=True)
                    if normalized:
                        known_skills_set.add(normalized.lower())
                    # Also add original (lowercased)
                    known_skills_set.add(skill.lower())
        
        # Now count frequencies of only known skills in job description
        job_desc_lower = job_description.lower()
        skill_frequencies = {}
        
        # Count each known skill
        for skill in known_skills_set:
            # Create pattern to match the skill (word boundaries)
            # Handle multi-word skills
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            matches = len(re.findall(skill_pattern, job_desc_lower, re.IGNORECASE))
            if matches >= min_frequency:
                skill_frequencies[skill] = matches
        
        return skill_frequencies
    
    def _identify_critical_requirements(self, job_description: str) -> Dict[str, List[Dict[str, any]]]:
        """
        Identify critical requirements that should be highlighted (not used for blocking).
        Supports career pivots by flagging missing critical skills but allowing evaluation to continue.
        
        Args:
            job_description: Full job description text
        
        Returns:
            Dictionary with categories: 'education', 'certifications', 'domain_expertise', 
            'years_experience', 'specific_skills'
            Each item includes: {'skill': str, 'is_critical': bool, 'highlight_reason': str}
        """
        critical = {
            'education': [],
            'certifications': [],
            'domain_expertise': [],
            'years_experience': [],
            'specific_skills': []
        }
        
        job_desc_lower = job_description.lower()
        
        # Enhanced patterns for critical requirements
        # Check if we're in a "Required Qualifications" section context
        required_section_context = re.search(r'required\s+(?:qualifications?|skills?|experience)', job_desc_lower, re.IGNORECASE)
        
        # Education requirements - check both explicit "required" patterns and section context
        education_patterns = [
            (r'\b(?:required|must have|non-negotiable|essential).*?(?:ph\.?d\.?|phd|doctorate)\b', 'PhD', 'Required in job description'),
            (r'\b(?:required|must have|non-negotiable|essential).*?(?:master\'?s?\s+degree|m\.?s\.?|m\.?a\.?)\b', "Master's Degree", 'Required in job description'),
            (r'\b(?:required|must have|non-negotiable|essential).*?(?:bachelor\'?s?\s+degree|b\.?s\.?|b\.?a\.?)\b', "Bachelor's Degree", 'Required in job description'),
        ]
        
        # If in required section, also check for education without explicit "required" keyword
        if required_section_context:
            education_patterns.extend([
                (r'\b(?:ph\.?d\.?|phd|doctorate)\b', 'PhD', 'Required in Required Qualifications section'),
                (r'\bmaster[\'\u2019]?s?\s+degree\b', "Master's Degree", 'Required in Required Qualifications section'),
                (r'\bbachelor[\'\u2019]?s?\s+degree\b', "Bachelor's Degree", 'Required in Required Qualifications section'),
            ])
        
        for pattern, skill_name, reason in education_patterns:
            if re.search(pattern, job_description, re.IGNORECASE):
                # Avoid duplicates
                if not any(item['skill'] == skill_name for item in critical['education']):
                    critical['education'].append({
                        'skill': skill_name,
                        'is_critical': True,
                        'highlight_reason': reason
                    })
        
        # Years of experience requirements
        years_patterns = [
            (r'\b(?:required|must have|non-negotiable|essential).*?(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|exp)\b', 'years_experience'),
            (r'\bminimum\s+of\s+(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|exp)\b', 'years_experience'),
        ]
        
        # If in required section, also check for years without explicit "required" keyword
        if required_section_context:
            years_patterns.append((r'\b(\d+)\+?\s*years?\s+(?:of\s+)?(?:directly\s+)?(?:relevant\s+)?(?:work\s+)?(?:experience|exp)\b', 'years_experience'))
        
        for pattern, category in years_patterns:
            matches = re.finditer(pattern, job_description, re.IGNORECASE)
            for match in matches:
                years = match.group(1)
                skill_name = f"{years}+ years experience"
                # Avoid duplicates
                if not any(item['skill'] == skill_name for item in critical['years_experience']):
                    critical['years_experience'].append({
                        'skill': skill_name,
                        'is_critical': True,
                        'highlight_reason': 'Minimum experience requirement specified'
                    })
        
        # Certifications
        cert_patterns = [
            (r'\b(?:required|must have|non-negotiable|essential).*?(?:aws\s+certified|aws\s+certification)\b', 'AWS Certification', 'Required certification'),
            (r'\b(?:required|must have|non-negotiable|essential).*?(?:pmp|certified\s+project\s+manager)\b', 'PMP Certification', 'Required certification'),
            (r'\b(?:required|must have|non-negotiable|essential).*?(?:cdmp|data\s+management\s+professional)\b', 'CDMP', 'Required certification'),
        ]
        
        for pattern, cert_name, reason in cert_patterns:
            if re.search(pattern, job_description, re.IGNORECASE):
                critical['certifications'].append({
                    'skill': cert_name,
                    'is_critical': True,
                    'highlight_reason': reason
                })
        
        # Domain expertise (already partially handled, but enhance)
        domain_keywords = ['biology', 'chemistry', 'physics', 'genetics', 'biochemistry', 'immunology', 'bioinformatics', 'molecular biology']
        for domain in domain_keywords:
            if re.search(rf'\b(?:required|must have|non-negotiable|essential).*?{domain}\b', job_description, re.IGNORECASE):
                critical['domain_expertise'].append({
                    'skill': domain.title(),
                    'is_critical': True,
                    'highlight_reason': 'Required domain expertise'
                })
        
        return critical
    
    def _extract_hard_skills_from_sections(self, job_description: str) -> List[str]:
        """
        Extract hard skills (technical nouns) from specific sections.
        
        Focus on:
        - "Required Qualifications" section
        - "Must-Have Skills" section
        - "Technical Requirements" section
        - Bullet points starting with technical terms
        
        Args:
            job_description: Full job description text
        
        Returns:
            List of hard skills extracted from structured sections
        """
        hard_skills = []
        job_desc_lower = job_description.lower()
        
        # Define section markers
        required_sections = [
            r'required\s+qualifications?',
            r'required\s+skills?',
            r'must[- ]have\s+(?:technical\s+)?skills?',
            r'technical\s+requirements?',
            r'required\s+experience',
            r'essential\s+qualifications?',
            r'essential\s+skills?'
        ]
        
        # Find sections and extract skills from them
        for section_pattern in required_sections:
            # Find the section
            section_match = re.search(rf'{section_pattern}.*?(?=\n\n|\n##|\n###|$)', job_description, re.IGNORECASE | re.DOTALL)
            if section_match:
                section_text = section_match.group(0)
                section_lower = section_text.lower()
                
                # Extract technologies from this section using SimpleTechExtractor
                section_techs = self.tech_extractor.extract_technologies(section_text)
                for tech in section_techs:
                    if tech not in hard_skills:
                        hard_skills.append(tech)
                
                # Extract skills from bullet points in this section
                bullet_points = re.findall(r'[•\-\*]\s*(.+?)(?=\n|$)', section_text, re.MULTILINE)
                for bullet in bullet_points:
                    # Check if bullet contains technical terms
                    bullet_lower = bullet.lower()
                    # Extract potential technical skills (capitalized words, technical terms)
                    tech_terms = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', bullet)
                    for term in tech_terms:
                        if len(term) > 2 and term.lower() not in ['the', 'and', 'or', 'for', 'with']:
                            normalized = self.skill_normalizer.normalize(term, fuzzy=True)
                            if normalized and normalized not in hard_skills:
                                hard_skills.append(normalized)
        
        return hard_skills
    
    def _check_candidate_meets_requirement(self, requirement_type: str, requirement_value: str) -> bool:
        """
        Check if candidate meets a critical requirement (years of experience, education).
        
        Args:
            requirement_type: 'years_experience' or 'education'
            requirement_value: The requirement value (e.g., "10+ years experience", "Master's Degree")
        
        Returns:
            True if candidate meets the requirement, False otherwise
        """
        # Load base resume to check candidate qualifications
        base_resume_path = Path(__file__).parent.parent.parent / "resumes" / "base_resume.md"
        if not base_resume_path.exists():
            return False  # Can't verify, assume doesn't meet (conservative)
        
        try:
            resume_content = read_text_file(base_resume_path).lower()
        except Exception:
            return False
        
        if requirement_type == 'years_experience':
            # Extract years from requirement (e.g., "10+ years" -> 10)
            years_match = re.search(r'(\d+)\+?\s*years?', requirement_value.lower())
            if not years_match:
                return False
            
            required_years = int(years_match.group(1))
            
            # Extract candidate's years of experience from resume
            # Look for patterns like "15 years", "over 15 years", "15+ years", etc.
            candidate_years_patterns = [
                r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|expertise|professional)',
                r'over\s+(\d+)\s+years?',
                r'more\s+than\s+(\d+)\s+years?',
                r'(\d+)\+?\s*years?\s+in',
            ]
            
            max_candidate_years = 0
            for pattern in candidate_years_patterns:
                matches = re.finditer(pattern, resume_content, re.IGNORECASE)
                for match in matches:
                    years = int(match.group(1))
                    max_candidate_years = max(max_candidate_years, years)
            
            # Candidate meets requirement if they have >= required years
            return max_candidate_years >= required_years
        
        elif requirement_type == 'education':
            # Check if candidate has equivalent or higher education
            # Education hierarchy: PhD > Master's > Bachelor's
            
            requirement_lower = requirement_value.lower()
            resume_lower = resume_content.lower()
            
            # Check for PhD requirement
            if 'phd' in requirement_lower or 'doctorate' in requirement_lower:
                return 'phd' in resume_lower or 'doctorate' in resume_lower or 'ph.d' in resume_lower
            
            # Check for Master's requirement
            elif "master" in requirement_lower:
                # Candidate meets if they have Master's, PhD, or equivalent
                return ('master' in resume_lower or 'm.s' in resume_lower or 
                       'm.a' in resume_lower or 'mba' in resume_lower or
                       'phd' in resume_lower or 'doctorate' in resume_lower)
            
            # Check for Bachelor's requirement
            elif "bachelor" in requirement_lower:
                # Candidate meets if they have Bachelor's, Master's, PhD, or equivalent
                return ('bachelor' in resume_lower or 'b.s' in resume_lower or 
                       'b.a' in resume_lower or 'degree' in resume_lower or
                       'master' in resume_lower or 'phd' in resume_lower)
            
            return False
        
        return False
    
    def _is_skill_matched(self, job_skill: str, matched_skills: set) -> bool:
        """Check if a job skill matches any candidate skill (optimized with cache)"""
        if not job_skill or not job_skill.strip():
            return False
            
        # Use advanced SkillNormalizer
        normalized_result = self.skill_normalizer.normalize(job_skill, fuzzy=True)
        job_skill_normalized = normalized_result.lower() if normalized_result else ""
        
        # If normalization returns empty/None, use lowercase original as fallback                                                                               
        if not job_skill_normalized:
            job_skill_normalized = job_skill.lower().strip()
        
        # Normalize hyphens and handle plurals for better matching
        job_skill_normalized = job_skill_normalized.replace('-', ' ').replace('_', ' ')
        job_skill_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_skill_normalized).strip()
        
        # Combine hardcoded equivalences with loaded equivalency mappings
        # Start with legacy hardcoded mappings for backward compatibility
        skill_equivalences = {
            'aws lake formation': ['aws', 'lake formation', 'data lake', 'data warehousing'],
            'amazon kinesis': ['aws', 'kinesis', 'streaming', 'data streaming'],
            'amazon q': ['aws', 'ai', 'artificial intelligence', 'machine learning'],
            'budget management': ['financial management', 'budget', 'financial', 'management', 'leadership'],
            'financial management': ['budget management', 'financial', 'budget', 'management', 'leadership'],
            'insights': ['insight', 'analytics', 'data insights', 'business insights'],                                                                         
            'paid advertising': ['advertising', 'digital marketing', 'google ads', 'meta', 'amazon ads'],
            'advertising platforms': ['paid advertising', 'digital marketing', 'google ads', 'meta', 'amazon ads'],
            'problem solving': ['problem-solving', 'problem-solving skills', 'problem solving skills'],
            'problem-solving': ['problem solving', 'problem-solving skills', 'problem solving skills'],
            'problem-solving skills': ['problem solving', 'problem-solving'],
        }
        
        # Add loaded equivalency mappings (from YAML file)
        # Normalize keys and values to lowercase for matching
        for key, values in self.skill_equivalencies.items():
            key_normalized = key.lower().strip()
            values_normalized = [v.lower().strip() for v in values]
            if key_normalized not in skill_equivalences:
                skill_equivalences[key_normalized] = values_normalized
            else:
                # Merge with existing values
                skill_equivalences[key_normalized].extend(values_normalized)
        
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
            # SIMPLIFIED: Only exact matches for multi-word skills to avoid false positives
            # e.g., "power bi" should NOT match "business intelligence" even though "bi" is in both
            if job_skill_normalized == candidate_skill_normalized:
                return True
            
            # For single-word skills, allow substring matching (e.g., "sql" in "postgresql")
            # But for multi-word, require exact match to avoid false positives
            job_words = job_skill_normalized.split()
            candidate_words = candidate_skill_normalized.split()
            
            if len(job_words) == 1 and len(candidate_words) == 1:
                # Both single word - allow substring matching
                if (job_skill_normalized in candidate_skill_normalized or
                    candidate_skill_normalized in job_skill_normalized):
                    return True
            
            # Check for skill equivalences (only if direct match failed)
            # First check if job skill has equivalents defined
            if job_skill_normalized in skill_equivalences:
                for equivalent in skill_equivalences[job_skill_normalized]:
                    equivalent_normalized = equivalent.lower().strip().replace('-', ' ').replace('_', ' ')
                    equivalent_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', equivalent_normalized).strip()
                    
                    # Check if equivalent matches candidate skill (exact match preferred)
                    if equivalent_normalized == candidate_skill_normalized:
                        return True
                    # Also check if equivalent is contained in candidate skill or vice versa
                    if len(equivalent_normalized) > 2 and len(candidate_skill_normalized) > 2:
                        if equivalent_normalized in candidate_skill_normalized or candidate_skill_normalized in equivalent_normalized:
                            return True
            
            # Also check reverse: if candidate skill has equivalents, check if job skill matches any equivalent
            if candidate_skill_normalized in skill_equivalences:
                for equivalent in skill_equivalences[candidate_skill_normalized]:
                    equivalent_normalized = equivalent.lower().strip().replace('-', ' ').replace('_', ' ')
                    equivalent_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', equivalent_normalized).strip()
                    
                    # Check if equivalent matches job skill (exact match preferred)
                    if equivalent_normalized == job_skill_normalized:
                        return True
                    # Also check if equivalent is contained in job skill or vice versa
                    if len(equivalent_normalized) > 2 and len(job_skill_normalized) > 2:
                        if equivalent_normalized in job_skill_normalized or job_skill_normalized in equivalent_normalized:
                            return True
                    
        # No match found
        return False
    
    def _check_equivalency_match(self, job_skill: str, candidate_skills: set) -> bool:
        """
        Check if a job skill matches any candidate skill via equivalency mappings.
        This checks both directions: job skill -> equivalent -> candidate skill AND candidate skill -> equivalent -> job skill.
        
        Args:
            job_skill: Job skill to match
            candidate_skills: Set of candidate skill names
            
        Returns:
            True if match found via equivalency, False otherwise
        """
        if not job_skill or not job_skill.strip():
            return False
        
        # Normalize job skill
        normalized_result = self.skill_normalizer.normalize(job_skill, fuzzy=True)
        job_skill_normalized = normalized_result.lower() if normalized_result else job_skill.lower().strip()
        job_skill_normalized = job_skill_normalized.replace('-', ' ').replace('_', ' ')
        job_skill_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_skill_normalized).strip()
        
        # Check if job skill has equivalents defined
        if job_skill_normalized in self.skill_equivalencies:
            equivalents = self.skill_equivalencies[job_skill_normalized]
            # Check if any candidate skill matches any equivalent
            for candidate_skill in candidate_skills:
                candidate_normalized = self._get_normalized_skill(candidate_skill)
                if not candidate_normalized:
                    candidate_normalized = candidate_skill.lower().strip()
                candidate_normalized = candidate_normalized.replace('-', ' ').replace('_', ' ')
                candidate_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', candidate_normalized).strip()
                
                # Check if candidate skill matches any equivalent
                for equivalent in equivalents:
                    equiv_normalized = equivalent.lower().strip().replace('-', ' ').replace('_', ' ')
                    equiv_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', equiv_normalized).strip()
                    
                    if equiv_normalized == candidate_normalized:
                        return True
                    # Also check substring match for variations
                    if equiv_normalized in candidate_normalized or candidate_normalized in equiv_normalized:
                        return True
        
        # Check reverse direction: if any candidate skill has equivalents, check if job skill matches any equivalent
        for candidate_skill in candidate_skills:
            candidate_normalized = self._get_normalized_skill(candidate_skill)
            if not candidate_normalized:
                candidate_normalized = candidate_skill.lower().strip()
            candidate_normalized = candidate_normalized.replace('-', ' ').replace('_', ' ')
            candidate_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', candidate_normalized).strip()
            
            if candidate_normalized in self.skill_equivalencies:
                equivalents = self.skill_equivalencies[candidate_normalized]
                # Check if job skill matches any equivalent
                for equivalent in equivalents:
                    equiv_normalized = equivalent.lower().strip().replace('-', ' ').replace('_', ' ')
                    equiv_normalized = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', equiv_normalized).strip()
                    
                    if equiv_normalized == job_skill_normalized:
                        return True
                    # Also check substring match for variations
                    if equiv_normalized in job_skill_normalized or job_skill_normalized in equiv_normalized:
                        return True
        
        return False
    
    def _find_exact_candidate_skill(self, job_skill: str, candidate_skills: set) -> str:
        """
        Find the exact candidate skill that matches a job skill.
        Returns the candidate skill name if found, empty string otherwise.
        
        Args:
            job_skill: Job skill to match
            candidate_skills: Set of candidate skill names
            
        Returns:
            Candidate skill name if exact match found, empty string otherwise
        """
        if not job_skill or not job_skill.strip():
            return ""
        
        # Normalize job skill
        job_skill_normalized = self._get_normalized_skill(job_skill)
        if not job_skill_normalized:
            job_skill_normalized = job_skill.lower().strip()
        
        job_skill_clean = job_skill_normalized.replace('-', ' ').replace('_', ' ')
        job_skill_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_skill_clean).strip()
        job_skill_lower = job_skill.lower().strip()
        
        # Check each candidate skill for exact match
        for candidate_skill in candidate_skills:
            candidate_normalized = self._get_normalized_skill(candidate_skill)
            if not candidate_normalized:
                candidate_normalized = candidate_skill.lower().strip()
            
            candidate_clean = candidate_normalized.replace('-', ' ').replace('_', ' ')
            candidate_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', candidate_clean).strip()
            candidate_lower = candidate_skill.lower().strip()
            
            # Exact match (case-insensitive, normalized)
            if job_skill_clean == candidate_clean:
                return candidate_skill
            
            # Also check if original names match (case-insensitive)
            if job_skill_lower == candidate_lower:
                return candidate_skill
            
            # Check if one is a substring of the other (e.g., "MS Access" vs "Microsoft MS Access")
            if job_skill_lower in candidate_lower or candidate_lower in job_skill_lower:
                # But only if they're very similar (to avoid false positives)
                job_words = set(job_skill_lower.split())
                candidate_words = set(candidate_lower.split())
                if job_words == candidate_words or (len(job_words) > 0 and job_words.issubset(candidate_words)) or (len(candidate_words) > 0 and candidate_words.issubset(job_words)):
                    return candidate_skill
        
        return ""
    
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
                # Use advanced SkillNormalizer
                normalized_result = self.skill_normalizer.normalize(skill, fuzzy=True)
                skill_normalized = normalized_result.lower() if normalized_result else ""
                if skill_normalized in job_desc_lower or self._is_partial_match(skill_normalized, job_desc_lower):
                    requirements[category].append(skill)
        
        return requirements
    
    def generate_preliminary_analysis(self, job_description: str) -> Dict[str, any]:
        """Generate preliminary analysis to reduce AI load"""
        
        # Find matches
        matches = self.find_skill_matches(job_description)
        
        # Extract requirements
        requirements = self.extract_job_requirements(job_description)
        
        # Extract technologies from JD once (to avoid duplicate extraction later)
        # This is cached in preliminary_analysis so enhanced_analyzer can reuse it
        extracted_technologies = self.tech_extractor.extract_technologies(job_description)
        
        # Generate summary
        analysis = {
            'preliminary_match_score': matches['match_score'],
            'exact_matches': matches['exact_matches'],
            'partial_matches': matches['partial_matches'],
            'missing_skills': matches['missing_skills'],
            'unmatched_job_skills': matches['unmatched_job_skills'],  # Include unmatched job skills
            'job_requirements': requirements,
            'extracted_job_technologies': extracted_technologies,  # Cache for reuse - avoid duplicate extraction
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
    
    def create_ai_prompt_context(self, job_description: str, preliminary_analysis: Optional[Dict] = None) -> str:
        """Create context for AI analysis based on preliminary matching"""
        
        # Use provided analysis or generate if not provided (backward compatibility)
        if preliminary_analysis is None:
            analysis = self.generate_preliminary_analysis(job_description)
        else:
            analysis = preliminary_analysis
        
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
            
            # Data Engineering - keep data pipeline separate as it's more specific
            'data pipeline': ['data pipeline', 'data pipelines'],
            'data engineering': ['data engineering', 'data engineering pipelines', 'data pipeline engineering'],
            'pipelines': ['pipelines', 'pipeline'],
            
            # Data Management (keep separate from metadata management)
            'data management': ['data management'],
            'metadata management': ['metadata management'],
            
            # Modeling - check data modeling first (more specific) before generic modeling
            'data modeling': ['data modeling'],
            'modeling': ['modeling', 'data models', 'modeling techniques'],
            
            # Communication
            'communication': ['communication', 'communication skills', 'excellent communication', 'strong communication', 'excellent communication skills', 'strong communication skills'],
            'communication skills': ['communication skills', 'communication', 'excellent communication skills', 'strong communication skills'],
            
            # Leadership and management
            'leadership': ['leadership', 'team leadership'],
            # Don't consolidate "Data Management", "Stakeholder Management", "Risk Management" into generic "management"
            # Only consolidate generic management terms
            'management': ['team management', 'project management'],
            'data management': ['data management'],
            'stakeholder management': ['stakeholder management'],
            'risk management': ['risk management'],
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
                    # Use exact match or word boundary matching to avoid false positives
                    # e.g., "metadata management" should NOT match "data management"
                    exact_match = (member_normalized == skill_normalized)
                    # For substring matching, require word boundaries to avoid partial matches
                    word_boundary_match = (
                        re.search(r'\b' + re.escape(member_normalized) + r'\b', skill_normalized) or
                        re.search(r'\b' + re.escape(skill_normalized) + r'\b', member_normalized)
                    )
                    
                    if exact_match or word_boundary_match:
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
    
    def _get_normalized_skill(self, skill: str) -> str:
        """Get normalized form of a skill (helper method)"""
        normalized_result = self.skill_normalizer.normalize(skill, fuzzy=True)
        return normalized_result.lower() if normalized_result else skill.lower()
    
    def _validate_skill_match(self, candidate_skill: str, candidate_normalized: str, 
                              job_skill: str, job_skill_normalized: str) -> bool:
        """
        Validate that a skill match is semantically valid.
        
        Prevents false positives where normalization creates spurious matches
        (e.g., "power-bi" -> "Business Intelligence" matching "Business Intelligence" requirement)
        
        Args:
            candidate_skill: Original candidate skill name (e.g., "power-bi")
            candidate_normalized: Normalized candidate skill (e.g., "business intelligence")
            job_skill: Original job skill name (e.g., "Business Intelligence")
            job_skill_normalized: Normalized job skill (e.g., "business intelligence")
        
        Returns:
            True if match is valid, False if it's a false positive
        """
        # Case 1: Normalized forms are identical - check if originals are related
        if candidate_normalized == job_skill_normalized:
            # Check if original names share significant words
            cand_lower = candidate_skill.lower().replace('-', ' ').replace('_', ' ')
            job_lower = job_skill.lower().replace('-', ' ').replace('_', ' ')
            
            cand_words = set(cand_lower.split())
            job_words = set(job_lower.split())
            
            # If they're identical, always valid
            if cand_lower == job_lower:
                return True
            
            # Check for substring relationship (e.g., "Airflow" in "Apache Airflow")
            if cand_lower in job_lower or job_lower in cand_lower:
                return True
            
            # Check word overlap - require at least 50% overlap
            if cand_words and job_words:
                overlap = len(cand_words & job_words)
                min_words = min(len(cand_words), len(job_words))
                if min_words > 0:
                    overlap_ratio = overlap / min_words
                    # If overlap is too low, it's likely a false match from normalization
                    # e.g., "power bi" vs "business intelligence" = 0% overlap
                    if overlap_ratio < 0.5:
                        return False
            
            return True
        
        # Case 2: Normalized forms differ - should not have matched in the first place
        return False
    
    def _find_matched_job_skill(self, candidate_skill: str, candidate_skill_normalized: str, job_skills: list) -> str:
        """Find which job skill matches a candidate skill (checks equivalencies too)"""
        # Normalize candidate skill for comparison
        candidate_normalized_clean = candidate_skill_normalized.replace('-', ' ').replace('_', ' ')
        candidate_normalized_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', candidate_normalized_clean).strip()
        
        # First pass: Check exact matches
        for job_skill in job_skills:
            # Use advanced SkillNormalizer
            normalized_result = self.skill_normalizer.normalize(job_skill, fuzzy=True)
            job_skill_normalized = normalized_result.lower() if normalized_result else job_skill.lower()
            job_skill_normalized_clean = job_skill_normalized.replace('-', ' ').replace('_', ' ')
            job_skill_normalized_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_skill_normalized_clean).strip()
            
            # Exact match (case-insensitive, normalized)
            if candidate_normalized_clean == job_skill_normalized_clean:
                return job_skill
        
        # Second pass: Check equivalencies
        # Combine hardcoded and loaded equivalencies
        skill_equivalences = {
            'aws lake formation': ['aws', 'lake formation', 'data lake', 'data warehousing'],
            'amazon kinesis': ['aws', 'kinesis', 'streaming', 'data streaming'],
            'insights': ['insight', 'analytics', 'data insights', 'business insights'],
        }
        for key, values in self.skill_equivalencies.items():
            key_normalized = key.lower().strip()
            values_normalized = [v.lower().strip() for v in values]
            if key_normalized not in skill_equivalences:
                skill_equivalences[key_normalized] = values_normalized
        
        # Check if candidate skill or its equivalents match any job skill
        for job_skill in job_skills:
            normalized_result = self.skill_normalizer.normalize(job_skill, fuzzy=True)
            job_skill_normalized = normalized_result.lower() if normalized_result else job_skill.lower()
            job_skill_normalized_clean = job_skill_normalized.replace('-', ' ').replace('_', ' ')
            job_skill_normalized_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_skill_normalized_clean).strip()
            
            # Check if candidate skill has equivalents that match job skill
            if candidate_normalized_clean in skill_equivalences:
                for equivalent in skill_equivalences[candidate_normalized_clean]:
                    equiv_clean = equivalent.replace('-', ' ').replace('_', ' ')
                    equiv_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', equiv_clean).strip()
                    if equiv_clean == job_skill_normalized_clean:
                        return job_skill
            
            # Check if job skill has equivalents that match candidate skill
            if job_skill_normalized_clean in skill_equivalences:
                for equivalent in skill_equivalences[job_skill_normalized_clean]:
                    equiv_clean = equivalent.replace('-', ' ').replace('_', ' ')
                    equiv_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', equiv_clean).strip()
                    if equiv_clean == candidate_normalized_clean:
                        return job_skill
        
        return ""
    
    def _find_exact_candidate_skill(self, job_skill: str, candidate_skills: set) -> Optional[str]:
        """Find the candidate skill that exactly matches a job skill (case-insensitive, normalized)"""
        job_skill_normalized = self._get_normalized_skill(job_skill)
        if not job_skill_normalized:
            return None
        
        job_skill_normalized_clean = job_skill_normalized.replace('-', ' ').replace('_', ' ')
        job_skill_normalized_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_skill_normalized_clean).strip()
        
        for candidate_skill in candidate_skills:
            candidate_normalized = self._get_normalized_skill(candidate_skill)
            if not candidate_normalized:
                continue
            candidate_normalized_clean = candidate_normalized.replace('-', ' ').replace('_', ' ')
            candidate_normalized_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', candidate_normalized_clean).strip()
            
            if candidate_normalized_clean == job_skill_normalized_clean:
                return candidate_skill
        
        return None
    
    def _add_match_if_not_duplicate(self, job_skill: str, candidate_skill: str, matches: dict):
        """Add a match to exact_matches or partial_matches if not already present"""
        # Check if already in exact_matches
        if any(m.get('job_skill', '').lower() == job_skill.lower() for m in matches['exact_matches']):
            return
        # Check if already in partial_matches
        if any(m.get('job_skill', '').lower() == job_skill.lower() for m in matches['partial_matches']):
            return
        
        # Determine if it's an exact match (normalized forms are identical)
        job_skill_normalized = self._get_normalized_skill(job_skill)
        candidate_skill_normalized = self._get_normalized_skill(candidate_skill)
        
        if job_skill_normalized and candidate_skill_normalized:
            job_clean = job_skill_normalized.replace('-', ' ').replace('_', ' ')
            job_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', job_clean).strip()
            cand_clean = candidate_skill_normalized.replace('-', ' ').replace('_', ' ')
            cand_clean = re.sub(r'\s+(skills?|experience|expertise|knowledge|proficiency)$', '', cand_clean).strip()
            
            if job_clean == cand_clean:
                # Exact match
                matches['exact_matches'].append({
                    'skill': candidate_skill,
                    'job_skill': job_skill,
                    'category': self.candidate_skills.get(candidate_skill, {}).get('category', 'Unknown'),
                    'source': self.candidate_skills.get(candidate_skill, {}).get('source', 'Unknown')
                })
            else:
                # Partial match
                matches['partial_matches'].append({
                    'skill': candidate_skill,
                    'job_skill': job_skill,
                    'category': self.candidate_skills.get(candidate_skill, {}).get('category', 'Unknown'),
                    'source': self.candidate_skills.get(candidate_skill, {}).get('source', 'Unknown')
                })

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
    
    from app.utils.message_logger import log_message
    analysis = matcher.generate_preliminary_analysis(sample_job)
    log_message(75, "Preliminary Analysis Results:")
    log_message(76, f"Match Score: {analysis['preliminary_match_score']}%")
    log_message(77, f"Exact Matches: {len(analysis['exact_matches'])}")
    log_message(78, f"Partial Matches: {len(analysis['partial_matches'])}")
    log_message(79, f"AI Focus Areas: {analysis['ai_focus_areas']}")
