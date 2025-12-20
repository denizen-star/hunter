#!/usr/bin/env python3
"""
Generate demo application detail pages
"""
import re
from pathlib import Path
from datetime import datetime

# Template summary page
TEMPLATE_PATH = 'data/applications/Stripe-Product-Manager-Finance-Systems/20251209120038-Summary-Stripe-Product-Manager,-Finance-Systems.html'

# Demo applications
APPS = [
    {
        'id': 'capital-finance-firm-001',
        'company': 'Capital Finance Firm',
        'job_title': 'Senior Software Engineer',
        'status': 'applied',
        'match_score': 85,
        'folder_name': 'Capital-Finance-Firm-SeniorSoftwareEngineer',
        'location': 'New York, NY',
        'salary_range': '$120,000 - $150,000'
    },
    {
        'id': 'handy-repairs-001',
        'company': 'Handy repairs',
        'job_title': 'Software Engineer',
        'status': 'company response',
        'match_score': 78,
        'folder_name': 'Handy-repairs-SoftwareEngineer',
        'location': 'San Francisco, CA',
        'salary_range': '$100,000 - $130,000'
    },
    {
        'id': 'hitech-co-001',
        'company': 'Hitech co',
        'job_title': 'Full Stack Developer',
        'status': 'scheduled interview',
        'match_score': 92,
        'folder_name': 'Hitech-co-FullStackDeveloper',
        'location': 'Austin, TX',
        'salary_range': '$110,000 - $140,000'
    },
    {
        'id': 'superstars-001',
        'company': 'Superstars',
        'job_title': 'Backend Engineer',
        'status': 'applied',
        'match_score': 80,
        'folder_name': 'Superstars-BackendEngineer',
        'location': 'Seattle, WA',
        'salary_range': '$115,000 - $145,000'
    },
    {
        'id': 'mortgage-co-001',
        'company': 'Mortgage Co',
        'job_title': 'Senior Developer',
        'status': 'pending',
        'match_score': 75,
        'folder_name': 'Mortgage-Co-SeniorDeveloper',
        'location': 'Chicago, IL',
        'salary_range': '$105,000 - $135,000'
    },
    {
        'id': 'fintech-a-co-001',
        'company': 'Fintech A co',
        'job_title': 'Software Engineer',
        'status': 'interview notes',
        'match_score': 88,
        'folder_name': 'Fintech-A-co-SoftwareEngineer',
        'location': 'Boston, MA',
        'salary_range': '$125,000 - $155,000'
    },
    {
        'id': 'fintect-b-co-001',
        'company': 'Fintect B Co',
        'job_title': 'Senior Full Stack Engineer',
        'status': 'applied',
        'match_score': 82,
        'folder_name': 'Fintect-B-Co-SeniorFullStackEngineer',
        'location': 'Denver, CO',
        'salary_range': '$130,000 - $160,000'
    },
    {
        'id': 'global-a-co-001',
        'company': 'Global a co',
        'job_title': 'Lead Software Engineer',
        'status': 'company response',
        'match_score': 90,
        'folder_name': 'Global-a-co-LeadSoftwareEngineer',
        'location': 'Remote',
        'salary_range': '$140,000 - $170,000'
    },
    {
        'id': 'justtest-001',
        'company': 'JustTest',
        'job_title': 'QA Engineer',
        'status': 'applied',
        'match_score': 70,
        'folder_name': 'JustTest-QAEngineer',
        'location': 'Portland, OR',
        'salary_range': '$95,000 - $120,000'
    }
]

