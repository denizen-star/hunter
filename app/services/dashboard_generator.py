"""Dashboard generation service"""
from pathlib import Path
from typing import List
from app.models.application import Application
from app.services.job_processor import JobProcessor
from app.utils.file_utils import get_data_path, ensure_dir_exists, write_text_file
from app.utils.datetime_utils import format_for_display


class DashboardGenerator:
    """Generates HTML dashboard"""
    
    def __init__(self):
        self.output_dir = get_data_path('output')
        ensure_dir_exists(self.output_dir)
        self.job_processor = JobProcessor()
    
    def generate_index_page(self) -> None:
        """Generate the main dashboard HTML page"""
        applications = self.job_processor.list_all_applications()
        
        html = self._create_dashboard_html(applications)
        
        dashboard_path = self.output_dir / 'index.html'
        write_text_file(html, dashboard_path)
        
        print(f"Dashboard generated: {dashboard_path}")
    
    def _create_dashboard_html(self, applications: List[Application]) -> str:
        """Create the HTML dashboard"""
        # Calculate stats for all possible statuses
        total = len(applications)
        status_counts = {
            'pending': len([a for a in applications if a.status.lower() == 'pending']),
            'applied': len([a for a in applications if a.status.lower() == 'applied']),
            'contacted someone': len([a for a in applications if a.status.lower() == 'contacted someone']),
            'contacted hiring manager': len([a for a in applications if a.status.lower() == 'contacted hiring manager']),
            'interviewed': len([a for a in applications if a.status.lower() == 'interviewed']),
            'offered': len([a for a in applications if a.status.lower() == 'offered']),
            'rejected': len([a for a in applications if a.status.lower() == 'rejected']),
            'accepted': len([a for a in applications if a.status.lower() == 'accepted'])
        }
        
        # Generate tabbed content for each status
        tabs_html = self._create_tabs_html(applications, status_counts)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application Dashboard</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f5f5f5;
            min-height: 100vh;
            padding: 0;
            margin: 0;
            position: relative;
        }}
        .container {{ 
            width: calc(100vw - 250px);
            margin: 0;
            padding: 20px 20px 20px 20px;
            margin-left: 250px;
            box-sizing: border-box;
        }}
        
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 250px;
            height: 100vh;
            background: #8b9dc3;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 1000;
            padding: 20px 0;
            overflow-y: auto;
        }}
        
        .sidebar-header {{
            padding: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }}
        
        .sidebar-header h3 {{
            color: white;
            font-size: 18px;
            font-weight: 600;
            margin: 0;
        }}
        
        .sidebar-menu {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .sidebar-menu li {{
            margin: 0;
        }}
        
        .sidebar-menu a {{
            display: block;
            padding: 15px 20px;
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
            font-weight: 500;
        }}
        
        .sidebar-menu a:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border-left-color: #ffffff;
            transform: translateX(5px);
        }}
        
        .sidebar-menu a.active {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border-left-color: #ffffff;
        }}
        
        .sidebar-menu a i {{
            margin-right: 10px;
            width: 20px;
            text-align: center;
        }}
        .header {{
            text-align: center;
            color: white;
            margin: 0 -20px;
            position: relative;
            z-index: 1;
            background: #8b9dc3;
            padding: 0 20px;
            width: calc(100% + 40px);
            border-radius: 0;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .header h1 {{
            font-size: 48px;
            margin-bottom: 10px;
            color: white;
            font-weight: 300;
        }}
        .actions {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .nav-bar {{
            background: rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(20px);
            padding: 15px 0;
            margin-bottom: 30px;
            border-radius: 10px;
            position: relative;
            z-index: 1;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .nav-links {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .nav-link {{
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 6px;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        .nav-link:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-1px);
        }}
        .btn {{
            background: white;
            color: #667eea;
            border: none;
            padding: 15px 40px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        .tabs-container {{
            background: white;
            backdrop-filter: blur(20px);
            border-radius: 0;
            border: 1px solid rgba(74, 85, 104, 0.2);
            box-shadow: 0 4px 12px rgba(74, 85, 104, 0.1);
            overflow: hidden;
            margin: 0 -20px 20px -20px;
            width: calc(100% + 40px);
            position: relative;
            z-index: 1;
        }}
        .tabs-header {{
            display: flex;
            background: #8b9dc3;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            overflow-x: auto;
        }}
        .tab {{
            flex: 1;
            min-width: 120px;
            padding: 15px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.8);
            transition: all 0.2s;
            white-space: nowrap;
            position: relative;
        }}
        .tab:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }}
        .tab.active {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border-bottom: 3px solid #ffffff;
        }}
        .tab-count {{
            font-size: 12px;
            opacity: 0.7;
            margin-left: 5px;
        }}
        .tab-content {{
            padding: 30px;
            min-height: 400px;
        }}
        .sort-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .sort-select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            background: white;
        }}
        .applications-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(74, 85, 104, 0.1);
            border: 1px solid rgba(74, 85, 104, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(74, 85, 104, 0.15);
        }}
        .card-company {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }}
        .card-title {{
            font-size: 18px;
            color: #666;
            margin-bottom: 15px;
        }}
        .card-status {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            text-transform: capitalize;
            margin-bottom: 15px;
        }}
        .status-pending {{ background: #fff3cd; color: #856404; }}
        .status-applied {{ background: #d1ecf1; color: #0c5460; }}
        .status-contacted someone {{ background: #e2e3e5; color: #383d41; }}
        .status-contacted hiring manager {{ background: #f8d7da; color: #721c24; }}
        .status-interviewed {{ background: #d4edda; color: #155724; }}
        .status-offered {{ background: #c3e6cb; color: #155724; }}
        .status-rejected {{ background: #f8d7da; color: #721c24; }}
        .status-accepted {{ background: #d4edda; color: #155724; }}
        .card-meta {{
            font-size: 13px;
            color: #999;
            margin-bottom: 8px;
        }}
        .card-actions {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        .card-btn {{
            display: inline-block;
            background: #8b9dc3;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.2s;
        }}
        .card-btn:hover {{
            background: #7a8bb0;
        }}
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            background: #f8f9fa;
            border-radius: 12px;
            color: #999;
        }}
        .empty-state-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        .empty-state-text {{
            font-size: 20px;
        }}
        .match-score {{
            float: right;
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h3>Job Hunter</h3>
        </div>
        <ul class="sidebar-menu">
            <li><a href="/" class="nav-link">Home</a></li>
            <li><a href="/new-application" class="nav-link">New Application</a></li>
            <li><a href="/dashboard" class="nav-link active">Dashboard</a></li>
            <li><a href="/reports" class="nav-link">Reports</a></li>
        </ul>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>Job Application Dashboard - {total}</h1>
        </div>
        
        
        {tabs_html}
    </div>
    
    <script>
        // AI Status Check Function - Show message on screen
        async function showAIStatus() {{
            try {{
                const response = await fetch('/api/check-ollama');
                const data = await response.json();
                
                // Create status message element
                let statusDiv = document.getElementById('ai-status-message');
                if (!statusDiv) {{
                    statusDiv = document.createElement('div');
                    statusDiv.id = 'ai-status-message';
                    statusDiv.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #28a745;
                        color: white;
                        padding: 15px 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                        z-index: 1000;
                        max-width: 300px;
                        font-size: 14px;
                    `;
                    document.body.appendChild(statusDiv);
                }}
                
                if (data.connected) {{
                    statusDiv.style.background = '#28a745';
                    statusDiv.innerHTML = `
                        <strong>AI Status: Connected</strong><br>
                        Model: ${{data.current_model}}<br>
                        Available: ${{data.available_models.join(', ')}}
                    `;
                }} else {{
                    statusDiv.style.background = '#dc3545';
                    statusDiv.innerHTML = `
                        <strong>AI Status: Not Connected</strong><br>
                        Please check your Ollama installation.
                    `;
                }}
                
                // Auto-hide after 5 seconds
                setTimeout(() => {{
                    if (statusDiv) statusDiv.remove();
                }}, 5000);
                
            }} catch (error) {{
                console.error('AI Status Error:', error);
            }}
        }}
        
        // New Application Function
        function openNewApplication() {{
            // Open new application form in same window
            window.location.href = '/new-application';
        }}
        
        // Resume Manager Function  
        function openResumeManager() {{
            // Open new application page where resume manager is located
            window.location.href = '/new-application';
        }}
        
        // Tab switching functionality
        function switchTab(status) {{
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {{
                content.style.display = 'none';
            }});
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            const selectedContent = document.getElementById('tab-' + status);
            if (selectedContent) {{
                selectedContent.style.display = 'block';
            }}
            
            // Add active class to clicked tab
            const selectedTab = document.querySelector(`[data-status="${{status}}"]`);
            if (selectedTab) {{
                selectedTab.classList.add('active');
            }}
            
            // Update sort dropdown for this tab
            updateSortOptions(status);
        }}
        
        // Update sort options based on current tab
        function updateSortOptions(status) {{
            const sortSelect = document.getElementById('sort-select-' + status);
            if (sortSelect) {{
                // Reset to default sorting
                sortSelect.value = 'updated_desc';
                sortApplications(status, 'updated_desc');
            }}
        }}
        
        // Sort applications in the current tab
        function sortApplications(status, sortBy) {{
            const tabContent = document.getElementById('tab-' + status);
            if (!tabContent) return;
            
            const grid = tabContent.querySelector('.applications-grid');
            if (!grid) return;
            
            const cards = Array.from(grid.querySelectorAll('.card'));
            
            cards.sort((a, b) => {{
                switch(sortBy) {{
                    case 'updated_desc':
                        return new Date(b.dataset.updatedAt) - new Date(a.dataset.updatedAt);
                    case 'updated_asc':
                        return new Date(a.dataset.updatedAt) - new Date(b.dataset.updatedAt);
                    case 'applied_desc':
                        return new Date(b.dataset.appliedAt) - new Date(a.dataset.appliedAt);
                    case 'applied_asc':
                        return new Date(a.dataset.appliedAt) - new Date(b.dataset.appliedAt);
                    case 'job_posted_desc':
                        return new Date(b.dataset.appliedAt) - new Date(a.dataset.appliedAt);
                    case 'job_posted_asc':
                        return new Date(a.dataset.appliedAt) - new Date(b.dataset.appliedAt);
                    case 'match_desc':
                        return parseFloat(b.dataset.matchScore || 0) - parseFloat(a.dataset.matchScore || 0);
                    case 'match_asc':
                        return parseFloat(a.dataset.matchScore || 0) - parseFloat(b.dataset.matchScore || 0);
                    default:
                        return 0;
                }}
            }});
            
            // Re-append sorted cards
            cards.forEach(card => grid.appendChild(card));
        }}
        
        // Handle sort dropdown change
        function handleSortChange() {{
            const activeTab = document.querySelector('.tab.active');
            
            if (activeTab) {{
                const status = activeTab.dataset.status;
                const sortSelect = document.getElementById('sort-select-' + status);
                if (sortSelect) {{
                    sortApplications(status, sortSelect.value);
                }}
            }}
        }}
        
        // Initialize with first tab active
        document.addEventListener('DOMContentLoaded', function() {{
            // Activate first tab by default
            const firstTab = document.querySelector('.tab');
            if (firstTab) {{
                const status = firstTab.dataset.status;
                switchTab(status);
            }}
        }});
    </script>
</body>
</html>"""
        return html
    
    def _create_tabs_html(self, applications: List[Application], status_counts: dict) -> str:
        """Create the tabbed interface HTML"""
        # Define status order with 'all' first, then as shown in the image
        status_order = [
            'all',
            'pending',
            'applied', 
            'contacted someone',
            'contacted hiring manager',
            'interviewed',
            'offered',
            'rejected',
            'accepted'
        ]
        
        # Create tab headers
        tab_headers = ""
        for status in status_order:
            if status == 'all':
                count = len(applications)  # Total count for all applications
                status_display = "All"
            else:
                count = status_counts.get(status, 0)
                # Shorten long tab titles to prevent overlap
                if status == 'contacted someone':
                    status_display = "Contacted"
                elif status == 'contacted hiring manager':
                    status_display = "Hiring Mgr"
                else:
                    status_display = status.replace('_', ' ').title()
            tab_headers += f'''
                <button class="tab" data-status="{status}" onclick="switchTab('{status}')">
                    {status_display}
                    <span class="tab-count">({count})</span>
                </button>
            '''
        
        # Create tab contents
        tab_contents = ""
        for status in status_order:
            if status == 'all':
                status_apps = applications  # All applications
                status_title = "All Applications"
                default_display = 'block'  # Show 'all' tab by default
            else:
                status_apps = [app for app in applications if app.status.lower() == status]
                # Use full names in content area for clarity
                if status == 'contacted someone':
                    status_title = "Contacted Someone Applications"
                elif status == 'contacted hiring manager':
                    status_title = "Contacted Hiring Manager Applications"
                else:
                    status_title = f"{status.replace('_', ' ').title()} Applications"
                default_display = 'none'
            
            # Sort applications by updated timestamp (newest first) by default
            status_apps.sort(key=lambda x: x.status_updated_at or x.created_at, reverse=True)
            
            cards_html = ""
            for app in status_apps:
                cards_html += self._create_application_card(app)
            
            tab_contents += f'''
                <div class="tab-content" id="tab-{status}" style="display: {default_display}">
                    <div class="sort-controls">
                        <h3 style="margin: 0; color: #333;">{status_title}</h3>
                        <select id="sort-select-{status}" class="sort-select" onchange="handleSortChange()">
                            <option value="updated_desc">Updated (Newest First)</option>
                            <option value="updated_asc">Updated (Oldest First)</option>
                            <option value="applied_desc">Applied (Newest First)</option>
                            <option value="applied_asc">Applied (Oldest First)</option>
                            <option value="job_posted_desc">Job Posted (Newest First)</option>
                            <option value="job_posted_asc">Job Posted (Oldest First)</option>
                            <option value="match_desc">Match % (Highest First)</option>
                            <option value="match_asc">Match % (Lowest First)</option>
                        </select>
                    </div>
                    {f'<div class="applications-grid">{cards_html}</div>' if cards_html else self._create_empty_state(status)}
                </div>
            '''
        
        return f'''
        <div class="tabs-container">
            <div class="tabs-header">
                {tab_headers}
            </div>
            {tab_contents}
        </div>
        '''
    
    def _create_application_card(self, app: Application) -> str:
        """Create HTML for a single application card"""
        # Generate proper URLs for summary and folder
        if app.summary_path:
            folder_name = app.folder_path.name
            summary_filename = app.summary_path.name
            summary_link = f"/applications/{folder_name}/{summary_filename}"
        else:
            summary_link = "#"
        
        match_score_html = f'<span class="match-score">{app.match_score:.0f}%</span>' if app.match_score else ''
        
        # Create data attributes for sorting
        updated_at = app.status_updated_at or app.created_at
        applied_at = app.created_at
        match_score = app.match_score or 0
        
        return f"""
        <div class="card" 
             data-updated-at="{updated_at.isoformat()}" 
             data-applied-at="{applied_at.isoformat()}" 
             data-match-score="{match_score}">
            <div class="card-company">
                {app.company}
                {match_score_html}
            </div>
            <div class="card-title">{app.job_title}</div>
            <div>
                <span class="card-status status-{app.status.lower()}">{app.status}</span>
            </div>
            <div class="card-meta">
                📅 Applied: {format_for_display(app.created_at)}
            </div>
            <div class="card-meta">
                📋 Posted: {app.posted_date if app.posted_date else 'N/A'}
            </div>
            <div class="card-meta">
                🔄 Updated: {format_for_display(app.status_updated_at)}
            </div>
            <div class="card-actions">
                <a href="{summary_link}" class="card-btn">View Summary →</a>
            </div>
        </div>
        """
    
    def _create_empty_state(self, status: str = None) -> str:
        """Create empty state HTML"""
        if status:
            status_display = status.replace('_', ' ').title()
            message = f"No {status_display} applications yet."
        else:
            message = "No applications yet. Create your first one!"
        
        return f"""
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div class="empty-state-text">{message}</div>
        </div>
        """

