# Skill Matching Process - Technical Documentation

## Overview

The skill matching process in Hunter is a sophisticated multi-stage system that compares candidate skills against job requirements to generate accurate match scores and detailed analysis. The system uses a hybrid approach combining rule-based preliminary matching with AI-powered contextual analysis to provide both speed and accuracy.

## Architecture

The skill matching system consists of several integrated components:

1. **Preliminary Matcher** (`app/services/preliminary_matcher.py`) - Fast rule-based matching
2. **Enhanced Qualifications Analyzer** (`app/services/enhanced_qualifications_analyzer.py`) - Orchestrates preliminary + AI analysis
3. **Skill Normalizer** (`app/utils/skill_normalizer.py`) - Normalizes skill names using taxonomy
4. **Simple Tech Extractor** (`app/utils/simple_tech_extractor.py`) - Extracts technology names
5. **AI Analyzer** (`app/services/ai_analyzer.py`) - Provides AI-powered analysis
6. **Resume Manager** (`app/services/resume_manager.py`) - Manages candidate skills data

## Data Sources

### Candidate Skills Database

**Location**: `data/resumes/skills.yaml`

This file contains the candidate's skills organized as a YAML dictionary. Each skill entry includes:

- **Skill name**: The canonical name of the skill
- **Category**: Classification (e.g., "Programming Languages", "Cloud Platforms")
- **Source**: Where the skill was extracted from (e.g., "technical_skills", "experience")
- **Variations found**: Alternative names or formats discovered for this skill

Example structure:
```yaml
skills:
  Python:
    category: Programming Languages
    source: technical_skills
    variations_found: ['python', 'py']
  AWS:
    category: Cloud Platforms
    source: technical_skills
    variations_found: ['aws', 'amazon web services']
```

### Job Skills Database

**Location**: `Jobdescr-General Skils.md`

This markdown file contains a comprehensive list of skills commonly found in job descriptions, organized by category:

- Technical Skills
- Soft Skills
- Tools & Technologies
- Experience Requirements
- Education & Certifications

The Preliminary Matcher uses this database to extract skills from job descriptions by matching patterns against known skill names.

### Skill Normalization Taxonomy

**Location**: `data/config/skill_normalization.yaml`

This comprehensive taxonomy contains:

- **Canonical skill names**: Standardized names for skills
- **Aliases**: Alternative names that map to canonical names
- **Categories**: Hierarchical organization of skills
- **Fuzzy matching rules**: Configuration for approximate matching
- **Word replacements**: Expansions (e.g., "BI" → "Business Intelligence")
- **Prefix/suffix stripping**: Rules for removing qualifiers

The taxonomy contains 499 canonical skills with 325 aliases, providing extensive coverage for normalization.

## Process Flow

### Step 1: Initialization

When the system starts analyzing a job match:

1. **Load Candidate Skills**: The `PreliminaryMatcher` loads skills from `data/resumes/skills.yaml`
2. **Load Job Skills**: The matcher loads known job skills from `Jobdescr-General Skils.md`
3. **Build Normalization Cache**: The matcher initializes empty caches for normalized skills (lazy loading)
4. **Initialize Tech Extractor**: The `SimpleTechExtractor` is initialized with its predefined technology dictionary

### Step 2: Job Description Analysis

The system extracts skills from the job description using multiple methods:

#### 2.1 Pattern-Based Extraction

The `_extract_job_skills_from_description()` method:

1. **Normalizes the job description**: Converts to lowercase for case-insensitive matching
2. **Iterates through job skills database**: Checks each known skill against the job description
3. **Normalizes skill names**: Removes prefixes, suffixes, and parenthetical information
4. **Validates presence**: Uses word boundary matching to ensure skills are actually mentioned
5. **Filters invalid entries**: Removes placeholders, incomplete phrases, and overly long entries
6. **Consolidates similar skills**: Deduplicates equivalent skills (e.g., "Tableau" and "BI Tools")

#### 2.2 Specific Technology Extraction

The system also checks for specific technologies using a predefined list:

