"""
Advanced Skill Normalization Service
Supports configurable taxonomy, aliases, and fuzzy matching
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from difflib import SequenceMatcher


class SkillNormalizer:
    """
    Advanced skill normalization with configurable taxonomy support.
    
    Features:
    - Canonical name mapping via aliases
    - Hierarchical category structure
    - Relationship mapping (parent/child, equivalence)
    - Fuzzy matching with configurable thresholds
    - Configurable prefix/suffix removal
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the normalizer with configuration.
        
        Args:
            config_path: Path to skill_normalization.yaml config file
        """
        if config_path is None:
            # Default config path
            config_path = Path(__file__).parent.parent.parent / "data" / "config" / "skill_normalization.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.alias_map = self._build_alias_map()
        self.canonical_names = set(self.config.get('skills', {}).keys())
        self.similarity_threshold = self.config.get('fuzzy_rules', {}).get('similarity_threshold', 0.85)
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config or {}
    
    def _build_alias_map(self) -> Dict[str, str]:
        """
        Build reverse mapping from aliases to canonical names.
        
        Returns:
            Dictionary mapping alias -> canonical name
        """
        alias_map = {}
        skills = self.config.get('skills', {})
        
        for canonical_name, skill_data in skills.items():
            # Skip special keys like 'relationships'
            if canonical_name == 'relationships':
                continue
            
            # Ensure skill_data is a dictionary
            if not isinstance(skill_data, dict):
                continue
            
            # Add canonical name mapping to itself
            alias_map[canonical_name.lower()] = canonical_name
            
            # Add aliases
            aliases = skill_data.get('aliases', [])
            if isinstance(aliases, list):
                for alias in aliases:
                    if isinstance(alias, str):
                        alias_map[alias.lower()] = canonical_name
            
            # Also normalize the canonical name
            normalized_canonical = self._normalize_string(canonical_name)
            if normalized_canonical != canonical_name.lower():
                alias_map[normalized_canonical] = canonical_name
        
        return alias_map
    
    def _normalize_string(self, text: str) -> str:
        """
        Normalize string for comparison.
        
        Args:
            text: Input text
            
        Returns:
            Normalized string
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove punctuation if configured
        fuzzy_rules = self.config.get('fuzzy_rules', {})
        if fuzzy_rules.get('ignore_punctuation', True):
            text = re.sub(r'[^\w\s-]', '', text)
        
        # Normalize whitespace
        if fuzzy_rules.get('ignore_whitespace', True):
            text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _apply_word_replacements(self, text: str) -> str:
        """Apply configured word replacements."""
        replacements = self.config.get('fuzzy_rules', {}).get('word_replacements', [])
        
        for old_word, new_word in replacements:
            # Replace whole words only
            pattern = r'\b' + re.escape(old_word) + r'\b'
            text = re.sub(pattern, new_word, text, flags=re.IGNORECASE)
        
        return text
    
    def _strip_prefixes_suffixes(self, text: str) -> str:
        """Remove configured prefixes and suffixes."""
        fuzzy_rules = self.config.get('fuzzy_rules', {})
        
        # Strip prefixes
        prefixes = fuzzy_rules.get('strip_prefixes', [])
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Strip suffixes
        suffixes = fuzzy_rules.get('strip_suffixes', [])
        for suffix in suffixes:
            if text.endswith(suffix):
                text = text[:-len(suffix)].strip()
        
        return text
    
    def normalize(self, skill_name: str, fuzzy: bool = True) -> Optional[str]:
        """
        Normalize a skill name to its canonical form.
        
        Args:
            skill_name: Input skill name
            fuzzy: Enable fuzzy matching if exact match not found
            
        Returns:
            Canonical name if found, None otherwise
        """
        # Early return for empty input
        if not skill_name or not skill_name.strip():
            return None
        
        # Normalize the input
        normalized_input = self._normalize_string(skill_name)
        
        # Try exact match in alias map FIRST (before word replacements)
        if normalized_input in self.alias_map:
            return self.alias_map[normalized_input]
        
        # Try stripping prefixes/suffixes
        stripped_input = self._strip_prefixes_suffixes(normalized_input)
        if stripped_input != normalized_input and stripped_input in self.alias_map:
            return self.alias_map[stripped_input]
        
        # Apply word replacements for fuzzy matching (e.g., "bi" -> "business intelligence")
        expanded_input = self._apply_word_replacements(stripped_input)
        
        # Try exact match with expanded input
        if expanded_input != stripped_input and expanded_input in self.alias_map:
            return self.alias_map[expanded_input]
        
        # Fuzzy matching if enabled
        if fuzzy:
            result = self._fuzzy_match(expanded_input)
            if result:
                return result
        
        return None
    
    def _fuzzy_match(self, text: str) -> Optional[str]:
        """
        Find best fuzzy match for text.
        
        Args:
            text: Normalized input text
            
        Returns:
            Canonical name if similarity above threshold, None otherwise
        """
        best_match = None
        best_score = 0.0
        
        # Compare against all aliases
        for alias, canonical in self.alias_map.items():
            # Skip if already tested exact
            if alias == text:
                continue
            
            # Calculate similarity score
            score = SequenceMatcher(None, text, alias).ratio()
            
            if score > best_score:
                best_score = score
                best_match = canonical
        
        # Return only if above threshold
        if best_score >= self.similarity_threshold:
            return best_match
        
        return None
    
    def get_category(self, canonical_name: str) -> Optional[str]:
        """
        Get category for a canonical skill name.
        
        Args:
            canonical_name: Canonical skill name
            
        Returns:
            Category name or None
        """
        skill_data = self.config.get('skills', {}).get(canonical_name, {})
        return skill_data.get('category')
    
    def get_tags(self, canonical_name: str) -> List[str]:
        """
        Get tags for a canonical skill name.
        
        Args:
            canonical_name: Canonical skill name
            
        Returns:
            List of tags
        """
        skill_data = self.config.get('skills', {}).get(canonical_name, {})
        return skill_data.get('tags', [])
    
    def get_parent(self, canonical_name: str) -> Optional[str]:
        """
        Get parent skill (for hierarchical relationships).
        
        Args:
            canonical_name: Canonical skill name
            
        Returns:
            Parent canonical name or None
        """
        skill_data = self.config.get('skills', {}).get(canonical_name, {})
        return skill_data.get('parent')
    
    def get_children(self, canonical_name: str) -> List[str]:
        """
        Get child skills (for hierarchical relationships).
        
        Args:
            canonical_name: Canonical skill name
            
        Returns:
            List of child canonical names
        """
        relationships = self.config.get('skills', {}).get('relationships', {})
        return relationships.get(canonical_name, [])
    
    def are_equivalent(self, skill1: str, skill2: str) -> bool:
        """
        Check if two skills are equivalent.
        
        Args:
            skill1: First skill name
            skill2: Second skill name
            
        Returns:
            True if equivalent, False otherwise
        """
        # Normalize both
        canonical1 = self.normalize(skill1, fuzzy=False)
        canonical2 = self.normalize(skill2, fuzzy=False)
        
        # Check if same canonical
        if canonical1 and canonical2 and canonical1 == canonical2:
            return True
        
        # Check equivalence rules
        equivalences = self.config.get('skills', {}).get('relationships', {}).get('equivalences', [])
        for eq_pair in equivalences:
            if len(eq_pair) >= 2:
                eq1 = self.normalize(eq_pair[0], fuzzy=False)
                eq2 = self.normalize(eq_pair[1], fuzzy=False)
                if ((canonical1 == eq1 and canonical2 == eq2) or 
                    (canonical1 == eq2 and canonical2 == eq1)):
                    return True
        
        return False
    
    def is_parent_of(self, parent: str, child: str) -> bool:
        """
        Check hierarchical relationship.
        
        Args:
            parent: Parent skill name
            child: Child skill name
            
        Returns:
            True if parent -> child relationship exists
        """
        parent_canonical = self.normalize(parent, fuzzy=False)
        child_canonical = self.normalize(child, fuzzy=False)
        
        if not parent_canonical or not child_canonical:
            return False
        
        # Check direct parent
        child_data = self.config.get('skills', {}).get(child_canonical, {})
        if child_data.get('parent') == parent_canonical:
            return True
        
        # Check relationships section
        children = self.get_children(parent_canonical)
        return child_canonical in children
    
    def batch_normalize(self, skill_names: List[str], fuzzy: bool = True) -> Dict[str, Optional[str]]:
        """
        Normalize a list of skills efficiently.
        
        Args:
            skill_names: List of skill names
            fuzzy: Enable fuzzy matching
            
        Returns:
            Dictionary mapping original -> canonical
        """
        return {skill: self.normalize(skill, fuzzy=fuzzy) for skill in skill_names}
    
    def add_skill(self, canonical_name: str, aliases: List[str], 
                  category: Optional[str] = None, tags: Optional[List[str]] = None,
                  parent: Optional[str] = None) -> None:
        """
        Add a new skill to the taxonomy (runtime modification).
        Note: Does not persist to config file.
        
        Args:
            canonical_name: Canonical name for the skill
            aliases: List of aliases
            category: Category assignment
            tags: List of tags
            parent: Parent skill for hierarchical relationship
        """
        # Add to config
        if 'skills' not in self.config:
            self.config['skills'] = {}
        
        self.config['skills'][canonical_name] = {
            'canonical': canonical_name,
            'aliases': aliases,
            'category': category,
            'tags': tags or [],
            'parent': parent
        }
        
        # Rebuild alias map
        self.alias_map = self._build_alias_map()
        self.canonical_names.add(canonical_name)
    
    def save_config(self, output_path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            output_path: Optional custom output path
        """
        output_path = output_path or self.config_path
        
        # Update metadata
        skills_dict = self.config.get('skills', {})
        
        # Calculate stats
        total_skills = len([k for k in skills_dict.keys() if k != 'relationships'])
        total_aliases = sum(len(s.get('aliases', [])) for k, s in skills_dict.items() if k != 'relationships')
        
        if 'metadata' not in self.config:
            self.config['metadata'] = {}
        
        self.config['metadata']['total_skills'] = total_skills
        self.config['metadata']['total_aliases'] = total_aliases
        
        # Write to file
        with open(output_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)


# Convenience functions
def normalize_skill(skill_name: str, fuzzy: bool = True) -> Optional[str]:
    """
    Convenience function for single skill normalization.
    
    Args:
        skill_name: Skill name to normalize
        fuzzy: Enable fuzzy matching
        
    Returns:
        Canonical name or None
    """
    normalizer = SkillNormalizer()
    return normalizer.normalize(skill_name, fuzzy=fuzzy)


def batch_normalize_skills(skill_names: List[str], fuzzy: bool = True) -> Dict[str, Optional[str]]:
    """
    Convenience function for batch normalization.
    
    Args:
        skill_names: List of skill names
        fuzzy: Enable fuzzy matching
        
    Returns:
        Dictionary mapping original -> canonical
    """
    normalizer = SkillNormalizer()
    return normalizer.batch_normalize(skill_names, fuzzy=fuzzy)


# Example usage
if __name__ == "__main__":
    # Initialize normalizer
    normalizer = SkillNormalizer()
    
    # Test various inputs
    test_skills = [
        "python",
        "Py",
        "PostgreSQL",
        "Postgres",
        "AWS",
        "Amazon Web Services",
        "Power BI",
        "PowerBI",
        "business intelligence",
        "BI",
        "apache airflow",
        "Airflow",
        "something random that won't match"
    ]
    
    print("Testing Skill Normalization")
    print("=" * 60)
    
    for skill in test_skills:
        canonical = normalizer.normalize(skill)
        category = normalizer.get_category(canonical) if canonical else None
        
        print(f"'{skill}' -> '{canonical}' [{category}]")
    
    print("\n" + "=" * 60)
    print("Equivalence Tests")
    print("=" * 60)
    
    equivalence_tests = [
        ("PostgreSQL", "Postgres"),
        ("Power BI", "PowerBI"),
        ("BI", "Business Intelligence"),
        ("AWS", "Amazon Web Services"),
        ("Python", "Java")  # Should be False
    ]
    
    for skill1, skill2 in equivalence_tests:
        result = normalizer.are_equivalent(skill1, skill2)
        print(f"'{skill1}' == '{skill2}': {result}")
    
    print("\n" + "=" * 60)
    print("Hierarchical Relationship Tests")
    print("=" * 60)
    
    parent_tests = [
        ("AWS", "Amazon Kinesis"),
        ("AWS", "AWS Redshift"),
        ("Cloud Computing", "AWS")
    ]
    
    for parent, child in parent_tests:
        result = normalizer.is_parent_of(parent, child)
        print(f"'{parent}' is parent of '{child}': {result}")

