"""Dashboard generation service"""
from pathlib import Path
from typing import List
from app.models.application import Application
from app.services.job_processor import JobProcessor
from app.utils.file_utils import get_data_path, ensure_dir_exists, write_text_file
from app.utils.datetime_utils import format_for_display

STATUS_NORMALIZATION_MAP = {
    'contacted hiring manager': 'company response',
    'company response': 'company response',
    'interviewed': 'interview notes',
    'interview notes': 'interview notes',
    'interview follow up': 'interview - follow up',
    'interview follow-up': 'interview - follow up',
    'interview - follow up': 'interview - follow up',
}


class DashboardGenerator:
    """Generates HTML dashboard"""
    
    def __init__(self):
        self.output_dir = get_data_path('output')
        ensure_dir_exists(self.output_dir)
        self.job_processor = JobProcessor()
    
    def _normalize_status(self, status: str) -> str:
        """Normalize status strings for consistent reporting."""
        if not status:
            return ''
        normalized = status.strip().lower()
        normalized = normalized.replace('–', '-').replace('—', '-')
        normalized = normalized.replace('  ', ' ')
        return STATUS_NORMALIZATION_MAP.get(normalized, normalized)

    def _status_matches(self, status: str, *targets: str) -> bool:
        """Return True if status matches any target labels after normalization."""
        normalized_status = self._normalize_status(status)
        normalized_targets = {self._normalize_status(target) for target in targets}
        return normalized_status in normalized_targets

    def _status_to_class(self, status: str) -> str:
        """Convert status label into CSS-friendly class suffix."""
        if not status:
            return "unknown"
        return (
            status.strip()
            .lower()
            .replace("&", "and")
            .replace("/", "-")
            .replace("(", "")
            .replace(")", "")
            .replace("'", "")
            .replace(".", "")
            .replace(",", "")
            .replace(" - ", "-")
            .replace(" ", "-")
        )

    def generate_index_page(self) -> None:
        """Generate the main dashboard HTML page"""
        applications = self.job_processor.list_all_applications()
        
        html = self._create_dashboard_html(applications)
        
        dashboard_path = self.output_dir / 'index.html'
        write_text_file(html, dashboard_path)
        
        print(f"Dashboard generated: {dashboard_path}")
    
    def generate_progress_dashboard(self) -> None:
        """Generate the progress dashboard HTML page"""
        applications = self.job_processor.list_all_applications()
        
        html = self._create_progress_dashboard_html(applications)
        
        dashboard_path = self.output_dir / 'progress.html'
        write_text_file(html, dashboard_path)
        
        print(f"Progress dashboard generated: {dashboard_path}")
    
    def _create_dashboard_html(self, applications: List[Application]) -> str:
        """Create the HTML dashboard"""
        # Calculate stats for all possible statuses
        def count_status(*labels):
            return len([a for a in applications if self._status_matches(a.status, *labels)])

        status_counts = {
            'pending': count_status('pending'),
            'applied': count_status('applied'),
            'contacted someone': count_status('contacted someone'),
            'company response': count_status('company response', 'contacted hiring manager'),
            'scheduled interview': count_status('scheduled interview'),
            'interview notes': count_status('interview notes', 'interviewed'),
            'interview - follow up': count_status('interview - follow up'),
            'offered': count_status('offered'),
            'rejected': count_status('rejected'),
            'accepted': count_status('accepted')
        }
        
        total = len(applications)

        # Generate stat cards and filter interface
        dashboard_html = self._create_dashboard_with_stats(applications, status_counts)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application Dashboard</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <!-- Google Fonts - Poppins -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #fafafa;
            --bg-hover: #f9fafb;
            --bg-active: #f3f4f6;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --text-tertiary: #9ca3af;
            --border-primary: #e5e7eb;
            --border-light: #f3f4f6;
            --accent-blue: #3b82f6;
            --accent-blue-hover: #2563eb;
            --accent-blue-light: #eff6ff;
            --accent-green: #10b981;
            --font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --space-xs: 4px;
            --space-sm: 8px;
            --space-md: 16px;
            --space-lg: 24px;
            --space-xl: 32px;
            --radius-sm: 6px;
            --radius-md: 8px;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.08);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: var(--font-family); 
            background: var(--bg-secondary);
            min-height: 100vh;
            padding: 0;
            margin: 0;
            position: relative;
            overflow-x: hidden;
            color: var(--text-primary);
        }}
        .container {{ 
            width: calc(100vw - 180px);
            margin: 0;
            padding: var(--space-lg);
            margin-left: 180px;
            box-sizing: border-box;
        }}
        
        /* Hero Header - Full Width */
        .hero-header {{
            background: #ffffff;
            border-bottom: 1px solid #e5e7eb;
            padding: 8px 16px;
            position: sticky;
            top: 0;
            z-index: 100;
            width: calc(100% - 180px);
            margin-left: 180px;
            box-sizing: border-box;
        }}
        
        .hero-header-top {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
        }}
        
        .hero-header h1 {{
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
            text-align: left;
        }}
        
        .hero-header-subtitle {{
            font-size: 14px;
            color: #6b7280;
            margin: 0;
        }}
        
        /* Footer */
        .page-footer {{
            background: #ffffff;
            border-top: 1px solid #e5e7eb;
            padding: 20px 32px;
            width: calc(100% - 180px);
            margin-left: 180px;
            box-sizing: border-box;
            position: fixed;
            bottom: 0;
            z-index: 100;
        }}
        
        .footer-buttons {{
            display: flex;
            justify-content: center;
            gap: 16px;
        }}
        
        .footer-btn {{
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            color: #1f2937;
            text-decoration: none;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        
        .footer-btn:hover {{
            background: #f9fafb;
            border-color: #d1d5db;
        }}
        
        .footer-btn-primary {{
            background: #3b82f6;
            color: #ffffff;
            border-color: #3b82f6;
        }}
        
        .footer-btn-primary:hover {{
            background: #2563eb;
            border-color: #2563eb;
        }}
        
        .container {{
            padding-bottom: 100px; /* Space for fixed footer */
        }}
        
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 180px;
            height: 100vh;
            background: var(--bg-primary);
            border-right: 1px solid var(--border-primary);
            z-index: 1000;
            padding: var(--space-md) 0;
            overflow-y: auto;
        }}
        
        .sidebar-header {{
            padding: var(--space-md) var(--space-lg);
            border-bottom: 1px solid var(--border-primary);
            margin-bottom: var(--space-md);
        }}
        
        .sidebar-header h3 {{
            color: var(--text-primary);
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
            padding: 12px var(--space-lg);
            color: var(--text-secondary);
            text-decoration: none;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
            font-weight: 500;
            font-size: 14px;
        }}
        
        .sidebar-menu a:hover {{
            background: var(--bg-hover);
            color: var(--text-primary);
            border-left-color: var(--accent-blue);
        }}
        
        .sidebar-menu a.active {{
            background: var(--bg-active);
            color: var(--text-primary);
            border-left-color: var(--accent-blue);
        }}
        
        .sidebar-menu a i {{
            margin-right: 10px;
            width: 20px;
            text-align: center;
        }}
        .header {{
            text-align: center;
            margin-bottom: var(--space-xl);
            background: var(--bg-primary);
            padding: var(--space-xl);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-sm);
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: var(--space-sm);
            color: var(--text-primary);
            font-weight: 600;
        }}
        .actions {{
            text-align: center;
            margin-bottom: var(--space-lg);
        }}
        .nav-bar {{
            background: var(--bg-primary);
            padding: var(--space-md) 0;
            margin-bottom: var(--space-lg);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-sm);
        }}
        .nav-links {{
            display: flex;
            justify-content: center;
            gap: var(--space-md);
            flex-wrap: wrap;
        }}
        .nav-link {{
            color: var(--text-primary);
            text-decoration: none;
            padding: 10px var(--space-md);
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
            font-weight: var(--font-medium);
            font-size: var(--font-sm);
        }}
        .nav-link:hover {{
            background: var(--bg-hover);
        }}
        .btn {{
            background: var(--accent-blue);
            color: #ffffff;
            border: none;
            padding: 12px var(--space-xl);
            font-size: var(--font-sm);
            font-weight: var(--font-medium);
            border-radius: var(--radius-sm);
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s ease;
            font-family: var(--font-family);
        }}
        .btn:hover {{
            background: var(--accent-blue-hover);
        }}
        .tabs-container {{
            background: var(--bg-primary);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-sm);
            overflow: hidden;
            margin-bottom: var(--space-lg);
        }}
        .tabs-header {{
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-primary);
            overflow-x: auto;
            flex-wrap: wrap;
        }}
        .tab {{
            flex: 1;
            min-width: 100px;
            padding: 14px var(--space-lg);
            background: none;
            border: none;
            cursor: pointer;
            font-size: var(--font-sm);
            font-weight: var(--font-medium);
            color: var(--text-secondary);
            transition: all 0.2s ease;
            white-space: nowrap;
            position: relative;
            font-family: var(--font-family);
        }}
        .tab:hover {{
            background: var(--bg-active);
            color: var(--text-primary);
        }}
        .tab.active {{
            background: var(--accent-blue);
            color: #ffffff;
        }}
        .tab-count {{
            font-size: 12px;
            opacity: 0.7;
            margin-left: 5px;
        }}
        .tab-content {{
            padding: var(--space-lg);
            min-height: 400px;
        }}
        .sort-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--space-lg);
            padding-bottom: var(--space-md);
            border-bottom: 1px solid var(--border-light);
        }}
        .sort-controls h3 {{
            margin: 0;
            color: var(--text-primary);
            font-size: var(--font-lg);
            font-weight: var(--font-semibold);
        }}
        .sort-select {{
            padding: 10px 16px;
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-sm);
            font-size: var(--font-sm);
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-family);
            cursor: pointer;
        }}
        .sort-select:focus {{
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px var(--accent-blue-light);
        }}
        .applications-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: var(--space-lg);
        }}
        .card {{
            background: var(--bg-primary);
            border-radius: var(--radius-md);
            padding: var(--space-lg);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-primary);
            transition: all 0.2s ease;
        }}
        .card:hover {{
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }}
        .card-company {{
            font-size: var(--font-xl);
            font-weight: var(--font-bold);
            color: var(--text-primary);
            flex: 1;
        }}
        .flag-btn {{
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: var(--space-xs);
            margin-left: var(--space-sm);
            transition: transform 0.2s;
            opacity: 0.6;
        }}
        .flag-btn:hover {{
            transform: scale(1.2);
            opacity: 1;
        }}
        .flag-btn.flagged {{
            opacity: 1;
        }}
        .card-title {{
            font-size: var(--font-sm);
            color: var(--text-primary);
            margin-bottom: var(--space-md);
            font-weight: var(--font-medium);
        }}
        .card-status-container {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        .card-status {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            text-transform: capitalize;
        }}
        .card-progress-pill {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
            background: var(--bg-active);
            color: var(--text-secondary);
            border: 1px solid var(--border-primary);
        }}
        .status-pending {{ background: #fef3c7; color: #92400e; }}
        .status-applied {{ background: #dbeafe; color: #1e40af; }}
        .status-contacted-someone {{ background: var(--bg-active); color: var(--text-secondary); }}
        .status-contacted-hiring-manager {{ background: #fee2e2; color: #991b1b; }}
        .status-company-response {{ background: var(--accent-blue-light); color: #1e40af; }}
        .status-scheduled-interview {{ background: #fef3c7; color: #92400e; }}
        .status-interviewed {{ background: #d1fae5; color: #065f46; }}
        .status-interview-notes {{ background: #d1fae5; color: #065f46; }}
        .status-interview-follow-up {{ background: #fce7f3; color: #9f1239; }}
        .status-offered {{ background: #d1fae5; color: #065f46; }}
        .status-rejected {{ background: #fee2e2; color: #991b1b; }}
        .status-accepted {{ background: #d1fae5; color: #065f46; }}
        .card-meta {{
            font-size: 10px;
            color: var(--text-secondary);
            margin-bottom: var(--space-sm);
        }}
        .card-actions {{
            margin-top: var(--space-lg);
            padding-top: var(--space-md);
            border-top: 1px solid var(--border-light);
        }}
        .card-btn {{
            display: inline-block;
            background: var(--accent-blue);
            color: #ffffff;
            padding: 10px var(--space-md);
            border-radius: var(--radius-sm);
            text-decoration: none;
            font-size: var(--font-sm);
            font-weight: var(--font-medium);
            transition: all 0.2s ease;
            font-family: var(--font-family);
            width: 100%;
            text-align: center;
        }}
        .card-btn:hover {{
            background: var(--accent-blue-hover);
        }}
        .empty-state {{
            text-align: center;
            padding: 64px var(--space-xl);
            color: var(--text-secondary);
        }}
        .empty-state-icon {{
            font-size: 48px;
            margin-bottom: var(--space-md);
            opacity: 0.5;
        }}
        .empty-state-text {{
            font-size: var(--font-lg);
            font-weight: var(--font-semibold);
            color: var(--text-primary);
        }}
        .match-score {{
            float: right;
            font-size: var(--font-lg);
            font-weight: var(--font-bold);
            color: var(--accent-blue);
        }}
        .hidden {{ display: none; }}
        
        /* Status Toggle Box */
        .status-toggle-box {{
            background: var(--bg-primary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            margin-bottom: var(--space-lg);
            box-shadow: var(--shadow-sm);
        }}
        
        .status-toggle-header {{
            font-size: var(--font-sm);
            font-weight: var(--font-semibold);
            color: var(--text-primary);
            margin-bottom: var(--space-sm);
        }}
        
        .status-toggle-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: var(--space-xs);
        }}
        
        .status-toggle-btn {{
            padding: 6px 12px;
            font-size: var(--font-xs);
            font-weight: var(--font-medium);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-sm);
            background: var(--bg-primary);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: var(--font-family);
        }}
        
        .status-toggle-btn:hover {{
            background: var(--bg-hover);
            border-color: var(--accent-blue);
            color: var(--text-primary);
        }}
        
        .status-toggle-btn.active {{
            background: var(--accent-blue);
            color: #ffffff;
            border-color: var(--accent-blue);
        }}
        
        /* Dashboard Stats Container */
        .dashboard-stats-container {{
            padding: var(--space-lg);
        }}
        
        /* Stat Cards Grid - Single row, ultra-compact */
        .stat-cards-grid {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 6px;
            margin-bottom: var(--space-sm);
            max-width: 1200px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .stat-card {{
            background: var(--bg-primary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-sm);
            padding: 6px;
            text-align: center;
            box-shadow: none;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        
        .stat-card:hover {{
            box-shadow: var(--shadow-sm);
            transform: translateY(-1px);
            border-color: var(--accent-blue);
        }}
        
        .stat-card.active {{
            border: 1px solid var(--accent-blue);
            background: var(--accent-blue-light);
        }}
        
        .stat-number {{
            font-size: 17px;
            font-weight: var(--font-bold);
            color: var(--text-primary);
            margin-bottom: 1px;
            line-height: 1.2;
        }}
        
        .stat-label {{
            font-size: 10px;
            color: var(--text-secondary);
            font-weight: var(--font-medium);
            line-height: 1.2;
        }}
        
        @media (max-width: 1400px) {{
            .stat-cards-grid {{
                grid-template-columns: repeat(6, 1fr);
            }}
        }}
        
        @media (max-width: 900px) {{
            .stat-cards-grid {{
                grid-template-columns: repeat(4, 1fr);
            }}
        }}
        
        @media (max-width: 600px) {{
            .stat-cards-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h3>Hunter</h3>
        </div>
        <ul class="sidebar-menu">
            <li><a href="/" class="nav-link">Home</a></li>
            <li><a href="/new-application" class="nav-link">New Application</a></li>
            <li><a href="/templates" class="nav-link">Templates</a></li>
            <li><a href="/progress" class="nav-link">Progress</a></li>
            <li><a href="/dashboard" class="nav-link active">Dashboard</a></li>
            <li><a href="/reports" class="nav-link">Reports</a></li>
            <li><a href="/daily-activities" class="nav-link">Daily Activities</a></li>
            <li><a href="#" onclick="showAIStatus(); return false;" class="nav-link">Check AI Status</a></li>
        </ul>
    </div>
    
    <!-- Hero Header -->
    <div class="hero-header">
        <div class="hero-header-top">
            <h1>Job Application Dashboard - {total}</h1>
        </div>
        </div>
        
    <div class="container">
        {dashboard_html}
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
        
        // Filter applications by status
        function filterApplications(filterStatus) {{
            // Update active stat card
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach(card => {{
                card.classList.remove('active');
                card.style.border = '1px solid var(--border-primary)';
            }});
            const activeCard = document.querySelector(`.stat-card[data-status="${{filterStatus}}"]`);
            if (activeCard) {{
                activeCard.classList.add('active');
            }}
            
            // Get all application cards
            const grid = document.getElementById('applications-grid');
            if (!grid) return;
            
            const cards = Array.from(grid.querySelectorAll('.card'));
            
            // Filter cards based on status
            cards.forEach(card => {{
                let show = false;
                const statusElement = card.querySelector('.card-status');
                const statusText = statusElement?.textContent.toLowerCase() || '';
                const statusClass = statusElement?.className || '';
                const isFlagged = card.dataset.flagged === 'true';
                
                if (filterStatus === 'all') {{
                    show = true;
                }} else if (filterStatus === 'active') {{
                    // Show all non-rejected and non-accepted
                    show = !statusText.includes('rejected') && !statusText.includes('accepted');
                }} else if (filterStatus === 'flagged') {{
                    show = isFlagged;
                }} else if (filterStatus === 'pending') {{
                    show = statusText.includes('pending');
                }} else if (filterStatus === 'applied') {{
                    show = statusText.includes('applied') && !statusText.includes('company') && !statusClass.includes('company');
                }} else if (filterStatus === 'contacted') {{
                    show = statusText.includes('contacted') || statusClass.includes('contacted');
                }} else if (filterStatus === 'company') {{
                    show = statusText.includes('company') || statusClass.includes('company-response');
                }} else if (filterStatus === 'scheduled') {{
                    show = statusText.includes('scheduled') || statusClass.includes('scheduled');
                }} else if (filterStatus === 'follow-up') {{
                    show = statusText.includes('follow') || statusClass.includes('follow');
                }} else if (filterStatus === 'offered') {{
                    show = statusText.includes('offered') || statusClass.includes('offered');
                }} else if (filterStatus === 'rejected') {{
                    show = statusText.includes('rejected') || statusClass.includes('rejected');
                }} else if (filterStatus === 'accepted') {{
                    show = statusText.includes('accepted') || statusClass.includes('accepted');
                }}
                
                card.style.display = show ? '' : 'none';
            }});
        }}
        
        // Sort applications
        function sortApplications(sortBy) {{
            const grid = document.getElementById('applications-grid');
            if (!grid) return;
            
            const cards = Array.from(grid.querySelectorAll('.card:not([style*="display: none"])'));
            
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
            const sortSelect = document.getElementById('sort-select');
                if (sortSelect) {{
                sortApplications(sortSelect.value);
            }}
        }}
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {{
            // Make stat cards clickable
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach(card => {{
                card.addEventListener('click', function() {{
                    const status = this.dataset.status;
                    filterApplications(status);
                }});
            }});
            
            // Initialize with "active" filter active
            filterApplications('active');
        }});
        
        // Toggle flag for an application
        async function toggleFlag(appId, currentFlagged) {{
            try {{
                const newFlagged = !currentFlagged;
                const response = await fetch(`/api/applications/${{appId}}/flag`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ flagged: newFlagged }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    // Find the card by looking for the button with matching onclick attribute
                    const flagBtn = Array.from(document.querySelectorAll('.flag-btn')).find(btn => 
                        btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(`'${{appId}}'`)
                    );
                    
                    if (flagBtn) {{
                        flagBtn.textContent = newFlagged ? '🚩' : '⚐';
                        flagBtn.className = `flag-btn ${{newFlagged ? 'flagged' : 'unflagged'}}`;
                        flagBtn.title = newFlagged ? 'Unflag this job' : 'Flag this job';
                        flagBtn.setAttribute('onclick', `toggleFlag('${{appId}}', ${{String(newFlagged).toLowerCase()}})`);
                        
                        // Update the card's data-flagged attribute
                        const card = flagBtn.closest('.card');
                        if (card) {{
                            card.setAttribute('data-flagged', String(newFlagged).toLowerCase());
                        }}
                    }}
                    
                    // Reload the page to update the flagged tab count and ensure consistency
                    setTimeout(() => {{
                        window.location.reload();
                    }}, 300);
                }} else {{
                    alert('Failed to update flag: ' + (data.error || 'Unknown error'));
                }}
            }} catch (error) {{
                console.error('Error toggling flag:', error);
                alert('Error updating flag. Please try again.');
            }}
        }}
        
    </script>
</body>
</html>"""
        return html
    
    def _create_dashboard_with_stats(self, applications: List[Application], status_counts: dict) -> str:
        """Create dashboard with stat cards and filter buttons"""
        # Calculate counts for each status
        def count_status(*labels):
            return len([a for a in applications if self._status_matches(a.status, *labels)])
        
        def count_flagged():
            return len([a for a in applications if a.flagged])
        
        def count_active():
            return len([a for a in applications if a.status.lower() != 'rejected' and a.status.lower() != 'accepted'])
        
        # Calculate stats
        stats = {
            'active': count_active(),
            'all': len(applications),
            'flagged': count_flagged(),
            'pending': count_status('pending'),
            'applied': count_status('applied'),
            'contacted': count_status('contacted someone'),
            'company': count_status('company response', 'contacted hiring manager'),
            'scheduled': count_status('scheduled interview'),
            'follow-up': count_status('interview - follow up'),
            'offered': count_status('offered'),
            'rejected': count_status('rejected'),
            'accepted': count_status('accepted')
        }
        
        # Create stat cards (two rows, 6 cards per row)
        stat_cards_html = ""
        status_order = ['active', 'all', 'flagged', 'pending', 'applied', 'contacted', 'company', 'scheduled', 'follow-up', 'offered', 'rejected', 'accepted']
        status_labels = {
            'active': 'Active',
            'all': 'All',
            'flagged': 'Flagged',
            'pending': 'Pending',
            'applied': 'Applied',
            'contacted': 'Contacted',
            'company': 'Company',
            'scheduled': 'Scheduled',
            'follow-up': 'Follow Up',
            'offered': 'Offered',
            'rejected': 'Rejected',
            'accepted': 'Accepted'
        }
        
        for i, status in enumerate(status_order):
            count = stats[status]
            label = status_labels[status]
            stat_cards_html += f'''
                <div class="stat-card" data-status="{status}">
                    <div class="stat-number">{count}</div>
                    <div class="stat-label">{label}</div>
                </div>
            '''
        
        # Create all application cards
        cards_html = ""
        # Sort applications by updated timestamp (newest first)
        def safe_datetime_sort_key(app):
            if app.status_updated_at:
                return str(app.status_updated_at)
            return str(app.created_at)
        
        sorted_apps = sorted(applications, key=safe_datetime_sort_key, reverse=True)
        for app in sorted_apps:
            cards_html += self._create_application_card(app)
        
        return f'''
        <div class="dashboard-stats-container">
            <div class="stat-cards-grid">
                {stat_cards_html}
            </div>
            <div class="sort-controls">
                <h3 style="margin: 0; color: var(--text-primary); font-size: var(--font-lg); font-weight: var(--font-semibold);">Applications</h3>
                <select id="sort-select" class="sort-select" onchange="handleSortChange()">
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
            <div class="applications-grid" id="applications-grid">
                {cards_html if cards_html else self._create_empty_state('all')}
            </div>
        </div>
        '''
    
    def _create_tabs_html(self, applications: List[Application], status_counts: dict) -> str:
        """Create the tabbed interface HTML"""
        # Define status order with 'active' first (as landing page), then 'all', then 'flagged', then as shown in the image
        status_order = [
            'active',
            'all',
            'flagged',
            'pending',
            'applied', 
            'contacted someone',
            'company response',
            'scheduled interview',
            'interview - follow up',
            'offered',
            'rejected',
            'accepted'
        ]
        
        # Create tab headers
        tab_headers = ""
        for status in status_order:
            if status == 'active':
                # Count all applications except rejected ones
                count = len([app for app in applications if app.status.lower() != 'rejected'])
                status_display = "Active"
            elif status == 'all':
                count = len(applications)  # Total count for all applications
                status_display = "All"
            elif status == 'flagged':
                count = len([app for app in applications if app.flagged])
                status_display = "Flagged"
            else:
                count = status_counts.get(status, 0)
                # Shorten long tab titles to prevent overlap
                if status == 'contacted someone':
                    status_display = "Contacted"
                elif status == 'company response':
                    status_display = "Company"
                elif status == 'scheduled interview':
                    status_display = "Scheduled"
                elif status == 'interview - follow up':
                    status_display = "Follow Up"
                else:
                    status_display = status.replace('_', ' ').title()
            tab_headers += f'''
                <button class="tab" data-status="{status}" onclick="switchTab('{status}')">
                    {status_display}
                </button>
            '''
        
        # Create tab contents
        tab_contents = ""
        for status in status_order:
            if status == 'active':
                # Count all applications except rejected ones
                count = len([app for app in applications if app.status.lower() != 'rejected'])
                # All applications except rejected ones
                status_apps = [app for app in applications if app.status.lower() != 'rejected']
                status_title = f"Active Applications ({count})"
                default_display = 'block'  # Show 'active' tab by default (landing page)
            elif status == 'all':
                count = len(applications)  # Total count for all applications
                status_apps = applications  # All applications
                status_title = f"All Applications ({count})"
                default_display = 'none'  # No longer the default
            elif status == 'flagged':
                count = len([app for app in applications if app.flagged])
                status_apps = [app for app in applications if app.flagged]
                status_title = f"Flagged Applications ({count})"
                default_display = 'none'
            else:
                count = status_counts.get(status, 0)
                status_apps = [app for app in applications if self._status_matches(app.status, status)]
                # Use full names in content area for clarity
                if status == 'contacted someone':
                    status_title = f"Contacted Someone Applications ({count})"
                elif status == 'company response':
                    status_title = f"Company Response Applications ({count})"
                elif status == 'scheduled interview':
                    status_title = f"Scheduled Interview Applications ({count})"
                elif status == 'interview - follow up':
                    status_title = f"Interview - Follow Up Applications ({count})"
                else:
                    status_title = f"{status.replace('_', ' ').title()} Applications ({count})"
                default_display = 'none'
            
            # Sort applications by updated timestamp (newest first) by default
            # Use string comparison to avoid datetime timezone issues
            def safe_datetime_sort_key(app):
                if app.status_updated_at:
                    return str(app.status_updated_at)
                return str(app.created_at)
            
            status_apps.sort(key=safe_datetime_sort_key, reverse=True)
            
            cards_html = ""
            for app in status_apps:
                cards_html += self._create_application_card(app)
            
            # Add status toggle box for Active Applications tab
            status_toggle_html = ""
            if status == 'active':
                status_toggle_html = f'''
                    <div class="status-toggle-box">
                        <div class="status-toggle-header">Filter by Status:</div>
                        <div class="status-toggle-buttons">
                            <button class="status-toggle-btn active" onclick="filterByStatus('active', 'active')">Active</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'flagged')">Flagged</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'pending')">Pending</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'applied')">Applied</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'contacted')">Contacted</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'company')">Company</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'scheduled')">Scheduled</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'follow-up')">Follow Up</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'offered')">Offered</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'rejected')">Rejected</button>
                            <button class="status-toggle-btn" onclick="filterByStatus('active', 'all')">All</button>
                        </div>
                    </div>
                '''
            
            tab_contents += f'''
                <div class="tab-content" id="tab-{status}" style="display: {default_display}">
                    <div class="sort-controls">
                        <h3 style="margin: 0; color: var(--text-primary); font-size: var(--font-lg); font-weight: var(--font-semibold);">{status_title}</h3>
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
                    {status_toggle_html}
                    {f'<div class="applications-grid" id="applications-grid-{status}">{cards_html}</div>' if cards_html else self._create_empty_state(status)}
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
        
        # Flag button HTML
        flag_icon = '🚩' if app.flagged else '⚐'
        flag_class = 'flagged' if app.flagged else 'unflagged'
        flag_title = 'Unflag this job' if app.flagged else 'Flag this job'
        
        return f"""
        <div class="card" 
             data-updated-at="{updated_at.isoformat()}" 
             data-applied-at="{applied_at.isoformat()}" 
             data-match-score="{match_score}"
             data-flagged="{str(app.flagged).lower()}">
            <div class="card-header">
                <div class="card-company">
                    {app.company}
                    {match_score_html}
                </div>
                <button class="flag-btn {flag_class}" 
                        onclick="toggleFlag('{app.id}', {str(app.flagged).lower()})" 
                        title="{flag_title}">
                    {flag_icon}
                </button>
            </div>
            <div class="card-title">{app.job_title}</div>
            <div class="card-status-container">
                <span class="card-status status-{self._status_to_class(app.status)}">{app.status}</span>
                {self._get_progress_pill_html(app)}
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
    
    def _get_progress_pill_html(self, app: Application) -> str:
        """Get progress pill HTML for dashboard card"""
        latest_item = app.get_latest_completed_checklist_item()
        
        if not latest_item:
            return ""
        
        checklist_definitions = {
            "application_submitted": "Application Submitted",
            "linkedin_message_sent": "LinkedIn Message Sent",
            "contact_email_found": "Contact Email Found",
            "email_verified": "Email Verified",
            "email_sent": "Email Sent",
            "message_read": "Message Read",
            "profile_viewed": "Profile Viewed",
            "response_received": "Response Received",
            "followup_sent": "Follow-up Sent",
            "interview_scheduled": "Interview Scheduled",
            "interview_completed": "Interview Completed",
            "thank_you_sent": "Thank You Sent"
        }
        
        display_name = checklist_definitions.get(latest_item, latest_item)
        return f'<span class="card-progress-pill">{display_name}</span>'
    
    def _create_progress_dashboard_html(self, applications: List[Application]) -> str:
        """Create the progress dashboard HTML"""
        # Filter out rejected applications
        active_apps = [app for app in applications if app.status.lower() != 'rejected']
        
        # Group applications by their latest completed checklist item
        progress_groups = {}
        no_progress = []
        
        checklist_definitions = {
            "application_submitted": "Application Submitted",
            "linkedin_message_sent": "LinkedIn Message Sent",
            "contact_email_found": "Contact Email Found",
            "email_verified": "Email Verified",
            "email_sent": "Email Sent",
            "message_read": "Message Read",
            "profile_viewed": "Profile Viewed",
            "response_received": "Response Received",
            "followup_sent": "Follow-up Sent",
            "interview_scheduled": "Interview Scheduled",
            "interview_completed": "Interview Completed",
            "thank_you_sent": "Thank You Sent"
        }
        
        # Define progress order
        progress_order = list(checklist_definitions.keys())
        
        for app in active_apps:
            latest_item = app.get_latest_completed_checklist_item()
            if latest_item:
                if latest_item not in progress_groups:
                    progress_groups[latest_item] = []
                progress_groups[latest_item].append(app)
            else:
                no_progress.append(app)
        
        # Calculate counts
        progress_counts = {key: len(progress_groups.get(key, [])) for key in progress_order}
        progress_counts['no_progress'] = len(no_progress)
        progress_counts['all'] = len(active_apps)
        
        # Generate tabs HTML
        tabs_html = self._create_progress_tabs_html(active_apps, progress_groups, no_progress, progress_counts, checklist_definitions, progress_order)
        
        total = len(active_apps)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Progress Dashboard - Job Applications</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <!-- Google Fonts - Poppins -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #fafafa;
            --bg-hover: #f9fafb;
            --bg-active: #f3f4f6;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --text-tertiary: #9ca3af;
            --border-primary: #e5e7eb;
            --border-light: #f3f4f6;
            --accent-blue: #3b82f6;
            --accent-blue-hover: #2563eb;
            --accent-blue-light: #eff6ff;
            --accent-green: #10b981;
            --font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-xs: 12px;
            --font-sm: 14px;
            --font-base: 16px;
            --font-lg: 18px;
            --font-xl: 20px;
            --font-2xl: 24px;
            --font-3xl: 32px;
            --font-medium: 500;
            --font-semibold: 600;
            --font-bold: 700;
            --space-xs: 4px;
            --space-sm: 8px;
            --space-md: 16px;
            --space-lg: 24px;
            --space-xl: 32px;
            --radius-sm: 6px;
            --radius-md: 8px;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.08);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: var(--font-family); 
            background: var(--bg-secondary);
            min-height: 100vh;
            padding: 0;
            margin: 0;
            position: relative;
            overflow-x: hidden;
            color: var(--text-primary);
        }}
        .container {{ 
            width: calc(100vw - 180px);
            margin: 0;
            padding: var(--space-lg);
            margin-left: 180px;
            box-sizing: border-box;
        }}
        
        /* Hero Header - Full Width */
        .hero-header {{
            background: #ffffff;
            border-bottom: 1px solid #e5e7eb;
            padding: 8px 16px;
            position: sticky;
            top: 0;
            z-index: 100;
            width: calc(100% - 180px);
            margin-left: 180px;
            box-sizing: border-box;
        }}
        
        .hero-header-top {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
        }}
        
        .hero-header h1 {{
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
            text-align: left;
        }}
        
        .hero-header-subtitle {{
            font-size: 14px;
            color: #6b7280;
            margin: 0;
        }}
        
        /* Footer */
        .page-footer {{
            background: #ffffff;
            border-top: 1px solid #e5e7eb;
            padding: 20px 32px;
            width: calc(100% - 180px);
            margin-left: 180px;
            box-sizing: border-box;
            position: fixed;
            bottom: 0;
            z-index: 100;
        }}
        
        .footer-buttons {{
            display: flex;
            justify-content: center;
            gap: 16px;
        }}
        
        .footer-btn {{
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            color: #1f2937;
            text-decoration: none;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        
        .footer-btn:hover {{
            background: #f9fafb;
            border-color: #d1d5db;
        }}
        
        .footer-btn-primary {{
            background: #3b82f6;
            color: #ffffff;
            border-color: #3b82f6;
        }}
        
        .footer-btn-primary:hover {{
            background: #2563eb;
            border-color: #2563eb;
        }}
        
        .container {{
            padding-bottom: 100px; /* Space for fixed footer */
        }}
        
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 180px;
            height: 100vh;
            background: var(--bg-primary);
            border-right: 1px solid var(--border-primary);
            z-index: 1000;
            padding: var(--space-md) 0;
            overflow-y: auto;
        }}
        
        .sidebar-header {{
            padding: var(--space-md) var(--space-lg);
            border-bottom: 1px solid var(--border-primary);
            margin-bottom: var(--space-md);
        }}
        
        .sidebar-header h3 {{
            color: var(--text-primary);
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
            padding: 12px var(--space-lg);
            color: var(--text-secondary);
            text-decoration: none;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
            font-weight: 500;
            font-size: 14px;
        }}
        
        .sidebar-menu a:hover {{
            background: var(--bg-hover);
            color: var(--text-primary);
            border-left-color: var(--accent-blue);
        }}
        
        .sidebar-menu a.active {{
            background: var(--bg-active);
            color: var(--text-primary);
            border-left-color: var(--accent-blue);
        }}
        
        .header {{
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: var(--space-xl);
            border-radius: var(--radius-md);
            margin-bottom: var(--space-lg);
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-sm);
        }}
        
        .header h1 {{
            font-size: var(--font-2xl);
            margin-bottom: var(--space-sm);
            font-weight: 600;
        }}
        
        .header p {{
            font-size: var(--font-base);
            color: var(--text-secondary);
        }}
        
        .tabs-container {{
            background: transparent;
            border: none;
            box-shadow: none;
            overflow: visible;
            margin-bottom: var(--space-md);
        }}
        
        .tabs-header {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 6px;
            background: transparent;
            border: none;
            overflow-x: auto;
            padding: 0;
            flex-wrap: nowrap;
            margin-bottom: var(--space-sm);
        }}
        
        .tab {{
            background: var(--bg-primary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-sm);
            padding: 6px;
            text-align: center;
            box-shadow: none;
            transition: all 0.2s ease;
            cursor: pointer;
            font-size: 10px;
            font-weight: var(--font-medium);
            color: var(--text-secondary);
            white-space: nowrap;
            font-family: var(--font-family);
            min-width: auto;
            flex: 0 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 2px;
        }}
        
        .tab:hover {{
            box-shadow: var(--shadow-sm);
            transform: translateY(-1px);
            border-color: var(--accent-blue);
        }}
        
        .tab.active {{
            border: 1px solid var(--accent-blue);
            background: var(--accent-blue-light);
            color: var(--text-primary);
        }}
        
        .tab-count {{
            font-size: 17px;
            font-weight: var(--font-bold);
            color: var(--text-primary);
            line-height: 1.2;
        }}
        
        .tab-label {{
            font-size: 10px;
            color: var(--text-secondary);
            font-weight: var(--font-medium);
            line-height: 1.2;
        }}
        
        @media (max-width: 1400px) {{
            .tabs-header {{
                grid-template-columns: repeat(6, 1fr);
            }}
        }}
        
        @media (max-width: 900px) {{
            .tabs-header {{
                grid-template-columns: repeat(4, 1fr);
            }}
        }}
        
        @media (max-width: 600px) {{
            .tabs-header {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        .tab-count {{
            font-size: 12px;
            opacity: 0.7;
            margin-left: 5px;
        }}
        
        .tab-content {{
            padding: var(--space-lg);
            min-height: 400px;
        }}
        
        .sort-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--space-lg);
            padding-bottom: var(--space-md);
            border-bottom: 1px solid var(--border-light);
        }}
        
        .sort-controls h3 {{
            margin: 0;
            color: var(--text-primary);
            font-size: var(--font-lg);
            font-weight: var(--font-semibold);
        }}
        
        .sort-select {{
            padding: 10px 16px;
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-sm);
            font-size: var(--font-sm);
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-family);
            cursor: pointer;
        }}
        
        .sort-select:focus {{
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px var(--accent-blue-light);
        }}
        
        .applications-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: var(--space-lg);
        }}
        
        .card {{
            background: var(--bg-primary);
            border-radius: var(--radius-md);
            padding: var(--space-lg);
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-primary);
            transition: all 0.2s ease;
        }}
        
        .card:hover {{
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--space-sm);
        }}
        
        .card-company {{
            font-size: var(--font-xl);
            font-weight: var(--font-bold);
            color: var(--text-primary);
            flex: 1;
        }}
        
        .flag-btn {{
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            opacity: 0.5;
            transition: opacity 0.2s;
        }}
        
        .flag-btn:hover {{
            opacity: 1;
        }}
        
        .flag-btn.flagged {{
            opacity: 1;
        }}
        
        .card-title {{
            font-size: var(--font-sm);
            color: var(--text-primary);
            margin-bottom: var(--space-md);
            font-weight: var(--font-medium);
        }}
        
        .card-status-container {{
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            margin-bottom: var(--space-md);
            flex-wrap: wrap;
        }}
        
        .card-status {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: var(--font-xs);
            font-weight: var(--font-medium);
            text-transform: capitalize;
        }}
        
        .card-progress-pill {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: var(--font-xs);
            font-weight: var(--font-medium);
            background: var(--bg-active);
            color: var(--text-secondary);
            border: 1px solid var(--border-primary);
        }}
        
        .status-pending {{ background: #fef3c7; color: #92400e; }}
        .status-applied {{ background: #dbeafe; color: #1e40af; }}
        .status-contacted-someone {{ background: var(--bg-active); color: var(--text-secondary); }}
        .status-company-response {{ background: var(--accent-blue-light); color: #1e40af; }}
        .status-scheduled-interview {{ background: #fef3c7; color: #92400e; }}
        .status-interview-notes {{ background: #d1fae5; color: #065f46; }}
        .status-interview-follow-up {{ background: #fce7f3; color: #9f1239; }}
        .status-offered {{ background: #d1fae5; color: #065f46; }}
        .status-rejected {{ background: #fee2e2; color: #991b1b; }}
        .status-accepted {{ background: #d1fae5; color: #065f46; }}
        
        .card-meta {{
            font-size: 10px;
            color: var(--text-secondary);
            margin-bottom: var(--space-sm);
        }}
        
        .card-actions {{
            margin-top: var(--space-lg);
            padding-top: var(--space-md);
            border-top: 1px solid var(--border-light);
        }}
        
        .card-btn {{
            display: inline-block;
            background: var(--accent-blue);
            color: #ffffff;
            padding: 10px var(--space-md);
            border-radius: var(--radius-sm);
            text-decoration: none;
            font-size: var(--font-sm);
            font-weight: var(--font-medium);
            transition: all 0.2s ease;
            font-family: var(--font-family);
            width: 100%;
            text-align: center;
        }}
        
        .card-btn:hover {{
            background: var(--accent-blue-hover);
        }}
        
        .empty-state {{
            text-align: center;
            padding: 64px var(--space-xl);
            color: var(--text-secondary);
        }}
        
        .empty-state-icon {{
            font-size: 48px;
            margin-bottom: var(--space-md);
            opacity: 0.5;
        }}
        
        .empty-state-text {{
            font-size: var(--font-lg);
            font-weight: var(--font-semibold);
            color: var(--text-primary);
        }}
        
        .match-score {{
            float: right;
            font-size: var(--font-lg);
            font-weight: var(--font-bold);
            color: var(--accent-blue);
        }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h3>Hunter</h3>
        </div>
        <ul class="sidebar-menu">
            <li><a href="/" class="nav-link">Home</a></li>
            <li><a href="/new-application" class="nav-link">New Application</a></li>
            <li><a href="/templates" class="nav-link">Templates</a></li>
            <li><a href="/progress" class="nav-link active">Progress</a></li>
            <li><a href="/dashboard" class="nav-link">Dashboard</a></li>
            <li><a href="/reports" class="nav-link">Reports</a></li>
            <li><a href="/daily-activities" class="nav-link">Daily Activities</a></li>
            <li><a href="#" onclick="showAIStatus(); return false;" class="nav-link">Check AI Status</a></li>
            <li><a href="/new-application?resume=true" class="nav-link">Manage Resume</a></li>
        </ul>
    </div>
    
    <!-- Hero Header -->
    <div class="hero-header">
        <div class="hero-header-top">
            <h1>Progress Dashboard - {total} Applications</h1>
        </div>
        </div>
    
    <div class="container">
        
        {tabs_html}
    </div>
    
    <script>
        function switchTab(progressKey) {{
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {{
                content.style.display = 'none';
            }});
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            const target = document.getElementById('progress-' + progressKey);
            if (target) {{
                target.style.display = 'block';
            }}
            
            // Activate clicked tab
            const clickedTab = document.querySelector(`[data-progress="${{progressKey}}"]`);
            if (clickedTab) {{
                clickedTab.classList.add('active');
            }}
        }}
        
        function sortCards(selectElement, progressKey) {{
            const tabContent = document.getElementById('progress-' + progressKey);
            if (!tabContent) return;
            
            const cards = Array.from(tabContent.querySelectorAll('.card'));
            const sortBy = selectElement.value;
            
            cards.sort((a, b) => {{
                if (sortBy === 'date-applied') {{
                    return new Date(b.dataset.appliedAt) - new Date(a.dataset.appliedAt);
                }} else if (sortBy === 'date-updated') {{
                    return new Date(b.dataset.updatedAt) - new Date(a.dataset.updatedAt);
                }} else if (sortBy === 'match-score') {{
                    return parseFloat(b.dataset.matchScore) - parseFloat(a.dataset.matchScore);
                }} else if (sortBy === 'company') {{
                    return a.querySelector('.card-company').textContent.localeCompare(b.querySelector('.card-company').textContent);
                }}
                return 0;
            }});
            
            const grid = tabContent.querySelector('.applications-grid');
            cards.forEach(card => grid.appendChild(card));
        }}
        
        async function toggleFlag(appId, currentFlagged) {{
            try {{
                const response = await fetch(`/api/applications/${{appId}}/flag`, {{
                    method: 'PUT',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ flagged: !currentFlagged }})
                }});
                
                const result = await response.json();
                if (result.success) {{
                    location.reload();
                }} else {{
                    alert('Error updating flag. Please try again.');
                }}
            }} catch (error) {{
                console.error('Error toggling flag:', error);
                alert('Error updating flag. Please try again.');
            }}
        }}
        
        // Initialize with 'all' tab as default
        document.addEventListener('DOMContentLoaded', function() {{
            const allTab = document.querySelector('[data-progress="all"]');
            if (allTab) {{
                switchTab('all');
            }}
        }});
    </script>
    
    <!-- Footer -->
    <div class="page-footer">
        <div class="footer-buttons">
            <a href="/new-application" class="footer-btn footer-btn-primary">New Application</a>
            <a href="/new-application?resume=true" class="footer-btn">Manage Resume</a>
        </div>
    </div>
</body>
</html>"""
        return html
    
    def _create_progress_tabs_html(self, applications: List[Application], progress_groups: dict, no_progress: List[Application], progress_counts: dict, checklist_definitions: dict, progress_order: list) -> str:
        """Create the progress tabs HTML"""
        # Create tab headers
        tab_headers = ""
        
        # Add 'all' tab first
        count = progress_counts.get('all', 0)
        tab_headers += f'''
            <button class="tab active" data-progress="all" onclick="switchTab('all')">
                <div class="tab-count">{count}</div>
                <div class="tab-label">All</div>
            </button>
        '''
        
        # Add 'no_progress' tab
        if progress_counts.get('no_progress', 0) > 0:
            count = progress_counts['no_progress']
            tab_headers += f'''
                <button class="tab" data-progress="no_progress" onclick="switchTab('no_progress')">
                    <div class="tab-count">{count}</div>
                    <div class="tab-label">No Progress</div>
                </button>
            '''
        
        # Add tabs for each progress stage
        for progress_key in progress_order:
            count = progress_counts.get(progress_key, 0)
            if count > 0:
                display_name = checklist_definitions[progress_key]
                # Shorten long names for tabs
                if len(display_name) > 20:
                    short_name = display_name.split(',')[0] if ',' in display_name else display_name[:17] + '...'
                else:
                    short_name = display_name
                
                tab_headers += f'''
                    <button class="tab" data-progress="{progress_key}" onclick="switchTab('{progress_key}')">
                        <div class="tab-count">{count}</div>
                        <div class="tab-label">{short_name}</div>
                    </button>
                '''
        
        # Create tab contents
        tab_contents = ""
        
        # 'all' tab
        cards_html = ''.join([self._create_application_card(app) for app in applications])
        tab_contents += f'''
            <div id="progress-all" class="tab-content" style="display: block;">
                <div class="sort-controls">
                    <h3 style="margin: 0; color: var(--text-primary); font-size: var(--font-lg); font-weight: var(--font-semibold);">All Applications ({progress_counts['all']})</h3>
                    <select class="sort-select" onchange="sortCards(this, 'all')">
                        <option value="date-updated">Date Updated</option>
                        <option value="date-applied">Date Applied</option>
                        <option value="match-score">Match Score</option>
                        <option value="company">Company</option>
                    </select>
                </div>
                <div class="applications-grid">{cards_html}</div>
            </div>
        '''
        
        # 'no_progress' tab
        if no_progress:
            cards_html = ''.join([self._create_application_card(app) for app in no_progress])
            tab_contents += f'''
                <div id="progress-no_progress" class="tab-content" style="display: none;">
                    <div class="sort-controls">
                        <h3 style="margin: 0; color: var(--text-primary); font-size: var(--font-lg); font-weight: var(--font-semibold);">No Progress Applications ({progress_counts['no_progress']})</h3>
                        <select class="sort-select" onchange="sortCards(this, 'no_progress')">
                            <option value="date-updated">Date Updated</option>
                            <option value="date-applied">Date Applied</option>
                            <option value="match-score">Match Score</option>
                            <option value="company">Company</option>
                        </select>
                    </div>
                    <div class="applications-grid">{cards_html}</div>
                </div>
            '''
        else:
            tab_contents += f'''
                <div id="progress-no_progress" class="tab-content" style="display: none;">
                    <div class="sort-controls">
                        <h3 style="margin: 0; color: var(--text-primary); font-size: var(--font-lg); font-weight: var(--font-semibold);">No Progress Applications ({progress_counts['no_progress']})</h3>
                    </div>
                    {self._create_empty_state('no progress')}
                </div>
            '''
        
        # Tabs for each progress stage
        for progress_key in progress_order:
            apps = progress_groups.get(progress_key, [])
            if apps:
                cards_html = ''.join([self._create_application_card(app) for app in apps])
                display_name = checklist_definitions[progress_key]
                count = progress_counts.get(progress_key, 0)
                tab_contents += f'''
                    <div id="progress-{progress_key}" class="tab-content" style="display: none;">
                        <div class="sort-controls">
                            <h3 style="margin: 0; color: var(--text-primary); font-size: var(--font-lg); font-weight: var(--font-semibold);">{display_name} Applications ({count})</h3>
                            <select class="sort-select" onchange="sortCards(this, '{progress_key}')">
                                <option value="date-updated">Date Updated</option>
                                <option value="date-applied">Date Applied</option>
                                <option value="match-score">Match Score</option>
                                <option value="company">Company</option>
                            </select>
                        </div>
                        <div class="applications-grid">{cards_html}</div>
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