# Timeline entries for each app
TIMELINES = {
    'capital-finance-firm-001': [
        {'datetime': '2025-12-18T14:20:00', 'status': 'applied', 'notes': 'Application submitted successfully. Received confirmation email from HR.'},
        {'datetime': '2025-12-15T10:30:00', 'status': 'pending', 'notes': 'Application created and prepared for submission.'}
    ],
    'handy-repairs-001': [
        {'datetime': '2025-12-19T11:45:00', 'status': 'company response', 'notes': 'Received response from hiring manager. They are interested in scheduling a phone call.'},
        {'datetime': '2025-12-17T09:30:00', 'status': 'applied', 'notes': 'Application submitted. Confirmation received.'},
        {'datetime': '2025-12-14T09:15:00', 'status': 'pending', 'notes': 'Application created.'}
    ],
    'hitech-co-001': [
        {'datetime': '2025-12-19T16:30:00', 'status': 'scheduled interview', 'notes': 'Phone screening scheduled for next week. Looking forward to discussing the role.'},
        {'datetime': '2025-12-16T14:00:00', 'status': 'company response', 'notes': 'Received positive response. They want to move forward with an interview.'},
        {'datetime': '2025-12-14T10:00:00', 'status': 'applied', 'notes': 'Application submitted successfully.'},
        {'datetime': '2025-12-13T08:00:00', 'status': 'pending', 'notes': 'Application created.'}
    ],
    'superstars-001': [
        {'datetime': '2025-12-17T09:10:00', 'status': 'applied', 'notes': 'Application submitted. Waiting for response.'},
        {'datetime': '2025-12-16T11:20:00', 'status': 'pending', 'notes': 'Application created.'}
    ],
    'mortgage-co-001': [
        {'datetime': '2025-12-17T13:45:00', 'status': 'pending', 'notes': 'Application created. Ready to submit.'}
    ],
    'fintech-a-co-001': [
        {'datetime': '2025-12-19T15:00:00', 'status': 'interview notes', 'notes': 'Completed technical interview. Discussion went well. They asked about my experience with microservices architecture.'},
        {'datetime': '2025-12-17T10:00:00', 'status': 'scheduled interview', 'notes': 'Technical interview scheduled for this week.'},
        {'datetime': '2025-12-15T11:30:00', 'status': 'company response', 'notes': 'Received call from recruiter. They are interested in moving forward.'},
        {'datetime': '2025-12-13T09:00:00', 'status': 'applied', 'notes': 'Application submitted.'},
        {'datetime': '2025-12-12T10:00:00', 'status': 'pending', 'notes': 'Application created.'}
    ],
    'fintect-b-co-001': [
        {'datetime': '2025-12-18T10:15:00', 'status': 'applied', 'notes': 'Application submitted. Received confirmation.'},
        {'datetime': '2025-12-15T14:30:00', 'status': 'pending', 'notes': 'Application created.'}
    ],
    'global-a-co-001': [
        {'datetime': '2025-12-19T12:30:00', 'status': 'company response', 'notes': 'Received email from engineering manager. They are reviewing applications and will get back soon.'},
        {'datetime': '2025-12-15T10:00:00', 'status': 'applied', 'notes': 'Application submitted successfully.'},
        {'datetime': '2025-12-11T09:00:00', 'status': 'pending', 'notes': 'Application created.'}
    ],
    'justtest-001': [
        {'datetime': '2025-12-18T15:00:00', 'status': 'applied', 'notes': 'Application submitted.'},
        {'datetime': '2025-12-18T15:00:00', 'status': 'pending', 'notes': 'Application created.'}
    ]
}

# Scrambled research content (realistic placeholder)
SCRAMBLED_RESEARCH = """# Company Research: {company}

**Company Website:** https://www.{company_lower}.com

## Company Overview & Mission
- {company} is a leading provider of innovative solutions in the technology sector, serving clients across multiple industries
- The company focuses on delivering cutting-edge products and services that drive digital transformation
- With a strong commitment to innovation and customer success, {company} has established itself as a trusted partner for businesses seeking technological advancement

## Recent News & Developments
- Recent expansion into new market segments demonstrates the company's growth trajectory
- Strategic partnerships with industry leaders have strengthened their market position
- Investment in research and development continues to drive product innovation

## Company Culture & Values
- Emphasis on collaboration, innovation, and professional development
- Commitment to diversity and inclusion in the workplace
- Strong focus on work-life balance and employee well-being

## Industry Position
- Recognized as a key player in the technology services sector
- Strong financial performance and market presence
- Active in industry associations and thought leadership initiatives

## Technology Stack & Innovation
- Utilizes modern technology platforms and development methodologies
- Invests heavily in emerging technologies and digital solutions
- Maintains a forward-thinking approach to technology adoption"""

def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y %I:%M %p EST')
    except:
        return date_str

def generate_timeline_html(timeline_entries):
    """Generate timeline HTML from entries"""
    if not timeline_entries:
        return '<div class="timeline"><p style="color: #6b7280; font-size: 14px;">No timeline entries yet.</p></div>'
    
    html = '<div class="timeline">'
    for entry in timeline_entries:
        status_class = entry['status'].lower().replace(' ', '-')
        html += f'''
            <div class="timeline-item">
                <div class="timeline-date">{format_date(entry['datetime'])}</div>
                <div class="timeline-content">
                    <div class="timeline-status status-{status_class}">{entry['status']}</div>
                    <div class="timeline-notes-content" style="margin-top: 8px; font-size: 14px; color: #000;">
                        {entry['notes']}
                    </div>
                </div>
            </div>
        '''
    html += '</div>'
    return html

