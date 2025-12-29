"""Contact count cache service for performance optimization"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from app.services.networking_processor import NetworkingProcessor
from app.utils.file_utils import get_data_path, ensure_dir_exists, load_yaml, save_yaml
from app.utils.datetime_utils import get_est_now


class ContactCountCache:
    """Manages YAML cache for contact counts by company name"""
    
    def __init__(self):
        self.cache_dir = get_data_path('config')
        ensure_dir_exists(self.cache_dir)
        self.cache_file = self.cache_dir / 'contact_counts_cache.yaml'
        self.networking_processor = NetworkingProcessor()
    
    def load_cache(self) -> Dict[str, Dict]:
        """
        Load cache from YAML file.
        Returns empty dict if cache is missing or invalid.
        """
        if not self.cache_file.exists():
            return {}
        
        try:
            cache_data = load_yaml(self.cache_file)
            company_counts = cache_data.get('company_counts', {})
            return company_counts
        except Exception as e:
            print(f"Warning: Could not load contact count cache: {e}")
            return {}
    
    def get_count(self, company_name: str, cache: Optional[Dict] = None) -> int:
        """
        Get contact count for a company name (O(1) lookup).
        
        Args:
            company_name: Company name to look up
            cache: Optional pre-loaded cache dict. If None, loads from file.
        
        Returns:
            Contact count for the company (0 if not found)
        """
        if cache is None:
            cache = self.load_cache()
        
        company_key = company_name.lower().strip()
        if not company_key:
            return 0
        
        company_data = cache.get(company_key, {})
        return company_data.get('count', 0)
    
    def get_contact_ids(self, company_name: str, cache: Optional[Dict] = None) -> List[str]:
        """
        Get contact IDs for a company name.
        
        Args:
            company_name: Company name to look up
            cache: Optional pre-loaded cache dict. If None, loads from file.
        
        Returns:
            List of contact IDs for the company (empty list if not found)
        """
        if cache is None:
            cache = self.load_cache()
        
        company_key = company_name.lower().strip()
        if not company_key:
            return []
        
        company_data = cache.get(company_key, {})
        return company_data.get('contact_ids', [])
    
    def get_latest_badge(self, company_name: str, cache: Optional[Dict] = None) -> Optional[Dict]:
        """
        Get the latest earned badge for a company name (O(1) lookup).
        
        Args:
            company_name: Company name to look up
            cache: Optional pre-loaded cache dict. If None, loads from file.
        
        Returns:
            Dict with badge_id, badge_name, badge_points, or None if no badge earned
        """
        if cache is None:
            cache = self.load_cache()
        
        company_key = company_name.lower().strip()
        if not company_key:
            return None
        
        company_data = cache.get(company_key, {})
        return company_data.get('latest_badge')
    
    def _calculate_latest_badge_for_company(self, contacts: List) -> Optional[Dict]:
        """
        Calculate the latest/highest earned badge for a company based on its contacts.
        
        Args:
            contacts: List of NetworkingContact objects for the company
            
        Returns:
            Dict with badge_id, badge_name, badge_points, or None if no badge earned
        """
        try:
            from app.services.badge_calculation_service import BadgeCalculationService
            badge_service = BadgeCalculationService()
            
            # Status progression order (for determining highest badge)
            status_progression = [
                'Sent LinkedIn Connection',  # Deep Diver (+10)
                'Sent Email',                 # Profile Magnet (+3)
                'Connection Accepted',         # Qualified Lead (+15)
                # Legacy statuses (backward compatibility)
                'Ready to Connect',           # Deep Diver (+10)
                'Pending Reply',              # Profile Magnet (+3)
                'Connected - Initial',        # Qualified Lead (+15)
                'In Conversation',       # Conversation Starter (+20)
                'Meeting Scheduled',     # Scheduler Master (+30)
                'Meeting Complete',      # Rapport Builder (+50)
                'Strong Connection',     # Relationship Manager (+2, recurring)
                'Referral Partner'       # Super Connector (+100)
            ]
            
            # Status to badge mapping for progression (with backward compatibility)
            status_to_badge_progression = {
                'Sent LinkedIn Connection': 'deep_diver',
                'Sent Email': 'profile_magnet',
                'Connection Accepted': 'qualified_lead',
                # Legacy statuses (backward compatibility)
                'Ready to Connect': 'deep_diver',
                'Pending Reply': 'profile_magnet',
                'Connected - Initial': 'qualified_lead',
                'In Conversation': 'conversation_starter',
                'Meeting Scheduled': 'scheduler_master',
                'Meeting Complete': 'rapport_builder',
                'Strong Connection': 'relationship_manager',
                'Referral Partner': 'super_connector'
            }
            
            # Status mapping for legacy statuses (maps to new status names)
            status_mapping = {
                'Ready to Contact': 'Sent LinkedIn Connection',
                'Ready to Connect': 'Sent LinkedIn Connection',
                'Contacted - Sent': 'Sent Email',
                'Contacted - No Response': 'Sent Email',
                'Contacted - Replied': 'Connection Accepted',
                'New Connection': 'Connection Accepted',
                'Pending Reply': 'Sent Email',
                'Connected - Initial': 'Connection Accepted',
                'Action Pending - You': 'In Conversation',
                'Action Pending - Them': 'In Conversation',
                'Nurture (1-3 Mo.)': 'Strong Connection',
                'Nurture (4-6 Mo.)': 'Strong Connection'
            }
            
            # Find highest status across all contacts
            highest_status_index = -1
            highest_status = None
            
            for contact in contacts:
                normalized_status = status_mapping.get(contact.status, contact.status)
                if normalized_status in status_progression:
                    status_index = status_progression.index(normalized_status)
                    if status_index > highest_status_index:
                        highest_status_index = status_index
                        highest_status = normalized_status
            
            # Get the highest badge achieved
            if highest_status and highest_status in status_to_badge_progression:
                badge_id = status_to_badge_progression[highest_status]
                badge_def = badge_service.badge_definitions.get(badge_id)
                
                if badge_def:
                    return {
                        'badge_id': badge_id,
                        'badge_name': badge_def['name'],
                        'badge_points': badge_def['points']
                    }
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not calculate badge for company: {e}")
            return None
    
    def regenerate_cache(self) -> Dict[str, Dict]:
        """
        Regenerate cache by loading all contacts and building lookup dictionary.
        Also calculates and stores latest earned badge per company.
        Saves cache to YAML file.
        
        Returns:
            Dictionary mapping company name (normalized) -> {count, contact_ids, latest_badge}
        """
        try:
            all_contacts = self.networking_processor.list_all_contacts()
            
            # Build cache dictionary: company_name (normalized) -> {count, contact_ids, latest_badge}
            company_counts = {}
            
            # Group contacts by company first
            contacts_by_company = {}
            for contact in all_contacts:
                if contact and contact.company_name:
                    company_key = contact.company_name.lower().strip()
                    if company_key:
                        if company_key not in contacts_by_company:
                            contacts_by_company[company_key] = []
                        contacts_by_company[company_key].append(contact)
            
            # Build cache structure with counts, IDs, and badges
            for company_key, contacts in contacts_by_company.items():
                contact_ids = [c.id for c in contacts if c.id]
                
                # Calculate latest badge for this company
                latest_badge = self._calculate_latest_badge_for_company(contacts)
                
                company_counts[company_key] = {
                    'count': len(contacts),
                    'contact_ids': contact_ids,
                    'latest_badge': latest_badge
                }
            
            # Save to YAML file
            cache_data = {
                'last_updated': get_est_now().isoformat(),
                'company_counts': company_counts
            }
            save_yaml(cache_data, self.cache_file)
            
            print(f"Contact count cache regenerated: {len(company_counts)} companies, {len(all_contacts)} total contacts")
            return company_counts
            
        except Exception as e:
            print(f"Error regenerating contact count cache: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def invalidate_cache(self) -> None:
        """
        Invalidate cache by deleting the cache file.
        Cache will be automatically regenerated on next load.
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                print("Contact count cache invalidated")
        except Exception as e:
            print(f"Warning: Could not invalidate contact count cache: {e}")
    
    def get_or_regenerate_cache(self) -> Dict[str, Dict]:
        """
        Get cache if it exists, otherwise regenerate it.
        This is the main method to use for loading cache.
        
        Returns:
            Dictionary mapping company name (normalized) -> {count, contact_ids, latest_badge}
        """
        cache = self.load_cache()
        
        # If cache is empty, regenerate it
        if not cache:
            cache = self.regenerate_cache()
        
        return cache

