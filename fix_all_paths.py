"""
Comprehensive script to fix ALL hardcoded paths in Hunter
This will replace all absolute paths with relative paths
"""
import os
import re
from pathlib import Path

def fix_all_hardcoded_paths():
    """Fix hardcoded paths in all Python files"""
    
    # Define the files that need fixing based on the search results
    files_to_fix = [
        'app/services/preliminary_matcher.py',
        'fix_paths.py',
        'fix_research_and_intros.py',
        'interactive_research_fix.py',
        'regenerate_research.py',
        'migrate_existing_applications.py',
        'process_insight_global.py',
        'process_next_application.py',
        'regenerate_bestbuy.py',
        'resume_research_fix.py',
        'simple_migration.py',
        'update_bestbuy_html.py'
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"⊗ Skipping {file_path} (not found)")
            continue
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace all variations of the hardcoded path
            # Pattern 1: 
            content = re.sub(
                r'',
                '',
                content
            )
            
            # Pattern 2: For sys.path.append and sys.path.insert
            content = re.sub(
                r"sys\.path\.(append|insert)\([^,]*,\s*['\"]\/Users\/kervinleacock\/Documents\/Development\/hunter['\"]",
                r"# sys.path.\1 not needed with relative paths",
                content
            )
            
            # Pattern 3: Path objects with absolute paths
            content = re.sub(
                r'Path\(["\']\/Users\/kervinleacock\/Documents\/Development\/hunter\/',
                'Path("',
                content
            )
            
            # Pattern 4: String literals with absolute paths
            content = re.sub(
                r'["\']\/Users\/kervinleacock\/Documents\/Development\/hunter\/',
                '"',
                content
            )
            
            # Pattern 5: Fix name_clean assignments (for KervinLeacock references)
            content = re.sub(
                r'name_clean\s*=\s*["\']KervinLeacock["\']',
                'name_clean = "Rhetta_Chappell"',
                content
            )
            
            # Pattern 6: Filenames with KervinLeacock
            content = re.sub(
                r'KervinLeacock-',
                'RhettaChappell-',
                content
            )
            content = re.sub(
                r'kervinleacock-',
                'rhettachappell-',
                content
            )
            
            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Fixed {file_path}")
                fixed_count += 1
            else:
                print(f"○ No changes needed for {file_path}")
                
        except Exception as e:
            print(f"✗ Error fixing {file_path}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} files")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Run: python -m app.web")
    print("2. Your Hunter application should now start successfully!")

if __name__ == '__main__':
    print("Fixing all hardcoded paths in Hunter...\n")
    fix_all_hardcoded_paths()
