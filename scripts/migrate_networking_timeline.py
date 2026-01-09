#!/usr/bin/env python3
"""
Migration script to update existing application summary HTML files:
1. Add sidebar navigation menu to match standard menu
2. Classify existing timeline entries as 'application' type (they're all application updates)
3. Update tab names to new format

This script is idempotent - safe to run multiple times.
"""

import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.job_processor import JobProcessor
from app.utils.file_utils import read_text_file, write_text_file

def update_sidebar_menu(html_content: str) -> str:
    """Update sidebar menu to match standard menu structure"""
    # Find the sidebar menu section
    sidebar_pattern = r'(<ul class="sidebar-menu">.*?</ul>)'
    
    standard_menu = '''        <ul class="sidebar-menu">
            <li><a href="/dashboard" class="nav-link">App Dash</a></li>
            <li><a href="/new-application" class="nav-link">New Application</a></li>
            <li><a href="/networking" class="nav-link">Network Dash</a></li>
            <li><a href="/new-networking-contact" class="nav-link">New Contact</a></li>
            <li><a href="/templates" class="nav-link">Templates</a></li>
            <li><a href="/reports" class="nav-link">Reports</a></li>
            <li><a href="/analytics" class="nav-link">Analytics</a></li>
            <li><a href="/daily-activities" class="nav-link">Daily Activities</a></li>
            <li><a href="#" onclick="showAIStatus(); return false;" class="nav-link">Check AI Status</a></li>
            <li><a href="/new-application?resume=true" class="nav-link">Manage Resume</a></li>
        </ul>'''
    
    # Replace existing sidebar menu
    if re.search(sidebar_pattern, html_content, re.DOTALL):
        html_content = re.sub(sidebar_pattern, standard_menu, html_content, flags=re.DOTALL)
    
    return html_content

def update_tab_names(html_content: str) -> str:
    """Update tab names to new format"""
    # Rename tabs
    replacements = [
        (r'>Job Description<', '>JD<'),
        (r'>Qualifications Analysis<', '>Qualifications<'),
        (r'>Customized Resume<', '>Custom Resume<'),
        (r'>Updates & Notes<', '>Updates<'),
        (r'Updates &amp; Notes', 'Updates'),
    ]
    
    for old, new in replacements:
        html_content = html_content.replace(old, new)
    
    return html_content

def add_networking_and_timeline_tabs(html_content: str) -> str:
    """Add Networking and Timeline tabs if they don't exist"""
    # Check if Networking tab already exists
    if 'onclick="showTab(this, \'networking\')">Networking</button>' in html_content:
        return html_content  # Already has the tabs
    
    # Find the Updates tab button
    updates_tab_pattern = r'(<button type="button" class="tab" onclick="showTab\(this, \'updates\'\)">Updates</button>)'
    
    # Add Networking tab before Updates, Timeline tab after Updates
    networking_tab = '<button type="button" class="tab" onclick="showTab(this, \'networking\')">Networking</button>\n            '
    timeline_tab = '\n            <button type="button" class="tab" onclick="showTab(this, \'timeline\')">Timeline</button>'
    
    if re.search(updates_tab_pattern, html_content):
        # Insert Networking tab before Updates
        html_content = re.sub(
            updates_tab_pattern,
            networking_tab + r'\1' + timeline_tab,
            html_content
        )
    
    return html_content

