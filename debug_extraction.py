#!/usr/bin/env python3
"""Debug the technology extraction"""
import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_extraction():
    # Read the Insight Global qualification analysis
    qual_file = Path("data/applications/Insight-Global-Head-of-Business-Intelligence/HeadofBusinessIntelligence-Qualifications.md")
    
    with open(qual_file, 'r') as f:
        qual_content = f.read()
    
    # Find the Technologies & Tools section
    tech_section_match = re.search(
        r'\*\*Technologies & Tools\*\*.*?(?=\*\*[A-Z]|\Z)',
        qual_content,
        re.DOTALL
    )
    
    if not tech_section_match:
        print("No Technologies & Tools section found!")
        return
    
    tech_section = tech_section_match.group(0)
    print("=== Technologies & Tools Section ===")
    print(tech_section)
    print("\n=== Lines ===")
    
    lines = tech_section.split('\n')
    for i, line in enumerate(lines):
        print(f"Line {i}: '{line}'")
        
        if line.strip() and not line.startswith('**') and not line.startswith('|'):
            # Match pattern: "- Technology: ✓" or "- Technology: ✗"
            match = re.search(r'-\s+([^:]+):\s*([✓✗⚠])', line)
            if match:
                tech_name = match.group(1).strip()
                symbol = match.group(2).strip()
                print(f"  -> MATCH: '{tech_name}' = '{symbol}'")
            else:
                print(f"  -> NO MATCH for pattern")

if __name__ == "__main__":
    debug_extraction()
