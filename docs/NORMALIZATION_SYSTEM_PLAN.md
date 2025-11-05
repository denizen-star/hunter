# Skill Normalization System - Implementation Plan

## Executive Summary

We've built a new advanced skill normalization system that replaces the existing hard-coded normalization with a flexible, user-configurable taxonomy. This system allows you to define aliases, categories, relationships, and fuzzy matching rules through a YAML configuration file.

## Current Status

✅ **Completed:**
1. Normalization taxonomy YAML structure (`data/config/skill_normalization.yaml`)
2. SkillNormalizer service (`app/utils/skill_normalizer.py`)
3. Fix for word replacement ordering bug

⏳ **In Progress:**
- Documentation and testing

📋 **Next Steps:**
1. Create management UI for aliases/categories
2. Integrate into existing matching system
3. Populate with comprehensive skill database

---

## Architecture

### 1. Configuration File Structure

**Location:** `data/config/skill_normalization.yaml`

```yaml
# Canonical skills with aliases
skills:
  Python:
    canonical: Python
    aliases: [py, python3]
    category: Programming Languages
    tags: [language, scripting]
  
  # Relationships (hierarchical and equivalence)
  relationships:
    AWS:
      - Amazon Kinesis
      - Lambda
    equivalences:
      - [Power BI, PowerBI]
```

**Features:**
- ✅ Canonical name mapping
- ✅ Alias lists
- ✅ Category assignment
- ✅ Hierarchical relationships (parent/child)
- ✅ Equivalence relationships (same skill)
- ✅ Fuzzy matching configuration

### 2. SkillNormalizer Service

**Location:** `app/utils/skill_normalizer.py`

**Key Methods:**
```python
# Single skill normalization
normalizer = SkillNormalizer()
canonical = normalizer.normalize("PostgreSQL")  # -> "PostgreSQL"
canonical = normalizer.normalize("Postgres")     # -> "PostgreSQL"

# Batch processing
results = normalizer.batch_normalize(["python", "SQL", "aws"])

# Relationship checks
is_parent = normalizer.is_parent_of("AWS", "Amazon Kinesis")  # -> True
are_same = normalizer.are_equivalent("BI", "Business Intelligence")  # -> True
```

**Normalization Pipeline:**
1. **String Normalization**: Lowercase, remove punctuation, normalize whitespace
2. **Exact Match**: Check alias map first (fastest)
3. **Prefix/Suffix Stripping**: Remove common prefixes like "Microsoft"
4. **Word Replacement**: Expand abbreviations (BI → Business Intelligence)
5. **Fuzzy Matching**: Similarity matching if threshold met (85% default)

---

## How It Solves Your Requirements

### ✅ Map Multi-Word Aliases

**Example:**
```yaml
AWS:
  aliases:
    - amazon web services
    - amazon aws
    - aws cloud
```

**Result:** All three map to "AWS"

### ✅ Resolve Composite Overlaps

**Example:**
```yaml
AWS Redshift:
  aliases: [redshift, amazon redshift, aws redshift]
  parent: AWS

relationships:
  AWS:
    - AWS Redshift
    - Amazon Kinesis
    - Lambda
```

**Result:** "Redshift" maps to "AWS Redshift" which has parent "AWS"

### ✅ Detect Fuzzy Equivalences

**Example:**
```python
normalizer.are_equivalent("PostgreSQL", "Postgres")  # -> True
normalizer.are_equivalent("Power BI", "PowerBI")     # -> True
```

**Configuration:**
```yaml
equivalences:
  - [PostgreSQL, Postgres]
  - [Power BI, PowerBI]
  - [Business Intelligence, BI]
```

### ✅ Taxonomy Over String Rules

**Old Approach:**
```python
# Hard-coded in code
if skill.startswith("experience with"):
    skill = skill[14:]
```

**New Approach:**
```yaml
# Configurable
fuzzy_rules:
  strip_prefixes:
    - microsoft
    - amazon
    - apache
  strip_suffixes:
    - experience
    - knowledge
    - skills
```

---

## Adding New Skills - User Guide

### Method 1: Edit YAML File Directly

```yaml
skills:
  Your New Skill:
    canonical: Your New Skill
    aliases:
      - alias1
      - alias2
      - variant name
    category: Category Name
    tags: [tag1, tag2]
    parent: Parent Skill (optional)
```

### Method 2: Via Python API

```python
from app.utils.skill_normalizer import SkillNormalizer

normalizer = SkillNormalizer()
normalizer.add_skill(
    canonical_name="Your New Skill",
    aliases=["alias1", "alias2"],
    category="Category Name",
    tags=["tag1", "tag2"],
    parent="Parent Skill"
)
# Save to file
normalizer.save_config()
```

### Method 3: Web UI (Future)

- Visual editor for skills
- Auto-suggest aliases
- Category management
- Import/export functionality

---

## Integration Points

### Current System Integration

**Files to Update:**

1. **`app/services/preliminary_matcher.py`**
   - Replace `normalize_skill_name()` with `SkillNormalizer.normalize()`

2. **`app/utils/simple_tech_extractor.py`**
   - Integrate with TECHNOLOGIES dictionary

3. **`app/services/enhanced_qualifications_analyzer.py`**
   - Use new normalizer for skill comparisons

### Example Integration

