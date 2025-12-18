"""Badge calculation service for networking rewards system"""
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from app.utils.file_utils import get_data_path, ensure_dir_exists
from app.services.networking_processor import NetworkingProcessor
from app.models.networking_contact import NetworkingContact


class BadgeCalculationService:
    """Service for calculating and managing networking badges and points"""
    
    def __init__(self):
        self.rewards_file = get_data_path('output') / 'networking_rewards.json'
        self.networking_processor = NetworkingProcessor()
        
        # Badge definitions - each contact gets ONE badge based on their current status
        # Status to badge mapping:
        # 1. Found Contact → None
        # 2. Sent LinkedIn Connection → Deep Diver (+10)
        # 3. Sent Email → Profile Magnet (+3)
        # 4. Connection Accepted → Qualified Lead (+15)
        # 5. Cold/Inactive → None
        # 6. In Conversation → Conversation Starter (+20)
        # 7. Meeting Scheduled → Scheduler Master (+30)
        # 8. Meeting Complete → Rapport Builder (+50)
        # 9. Strong Connection → Relationship Manager (+2) - Recurring
        # 10. Referral Partner → Super Connector (+100)
        # 11. Dormant → None
        self.badge_definitions = {
            'deep_diver': {
                'name': 'Deep Diver',
                'points': 10,
                'trigger_status': 'Sent LinkedIn Connection',
                'phase': 'prospecting',
                'description': 'Contact reached "Sent LinkedIn Connection" status',
                'badges_tracking': 'Deep Research Complete (Steps 1.1-1.3). Specific personalization hook is defined.',
                'requires_count': 1
            },
            'profile_magnet': {
                'name': 'Profile Magnet',
                'points': 3,
                'trigger_status': 'Sent Email',
                'phase': 'outreach',
                'description': 'Contact reached "Sent Email" status',
                'badges_tracking': 'Personalized LinkedIn Message Sent (Step 2.1). Awaiting connection acceptance or response.',
                'requires_count': 1
            },
            'qualified_lead': {
                'name': 'Qualified Lead',
                'points': 15,
                'trigger_status': 'Connection Accepted',
                'phase': 'outreach',
                'description': 'Contact reached "Connection Accepted" status',
                'badges_tracking': 'Contact Viewed Profile (2.3) OR Connection Accepted (2.4) OR Email Reply Received (3.4). Any positive sign of engagement.',
                'requires_count': 1
            },
            'conversation_starter': {
                'name': 'Conversation Starter',
                'points': 20,
                'trigger_status': 'In Conversation',
                'phase': 'engagement',
                'description': 'Contact reached "In Conversation" status',
                'badges_tracking': 'Value-Driven Email Sent (3.3) and Contact is Actively Responding. You are exchanging messages to set a meeting.',
                'requires_count': 1
            },
            'scheduler_master': {
                'name': 'Scheduler Master',
                'points': 30,
                'trigger_status': 'Meeting Scheduled',
                'phase': 'engagement',
                'description': 'Contact reached "Meeting Scheduled" status',
                'badges_tracking': 'Call/Meeting Confirmed on Calendar (Step 8). A specific date/time is set.',
                'requires_count': 1
            },
            'rapport_builder': {
                'name': 'Rapport Builder',
                'points': 50,
                'trigger_status': 'Meeting Complete',
                'phase': 'engagement',
                'description': 'Contact reached "Meeting Complete" status',
                'badges_tracking': 'Meeting Occurred and Debrief is Done (Step 9). Informational interview or call is complete.',
                'requires_count': 1
            },
            'relationship_manager': {
                'name': 'Relationship Manager',
                'points': 2,
                'trigger_status': 'Strong Connection',
                'phase': 'nurture',
                'description': 'Contact reached "Strong Connection" status',
                'badges_tracking': 'Next Check-in Scheduled (Step 4.1) or Maintenance Check-in Sent (Step 4.2). Relationship is established and active.',
                'requires_count': 1,
                'recurring': True
            },
            'super_connector': {
                'name': 'Super Connector',
                'points': 100,
                'trigger_status': 'Referral Partner',
                'phase': 'nurture',
                'description': 'Contact reached "Referral Partner" status',
                'badges_tracking': 'Contact Provides Referral/Opportunity OR Explicitly Offers Advocacy. Confirmed as a high-value relationship.',
                'requires_count': 1
            }
        }
        
        # Status to badge mapping (for quick lookup)
        # Includes both new and old status names for backward compatibility
        self.status_to_badge = {
            # New status names
            'Found Contact': None,
            'Sent LinkedIn Connection': 'deep_diver',
            'Sent Email': 'profile_magnet',
            'Connection Accepted': 'qualified_lead',
            # Old status names (backward compatibility)
            'To Research': None,
            'Ready to Connect': 'deep_diver',
            'Pending Reply': 'profile_magnet',
            'Connected - Initial': 'qualified_lead',
            'Cold/Inactive': None,
            'In Conversation': 'conversation_starter',
            'Meeting Scheduled': 'scheduler_master',
            'Meeting Complete': 'rapport_builder',
            'Strong Connection': 'relationship_manager',
            'Referral Partner': 'super_connector',
            'Dormant': None
        }
    
    def load_rewards_data(self) -> Dict:
        """Load rewards data from JSON file"""
        if not self.rewards_file.exists():
            return self._initialize_rewards_data()
        
        try:
            with open(self.rewards_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure all badges are defined
                return self._ensure_badge_structure(data)
        except Exception as e:
            print(f"Error loading rewards data: {e}")
            return self._initialize_rewards_data()
    
    def save_rewards_data(self, data: Dict) -> None:
        """Save rewards data to JSON file"""
        ensure_dir_exists(self.rewards_file.parent)
        with open(self.rewards_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_rewards_data(self) -> Dict:
        """Initialize empty rewards data structure"""
        badges = {}
        for badge_id, badge_def in self.badge_definitions.items():
            badges[badge_id] = {
                'earned': False,
                'points': badge_def['points'],
                'count': 0,
                'required': badge_def.get('requires_count', 1),
                'last_earned': None
            }
            if 'time_window' in badge_def:
                badges[badge_id]['time_window'] = badge_def['time_window']
        
        return {
            'version': '1.0',
            'last_calculated': datetime.now().isoformat(),
            'total_points': 0,
            'badges': badges,
            'points_by_category': {
                'prospecting': 0,
                'outreach': 0,
                'engagement': 0,
                'nurture': 0
            },
            'application_badges': {}
        }
    
    def _ensure_badge_structure(self, data: Dict) -> Dict:
        """Ensure all badges are present in data structure"""
        if 'badges' not in data:
            data['badges'] = {}
        
        # Add any missing badges
        for badge_id, badge_def in self.badge_definitions.items():
            if badge_id not in data['badges']:
                data['badges'][badge_id] = {
                    'earned': False,
                    'points': badge_def['points'],
                    'count': 0,
                    'required': badge_def.get('requires_count', 1),
                    'last_earned': None
                }
                if 'time_window' in badge_def:
                    data['badges'][badge_id]['time_window'] = badge_def['time_window']
        
        # Ensure points_by_category exists
        if 'points_by_category' not in data:
            data['points_by_category'] = {
                'prospecting': 0,
                'outreach': 0,
                'engagement': 0,
                'nurture': 0
            }
        
        # Ensure application_badges exists
        if 'application_badges' not in data:
            data['application_badges'] = {}
        
        return data
    
    def get_contacts_for_application(self, company: str) -> List[NetworkingContact]:
        """Get all contacts linked to an application by company name match"""
        all_contacts = self.networking_processor.list_all_contacts()
        
        # Filter by exact company match (case-insensitive, trimmed)
        matching_contacts = []
        company_normalized = company.lower().strip()
        
        for contact in all_contacts:
            contact_company = contact.company_name.lower().strip() if contact.company_name else ''
            if contact_company == company_normalized:
                matching_contacts.append(contact)
        
        return matching_contacts
    
    def calculate_badges_for_application(self, application_id: str, company: str) -> Dict:
        """Calculate badges for contacts linked to a specific application
        Each contact gets ONE badge based on their current status
        """
        contacts = self.get_contacts_for_application(company)
        
        if not contacts:
            return {
                'total_points': 0,
                'badges': {},
                'contacts_count': 0,
                'points_by_category': {
                    'prospecting': 0,
                    'outreach': 0,
                    'engagement': 0,
                    'nurture': 0
                }
            }
        
        # Status mapping for legacy statuses (maps to new status names)
        status_mapping = {
            'Ready to Contact': 'Sent LinkedIn Connection',
            'Ready to Connect': 'Sent LinkedIn Connection',  # Old name
            'Contacted - Sent': 'Sent Email',
            'Contacted - No Response': 'Sent Email',
            'Contacted - Replied': 'Connection Accepted',
            'New Connection': 'Connection Accepted',
            'To Research': 'Found Contact',  # Old name
            'Pending Reply': 'Sent Email',  # Old name
            'Connected - Initial': 'Connection Accepted',  # Old name
            'Cold/Archive': 'Cold/Inactive',
            'Action Pending - You': 'In Conversation',
            'Action Pending - Them': 'In Conversation',
            'Nurture (1-3 Mo.)': 'Strong Connection',
            'Nurture (4-6 Mo.)': 'Strong Connection',
            'Inactive/Dormant': 'Dormant'
        }
        
        # Initialize badge counts
        badge_counts = {}
        for badge_id in self.badge_definitions.keys():
            badge_counts[badge_id] = {
                'count': 0,
                'earned': False,
                'points': self.badge_definitions[badge_id]['points'],
                'required': 1,
                'contacts': []  # Track which contacts have this badge
            }
        
        points_by_category = {
            'prospecting': 0,
            'outreach': 0,
            'engagement': 0,
            'nurture': 0
        }
        
        # Assign one badge per contact based on their status
        for contact in contacts:
            # Normalize status (map legacy to new if needed)
            normalized_status = status_mapping.get(contact.status, contact.status)
            
            # Get badge for this contact's status
            badge_id = self.status_to_badge.get(normalized_status)
            
            if badge_id and badge_id in badge_counts:
                badge_counts[badge_id]['count'] += 1
                badge_counts[badge_id]['contacts'].append({
                    'id': contact.id,
                    'name': contact.person_name,
                    'status': normalized_status
                })
                
                # Add points to category
                badge_def = self.badge_definitions[badge_id]
                phase = badge_def['phase']
                points = badge_def['points']
                
                # For recurring badges, add points for each contact
                # For non-recurring badges, only add points once (when first contact earns it)
                if badge_def.get('recurring', False):
                    # Recurring: add points for each contact
                    points_by_category[phase] += points
                else:
                    # Non-recurring: only add points once when first contact earns the badge
                    if badge_counts[badge_id]['count'] == 1:
                        points_by_category[phase] += points
        
        # Calculate total points and mark badges as earned
        total_points = sum(points_by_category.values())
        
        # Mark badges as earned if they have at least 1 contact
        for badge_id, badge_data in badge_counts.items():
            if badge_data['count'] > 0:
                badge_data['earned'] = True
        
        return {
            'total_points': total_points,
            'badges': badge_counts,
            'contacts_count': len(contacts),
            'points_by_category': points_by_category
        }
    
    def _count_weekly_sends(self, contact: NetworkingContact) -> int:
        """Count how many times contact was sent to in the past week"""
        if not contact.folder_path:
            return 0
        
        updates_dir = contact.folder_path / "updates"
        if not updates_dir.exists():
            return 0
        
        week_ago = datetime.now() - timedelta(days=7)
        send_count = 0
        
        for update_file in updates_dir.iterdir():
            if update_file.is_file() and update_file.suffix == '.html':
                # Check file modification time
                file_time = datetime.fromtimestamp(update_file.stat().st_mtime)
                if file_time >= week_ago:
                    # Check if status indicates a send
                    filename_parts = update_file.stem.split('-', 1)
                    if len(filename_parts) == 2:
                        status = filename_parts[1]
                        if 'Pending Reply' in status or 'Contacted' in status:
                            send_count += 1
        
        return send_count
    
    def update_badge_cache(self, contact_id: str, old_status: str, new_status: str) -> None:
        """Incrementally update badge cache when status changes"""
        # Load current rewards data
        rewards_data = self.load_rewards_data()
        
        # Get contact to check company
        contact = self.networking_processor.get_contact_by_id(contact_id)
        if not contact:
            return
        
        # Check if status change triggers any badges
        for badge_id, badge_def in self.badge_definitions.items():
            if new_status == badge_def['trigger_status']:
                # Check if contact is linked to any application
                # For now, we'll update global badges
                # Application-specific badges are calculated on-demand
                
                badge_data = rewards_data['badges'].get(badge_id, {
                    'earned': False,
                    'points': badge_def['points'],
                    'count': 0,
                    'required': badge_def.get('requires_count', 1),
                    'last_earned': None
                })
                
                badge_data['count'] += 1
                
                # Check if badge is now earned
                if badge_data['count'] >= badge_data['required']:
                    if not badge_data['earned']:
                        badge_data['earned'] = True
                    badge_data['last_earned'] = datetime.now().isoformat()
                    
                    # Update points
                    phase = badge_def['phase']
                    if badge_def.get('recurring', False):
                        points_to_add = badge_def['points']
                    else:
                        # Only add points if this is the first time earning
                        if badge_data['count'] == badge_data['required']:
                            points_to_add = badge_def['points']
                        else:
                            points_to_add = 0
                    
                    if points_to_add > 0:
                        rewards_data['total_points'] += points_to_add
                        rewards_data['points_by_category'][phase] += points_to_add
                
                rewards_data['badges'][badge_id] = badge_data
        
        # Update last calculated timestamp
        rewards_data['last_calculated'] = datetime.now().isoformat()
        
        # Save updated data
        self.save_rewards_data(rewards_data)
    
    def calculate_historical_badges(self) -> Dict:
        """Calculate badges for all existing contacts retroactively"""
        print("Calculating historical badges...")
        
        all_contacts = self.networking_processor.list_all_contacts()
        rewards_data = self._initialize_rewards_data()
        
        print(f"Processing {len(all_contacts)} contacts...")
        
        # Process each contact
        for i, contact in enumerate(all_contacts, 1):
            if i % 10 == 0:
                print(f"  Processed {i}/{len(all_contacts)} contacts...")
            
            # Check current status for badges
            for badge_id, badge_def in self.badge_definitions.items():
                if contact.status == badge_def['trigger_status']:
                    badge_data = rewards_data['badges'][badge_id]
                    badge_data['count'] += 1
                    
                    # Check if badge is earned
                    if badge_data['count'] >= badge_data['required']:
                        badge_data['earned'] = True
                        if not badge_data['last_earned']:
                            badge_data['last_earned'] = datetime.now().isoformat()
                        
                        # Add points (for recurring badges, add points each time)
                        phase = badge_def['phase']
                        if badge_def.get('recurring', False):
                            # Recurring badges: add points for each occurrence
                            rewards_data['total_points'] += badge_def['points']
                            rewards_data['points_by_category'][phase] += badge_def['points']
                        else:
                            # Non-recurring badges: only add points once when first earned
                            if badge_data['count'] == badge_data['required']:
                                rewards_data['total_points'] += badge_def['points']
                                rewards_data['points_by_category'][phase] += badge_def['points']
        
        # Recalculate total points based on final badge counts
        # This ensures accuracy for recurring badges
        total_points = 0
        points_by_category = {
            'prospecting': 0,
            'outreach': 0,
            'engagement': 0,
            'nurture': 0
        }
        
        for badge_id, badge_data in rewards_data['badges'].items():
            # Skip badges that no longer exist in definitions
            if badge_id not in self.badge_definitions:
                continue
            if badge_data['earned']:
                badge_def = self.badge_definitions[badge_id]
                phase = badge_def['phase']
                
                if badge_def.get('recurring', False):
                    points = badge_def['points'] * badge_data['count']
                else:
                    points = badge_def['points']
                
                total_points += points
                points_by_category[phase] += points
        
        rewards_data['total_points'] = total_points
        rewards_data['points_by_category'] = points_by_category
        
        # Update timestamp
        rewards_data['last_calculated'] = datetime.now().isoformat()
        
        # Save rewards data
        self.save_rewards_data(rewards_data)
        
        print(f"Historical badge calculation complete. Total points: {rewards_data['total_points']}")
        return rewards_data
    
    def get_badges_by_category(self) -> Dict:
        """Get badges and points organized by category"""
        rewards_data = self.load_rewards_data()
        
        badges_by_category = {
            'prospecting': {'badges': [], 'points': 0},
            'outreach': {'badges': [], 'points': 0},
            'engagement': {'badges': [], 'points': 0},
            'nurture': {'badges': [], 'points': 0}
        }
        
        for badge_id, badge_data in rewards_data['badges'].items():
            # Skip badges that no longer exist in definitions (e.g., removed badges)
            if badge_id not in self.badge_definitions:
                continue
            badge_def = self.badge_definitions[badge_id]
            phase = badge_def['phase']
            
            badge_info = {
                'id': badge_id,
                'name': badge_def['name'],
                'points': badge_def['points'],
                'earned': badge_data['earned'],
                'count': badge_data['count'],
                'required': badge_data.get('required', 1),
                'description': badge_def['description']
            }
            
            badges_by_category[phase]['badges'].append(badge_info)
            
            # Calculate points for this badge
            if badge_data['earned']:
                if badge_def.get('recurring', False):
                    points = badge_def['points'] * badge_data['count']
                else:
                    points = badge_def['points']
                badges_by_category[phase]['points'] += points
        
        return badges_by_category

