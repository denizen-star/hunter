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
    
    def regenerate_cache(self) -> Dict[str, Dict]:
        """
        Regenerate cache by loading all contacts and building lookup dictionary.
        Saves cache to YAML file.
        
        Returns:
            Dictionary mapping company name (normalized) -> {count, contact_ids}
        """
        try:
            all_contacts = self.networking_processor.list_all_contacts()
            
            # Build cache dictionary: company_name (normalized) -> {count, contact_ids}
            company_counts = {}
            
            for contact in all_contacts:
                if contact and contact.company_name:
                    company_key = contact.company_name.lower().strip()
                    if company_key:
                        if company_key not in company_counts:
                            company_counts[company_key] = {
                                'count': 0,
                                'contact_ids': []
                            }
                        company_counts[company_key]['count'] += 1
                        if contact.id:
                            company_counts[company_key]['contact_ids'].append(contact.id)
            
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
            Dictionary mapping company name (normalized) -> {count, contact_ids}
        """
        cache = self.load_cache()
        
        # If cache is empty, regenerate it
        if not cache:
            cache = self.regenerate_cache()
        
        return cache