- Programming languages (Python, SQL, Java, etc.)
- Cloud platforms (AWS, Azure, GCP)
- Data tools (Snowflake, BigQuery, Spark, etc.)
- Business Intelligence tools (Tableau, Power BI, Looker, etc.)
- And many more categories

#### 2.3 Validation and Filtering

Extracted skills undergo strict validation:

- Must be 3-50 characters long
- Cannot be just numbers or punctuation
- Must not contain experience qualifiers alone ("5+ years" without skill name)
- Must actually appear in the job description (not just similar words)
- For multi-word skills, all significant words must be present

### Step 3: Skill Normalization

Before matching, skills are normalized to handle variations:

#### 3.1 Normalization Process

The `normalize_skill_name()` method:

1. **Converts to lowercase**: Standardizes case
2. **Removes invalid patterns**: Filters out "etc.)", single characters, numbers only
3. **Strips common prefixes**: Removes "experience with", "knowledge of", "proficiency in", etc.
4. **Removes parentheticals**: Strips information in parentheses
5. **Removes common suffixes**: Removes "experience", "knowledge", "skills", etc.

Example:
- "Experience with Python programming" → "python programming" → "python"
- "AWS (Amazon Web Services) experience" → "aws"

#### 3.2 Taxonomy-Based Normalization

The `SkillNormalizer` class provides more sophisticated normalization:

1. **Exact alias matching**: Checks if skill matches any alias in the taxonomy
2. **Prefix/suffix stripping**: Applies configured stripping rules
3. **Word replacement**: Expands abbreviations (e.g., "BI" → "Business Intelligence")
4. **Fuzzy matching**: Uses SequenceMatcher to find similar skills (85% similarity threshold)

### Step 4: Preliminary Matching

The core matching logic in `find_skill_matches()`:

#### 4.1 Exact Matching

For each candidate skill:

1. **Normalize the skill**: Apply normalization rules
2. **Get variations**: Include skill name and all variations found
3. **Check job description**: Search for each variation in the normalized job description
4. **Mark as matched**: If found, add to exact matches list

The matching checks:
- Direct substring matches
- Normalized variations
- All skill aliases

#### 4.2 Partial Matching

For skills not found exactly, the system uses fuzzy matching:

1. **Word-based matching**: For multi-word skills, checks if 60% of words appear
2. **Contextual matching**: Considers partial skill names
3. **Mark as partial**: Adds to partial matches if threshold met

Example:
- Candidate skill: "Data Engineering and Architecture"
- Job description mentions: "data engineering experience"
- Result: Partial match (2 out of 3 words match)

#### 4.3 Job Skill Matching

After matching candidate skills, the system identifies which job skills are matched:

1. **Two-phase matching**:
   - Phase 1: Quick check against skills already found in job description
   - Phase 2: Fallback check against ALL candidate skills (for cases like "strategy" → "Business Strategy")

2. **Skill equivalence**: Uses predefined mappings:
   - "AWS Lake Formation" → matches "AWS"
   - "Amazon Kinesis" → matches "AWS" or "streaming"
   - "Budget Management" → matches "Financial Management" or "Leadership"
   - "Product Strategy" → matches "Strategy" or "Planning"

3. **Unmatched skills**: Job skills not found in candidate skills are tracked separately

### Step 5: Match Score Calculation

The system calculates a match score based on job requirements (not candidate skills):

#### 5.1 Base Score Calculation

```python
total_job_skills = len(job_skills_found)
matched_job_skills = count_of_matched_job_skills
base_score = (matched_job_skills / total_job_skills) * 100
```

This ensures the score reflects how many of the job's requirements are met, not how many candidate skills match.

#### 5.2 Overqualification Handling

The system detects when candidates are overqualified (have significantly more skills than required):

1. **Calculate ratio**: `total_candidate_skills / total_job_skills`
2. **Detect overqualification**: If ratio >= 2.0 (candidate has 2x+ more skills)
3. **Apply bonuses**: Overqualified candidates receive score bonuses:
   - 4x+ overqualified: +15 points
   - 3x+ overqualified: +10 points
   - 2x+ overqualified: +5 points

4. **Reduce penalties**: Missing skills are penalized less for overqualified candidates:
   - Critical skills: 1.5 points penalty (vs 3.0 for standard)
   - Nice-to-have skills: 0.5 points penalty (vs 1.0 for standard)
   - Maximum penalty capped at 10% (vs 20% for standard)