def scramble_research_content(company):
    """Generate scrambled research content"""
    company_lower = company.lower().replace(' ', '').replace('-', '').replace('.', '')
    return SCRAMBLED_RESEARCH.format(company=company, company_lower=company_lower)

# Read template
template_path = Path(TEMPLATE_PATH)
if not template_path.exists():
    print(f"Template not found: {TEMPLATE_PATH}")
    exit(1)

with open(template_path, 'r', encoding='utf-8') as f:
    template_content = f.read()

# Generate pages for each app
for app in APPS:
    content = template_content
    
    # Replace company and job title
    content = content.replace('Stripe', app['company'])
    content = content.replace('Product Manager, Finance Systems', app['job_title'])
    content = content.replace('Stripe-Product-Manager-Finance-Systems', app['folder_name'])
    
    # Replace personal info
    content = content.replace('Kervin', 'Jason')
    content = content.replace('Leacock', 'Smith')
    content = content.replace('leacock.kervin@gmail.com', 'jason.smith@hunterapp.com')
    
    # Replace match score
    content = re.sub(r'data-score="\d+"', f'data-score="{app["match_score"]}"', content)
    content = re.sub(r'>\d+%<', f'>{app["match_score"]}%<', content)
    
    # Replace location and salary
    if 'location' in app:
        content = re.sub(r'<span>.*?</span>\s*</div>\s*<div class="meta-item">\s*<svg.*?salary', 
                         f'<span>{app["location"]}</span></div><div class="meta-item"><svg...salary', content, flags=re.DOTALL)
    
    # Generate timeline HTML
    timeline_entries = TIMELINES.get(app['id'], [])
    timeline_html = generate_timeline_html(timeline_entries)
    
    # Replace timeline content (find timeline div and replace)
    timeline_pattern = r'(<div id="timeline"[^>]*>)(.*?)(</div>\s*</div>\s*</div>)'
    content = re.sub(timeline_pattern, r'\1' + timeline_html + r'\3', content, flags=re.DOTALL)
    
    # Scramble research content
    scrambled_research = scramble_research_content(app['company'])
    research_pattern = r'(<div id="research"[^>]*>)(.*?)(</div>\s*</div>)'
    content = re.sub(research_pattern, r'\1<h2>Company Research</h2><div class="content-section">' + scrambled_research + r'\3', content, flags=re.DOTALL)
    
    # Disable buttons
    content = content.replace('onclick="generateIntroMessages', 'onclick="showUpgradeMessage(); return false;')
    content = content.replace('onclick="generateCustomResume()', 'onclick="showUpgradeMessage(); return false;')
    content = content.replace('Generate Hiring Manager Intro Messages', 'Generate Hiring Manager Intro Messages')
    content = content.replace('Generate Recruiter Intro Messages', 'Generate Recruiter Intro Messages')
    content = content.replace('Generate Customized Resume', 'Generate Customized Resume')
    
    # Add btn-disabled class to buttons
    content = re.sub(r'(<button[^>]*Generate.*?Messages[^>]*>)', r'\1 class="btn-disabled" title="Purchase Upgrade for Functionality"', content)
    content = re.sub(r'(<button[^>]*Generate.*?Resume[^>]*>)', r'\1 class="btn-disabled" title="Purchase Upgrade for Functionality"', content)
    content = re.sub(r'(<button[^>]*Update Status[^>]*>)', r'\1 class="btn-disabled" title="Purchase Upgrade for Functionality"', content)
    
    # Update AI status check
    content = content.replace('async function showAIStatus()', 'async function showAIStatus() { alert(\'AI Connected - Model: llama3:latest\\nStatus: Operational\'); return; } async function showAIStatus_original()')
    
    # Add demo data and upgrade handler scripts
    if '</body>' in content:
        content = content.replace('</body>', '''
    <!-- Demo Data -->
    <script src="/static/js/demo-data.js"></script>
    <!-- Upgrade Handler -->
    <script src="/static/js/upgrade-handler.js"></script>
    <script>
        function showUpgradeMessage() {
            alert('Purchase Upgrade for Functionality');
        }
    </script>
</body>''')
    
    # Write to file
    output_dir = Path(f'hunterapp_demo/applications/{app["folder_name"]}')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'index.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated: {output_file}")

print("All application detail pages generated!")
