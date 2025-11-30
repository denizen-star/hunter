# Matching System Invariants

This document defines rules that must ALWAYS hold true in the matching system. These are non-negotiable constraints that prevent regressions.

## Core Invariants

### 1. Technology Validation Invariant
**Rule**: Technologies can ONLY be marked as "strong matches" if they exist in the candidate's resume/skills.yaml

**Why**: Prevents false positives like "Power BI" appearing as a match when it's only mentioned in the job description, not the candidate's actual resume.

**Implementation**: 
- Technologies are validated using cached `candidate_skills` from `skills.yaml`
- No re-extraction from `resume_content` (performance optimization)
- Validation method: `_validate_technology_match()` in `enhanced_qualifications_analyzer.py`

### 2. Match Score Cap Invariant  
**Rule**: Match scores CANNOT be 100% when there are unmatched job skills

**Why**: Prevents inflated scores that don't reflect actual skill gaps.

**Implementation**:
- Overqualification bonus is capped at 95% when unmatched skills exist
- Maximum score = 95% if `unmatched_job_skills` is not empty
- Location: `preliminary_matcher.py` lines 282-292

### 3. Performance Invariant
**Rule**: Resume content should NOT be re-processed for technology extraction during matching

**Why**: Resume content is large and extraction is expensive. Skills.yaml is the source of truth and is loaded once at startup.

**Implementation**:
- Use cached `preliminary_matcher.candidate_skills` instead of `extract_technologies(resume_content)`
- Resume content is only loaded for AI context, not for technology matching
- Location: `enhanced_qualifications_analyzer.py` uses cached skills, not resume extraction

### 4. Single Extraction Invariant
**Rule**: Job description technologies should be extracted ONCE and reused

**Why**: Avoids duplicate work and ensures consistency.

**Implementation**:
- Technologies extracted in `preliminary_matcher.generate_preliminary_analysis()`
- Stored in `preliminary_analysis['extracted_job_technologies']`
- Reused in `enhanced_qualifications_analyzer._combine_analyses()`

## Validation Checklist

Before making changes to matching logic, verify:

- [ ] Technologies only marked as matches if in candidate skills
- [ ] Scores capped at 95% when skills are missing
- [ ] No resume content extraction during matching (use cached skills)
- [ ] Job technologies extracted once and reused
- [ ] All validation logic uses `_validate_technology_match()` method

## Why These Invariants Matter

These rules prevent common regression issues:
- **False positive technologies**: Power BI appearing when not in resume
- **Inflated scores**: 100% matches when skills are missing
- **Performance degradation**: Slow processing from re-extracting data
- **Inconsistent results**: Different extractions leading to different matches

## Breaking These Invariants

If you need to change these rules:
1. Update this document first
2. Update all affected code locations
3. Run regression tests
4. Document the reason for the change


