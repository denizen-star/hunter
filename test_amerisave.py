#!/usr/bin/env python3
"""Test the technology extraction with AmeriSave"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.document_generator import DocumentGenerator

def test_amerisave():
    # Read the AmeriSave qualification analysis
    qual_file = Path("data/applications/AmeriSave-Mortgage-Corporation-Director-of-Analytics-Performance-Measurement/DirectorofAnalyticsPerformanceMeasurement-Qualifications.md")
    
    if not qual_file.exists():
        print(f"File not found: {qual_file}")
        return
    
    with open(qual_file, 'r') as f:
        qual_content = f.read()
    
    # Test extraction
    doc_gen = DocumentGenerator()
    technologies = doc_gen._extract_technologies_from_qual_analysis(qual_content)
    
    print("=== AmeriSave Technology Extraction Test ===")
    print(f"Matched: {technologies['matched']}")
    print(f"Missing: {technologies['missing']}")
    print(f"Partial: {technologies['partial']}")

if __name__ == "__main__":
    test_amerisave()
