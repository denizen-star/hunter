#!/usr/bin/env python3
"""
Daily Digest Generator - Standalone Script
Generates a daily digest of activities, reports, and analytics.
Can be run via cron or manually.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.activity_log_service import ActivityLogService
from app.services.analytics_generator import AnalyticsGenerator
from app.utils.file_utils import get_data_path, ensure_dir_exists, read_text_file, write_text_file, load_yaml
from jinja2 import Template


class DailyDigestGenerator:
    """Generates daily digest from activities, reports, and analytics"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize digest generator with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'digest_config.yaml'
        
        self.config = self._load_config(config_path)
        self.activity_log_service = ActivityLogService()
        self.analytics_generator = AnalyticsGenerator()
        
        # Setup output directory
        self.output_dir = get_data_path('output') / 'digests'
        ensure_dir_exists(self.output_dir)
        
        # Load template
        template_path = Path(__file__).parent / 'digest_template.md'
        if template_path.exists():
            self.template = Template(read_text_file(template_path))
        else:
            # Fallback to default template
            self.template = Template(self._get_default_template())
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from YAML file"""
        if config_path.exists():
            return load_yaml(config_path)
        else:
            # Return default config
            return {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'sender_email': '',
                    'sender_password': '',
                    'recipient_email': '',
                    'subject': 'Daily Job Hunt Digest'
                },
                'output': {
                    'include_skills_analysis': False,
                    'include_full_analytics': True
                }
            }
    
    def _get_default_template(self) -> str:
        """Default template if file doesn't exist"""
        return """# Daily Digest - {{ date }}

## Today's Activities

{% if daily_activities %}
### Summary
- **Total Activities**: {{ daily_activities|length }}
- **New Applications**: {{ new_applications_count }}
- **Status Changes**: {{ status_changes_count }}
- **Networking Contacts**: {{ networking_contacts_count }}

### Activity Details
{% for activity in daily_activities %}
- **{{ activity.timestamp }}** - {{ activity.company }} - {{ activity.position }}
  - {{ activity.activity }}
  - Status: {{ activity.status }}
{% endfor %}
{% else %}
No activities recorded today.
{% endif %}

## Key Metrics (Last 30 Days)

### Application Analytics
- **Total Applications**: {{ metrics.total_applications }}
- **Response Rate**: {{ "%.1f"|format(metrics.response_rate) }}%
- **Interview Conversion**: {{ "%.1f"|format(metrics.interview_rate) }}%

### Pipeline Status
- **Applied**: {{ pipeline.applied }}
- **Responded**: {{ pipeline.responded }} ({{ "%.1f"|format(pipeline.response_rate) }}%)
- **Phone Screens**: {{ pipeline.phone_screen }} ({{ "%.1f"|format(pipeline.phone_screen_rate) }}%)
- **Interviews**: {{ pipeline.interview }} ({{ "%.1f"|format(pipeline.interview_rate) }}%)
- **Offers**: {{ pipeline.offer }} ({{ "%.1f"|format(pipeline.offer_rate) }}%)

## Reports Snapshot

### Status Distribution
{% for status, count in status_distribution.items() %}
- **{{ status }}**: {{ count }}
{% endfor %}

## Best Performing Days

{% for day, stats in best_days.items() %}
- **{{ day }}**: {{ stats.total_applications }} applications, {{ "%.1f"|format(stats.response_rate) }}% response rate
{% endfor %}

---
*Generated on {{ generated_at }}*
"""
    
    def generate_digest(self, date: Optional[datetime] = None) -> Path:
        """Generate digest for specified date (defaults to today)"""
        if date is None:
            date = datetime.now(timezone(timedelta(hours=-5)))  # EST
        
        try:
            # Get daily activities
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            daily_summary = self.activity_log_service.get_daily_activities_summary(
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not load daily activities: {e}")
            daily_summary = {}
        
        # Format activities for template
        date_str = date.strftime('%Y-%m-%d')
        daily_activities = daily_summary.get(date_str, [])
        
        # Count activity types
        new_applications_count = sum(
            1 for a in daily_activities 
            if 'created' in a.get('activity', '').lower()
        )
        status_changes_count = sum(
            1 for a in daily_activities 
            if 'status changed' in a.get('activity', '').lower()
        )
        networking_contacts_count = sum(
            1 for a in daily_activities 
            if a.get('type') == 'networking'
        )
        
        # Get analytics for last 30 days
        try:
            analytics = self.analytics_generator.generate_analytics(period='30days')
            app_analytics = analytics.get('application_analytics', {})
        except Exception as e:
            print(f"⚠️ Warning: Could not load analytics: {e}")
            analytics = {'total_applications': 0, 'application_analytics': {}}
            app_analytics = {}
        
        # Get reports data
        try:
            reports_data = self.activity_log_service.get_reports_data(
                period='30days',
                report_type='both'
            )
        except Exception as e:
            print(f"⚠️ Warning: Could not load reports data: {e}")
            reports_data = {'applications_by_status': {}}
        
        # Get status changes for today (from/to analysis)
        status_changes_today = self._get_status_changes_for_date(date)
        
        # Prepare template context with safe defaults
        pipeline_data = app_analytics.get('interview_conversion', {})
        context = {
            'date': date.strftime('%B %d, %Y'),
            'date_iso': date_str,
            'daily_activities': daily_activities or [],
            'new_applications_count': new_applications_count,
            'status_changes_count': status_changes_count,
            'networking_contacts_count': networking_contacts_count,
            'status_changes': status_changes_today,
            'metrics': {
                'total_applications': analytics.get('total_applications', 0),
                'response_rate': app_analytics.get('response_rate', 0.0),
                'interview_rate': pipeline_data.get('interview_rate', 0.0)
            },
            'pipeline': {
                'applied': pipeline_data.get('applied', 0),
                'responded': pipeline_data.get('responded', 0),
                'phone_screen': pipeline_data.get('phone_screen', 0),
                'interview': pipeline_data.get('interview', 0),
                'offer': pipeline_data.get('offer', 0),
                'response_rate': pipeline_data.get('response_rate', 0.0),
                'phone_screen_rate': pipeline_data.get('phone_screen_rate', 0.0),
                'interview_rate': pipeline_data.get('interview_rate', 0.0),
                'offer_rate': pipeline_data.get('offer_rate', 0.0)
            },
            'status_distribution': reports_data.get('applications_by_status', {}) or {},
            'best_days': app_analytics.get('best_performing_day', {}) or {},
            'generated_at': datetime.now(timezone(timedelta(hours=-5))).strftime('%Y-%m-%d %H:%M:%S EST')
        }
        
        # Add optional sections if enabled
        if self.config.get('output', {}).get('include_skills_analysis', False):
            skills_analysis = analytics.get('skills_gap_analysis', {})
            context['skills_analysis'] = {
                'most_requested': skills_analysis.get('most_requested_skills', [])[:10],
                'skill_gaps': skills_analysis.get('skill_gaps', [])[:10]
            }
        
        # Render template
        digest_content = self.template.render(**context)
        
        # Save to file
        filename = f"{date_str}-digest.md"
        output_path = self.output_dir / filename
        write_text_file(digest_content, output_path)
        
        print(f"✅ Digest generated: {output_path}")
        
        return output_path
    
    def send_email(self, digest_path: Path) -> bool:
        """Send digest via email"""
        email_config = self.config.get('email', {})
        
        if not email_config.get('enabled', False):
            return False
        
        try:
            # Read digest content
            digest_content = read_text_file(digest_path)
            
            # Convert markdown to HTML (simple conversion)
            html_content = self._markdown_to_html(digest_content)
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = email_config.get('subject', 'Daily Job Hunt Digest')
            
            # Add HTML body
            msg.attach(MIMEText(html_content, 'html'))
            
            # Attach markdown file
            with open(digest_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {digest_path.name}'
                )
                msg.attach(part)
            
            # Send email
            smtp_port = email_config.get('smtp_port', 587)
            
            # Use SSL for port 465, TLS for port 587
            if smtp_port == 465:
                server = smtplib.SMTP_SSL(email_config['smtp_server'], smtp_port)
            else:
                server = smtplib.SMTP(email_config['smtp_server'], smtp_port)
                server.starttls()
            
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent to {email_config['recipient_email']}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def _get_status_changes_for_date(self, date: datetime) -> Dict:
        """Get status changes for a specific date with from/to analysis"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        try:
            activities = self.activity_log_service.get_activities(
                start_date=start_date,
                end_date=end_date
            )
            
            # Filter only status change activities
            status_changes = [
                a for a in activities 
                if a.get('type') in ['job_application_status_changed', 'networking_status_changed']
            ]
            
            # Count by from/to status
            from_to_counts = {}
            to_counts = {}
            from_counts = {}
            
            for change in status_changes:
                old_status = change.get('old_status', 'Unknown')
                new_status = change.get('new_status', 'Unknown')
                
                # Normalize networking statuses
                if change.get('type') == 'networking_status_changed':
                    new_status = self.activity_log_service._normalize_networking_status(new_status)
                    old_status = self.activity_log_service._normalize_networking_status(old_status)
                
                # Create from/to key
                from_to_key = f"{old_status} → {new_status}"
                from_to_counts[from_to_key] = from_to_counts.get(from_to_key, 0) + 1
                
                # Count by "to" status
                to_counts[new_status] = to_counts.get(new_status, 0) + 1
                
                # Count by "from" status
                from_counts[old_status] = from_counts.get(old_status, 0) + 1
            
            # Sort by count (descending)
            from_to_sorted = sorted(
                from_to_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return {
                'total_changes': len(status_changes),
                'from_to_changes': dict(from_to_sorted[:10])  # Top 10 transitions
            }
            
        except Exception as e:
            print(f"⚠️ Warning: Could not analyze status changes: {e}")
            return {
                'total_changes': 0,
                'from_to_changes': {}
            }
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """Simple markdown to HTML conversion"""
        import re
        
        html = markdown_text
        
        # Headers (process in reverse order to avoid conflicts)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold - handle pairs of **
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Lists - wrap consecutive list items in <ul>
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                # Remove the '- ' and wrap content
                content = line.strip()[2:]
                result_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                if line.strip():
                    result_lines.append(f'<p>{line}</p>')
                else:
                    result_lines.append('<br>')
        
        if in_list:
            result_lines.append('</ul>')
        
        html = '\n'.join(result_lines)
        
        # Horizontal rules
        html = html.replace('---', '<hr>')
        
        # Wrap in HTML structure
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        h3 {{ color: #777; margin-top: 20px; }}
        ul {{ margin: 10px 0; padding-left: 25px; }}
        li {{ margin: 5px 0; }}
        p {{ margin: 10px 0; }}
        hr {{ margin: 20px 0; border: none; border-top: 1px solid #ddd; }}
        strong {{ color: #333; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
        
        return html


def main():
    """Main entry point for script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate daily job hunt digest')
    parser.add_argument(
        '--date',
        type=str,
        help='Date in YYYY-MM-DD format (defaults to today)',
        default=None
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Skip email sending even if configured'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file (defaults to config/digest_config.yaml)',
        default=None
    )
    
    args = parser.parse_args()
    
    # Parse date if provided
    date = None
    if args.date:
        try:
            date = datetime.strptime(args.date, '%Y-%m-%d')
            date = date.replace(tzinfo=timezone(timedelta(hours=-5)))
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD")
            return 1
    
    # Initialize generator
    config_path = Path(args.config) if args.config else None
    generator = DailyDigestGenerator(config_path)
    
    # Generate digest
    digest_path = generator.generate_digest(date)
    
    # Send email if configured and not disabled
    if not args.no_email:
        generator.send_email(digest_path)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

