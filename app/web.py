#!/usr/bin/env python3
"""
Web UI for Job Hunting Follow-Ups
Flask application providing REST API and web interface
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from werkzeug.utils import secure_filename

from app.services.resume_manager import ResumeManager
from app.services.job_processor import JobProcessor
from app.services.ai_analyzer import AIAnalyzer
from app.services.document_generator import DocumentGenerator
from app.services.dashboard_generator import DashboardGenerator
from app.services.template_manager import TemplateManager
from app.services.analytics_generator import AnalyticsGenerator
from app.services.networking_processor import NetworkingProcessor
from app.services.networking_document_generator import NetworkingDocumentGenerator
from app.services.activity_log_service import ActivityLogService
from app.services.contact_count_cache import ContactCountCache
from app.utils.datetime_utils import format_for_display
from app.utils.file_utils import get_project_root, get_data_path
from app.utils.cache_utils import is_cache_stale, get_cached_json, save_cached_json
from app.utils.input_sanitizer import sanitize_text, sanitize_email, sanitize_phone

app = Flask(__name__, 
           template_folder='templates/web',
           static_folder='../static',
           static_url_path='/static')
CORS(app)

# #region agent log
import json
import time
# Debug logging disabled - .cursor directory has special protections
# with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
#     f.write(json.dumps({"location":"web.py:init","message":"Starting service initialization","data":{},"timestamp":time.time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"C"}) + '\n')
# #endregion

# Initialize services
resume_manager = ResumeManager()
job_processor = JobProcessor()
ai_analyzer = AIAnalyzer()
doc_generator = DocumentGenerator()
dashboard_generator = DashboardGenerator()
template_manager = TemplateManager()
analytics_generator = AnalyticsGenerator()
activity_log_service = ActivityLogService()

# #region agent log
# Debug logging disabled - .cursor directory has special protections
# with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
#     f.write(json.dumps({"location":"web.py:init","message":"About to initialize NetworkingProcessor","data":{},"timestamp":time.time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"C"}) + '\n')
# #endregion

networking_processor = NetworkingProcessor()
networking_doc_generator = NetworkingDocumentGenerator()
contact_count_cache = ContactCountCache()

# #region agent log
# Debug logging disabled - .cursor directory has special protections
# with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
#     f.write(json.dumps({"location":"web.py:init","message":"All services initialized successfully","data":{},"timestamp":time.time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"C"}) + '\n')
# #endregion

STATUS_NORMALIZATION_MAP = {
    'contacted hiring manager': 'company response',
    'company response': 'company response',
    'interviewed': 'interview notes',
    'interview notes': 'interview notes',
    'interview follow up': 'interview - follow up',
    'interview follow-up': 'interview - follow up',
    'interview - follow up': 'interview - follow up',
}


def normalize_status_label(status: str) -> str:
    """Normalize status strings for consistent downstream reporting."""
    if not status:
        return ''
    normalized = status.strip().lower()
    normalized = normalized.replace('–', '-').replace('—', '-')
    normalized = normalized.replace('  ', ' ')
    return STATUS_NORMALIZATION_MAP.get(normalized, normalized)


def _extract_status_from_name_status(status: str) -> str:
    """Extract status from name-status format (e.g., 'Name-Status' -> 'Status').
    
    This handles statuses that may contain person names or other prefixes
    separated by dashes. Returns the normalized status portion.
    """
    if not status:
        return status
    
    parts = status.replace('---', '-').replace('--', '-').split('-')
    status_keywords = ['contacted', 'sent', 'research', 'conversation', 'pending', 
                      'inactive', 'dormant', 'ready', 'new', 'connection', 'archive', 'cold', 'to', 'action']
    
    # If status has multiple parts and contains status keywords, normalize it
    if len(parts) > 1:
        for part in reversed(parts):
            part_lower = part.lower()
            if any(keyword in part_lower for keyword in status_keywords):
                return part.replace('-', ' ').strip()
        else:
            # If no keyword found in any part, use last part
            return parts[-1].replace('-', ' ').strip()
    
    return status


def is_networking_status(status: str) -> bool:
    """Check if a status is a networking-related status (vs job application status)"""
    if not status:
        return False
    status_lower = status.lower().strip()
    
    # Clear networking status indicators (these are definitely networking)
    clear_networking_indicators = [
        'contacted sent', 'contacted---sent', 'ready to contact', 'to research', 'found contact',
        'sent linkedin connection', 'sent email', 'connection accepted',
        'in conversation', 'conversation', 'action pending', 'new connection',
        'cold', 'archive', 'dormant', 'inactive', 'research', 'sent'
    ]
    
    # Check for clear networking indicators first
    if any(indicator in status_lower for indicator in clear_networking_indicators):
        return True
    
    # Job application statuses that should NOT be grouped
    job_statuses = [
        'applied', 'rejected', 'accepted', 'offered',
        'interview notes', 'interview follow up', 'scheduled interview',
        'company response', 'contacted hiring manager', 'contacted someone'
    ]
    
    # If it's a clear job status, it's not networking
    if any(job_status in status_lower for job_status in job_statuses):
        return False
    
    # Ambiguous: "Contacted" alone could be job or networking
    # But "Contacted Sent" is networking (already caught above)
    # "Pending" alone is ambiguous - check if it's "Action Pending" (networking)
    if status_lower == 'contacted':
        # "Contacted" without "Someone" or "Hiring Manager" is likely networking
        return True
    
    # If we get here, it's likely not a networking status
    return False


def categorize_networking_status(status: str) -> str:
    """
    Categorize networking statuses into new pipeline phases.
    
    New Categories:
    1. Prospecting: Initial research and preparation
    2. Outreach: Initial contact and response tracking
    3. Engagement: Active communication and meetings
    4. Nurture: Ongoing relationship maintenance
    
    Returns the category name, or the original status if not a networking status.
    """
    if not status:
        return status
    
    status_lower = status.lower().strip()
    
    # PROSPECTING category - new status system
    prospecting_statuses = [
        'found contact',  # New name
        'sent linkedin connection',  # New name
        'to research',  # Old name (backward compatibility)
        'ready to connect',  # Old name (backward compatibility)
        # Legacy support
        'ready to contact'
    ]
    
    # OUTREACH category - new status system
    outreach_statuses = [
        'sent email',  # New name
        'connection accepted',  # New name
        'pending reply',  # Old name (backward compatibility)
        'connected - initial',  # Old name (backward compatibility)
        'cold/inactive',
        # Legacy support
        'contacted - sent',
        'contacted---sent',
        'contacted sent',
        'contacted - replied',
        'contacted---replied',
        'contacted replied',
        'contacted - no response',
        'contacted---no response',
        'contacted no response',
        'new connection',
        'cold/archive'
    ]
    
    # ENGAGEMENT category - new status system
    engagement_statuses = [
        'in conversation',
        'meeting scheduled',
        'meeting complete',
        # Legacy support
        'action pending - you',
        'action pending---you',
        'action pending you',
        'action pending - them',
        'action pending---them',
        'action pending them',
        'action pending',
        'conversation'
    ]
    
    # NURTURE category - new status system
    nurture_statuses = [
        'strong connection',
        'referral partner',
        'dormant',
        # Legacy support
        'nurture (1-3 mo.)',
        'nurture (4-6 mo.)',
        'nurture 1-3 mo',
        'nurture 4-6 mo',
        'inactive/dormant',
        'referral'
    ]
    
    # Normalize status for comparison (handle variations)
    normalized_for_match = status_lower.replace('  ', ' ').replace('---', ' - ')
    
    # Check each category in order
    for prospecting_status in prospecting_statuses:
        if prospecting_status in normalized_for_match or prospecting_status in status_lower:
            return 'Prospecting'
    
    for outreach_status in outreach_statuses:
        if outreach_status in normalized_for_match or outreach_status in status_lower:
            return 'Outreach'
    
    for engagement_status in engagement_statuses:
        if engagement_status in normalized_for_match or engagement_status in status_lower:
            return 'Engagement'
    
    for nurture_status in nurture_statuses:
        if nurture_status in normalized_for_match or nurture_status in status_lower:
            return 'Nurture'
    
    # Fallback: keyword-based matching for variations not in the exact list
    if 'research' in status_lower and 'to' in status_lower:
        return 'Prospecting'
    if 'ready' in status_lower and ('connect' in status_lower or 'contact' in status_lower):
        return 'Prospecting'
    
    if 'pending' in status_lower and 'reply' in status_lower:
        return 'Outreach'
    if 'connected' in status_lower and 'initial' in status_lower:
        return 'Outreach'
    if 'cold' in status_lower or 'inactive' in status_lower:
        return 'Outreach'
    if 'contacted' in status_lower:
        return 'Outreach'
    
    if 'conversation' in status_lower or 'meeting' in status_lower:
        return 'Engagement'
    if 'action pending' in status_lower:
        return 'Engagement'
    
    if 'strong connection' in status_lower or 'nurture' in status_lower:
        return 'Nurture'
    if 'referral' in status_lower or 'dormant' in status_lower:
        return 'Nurture'
    
    # If not a networking status, return original (for job application statuses)
    return status


def status_matches(current_status: str, *targets: str) -> bool:
    """Check whether a status matches any of the target labels (with normalization)."""
    normalized_status = normalize_status_label(current_status)
    normalized_targets = {normalize_status_label(target) for target in targets}
    return normalized_status in normalized_targets


@app.route('/')
def index():
    """Dashboard as landing page"""
    from app.utils.file_utils import get_data_path
    # Always regenerate dashboard to ensure navigation is up to date
    dashboard_generator.generate_index_page()
    dashboard_path = get_data_path('output') / 'index.html'
    
    if dashboard_path.exists():
        return send_from_directory(
            dashboard_path.parent,
            dashboard_path.name
        )
    return "Dashboard not generated yet.", 404

@app.route('/new-application')
def new_application():
    """New application form page"""
    return render_template('ui.html')


@app.route('/new-networking-contact')
def new_networking_contact():
    """New networking contact form page"""
    company = request.args.get('company', '')
    return render_template('networking_form.html', company=company)


@app.route('/networking')
def networking_dashboard():
    """Networking contacts dashboard"""
    return render_template('networking_dashboard.html')

@app.route('/search')
def search_page():
    """Search page for applications and contacts"""
    return render_template('search.html')


@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        applications = job_processor.list_all_applications()
        
        def count_status(*labels):
            return sum(1 for app in applications if status_matches(app.status, *labels))

        stats = {
            'total': len(applications),
            'pending': count_status('pending'),
            'applied': count_status('applied'),
            'contacted_someone': count_status('contacted someone'),
            'company_response': count_status('company response', 'contacted hiring manager'),
            'scheduled_interview': count_status('scheduled interview'),
            'interview_notes': count_status('interview notes', 'interviewed'),
            'interview_follow_up': count_status('interview - follow up'),
            'offered': count_status('offered'),
            'rejected': count_status('rejected'),
            'accepted': count_status('accepted')
        }
        stats['interviewed'] = stats['interview_notes']
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recent-applications', methods=['GET'])
def recent_applications():
    """Get recent applications for dashboard"""
    try:
        applications = job_processor.list_all_applications()
        # Sort by created_at descending and take first 5
        recent = sorted(applications, key=lambda x: x.created_at, reverse=True)[:5]
        
        return jsonify([{
            'id': app.id,
            'company': app.company,
            'job_title': app.job_title,
            'status': app.status,
            'created_at': app.created_at.isoformat(),
            'match_score': app.match_score,
            'flagged': app.flagged
        } for app in recent])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _is_rejected_status(status: str) -> bool:
    """Check if a status indicates the application was rejected"""
    if not status:
        return False
    normalized = normalize_status_label(status)
    return normalized == 'rejected'

@app.route('/api/applications', methods=['GET'])
def get_all_applications():
    """Get all applications for dashboard cards"""
    try:
        applications = job_processor.list_all_applications()
        
        # Filter out rejected applications (they should only appear in archived dashboard)
        applications = [app for app in applications if not _is_rejected_status(app.status)]
        
        # Filter by flagged status if requested
        flagged_filter = request.args.get('flagged', '').lower()
        if flagged_filter == 'true':
            applications = [app for app in applications if app.flagged]
        elif flagged_filter == 'false':
            applications = [app for app in applications if not app.flagged]
        
        return jsonify([{
            'id': app.id,
            'company': app.company,
            'job_title': app.job_title,
            'status': app.status,
            'created_at': app.created_at.isoformat(),
            'status_updated_at': app.status_updated_at.isoformat() if app.status_updated_at else None,
            'match_score': app.match_score,
            'posted_date': app.posted_date,
            'job_url': app.job_url,
            'salary_range': app.salary_range,
            'location': app.location,
            'hiring_manager': app.hiring_manager,
            'summary_path': str(app.summary_path) if app.summary_path else None,
            'flagged': app.flagged
        } for app in applications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications-and-contacts', methods=['GET'])
def get_applications_and_contacts():
    """Get combined list of applications and contacts for list view (includes rejected and archived applications)"""
    try:
        # Get all applications (including rejected ones for search)
        applications = job_processor.list_all_applications()
        
        # Get archived applications
        archived_applications = job_processor.list_archived_applications()
        
        # Combine applications, avoiding duplicates by ID
        application_ids = {app.id for app in applications}
        all_applications = applications + [app for app in archived_applications if app.id not in application_ids]
        
        # Get all contacts
        contacts = networking_processor.list_all_contacts()
        
        # Combine into unified list
        combined = []
        
        # Add applications (including archived and rejected)
        for app in all_applications:
            # Determine the URL to the details page
            if app.summary_path and app.folder_path:
                folder_name = app.folder_path.name
                summary_filename = app.summary_path.name
                detail_url = f"/applications/{folder_name}/{summary_filename}"
            elif app.folder_path:
                # Fallback: use folder name if no summary
                detail_url = f"/applications/{app.folder_path.name}/"
            else:
                detail_url = f"/applications/{app.id}"
            
            combined.append({
                'type': 'application',
                'id': app.id,
                'name': f"{app.company} - {app.job_title}",
                'company': app.company,
                'match_score': app.match_score,
                'status': app.status,
                'last_updated': app.status_updated_at if app.status_updated_at else app.created_at,
                'detail_url': detail_url
            })
        
        # Add contacts
        for contact in contacts:
            # Determine the URL to the details page
            if contact.summary_path and contact.folder_path:
                folder_name = contact.folder_path.name
                summary_filename = contact.summary_path.name
                detail_url = f"/networking/{folder_name}/{summary_filename}"
            elif contact.folder_path:
                # Fallback: use folder name if no summary
                detail_url = f"/networking/{contact.folder_path.name}/"
            else:
                detail_url = f"/networking/{contact.id}"
            
            combined.append({
                'type': 'contact',
                'id': contact.id,
                'name': f"{contact.person_name} - {contact.company_name}",
                'company': contact.company_name,
                'match_score': contact.match_score,
                'status': contact.status,
                'last_updated': contact.status_updated_at if contact.status_updated_at else contact.created_at,
                'detail_url': detail_url
            })
        
        # Helper function to get timestamp for sorting
        def get_timestamp(item):
            """Get timestamp from last_updated for sorting"""
            last_updated = item['last_updated']
            if isinstance(last_updated, datetime):
                # Handle timezone-aware and timezone-naive datetimes
                if last_updated.tzinfo is None:
                    # Naive datetime - assume UTC
                    from datetime import timezone
                    last_updated = last_updated.replace(tzinfo=timezone.utc)
                return last_updated.timestamp()
            elif isinstance(last_updated, str):
                try:
                    dt = datetime.fromisoformat(last_updated)
                    if dt.tzinfo is None:
                        from datetime import timezone
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt.timestamp()
                except (ValueError, AttributeError):
                    return 0
            else:
                return 0
        
        # Sort: Applications first (by company name, then last updated), then Contacts (by company name, then last updated)
        # Separate applications and contacts
        applications_list = [item for item in combined if item['type'] == 'application']
        contacts_list = [item for item in combined if item['type'] == 'contact']
        
        # Sort applications: by company name, then by last updated (newest to oldest)
        def sort_key_app(item):
            company = item['company'].lower()
            timestamp = get_timestamp(item)
            return (company, -timestamp)  # Negative timestamp for descending (newest first)
        
        applications_list.sort(key=sort_key_app)
        
        # Sort contacts: by company name, then by last updated (newest to oldest)
        def sort_key_contact(item):
            company = item['company'].lower()
            timestamp = get_timestamp(item)
            return (company, -timestamp)  # Negative timestamp for descending (newest first)
        
        contacts_list.sort(key=sort_key_contact)
        
        # Combine: applications first, then contacts
        combined = applications_list + contacts_list
        
        # Convert datetime objects to ISO format for JSON serialization
        for item in combined:
            if isinstance(item['last_updated'], datetime):
                item['last_updated'] = item['last_updated'].isoformat()
        
        return jsonify({
            'success': True,
            'items': combined,
            'count': len(combined)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-ollama', methods=['GET'])
def check_ollama():
    """Check Ollama connection and list models"""
    try:
        is_connected = ai_analyzer.check_connection()
        models = ai_analyzer.list_available_models() if is_connected else []
        
        return jsonify({
            'success': True,
            'connected': is_connected,
            'base_url': ai_analyzer.base_url,
            'current_model': ai_analyzer.model,
            'available_models': models
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume', methods=['GET'])
def get_resume():
    """Get base resume"""
    try:
        resume = resume_manager.load_base_resume()
        return jsonify({
            'success': True,
            'resume': resume.to_dict()
        })
    except FileNotFoundError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume', methods=['PUT'])
def update_resume():
    """Update base resume"""
    try:
        data = request.json
        print(f"Received resume update - content length: {len(data.get('content', ''))}")
        print(f"Content preview: {data.get('content', '')[:200]}...")
        
        # Load existing or create new
        try:
            resume = resume_manager.load_base_resume()
        except FileNotFoundError:
            from app.models.resume import Resume
            resume = Resume(
                full_name='',
                email='',
                phone='',
                content=''
            )
        
        # Update fields with sanitization (exclude linkedin and content)
        resume.full_name = sanitize_text(data.get('full_name', resume.full_name))
        resume.email = sanitize_email(data.get('email', resume.email))
        resume.phone = sanitize_phone(data.get('phone', resume.phone))
        resume.linkedin = data.get('linkedin', resume.linkedin)  # Exclude from sanitization (URL)
        resume.location = sanitize_text(data.get('location', resume.location))
        resume.content = data.get('content', resume.content)  # Exclude from sanitization (rich format)
        
        print(f"Saving resume with content length: {len(resume.content)}")
        
        # Save resume (this will trigger technology and skill extraction)
        resume_manager.save_base_resume(resume)
        
        # Check if skills were extracted
        from pathlib import Path
        import yaml
        skills_path = Path("data/resumes/skills.yaml")
        skills_extracted = False
        skills_count = 0
        if skills_path.exists():
            try:
                with open(skills_path, 'r') as f:
                    skills_data = yaml.safe_load(f)
                    skills_count = skills_data.get('total_skills', 0)
                    skills_extracted = True
            except:
                pass
        
        return jsonify({
            'success': True,
            'message': 'Resume updated successfully',
            'skills_extracted': skills_extracted,
            'skills_count': skills_count
        })
    except Exception as e:
        print(f"Error updating resume: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume/init', methods=['POST'])
def init_resume():
    """Initialize base resume template"""
    try:
        resume_manager.create_base_resume_template()
        return jsonify({
            'success': True,
            'message': 'Base resume template created successfully',
            'path': str(resume_manager.resumes_dir)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume/technologies', methods=['GET'])
def get_resume_technologies():
    """Get technologies extracted from resume"""
    try:
        tech_data = resume_manager.load_technologies()
        if not tech_data:
            return jsonify({
                'success': True,
                'technologies': None,
                'message': 'No technologies extracted yet. Save your resume to extract technologies.'
            })
        
        return jsonify({
            'success': True,
            'technologies': tech_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/resume/technologies/regenerate', methods=['POST'])
def regenerate_technologies():
    """Regenerate technologies from current resume"""
    try:
        # Load current resume
        resume = resume_manager.load_base_resume()
        
        # Extract and save technologies
        tech_data = resume_manager.extract_and_save_technologies(resume.content)
        
        return jsonify({
            'success': True,
            'message': f'Technologies regenerated successfully. Found {tech_data["total_technologies"]} technologies.',
            'technologies': tech_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications', methods=['POST'])
def create_application():
    """Create a new job application"""
    try:
        data = request.json
        # Sanitize text inputs (trim spaces, remove dangerous chars)
        company = sanitize_text(data.get('company')) if data.get('company') else None
        job_title = sanitize_text(data.get('job_title')) if data.get('job_title') else None
        job_description = data.get('job_description')  # Exclude from sanitization (long-form text)
        job_url = data.get('job_url')  # Exclude from sanitization (URL)
        
        if not all([company, job_title, job_description]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: company, job_title, job_description'
            }), 400
        
        # Check if resume exists
        try:
            resume_manager.load_base_resume()
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Base resume not found. Please create a resume first.'
            }), 400
        
        # Check Ollama connection
        if not ai_analyzer.check_connection():
            return jsonify({
                'success': False,
                'error': 'Cannot connect to Ollama. Please ensure Ollama is running.'
            }), 503
        
        # Create application
        application = job_processor.create_job_application(
            job_description=job_description,
            company=company,
            job_title=job_title,
            job_url=job_url
        )
        
        # Generate all documents synchronously
        doc_generator.generate_all_documents(application)
        
        # Save updated metadata with paths
        job_processor._save_application_metadata(application)
        
        # Generate relative URL for summary
        summary_url = None
        if application.summary_path:
            folder_name = application.folder_path.name
            summary_filename = application.summary_path.name
            summary_url = f"/applications/{folder_name}/{summary_filename}"
        
        # Load qualifications analysis for detailed response (best-effort)
        qualifications_data = None
        if application.qualifications_path and application.qualifications_path.exists():
            try:
                from app.utils.file_utils import read_text_file
                qual_content = read_text_file(application.qualifications_path)
                qualifications_data = {
                    'match_score': application.match_score or 0.0,
                    'features_compared': 0,
                    'strong_matches': [],
                    'missing_skills': [],
                    'partial_matches': [],
                    'soft_skills': [],
                    'recommendations': [],
                    'detailed_analysis': qual_content
                }
                import re
                features_match = re.search(r'Features Compared:?\s*(\d+)', qual_content, re.IGNORECASE)
                if features_match:
                    qualifications_data['features_compared'] = int(features_match.group(1))
                strong_section = re.search(r'Strong Matches:?\s*([^\n]+)', qual_content, re.IGNORECASE)
                if strong_section:
                    qualifications_data['strong_matches'] = [s.strip() for s in strong_section.group(1).split(',')]
                missing_section = re.search(r'Missing Skills:?\s*([^\n]+)', qual_content, re.IGNORECASE)
                if missing_section:
                    qualifications_data['missing_skills'] = [s.strip() for s in missing_section.group(1).split(',')]
            except Exception as e:
                print(f"Warning: Could not load qualifications data: {e}")
                qualifications_data = None

        return jsonify({
            'success': True,
            'message': 'Application created successfully',
            'application_id': application.id,
            'folder_path': str(application.folder_path),
            'summary_path': str(application.summary_path),
            'summary_url': summary_url,
            'match_score': application.match_score,
            'qualifications': qualifications_data,
            'location': application.location,
            'salary_range': application.salary_range,
            'posted_date': application.posted_date,
            'created_at': format_for_display(application.created_at) if application.created_at else None,
            'job_url': application.job_url
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/comparison', methods=['GET'])
def get_normalization_comparison(app_id):
    """Get side-by-side comparison of old vs new normalization"""
    try:
        from app.services.preliminary_matcher import PreliminaryMatcher
        from app.utils.skill_normalizer import SkillNormalizer
        from app.utils.file_utils import read_text_file
        
        application = job_processor.get_application_by_id(app_id)
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Load job description
        job_text = read_text_file(application.raw_job_description_path)
        
        # Initialize matchers
        matcher = PreliminaryMatcher()
        
        # Get old system results
        old_matches = matcher.find_skill_matches(job_text)
        old_extracted = matcher._extract_job_skills_from_description(job_text)
        
        # Get new system results (with normalization)
        new_extracted = []
        for skill in old_extracted:
            # Use SkillNormalizer directly for canonical names
            normalized_result = matcher.skill_normalizer.normalize(skill, fuzzy=True)
            if normalized_result:
                new_extracted.append(normalized_result)
        
        # Compare individual skills
        skill_comparisons = []
        test_skills = old_extracted[:20]  # First 20 for comparison
        for skill in test_skills:
            # Use SkillNormalizer for both old and new normalization
            old_norm = matcher.normalize_skill_name(skill)  # Returns lowercase string
            new_canonical = matcher.skill_normalizer.normalize(skill, fuzzy=True)  # Returns canonical name
            new_category = matcher.skill_normalizer.get_category(new_canonical) if new_canonical else None
            
            skill_comparisons.append({
                'original': skill,
                'old_normalized': old_norm,
                'new_canonical': new_canonical,
                'new_category': new_category,
                'different': (old_norm != new_canonical.lower() if new_canonical else False)
            })
        
        return jsonify({
            'success': True,
            'comparison': {
                'old_system': {
                    'match_score': old_matches['match_score'],
                    'extracted_count': len(old_extracted),
                    'extracted_skills': old_extracted[:10]
                },
                'new_system': {
                    'normalized_count': len(set(new_extracted)),
                    'normalized_skills': list(set(new_extracted))[:10]
                },
                'skill_comparisons': skill_comparisons,
                'improvements': len([s for s in skill_comparisons if s['different']])
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications', methods=['GET'])
def list_applications():
    """List all applications"""
    try:
        applications = job_processor.list_all_applications()
        
        # Filter out rejected applications (they should only appear in archived dashboard)
        applications = [app for app in applications if not _is_rejected_status(app.status)]
        
        app_list = []
        for app in applications:
            app_list.append({
                'id': app.id,
                'company': app.company,
                'job_title': app.job_title,
                'status': app.status,
                'created_at': format_for_display(app.created_at),
                'updated_at': format_for_display(app.status_updated_at),
                'folder_path': str(app.folder_path),
                'summary_path': str(app.summary_path) if app.summary_path else None,
                'match_score': app.match_score,
                'flagged': app.flagged
            })
        
        return jsonify({
            'success': True,
            'applications': app_list,
            'count': len(app_list)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>', methods=['GET'])
def get_application(app_id):
    """Get application details"""
    try:
        application = job_processor.get_application_by_id(app_id)
        
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Get updates
        updates = job_processor.get_application_updates(application)
        
        return jsonify({
            'success': True,
            'application': {
                'id': application.id,
                'company': application.company,
                'job_title': application.job_title,
                'status': application.status,
                'created_at': format_for_display(application.created_at),
                'updated_at': format_for_display(application.status_updated_at),
                'match_score': application.match_score,
                'job_url': application.job_url,
                'posted_date': application.posted_date,
                'salary_range': application.salary_range,
                'location': application.location,
                'hiring_manager': application.hiring_manager,
                'folder_path': str(application.folder_path),
                'summary_path': str(application.summary_path) if application.summary_path else None,
                'flagged': application.flagged,
                'checklist_items': application.checklist_items,
                'updates': updates
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/search', methods=['GET'])
def search_applications():
    """Search applications for dropdown selection"""
    try:
        query = request.args.get('q', '').lower()
        applications = job_processor.list_all_applications()
        
        # Filter applications based on query
        filtered_apps = []
        for app in applications:
            if (query in app.company.lower() or 
                query in app.job_title.lower() or 
                query in app.id.lower()):
                filtered_apps.append({
                    'id': app.id,
                    'company': app.company,
                    'job_title': app.job_title,
                    'status': app.status,
                    'flagged': app.flagged,
                    'display_text': f"{app.company} - {app.job_title} ({app.id})"
                })
        
        return jsonify({
            'success': True,
            'applications': filtered_apps,
            'count': len(filtered_apps)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/status', methods=['PUT'])
def update_status(app_id):
    """Update application status"""
    try:
        data = request.json
        status = data.get('status')
        notes = data.get('notes')
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Missing required field: status'
            }), 400
        
        # Load application
        application = job_processor.get_application_by_id(app_id)
        
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Update status with notes
        job_processor.update_application_status(application, status, notes)
        
        # Regenerate summary page to include new update in timeline
        try:
            # Load qualifications to regenerate summary (uses JSON if available)
            qualifications = doc_generator._load_qualifications(application)
            if qualifications.match_score > 0:
                # Update application metadata with qualifications info
                application.match_score = qualifications.match_score
                
                # Regenerate summary page
                doc_generator.generate_summary_page(application, qualifications)
                
                # Save updated metadata
                job_processor._save_application_metadata(application)
        except Exception as e:
            print(f"Warning: Could not regenerate summary page: {e}")
        
        # Generate response data
        response_data = {
            'success': True,
            'message': f'Status updated to {status}',
            'application_id': application.id,
            'status': status,
            'updated_at': format_for_display(application.status_updated_at)
        }
        
        # For rejected applications, include redirect information
        normalized_status = normalize_status_label(status)
        if normalized_status == 'rejected':
            response_data['redirect'] = 'dashboard'  # Navigate to dashboard page
            response_data['message'] = f'Status updated to {status}. Application cleaned up and redirected to dashboard.'
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/details', methods=['PUT'])
def update_job_details(app_id):
    """Update job details (salary_range, location, hiring_manager)"""
    try:
        data = request.json
        salary_range = data.get('salary_range')
        location = data.get('location')
        hiring_manager = data.get('hiring_manager')
        
        # Check if at least one field is provided
        if not any([salary_range, location, hiring_manager]):
            return jsonify({
                'success': False,
                'error': 'At least one field must be provided: salary_range, location, hiring_manager'
            }), 400
        
        # Load application
        application = job_processor.get_application_by_id(app_id)
        
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Update job details
        job_processor.update_job_details(
            application,
            salary_range=salary_range,
            location=location,
            hiring_manager=hiring_manager
        )
        
        return jsonify({
            'success': True,
            'message': 'Job details updated successfully',
            'application_id': application.id,
            'updated_fields': {
                'salary_range': application.salary_range,
                'location': application.location,
                'hiring_manager': application.hiring_manager
            },
            'updated_at': format_for_display(application.status_updated_at)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/flag', methods=['PUT'])
def toggle_flag(app_id):
    """Toggle flag status for an application"""
    try:
        data = request.json
        flagged = data.get('flagged')
        
        if flagged is None:
            return jsonify({
                'success': False,
                'error': 'Missing required field: flagged (boolean)'
            }), 400
        
        # Load application
        application = job_processor.get_application_by_id(app_id)
        
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Update flagged status
        application.flagged = bool(flagged)
        
        # Save updated metadata
        job_processor._save_application_metadata(application)
        
        # Update dashboard
        dashboard_generator.generate_index_page()
        
        return jsonify({
            'success': True,
            'message': f'Application {"flagged" if application.flagged else "unflagged"} successfully',
            'application_id': application.id,
            'flagged': application.flagged
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/checklist', methods=['PUT'])
def update_checklist(app_id):
    """Update application checklist items"""
    try:
        data = request.json
        checklist_updates = data.get('checklist', {})
        
        if not checklist_updates:
            return jsonify({
                'success': False,
                'error': 'Missing required field: checklist (dict)'
            }), 400
        
        # Load application
        application = job_processor.get_application_by_id(app_id)
        
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Update checklist
        job_processor.update_application_checklist(application, checklist_updates)
        
        # Regenerate summary page to reflect checklist changes
        try:
            # Load qualifications (uses JSON if available)
            qualifications = doc_generator._load_qualifications(application)
            if qualifications.match_score > 0 or qualifications.detailed_analysis:
                # Regenerate summary page with updated checklist
                doc_generator.generate_summary_page(application, qualifications)
        except Exception as e:
            print(f"Warning: Could not regenerate summary page: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Checklist updated successfully',
            'application_id': application.id,
            'checklist': application.checklist_items
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/regenerate', methods=['POST'])
def regenerate_documents(app_id):
    """Regenerate documents for an application"""
    try:
        application = job_processor.get_application_by_id(app_id)
        
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Regenerate all documents
        doc_generator.generate_all_documents(application)
        
        # Save updated metadata
        job_processor._save_application_metadata(application)
        
        return jsonify({
            'success': True,
            'message': 'Documents regenerated successfully',
            'application_id': application.id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/custom-resume', methods=['POST'])
def set_custom_resume(app_id):
    """Set a custom resume for a specific application and regenerate documents"""
    try:
        data = request.json
        resume_content = data.get('resume_content')
        
        if not resume_content:
            return jsonify({
                'success': False,
                'error': 'Missing required field: resume_content'
            }), 400
        
        # Load application
        application = job_processor.get_application_by_id(app_id)
        
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Save custom resume
        custom_resume_path = resume_manager.save_custom_resume(
            app_id,
            resume_content,
            application.folder_path
        )
        
        application.custom_resume_path = custom_resume_path
        application.resume_used = custom_resume_path.name
        
        # Regenerate all documents with new resume
        doc_generator.generate_all_documents(application)
        
        # Save updated metadata
        job_processor._save_application_metadata(application)
        
        return jsonify({
            'success': True,
            'message': 'Custom resume set and documents regenerated',
            'resume_path': str(custom_resume_path)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/generate-resume', methods=['POST'])
def generate_resume(app_id):
    """Generate a customized resume from base resume and existing qualifications"""
    try:
        # Load application
        application = job_processor.get_application_by_id(app_id)
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Ensure qualifications exist
        if not application.qualifications_path or not application.qualifications_path.exists():
            return jsonify({'success': False, 'error': 'Qualifications not found for this application'}), 400
        
        # Load base resume and qualifications content
        resume = resume_manager.load_base_resume()
        # Load qualifications (uses JSON if available, includes preliminary_analysis)
        qualifications = doc_generator._load_qualifications(application)
        
        # Generate resume
        doc_generator.generate_custom_resume(application, qualifications, resume.content)
        
        # Regenerate summary to include resume tab/content
        doc_generator.generate_summary_page(application, qualifications)
        
        # Save metadata and update dashboard
        job_processor._save_application_metadata(application)
        dashboard_generator.generate_index_page()
        
        return jsonify({'success': True, 'message': 'Customized resume generated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/generate-intros', methods=['POST'])
def generate_intros(app_id):
    """Generate intro messages (hiring manager and/or recruiter) on demand"""
    try:
        data = request.json
        message_type = data.get('message_type', 'both')  # 'hiring_manager', 'recruiter', or 'both'
        
        # Load application
        application = job_processor.get_application_by_id(app_id)
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Ensure qualifications exist
        if not application.qualifications_path or not application.qualifications_path.exists():
            return jsonify({'success': False, 'error': 'Qualifications not found for this application'}), 400
        
        # Load resume and qualifications
        resume = resume_manager.load_base_resume()
        # Load qualifications (uses JSON if available, includes preliminary_analysis)
        qualifications = doc_generator._load_qualifications(application)
        
        # Generate intro messages (both types always generated together for efficiency)
        doc_generator.generate_intro_messages(application, qualifications, resume.full_name)
        
        # Regenerate summary to include intro messages
        doc_generator.generate_summary_page(application, qualifications)
        
        # Save metadata and update dashboard
        job_processor._save_application_metadata(application)
        dashboard_generator.generate_index_page()
        
        return jsonify({'success': True, 'message': 'Intro messages generated successfully'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# NETWORKING ENDPOINTS
# ============================================================================

@app.route('/api/networking/contacts', methods=['POST'])
def create_networking_contact():
    """Create a new networking contact"""
    try:
        data = request.json
        # Sanitize text inputs (trim spaces, remove dangerous chars)
        person_name = sanitize_text(data.get('person_name')) if data.get('person_name') else None
        company_name = sanitize_text(data.get('company_name')) if data.get('company_name') else None
        profile_details = data.get('profile_details')  # Exclude from sanitization (long-form text)
        job_title = sanitize_text(data.get('job_title')) if data.get('job_title') else None
        linkedin_url = data.get('linkedin_url')  # Exclude from sanitization (URL)
        requires_ai_processing = data.get('requires_ai_processing', True)  # Default to True for backwards compatibility
        
        if not all([person_name, company_name, profile_details]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: person_name, company_name, profile_details'
            }), 400
        
        # Check if resume exists
        try:
            resume = resume_manager.load_base_resume()
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Base resume not found. Please create a resume first.'
            }), 400
        
        # Check Ollama connection - warn for simple contacts but allow fallback
        if requires_ai_processing and not ai_analyzer.check_connection():
            return jsonify({
                'success': False,
                'error': 'Cannot connect to Ollama. Please ensure Ollama is running for full AI processing.'
            }), 503
        # For simple contacts, we'll use a fallback template if Ollama isn't available
        
        # Create contact
        contact = networking_processor.create_networking_contact(
            person_name=person_name,
            company_name=company_name,
            profile_details=profile_details,
            job_title=job_title,
            linkedin_url=linkedin_url,
            requires_ai_processing=requires_ai_processing
        )
        
        # Generate documents based on processing type
        if requires_ai_processing:
            # Full AI processing (current behavior)
            networking_doc_generator.generate_all_documents(contact, resume.content)
        else:
            # Simple contact - generate lightweight summary page (no AI)
            networking_doc_generator.generate_simple_summary_page(contact)
        
        # Save updated metadata with paths and match score
        networking_processor._save_contact_metadata(contact)
        
        # Invalidate contact count cache (will regenerate on next dashboard load)
        try:
            contact_count_cache.invalidate_cache()
        except Exception as e:
            print(f"Warning: Could not invalidate contact count cache: {e}")
        
        # Update matching applications' status_updated_at
        try:
            from datetime import datetime
            from app.utils.datetime_utils import get_est_now
            applications = job_processor.list_all_applications()
            updated_apps = []
            for app in applications:
                if app.company.lower().strip() == contact.company_name.lower().strip():
                    app.status_updated_at = get_est_now()
                    job_processor._save_application_metadata(app)
                    updated_apps.append(app)
            
            # Regenerate dashboards in background if any applications were updated
            if updated_apps:
                import threading
                def regenerate_dashboards():
                    try:
                        dashboard_generator.generate_index_page()
                        dashboard_generator.generate_archived_dashboard()
                    except Exception as e:
                        print(f"Warning: Could not regenerate dashboards: {e}")
                threading.Thread(target=regenerate_dashboards, daemon=True).start()
        except Exception as e:
            # Don't fail the contact creation if application update fails
            print(f"Warning: Could not update applications for contact creation: {e}")
        
        # Generate summary URL
        summary_url = None
        if contact.summary_path:
            folder_name = contact.folder_path.name
            summary_filename = contact.summary_path.name
            summary_url = f"/networking/{folder_name}/{summary_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Networking contact created successfully',
            'contact_id': contact.id,
            'person_name': contact.person_name,
            'company_name': contact.company_name,
            'match_score': contact.match_score,
            'summary_url': summary_url,
            'folder_path': str(contact.folder_path),
            'requires_ai_processing': contact.requires_ai_processing
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/applications/<app_id>/networking-contacts', methods=['GET'])
def get_application_networking_contacts(app_id):
    """Get networking contacts matching the application's company"""
    try:
        # Get application
        application = job_processor.get_application_by_id(app_id)
        if not application:
            return jsonify({'success': False, 'error': 'Application not found'}), 404
        
        # Get all contacts
        all_contacts = networking_processor.list_all_contacts()
        
        # Filter contacts matching the company (case-insensitive)
        matched_contacts = [
            c for c in all_contacts
            if c.company_name.lower().strip() == application.company.lower().strip()
        ]
        
        return jsonify({
            'success': True,
            'contacts': [{
                'id': c.id,
                'person_name': c.person_name,
                'company_name': c.company_name,
                'job_title': c.job_title,
                'status': c.status,
                'created_at': c.created_at.isoformat(),
                'status_updated_at': c.status_updated_at.isoformat() if c.status_updated_at else None,
                'match_score': c.match_score,
                'linkedin_url': c.linkedin_url,
                'email': c.email,
                'location': c.location,
                'flagged': c.flagged,
                'days_since_update': c.get_days_since_update(),
                'timing_color': c.get_timing_color_class(),
                'next_step': c.get_next_step()
            } for c in matched_contacts],
            'count': len(matched_contacts)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/networking/contacts', methods=['GET'])
def list_networking_contacts():
    """List all networking contacts"""
    try:
        from app.services.badge_calculation_service import BadgeCalculationService
        badge_service = BadgeCalculationService()
        
        contacts = networking_processor.list_all_contacts()
        
        contact_list = []
        for c in contacts:
            # Get badge for this contact based on status
            badge_id = badge_service.status_to_badge.get(c.status)
            badge_data = None
            if badge_id:
                badge_def = badge_service.badge_definitions.get(badge_id)
                if badge_def:
                    badge_data = {
                        'badge_id': badge_id,
                        'badge_name': badge_def['name'],
                        'badge_points': badge_def['points']
                    }
            
            contact_list.append({
                'id': c.id,
                'person_name': c.person_name,
                'company_name': c.company_name,
                'job_title': c.job_title,
                'status': c.status,
                'created_at': c.created_at.isoformat(),
                'status_updated_at': c.status_updated_at.isoformat() if c.status_updated_at else None,
                'match_score': c.match_score,
                'linkedin_url': c.linkedin_url,
                'email': c.email,
                'location': c.location,
                'flagged': c.flagged,
                'days_since_update': c.get_days_since_update(),
                'timing_color': c.get_timing_color_class(),
                'next_step': c.get_next_step(),
                'summary_path': str(c.summary_path) if c.summary_path else None,
                'messages_path': str(c.messages_path) if c.messages_path else None,
                'latest_badge': badge_data
            })
        
        return jsonify({
            'success': True,
            'contacts': contact_list,
            'count': len(contacts)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/networking/contacts/<contact_id>', methods=['GET'])
def get_networking_contact(contact_id):
    """Get networking contact details"""
    try:
        contact = networking_processor.get_contact_by_id(contact_id)
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        # Get updates
        updates = networking_processor.get_contact_updates(contact)
        
        return jsonify({
            'success': True,
            'contact': {
                'id': contact.id,
                'person_name': contact.person_name,
                'company_name': contact.company_name,
                'job_title': contact.job_title,
                'status': contact.status,
                'created_at': format_for_display(contact.created_at),
                'updated_at': format_for_display(contact.status_updated_at),
                'match_score': contact.match_score,
                'linkedin_url': contact.linkedin_url,
                'email': contact.email,
                'location': contact.location,
                'flagged': contact.flagged,
                'next_step': contact.get_next_step(),
                'summary_path': str(contact.summary_path) if contact.summary_path else None,
                'messages_path': str(contact.messages_path) if contact.messages_path else None,
                'updates': updates
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/networking/contacts/<contact_id>/status', methods=['PUT'])
def update_networking_status(contact_id):
    """Update networking contact status"""
    try:
        data = request.json
        status = data.get('status')
        notes = data.get('notes')
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Missing required field: status'
            }), 400
        
        # Load contact
        contact = networking_processor.get_contact_by_id(contact_id)
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        # Update status with notes
        networking_processor.update_contact_status(contact, status, notes)
        
        # Invalidate contact count cache (will regenerate on next dashboard load)
        try:
            contact_count_cache.invalidate_cache()
        except Exception as e:
            print(f"Warning: Could not invalidate contact count cache: {e}")
        
        # Check if contact's company matches any application and create timeline entry
        try:
            from app.utils.datetime_utils import get_est_now
            applications = job_processor.list_all_applications()
            updated_apps = []
            for app in applications:
                if app.company.lower().strip() == contact.company_name.lower().strip():
                    # Update application's status_updated_at
                    app.status_updated_at = get_est_now()
                    job_processor._save_application_metadata(app)
                    updated_apps.append(app)
                    
                    # Create networking timeline entry in matching application
                    job_processor.create_networking_timeline_entry(
                        app,
                        contact.person_name,
                        status,
                        notes
                    )
                    # Regenerate summary to include the new timeline entry
                    job_processor._regenerate_summary(app)
            
            # Regenerate dashboards in background if any applications were updated
            if updated_apps:
                import threading
                def regenerate_dashboards():
                    try:
                        dashboard_generator.generate_index_page()
                        dashboard_generator.generate_archived_dashboard()
                    except Exception as e:
                        print(f"Warning: Could not regenerate dashboards: {e}")
                threading.Thread(target=regenerate_dashboards, daemon=True).start()
        except Exception as e:
            # Don't fail the status update if timeline entry creation fails
            print(f"Warning: Could not create timeline entry for contact update: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Status updated to {status}',
            'contact_id': contact.id,
            'status': status,
            'updated_at': format_for_display(contact.status_updated_at)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/networking/contacts/<contact_id>/details', methods=['PUT'])
def update_networking_details(contact_id):
    """Update networking contact details"""
    try:
        data = request.json
        # Sanitize inputs (trim spaces, remove dangerous chars)
        email = sanitize_email(data.get('email')) if 'email' in data and data.get('email') else None
        location = sanitize_text(data.get('location')) if 'location' in data and data.get('location') else None
        job_title = sanitize_text(data.get('job_title')) if 'job_title' in data and data.get('job_title') else None
        
        # Check which fields were explicitly provided in the request
        email_provided = 'email' in data
        location_provided = 'location' in data
        job_title_provided = 'job_title' in data
        
        # Load contact
        contact = networking_processor.get_contact_by_id(contact_id)
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        # Update details (only update fields that were explicitly provided)
        networking_processor.update_contact_details(
            contact,
            email=email,
            location=location,
            job_title=job_title,
            _email_provided=email_provided,
            _location_provided=location_provided,
            _job_title_provided=job_title_provided
        )
        
        # Invalidate contact count cache if company name changed (will regenerate on next dashboard load)
        # Note: We invalidate even if company didn't change, to be safe
        try:
            contact_count_cache.invalidate_cache()
        except Exception as e:
            print(f"Warning: Could not invalidate contact count cache: {e}")
        
        # Regenerate summary page to reflect updated contact details
        try:
            # Reload contact to get fresh data from YAML
            contact = networking_processor.get_contact_by_id(contact_id)
            
            # If we don't have a summary yet, nothing to regenerate
            if not contact or not contact.summary_path:
                pass
            # For full AI contacts, regenerate the rich summary page
            elif contact.requires_ai_processing:
                from app.utils.file_utils import read_text_file
                
                # Read existing match analysis and messages if available
                match_analysis = ""
                messages = {}
                research_content = ""
                
                if contact.match_analysis_path and contact.match_analysis_path.exists():
                    match_analysis = read_text_file(contact.match_analysis_path)
                
                if contact.messages_path and contact.messages_path.exists():
                    messages_content = read_text_file(contact.messages_path)
                    # Parse messages from the formatted file
                    lines = messages_content.split('\n')
                    current_section = None
                    current_message = []
                    
                    for line in lines:
                        if '1. INITIAL CONNECTION REQUEST' in line:
                            current_section = 'connection_request'
                            current_message = []
                        elif '2. MEETING INVITATION' in line:
                            if current_section:
                                messages[current_section] = '\n'.join(current_message).strip()
                            current_section = 'meeting_invitation'
                            current_message = []
                        elif '3. THANK YOU MESSAGE' in line:
                            if current_section:
                                messages[current_section] = '\n'.join(current_message).strip()
                            current_section = 'thank_you'
                            current_message = []
                        elif '4. CONSULTING SERVICES OFFER' in line:
                            if current_section:
                                messages[current_section] = '\n'.join(current_message).strip()
                            current_section = 'consulting_offer'
                            current_message = []
                        elif current_section and line.strip() and not line.startswith('-') and not line.startswith('='):
                            current_message.append(line)
                    
                    # Save last section
                    if current_section:
                        messages[current_section] = '\n'.join(current_message).strip()
                
                if contact.research_path and contact.research_path.exists():
                    research_content = read_text_file(contact.research_path)
                
                # Regenerate summary page with updated contact data (full AI layout)
                networking_doc_generator.generate_summary_page(
                    contact,
                    match_analysis,
                    messages,
                    research_content
                )
            else:
                # Simple contacts: keep the lightweight layout and just regenerate that page
                networking_doc_generator.generate_simple_summary_page(contact)
        except Exception as e:
            print(f"Warning: Could not regenerate summary page after update: {e}")
            import traceback
            traceback.print_exc()
        
        # Update matching applications' status_updated_at
        try:
            from app.utils.datetime_utils import get_est_now
            applications = job_processor.list_all_applications()
            updated_apps = []
            for app in applications:
                if app.company.lower().strip() == contact.company_name.lower().strip():
                    app.status_updated_at = get_est_now()
                    job_processor._save_application_metadata(app)
                    updated_apps.append(app)
            
            # Regenerate dashboards in background if any applications were updated
            if updated_apps:
                import threading
                def regenerate_dashboards():
                    try:
                        dashboard_generator.generate_index_page()
                        dashboard_generator.generate_archived_dashboard()
                    except Exception as e:
                        print(f"Warning: Could not regenerate dashboards: {e}")
                threading.Thread(target=regenerate_dashboards, daemon=True).start()
        except Exception as e:
            # Don't fail the details update if application update fails
            print(f"Warning: Could not update applications for contact details update: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Contact details updated successfully',
            'contact_id': contact.id,
            'updated_fields': {
                'email': contact.email,
                'location': contact.location,
                'job_title': contact.job_title
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/networking/contacts/<contact_id>/flag', methods=['PUT'])
def toggle_networking_flag(contact_id):
    """Toggle flag status for a networking contact"""
    try:
        data = request.json
        flagged = data.get('flagged')
        
        if flagged is None:
            return jsonify({
                'success': False,
                'error': 'Missing required field: flagged (boolean)'
            }), 400
        
        # Load contact
        contact = networking_processor.get_contact_by_id(contact_id)
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        # Update flagged status
        contact.flagged = bool(flagged)
        
        # Save updated metadata
        networking_processor._save_contact_metadata(contact)
        
        return jsonify({
            'success': True,
            'message': f'Contact {"flagged" if contact.flagged else "unflagged"} successfully',
            'contact_id': contact.id,
            'flagged': contact.flagged
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/networking/rewards/category', methods=['GET'])
def get_networking_rewards_by_category():
    """Get networking rewards broken down by category"""
    try:
        from app.services.badge_calculation_service import BadgeCalculationService
        badge_service = BadgeCalculationService()
        
        # Get badges by category
        badges_by_category = badge_service.get_badges_by_category()
        
        # Calculate total points
        total_points = sum(
            category_data['points'] 
            for category_data in badges_by_category.values()
        )
        
        # Format points by category
        points_by_category = {
            category: data['points']
            for category, data in badges_by_category.items()
        }
        
        return jsonify({
            'success': True,
            'points_by_category': points_by_category,
            'total_points': total_points,
            'badges_by_category': badges_by_category
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/networking/contacts/<contact_id>/regenerate', methods=['POST'])
def regenerate_networking_documents(contact_id):
    """Regenerate AI analysis and messages for a networking contact"""
    try:
        # Reimport to get latest code changes (fixes Flask reload issue)
        import importlib
        from app.services import networking_document_generator as ndg_module
        importlib.reload(ndg_module)
        doc_gen_fresh = ndg_module.NetworkingDocumentGenerator()
        
        # Load contact
        contact = networking_processor.get_contact_by_id(contact_id)
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        # Load resume
        try:
            resume = resume_manager.load_base_resume()
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Base resume not found. Please create a resume first.'
            }), 400
        
        # Check Ollama connection
        if not ai_analyzer.check_connection():
            return jsonify({
                'success': False,
                'error': 'Cannot connect to Ollama. Please ensure Ollama is running.'
            }), 503
        
        # Upgrade simple contacts to full AI processing when regenerating
        was_simple_contact = not contact.requires_ai_processing
        if was_simple_contact:
            contact.requires_ai_processing = True
        
        # Regenerate all documents with fresh instance (this will create full summary page)
        doc_gen_fresh.generate_all_documents(contact, resume.content)
        
        # Save updated metadata (including the upgraded requires_ai_processing flag)
        networking_processor._save_contact_metadata(contact)
        
        # Generate summary URL for redirect
        summary_url = None
        if contact.summary_path:
            folder_name = contact.folder_path.name
            summary_filename = contact.summary_path.name
            summary_url = f"/networking/{folder_name}/{summary_filename}"
        
        return jsonify({
            'success': True,
            'message': 'Documents regenerated successfully' + (' (upgraded to full AI processing)' if was_simple_contact else ''),
            'contact_id': contact.id,
            'match_score': contact.match_score,
            'summary_url': summary_url
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/networking/<path:filepath>')
def serve_networking_file(filepath):
    """Serve networking files (summaries, documents, etc.)"""
    from app.utils.file_utils import get_data_path
    # Get data directory and add networking subfolder
    data_dir = get_data_path('.')
    networking_dir = data_dir / 'networking'
    file_path = networking_dir / filepath
    
    if file_path.exists() and file_path.is_file():
        return send_from_directory(
            file_path.parent,
            file_path.name
        )
    return "File not found", 404


@app.route('/api/dashboard/update', methods=['POST'])
def update_dashboard():
    """Update the dashboard"""
    try:
        return jsonify({
            'success': True,
            'message': 'Dashboards updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Upload image for status updates"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image file selected'}), 400
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400
        
        # Create images directory
        images_dir = Path('data/images')
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = images_dir / unique_filename
        
        # Save file
        file.save(file_path)
        
        # Return the URL for the image
        image_url = f"/images/{unique_filename}"
        
        return jsonify({
            'success': True,
            'url': image_url,
            'filename': unique_filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/images/<filename>')
def serve_image(filename):
    """Serve uploaded images"""
    try:
        images_dir = Path('data/images')
        return send_from_directory(images_dir, filename)
    except Exception as e:
        return jsonify({'error': 'Image not found'}), 404


@app.route('/reports')
def view_reports():
    """View the reports page"""
    return render_template('reports.html')

@app.route('/analytics')
def view_analytics():
    """View the analytics page"""
    return render_template('analytics.html')

@app.route('/daily-activities')
def view_daily_activities():
    """View the daily activities page"""
    return render_template('daily_activities.html')

@app.route('/templates')
def view_templates():
    """View the templates page"""
    return render_template('templates.html')

@app.route('/rewards')
def view_rewards():
    """View the rewards system page"""
    return render_template('rewards.html')

@app.route('/how-to-hunter')
def view_how_to_hunter():
    """View the How to Hunter guide page"""
    return render_template('how_to_hunter.html')

@app.route('/tracking-guide')
def view_tracking_guide():
    """View the Tracking guide page"""
    return render_template('tracking_guide.html')

@app.route('/dashes-guide')
def view_dashes_guide():
    """View the Dashes guide page"""
    return render_template('dashes_guide.html')

@app.route('/templating-guide')
def view_templating_guide():
    """View the Templating guide page"""
    return render_template('templating_guide.html')

@app.route('/api/reports', methods=['GET'])
def get_reports_data():
    """Get reports data for specified period"""
    try:
        from datetime import datetime, timedelta, timezone
        from pathlib import Path
        
        period = request.args.get('period', '30days')
        report_type = request.args.get('type', 'jobs')  # 'jobs', 'networking', or 'both'
        gap_period = request.args.get('gap_period', 'all')  # For skill gaps: 'daily', 'weekly', 'monthly', 'all'

        # ------------------------------------------------------------------
        # Simple file-based caching, similar to dashboard caching.
        # Cache key includes period, report_type, and gap_period.
        # ------------------------------------------------------------------
        cache_filename = f"reports_cache_{period}_{report_type}_{gap_period}.json"
        cache_path = get_data_path('output') / Path(cache_filename)

        if not is_cache_stale(cache_path, ttl_seconds=300):
            cached = get_cached_json(cache_path)
            if cached is not None:
                return jsonify(cached)
        
        # Calculate date ranges based on period
        now = datetime.now(timezone(timedelta(hours=-4)))
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == '7days':
            start_date = now - timedelta(days=7)
            end_date = now
        elif period == '30days':
            start_date = now - timedelta(days=30)
            end_date = now
        elif period == 'all':
            start_date = datetime(2020, 1, 1, tzinfo=timezone(timedelta(hours=-4)))
            end_date = now
        else:
            # Default to today
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        
        # ===== USE ACTIVITY LOG FOR FAST DATA RETRIEVAL =====
        # Get activities from activity log (much faster than scanning files)
        activities = activity_log_service.get_activities(start_date=start_date, end_date=end_date)
        
        # Filter by type
        if report_type == 'jobs':
            activities = [a for a in activities if 'application' in a.get('type', '')]
        elif report_type == 'networking':
            activities = [a for a in activities if 'networking' in a.get('type', '')]
        # 'both' includes all activities
        
        # Sort activities by timestamp to ensure chronological processing
        # This ensures creations are processed before status changes for the same application
        activities.sort(key=lambda a: a.get('timestamp', ''))
        
        # Process activities for reports
        from collections import defaultdict
        applications_by_status = {}
        status_changes_by_status = {}  # Now tracks transitions: "from_status → to_status"
        daily_counts = defaultdict(lambda: defaultdict(int))
        status_changes_count = 0
        
        # Track final status per application/contact for the period (to avoid double-counting)
        app_final_status = {}  # app_id -> final status in period
        
        # Track whether we're showing networking data (for grouping)
        is_networking_view = report_type in ['networking', 'both']
        
        for activity in activities:
            activity_type = activity.get('type', '')
            activity_date = activity['date']
            is_networking_activity = 'networking' in activity_type
            
            if activity_type in ['job_application_created', 'networking_contact_created']:
                status = activity.get('status', '')
                is_networking_activity = activity_type == 'networking_contact_created'
                
                if status:
                    # Extract status from name-status format using helper function
                    status_extracted = _extract_status_from_name_status(status)
                    normalized_status = normalize_status_label(status_extracted)
                    
                    # Group networking statuses for charts if in networking view
                    # Check both activity type AND if status looks like networking
                    if is_networking_view and (is_networking_activity or is_networking_status(normalized_status)):
                        category = categorize_networking_status(normalized_status)
                        display_status = category if category != normalized_status else normalized_status
                    else:
                        display_status = normalized_status
                    
                    # Track initial status for this application (will be overridden by status changes if any)
                    app_id = activity.get('application_id') or activity.get('contact_id', '')
                    if app_id:
                        if app_id not in app_final_status:
                            app_final_status[app_id] = display_status
                    else:
                        # No app_id, track it with a temporary ID based on company/position (fallback)
                        # Use company and position as a fallback identifier
                        company = activity.get('company') or activity.get('company_name', '')
                        position = activity.get('job_title', '')
                        if company and position:
                            temp_id = f"{company}-{position}-{activity_date}"
                            if temp_id not in app_final_status:
                                app_final_status[temp_id] = display_status
                    
                    # Count daily (apply same normalization and grouping)
                    date_obj = datetime.strptime(activity_date, '%Y-%m-%d').date()
                    daily_counts[date_obj][display_status] += 1
            
            elif activity_type in ['job_application_status_changed', 'networking_status_changed']:
                old_status_raw = activity.get('old_status', '')
                new_status_raw = activity.get('new_status', '')
                is_networking_activity = activity_type == 'networking_status_changed'
                
                if new_status_raw:
                    # Extract status from name-status format for both old and new statuses
                    old_status_extracted = _extract_status_from_name_status(old_status_raw) if old_status_raw else ''
                    new_status_extracted = _extract_status_from_name_status(new_status_raw)
                    
                    # Normalize both statuses
                    old_status_normalized = normalize_status_label(old_status_extracted) if old_status_extracted else 'unknown'
                    new_status_normalized = normalize_status_label(new_status_extracted)
                    
                    # Group networking statuses for charts if in networking view
                    # Check both activity type AND if status looks like networking
                    if is_networking_view and (is_networking_activity or is_networking_status(new_status_normalized)):
                        old_category = categorize_networking_status(old_status_normalized) if old_status_normalized != 'unknown' else 'unknown'
                        new_category = categorize_networking_status(new_status_normalized)
                        old_display_status = old_category if old_category != old_status_normalized else old_status_normalized
                        new_display_status = new_category if new_category != new_status_normalized else new_status_normalized
                    else:
                        old_display_status = old_status_normalized
                        new_display_status = new_status_normalized
                    
                    # Create transition key: "from_status → to_status"
                    transition_key = f"{old_display_status} → {new_display_status}"
                    
                    # Track final status (status changes override initial status for the period)
                    app_id = activity.get('application_id') or activity.get('contact_id', '')
                    if app_id:
                        app_final_status[app_id] = new_display_status
                    else:
                        # No app_id, track it with a temporary ID based on company/position (fallback)
                        company = activity.get('company') or activity.get('company_name', '')
                        position = activity.get('job_title', '')
                        if company and position:
                            temp_id = f"{company}-{position}-{activity_date}"
                            app_final_status[temp_id] = new_display_status
                    
                    # Track transitions instead of just destination status
                    status_changes_by_status[transition_key] = status_changes_by_status.get(transition_key, 0) + 1
                    status_changes_count += 1
                
                # Count daily (apply same normalization and grouping)
                # For daily counts, we track the new status (destination) to show daily activity
                date_obj = datetime.strptime(activity_date, '%Y-%m-%d').date()
                new_status_raw = activity.get('new_status', '')
                if new_status_raw:
                    new_status_extracted = _extract_status_from_name_status(new_status_raw)
                    normalized_status = normalize_status_label(new_status_extracted)
                    
                    # Group networking statuses for charts if in networking view
                    # Check both activity type AND if status looks like networking
                    if is_networking_view and (is_networking_activity or is_networking_status(normalized_status)):
                        category = categorize_networking_status(normalized_status)
                        display_status = category if category != normalized_status else normalized_status
                    else:
                        display_status = normalized_status
                    
                    daily_counts[date_obj][display_status] += 1
        
        # Rebuild applications_by_status from final statuses (more accurate than incremental counting)
        applications_by_status = {}
        for app_id, final_status in app_final_status.items():
            applications_by_status[final_status] = applications_by_status.get(final_status, 0) + 1
        
        # Calculate total count from activities
        total_count = len([a for a in activities if a.get('type') in ['job_application_created', 'networking_contact_created']])
        
        # Get all dates in the period range (only where there's actual data)
        all_dates = []
        if daily_counts:
            # Find the earliest date with actual data
            actual_start_date = min(daily_counts.keys())
            # Use the later of actual_start_date or period start_date
            effective_start_date = max(actual_start_date, start_date.date())
            
            current_date = effective_start_date
            end_date_only = end_date.date()
            while current_date <= end_date_only:
                all_dates.append(current_date)
                current_date += timedelta(days=1)
        else:
            # If no data, just use an empty list
            all_dates = []
        
        # Get all statuses that appear in the data
        all_statuses = set()
        for date in daily_counts:
            all_statuses.update(daily_counts[date].keys())
        
        # Sort statuses: networking categories first (in order), then others alphabetically
        def sort_status_key(status):
            """Sort statuses with networking categories first"""
            category_order = ['Research & Contact', 'Engagement', 'Relationship']
            if status in category_order:
                return (category_order.index(status), status)
            else:
                return (len(category_order), status)
        
        sorted_statuses = sorted(all_statuses, key=sort_status_key)
        
        # Format daily activities for frontend: {status: [{date: "YYYY-MM-DD", count: N}, ...]}
        daily_activities_by_status = {}
        for status in sorted_statuses:
            daily_activities_by_status[status] = []
            for date in all_dates:
                count = daily_counts[date].get(status, 0)
                daily_activities_by_status[status].append({
                    'date': str(date),
                    'count': count
                })
        
        # Calculate cumulative activities
        cumulative_activities_by_status = {}
        for status in sorted_statuses:
            cumulative_activities_by_status[status] = []
            cumulative_count = 0
            for date in all_dates:
                cumulative_count += daily_counts[date].get(status, 0)
                cumulative_activities_by_status[status].append({
                    'date': str(date),
                    'count': cumulative_count
                })
        
        # ===== LOAD APPLICATIONS/CONTACTS ONLY FOR FOLLOW-UP AND FLAGGED =====
        # These need current state, so we still need to load them (but only when needed)
        one_week_ago = now - timedelta(days=7)
        followup_applications = []
        flagged_applications = []
        networking_followup_list = []
        networking_flagged_list = []
        
        # Only load applications/contacts if we need follow-up or flagged data
        if report_type in ['jobs', 'both']:
            applications = job_processor.list_all_applications()
            for app in applications:
                # Follow-up applications
                app_created_at = app.created_at.replace(tzinfo=timezone(timedelta(hours=-4)))
                app_status_updated_at = app.status_updated_at.replace(tzinfo=timezone(timedelta(hours=-4))) if app.status_updated_at else None
                last_update = app_status_updated_at or app_created_at
                
                if (last_update < one_week_ago and 
                    normalize_status_label(app.status) not in ['rejected', 'accepted']):
                    summary_url = None
                    if app.summary_path and app.summary_path.exists():
                        folder_name = app.folder_path.name
                        summary_filename = app.summary_path.name
                        summary_url = f"/applications/{folder_name}/{summary_filename}"
                    
                    followup_applications.append({
                        'company': app.company,
                        'job_title': app.job_title,
                        'match_score': round(app.match_score or 0),
                        'last_updated': format_for_display(last_update),
                        'summary_url': summary_url,
                        'contact_count': app.calculate_contact_count()
                    })
                
                # Flagged applications
                if app.flagged:
                    summary_url = None
                    if app.summary_path and app.summary_path.exists():
                        folder_name = app.folder_path.name
                        summary_filename = app.summary_path.name
                        summary_url = f"/applications/{folder_name}/{summary_filename}"
                    
                    last_update = app.status_updated_at or app.created_at
                    flagged_applications.append({
                        'company': app.company,
                        'job_title': app.job_title,
                        'match_score': round(app.match_score or 0),
                        'last_updated': format_for_display(last_update),
                        'summary_url': summary_url,
                        'contact_count': app.calculate_contact_count(),
                        'status': app.status
                    })
        
        if report_type in ['networking', 'both']:
            networking_contacts = networking_processor.list_all_contacts()
            for contact in networking_contacts:
                contact_created_at = contact.created_at.replace(tzinfo=timezone(timedelta(hours=-4)))
                contact_status_updated_at = contact.status_updated_at.replace(tzinfo=timezone(timedelta(hours=-4))) if contact.status_updated_at else None
                last_update = contact_status_updated_at or contact_created_at
                
                # Follow-up contacts
                if (last_update < one_week_ago and 
                    contact.status not in ['Cold/Archive']):
                    summary_url = None
                    if contact.summary_path and contact.summary_path.exists():
                        folder_name = contact.folder_path.name
                        summary_filename = contact.summary_path.name
                        summary_url = f"/networking/{folder_name}/{summary_filename}"
                    
                    networking_followup_list.append({
                        'company': contact.company_name,
                        'job_title': contact.job_title or 'N/A',
                        'match_score': round(contact.match_score or 0),
                        'last_updated': format_for_display(last_update),
                        'summary_url': summary_url,
                        'contact_count': contact.contact_count or 0,
                        'type': 'networking'
                    })
                
                # Flagged contacts
                if contact.flagged:
                    summary_url = None
                    if contact.summary_path and contact.summary_path.exists():
                        folder_name = contact.folder_path.name
                        summary_filename = contact.summary_path.name
                        summary_url = f"/networking/{folder_name}/{summary_filename}"
                    
                    last_update = contact_status_updated_at or contact_created_at
                    networking_flagged_list.append({
                        'company': contact.company_name,
                        'job_title': contact.job_title or 'N/A',
                        'match_score': round(contact.match_score or 0),
                        'last_updated': format_for_display(last_update),
                        'summary_url': summary_url,
                        'contact_count': contact.contact_count or 0,
                        'status': contact.status,
                        'type': 'networking'
                    })
        
        # Sort lists
        followup_applications.sort(key=lambda x: x['last_updated'], reverse=True)
        flagged_applications.sort(key=lambda x: x['last_updated'], reverse=True)
        
        # ===== COMBINE DATA BASED ON TYPE =====
        if report_type == 'networking':
            # Use only networking data from activity log
            # (networking_by_status already processed from activities above)
            followup_applications = networking_followup_list
            flagged_applications = networking_flagged_list
        elif report_type == 'both':
            # Combine follow-up and flagged lists
            followup_applications.extend(networking_followup_list)
            flagged_applications.extend(networking_flagged_list)
        
        # Sort combined lists
        followup_applications.sort(key=lambda x: x['last_updated'], reverse=True)
        flagged_applications.sort(key=lambda x: x['last_updated'], reverse=True)
        
        # Calculate rejected applications from status changes (applications rejected in period)
        rejected_count = status_changes_by_status.get('rejected', 0)
        if report_type in ['networking', 'both']:
            # Check for networking archived status
            for status_key in status_changes_by_status.keys():
                if 'cold' in status_key.lower() or 'archive' in status_key.lower():
                    rejected_count += status_changes_by_status.get(status_key, 0)
        
        # Calculate active applications (total - rejected)
        active_applications = total_count - rejected_count
        
        # Calculate total contact count from status_changes_by_status (matches the chart)
        # Note: status_changes_by_status now contains transitions like "old → new"
        total_contact_count = 0
        for transition_key, count in status_changes_by_status.items():
            transition_lower = transition_key.lower()
            # Check if transition involves contacted or company response statuses
            if '→ contacted' in transition_lower or 'contacted →' in transition_lower or 'company response' in transition_lower:
                total_contact_count += count
        
        # Calculate total actions (applications/contacts created + status changes) for the period
        total_actions = total_count + status_changes_count
        
        # Summary statistics
        summary = {
            'total_applications': total_count,
            'new_applications': total_count,
            'active_applications': active_applications,
            'status_changes': status_changes_count,
            'rejected': rejected_count,
            'followup_needed': len(followup_applications),
            'total_contact_count': total_contact_count,
            'total_actions': total_actions
        }

        # Sort status dictionaries by category order
        def sort_dict_by_status_order(d):
            """Sort dictionary keys with networking categories first"""
            category_order = ['Research & Contact', 'Engagement', 'Relationship']
            sorted_items = []
            # Add categories in order
            for category in category_order:
                if category in d:
                    sorted_items.append((category, d[category]))
            # Add remaining statuses alphabetically
            remaining = [(k, v) for k, v in d.items() if k not in category_order]
            remaining.sort(key=lambda x: x[0])
            sorted_items.extend(remaining)
            return dict(sorted_items)
        
        response_payload = {
            'success': True,
            'period': period,
            'summary': summary,
            'applications_by_status': sort_dict_by_status_order(applications_by_status),
            'status_changes': sort_dict_by_status_order(status_changes_by_status),
            'daily_activities_by_status': daily_activities_by_status,
            'cumulative_activities_by_status': cumulative_activities_by_status,
            'followup_applications': followup_applications,
            'flagged_applications': flagged_applications
        }

        # Save to cache for subsequent fast loads.
        save_cached_json(cache_path, response_payload)

        return jsonify(response_payload)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/export-csv', methods=['GET'])
def export_reports_csv():
    """Export daily and cumulative activities to CSV"""
    try:
        from datetime import datetime, timedelta, timezone
        from flask import Response
        import io
        import csv
        
        period = request.args.get('period', 'all')
        applications = job_processor.list_all_applications()
        
        # Calculate date ranges based on period
        now = datetime.now(timezone(timedelta(hours=-4)))
        
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif period == 'yesterday':
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == '7days':
            start_date = now - timedelta(days=7)
            end_date = now
        elif period == '30days':
            start_date = now - timedelta(days=30)
            end_date = now
        elif period == 'all':
            start_date = datetime(2020, 1, 1, tzinfo=timezone(timedelta(hours=-4)))
            end_date = now
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        
        # Filter applications by period
        status_changes = []
        for app in applications:
            app_status_updated_at = app.status_updated_at.replace(tzinfo=timezone(timedelta(hours=-4))) if app.status_updated_at else None
            if app_status_updated_at and start_date <= app_status_updated_at <= end_date:
                status_changes.append(app)
        
        # Calculate daily activities - count ALL activities (creation + updates)
        from collections import defaultdict
        daily_counts = defaultdict(lambda: defaultdict(int))
        
        # Iterate through all applications and count activities
        for app in applications:
            # Get all update files
            updates = job_processor.get_application_updates(app)
            
            # If no updates exist, count the application creation with current status
            if not updates:
                app_created_at = app.created_at.replace(tzinfo=timezone(timedelta(hours=-4)))
                if start_date <= app_created_at <= end_date:
                    date = app_created_at.date()
                    status = normalize_status_label(app.status)
                    daily_counts[date][status] += 1
            
            # Count all update files
            for update in updates:
                try:
                    from datetime import datetime as dt
                    update_dt = dt.strptime(update['timestamp'], '%Y%m%d%H%M%S')
                    update_dt = update_dt.replace(tzinfo=timezone(timedelta(hours=-4)))
                    
                    if start_date <= update_dt <= end_date:
                        date = update_dt.date()
                        status = normalize_status_label(update['status'])
                        daily_counts[date][status] += 1
                except:
                    continue
        
        # Get all dates with actual data
        all_dates = []
        if daily_counts:
            actual_start_date = min(daily_counts.keys())
            effective_start_date = max(actual_start_date, start_date.date())
            
            current_date = effective_start_date
            end_date_only = end_date.date()
            while current_date <= end_date_only:
                all_dates.append(current_date)
                current_date += timedelta(days=1)
        
        # Get all statuses
        all_statuses = set()
        for date in daily_counts:
            all_statuses.update(daily_counts[date].keys())
        all_statuses = sorted(all_statuses)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write daily activities section
        writer.writerow(['Daily Activities by Status'])
        writer.writerow(['Date'] + all_statuses)
        for date in all_dates:
            row = [str(date)]
            for status in all_statuses:
                row.append(daily_counts[date].get(status, 0))
            writer.writerow(row)
        
        # Add blank row
        writer.writerow([])
        
        # Write cumulative activities section
        writer.writerow(['Cumulative Activities by Status'])
        writer.writerow(['Date'] + all_statuses)
        cumulative_counts = {status: 0 for status in all_statuses}
        for date in all_dates:
            row = [str(date)]
            for status in all_statuses:
                cumulative_counts[status] += daily_counts[date].get(status, 0)
                row.append(cumulative_counts[status])
            writer.writerow(row)
        
        # Prepare response
        csv_data = output.getvalue()
        output.close()
        
        # Create filename with period
        filename = f"daily_activities_{period}_{now.strftime('%Y%m%d')}.csv"
        
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/daily-activities', methods=['GET'])
def get_daily_activities():
    """Get daily activities data (combined jobs + networking) - optimized using activity log"""
    try:
        from datetime import datetime, timezone, timedelta
        from pathlib import Path
        
        # ------------------------------------------------------------------
        # File-based caching for daily activities.
        # Single cache file since this endpoint has no query parameters.
        # Cache for 5 minutes (300 seconds) - activities are logged in real-time
        # ------------------------------------------------------------------
        cache_filename = "daily_activities_cache.json"
        cache_path = get_data_path('output') / Path(cache_filename)

        if not is_cache_stale(cache_path, ttl_seconds=300):
            cached = get_cached_json(cache_path)
            if cached is not None:
                return jsonify(cached)

        # Use activity log service for fast data retrieval
        daily_summary = activity_log_service.get_daily_activities_summary()
        
        # Convert to list format sorted by date (newest first)
        activities_list = []
        for date_str in sorted(daily_summary.keys(), reverse=True):
            # Parse date string and format for display
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            activities_list.append({
                'date': date_obj.strftime('%B %d, %Y'),
                'activity_count': len(daily_summary[date_str]),
                'activities': daily_summary[date_str]
            })

        response_payload = {
            'success': True,
            'daily_activities': activities_list
        }

        # Save to cache for subsequent fast loads.
        save_cached_json(cache_path, response_payload)

        return jsonify(response_payload)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/digest/generate', methods=['POST'])
def generate_digest():
    """Generate daily digest and optionally send via email"""
    try:
        import sys
        from pathlib import Path
        
        # Import the digest generator
        sys.path.insert(0, str(get_project_root()))
        from scripts.generate_daily_digest import DailyDigestGenerator
        
        # Initialize generator
        generator = DailyDigestGenerator()
        
        # Generate digest for today
        digest_path = generator.generate_digest()
        
        # Try to send email if configured
        email_sent = False
        email_message = ""
        try:
            email_sent = generator.send_email(digest_path)
            if email_sent:
                email_message = "Digest generated and emailed successfully."
            else:
                email_message = "Digest generated. Email not configured or disabled."
        except Exception as e:
            email_message = f"Digest generated. Email failed: {str(e)}"
        
        return jsonify({
            'success': True,
            'message': email_message or 'Digest generated successfully.',
            'digest_path': str(digest_path),
            'email_sent': email_sent
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates, optionally filtered by category"""
    try:
        category = request.args.get('category')
        if category:
            templates = template_manager.list_templates_by_category(category)
        else:
            templates = template_manager.list_templates()
        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create a new template"""
    try:
        data = request.json
        title = data.get('title')
        delivery_method = data.get('delivery_method')
        content = data.get('content')
        category = data.get('category', 'All')  # Default to 'All' for backward compatibility
        
        if not all([title, delivery_method, content]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: title, delivery_method, content'
            }), 400
        
        template = template_manager.create_template(title, delivery_method, content, category)
        
        return jsonify({
            'success': True,
            'message': 'Template created successfully',
            'template': template
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    try:
        success = template_manager.delete_template(template_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Template deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive analytics data for specified period"""
    try:
        from pathlib import Path

        period = request.args.get('period', '30days')
        
        # Validate period
        valid_periods = ['today', '7days', '30days', 'all']
        if period not in valid_periods:
            period = '30days'
        
        # Generate analytics
        gap_period = request.args.get('gap_period', 'all')  # For skill gaps: 'daily', 'weekly', 'monthly', 'all'

        # ------------------------------------------------------------------
        # File-based caching for analytics.
        # Cache key includes period and gap_period.
        # Analytics refreshes once per day (24 hours = 86400 seconds)
        # ------------------------------------------------------------------
        cache_filename = f"analytics_cache_{period}_{gap_period}.json"
        cache_path = get_data_path('output') / Path(cache_filename)

        if not is_cache_stale(cache_path, ttl_seconds=86400):  # 24 hours
            cached = get_cached_json(cache_path)
            if cached is not None:
                return jsonify(cached)

        analytics_data = analytics_generator.generate_analytics(period, gap_period)

        response_payload = {
            'success': True,
            **analytics_data
        }

        # Save to cache for subsequent fast loads.
        save_cached_json(cache_path, response_payload)

        return jsonify(response_payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/dashboard')
def view_dashboard():
    """View the generated dashboard"""
    # Only regenerate the dashboard when the cached HTML is missing or stale.
    # This avoids re-loading all applications and rebuilding the page on every request.
    if dashboard_generator.is_dashboard_stale():
        dashboard_generator.generate_index_page()
    
    dashboard_path = dashboard_generator.get_dashboard_path()
    
    if dashboard_path.exists():
        return send_from_directory(
            dashboard_path.parent,
            dashboard_path.name
        )
    return "Dashboard not found", 404

@app.route('/archived')
def archived_dashboard():
    """Archived applications dashboard"""
    from app.utils.file_utils import get_data_path
    # Always regenerate archived dashboard to ensure it's up to date
    dashboard_generator.generate_archived_dashboard()
    dashboard_path = get_data_path('output') / 'archived.html'
    
    if dashboard_path.exists():
        return send_from_directory(
            dashboard_path.parent,
            dashboard_path.name
        )
    return "Archived dashboard not generated yet.", 404


@app.route('/applications/<path:filepath>')
def serve_application_file(filepath):
    """Serve application files (summaries, documents, etc.)"""
    from app.utils.file_utils import get_data_path
    # Check both applications and applications_archived folders
    applications_dir = get_data_path('applications')
    archived_dir = get_data_path('applications_archived')
    
    # Try applications folder first
    file_path = applications_dir / filepath
    if file_path.exists() and file_path.is_file():
        return send_from_directory(
            file_path.parent,
            file_path.name
        )
    
    # Try archived folder
    file_path = archived_dir / filepath
    if file_path.exists() and file_path.is_file():
        return send_from_directory(
            file_path.parent,
            file_path.name
        )
    
    # File not found - redirect to dashboard instead of showing error
    # This handles cases where summary files were deleted (e.g., rejected applications)
    return redirect('/dashboard'), 302


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # #region agent log
    # Debug logging disabled - .cursor directory has special protections
    # with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
    #     f.write(json.dumps({"location":"web.py:main","message":"Starting main execution","data":{},"timestamp":time.time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"A"}) + '\n')
    # #endregion
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 51003))
    
    # #region agent log
    # Debug logging disabled - .cursor directory has special protections
    # with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
    #     f.write(json.dumps({"location":"web.py:main","message":"Port configured","data":{"port":port},"timestamp":time.time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"C"}) + '\n')
    # #endregion
    
    print("🚀 Starting Job Hunter Application...")
    print(f"📱 Open http://localhost:{port} in your browser")
    print(f"📊 Dashboard: http://localhost:{port}/dashboard")
    print(f"🤝 Networking: http://localhost:{port}/networking")
    print("Press Ctrl+C to stop")
    print()
    
    # Check Ollama connection
    try:
        if ai_analyzer.check_connection():
            print("✅ Ollama is connected")
            models = ai_analyzer.list_available_models()
            print(f"📦 Available models: {', '.join(models) if models else 'None'}")
        else:
            print("⚠️  Ollama is not connected. Please start Ollama:")
            print("   1. Install: brew install ollama")
            print("   2. Start: ollama serve")
            print("   3. Pull model: ollama pull llama3")
    except Exception as e:
        print(f"⚠️  Could not check Ollama connection: {e}")
    
    # #region agent log
    # Debug logging disabled - .cursor directory has special protections
    # with open('/Users/kervinleacock/Documents/Development/hunter/.cursor/debug.log', 'a') as f:
    #     f.write(json.dumps({"location":"web.py:main","message":"About to start Flask app","data":{"port":port,"host":"0.0.0.0","debug":True},"timestamp":time.time()*1000,"sessionId":"debug-session","runId":"startup","hypothesisId":"A"}) + '\n')
    # #endregion
    
    print()
    print("🔄 Starting Flask server...")
    app.run(debug=True, port=port, host='0.0.0.0')