def update_networking_tab_height(html_content: str) -> str:
    """Update networking tab container to use position:fixed for full viewport height"""
    # Pattern to match networking-summary-container with various height styles
    # Update to use position:fixed approach for full viewport coverage
    
    # Match container with old height calculation or margin-top
    old_patterns = [
        (r'<div id="networking-summary-container" style="[^"]*margin-top:\s*20px[^"]*height:\s*calc\(100vh\s*-\s*\d+px\)[^"]*"', 
         '<div id="networking-summary-container" style="display: none; position: fixed; top: 0; left: 180px; right: 0; bottom: 0; background: white; z-index: 1000; flex-direction: column; overflow: hidden;">'),
        (r'<div id="networking-summary-container" style="[^"]*height:\s*calc\(100vh\s*-\s*\d+px\)[^"]*"',
         '<div id="networking-summary-container" style="display: none; position: fixed; top: 0; left: 180px; right: 0; bottom: 0; background: white; z-index: 1000; flex-direction: column; overflow: hidden;">'),
    ]
    
    for pattern, replacement in old_patterns:
        if re.search(pattern, html_content):
            html_content = re.sub(pattern, replacement, html_content)
            break
    
    # Update header div to remove border-radius and adjust styling
    header_pattern = r'(<div style="display: flex; justify-content: space-between; align-items: center;[^"]*margin-bottom:\s*16px[^"]*padding:\s*16px\s*24px[^"]*background:\s*white[^"]*border-radius:\s*8px\s*8px\s*0\s*0[^"]*border:\s*1px\s*solid\s*#e5e7eb[^"]*border-bottom:\s*none[^"]*flex-shrink:\s*0[^"]*")'
    new_header = '<div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; flex-shrink: 0; background: white;">'
    html_content = re.sub(header_pattern, new_header, html_content)
    
    # Update content div to use position: relative for absolute iframe positioning
    content_pattern = r'(<div id="networking-summary-content" style="[^"]*border-radius:\s*0\s*0\s*8px\s*8px[^"]*border:\s*1px\s*solid\s*#e5e7eb[^"]*border-top:\s*none[^"]*")'
    new_content = '<div id="networking-summary-content" style="flex: 1; overflow: hidden; min-height: 0; position: relative;">'
    html_content = re.sub(content_pattern, new_content, html_content)
    
    # Also update content div if it has display: flex
    content_pattern2 = r'(<div id="networking-summary-content" style="[^"]*display:\s*flex[^"]*flex-direction:\s*column[^"]*")'
    new_content2 = '<div id="networking-summary-content" style="flex: 1; overflow: hidden; min-height: 0; position: relative;">'
    html_content = re.sub(content_pattern2, new_content2, html_content)
    
    # Ensure iframe uses absolute positioning to fill container
    def update_iframe(match):
        full_match = match.group(0)
        # Remove old positioning/sizing properties
        style_attr = re.search(r'style="([^"]*)"', full_match)
        if style_attr:
            style = style_attr.group(1)
            # Remove old properties
            style = re.sub(r'position:\s*[^;]+;?', '', style)
            style = re.sub(r'top:\s*[^;]+;?', '', style)
            style = re.sub(r'left:\s*[^;]+;?', '', style)
            style = re.sub(r'width:\s*[^;]+;?', '', style)
            style = re.sub(r'height:\s*[^;]+;?', '', style)
            style = re.sub(r'flex:\s*[^;]+;?', '', style)
            style = re.sub(r'min-height:\s*[^;]+;?', '', style)
            style = re.sub(r'display:\s*[^;]+;?', '', style)
            # Clean up extra semicolons and spaces
            style = re.sub(r';\s*;+', ';', style)
            style = style.strip('; ')
            # Add new absolute positioning
            if 'position: absolute' not in style:
                style = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; ' + style
            return full_match.replace(style_attr.group(0), f'style="{style}"')
        return full_match
    
    html_content = re.sub(r'<iframe[^>]*style="[^"]*"[^>]*>', update_iframe, html_content)
    
    # Update JavaScript to use display: flex instead of display: block
    # Fix networking-summary-container display
    html_content = re.sub(
        r"document\.getElementById\('networking-summary-container'\)\.style\.display\s*=\s*['\"]block['\"]",
        "document.getElementById('networking-summary-container').style.display = 'flex'",
        html_content
    )
    
    # Remove scrollIntoView calls for fixed position container
    html_content = re.sub(
        r'\s*// Scroll to summary\s*document\.getElementById\([\'"]networking-summary-container[\'"]\)\.scrollIntoView\([^)]+\);\s*',
        '',
        html_content
    )
    
    return html_content

def migrate_application_summary(summary_path: Path) -> bool:
    """Migrate a single application summary HTML file"""
    try:
        if not summary_path.exists():
            return False
        
        html_content = read_text_file(summary_path)
        original_content = html_content
        
        # Update sidebar menu
        html_content = update_sidebar_menu(html_content)
        
        # Update tab names
        html_content = update_tab_names(html_content)
        
        # Add Networking and Timeline tabs (if not already present)
        html_content = add_networking_and_timeline_tabs(html_content)
        
        # Update networking tab to use full viewport height
        html_content = update_networking_tab_height(html_content)
        
        # Only write if content changed
        if html_content != original_content:
            write_text_file(html_content, summary_path)
            return True
        
        return False
    except Exception as e:
        print(f"  ❌ Error migrating {summary_path.name}: {e}")
        return False

def main():
    """Main migration function"""
    print("=" * 60)
    print("Migrating Application Summary Files")
    print("=" * 60)
    print()
    
    job_processor = JobProcessor()
    applications = job_processor.list_all_applications()
    
    if not applications:
        print("No applications found to migrate.")
        return
    
    print(f"Found {len(applications)} applications to migrate...")
    print()
    
    migrated_count = 0
    skipped_count = 0
    
    for app in applications:
        if not app.summary_path or not Path(app.summary_path).exists():
            print(f"  ⚠️  Skipping {app.company} - {app.job_title} (no summary file)")
            skipped_count += 1
            continue
        
        print(f"  🔄 Migrating {app.company} - {app.job_title}...")
        summary_path = Path(app.summary_path)
        
        if migrate_application_summary(summary_path):
            print(f"     ✅ Updated")
            migrated_count += 1
        else:
            print(f"     ⏭️  Already up to date")
            skipped_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Migration complete!")
    print(f"   Updated: {migrated_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total: {len(applications)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
