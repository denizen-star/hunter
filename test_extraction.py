#!/usr/bin/env python3
"""Test the technology extraction"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.document_generator import DocumentGenerator

def test_extraction():
    # Read the Insight Global qualification analysis
    qual_file = Path("data/applications/Insight-Global-Head-of-Business-Intelligence/HeadofBusinessIntelligence-Qualifications.md")
    
    if not qual_file.exists():
        print(f"File not found: {qual_file}")
        return
    
    with open(qual_file, 'r') as f:
        qual_content = f.read()
    
    # Test extraction
    doc_gen = DocumentGenerator()
    technologies = doc_gen._extract_technologies_from_qual_analysis(qual_content)
    
    print("=== Technology Extraction Test ===")
    print(f"Matched: {technologies['matched']}")
    print(f"Missing: {technologies['missing']}")
    print(f"Partial: {technologies['partial']}")
    
    # Expected results based on the qualification analysis:
    expected_matched = ["Python", "AWS", "Tableau"]
    expected_missing = ["R", "MySQL", "PostgreSQL", "Oracle", "Redshift", "Docker", "Kubernetes", "Terraform", "Sisense", "Qlik", "Power BI", "Looker"]
    
    print("\n=== Expected vs Actual ===")
    print(f"Expected Matched: {expected_matched}")
    print(f"Actual Matched: {technologies['matched']}")
    print(f"Match: {set(expected_matched) == set(technologies['matched'])}")
    
    print(f"\nExpected Missing: {expected_missing}")
    print(f"Actual Missing: {technologies['missing']}")
    print(f"Match: {set(expected_missing) == set(technologies['missing'])}")

if __name__ == "__main__":
    test_extraction()
