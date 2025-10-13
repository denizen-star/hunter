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
        # Generate application cards
        cards_html = ""
        for app in applications:
            cards_html += self._create_application_card(app)
        
        # Calculate stats
        total = len(applications)
        pending = len([a for a in applications if a.status == 'pending'])
        applied = len([a for a in applications if a.status == 'applied'])
        interviewed = len([a for a in applications if a.status == 'interviewed'])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 48px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: rgba(255,255,255,0.2);
            padding: 15px 30px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .actions {{
            text-align: center;
            margin-bottom: 30px;
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
        .applications-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
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
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.2s;
        }}
        .card-btn:hover {{
            background: #5568d3;
        }}
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            background: white;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Job Application Dashboard</h1>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Total</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{pending}</div>
                    <div class="stat-label">Pending</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{applied}</div>
                    <div class="stat-label">Applied</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{interviewed}</div>
                    <div class="stat-label">Interviewed</div>
                </div>
            </div>
        </div>
        
        <div class="actions">
            <a href="http://localhost:51002" class="btn">+ New Application</a>
        </div>
        
        {"<div class='applications-grid'>" + cards_html + "</div>" if applications else self._create_empty_state()}
    </div>
</body>
</html>"""
        return html
    
    def _create_application_card(self, app: Application) -> str:
        """Create HTML for a single application card"""
        # Generate proper URLs for summary and folder
        if app.summary_path:
            folder_name = app.folder_path.name
            summary_filename = app.summary_path.name
            summary_link = f"http://localhost:51002/applications/{folder_name}/{summary_filename}"
        else:
            summary_link = "#"
        
        match_score_html = f'<span class="match-score">{app.match_score:.0f}%</span>' if app.match_score else ''
        
        return f"""
        <div class="card">
            <div class="card-company">
                {app.company}
                {match_score_html}
            </div>
            <div class="card-title">{app.job_title}</div>
            <div>
                <span class="card-status status-{app.status}">{app.status}</span>
            </div>
            <div class="card-meta">
                📅 Applied: {format_for_display(app.created_at)}
            </div>
            <div class="card-meta">
                🔄 Updated: {format_for_display(app.status_updated_at)}
            </div>
            <div class="card-actions">
                <a href="{summary_link}" class="card-btn" target="_blank">View Summary →</a>
            </div>
        </div>
        """
    
    def _create_empty_state(self) -> str:
        """Create empty state HTML"""
        return """
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div class="empty-state-text">No applications yet. Create your first one!</div>
        </div>
        """

