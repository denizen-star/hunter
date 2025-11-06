#!/usr/bin/env python3
"""
Comprehensive Skill Extractor - Extracts all skills from resume using AI
"""
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from app.services.ai_analyzer import AIAnalyzer
from app.utils.file_utils import save_yaml, read_text_file, get_data_path


class SkillExtractor:
    """Extract comprehensive skills from resume using AI"""
    
    # Skill categories used in skills.yaml
    CATEGORIES = [
        "Programming Languages",
        "Cloud Platforms",
        "Data Platforms",
        "Business Intelligence",
        "Data Sources",
        "Domain Expertise",
        "Experience Areas",
        "Leadership",
        "Communication",
        "Strategic Thinking",
        "Problem Solving",
        "Project Management",
        "Product Management",
        "Data Engineering",
        "Data Analytics",
        "Data Science",
        "Certifications",
        "Tools & Technologies",
        "Soft Skills",
        "Technical Skills",
        "Business Acumen",
        "Observability",
        "Other Tools"
    ]
    
    def __init__(self, ai_analyzer: Optional[AIAnalyzer] = None):
        """Initialize skill extractor"""
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
        self.skills_yaml_path = get_data_path('resumes') / 'skills.yaml'
    
    def extract_skills_from_resume(self, resume_content: str) -> Dict:
        """Extract comprehensive skills from resume using AI"""
        
        prompt = f"""Extract ALL skills, technologies, tools, and competencies mentioned in the following resume. 
Be comprehensive and extract everything relevant including:
- Programming languages (Python, SQL, Java, etc.)
- Cloud platforms and services (AWS, Azure, GCP, etc.)
- Data platforms and databases (Snowflake, PostgreSQL, etc.)
- Business Intelligence tools (Tableau, Power BI, etc.)
- Data engineering tools (Spark, Airflow, etc.)
- Soft skills (Leadership, Communication, etc.)
- Domain expertise (Data Analytics, Product Management, etc.)
- Certifications (if mentioned)
- Experience areas (Agile, Scrum, MLOps, etc.)

RESUME:
{resume_content}

Please provide the skills in the following YAML format:

```yaml
skills:
  Skill Name:
    category: Category Name
    display_name: Skill Name
    variations_found:
    - variation1
    - variation2
    source: technical_skills|soft_skills|experience|certifications|domain_expertise
```

Categories to use:
- Programming Languages: For programming languages (Python, SQL, Java, etc.)
- Cloud Platforms: For cloud services (AWS, Azure, GCP, etc.)
- Data Platforms: For databases and data storage (Snowflake, PostgreSQL, etc.)
- Business Intelligence: For BI tools (Tableau, Power BI, Qlik, etc.)
- Data Sources: For data sources and integrations
- Domain Expertise: For domain knowledge (Data Analytics, Product Management, etc.)
- Experience Areas: For methodologies and practices (Agile, Scrum, MLOps, etc.)
- Leadership: For leadership skills
- Communication: For communication skills
- Strategic Thinking: For strategic planning and thinking
- Problem Solving: For problem-solving skills
- Project Management: For project management skills
- Product Management: For product management skills
- Data Engineering: For data engineering skills
- Data Analytics: For data analytics skills
- Data Science: For data science skills
- Certifications: For certifications and credentials
- Tools & Technologies: For other tools and technologies
- Soft Skills: For other soft skills
- Technical Skills: For other technical skills

IMPORTANT:
- Extract the skill name exactly as it appears in the resume (capitalization, etc.)
- For variations, include common lowercase versions and abbreviations
- Be thorough - extract ALL skills mentioned, not just the most obvious ones
- Group similar skills together (e.g., "AWS" and "Amazon Web Services" should be one skill with variations)
- Include skills mentioned in job descriptions, responsibilities, and achievements
- Include soft skills demonstrated through job titles and responsibilities (e.g., "Product Manager" implies "Product Management")

Return ONLY the YAML format, no additional text."""

        try:
            response = self.ai_analyzer._call_ollama(prompt)
            
            # Extract YAML from response (might be wrapped in markdown code blocks)
            yaml_content = None
            
            # Try to find YAML in code blocks
            yaml_match = re.search(r'```yaml\s*\n(.*?)\n```', response, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
            else:
                # Try without yaml tag
                yaml_match = re.search(r'```\s*\n(.*?)\n```', response, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                else:
                    # Try to find YAML-like structure (starts with skills:)
                    yaml_match = re.search(r'^skills:\s*\n(.*?)(?=\n##|\n```|$)', response, re.DOTALL | re.MULTILINE)
                    if yaml_match:
                        yaml_content = 'skills:\n' + yaml_match.group(1)
                    else:
                        # Last resort: look for skills: anywhere
                        if 'skills:' in response:
                            # Extract everything after skills:
                            start_idx = response.find('skills:')
                            yaml_content = response[start_idx:]
                            # Try to find a reasonable end point
                            end_markers = ['\n##', '\n```', '\n---', '\n\n\n']
                            for marker in end_markers:
                                if marker in yaml_content:
                                    yaml_content = yaml_content[:yaml_content.find(marker)]
                                    break
                        else:
                            yaml_content = response
            
            # Parse YAML
            extracted_data = yaml.safe_load(yaml_content)
            
            if not extracted_data or 'skills' not in extracted_data:
                print("⚠️ Warning: Could not extract skills from AI response, using fallback")
                return self._extract_skills_fallback(resume_content)
            
            skills = extracted_data['skills']
            
            # Clean and validate skills
            cleaned_skills = self._clean_and_validate_skills(skills)
            
            # IMPORTANT: Merge with fallback to ensure all technologies are included
            # AI might miss some technologies, so we supplement with rule-based extraction
            print("🔍 Merging AI-extracted skills with technology extraction...")
            fallback_data = self._extract_skills_fallback(resume_content)
            fallback_skills = fallback_data.get('skills', {})
            
            # Merge: AI skills take precedence, but add any missing technologies
            for tech_name, tech_info in fallback_skills.items():
                if tech_name not in cleaned_skills:
                    # Add missing technology from fallback
                    cleaned_skills[tech_name] = tech_info
                    print(f"   ➕ Added missing technology: {tech_name}")
            
            print(f"✅ Final merged skills: {len(cleaned_skills)} total")
            
            return {
                'extracted_at': datetime.now().isoformat(),
                'skills': cleaned_skills,
                'total_skills': len(cleaned_skills)
            }
            
        except Exception as e:
            print(f"⚠️ Error extracting skills with AI: {e}")
            print("Falling back to rule-based extraction...")
            return self._extract_skills_fallback(resume_content)
    
    def _extract_skills_fallback(self, resume_content: str) -> Dict:
        """Fallback: Extract skills using rule-based approach"""
        from app.utils.simple_tech_extractor import SimpleTechExtractor
        import re
        
        tech_extractor = SimpleTechExtractor()
        technologies = tech_extractor.extract_technologies(resume_content)
        
        skills = {}
        
        # Extract technologies
        for tech in technologies:
            category = self._categorize_skill(tech)
            skills[tech] = {
                'category': category,
                'display_name': tech,
                'variations_found': [tech.lower()],
                'source': 'technical_skills'
            }
        
        # CORE SKILLS EXTRACTION: Extract explicitly mentioned core skills from resume
        # Look for common patterns that indicate core skills
        resume_lower = resume_content.lower()
        
        # Core skill patterns to extract (these are explicitly mentioned in resume)
        core_skill_patterns = {
            'Business Intelligence': [
                r'\bbusiness intelligence\b',
                r'\bbi\b',  # But only in context of Business Intelligence
                r'business intelligence\s+&?\s+analytics',
                r'business intelligence\s+professional',
                r'business intelligence\s+analyst',
                r'business intelligence\s+manager',
                r'business intelligence\s+team',
            ],
            'Communication': [
                r'\bcommunication\s+skills?\b',
                r'\bexcellent\s+communication\b',
                r'\bstrong\s+communication\b',
                r'\bcommunication\s+and\s+presentation\b',
                r'\bverbal\s+and\s+written\s+communication\b',
                r'\bcommunication\b',  # Just "communication" if mentioned
            ],
            'Data Engineering': [
                r'\bdata\s+engineering\b',
                r'\bdata\s+engineer\b',
                r'\bdata\s+engineering\s+team\b',
                r'\bdata\s+engineering\s+pipelines\b',
                r'\bdata\s+engineers\b',  # Plural
            ],
            'Data Modeling': [
                r'\bdata\s+modeling\b',
                r'\bdata\s+models\b',
                r'\bmodeling\s+techniques\b',
            ],
            'Pipelines': [
                r'\bdata\s+pipelines?\b',
                r'\bpipelines?\b',  # But only in data/engineering context
                r'\betl\s+pipelines?\b',
            ],
            'Forecasting': [
                r'\bforecasting\b',
                r'\bforecast\b',
                r'\bforecasts\b',
            ],
            'Tableau': [
                r'\btableau\b',
                r'\btickableau\b',  # Common typo
            ],
            'Snowflake': [
                r'\bsnowflake\b',
            ],
            'Mentoring': [
                r'\bmentoring\b',
                r'\bmentor\b',
                r'\bmentored\b',
            ],
        }
        
        # Extract core skills using patterns
        for skill_name, patterns in core_skill_patterns.items():
            if skill_name not in skills:  # Only add if not already extracted
                for pattern in patterns:
                    if re.search(pattern, resume_lower):
                        category = self._categorize_skill(skill_name)
                        skills[skill_name] = {
                            'category': category,
                            'display_name': skill_name,
                            'variations_found': [skill_name.lower()],
                            'source': 'experience'
                        }
                        print(f"   ✅ Extracted core skill: {skill_name}")
                        break  # Found it, move to next skill
        
        # Also extract soft/conceptual skills from resume
        # Look for bullet points with skills (common resume format)
        lines = resume_content.split('\n')
        for line in lines:
            line = line.strip()
            # Check for bullet points (-, *, •, etc.)
            if re.match(r'^[-*•]\s+', line):
                skill_text = re.sub(r'^[-*•]\s+', '', line).strip()
                # Remove common prefixes
                skill_text = re.sub(r'^(Superior|Strong|Excellent|Advanced|Proficient|Experienced)\s+', '', skill_text, flags=re.IGNORECASE)
                skill_text = re.sub(r'\s+Skills?$', '', skill_text, flags=re.IGNORECASE)
                skill_text = skill_text.strip()
                
                # Skip if it's too short, too long, or looks like a sentence
                # But allow single-word skills and common skill patterns
                is_single_word = len(skill_text.split()) == 1
                is_common_pattern = any(pattern in skill_text.lower() for pattern in [
                    'visualization', 'storytelling', 'analysis', 'management', 'leadership',
                    'engineering', 'engineer', 'development', 'design', 'architecture',
                    'problem solving', 'strategic', 'planning', 'collaboration'
                ])
                
                # Check for stop words, but allow technical terms
                stop_words = ['years', 'experience', 'with', 'in', 'of', 'the', 'and', 'or']
                has_stop_words = any(word in skill_text.lower() for word in stop_words)
                
                # Allow if it's a valid skill pattern even with some stop words
                if (len(skill_text) > 2 and len(skill_text) < 50 and 
                    (not skill_text.endswith('.') or is_single_word) and 
                    (is_single_word or is_common_pattern or not has_stop_words)):
                    
                    # Categorize the skill
                    category = self._categorize_skill(skill_text)
                    
                    # Add if not already in skills (avoid duplicates)
                    if skill_text not in skills:
                        skills[skill_text] = {
                            'category': category,
                            'display_name': skill_text,
                            'variations_found': [skill_text.lower()],
                            'source': 'soft_skills' if category in ['Communication', 'Leadership', 'Problem Solving', 'Strategic Thinking'] else 'experience'
                        }
        
        # Also look for skills sections explicitly
        skills_section_pattern = r'(?:##|###)\s*(?:Skills|Technical Skills|Soft Skills|Core Competencies|Key Skills)[:]*\s*\n(.*?)(?=\n##|\n\n\n|$)'
        skills_match = re.search(skills_section_pattern, resume_content, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_section = skills_match.group(1)
            for line in skills_section.split('\n'):
                line = line.strip()
                # Extract skills from various formats
                if re.match(r'^[-*•]\s+', line):
                    skill_text = re.sub(r'^[-*•]\s+', '', line).strip()
                elif ':' in line and not line.startswith('**'):
                    # Format: "Category: skill1, skill2, skill3"
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        skill_list = [s.strip() for s in parts[1].split(',')]
                        for skill in skill_list:
                            skill = skill.strip()
                            if len(skill) > 3 and len(skill) < 50 and skill not in skills:
                                category = self._categorize_skill(skill)
                                skills[skill] = {
                                    'category': category,
                                    'display_name': skill,
                                    'variations_found': [skill.lower()],
                                    'source': 'soft_skills' if category in ['Communication', 'Leadership', 'Problem Solving', 'Strategic Thinking'] else 'experience'
                                }
        
        print(f"✅ Fallback extraction: Found {len(skills)} skills (technologies + soft skills)")
        return {
            'extracted_at': datetime.now().isoformat(),
            'skills': skills,
            'total_skills': len(skills)
        }
    
    def _clean_and_validate_skills(self, skills: Dict) -> Dict:
        """Clean and validate extracted skills"""
        cleaned = {}
        
        for skill_name, skill_data in skills.items():
            if not skill_name or len(skill_name.strip()) < 2:
                continue
            
            # Ensure required fields
            category = skill_data.get('category', 'Technical Skills')
            display_name = skill_data.get('display_name', skill_name)
            variations = skill_data.get('variations_found', [skill_name.lower()])
            source = skill_data.get('source', 'technical_skills')
            
            # Validate category
            if category not in self.CATEGORIES:
                # Try to map to a valid category
                category = self._categorize_skill(skill_name)
            
            # Ensure variations list
            if not variations:
                variations = [skill_name.lower()]
            elif skill_name.lower() not in variations:
                variations.insert(0, skill_name.lower())
            
            cleaned[skill_name] = {
                'category': category,
                'display_name': display_name,
                'variations_found': variations,
                'source': source
            }
        
        return cleaned
    
    def _categorize_skill(self, skill_name: str) -> str:
        """Categorize a skill based on its name"""
        skill_lower = skill_name.lower()
        
        # Core Skills - Check first (exact matches and common patterns)
        if skill_lower == 'business intelligence' or skill_lower.startswith('business intelligence'):
            return "Business Intelligence"
        if skill_lower in ['communication', 'communication skills']:
            return "Communication"
        if skill_lower in ['data engineering', 'data engineer']:
            return "Data Engineering"
        if skill_lower in ['data modeling', 'data models', 'modeling']:
            return "Data Analytics"
        if skill_lower in ['pipelines', 'data pipelines', 'data pipeline']:
            return "Data Engineering"
        if skill_lower in ['forecasting', 'forecast']:
            return "Data Analytics"
        if skill_lower in ['tableau', 'tickableau']:
            return "Business Intelligence"
        if skill_lower in ['snowflake']:
            return "Data Platforms"
        if skill_lower in ['mentoring', 'mentor']:
            return "Leadership"
        
        # Communication & Storytelling (check early)
        if any(comm in skill_lower for comm in ['communication', 'storytelling', 'story telling', 'presentation', 'public speaking', 'writing']):
            return "Communication"
        
        # Data Visualization (check before other data skills)
        if any(dv in skill_lower for dv in ['data visualization', 'visualization', 'visualisation', 'data viz']):
            return "Data Analytics"  # Group with Data Analytics
        
        # Programming Languages
        if any(lang in skill_lower for lang in ['python', 'sql', 'java', 'scala', 'r ', 'javascript', 'typescript', 'go', 'rust', 'c++', 'c#']):
            return "Programming Languages"
        
        # Cloud Platforms
        if any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'google cloud', 'amazon web services', 'docker', 'kubernetes', 'terraform']):
            return "Cloud Platforms"
        
        # Data Platforms
        if any(db in skill_lower for db in ['snowflake', 'postgresql', 'mysql', 'mongodb', 'redis', 'oracle', 'data warehouse', 'data lake', 'databricks']):
            return "Data Platforms"
        
        # Business Intelligence
        if any(bi in skill_lower for bi in ['tableau', 'power bi', 'looker', 'qlik', 'business intelligence', 'bi ', 'business objects']):
            return "Business Intelligence"
        
        # Data Engineering
        if any(de in skill_lower for de in ['spark', 'airflow', 'etl', 'data pipeline', 'data engineering', 'kafka', 'hadoop']):
            return "Data Engineering"
        
        # Leadership
        if any(lead in skill_lower for lead in ['leadership', 'managing', 'team management', 'director', 'manager', 'lead']):
            return "Leadership"
        
        # Product Management
        if any(pm in skill_lower for pm in ['product management', 'product manager', 'roadmap', 'product strategy']):
            return "Product Management"
        
        # Project Management
        if any(pm in skill_lower for pm in ['project management', 'agile', 'scrum', 'kanban']):
            return "Project Management"
        
        # Certifications
        if any(cert in skill_lower for cert in ['certified', 'certification', 'certificate', 'pmp', 'aws certified']):
            return "Certifications"
        
        # Default
        return "Technical Skills"
    
    def save_skills_to_yaml(self, skills_data: Dict) -> None:
        """Save extracted skills to skills.yaml"""
        from app.utils.file_utils import ensure_dir_exists
        ensure_dir_exists(self.skills_yaml_path.parent)
        save_yaml(skills_data, self.skills_yaml_path)
        print(f"✅ Saved {skills_data['total_skills']} skills to {self.skills_yaml_path}")
    
    def extract_and_save_skills(self, resume_content: str) -> Dict:
        """Extract skills from resume and save to skills.yaml"""
        print("🔍 Extracting comprehensive skills from resume using AI...")
        print(f"   Resume length: {len(resume_content)} characters")
        try:
            skills_data = self.extract_skills_from_resume(resume_content)
            if skills_data and skills_data.get('total_skills', 0) > 0:
                self.save_skills_to_yaml(skills_data)
                print(f"✅ Extraction complete: {skills_data['total_skills']} skills found")
            else:
                print("⚠️ Warning: No skills extracted")
            return skills_data
        except Exception as e:
            print(f"❌ Error during skill extraction: {e}")
            import traceback
            traceback.print_exc()
            raise