#### 5.3 Critical vs Nice-to-Have Skills

The system distinguishes between critical and nice-to-have skills:

**Critical skills** (higher penalty if missing):
- Snowflake, BigQuery
- Cloud platforms
- Data engineering

**Nice-to-have skills** (lower penalty):
- Paid advertising, Google Ads
- Mentorship skills
- Problem-solving

#### 5.4 Final Score

The final score is calculated as:

```python
if overqualified:
    base_score = (matched_job_skills / total_job_skills) * 100
    penalty = calculate_reduced_penalty(missing_skills)
    base_score = max(0, base_score - penalty)
    if base_score >= 50:
        base_score = min(100, base_score + overqualification_bonus)
else:
    base_score = (matched_job_skills / total_job_skills) * 100
    penalty = calculate_standard_penalty(missing_skills)
    base_score = max(0, base_score - penalty)

final_score = round(base_score, 2)
```

### Step 6: Technology Matching

Parallel to skill matching, the system performs technology matching:

#### 6.1 Technology Extraction

The `SimpleTechExtractor` class uses a predefined dictionary of 157+ technologies with variations:

- Cloud Platforms: AWS, Azure, GCP (with 3-4 variations each)
- Data Engineering: Apache Spark, Kafka, Airflow (with 2-3 variations each)
- Databases: PostgreSQL, MySQL, MongoDB (with 2-3 variations each)
- BI Tools: Tableau, Power BI, Looker (with variations)
- Programming Languages: Python, Java, SQL (with variations)
- And many more categories

#### 6.2 Technology Comparison

The comparison process:

1. **Extract from job description**: Find all technologies mentioned
2. **Extract from resume**: Find all technologies mentioned (or use cached list from `tech.yaml`)
3. **Calculate matches**: Set intersection of job and resume technologies
4. **Calculate missing**: Set difference (job - resume)
5. **Calculate additional**: Set difference (resume - job) - bonus technologies

#### 6.3 Technology Score

```python
total_required = len(job_technologies)
match_count = len(matched_technologies)
technology_score = (match_count / total_required * 100) if total_required > 0 else 0
```

Technology matching is separate from skill matching but provides additional context for the AI analysis.

### Step 7: AI Analysis Integration

The enhanced system combines preliminary matching with AI analysis:

#### 7.1 Context Creation

The `create_ai_prompt_context()` method generates a focused context for the AI:

1. **Preliminary results summary**: Match score, exact matches count, partial matches count
2. **Exact matches list**: Formatted list of matched skills with categories
3. **Partial matches list**: Formatted list of partially matched skills
4. **Unmatched job skills**: Skills from job description not found in candidate resume
5. **AI focus areas**: Identified areas where AI should focus analysis

#### 7.2 Focused AI Prompt

The AI receives:
- Full job description
- Full resume content
- Preliminary matching results
- Instructions to focus on specific areas
- Guidance on being generous with skill recognition (recognizing equivalent skills)

#### 7.3 AI Response Parsing

The AI response is parsed to extract:
- Match score (noted but not used - preliminary score is source of truth)
- Features compared count
- Strong matches (merged with preliminary matches)
- Missing skills (validated against preliminary unmatched skills only)
- Partial matches
- Recommendations
- Detailed analysis

### Step 8: Result Combination

The `_combine_analyses()` method merges preliminary and AI results:

#### 8.1 Score Selection

**Critical**: The preliminary matcher score is ALWAYS used as the final score. The AI score is ignored because:
- Preliminary matcher uses exact, validated matching
- AI scores can be inconsistent
- Preliminary matcher has validated skill databases

#### 8.2 Strong Matches Combination

Combines:
- Exact matches from preliminary analysis
- Strong matches from AI analysis

#### 8.3 Missing Skills Validation

Only includes missing skills that:
- Are in the preliminary unmatched job skills list (validated from job description)
- Match exactly (case-insensitive) with preliminary unmatched skills

This prevents AI from adding skills that weren't actually in the job description.

#### 8.4 Skill Mapping Generation

