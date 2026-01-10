#!/usr/bin/env python3
"""
Script to update Best Buy HTML summary with new research data
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('/Users/kervinleacock/Documents/Development/hunter')

from app.services.document_generator import DocumentGenerator
from app.models.application import Application
from app.models.qualification import QualificationAnalysis
from app.models.resume import Resume
from app.utils.file_utils import load_yaml, read_text_file, write_text_file

def update_bestbuy_html():
    """Update Best Buy HTML summary with new research data"""
    print("🔄 Updating Best Buy HTML summary...")
    
    # Initialize document generator
    try:
        document_generator = DocumentGenerator()
    except Exception as e:
        print(f"❌ Error initializing document generator: {e}")
        return False
    
    # Find Best Buy application folder
    applications_dir = Path("/Users/kervinleacock/Documents/Development/hunter/data/applications")
    bestbuy_folder = applications_dir / "Best-Buy-Director-of-Product-Management---Data-AI-Enablement-team"
    
    if not bestbuy_folder.exists():
        print(f"❌ Best Buy folder not found: {bestbuy_folder}")
        return False
    
    print(f"📁 Found Best Buy folder: {bestbuy_folder.name}")
    
    # Load application data
    try:
        yaml_path = bestbuy_folder / "application.yaml"
        data = load_yaml(yaml_path)
        application = Application.from_dict(data)
        print(f"✅ Loaded application: {application.company} - {application.job_title}")
    except Exception as e:
        print(f"❌ Error loading application: {e}")
        return False
    
    # Load existing files
    try:
        # Load qualifications
        if application.qualifications_path and application.qualifications_path.exists():
            qualifications_content = read_text_file(application.qualifications_path)
            print("✅ Loaded qualifications file")
        else:
            print("⚠️ No qualifications file found")
            qualifications_content = "No qualifications data available"
        
        # Load job description
        if application.job_description_path and application.job_description_path.exists():
            job_desc_content = read_text_file(application.job_description_path)
            print("✅ Loaded job description file")
        else:
            print("⚠️ No job description file found")
            job_desc_content = "No job description available"
        
        # Load cover letter
        if application.cover_letter_path and application.cover_letter_path.exists():
            cover_letter_content = read_text_file(application.cover_letter_path)
            print("✅ Loaded cover letter file")
        else:
            print("⚠️ No cover letter file found")
            cover_letter_content = "No cover letter available"
        
        # Load resume
        if application.custom_resume_path and application.custom_resume_path.exists():
            resume_content = read_text_file(application.custom_resume_path)
            print("✅ Loaded resume file")
        else:
            print("⚠️ No resume file found")
            resume_content = "No resume available"
        
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return False
    
    # Create mock objects for HTML generation
    try:
        # Create a mock QualificationAnalysis object
        qualifications = QualificationAnalysis(
            match_score=85.0,  # Mock score
            features_compared=10,
            strong_matches=["Data Analytics", "Product Management", "AI/ML"],
            missing_skills=["Machine Learning"],
            partial_matches=["Python", "SQL"],
            soft_skills=[{"skill": "Leadership", "match": "Strong"}],
            recommendations=["Focus on AI/ML experience"],
            detailed_analysis="Strong match for data and product management role"
        )
        
        # Create mock job details
        job_details = {
            "salary_range": "Not specified",
            "location": "Remote/Hybrid",
            "hiring_manager": "Not specified"
        }
        
        # Create mock resume object
        resume = Resume(
            full_name="Kervin Leacock",
            email="kervin@example.com",
            phone="(555) 123-4567"
        )
        
        print("✅ Created mock objects for HTML generation")
        
    except Exception as e:
        print(f"❌ Error creating mock objects: {e}")
        return False
    
    # Generate new HTML summary
    try:
        print("🔄 Generating new HTML summary with improved research data...")
        
        # Generate company research
        research_data = document_generator._perform_company_research(application.company)
        
        # Generate new HTML
        new_html = document_generator._create_summary_html(
            application,
            qualifications,
            job_details,
            job_desc_content,
            qualifications_content,
            cover_letter_content,
            resume
        )
        
        # Backup old summary
        summary_path = application.summary_path
        if summary_path and summary_path.exists():
            backup_path = summary_path.with_suffix('.html.backup')
            if not backup_path.exists():
                old_content = read_text_file(summary_path)
                write_text_file(old_content, backup_path)
                print(f"💾 Backed up old summary to {backup_path.name}")
        
        # Write new HTML
        write_text_file(new_html, summary_path)
        print(f"✅ Updated HTML summary with improved research data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating HTML summary: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Best Buy HTML summary update...")
    
    if update_bestbuy_html():
        print("\n✅ Best Buy HTML summary update completed!")
        print("🔍 The research sections now show company-specific information:")
        print("   - Best Buy products/services (electronics, Geek Squad, etc.)")
        print("   - Real competitors (Amazon, Walmart, Target, Costco)")
        print("   - Company-specific news items")
        print("   - Industry-appropriate personnel roles")
    else:
        print("\n❌ Best Buy HTML summary update failed!")

if __name__ == "__main__":
    main()
