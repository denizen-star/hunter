#!/usr/bin/env python3
"""
Generate static search.html page with real data embedded
This script fetches data from the Flask app API and generates a static HTML file
that can be deployed to Netlify at hunter.kervinapps.com/search

Usage:
    python3 scripts/generate_static_search.py [filename]
    OR
    ./scripts/generate_static_search.py [filename]
    
    Default filename: search.html
    Example: python3 scripts/generate_static_search.py kpro.html

Requirements:
    - Flask app must be running on http://localhost:51003
    - requests library installed: pip3 install requests
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install it with: pip3 install requests")
    sys.exit(1)


def fetch_data_from_api(api_url='http://localhost:51003/api/applications-and-contacts'):
    """Fetch real data from Flask API endpoint"""
    try:
        print(f"Fetching data from {api_url}...")
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            raise Exception(f"API returned unsuccessful response: {data.get('error', 'Unknown error')}")
        
        print(f"✓ Successfully fetched {len(data.get('items', []))} items")
        return data.get('items', [])
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to Flask app at {api_url}")
        print("Make sure the Flask app is running: python3 app/web.py")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"ERROR: Request to {api_url} timed out")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to fetch data: {e}")
        sys.exit(1)


def load_static_template():
    """Load the static search template"""
    template_path = Path(__file__).parent.parent / 'app' / 'templates' / 'web' / 'search_static.html'
    
    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}")
        print("Please create the search_static.html template first")
        sys.exit(1)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_static_html(items, template):
    """Generate static HTML with embedded data"""
    # Convert items to JSON string, escaping for embedding in HTML/JavaScript
    # Using default=str to handle datetime objects and other non-serializable types
    items_json = json.dumps(items, indent=8, default=str)
    
    # Replace placeholder in template with embedded data
    # The placeholder should be: const allItems = {{EMBEDDED_DATA}};
    # After replacement: const allItems = [JSON data];
    html = template.replace('{{EMBEDDED_DATA}}', items_json)
    
    return html


def main():
    """Main function to generate static search page"""
    import sys
    
    # Allow custom filename via command line argument
    output_filename = sys.argv[1] if len(sys.argv) > 1 else 'search.html'
    
    print("=" * 60)
    print("Static Search Page Generator")
    print("=" * 60)
    print()
    
    # Fetch real data from API
    items = fetch_data_from_api()
    
    if not items:
        print("WARNING: No items found in API response")
        print("Generated page will show empty state")
    
    # Load template
    print("Loading static template...")
    template = load_static_template()
    print("✓ Template loaded")
    
    # Generate HTML
    print("Generating static HTML...")
    html = generate_static_html(items, template)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'static_search'
    output_dir.mkdir(exist_ok=True)
    
    # Write output file
    output_path = output_dir / output_filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Static search page generated: {output_path}")
    print()
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"Generated file: {output_path}")
    print(f"Items embedded: {len(items)}")
    print()
    print("Next steps:")
    print(f"1. Review the generated file: {output_path}")
    print(f"2. Deploy to Netlify at hunter.kervinapps.com/{output_filename.replace('.html', '')}")
    print("=" * 60)


if __name__ == '__main__':
    main()