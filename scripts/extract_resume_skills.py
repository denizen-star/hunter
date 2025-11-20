#!/usr/bin/env python3
"""
Standalone script to extract comprehensive skills from resume and update skills.yaml
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.resume_manager import ResumeManager
from app.services.skill_extractor import SkillExtractor
from app.services.ai_analyzer import AIAnalyzer

def main():
    print("=" * 60)
    print("EXTRACTING COMPREHENSIVE SKILLS FROM RESUME")
    print("=" * 60)
    
    # Load resume
    resume_manager = ResumeManager()
    try:
        resume = resume_manager.load_base_resume()
        print(f"\n✅ Resume loaded: {len(resume.content)} characters")
    except FileNotFoundError:
        print("\n❌ Resume not found! Please create a resume first.")
        return
    
    # Initialize AI analyzer and skill extractor
    print("\n🔍 Initializing AI analyzer...")
    try:
        ai_analyzer = AIAnalyzer()
        if not ai_analyzer.check_connection():
            print("❌ Cannot connect to Ollama. Please ensure Ollama is running.")
            print("   Run: ollama serve")
            return
        
        skill_extractor = SkillExtractor(ai_analyzer)
        print("✅ AI analyzer ready")
    except Exception as e:
        print(f"❌ Error initializing AI analyzer: {e}")
        return
    
    # Extract skills
    print("\n🔍 Extracting comprehensive skills from resume...")
    print("   This may take 30-60 seconds...")
    try:
        skills_data = skill_extractor.extract_and_save_skills(resume.content)
        
        print(f"\n✅ Successfully extracted {skills_data['total_skills']} skills")
        print(f"   Saved to: {skill_extractor.skills_yaml_path}")
        print(f"   Extracted at: {skills_data['extracted_at']}")
        
        # Show sample skills
        print(f"\n📋 Sample Skills (first 20):")
        for i, (skill_name, skill_info) in enumerate(list(skills_data['skills'].items())[:20]):
            category = skill_info.get('category', 'Unknown')
            print(f"   {i+1:2d}. {skill_name:30s} ({category})")
        
        if skills_data['total_skills'] > 20:
            print(f"   ... and {skills_data['total_skills'] - 20} more skills")
        
    except Exception as e:
        print(f"\n❌ Error extracting skills: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()





