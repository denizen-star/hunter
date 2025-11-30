# Complex Dependencies in Matching System

This document explains why the matching system has complex dependencies and how changes can break working functionality.

## The Dependency Chain

The matching system has a multi-stage pipeline with tight coupling:

```
DocumentGenerator
    ↓ (loads resume, calls)
AIAnalyzer
    ↓ (delegates to)
EnhancedQualificationsAnalyzer
    ↓ (uses)
PreliminaryMatcher
    ↓ (depends on)
    ├── Skills.yaml (candidate skills)
    ├── Jobdescr-General Skils.md (job skills database)
    ├── skill_normalization.yaml (normalization rules)
    └── SimpleTechExtractor (technology dictionary)
    ↓ (also uses)
SkillNormalizer
```

## Why Dependencies Are Complex

### 1. Multi-Layer Architecture
**Problem**: Data flows through 4+ layers, each transforming it
- DocumentGenerator → AIAnalyzer → EnhancedAnalyzer → PreliminaryMatcher
- Each layer adds assumptions about data format
- Changes in one layer can break downstream layers

**Example**: If PreliminaryMatcher changes skill format, EnhancedAnalyzer expects different structure

### 2. Shared State via Files
**Problem**: Skills are loaded from YAML files, not passed as parameters
- `skills.yaml` loaded once at PreliminaryMatcher initialization
- Changes to skills.yaml affect all matches
- No clear contract about what should be in these files

**Example**: Adding a skill to skills.yaml changes ALL match calculations

### 3. Duplicate Extraction Logic
**Problem**: Same data extracted in multiple places
- Technologies extracted in PreliminaryMatcher AND EnhancedAnalyzer
- Skills normalized in PreliminaryMatcher AND SkillNormalizer
- No single source of truth for extraction results

**Example**: Fixing extraction in one place doesn't fix it everywhere

### 4. Implicit Contracts
**Problem**: Methods assume specific data structures without explicit contracts
- `_combine_analyses()` expects `preliminary_analysis` to have specific keys
- No type hints or validation of intermediate data structures
- Changes to structure break silently

**Example**: Removing a key from `preliminary_analysis` breaks `_combine_analyses()` but no error until runtime

### 5. Validation Scattered
**Problem**: Validation logic duplicated across multiple methods
- Technology validation in `_combine_analyses()` 
- Skill matching in `_is_skill_matched()`
- Score calculation in `find_skill_matches()`
- Changes need to be made in multiple places

**Example**: Fixing Power BI false positive required changes in 3 different methods

## What Makes It Fragile

### Changes Cascade Unexpectedly
1. Change skill normalization → affects all matches
2. Change technology extraction → breaks validation
3. Change scoring logic → affects AI context
4. Change file format → breaks loading

### No Isolation
- Can't test one component in isolation
- Can't change one thing without affecting others
- Fixes in one place break other places

### Implicit Dependencies
- Resume content loaded but not always needed
- Skills cached but validation still extracts
- Technologies extracted multiple times
- No clear ownership of data

## Solutions Applied

### 1. Consolidated Validation
**Fix**: Created `_validate_technology_match()` method
- Single place for technology validation logic
- All technology matching uses this method
- Changes only need to be made once

### 2. Cache Extracted Data
**Fix**: Store extracted technologies in `preliminary_analysis`
- Extract once in PreliminaryMatcher
- Pass through to EnhancedAnalyzer
- Avoid duplicate extraction

### 3. Use Cached Skills
**Fix**: Use `candidate_skills` from skills.yaml instead of extracting from resume
- Skills loaded once at startup
- No re-extraction during matching
- Faster and more consistent

### 4. Document Invariants
**Fix**: Created MATCHING_INVARIANTS.md
- Clear rules that must always hold
- Prevents accidental breaking changes
- Reference for future developers

## Future Improvements Needed

1. **Explicit Contracts**: Add type hints and validate data structures
2. **Dependency Injection**: Pass data as parameters instead of loading files
3. **Single Responsibility**: Each component should do one thing
4. **Test Isolation**: Mock dependencies to test components independently
5. **Clear Data Flow**: Document how data transforms through pipeline

## How to Avoid Breaking Things

1. **Check Invariants**: Review MATCHING_INVARIANTS.md before changes
2. **Test All Paths**: Changes can affect multiple code paths
3. **Update All Places**: Validation logic might be duplicated
4. **Cache Decisions**: Don't re-extract data already extracted
5. **Document Assumptions**: Make implicit contracts explicit