Creates a detailed mapping showing:
- Each job skill → matched candidate skill (if found)
- Match type (EXACT or PARTIAL)
- Unmatched job skills (marked with dashes)

### Step 9: Final Output

The system produces a `QualificationAnalysis` object containing:

- **Match Score**: Final percentage (from preliminary matcher)
- **Features Compared**: Total number of skills/features analyzed
- **Strong Matches**: List of matched skills
- **Missing Skills**: List of missing skills (validated)
- **Partial Matches**: List of partially matched skills
- **Soft Skills**: Soft skills alignment analysis
- **Recommendations**: AI-generated recommendations
- **Detailed Analysis**: Combined preliminary + AI analysis with skill mapping

## Matching Algorithms

### Exact Matching Algorithm

```python
def find_exact_matches(job_description, candidate_skills):
    job_desc_lower = job_description.lower()
    matches = []
    
    for skill_name, skill_data in candidate_skills.items():
        skill_normalized = normalize_skill_name(skill_name)
        skill_variations = [skill_normalized] + skill_data.get('variations_found', [])
        
        for variation in skill_variations:
            if variation and variation in job_desc_lower:
                matches.append({
                    'skill': skill_name,
                    'category': skill_data.get('category'),
                    'source': skill_data.get('source')
                })
                break
    
    return matches
```

### Partial Matching Algorithm

```python
def _is_partial_match(skill, job_desc):
    skill_words = skill.split()
    
    if len(skill_words) == 1:
        return skill in job_desc
    
    # For multi-word skills, check if most words appear
    matches = sum(1 for word in skill_words if word in job_desc)
    return matches >= len(skill_words) * 0.6  # 60% of words must match
```

### Skill Equivalence Matching

```python
def _is_skill_matched(job_skill, matched_skills):
    job_skill_normalized = normalize_skill_name(job_skill)
    
    # Define skill equivalence mappings
    skill_equivalences = {
        'aws lake formation': ['aws', 'lake formation', 'data lake'],
        'amazon kinesis': ['aws', 'kinesis', 'streaming'],
        'budget management': ['financial management', 'budget', 'leadership'],
        'product strategy': ['strategy', 'strategic', 'planning'],
        'data engineering': ['data warehousing', 'etl', 'data pipeline'],
        # ... more mappings
    }
    
    for candidate_skill in matched_skills:
        candidate_normalized = normalize_skill_name(candidate_skill)
        
        # Direct match
        if job_skill_normalized == candidate_normalized:
            return True
        
        # Check equivalences
        if job_skill_normalized in skill_equivalences:
            for equivalent in skill_equivalences[job_skill_normalized]:
                if equivalent in candidate_normalized:
                    return True
    
    return False
```

## Performance Optimizations

### Lazy Normalization Caching

Skills are normalized on-demand and cached:

```python
def _get_normalized_skill(self, skill_name: str) -> str:
    if skill_name in self._normalized_candidate_skills_cache:
        return self._normalized_candidate_skills_cache[skill_name]
    
    normalized = self.normalize_skill_name(skill_name)
    if normalized:
        self._normalized_candidate_skills_cache[skill_name] = normalized
        self._normalized_candidate_skills_set.add(normalized)
    return normalized or ""
```

This avoids redundant normalization operations.

### Two-Phase Job Skill Matching

1. **Phase 1**: Quick check against skills already found
2. **Phase 2**: Fallback check against all candidate skills

This reduces computation for the majority of cases.

### Skill Consolidation

Similar skills are consolidated to avoid duplicates:

```python
skill_groups = {
    'tableau': ['tableau', 'bi tools', 'bi tool expertise'],
    'aws': ['aws', 'amazon web services'],
    'spark': ['spark', 'apache spark'],
    # ... more groups
}
```

## Configuration and Customization

### Adding New Skills

To add candidate skills, edit `data/resumes/skills.yaml`:

```yaml
skills:
  New Skill Name:
    category: Category Name
    source: technical_skills
    variations_found: ['variation1', 'variation2']
```

### Adding Job Skills

To add job skills, edit `Jobdescr-General Skils.md`:

