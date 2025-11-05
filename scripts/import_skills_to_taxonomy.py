#!/usr/bin/env python3
"""
Import skills from existing sources into the new normalization taxonomy.
Combines data from:
- app/utils/simple_tech_extractor.py (TECHNOLOGIES dictionary)
- data/resumes/skills.yaml
- Jobdescr-General Skils.md
"""

import sys
import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from existing systems
from app.utils.simple_tech_extractor import SimpleTechExtractor
from app.utils.file_utils import read_text_file

# Paths
TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "config" / "skill_normalization.yaml"
SKILLS_YAML_PATH = Path(__file__).parent.parent / "data" / "resumes" / "skills.yaml"
JOB_SKILLS_PATH = Path(__file__).parent.parent / "Jobdescr-General Skils.md"


def load_tech_extractor():
    """Load technologies from SimpleTechExtractor."""
    extractor = SimpleTechExtractor()
    return extractor.TECHNOLOGIES


def load_skills_yaml():
    """Load skills from skills.yaml."""
    with open(SKILLS_YAML_PATH, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('skills', {})


def load_job_skills():
    """Extract skills from Jobdescr-General Skils.md."""
    try:
        content = read_text_file(JOB_SKILLS_PATH)
        
        # Parse markdown format
        skills_by_category = {
            'Technical Skills': [],
            'Soft Skills': [],
            'Tools Technologies': [],
            'Experience Requirements': [],
            'Education Certifications': []
        }
        
        current_category = None
        for line in content.split('\n'):
            line = line.strip()
            
            # Detect category headers
            if line.startswith('## Technical Skills'):
                current_category = 'Technical Skills'
            elif line.startswith('## Soft Skills'):
                current_category = 'Soft Skills'
            elif line.startswith('## Tools Technologies'):
                current_category = 'Tools Technologies'
            elif line.startswith('## Experience Requirements'):
                current_category = 'Experience Requirements'
            elif line.startswith('## Education Certifications'):
                current_category = 'Education Certifications'
            elif line.startswith('- ') and current_category:
                skill = line[2:].strip()
                if skill and skill not in skills_by_category[current_category]:
                    skills_by_category[current_category].append(skill)
        
        return skills_by_category
    except Exception as e:
        print(f"Warning: Could not load job skills: {e}")
        return {}


def map_category(old_category: str) -> str:
    """Map old categories to new taxonomy categories."""
    mappings = {
        'Programming Languages': 'Programming Languages',
        'Cloud Platforms': 'Cloud Platforms',
        'Data Platforms': 'Databases',
        'Business Intelligence': 'Business Intelligence',
        'Data Sources': 'Data Sources',
        'Technical Skills': 'Technical Skills',
        'Soft Skills': 'Soft Skills',
        'Tools Technologies': 'Tools & Technologies',
        'Experience Requirements': 'Experience Areas',
        'Education Certifications': 'Certifications',
        'Domain Expertise': 'Domain Expertise',
        'Leadership': 'Leadership'
    }
    return mappings.get(old_category, 'Other')


def normalize_for_alias(text: str) -> str:
    """Normalize text for use as alias."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove common prefixes/suffixes that shouldn't be in aliases
    text = re.sub(r'^(experience with|knowledge of|proficiency in)\s+', '', text)
    text = re.sub(r'\s+(experience|knowledge|skills)$', '', text)
    
    return text.strip()


def build_combined_skills():
    """Build comprehensive skill taxonomy from all sources."""
    
    print("📦 Loading skills from all sources...")
    
    # Load from TECH extractor
    tech_dict = load_tech_extractor()
    print(f"  ✓ Loaded {len(tech_dict)} skills from SimpleTechExtractor")
    
    # Load from skills.yaml
    skills_yaml = load_skills_yaml()
    print(f"  ✓ Loaded {len(skills_yaml)} skills from skills.yaml")
    
    # Load from job skills
    job_skills = load_job_skills()
    total_job_skills = sum(len(skills) for skills in job_skills.values())
    print(f"  ✓ Loaded {total_job_skills} skills from job descriptions")
    
    # Combine all skills
    combined = {}
    
    # Process TECH extractor (highest priority - has aliases)
    for canonical, aliases in tech_dict.items():
        # Clean canonical name
        canonical = canonical.replace("'", "").replace('"', '')
        
        if canonical not in combined:
            combined[canonical] = {
                'canonical': canonical,
                'aliases': [],
                'categories': set(),
                'sources': []
            }
        
        # Add aliases
        for alias in aliases:
            # Handle regex patterns
            if isinstance(alias, str) and not alias.startswith(r'\b'):
                normalized_alias = normalize_for_alias(alias)
                if normalized_alias and normalized_alias not in combined[canonical]['aliases']:
                    combined[canonical]['aliases'].append(normalized_alias)
        
        # Determine category
        canonical_lower = canonical.lower()
        if any(kw in canonical_lower for kw in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform']):
            combined[canonical]['categories'].add('Cloud Platforms')
        elif any(kw in canonical_lower for kw in ['python', 'java', 'sql', 'javascript', 'typescript', 'go', 'rust']):
            combined[canonical]['categories'].add('Programming Languages')
        elif any(kw in canonical_lower for kw in ['tableau', 'looker', 'power', 'qlik', 'cognos']):
            combined[canonical]['categories'].add('Business Intelligence')
        elif any(kw in canonical_lower for kw in ['postgresql', 'mysql', 'oracle', 'mongodb', 'redis', 'snowflake', 'redshift']):
            combined[canonical]['categories'].add('Databases')
        elif any(kw in canonical_lower for kw in ['apache', 'kafka', 'spark', 'airflow', 'dbt', 'fivetran']):
            combined[canonical]['categories'].add('Data Engineering')
        elif any(kw in canonical_lower for kw in ['data warehouse', 'data lake', 'data mesh']):
            combined[canonical]['categories'].add('Data Architecture')
        
        combined[canonical]['sources'].append('TECH')
    
    # Process skills.yaml (medium priority - has categories)
    for skill_name, skill_data in skills_yaml.items():
        if skill_name not in combined:
            combined[skill_name] = {
                'canonical': skill_name,
                'aliases': [],
                'categories': set(),
                'sources': []
            }
        
        # Add aliases
        for var in skill_data.get('variations_found', []):
            normalized_alias = normalize_for_alias(var)
            if normalized_alias and normalized_alias not in combined[skill_name]['aliases']:
                combined[skill_name]['aliases'].append(normalized_alias)
        
        # Add category
        old_category = skill_data.get('category', '')
        new_category = map_category(old_category)
        if new_category:
            combined[skill_name]['categories'].add(new_category)
        
        combined[skill_name]['sources'].append('skills.yaml')
    
    # Process job skills (lower priority - just names)
    for category, skills in job_skills.items():
        mapped_category = map_category(category)
        
        for skill_name in skills:
            # Skip if too long or contains special formatting
            if len(skill_name) > 100 or ':' in skill_name or skill_name.startswith('None'):
                continue
            
            # Clean name
            skill_name = skill_name.replace("'", "").replace('"', '').strip()
            
            if not skill_name:
                continue
            
            if skill_name not in combined:
                combined[skill_name] = {
                    'canonical': skill_name,
                    'aliases': [],
                    'categories': set(),
                    'sources': []
                }
            
            combined[skill_name]['categories'].add(mapped_category)
            combined[skill_name]['sources'].append('job_skills')
    
    print(f"\n✅ Combined {len(combined)} unique skills")
    
    return combined


def generate_taxonomy_yaml(combined_skills: Dict):
    """Generate the taxonomy YAML structure."""
    
    print("\n📝 Generating taxonomy structure...")
    
    # Deduplicate similar skills (e.g., Power BI vs PowerBI)
    print("  🔍 Deduplicating similar skills...")
    normalized_names = {}  # normalized -> preferred canonical
    
    for canonical, skill_data in combined_skills.items():
        # Normalize skill name for comparison (remove spaces, lowercase)
        normalized = ''.join(canonical.lower().split())
        
        if normalized in normalized_names:
            # We have a duplicate - choose the better one
            existing = normalized_names[normalized]
            # Prefer the one with more aliases or from TECH source
            if len(skill_data.get('aliases', [])) > len(combined_skills[existing].get('aliases', [])):
                normalized_names[normalized] = canonical
                print(f"    Choosing '{canonical}' over '{existing}'")
        else:
            normalized_names[normalized] = canonical
    
    # Filter combined_skills to only include preferred versions
    deduplicated = {}
    for canonical, skill_data in combined_skills.items():
        normalized = ''.join(canonical.lower().split())
        if normalized_names[normalized] == canonical:
            deduplicated[canonical] = skill_data
    
    print(f"  ✓ Reduced from {len(combined_skills)} to {len(deduplicated)} skills")
    
    # Sort skills alphabetically
    sorted_skills = sorted(deduplicated.items())
    
    # Build YAML structure
    yaml_structure = {
        'skills': {},
        'categories': {
            'Programming Languages': {
                'parent': 'Technical Skills',
                'description': 'Programming and scripting languages',
                'examples': []
            },
            'Databases': {
                'parent': 'Technical Skills',
                'description': 'Database systems and data storage',
                'examples': []
            },
            'Cloud Platforms': {
                'parent': 'Technical Skills',
                'description': 'Cloud infrastructure and services',
                'examples': []
            },
            'Business Intelligence': {
                'parent': 'Technical Skills',
                'description': 'BI tools and platforms',
                'examples': []
            },
            'Data Engineering': {
                'parent': 'Technical Skills',
                'description': 'Data pipeline and orchestration tools',
                'examples': []
            },
            'Data Architecture': {
                'parent': 'Domain Expertise',
                'description': 'Data architecture concepts',
                'examples': []
            },
            'Leadership': {
                'parent': 'Soft Skills',
                'description': 'Leadership and management capabilities',
                'examples': []
            },
            'Domain Expertise': {
                'parent': 'Soft Skills',
                'description': 'Domain-specific knowledge',
                'examples': []
            },
            'Experience Areas': {
                'parent': 'Soft Skills',
                'description': 'Work experience and responsibilities',
                'examples': []
            },
            'Soft Skills': {
                'parent': None,
                'description': 'Interpersonal and professional skills',
                'examples': []
            },
            'Technical Skills': {
                'parent': None,
                'description': 'Technical knowledge and capabilities',
                'examples': []
            }
        },
        'fuzzy_rules': {
            'similarity_threshold': 0.85,
            'word_replacements': [
                ['aws', 'amazon web services'],
                ['bi', 'business intelligence'],
                ['sql', 'structured query language'],
                ['etl', 'extract transform load'],
                ['api', 'application programming interface']
            ],
            'ignore_punctuation': True,
            'ignore_whitespace': True,
            'strip_prefixes': [
                'microsoft',
                'amazon',
                'apache'
            ],
            'strip_suffixes': [
                'experience',
                'knowledge',
                'skills',
                'expertise',
                'proficiency'
            ]
        },
        'metadata': {
            'version': '1.0',
            'last_updated': '2025-11-01',
            'total_skills': 0,
            'total_aliases': 0,
            'notes': 'Auto-generated from existing skill sources'
        }
    }
    
    # Process each skill
    for canonical, skill_data in sorted_skills:
        # Determine primary category
        categories = skill_data['categories']
        primary_category = 'Other'
        
        if categories:
            # Prefer technical categories
            technical_precedence = [
                'Programming Languages',
                'Cloud Platforms',
                'Databases',
                'Business Intelligence',
                'Data Engineering'
            ]
            
            for preferred in technical_precedence:
                if preferred in categories:
                    primary_category = preferred
                    break
            
            if primary_category == 'Other':
                primary_category = list(categories)[0]
        
        # Add to YAML
        yaml_structure['skills'][canonical] = {
            'canonical': canonical,
            'aliases': sorted(list(set(skill_data['aliases']))),
            'category': primary_category,
            'tags': list(skill_data['sources']) + [cat.lower().replace(' ', '-') for cat in categories]
        }
        
        # Track in category examples
        if primary_category in yaml_structure['categories']:
            if canonical not in yaml_structure['categories'][primary_category]['examples']:
                yaml_structure['categories'][primary_category]['examples'].append(canonical)
    
    # Add relationships (AWS hierarchy)
    yaml_structure['skills']['relationships'] = {
        'AWS': [
            'Amazon Kinesis',
            'AWS Lake Formation',
            'AWS Redshift'
        ]
    }
    
    # Count stats
    total_aliases = sum(len(skill.get('aliases', [])) for name, skill in yaml_structure['skills'].items() if name != 'relationships')
    yaml_structure['metadata']['total_skills'] = len([k for k in yaml_structure['skills'].keys() if k != 'relationships'])
    yaml_structure['metadata']['total_aliases'] = total_aliases
    
    print(f"  ✓ Generated {yaml_structure['metadata']['total_skills']} skills")
    print(f"  ✓ Generated {total_aliases} aliases")
    
    return yaml_structure


def save_taxonomy(yaml_structure: Dict, output_path: Path):
    """Save taxonomy to YAML file."""
    print(f"\n💾 Saving to {output_path.name}...")
    
    # BACKUP: Save existing file if it exists
    if output_path.exists():
        import shutil
        from datetime import datetime
        backup_path = output_path.parent / f"{output_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        shutil.copy2(output_path, backup_path)
        print(f"  ⚠️  Backed up existing file to: {backup_path.name}")
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write YAML with nice formatting
    with open(output_path, 'w') as f:
        f.write("# Skill Normalization Taxonomy Configuration\n")
        f.write("# Auto-generated from existing skill sources\n")
        f.write("# Last Updated: 2025-11-01\n")
        f.write("# Version: 1.0\n\n")
        
        f.write("# Define canonical skill names and their aliases\n")
        f.write("skills:\n")
        
        for canonical, skill_data in sorted(yaml_structure['skills'].items()):
            if canonical == 'relationships':
                continue
            
            # Quote key if it contains special YAML characters
            special_chars = [':', '"', "'", '[', ']', '+', '#', '@', '`', '|', '>']
            needs_quotes = any(char in canonical for char in special_chars) or canonical.startswith('!')
            
            if needs_quotes:
                f.write(f"  \"{canonical}\":\n")
            else:
                f.write(f"  {canonical}:\n")
            
            # Quote value if needed
            if needs_quotes:
                f.write(f"    canonical: \"{canonical}\"\n")
            else:
                f.write(f"    canonical: {canonical}\n")
            
            if skill_data.get('aliases'):
                f.write("    aliases:\n")
                for alias in skill_data['aliases']:
                    f.write(f"      - {alias}\n")
            
            if skill_data.get('category'):
                f.write(f"    category: {skill_data['category']}\n")
            
            if skill_data.get('tags'):
                f.write("    tags: {}\n".format([str(tag) for tag in skill_data['tags']]))
            
            f.write("\n")
        
        # Write relationships
        f.write("  # Relationship mapping for composite skills\n")
        f.write("  relationships:\n")
        rels = yaml_structure['skills'].get('relationships', {})
        if rels:
            f.write("    # Hierarchical relationships (parent -> children)\n")
            for parent, children in rels.items():
                f.write(f"    {parent}:\n")
                for child in children:
                    f.write(f"      - {child}\n")
                f.write("\n")
        
        # Write categories
        f.write("\n# Category mappings\n")
        f.write("categories:\n")
        for cat_name, cat_data in sorted(yaml_structure['categories'].items()):
            f.write(f"  {cat_name}:\n")
            if cat_data.get('parent'):
                f.write(f"    parent: {cat_data['parent']}\n")
            if cat_data.get('description'):
                f.write(f"    description: {cat_data['description']}\n")
            if cat_data.get('examples'):
                f.write("    examples: {}\n".format([str(ex) for ex in cat_data['examples'][:5]]))
            f.write("\n")
        
        # Write fuzzy rules
        f.write("\n# Fuzzy matching rules\n")
        f.write("fuzzy_rules:\n")
        for key, value in yaml_structure['fuzzy_rules'].items():
            if isinstance(value, bool):
                f.write(f"  {key}: {str(value).lower()}\n")
            elif isinstance(value, (int, float)):
                f.write(f"  {key}: {value}\n")
            elif isinstance(value, list):
                f.write(f"  {key}:\n")
                for item in value:
                    if isinstance(item, list):
                        f.write("    - {}\n".format(item))
                    else:
                        f.write(f"    - {item}\n")
        
        # Write metadata
        f.write("\n# Debug and validation\n")
        f.write("metadata:\n")
        for key, value in yaml_structure['metadata'].items():
            if key == 'notes':
                f.write(f"  {key}: |\n")
                for line in str(value).split('\n'):
                    f.write(f"    {line}\n")
            else:
                f.write(f"  {key}: {value}\n")
    
    print(f"  ✅ Saved successfully")


def main():
    """Main import process."""
    print("=" * 70)
    print("Import Skills to Normalization Taxonomy")
    print("=" * 70)
    print()
    
    # SAFETY CHECK: Warn if file exists and hasn't been explicitly overridden
    if TAXONOMY_PATH.exists() and not os.environ.get('FORCE_IMPORT'):
        print("⚠️  WARNING: Taxonomy file already exists!")
        print()
        print("This script will OVERWRITE any manual edits you've made.")
        print()
        print("To continue:")
        print("  export FORCE_IMPORT=1")
        print("  python3 scripts/import_skills_to_taxonomy.py")
        print()
        print("Otherwise, just edit data/config/skill_normalization.yaml directly.")
        return
    
    # Build combined skills
    combined_skills = build_combined_skills()
    
    # Generate taxonomy YAML
    yaml_structure = generate_taxonomy_yaml(combined_skills)
    
    # Save to file
    save_taxonomy(yaml_structure, TAXONOMY_PATH)
    
    print()
    print("=" * 70)
    print("✅ Import Complete!")
    print("=" * 70)
    print()
    print(f"Taxonomy saved to: {TAXONOMY_PATH}")
    print(f"Total skills: {yaml_structure['metadata']['total_skills']}")
    print(f"Total aliases: {yaml_structure['metadata']['total_aliases']}")
    print()
    print("Next step: Test the normalizer with real data")
    print()


if __name__ == "__main__":
    main()