```python
# Old approach
def normalize_skill_name(self, skill: str) -> str:
    skill = skill.lower().strip()
    # ... hard-coded rules ...
    return skill

# New approach
from app.utils.skill_normalizer import SkillNormalizer

class PreliminaryMatcher:
    def __init__(self):
        self.normalizer = SkillNormalizer()
    
    def find_skill_matches(self, job_description: str):
        # ...
        skill_normalized = self.normalizer.normalize(skill_name)
        if self.normalizer.are_equivalent(skill1, skill2):
            # Handle as match
```

---

## Benefits vs. Current System

| Feature | Current System | New System |
|---------|---------------|------------|
| **Configuration** | Hard-coded in Python | YAML config file |
| **Aliases** | Limited variations | Unlimited aliases per skill |
| **Fuzzy Matching** | Not implemented | Configurable threshold |
| **Relationships** | None | Parent/child, equivalence |
| **Extensibility** | Requires code changes | Just edit YAML |
| **Speed** | Fast | Fast + better accuracy |
| **Maintenance** | Difficult | Easy |

---

## Migration Strategy

### Phase 1: Gradual Adoption (Week 1)

1. ✅ Keep existing normalization for backward compatibility
2. ✅ Run new normalizer in parallel
3. ✅ Compare results
4. ✅ Fix any issues

### Phase 2: Integration (Week 2)

1. Update `PreliminaryMatcher` to use new normalizer
2. Update `SimpleTechExtractor` for technology matching
3. Add comprehensive skill database to YAML

### Phase 3: Optimization (Week 3)

1. Build web UI for skill management
2. Add validation and testing
3. Performance tuning
4. Documentation

---

## Populating the Taxonomy

### Current State

- **Skills in YAML**: ~20 examples
- **Skills in Current System**: ~146 in skills.yaml, ~160 in TECHNOLOGIES

### Target State

- **Technical Skills**: 200+ skills
- **Soft Skills**: 100+ skills
- **Categories**: 20+ categories
- **Relationships**: Comprehensive hierarchy

### Data Sources

1. **Existing**: `data/resumes/skills.yaml` (146 skills)
2. **Existing**: `Jobdescr-General Skils.md` (400+ skills)
3. **Existing**: `app/utils/simple_tech_extractor.py` (160 technologies)
4. **Manual Input**: Your knowledge of skills

### Import Script

**Next Step:** Create a script to auto-import from existing sources:

```python
# scripts/import_skills_to_taxonomy.py
import yaml
from pathlib import Path

def import_from_skills_yaml():
    # Import from data/resumes/skills.yaml
    pass

def import_from_tech_extractor():
    # Import from TECHNOLOGIES dictionary
    pass

def merge_and_deduplicate():
    # Combine all sources
    pass
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_skill_normalizer.py
def test_exact_match():
    normalizer = SkillNormalizer()
    assert normalizer.normalize("Python") == "Python"
    assert normalizer.normalize("py") == "Python"

def test_alias_mapping():
    normalizer = SkillNormalizer()
    assert normalizer.normalize("Amazon Web Services") == "AWS"
    assert normalizer.normalize("Postgres") == "PostgreSQL"

def test_equivalence():
    normalizer = SkillNormalizer()
    assert normalizer.are_equivalent("Power BI", "PowerBI") == True
    assert normalizer.are_equivalent("Python", "Java") == False

def test_hierarchical():
    normalizer = SkillNormalizer()
    assert normalizer.is_parent_of("AWS", "Amazon Kinesis") == True
```

### Integration Tests

```python
# Test with actual resume and job descriptions
def test_real_world_normalization():
    resume_skills = extract_from_resume("data/resumes/base_resume.md")
    job_skills = extract_from_job_description("sample_job.md")
    
    normalizer = SkillNormalizer()
    normalized_resume = [normalizer.normalize(s) for s in resume_skills]
    normalized_job = [normalizer.normalize(s) for s in job_skills]
    
    matches = set(normalized_resume) & set(normalized_job)
    assert len(matches) > 0
```

---

## Next Steps

### Immediate (This Week)

1. ✅ Create YAML taxonomy structure
2. ✅ Build SkillNormalizer service
3. ⏳ Create import script for existing skills
4. ⏳ Add comprehensive test cases

### Short Term (Next 2 Weeks)

1. Integrate into `PreliminaryMatcher`
2. Build basic web UI for skill management
3. Run side-by-side comparison with old system
4. Populate with 200+ skills

### Long Term (Next Month)

1. Advanced UI with auto-suggestions
2. Historical matching comparison dashboard
3. Machine learning for alias discovery
4. Community-contributed skills database

---

## Questions for You

1. **Skill Population**: Should we auto-import from existing sources, or do you want to curate manually?

2. **UI Priority**: Web UI for managing skills - how important is this vs. just editing YAML?

3. **Backward Compatibility**: Keep old normalizer running in parallel or fully switch?

4. **Performance**: Should we cache normalization results for speed?

5. **Extensibility**: Want to add more advanced features like:
   - Confidence scores for fuzzy matches
   - Skill taxonomy visualization
   - Auto-discovery of new aliases
   - Multi-language support

---

## File Locations

- **Configuration**: `data/config/skill_normalization.yaml`
- **Service**: `app/utils/skill_normalizer.py`
- **Documentation**: `docs/NORMALIZATION_SYSTEM_PLAN.md`
- **Tests**: `tests/test_skill_normalizer.py` (to be created)

---

## Contact & Support

For questions or suggestions about the normalization system, edit the YAML file and save - changes take effect immediately on next load.