```markdown
## Technical Skills
- New Technical Skill
- Another Technical Skill

## Soft Skills
- New Soft Skill
```

### Configuring Skill Normalization

Edit `data/config/skill_normalization.yaml`:

```yaml
skills:
  "canonical skill name":
    canonical: "canonical skill name"
    aliases:
      - alias1
      - alias2
    category: Category Name
    tags: ['tag1', 'tag2']
```

### Adjusting Matching Thresholds

In `app/services/preliminary_matcher.py`:

- **Partial match threshold**: Currently 60% of words must match (line 498)
- **Overqualification ratio**: Currently 2.0 (line 242)
- **Score bonuses**: Adjustable in lines 267-275
- **Penalty values**: Adjustable in lines 251-262 and 282-290

## Error Handling

### Invalid Skills

The system filters invalid skills during normalization:
- Empty strings
- Single characters
- Numbers only
- Punctuation only
- Overly long strings (>50 characters)

### Missing Data

If `skills.yaml` is missing, the system falls back to:
- Extracting technologies from resume content directly
- Using empty skill lists (results in lower match scores)

### AI Analysis Failures

If AI analysis fails:
- System falls back to preliminary matching only
- Match score is still calculated from preliminary results
- Detailed analysis may be limited

## Integration Points

### Entry Point

The skill matching process is initiated from:

```python
# In app/services/ai_analyzer.py
analyzer.analyze_qualifications(job_description, resume_content)
```

### Enhanced Path

When `EnhancedQualificationsAnalyzer` is available:

```python
# In app/services/enhanced_qualifications_analyzer.py
analyzer.analyze_qualifications_enhanced(job_description, resume_content)
```

This uses the two-stage approach (preliminary + AI).

### Standard Path

When enhanced analyzer is not available:

```python
# In app/services/ai_analyzer.py
analyzer._analyze_qualifications_original(job_description, resume_content)
```

This uses technology matching + AI analysis only.

## Output Format

### QualificationAnalysis Object

```python
QualificationAnalysis(
    match_score=85.5,  # Float percentage
    features_compared=125,  # Integer count
    strong_matches=[...],  # List of strings
    missing_skills=[...],  # List of strings
    partial_matches=[...],  # List of strings
    soft_skills=[...],  # List of dicts
    recommendations=[...],  # List of strings
    detailed_analysis="..."  # String with full analysis
)
```

### Detailed Analysis Format

The detailed analysis includes:

1. **Preliminary Matching Results**: Summary with scores
2. **Skill Mapping**: Job skill → Candidate skill mapping
3. **AI Analysis**: Detailed contextual analysis
4. **Recommendations**: Actionable recommendations

## Debugging and Troubleshooting

### Enable Debug Output

The system prints progress messages:
- "Using Enhanced Qualifications Analyzer"
- "Creating focused AI analysis prompt"
- "Running AI analysis with preliminary context"
- "Combining preliminary and AI analysis results"

### Common Issues

1. **Low match scores**: Check if skills are properly normalized in `skills.yaml`
2. **Missing skills appearing**: Verify skills are actually in job description
3. **Overqualification not detected**: Check candidate skills count vs job skills count
4. **Technology matching issues**: Verify technology names in `SimpleTechExtractor.TECHNOLOGIES`

### Validation Checks

The system includes validation:
- Skills must actually appear in job description (word boundary matching)
- Multi-word skills require all words present
- Invalid patterns are filtered out
- AI-added skills are validated against preliminary results

## Future Enhancements

Potential improvements:

1. **Machine learning-based matching**: Train models on successful matches
2. **Semantic similarity**: Use embeddings for better skill matching
3. **Context-aware matching**: Consider skill context in job descriptions
4. **Dynamic skill learning**: Automatically learn new skills from job descriptions
5. **Industry-specific matching**: Specialized matching for different industries

## Conclusion

The skill matching process in Hunter is a sophisticated, multi-stage system that combines:
- Fast, rule-based preliminary matching
- Comprehensive skill normalization
- Technology extraction and matching
- AI-powered contextual analysis
- Validated result combination

This hybrid approach provides both speed and accuracy, ensuring candidates receive reliable match scores and detailed analysis of their fit for job opportunities.

