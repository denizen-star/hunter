"""Activity log service for tracking all job application and networking activities"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from app.utils.file_utils import get_data_path, ensure_dir_exists, read_text_file, write_text_file


class ActivityLogService:
    """Maintains a single JSON log file of all activities for fast reporting"""
    
    def __init__(self):
        self.log_dir = get_data_path('output')
        ensure_dir_exists(self.log_dir)
        self.log_file = self.log_dir / 'activity_log.json'
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure log file exists with proper structure"""
        if not self.log_file.exists():
            initial_data = {
                'version': '1.0',
                'created_at': datetime.now(timezone(timedelta(hours=-4))).isoformat(),
                'activities': []
            }
            write_text_file(json.dumps(initial_data, indent=2), self.log_file)
    
    def _load_log(self) -> Dict:
        """Load the activity log from disk"""
        try:
            content = read_text_file(self.log_file)
            return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            # If corrupted, create a new one
            self._ensure_log_file()
            content = read_text_file(self.log_file)
            return json.loads(content)
    
    def _save_log(self, data: Dict):
        """Save the activity log to disk"""
        write_text_file(json.dumps(data, indent=2), self.log_file)
    
    def log_application_created(
        self,
        application_id: str,
        company: str,
        job_title: str,
        created_at: datetime,
        match_score: Optional[float] = None,
        status: str = 'pending'
    ):
        """Log when a job application is created"""
        activity = {
            'id': f"{application_id}_{created_at.strftime('%Y%m%d%H%M%S')}",
            'type': 'job_application_created',
            'application_id': application_id,
            'company': company,
            'job_title': job_title,
            'status': status,
            'match_score': match_score,
            'timestamp': created_at.isoformat(),
            'date': created_at.date().isoformat()
        }
        self._add_activity(activity)
    
    def log_application_status_changed(
        self,
        application_id: str,
        company: str,
        job_title: str,
        old_status: str,
        new_status: str,
        updated_at: datetime,
        notes: Optional[str] = None
    ):
        """Log when an application status changes"""
        activity = {
            'id': f"{application_id}_status_{updated_at.strftime('%Y%m%d%H%M%S')}",
            'type': 'job_application_status_changed',
            'application_id': application_id,
            'company': company,
            'job_title': job_title,
            'old_status': old_status,
            'new_status': new_status,
            'notes': notes,
            'timestamp': updated_at.isoformat(),
            'date': updated_at.date().isoformat()
        }
        self._add_activity(activity)
    
    def log_networking_contact_created(
        self,
        contact_id: str,
        person_name: str,
        company_name: str,
        job_title: Optional[str],
        created_at: datetime,
        status: str = 'New',
        match_score: Optional[float] = None
    ):
        """Log when a networking contact is created"""
        activity = {
            'id': f"{contact_id}_{created_at.strftime('%Y%m%d%H%M%S')}",
            'type': 'networking_contact_created',
            'contact_id': contact_id,
            'person_name': person_name,
            'company_name': company_name,
            'job_title': job_title,
            'status': status,
            'match_score': match_score,
            'timestamp': created_at.isoformat(),
            'date': created_at.date().isoformat()
        }
        self._add_activity(activity)
    
    def log_networking_status_changed(
        self,
        contact_id: str,
        person_name: str,
        company_name: str,
        old_status: str,
        new_status: str,
        updated_at: datetime,
        notes: Optional[str] = None
    ):
        """Log when a networking contact status changes"""
        activity = {
            'id': f"{contact_id}_status_{updated_at.strftime('%Y%m%d%H%M%S')}",
            'type': 'networking_status_changed',
            'contact_id': contact_id,
            'person_name': person_name,
            'company_name': company_name,
            'old_status': old_status,
            'new_status': new_status,
            'notes': notes,
            'timestamp': updated_at.isoformat(),
            'date': updated_at.date().isoformat()
        }
        self._add_activity(activity)
    
    def _add_activity(self, activity: Dict):
        """Add an activity to the log (thread-safe append)"""
        data = self._load_log()
        data['activities'].append(activity)
        # Keep only last 10,000 activities to prevent file from growing too large
        if len(data['activities']) > 10000:
            data['activities'] = data['activities'][-10000:]
        data['last_updated'] = datetime.now(timezone(timedelta(hours=-4))).isoformat()
        self._save_log(data)
    
    def get_activities(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        activity_type: Optional[str] = None,
        application_id: Optional[str] = None,
        contact_id: Optional[str] = None
    ) -> List[Dict]:
        """Get activities filtered by criteria"""
        data = self._load_log()
        activities = data.get('activities', [])
        
        # Filter by date range
        if start_date or end_date:
            filtered = []
            for activity in activities:
                activity_dt = datetime.fromisoformat(activity['timestamp'])
                if start_date and activity_dt < start_date:
                    continue
                if end_date and activity_dt > end_date:
                    continue
                filtered.append(activity)
            activities = filtered
        
        # Filter by type
        if activity_type:
            activities = [a for a in activities if a.get('type') == activity_type]
        
        # Filter by application_id
        if application_id:
            activities = [a for a in activities if a.get('application_id') == application_id]
        
        # Filter by contact_id
        if contact_id:
            activities = [a for a in activities if a.get('contact_id') == contact_id]
        
        return activities
    
    def get_daily_activities_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get daily activities grouped by date for fast reporting"""
        activities = self.get_activities(start_date=start_date, end_date=end_date)
        
        # Group by date
        daily_summary = {}
        for activity in activities:
            date_str = activity['date']
            if date_str not in daily_summary:
                daily_summary[date_str] = []
            
            # Format for frontend
            activity_dt = datetime.fromisoformat(activity['timestamp'])
            old_status = activity.get('old_status', '')
            new_status = activity.get('new_status') or activity.get('status', '')
            
            # Normalize networking statuses if needed
            if activity.get('type', '').startswith('networking'):
                if old_status:
                    old_status = self._normalize_networking_status(old_status)
                if new_status:
                    new_status = self._normalize_networking_status(new_status)
            
            # Format status display: "old_status → new_status" or just "new_status"
            if old_status and new_status and old_status != new_status:
                status_display = f"{old_status} → {new_status}"
            else:
                status_display = new_status
            
            formatted_activity = {
                'company': activity.get('company') or activity.get('company_name', ''),
                'position': activity.get('job_title', ''),
                'timestamp': activity_dt.strftime('%I:%M %p EST'),
                'activity': self._format_activity_description(activity),
                'status': new_status,  # Keep original status for filtering/coloring
                'status_display': status_display,  # Formatted display string
                'old_status': old_status,  # Store old_status separately
                'application_id': activity.get('application_id') or activity.get('contact_id', ''),
                'type': 'job' if 'application' in activity.get('type', '') else 'networking',
                '_sort_key': activity_dt  # Store datetime for sorting
            }
            daily_summary[date_str].append(formatted_activity)
        
        # Sort activities within each day by timestamp (newest first)
        for date_str in daily_summary:
            daily_summary[date_str].sort(key=lambda x: x['_sort_key'], reverse=True)
            # Remove sort key from final output
            for activity in daily_summary[date_str]:
                del activity['_sort_key']
        
        return daily_summary
    
    def _normalize_networking_status(self, status: str) -> str:
        """Remove person names from networking status strings"""
        if not status:
            return status
        
        # Common networking status patterns that might include names
        # Pattern: "Name-Status" or "Name---Status" or "Name-status"
        # We want to extract just the status part
        
        # Split by common separators and take the last meaningful part
        parts = status.replace('---', '-').replace('--', '-').split('-')
        
        # Common status keywords to identify the actual status
        status_keywords = [
            'contacted', 'sent', 'research', 'conversation', 'pending', 'inactive',
            'dormant', 'ready', 'new', 'connection', 'archive', 'cold'
        ]
        
        # Find the part that looks like a status (contains status keywords)
        for part in reversed(parts):
            part_lower = part.lower()
            if any(keyword in part_lower for keyword in status_keywords):
                # This looks like a status, return it
                return part.replace('-', ' ').strip()
        
        # If no status keyword found, return the last part (likely the status)
        if len(parts) > 1:
            return parts[-1].replace('-', ' ').strip()
        
        return status
    
    def _format_activity_description(self, activity: Dict) -> str:
        """Format activity description for display"""
        activity_type = activity.get('type', '')
        
        if activity_type == 'job_application_created':
            return 'Application Created'
        elif activity_type == 'job_application_status_changed':
            return f'Status Changed to {activity.get("new_status", "")}'
        elif activity_type == 'networking_contact_created':
            return 'Networking Contact Created'
        elif activity_type == 'networking_status_changed':
            status = activity.get("new_status", "")
            normalized_status = self._normalize_networking_status(status)
            return f'Status Changed to {normalized_status}'
        else:
            return 'Activity'
    
    def get_reports_data(
        self,
        period: str,
        report_type: str = 'jobs'  # 'jobs', 'networking', 'both'
    ) -> Dict:
        """Get pre-computed reports data from activity log"""
        from datetime import datetime, timedelta, timezone
        
        now = datetime.now(timezone(timedelta(hours=-4)))
        
        # Calculate date range
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
        
        # Get activities for period
        activities = self.get_activities(start_date=start_date, end_date=end_date)
        
        # Filter by type
        if report_type == 'jobs':
            activities = [a for a in activities if 'application' in a.get('type', '')]
        elif report_type == 'networking':
            activities = [a for a in activities if 'networking' in a.get('type', '')]
        # 'both' includes all activities
        
        # Process activities for reports
        applications_by_status = {}
        status_changes_by_status = {}
        daily_counts = {}
        
        for activity in activities:
            activity_type = activity.get('type', '')
            activity_date = activity['date']
            
            if activity_type in ['job_application_created', 'networking_contact_created']:
                status = activity.get('status', '')
                if status:
                    applications_by_status[status] = applications_by_status.get(status, 0) + 1
                
                # Count daily
                if activity_date not in daily_counts:
                    daily_counts[activity_date] = {}
                daily_counts[activity_date][status] = daily_counts[activity_date].get(status, 0) + 1
            
            elif activity_type in ['job_application_status_changed', 'networking_status_changed']:
                new_status = activity.get('new_status', '')
                if new_status:
                    # Normalize networking statuses to remove person names
                    if activity_type == 'networking_status_changed':
                        new_status = self._normalize_networking_status(new_status)
                    status_changes_by_status[new_status] = status_changes_by_status.get(new_status, 0) + 1
                
                # Count daily
                if activity_date not in daily_counts:
                    daily_counts[activity_date] = {}
                # Apply same normalization for daily counts
                if activity_type == 'networking_status_changed':
                    original_status = activity.get('new_status', '')
                    new_status = self._normalize_networking_status(original_status)
                daily_counts[activity_date][new_status] = daily_counts[activity_date].get(new_status, 0) + 1
        
        return {
            'applications_by_status': applications_by_status,
            'status_changes_by_status': status_changes_by_status,
            'daily_counts': daily_counts,
            'total_activities': len(activities)
        }

