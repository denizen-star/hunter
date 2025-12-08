#!/usr/bin/env python3
"""
Web UI for Job Hunting Follow-Ups
Flask application providing REST API and web interface
"""
import os
import uuid
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
from app.utils.datetime_utils import format_for_display
from app.utils.file_utils import get_project_root

app = Flask(__name__, 
           template_folder='templates/web',
           static_folder='../static',
           static_url_path='/static')
CORS(app)

# Initialize services
resume_manager = ResumeManager()
job_processor = JobProcessor()
ai_analyzer = AIAnalyzer()
doc_generator = DocumentGenerator()
dashboard_generator = DashboardGenerator()
template_manager = TemplateManager()
analytics_generator = AnalyticsGenerator()

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

@app.route('/api/applications', methods=['GET'])
def get_all_applications():
    """Get all applications for dashboard cards"""
    try:
        applications = job_processor.list_all_applications()
        
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
        
        # Update fields
        resume.full_name = data.get('full_name', resume.full_name)
        resume.email = data.get('email', resume.email)
        resume.phone = data.get('phone', resume.phone)
        resume.linkedin = data.get('linkedin', resume.linkedin)
        resume.location = data.get('location', resume.location)
        resume.content = data.get('content', resume.content)
        
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
        company = data.get('company')
        job_title = data.get('job_title')
        job_description = data.get('job_description')
        job_url = data.get('job_url')
        
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
        
        # Update dashboard
        dashboard_generator.generate_index_page()
        
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
            # Load qualifications to regenerate summary
            if application.qualifications_path and Path(application.qualifications_path).exists():
                from app.utils.file_utils import read_text_file
                qual_content = read_text_file(application.qualifications_path)
                
                # Extract match score from qualifications
                import re
                match_score = 0.0
                score_match = re.search(r'Match Score:?\s*(\d+)', qual_content, re.IGNORECASE)
                if score_match:
                    match_score = float(score_match.group(1))
                
                # Create QualificationAnalysis object
                from app.models.qualification import QualificationAnalysis
                qualifications = QualificationAnalysis(
                    match_score=match_score,
                    features_compared=24,  # Default value
                    strong_matches=[],
                    missing_skills=[],
                    partial_matches=[],
                    soft_skills=[],
                    recommendations=[],
                    detailed_analysis=qual_content
                )
                
                # Update application metadata with qualifications info
                application.match_score = match_score
                application.qualifications_path = str(application.folder_path / "Headofdata-Qualifications.md")
                
                # Regenerate summary page
                doc_generator.generate_summary_page(application, qualifications)
                
                # Save updated metadata
                job_processor._save_application_metadata(application)
        except Exception as e:
            print(f"Warning: Could not regenerate summary page: {e}")
        
        # Update dashboard
        dashboard_generator.generate_index_page()
        
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
        
        # Update dashboard
        dashboard_generator.generate_index_page()
        
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
            if application.qualifications_path and Path(application.qualifications_path).exists():
                from app.utils.file_utils import read_text_file
                qual_content = read_text_file(application.qualifications_path)
                
                # Extract match score from qualifications
                import re
                match_score = 0.0
                score_match = re.search(r'Match Score:?\s*(\d+)', qual_content, re.IGNORECASE)
                if score_match:
                    match_score = float(score_match.group(1))
                
                # Create QualificationAnalysis object
                from app.models.qualification import QualificationAnalysis
                qualifications = QualificationAnalysis(
                    match_score=match_score,
                    features_compared=24,
                    strong_matches=[],
                    missing_skills=[],
                    partial_matches=[],
                    soft_skills=[],
                    recommendations=[],
                    detailed_analysis=qual_content
                )
                
                # Regenerate summary page with updated checklist
                doc_generator.generate_summary_page(application, qualifications)
        except Exception as e:
            print(f"Warning: Could not regenerate summary page: {e}")
        
        # Regenerate both dashboards to show updated progress pills
        dashboard_generator.generate_index_page()
        dashboard_generator.generate_progress_dashboard()
        
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
        
        # Update dashboard
        dashboard_generator.generate_index_page()
        
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
        
        # Update dashboard
        dashboard_generator.generate_index_page()
        
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
        from app.utils.file_utils import read_text_file
        qual_content = read_text_file(application.qualifications_path)
        
        # Build a minimal QualificationAnalysis instance from stored data
        from app.models.qualification import QualificationAnalysis
        qualifications = QualificationAnalysis(
            match_score=application.match_score or 0.0,
            features_compared=0,
            strong_matches=[],
            missing_skills=[],
            partial_matches=[],
            soft_skills=[],
            recommendations=[],
            detailed_analysis=qual_content
        )
        
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
        from app.utils.file_utils import read_text_file
        qual_content = read_text_file(application.qualifications_path)
        
        # Build a minimal QualificationAnalysis instance from stored data
        from app.models.qualification import QualificationAnalysis
        qualifications = QualificationAnalysis(
            match_score=application.match_score or 0.0,
            features_compared=0,
            strong_matches=[],
            missing_skills=[],
            partial_matches=[],
            soft_skills=[],
            recommendations=[],
            detailed_analysis=qual_content
        )
        
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


