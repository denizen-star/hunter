#!/usr/bin/env python3
"""
Daily Digest Generator - Standalone Script
Generates a daily digest of activities, reports, and analytics.
Can be run via cron or manually.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
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
    
    def generate_digest(self, date: Optional[datetime] = None) -> Tuple[str, Path]:
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
        
        # Return content and path (but don't save yet)
        filename = f"{date_str}-digest.md"
        output_path = self.output_dir / filename
        
        return digest_content, output_path
    
    def send_email(self, digest_content: str, digest_path: Optional[Path] = None) -> bool:
        """Send digest via email
        
        Args:
            digest_content: The markdown content of the digest
            digest_path: Optional path to digest file (used for attachment if email fails)
        """
        email_config = self.config.get('email', {})
        
        if not email_config.get('enabled', False):
            return False
        
        try:
            # Convert markdown to HTML (simple conversion)
            html_content = self._markdown_to_html(digest_content)
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = email_config['recipient_email']
            msg['Subject'] = email_config.get('subject', 'Daily Job Hunt Digest')
            
            # Add HTML body
            msg.attach(MIMEText(html_content, 'html'))
            
            # Attach markdown file if path is provided
            if digest_path and digest_path.exists():
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
    
    def _get_status_colors(self, status: str) -> tuple:
        """Get background and text colors for a status from STATUS_COLORS.md
        
        Handles both normalized formats (with hyphens) and original formats (with spaces).
        """
        if not status:
            return ('#f3f4f6', '#6b7280')  # Default gray
        
        # Normalize status: replace hyphens with spaces and convert to lowercase
        status_normalized = status.lower().strip().replace('-', ' ').replace('_', ' ')
        
        # Application status colors
        app_colors = {
            'pending': ('#fef3c7', '#92400e'),
            'applied': ('#dbeafe', '#1e40af'),
            'contacted someone': ('#f3f4f6', '#6b7280'),
            'contacted hiring manager': ('#fee2e2', '#991b1b'),
            'company response': ('#eff6ff', '#1e40af'),
            'scheduled interview': ('#fef3c7', '#92400e'),
            'interviewed': ('#d1fae5', '#065f46'),
            'interview notes': ('#d1fae5', '#065f46'),
            'interview follow up': ('#fce7f3', '#9f1239'),
            'offered': ('#d1fae5', '#065f46'),
            'rejected': ('#fee2e2', '#991b1b'),
            'accepted': ('#d1fae5', '#065f46'),
        }
        
        # Networking status colors
        networking_colors = {
            'found contact': ('#dbeafe', '#1e40af'),
            'to research': ('#dbeafe', '#1e40af'),
            'sent linkedin connection': ('#fef3c7', '#92400e'),
            'ready to connect': ('#fef3c7', '#92400e'),
            'sent email': ('#eff6ff', '#1e40af'),
            'pending reply': ('#eff6ff', '#1e40af'),
            'connection accepted': ('#d1fae5', '#065f46'),
            'connected initial': ('#d1fae5', '#065f46'),  # Handles "connected - initial" and "connected-initial"
            'in conversation': ('#d1fae5', '#065f46'),
            'meeting scheduled': ('#fef3c7', '#92400e'),
            'meeting complete': ('#d1fae5', '#065f46'),
            'strong connection': ('#d1fae5', '#065f46'),
            'referral partner': ('#d1fae5', '#065f46'),
            'cold inactive': ('#f3f4f6', '#6b7280'),  # Handles "cold/inactive" and "cold-inactive"
            'dormant': ('#f3f4f6', '#6b7280'),
            'inactive dormant': ('#f3f4f6', '#6b7280'),  # Handles "inactive/dormant"
        }
        
        # Check exact match first (normalized)
        all_colors = {**app_colors, **networking_colors}
        if status_normalized in all_colors:
            return all_colors[status_normalized]
        
        # Try partial matches (case-insensitive, normalized)
        for key, colors in all_colors.items():
            # Normalize key for comparison
            key_normalized = key.replace('-', ' ').replace('_', ' ')
            if key_normalized in status_normalized or status_normalized in key_normalized:
                return colors
        
        # Default gray for unmapped statuses
        return ('#f3f4f6', '#6b7280')
    
    def _get_status_type(self, status: str) -> str:
        """Determine if a status is for an application or contact.
        
        Returns 'app' for application statuses, 'contact' for contact statuses.
        """
        if not status:
            return 'app'  # Default to app
        
        # Normalize status: replace hyphens with spaces and convert to lowercase
        status_normalized = status.lower().strip().replace('-', ' ').replace('_', ' ')
        
        # Application statuses
        app_statuses = [
            'pending', 'applied', 'contacted someone', 'contacted hiring manager',
            'company response', 'scheduled interview', 'interviewed', 'interview notes',
            'interview follow up', 'offered', 'rejected', 'accepted'
        ]
        
        # Contact/Networking statuses
        contact_statuses = [
            'found contact', 'to research', 'sent linkedin connection', 'ready to connect',
            'sent email', 'pending reply', 'connection accepted', 'connected initial',
            'in conversation', 'meeting scheduled', 'meeting complete', 'strong connection',
            'referral partner', 'cold inactive', 'dormant', 'inactive dormant'
        ]
        
        # Check exact match first (normalized)
        if status_normalized in [s.replace('-', ' ').replace('_', ' ') for s in app_statuses]:
            return 'app'
        if status_normalized in [s.replace('-', ' ').replace('_', ' ') for s in contact_statuses]:
            return 'contact'
        
        # Try partial matches
        for app_status in app_statuses:
            app_status_normalized = app_status.replace('-', ' ').replace('_', ' ')
            if app_status_normalized in status_normalized or status_normalized in app_status_normalized:
                return 'app'
        
        for contact_status in contact_statuses:
            contact_status_normalized = contact_status.replace('-', ' ').replace('_', ' ')
            if contact_status_normalized in status_normalized or status_normalized in contact_status_normalized:
                return 'contact'
        
        # Default to app if unsure
        return 'app'
    
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
            
            # Sort by "to" status (alphabetically), then by count (descending) for same "to" status
            def sort_key(item):
                transition = item[0]  # e.g., "pending → applied"
                count = item[1]
                # Extract "to" status (part after "→")
                if '→' in transition:
                    to_status = transition.split('→')[1].strip()
                elif '->' in transition:
                    to_status = transition.split('->')[1].strip()
                else:
                    to_status = transition
                return (to_status.lower(), -count)  # Sort by "to" status, then by count descending
            
            from_to_sorted = sorted(
                from_to_counts.items(), 
                key=sort_key
            )
            
            return {
                'total_changes': len(status_changes),
                'from_to_changes': dict(from_to_sorted)  # All transitions sorted by "to" status
            }
            
        except Exception as e:
            print(f"⚠️ Warning: Could not analyze status changes: {e}")
            return {
                'total_changes': 0,
                'from_to_changes': {}
            }
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """Simple markdown to HTML conversion with timeline support"""
        import re
        
        html = markdown_text
        
        # Process status-list-container (no vertical line, bullet-style markers)
        # Pattern matches status items with data-status or data-transition, optionally with data-status-raw
        status_item_pattern = r'<div class="status-item"([^>]*)>\s*<div class="status-marker"></div>\s*<div class="status-content">((?:.|\n)*?)</div>\s*</div>'
        
        def replace_status_item(match):
            # Extract attributes from the div tag
            attrs_str = match.group(1)
            content_text = match.group(2).strip()
            
            # Extract data-status, data-transition, and data-status-raw from attributes
            status_from_attr = None
            status_raw = None
            is_transition = False
            
            # Look for data-status
            status_match = re.search(r'data-status="([^"]*)"', attrs_str)
            if status_match:
                status_from_attr = status_match.group(1)
            
            # Look for data-transition
            transition_match = re.search(r'data-transition="([^"]*)"', attrs_str)
            if transition_match:
                status_from_attr = transition_match.group(1)
                is_transition = True
            
            # Look for data-status-raw
            raw_match = re.search(r'data-status-raw="([^"]*)"', attrs_str)
            if raw_match:
                status_raw = raw_match.group(1)
            
            # If it's a transition (contains "→"), extract the "to" status for coloring
            status_for_color = status_from_attr
            if status_from_attr and ('→' in status_from_attr or '->' in status_from_attr):
                if '→' in status_from_attr:
                    parts = status_from_attr.split('→')
                else:
                    parts = status_from_attr.split('->')
                if len(parts) > 1:
                    status_for_color = parts[-1].strip()  # Get the "to" status
            
            bg_color, text_color = self._get_status_colors(status_for_color)
            
            # Determine status type and add icon (only for Status Distribution, not transitions)
            icon = ''
            if status_raw and not is_transition:  # Only add icon if we have raw status and it's not a transition
                status_type = self._get_status_type(status_raw)
                if status_type == 'app':
                    icon = '💼 '
                elif status_type == 'contact':
                    icon = '🤝 '
            
            # No bullet marker - just the colored content with icon
            return f'<div class="status-item" style="position: relative; margin-bottom: 6px; padding-left: 0px; margin-left: 0px;">' + \
                   f'<div class="status-content" style="background-color: {bg_color}; color: {text_color}; padding: 6px 10px; border-radius: 6px; margin-left: 0px; font-size: 14px; line-height: 1.5; display: inline-block;">{icon}{content_text}</div>' + \
                   '</div>'
        
        # Process status items without data-status (no styling)
        status_item_no_status_pattern = r'<div class="status-item"[^>]*>\s*<div class="status-content">((?:.|\n)*?)</div>\s*</div>'
        def replace_status_item_no_status(match):
            content_text = match.group(1).strip()
            return f'<div class="status-item" style="margin-bottom: 6px; padding-left: 0px;">' + \
                   f'<div class="status-content" style="padding: 6px 10px; font-size: 14px; line-height: 1.5; display: inline-block;">{content_text}</div>' + \
                   '</div>'
        
        html = re.sub(status_item_pattern, replace_status_item, html, flags=re.DOTALL)
        html = re.sub(status_item_no_status_pattern, replace_status_item_no_status, html, flags=re.DOTALL)
        
        # Process status-list-container (simple container, no vertical line)
        # For status transitions, remove padding-left to eliminate indentation
        html = re.sub(
            r'<div class="status-list-container">',
            '<div class="status-list-container" style="margin: 15px 0; padding-left: 0; margin-left: 0;">',
            html
        )
        
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
            # Skip already processed HTML (timeline, status items)
            if 'timeline' in line.lower() or 'status-item' in line.lower() or 'status-list-container' in line.lower():
                result_lines.append(line)
                continue
            
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
                if line.strip() and not line.strip().startswith('<'):
                    result_lines.append(f'<p>{line}</p>')
                elif not line.strip() and not line.strip().startswith('<'):
                    result_lines.append('<br>')
                else:
                    result_lines.append(line)
        
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #333; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 14pt; }}
        h2 {{ color: #555; margin-top: 5px; border-bottom: 1px solid #ddd; padding-bottom: 5px; font-size: 12pt; }}
        h3 {{ color: #777; margin-top: 5px; font-size: 12pt; }}
        ul {{ margin: 10px 0; padding-left: 25px; }}
        li {{ margin: 5px 0; font-size: 10pt; }}
        p {{ margin: 10px 0; font-size: 10pt; }}
        hr {{ margin: 5px 0; border: none; border-top: 1px solid #ddd; }}
        strong {{ color: #333; }}
        .timeline-container {{ position: relative; padding-left: 0; margin: 15px 0; }}
        .status-list-container {{ margin: 15px 0; padding-left: 0; margin-left: 0; }}
        .status-item {{ position: relative; margin-bottom: 6px; padding-left: 0px; margin-left: 0px; }}
        .status-marker {{ display: none; width: 0; height: 0; padding: 0; margin: 0; }}
        .status-content {{ padding: 6px 10px; border-radius: 6px; margin-left: 0px; font-size: 14px; line-height: 1.5; display: inline-block; }}
        .timeline-time {{ font-weight: 600; }}
        .timeline-company {{ font-weight: 600; }}
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
    
    # Generate digest content (don't save yet)
    digest_content, digest_path = generator.generate_digest(date)
    
    # Send email if configured and not disabled
    email_sent = False
    if not args.no_email:
        email_sent = generator.send_email(digest_content)
    
    # Only save .md file if email failed to send (or email is disabled)
    if not email_sent:
        write_text_file(digest_content, digest_path)
        print(f"✅ Digest saved to file: {digest_path}")
    else:
        print(f"✅ Email sent successfully - digest file not saved")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

