#!/usr/bin/env python3
"""
Generate all demo HTML pages for Hunter demo version
"""
import os
from pathlib import Path
from datetime import datetime, timedelta

# Demo data
DEMO_APPLICATIONS = [
    {
        'id': 'capital-finance-firm-001',
        'company': 'Capital Finance Firm',
        'job_title': 'Senior Software Engineer',
        'status': 'applied',
        'match_score': 85,
        'applied_at': '2025-12-15T10:30:00',
        'updated_at': '2025-12-18T14:20:00',
        'location': 'New York, NY',
        'salary_range': '$120,000 - $150,000',
        'folder_name': 'Capital-Finance-Firm-SeniorSoftwareEngineer',
        'posted_date': '2025-12-10',
        'flagged': False
    },
    {
        'id': 'handy-repairs-001',
        'company': 'Handy repairs',
        'job_title': 'Software Engineer',
        'status': 'company response',
        'match_score': 78,
        'applied_at': '2025-12-14T09:15:00',
        'updated_at': '2025-12-19T11:45:00',
        'location': 'San Francisco, CA',
        'salary_range': '$100,000 - $130,000',
        'folder_name': 'Handy-repairs-SoftwareEngineer',
        'posted_date': '2025-12-08',
        'flagged': False
    },
    {
        'id': 'hitech-co-001',
        'company': 'Hitech co',
        'job_title': 'Full Stack Developer',
        'status': 'scheduled interview',
        'match_score': 92,
        'applied_at': '2025-12-13T08:00:00',
        'updated_at': '2025-12-19T16:30:00',
        'location': 'Austin, TX',
        'salary_range': '$110,000 - $140,000',
        'folder_name': 'Hitech-co-FullStackDeveloper',
        'posted_date': '2025-12-05',
        'flagged': True
    },
    {
        'id': 'superstars-001',
        'company': 'Superstars',
        'job_title': 'Backend Engineer',
        'status': 'applied',
        'match_score': 80,
        'applied_at': '2025-12-16T11:20:00',
        'updated_at': '2025-12-17T09:10:00',
        'location': 'Seattle, WA',
        'salary_range': '$115,000 - $145,000',
        'folder_name': 'Superstars-BackendEngineer',
        'posted_date': '2025-12-12',
        'flagged': False
    },
    {
        'id': 'mortgage-co-001',
        'company': 'Mortgage Co',
        'job_title': 'Senior Developer',
        'status': 'pending',
        'match_score': 75,
        'applied_at': '2025-12-17T13:45:00',
        'updated_at': '2025-12-17T13:45:00',
        'location': 'Chicago, IL',
        'salary_range': '$105,000 - $135,000',
        'folder_name': 'Mortgage-Co-SeniorDeveloper',
        'posted_date': '2025-12-15',
        'flagged': False
    },
    {
        'id': 'fintech-a-co-001',
        'company': 'Fintech A co',
        'job_title': 'Software Engineer',
        'status': 'interview notes',
        'match_score': 88,
        'applied_at': '2025-12-12T10:00:00',
        'updated_at': '2025-12-19T15:00:00',
        'location': 'Boston, MA',
        'salary_range': '$125,000 - $155,000',
        'folder_name': 'Fintech-A-co-SoftwareEngineer',
        'posted_date': '2025-12-03',
        'flagged': False
    },
    {
        'id': 'fintect-b-co-001',
        'company': 'Fintect B Co',
        'job_title': 'Senior Full Stack Engineer',
        'status': 'applied',
        'match_score': 82,
        'applied_at': '2025-12-15T14:30:00',
        'updated_at': '2025-12-18T10:15:00',
        'location': 'Denver, CO',
        'salary_range': '$130,000 - $160,000',
        'folder_name': 'Fintect-B-Co-SeniorFullStackEngineer',
        'posted_date': '2025-12-10',
        'flagged': False
    },
    {
        'id': 'global-a-co-001',
        'company': 'Global a co',
        'job_title': 'Lead Software Engineer',
        'status': 'company response',
        'match_score': 90,
        'applied_at': '2025-12-11T09:00:00',
        'updated_at': '2025-12-19T12:30:00',
        'location': 'Remote',
        'salary_range': '$140,000 - $170,000',
        'folder_name': 'Global-a-co-LeadSoftwareEngineer',
        'posted_date': '2025-12-01',
        'flagged': False
    },
    {
        'id': 'justtest-001',
        'company': 'JustTest',
        'job_title': 'QA Engineer',
        'status': 'applied',
        'match_score': 70,
        'applied_at': '2025-12-18T15:00:00',
        'updated_at': '2025-12-18T15:00:00',
        'location': 'Portland, OR',
        'salary_range': '$95,000 - $120,000',
        'folder_name': 'JustTest-QAEngineer',
        'posted_date': '2025-12-16',
        'flagged': False
    },
    {
        'id': 'medical-network-co-001',
        'company': 'Medical Network Co',
        'job_title': 'Software Developer',
        'status': 'pending',
        'match_score': 72,
        'applied_at': '2025-12-19T08:30:00',
        'updated_at': '2025-12-19T08:30:00',
        'location': 'Philadelphia, PA',
        'salary_range': '$100,000 - $125,000',
        'folder_name': 'Medical-Network-Co-SoftwareDeveloper',
        'posted_date': '2025-12-17',
        'flagged': False
    }
]

def format_date(date_str):
    """Format ISO date string for display"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y')
    except:
        return date_str

def status_to_class(status):
    """Convert status to CSS class"""
    return status.lower().replace(' ', '-').replace('_', '-')

def create_app_card(app):
    """Create HTML for application card"""
    match_score_html = f'<span class="match-score">{app["match_score"]:.0f}%</span>' if app.get('match_score') else ''
    flag_icon = '🚩' if app.get('flagged') else '⚐'
    flag_class = 'flagged' if app.get('flagged') else 'unflagged'
    summary_link = f'/applications/{app["folder_name"]}/index.html'
    
    return f'''
        <div class="card" 
             data-updated-at="{app["updated_at"]}" 
             data-applied-at="{app["applied_at"]}" 
             data-match-score="{app.get("match_score", 0)}"
             data-flagged="{str(app.get("flagged", False)).lower()}">
            <div class="card-header">
                <div class="card-company">
                    {app["company"]}
                    {match_score_html}
                </div>
                <button class="flag-btn {flag_class}" 
                        onclick="return false;" 
                        title="Flag this job">
                    {flag_icon}
                </button>
            </div>
            <div class="card-title">{app["job_title"]}</div>
            <div class="card-status-container">
                <span class="card-status status-{status_to_class(app["status"])}">{app["status"]}</span>
            </div>
            <div class="card-meta">
                📅 Applied: {format_date(app["applied_at"])}
            </div>
            <div class="card-meta">
                📋 Posted: {app.get("posted_date", "N/A")}
            </div>
            <div class="card-meta">
                🔄 Updated: {format_date(app["updated_at"])}
            </div>
            <div class="card-actions">
                <a href="{summary_link}" class="card-btn">View Summary →</a>
            </div>
        </div>
    '''

# This is a placeholder - the full implementation will be in the next step
# For now, let's create a basic structure
print("Demo page generator script created")