@app.route('/api/dashboard/update', methods=['POST'])
def update_dashboard():
    """Update the dashboard"""
    try:
        dashboard_generator.generate_index_page()
        dashboard_generator.generate_progress_dashboard()
        
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

@app.route('/api/reports', methods=['GET'])
def get_reports_data():
    """Get reports data for specified period"""
    try:
        from datetime import datetime, timedelta, timezone
        
        period = request.args.get('period', '30days')
        gap_period = request.args.get('gap_period', 'all')  # For skill gaps: 'daily', 'weekly', 'monthly', 'all'
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
            # Default to today
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        
        # Filter applications by period
        period_applications = []
        status_changes = []
        
        for app in applications:
            # Convert application datetimes to the same timezone format for comparison
            app_created_at = app.created_at.replace(tzinfo=timezone(timedelta(hours=-4)))
            app_status_updated_at = app.status_updated_at.replace(tzinfo=timezone(timedelta(hours=-4))) if app.status_updated_at else None
            
            if start_date <= app_created_at <= end_date:
                period_applications.append(app)
            
            # Check if status was updated in period
            if app_status_updated_at and start_date <= app_status_updated_at <= end_date:
                status_changes.append(app)
        
        # Applications by status (for period) - count applications created in period by their current status
        applications_by_status = {}
        for app in period_applications:
            status = normalize_status_label(app.status)
            applications_by_status[status] = applications_by_status.get(status, 0) + 1
        
        # Status changes by status (for period) - count status changes that happened in period by the new status
        status_changes_by_status = {}
        status_changes_count = 0
        for app in status_changes:
            status = normalize_status_label(app.status)
            status_changes_count += 1  # Include all status changes
            status_changes_by_status[status] = status_changes_by_status.get(status, 0) + 1
        
        # Follow-up applications (more than one week without updates)
        one_week_ago = now - timedelta(days=7)
        followup_applications = []
        
        for app in applications:
            # Skip applications that are already rejected or accepted
            if normalize_status_label(app.status) in ['rejected', 'accepted']:
                continue
            
            # Convert to same timezone for comparison
            app_created_at = app.created_at.replace(tzinfo=timezone(timedelta(hours=-4)))
            app_status_updated_at = app.status_updated_at.replace(tzinfo=timezone(timedelta(hours=-4))) if app.status_updated_at else None
            
            last_update = app_status_updated_at or app_created_at
            if last_update < one_week_ago:
                # Generate summary URL
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
        
        # Sort follow-up applications by newest update first
        followup_applications.sort(key=lambda x: x['last_updated'], reverse=True)
        
        # Flagged applications
        flagged_applications = []
        for app in applications:
            if app.flagged:
                # Generate summary URL
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
        
        # Sort flagged applications by newest update first
        flagged_applications.sort(key=lambda x: x['last_updated'], reverse=True)
        
        # Calculate rejected applications from status changes (applications rejected in period)
        rejected_count = status_changes_by_status.get('rejected', 0)
        
        # Calculate active applications (total - rejected)
        active_applications = len(period_applications) - rejected_count
        
        # Calculate total contact count from status_changes_by_status (matches the chart)
        total_contact_count = 0
        if 'contacted someone' in status_changes_by_status:
            total_contact_count += status_changes_by_status['contacted someone']
        if 'company response' in status_changes_by_status:
            total_contact_count += status_changes_by_status['company response']
        if 'contacted hiring manager' in status_changes_by_status:
            total_contact_count += status_changes_by_status['contacted hiring manager']
        
        # Calculate total actions (applications created + status changes) for the period
        total_actions = len(period_applications) + status_changes_count
        
        # Summary statistics
        summary = {
            'total_applications': len(period_applications),
            'new_applications': len(period_applications),
            'active_applications': active_applications,
            'status_changes': status_changes_count,
            'rejected': rejected_count,
            'followup_needed': len(followup_applications),
            'total_contact_count': total_contact_count,
            'total_actions': total_actions
        }
        
        return jsonify({
            'success': True,
            'period': period,
            'summary': summary,
            'applications_by_status': applications_by_status,
            'status_changes': status_changes_by_status,
            'followup_applications': followup_applications,
            'flagged_applications': flagged_applications
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/daily-activities', methods=['GET'])
def get_daily_activities():
    """Get daily activities data"""
    try:
        from datetime import datetime, timezone, timedelta
        
        applications = job_processor.list_all_applications()
        
        # Group activities by date
        daily_activities = {}
        
        for app in applications:
            # Get all updates for this application
            updates = job_processor.get_application_updates(app)
            
            # Add application creation as an activity
            created_date = app.created_at.replace(tzinfo=timezone(timedelta(hours=-4))).date()
            if created_date not in daily_activities:
                daily_activities[created_date] = []
            
            # Format timestamp for display
            created_timestamp = app.created_at.replace(tzinfo=timezone(timedelta(hours=-4))).strftime('%I:%M %p EST')
            
            daily_activities[created_date].append({
                'company': app.company,
                'position': app.job_title,
                'timestamp': created_timestamp,
                'activity': 'Application Created',
                'status': 'Created',
                'application_id': app.id,
                'datetime': app.created_at.replace(tzinfo=timezone(timedelta(hours=-4)))  # Add datetime for sorting
            })
            
            # Add status updates as activities
            for update in updates:
                try:
                    # Parse timestamp from filename
                    timestamp_str = update['timestamp']
                    dt = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                    dt = dt.replace(tzinfo=timezone(timedelta(hours=-4)))
                    update_date = dt.date()
                    
                    if update_date not in daily_activities:
                        daily_activities[update_date] = []
                    
                    # Format timestamp for display
                    display_timestamp = dt.strftime('%I:%M %p EST')
                    
                    daily_activities[update_date].append({
                        'company': app.company,
                        'position': app.job_title,
                        'timestamp': display_timestamp,
                        'activity': f'Status Changed to {update["status"]}',
                        'status': update['status'],
                        'application_id': app.id,
                        'datetime': dt  # Add datetime for sorting
                    })
                except Exception as e:
                    print(f"Error processing update {update}: {e}")
                    continue
        
        # Sort activities within each day by datetime (newest first)
        for date in daily_activities:
            daily_activities[date].sort(key=lambda x: x['datetime'], reverse=True)
            # Remove datetime field from final output (keep only for sorting)
            for activity in daily_activities[date]:
                del activity['datetime']
        
        # Convert to list format sorted by date (newest first)
        activities_list = []
        for date in sorted(daily_activities.keys(), reverse=True):
            activities_list.append({
                'date': date.strftime('%B %d, %Y'),
                'activity_count': len(daily_activities[date]),
                'activities': daily_activities[date]
            })
        
        return jsonify({
            'success': True,
            'daily_activities': activities_list
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all templates"""
    try:
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
        
        if not all([title, delivery_method, content]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: title, delivery_method, content'
            }), 400
        
        template = template_manager.create_template(title, delivery_method, content)
        
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
        period = request.args.get('period', '30days')
        
        # Validate period
        valid_periods = ['today', '7days', '30days', 'all']
        if period not in valid_periods:
            period = '30days'
        
        # Generate analytics
        gap_period = request.args.get('gap_period', 'all')  # For skill gaps: 'daily', 'weekly', 'monthly', 'all'
        analytics_data = analytics_generator.generate_analytics(period, gap_period)
        
        return jsonify({
            'success': True,
            **analytics_data
        })
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
    from app.utils.file_utils import get_data_path
    # Always regenerate dashboard to ensure it's up to date
    dashboard_generator.generate_index_page()
    dashboard_path = get_data_path('output') / 'index.html'
    
    if dashboard_path.exists():
        return send_from_directory(
            dashboard_path.parent,
            dashboard_path.name
        )
    return "Dashboard not found", 404

@app.route('/progress')
def view_progress_dashboard():
    """View the generated progress dashboard"""
    from app.utils.file_utils import get_data_path
    # Always regenerate progress dashboard to ensure it's up to date
    dashboard_generator.generate_progress_dashboard()
    progress_path = get_data_path('output') / 'progress.html'
    
    if progress_path.exists():
        return send_from_directory(
            progress_path.parent,
            progress_path.name
        )
    return "Dashboard not generated yet.", 404


@app.route('/applications/<path:filepath>')
def serve_application_file(filepath):
    """Serve application files (summaries, documents, etc.)"""
    from app.utils.file_utils import get_data_path
    applications_dir = get_data_path('applications')
    file_path = applications_dir / filepath
    
    if file_path.exists() and file_path.is_file():
        return send_from_directory(
            file_path.parent,
            file_path.name
        )
    # File not found - return 404
    return "File not found", 404


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 51003))
    
    print("🚀 Starting Job Hunter Application...")
    print(f"📱 Open http://localhost:{port} in your browser")
    print(f"📊 Dashboard: http://localhost:{port}/dashboard")
    print("Press Ctrl+C to stop")
    print()
    
    # Check Ollama connection
    if ai_analyzer.check_connection():
        print("✅ Ollama is connected")
        models = ai_analyzer.list_available_models()
        print(f"📦 Available models: {', '.join(models) if models else 'None'}")
    else:
        print("⚠️  Ollama is not connected. Please start Ollama:")
        print("   1. Install: brew install ollama")
        print("   2. Start: ollama serve")
        print("   3. Pull model: ollama pull llama3")
    
    print()
    app.run(debug=True, port=port, host='0.0.0.0')

