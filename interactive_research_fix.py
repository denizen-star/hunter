#!/usr/bin/env python3
"""
Interactive script to fix research data one application at a time
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('')

from app.services.document_generator import DocumentGenerator
from app.models.application import Application
from app.models.qualification import QualificationAnalysis
from app.models.resume import Resume
from app.utils.file_utils import load_yaml, save_yaml, read_text_file, write_text_file

def show_research_data(application, research_data):
    """Display research data for user review"""
    print(f"\n{'='*80}")
    print(f"🔍 RESEARCH DATA FOR: {application.company}")
    print(f"📋 Job: {application.job_title}")
    print(f"{'='*80}")
    
    # Mission & Vision
    print(f"\n🎯 MISSION & VISION:")
    print(f"Mission: {research_data.get('mission', 'Not found')}")
    print(f"Vision: {research_data.get('vision', 'Not found')}")
    
    # Products & Services
    print(f"\n🏢 PRODUCTS & SERVICES:")
    print(f"{research_data.get('products_services', 'Not found')}")
    
    # Competitors
    print(f"\n⚔️ COMPETITORS:")
    print(f"{research_data.get('competitors', 'Not found')}")
    
    # News
    print(f"\n📰 LATEST NEWS:")
    news_items = research_data.get('news', [])
    if news_items:
        for i, news in enumerate(news_items[:3], 1):  # Show first 3
            print(f"{i}. {news.get('title', 'No title')}")
            print(f"   {news.get('summary', 'No summary')}")
            print(f"   Source: {news.get('source', 'Unknown')}")
    else:
        print("No news found")
    
    # Personnel
    print(f"\n👥 KEY PERSONNEL:")
    personnel = research_data.get('personnel', [])
    if personnel:
        for i, person in enumerate(personnel[:3], 1):  # Show first 3
            print(f"{i}. {person.get('name', 'Unknown')} - {person.get('title', 'Unknown title')}")
    else:
        print("No personnel found")
    
    print(f"\n{'='*80}")

def fix_single_application(application_folder):
    """Fix research data for a single application with user approval"""
    try:
        print(f"\n🔧 Processing: {application_folder.name}")
        
        # Initialize document generator
        document_generator = DocumentGenerator()
        
        # Load application data
        yaml_path = application_folder / "application.yaml"
        data = load_yaml(yaml_path)
        application = Application.from_dict(data)
        
        print(f"  📋 {application.company} - {application.job_title}")
        
        # Generate real company research
        print("  🔍 Generating real company research...")
        research_data = document_generator._perform_company_research(application.company)
        
        # Show research data to user
        show_research_data(application, research_data)
        
        # Ask for approval
        while True:
            response = input(f"\n❓ Do you approve this research data for {application.company}? (y/n/s to skip): ").lower().strip()
            if response in ['y', 'yes']:
                print("  ✅ Research data approved!")
                return True
            elif response in ['n', 'no']:
                print("  ❌ Research data rejected!")
                return False
            elif response in ['s', 'skip']:
                print("  ⏭️ Skipping this application...")
                return None
            else:
                print("  Please enter 'y' for yes, 'n' for no, or 's' to skip")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Main function to process applications interactively"""
    print("🚀 Interactive Research Data Fix")
    print("This will show you the research data for each application and let you approve or decline it.")
    
    # Get all application folders
    applications_dir = Path("data/applications")
    if not applications_dir.exists():
        print(f"❌ Applications directory not found: {applications_dir}")
        return
    
    application_folders = [f for f in applications_dir.iterdir() if f.is_dir()]
    print(f"📁 Found {len(application_folders)} application folders")
    
    # Track results
    approved_count = 0
    rejected_count = 0
    skipped_count = 0
    
    # Process each application
    for i, folder in enumerate(application_folders, 1):
        print(f"\n📊 Progress: {i}/{len(application_folders)}")
        
        try:
            result = fix_single_application(folder)
            if result is True:
                approved_count += 1
            elif result is False:
                rejected_count += 1
            else:  # None (skipped)
                skipped_count += 1
        except Exception as e:
            print(f"❌ Failed to process {folder.name}: {e}")
            rejected_count += 1
    
    # Summary
    print(f"\n🎯 Final Summary:")
    print(f"  ✅ Approved: {approved_count}")
    print(f"  ❌ Rejected: {rejected_count}")
    print(f"  ⏭️ Skipped: {skipped_count}")
    print(f"  📊 Total: {len(application_folders)}")

if __name__ == "__main__":
    main()












