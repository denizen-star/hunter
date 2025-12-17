import re
from pathlib import Path

files = [
    'app/services/networking_processor.py',
    'app/web.py',
    'fix_all_paths.py',
    'fix_research_and_intros.py',
    'interactive_research_fix.py',
    'migrate_existing_applications.py',
    'regenerate_bestbuy.py',
    'resume_research_fix.py',
    'simple_migration.py',
    'update_bestbuy_html.py'
]

for file in files:
    filepath = Path(file)
    if not filepath.exists():
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the absolute path prefix
    content = content.replace('/Users/kervinleacock/Documents/Development/hunter/', '')
    content = content.replace('/Users/kervinleacock/Documents/Development/hunter', '')
    
    # Remove sys.path lines
    content = re.sub(r"sys\.path\.(append|insert)\([^)]*kervinleacock[^)]*\)", '# sys.path not needed', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {file}")

print("\nDone! Verify with: findstr /s /i \"kervinleacock\" *.py")
