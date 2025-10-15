#!/usr/bin/env python3
"""
Web UI for Job Hunting Follow-Ups
Flask application providing REST API and web interface
"""
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_cors import CORS

from app.services.resume_manager import ResumeManager
from app.services.job_processor import JobProcessor
from app.services.ai_analyzer import AIAnalyzer
from app.services.document_generator import DocumentGenerator
from app.services.dashboard_generator import DashboardGenerator
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


@app.route('/')
def index():
    """Landing page"""
    return render_template('landing.html')

@app.route('/new-application')
def new_application():
    """New application form page"""
    return render_template('ui.html')


@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        applications = job_processor.list_all_applications()
        
        stats = {
            'total': len(applications),
            'pending': len([app for app in applications if app.status.lower() == 'pending']),
            'applied': len([app for app in applications if app.status.lower() == 'applied']),
            'interviewed': len([app for app in applications if app.status.lower() == 'interviewed']),
            'offered': len([app for app in applications if app.status.lower() == 'offered']),
            'rejected': len([app for app in applications if app.status.lower() == 'rejected']),
            'accepted': len([app for app in applications if app.status.lower() == 'accepted'])
        }
        
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
            'match_score': app.match_score
        } for app in recent])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications', methods=['GET'])
def get_all_applications():
    """Get all applications for dashboard cards"""
    try:
        applications = job_processor.list_all_applications()
        
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
            'summary_path': str(app.summary_path) if app.summary_path else None
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
        
        resume_manager.save_base_resume(resume)
        
        return jsonify({
            'success': True,
            'message': 'Resume updated successfully'
        })
    except Exception as e:
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
        
        # Generate all documents
        doc_generator.generate_all_documents(application)
        
        # Save updated metadata with paths
        job_processor._save_application_metadata(application)
        
        # Update dashboard
        dashboard_generator.generate_index_page()
        
        # Generate relative URL for summary
        summary_url = None
        if application.summary_path:
            # Create relative path: /applications/folder-name/summary.html
            folder_name = application.folder_path.name
            summary_filename = application.summary_path.name
            summary_url = f"/applications/{folder_name}/{summary_filename}"
        
        # Load qualifications analysis for detailed response
        qualifications_data = None
        if application.qualifications_path and application.qualifications_path.exists():
            try:
                from app.models.qualification import QualificationAnalysis
                from app.utils.file_utils import read_text_file
                
                # Parse qualifications from file to get structured data
                qual_content = read_text_file(application.qualifications_path)
                
                # Create a basic QualificationAnalysis object from the match score
                qualifications_data = {
                    'match_score': application.match_score or 0.0,
                    'features_compared': 0,  # Will be parsed from content if available
                    'strong_matches': [],
                    'missing_skills': [],
                    'partial_matches': [],
                    'soft_skills': [],
                    'recommendations': [],
                    'detailed_analysis': qual_content
                }
                
                # Try to parse additional data from the content
                import re
                
                # Extract features compared
                features_match = re.search(r'Features Compared:?\s*(\d+)', qual_content, re.IGNORECASE)
                if features_match:
                    qualifications_data['features_compared'] = int(features_match.group(1))
                
                # Extract strong matches
                strong_section = re.search(r'Strong Matches:?\s*([^\n]+)', qual_content, re.IGNORECASE)
                if strong_section:
                    qualifications_data['strong_matches'] = [s.strip() for s in strong_section.group(1).split(',')]
                
                # Extract missing skills
                missing_section = re.search(r'Missing Skills:?\s*([^\n]+)', qual_content, re.IGNORECASE)
                if missing_section:
                    qualifications_data['missing_skills'] = [s.strip() for s in missing_section.group(1).split(',')]
                
            except Exception as e:
                print(f"Warning: Could not load qualifications data: {e}")
                qualifications_data = None

        return jsonify({
            'success': True,
            'message': f'Application created successfully',
            'application_id': application.id,
            'folder_path': str(application.folder_path),
            'summary_path': str(application.summary_path),
            'summary_url': summary_url,
            'match_score': application.match_score,
            'qualifications': qualifications_data
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
                'match_score': app.match_score
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
        
        return jsonify({
            'success': True,
            'message': f'Status updated to {status}',
            'application_id': application.id,
            'status': status,
            'updated_at': format_for_display(application.status_updated_at)
        })
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


@app.route('/api/dashboard/update', methods=['POST'])
def update_dashboard():
    """Update the dashboard"""
    try:
        dashboard_generator.generate_index_page()
        
        return jsonify({
            'success': True,
            'message': 'Dashboard updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/reports')
def view_reports():
    """View the reports page"""
    return render_template('reports.html')

@app.route('/api/reports', methods=['GET'])
def get_reports_data():
    """Get reports data for specified period"""
    try:
        from datetime import datetime, timedelta
        import pytz
        
        period = request.args.get('period', 'today')
        
        # Get all applications
        applications = job_processor.list_all_applications()
        
        # Calculate date ranges
        now = datetime.now(pytz.timezone('US/Eastern'))
        
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
        else:  # all
            start_date = datetime(2020, 1, 1, tzinfo=pytz.timezone('US/Eastern'))
            end_date = now
        
        # Filter applications by period
        period_applications = []
        status_changes = []
        
        for app in applications:
            # Check if application was created in period
            if start_date <= app.created_at <= end_date:
                period_applications.append(app)
            
            # Check if status was updated in period (must be significantly different from creation)
            if app.status_updated_at and start_date <= app.status_updated_at <= end_date:
                # Check if the status update was significantly different from creation (more than 1 minute)
                time_diff = abs((app.status_updated_at - app.created_at).total_seconds())
                if time_diff > 60:  # More than 1 minute difference
                    status_changes.append(app)
        
        # Applications by status (for period) - count applications created in period by their current status
        applications_by_status = {}
        for app in period_applications:
            status = app.status.lower()
            applications_by_status[status] = applications_by_status.get(status, 0) + 1
        
        # Status changes by status (for period) - count status changes that happened in period by the new status
        status_changes_by_status = {}
        for app in status_changes:
            status = app.status.lower()
            status_changes_by_status[status] = status_changes_by_status.get(status, 0) + 1
        
        
        # Follow-up applications (more than one week without updates)
        one_week_ago = now - timedelta(days=7)
        followup_applications = []
        
        for app in applications:
            # Skip applications that are already rejected or accepted
            if app.status.lower() in ['rejected', 'accepted']:
                continue
            
            last_update = app.status_updated_at or app.created_at
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
                    'summary_url': summary_url
                })
        
        # Sort follow-up applications by newest update first
        followup_applications.sort(key=lambda x: x['last_updated'], reverse=True)
        
        # Summary statistics
        summary = {
            'total_applications': len(period_applications),
            'new_applications': len(period_applications),
            'status_changes': len(status_changes),
            'followup_needed': len(followup_applications)
        }
        
        return jsonify({
            'success': True,
            'period': period,
            'summary': summary,
            'applications_by_status': applications_by_status,
            'status_changes': status_changes_by_status,
            'followup_applications': followup_applications
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard')
def view_dashboard():
    """View the generated dashboard"""
    from app.utils.file_utils import get_data_path
    dashboard_path = get_data_path('output') / 'index.html'
    
    if dashboard_path.exists():
        return send_from_directory(
            dashboard_path.parent,
            dashboard_path.name
        )
    else:
        # Generate dashboard if it doesn't exist
        dashboard_generator.generate_index_page()
        if dashboard_path.exists():
            return send_from_directory(
                dashboard_path.parent,
                dashboard_path.name
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

