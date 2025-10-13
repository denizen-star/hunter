#!/usr/bin/env python3
"""
Web UI for Job Hunting Follow-Ups
Flask application providing REST API and web interface
"""
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

from app.services.resume_manager import ResumeManager
from app.services.job_processor import JobProcessor
from app.services.ai_analyzer import AIAnalyzer
from app.services.document_generator import DocumentGenerator
from app.services.dashboard_generator import DashboardGenerator
from app.utils.datetime_utils import format_for_display
from app.utils.file_utils import get_project_root

app = Flask(__name__, template_folder='templates/web')
CORS(app)

# Initialize services
resume_manager = ResumeManager()
job_processor = JobProcessor()
ai_analyzer = AIAnalyzer()
doc_generator = DocumentGenerator()
dashboard_generator = DashboardGenerator()


@app.route('/')
def index():
    """Main UI page"""
    return render_template('ui.html')


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
        
        return jsonify({
            'success': True,
            'message': f'Application created successfully',
            'application_id': application.id,
            'folder_path': str(application.folder_path),
            'summary_path': str(application.summary_path),
            'summary_url': summary_url,
            'match_score': application.match_score
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
    print("🚀 Starting Job Hunter Application...")
    print("📱 Open http://localhost:51002 in your browser")
    print("📊 Dashboard: http://localhost:51002/dashboard")
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
    app.run(debug=True, port=51002, host='0.0.0.0')

