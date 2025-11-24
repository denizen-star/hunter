"""
Location Normalization Utility
Normalizes location strings to consistent formats
"""

import re
from typing import Optional


class LocationNormalizer:
    """Normalize location strings to consistent formats and group by metropolitan areas"""
    
    # Common location patterns and normalizations
    REMOTE_PATTERNS = [
        r'\bremote\b',
        r'\bwork from home\b',
        r'\bwfh\b',
        r'\bvirtual\b',
        r'\banywhere\b',
        r'\bdistributed\b'
    ]
    
    # Hybrid patterns that might indicate remote
    HYBRID_PATTERNS = [
        r'\bhybrid\b',
        r'\bflexible\b',
        r'\bon-site.*remote\b',
        r'\bremote.*on-site\b'
    ]
    
    # Common city/state/country patterns
    US_STATE_ABBREVIATIONS = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    # Metropolitan area mappings - cities that belong to the same metro area
    METRO_AREAS = {
        'New York Metro Area': {
            'cities': [
                'new york', 'new york city', 'nyc', 'manhattan', 'brooklyn', 'queens',
                'bronx', 'staten island', 'jersey city', 'newark', 'westchester',
                'long island', 'yonkers', 'elizabeth', 'paterson', 'bridgeport',
                'stamford', 'white plains', 'new rochelle'
            ],
            'states': ['NY', 'New York', 'NJ', 'New Jersey', 'CT', 'Connecticut'],
            'keywords': ['new york metropolitan area', 'nyc metro', 'tri-state area']
        },
        'Miami Metro Area': {
            'cities': [
                'miami', 'miami beach', 'fort lauderdale', 'hollywood', 'pompano beach',
                'plantation', 'coral gables', 'west palm beach', 'boca raton', 'davie',
                'sunrise', 'miramar', 'pembroke pines', 'weston', 'kendall', 'coral springs'
            ],
            'states': ['FL', 'Florida'],
            'keywords': ['south florida', 'miami-dade', 'broward county', 'miami metropolitan area']
        },
        'Los Angeles Metro Area': {
            'cities': [
                'los angeles', 'la', 'santa monica', 'beverly hills', 'pasadena',
                'glendale', 'long beach', 'anaheim', 'irvine', 'santa ana', 'riverside',
                'san bernardino', 'pomona', 'torrance', 'burbank', 'west covina'
            ],
            'states': ['CA', 'California'],
            'keywords': ['la metro', 'greater los angeles', 'southern california', 'socal']
        },
        'Chicago Metro Area': {
            'cities': [
                'chicago', 'aurora', 'naperville', 'joliet', 'rockford', 'elgin',
                'waukegan', 'cicero', 'peoria', 'champaign', 'bloomington'
            ],
            'states': ['IL', 'Illinois'],
            'keywords': ['chicago metropolitan area', 'greater chicago']
        },
        'San Francisco Bay Area': {
            'cities': [
                'san francisco', 'san jose', 'oakland', 'fremont', 'santa clara',
                'sunnyvale', 'hayward', 'concord', 'vallejo', 'san rafael', 'palo alto',
                'mountain view', 'redwood city', 'foster city', 'south san francisco'
            ],
            'states': ['CA', 'California'],
            'keywords': ['bay area', 'sf bay area', 'silicon valley', 'peninsula']
        },
        'Dallas-Fort Worth Metro Area': {
            'cities': [
                'dallas', 'fort worth', 'arlington', 'plano', 'garland', 'irving',
                'frisco', 'mckinney', 'denton', 'carrollton', 'lewisville'
            ],
            'states': ['TX', 'Texas'],
            'keywords': ['dfw', 'dallas-fort worth', 'metroplex']
        },
        'Seattle Metro Area': {
            'cities': [
                'seattle', 'bellevue', 'tacoma', 'everett', 'spokane', 'renton',
                'kent', 'yakima', 'bremerton', 'bellingham', 'federal way'
            ],
            'states': ['WA', 'Washington'],
            'keywords': ['puget sound', 'greater seattle', 'seattle metropolitan area']
        },
        'Minneapolis-St. Paul Metro Area': {
            'cities': [
                'minneapolis', 'saint paul', 'st. paul', 'bloomington', 'duluth',
                'rochester', 'eden prairie', 'minnetonka', 'plymouth', 'st. cloud'
            ],
            'states': ['MN', 'Minnesota'],
            'keywords': ['twin cities', 'minneapolis-st. paul', 'metro area']
        },
        'Boston Metro Area': {
            'cities': [
                'boston', 'cambridge', 'worcester', 'lowell', 'quincy', 'newton',
                'somerville', 'brookline', 'lynn', 'fall river', 'beverly'
            ],
            'states': ['MA', 'Massachusetts'],
            'keywords': ['greater boston', 'boston metropolitan area', 'metrowest']
        },
        'Atlanta Metro Area': {
            'cities': [
                'atlanta', 'augusta', 'columbus', 'savannah', 'athens', 'sandy springs',
                'roswell', 'macon', 'johns creek', 'albany', 'warner robins'
            ],
            'states': ['GA', 'Georgia'],
            'keywords': ['greater atlanta', 'atlanta metropolitan area']
        },
        'Denver Metro Area': {
            'cities': [
                'denver', 'aurora', 'colorado springs', 'fort collins', 'lakewood',
                'thornton', 'arvada', 'westminster', 'pueblo', 'greeley'
            ],
            'states': ['CO', 'Colorado'],
            'keywords': ['denver metropolitan area', 'front range', 'colorado front range']
        },
        'Orlando Metro Area': {
            'cities': [
                'orlando', 'kissimmee', 'sanford', 'winter park', 'altamonte springs',
                'oviedo', 'winter springs', 'apopka', 'winter garden', 'clermont'
            ],
            'states': ['FL', 'Florida'],
            'keywords': ['greater orlando', 'orlando metropolitan area', 'central florida']
        }
    }
    
    def extract_work_type(self, location: Optional[str], job_description: Optional[str] = None) -> str:
        """
        Extract work type (Remote, Hybrid, On-site) from location and job description.
        
        Args:
            location: Location string
            job_description: Optional job description text
            
        Returns:
            'Remote', 'Hybrid', or 'On-site'
        """
        if not location or not location.strip():
            location_lower = ''
        else:
            location_lower = location.lower()
        
        # Check location for work type indicators
        for pattern in self.REMOTE_PATTERNS:
            if location and re.search(pattern, location_lower, re.IGNORECASE):
                return 'Remote'
        
        for pattern in self.HYBRID_PATTERNS:
            if location and re.search(pattern, location_lower, re.IGNORECASE):
                return 'Hybrid'
        
        # Check job description if location is N/A or doesn't have clear indicators
        if job_description:
            job_desc_lower = job_description.lower()
            
            # Check for remote patterns
            for pattern in self.REMOTE_PATTERNS:
                if re.search(pattern, job_desc_lower, re.IGNORECASE):
                    return 'Remote'
            
            # Check for hybrid patterns
            for pattern in self.HYBRID_PATTERNS:
                if re.search(pattern, job_desc_lower, re.IGNORECASE):
                    return 'Hybrid'
        
        # If location is N/A or empty and no remote indicators, might still be remote
        if location_lower in ['n/a', 'na', 'not specified', 'not mentioned', '']:
            # Without job description, we can't tell, default to On-site
            return 'On-site'
        
        # Default to On-site if no indicators found
        return 'On-site'
    
    def normalize(self, location: Optional[str], job_description: Optional[str] = None, group_by_region: bool = True, remove_work_type: bool = True) -> Optional[str]:
        """
        Normalize a location string to a consistent format and optionally group by state/province/country.
        
        Args:
            location: Location string to normalize
            job_description: Optional job description text to check for remote indicators if location is N/A
            group_by_region: If True, group by state/province/country; if False, use metro areas or city names
            
        Returns:
            Normalized location string or None if invalid
        """
        if not location or not location.strip():
            return None
        
        location = location.strip()
        location_lower = location.lower()
        
        # Handle N/A cases - check if job description indicates remote
        if location_lower in ['n/a', 'na', 'not specified', 'not mentioned', '']:
            work_type = self.extract_work_type(location, job_description)
            # If it's remote and we're removing work type, skip it from location
            if remove_work_type and work_type == 'Remote':
                return None
            # If no remote indicators, return None (skip)
            return None
        
        # Extract work type first (before cleaning location)
        work_type = self.extract_work_type(location, job_description)
        
        # If remove_work_type is True and it's Remote, return None (skip from location insights)
        if remove_work_type and work_type == 'Remote':
            return None
        
        # Check for remote patterns in location itself - skip if remove_work_type
        if not remove_work_type:
            for pattern in self.REMOTE_PATTERNS:
                if re.search(pattern, location_lower, re.IGNORECASE):
                    return 'Remote'
        
        # Check for hybrid patterns - need to clean location before normalizing
        # (This is handled in the city cleaning section below)
        
        # Handle common formats: "City, State" or "City, State, Country"
        parts = [p.strip() for p in location.split(',')]
        
        if len(parts) == 0:
            return None
        
        # Get city (first part) - clean it up
        city_raw = parts[0].strip()
        # Remove parenthetical content like "(hybrid)", "(on-site)", "(Hybrid)", "(On-site)"
        city_raw = re.sub(r'\([^)]*\)', '', city_raw).strip()
        # Remove "on-site" prefixes
        city_raw = re.sub(r'^on-site\s*\(?', '', city_raw, flags=re.IGNORECASE).strip()
        city_raw = city_raw.rstrip('(').strip()
        city_raw = city_raw.rstrip(')').strip()  # Remove trailing parentheses
        
        # Also check if any part after comma contains work type indicators
        if len(parts) > 1:
            # Clean state/province part
            state_part = parts[1].strip()
            # Remove work type indicators from state part
            state_part = re.sub(r'\([^)]*(hybrid|on-site|remote)[^)]*\)', '', state_part, flags=re.IGNORECASE).strip()
            state_part = re.sub(r'\s*\(Hybrid\)', '', state_part, flags=re.IGNORECASE).strip()
            state_part = re.sub(r'\s*\(On-site\)', '', state_part, flags=re.IGNORECASE).strip()
            state_part = re.sub(r'\s*\(Remote\)', '', state_part, flags=re.IGNORECASE).strip()
            state_part = state_part.rstrip(')').strip()
            parts[1] = state_part
        
        if not city_raw:
            return None
        
        city_lower = city_raw.lower()
        
        # If group_by_region is False, check for metro areas first
        if not group_by_region:
            # Check if city belongs to a metropolitan area
            for metro_name, metro_info in self.METRO_AREAS.items():
                # Check keywords first (most reliable)
                if any(keyword.lower() in location_lower for keyword in metro_info['keywords']):
                    return metro_name
                
                # Check city name against metro cities
                metro_city_match = False
                for metro_city in metro_info['cities']:
                    metro_city_lower = metro_city.lower()
                    # Exact match or contains match
                    if (city_lower == metro_city_lower or 
                        city_lower in metro_city_lower or 
                        metro_city_lower in city_lower):
                        metro_city_match = True
                        break
                
                if metro_city_match:
                    # Verify state if provided
                    if len(parts) > 1:
                        state_or_region = parts[1].strip().upper()
                        state_full = self.US_STATE_ABBREVIATIONS.get(state_or_region, state_or_region)
                        
                        # Check if state matches metro area states
                        state_matches = (state_or_region in metro_info['states'] or 
                                        state_full in metro_info['states'] or
                                        state_full.lower() in [s.lower() for s in metro_info['states']])
                        
                        if state_matches:
                            return metro_name
                        # If city matches but state doesn't, still return metro (city match is stronger)
                        return metro_name
                    else:
                        # No state provided, city match is enough
                        return metro_name
        
        # Normalize city name (title case, remove extra spaces)
        city = ' '.join(word.capitalize() for word in city_raw.split())
        
        # If we have state/region info, group by state/province/country
        if len(parts) > 1:
            state_or_region = parts[1].strip().upper()
            
            # Check if it's a US state abbreviation
            if state_or_region in self.US_STATE_ABBREVIATIONS:
                state_full = self.US_STATE_ABBREVIATIONS[state_or_region]
                if group_by_region:
                    # Group by state only
                    return state_full
                else:
                    # Format as "City, State"
                    return f"{city}, {state_full}"
            else:
                # Check if it's a full state name
                state_full_lower = parts[1].strip().lower()
                for abbrev, full_name in self.US_STATE_ABBREVIATIONS.items():
                    if state_full_lower == full_name.lower():
                        if group_by_region:
                            return full_name
                        else:
                            return f"{city}, {full_name}"
                
                # Not a US state, check if it's a country or province
                if len(parts) >= 3:
                    # Format: City, Province, Country
                    country = parts[2].strip()
                    if group_by_region:
                        return country
                    else:
                        return f"{city}, {parts[1].strip()}, {country}"
                elif len(parts) == 2:
                    # Format: City, Province/State
                    province_or_state = parts[1].strip()
                    if group_by_region:
                        return province_or_state
                    else:
                        return f"{city}, {province_or_state}"
        elif group_by_region:
            # No state info, but grouping by region - just return city as is
            return city
        
        return city
    
    def normalize_multiple(self, locations: list, job_descriptions: Optional[list] = None) -> dict:
        """
        Normalize multiple locations and count frequencies.
        
        Args:
            locations: List of location strings
            job_descriptions: Optional list of job descriptions (one per location) for better N/A handling
            
        Returns:
            Dictionary mapping normalized locations to counts
        """
        from collections import Counter
        normalized = Counter()
        
        for i, location in enumerate(locations):
            job_desc = job_descriptions[i] if job_descriptions and i < len(job_descriptions) else None
            norm = self.normalize(location, job_desc)
            if norm:
                normalized[norm] += 1
        
        return dict(normalized)

