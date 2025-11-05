#!/usr/bin/env python3
"""
Side-by-side comparison of old and new normalization systems
Tests both systems on the same job description and resume
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.preliminary_matcher import PreliminaryMatcher
from app.utils.skill_normalizer import SkillNormalizer
from app.utils.file_utils import read_text_file

def compare_normalizers():
    """Compare old and new normalization approaches"""
    
    print("╔" + "="*100 + "╗")
    print("║" + " "*30 + "NORMALIZATION COMPARISON" + " "*45 + "║")
    print("╚" + "="*100 + "╝\n")
    
    # Initialize both systems
    print("📦 Initializing systems...")
    old_matcher = PreliminaryMatcher()
    new_normalizer = SkillNormalizer()
    print("✅ Both systems ready\n")
    
    # Load a sample job description
    print("📄 Loading test job description...")
    job_descriptions_dir = Path("data/applications")
    
    # Find a recent job description
    sample_job = None
    for app_dir in sorted(job_descriptions_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if app_dir.is_dir():
            raw_files = list(app_dir.glob("*raw.txt"))
            if raw_files:
                sample_job = raw_files[0]
                break
    
    if not sample_job:
        print("❌ No job description found. Please create an application first.")
        return
    
    job_text = read_text_file(sample_job)
    print(f"✅ Loaded: {sample_job.name}\n")
    
    # Test: Normalize some sample skills
    test_skills = [
        "PostgreSQL", "Postgres", "Python", "py", "AWS", "Amazon Web Services",
        "Power BI", "PowerBI", "SQL", "Structured Query Language",
        "Apache Airflow", "Airflow", "MongoDB", "Mongo"
    ]
    
    print("="*100)
    print("SKILL NORMALIZATION COMPARISON")
    print("="*100)
    print(f"\n{'Skill Input':<30} | {'Old System':<30} | {'New System':<30}")
    print("-"*100)
    
    differences = []
    for skill in test_skills:
        old_result = old_matcher.normalize_skill_name(skill)
        new_result = new_normalizer.normalize(skill, fuzzy=True)
        
        old_display = old_result if old_result else "(no change)"
        new_display = str(new_result) if new_result else "NO MATCH"
        
        same = (old_result.lower() == str(new_result).lower() if new_result and old_result else False)
        marker = "✅" if same else "⚠️ "
        if not same:
            differences.append({
                'skill': skill,
                'old': old_result,
                'new': new_result
            })
        
        print(f"{marker} {skill:<28} | {old_display:<30} | {new_display:<30}")
    
    print("="*100)
    
    # Test: Extract and compare job skills
    print("\n" + "="*100)
    print("JOB SKILL EXTRACTION COMPARISON")
    print("="*100)
    
    # Old system extraction
    old_matches = old_matcher.find_skill_matches(job_text)
    old_extracted = old_matcher._extract_job_skills_from_description(job_text)
    
    # New system - normalize old extracted skills
    new_extracted = []
    for skill in old_extracted:
        normalized = new_normalizer.normalize(skill, fuzzy=True)
        if normalized:
            new_extracted.append(normalized)
    
    print(f"\nOld System extracted: {len(old_extracted)} skills")
    print(f"New System normalized: {len(set(new_extracted))} unique skills")
    
    # Show differences
    print(f"\n⚠️  Differences found: {len(differences)} skills normalize differently")
    if differences:
        print("\nSample differences:")
        for diff in differences[:10]:
            print(f"  {diff['skill']}:")
            print(f"    Old: {diff['old']}")
            print(f"    New: {diff['new']}")
    
    # Match score comparison
    print("\n" + "="*100)
    print("MATCH SCORE COMPARISON")
    print("="*100)
    
    print(f"\nOld System Match Score: {old_matches['match_score']}%")
    print(f"  Exact matches: {old_matches['matched_count']}")
    print(f"  Missing: {old_matches['missing_count']}")
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    print(f"""
✅ Old System (PreliminaryMatcher):
   • Basic normalization (lowercase, prefix/suffix removal)
   • Exact string matching
   • Hard-coded skill patterns
   • Match Score: {old_matches['match_score']}%

✅ New System (SkillNormalizer):
   • 480 skills with 325+ aliases
   • Fuzzy matching (85% similarity)
   • Category-based organization
   • 88 fuzzy word replacements

⚠️  Key Differences:
   • New system maps aliases (Postgres → PostgreSQL)
   • New system handles abbreviations (AWS = Amazon Web Services)
   • Old system: {len(old_extracted)} extracted skills
   • New system: {len(set(new_extracted))} normalized unique skills

💡 Recommendation:
   {"New system provides better normalization and alias resolution" if len(differences) > 0 
    else "Both systems produce similar results"}
""")
    
    print("="*100)
    print("✅ Comparison complete!")
    print("="*100)


if __name__ == "__main__":
    compare_normalizers()




