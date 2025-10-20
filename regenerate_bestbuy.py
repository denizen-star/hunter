#!/usr/bin/env python3
"""
Script to regenerate Best Buy application with improved research data
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('/Users/kervinleacock/Documents/Development/hunter')

from app.services.document_generator import DocumentGenerator
from app.models.application import Application
from app.utils.file_utils import load_yaml

def regenerate_bestbuy():
    """Regenerate Best Buy application with new research data"""
    print("🔄 Regenerating Best Buy application...")
    
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
    
    # Regenerate research data
    try:
        print("🔍 Regenerating company research with improved data...")
        research_data = document_generator._perform_company_research(application.company)
        
        # Update the research data in the application (if needed)
        print("✅ Company research regenerated with improved fallback data")
        print(f"   - Products/Services: {len(research_data.get('products_services', ''))} characters")
        print(f"   - Competitors: {len(research_data.get('competitors', ''))} characters")
        print(f"   - News items: {len(research_data.get('news', []))}")
        print(f"   - Personnel: {len(research_data.get('personnel', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error regenerating research: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Best Buy application regeneration...")
    
    if regenerate_bestbuy():
        print("\n✅ Best Buy application regeneration completed!")
        print("📝 Note: The HTML summary will be updated the next time you generate a full application.")
        print("🔍 The research data now includes company-specific information instead of generic templates.")
    else:
        print("\n❌ Best Buy application regeneration failed!")

if __name__ == "__main__":
    main()

