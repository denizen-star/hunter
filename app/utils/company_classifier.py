"""Company type classification utility"""
from typing import Optional
import re


class CompanyClassifier:
    """Classify companies as startup, enterprise, or unknown"""
    
    def __init__(self):
        # Known enterprise indicators (Fortune 500, large corporations)
        self.enterprise_keywords = [
            'fortune 500', 'fortune 100', 'fortune 1000',
            'enterprise', 'corporation', 'corp', 'inc',
            'established', 'publicly traded', 'nyse', 'nasdaq',
            'multinational', 'global company', 'worldwide'
        ]
        
        # Known startup indicators
        self.startup_keywords = [
            'startup', 'early stage', 'seed stage', 'series a',
            'series b', 'series c', 'vc backed', 'venture backed',
            'y combinator', 'techstars', '500 startups',
            'growth stage', 'scale-up'
        ]
        
        # Well-known enterprise companies (can be expanded)
        self.known_enterprises = [
            'microsoft', 'google', 'apple', 'amazon', 'meta', 'facebook',
            'ibm', 'oracle', 'salesforce', 'adobe', 'intel', 'nvidia',
            'cisco', 'dell', 'hp', 'hewlett-packard', 'accenture',
            'deloitte', 'pwc', 'ey', 'kpmg', 'goldman sachs', 'jpmorgan',
            'morgan stanley', 'bank of america', 'wells fargo', 'citigroup'
        ]
        
        # Well-known startup accelerators/indicators
        self.startup_indicators = [
            'y combinator', 'yc ', 'techstars', '500 startups',
            'andreessen horowitz', 'sequoia', 'kleiner perkins'
        ]
    
    def classify(
        self,
        company_name: Optional[str] = None,
        job_description: Optional[str] = None
    ) -> str:
        """
        Classify company type based on name and/or job description.
        
        Args:
            company_name: Name of the company
            job_description: Full job description text
        
        Returns:
            'startup', 'enterprise', or 'unknown'
        """
        company_lower = (company_name or '').lower()
        job_desc_lower = (job_description or '').lower()
        
        combined_text = f"{company_lower} {job_desc_lower}"
        
        # Check for enterprise indicators
        enterprise_score = 0
        for keyword in self.enterprise_keywords:
            if keyword in combined_text:
                enterprise_score += 1
        
        # Check against known enterprise list
        for enterprise in self.known_enterprises:
            if enterprise in company_lower:
                enterprise_score += 2
        
        # Check for startup indicators
        startup_score = 0
        for keyword in self.startup_keywords:
            if keyword in combined_text:
                startup_score += 1
        
        # Check against known startup indicators
        for indicator in self.startup_indicators:
            if indicator in combined_text:
                startup_score += 2
        
        # Look for funding rounds in job description
        funding_patterns = [
            r'series [a-z]',
            r'seed round',
            r'vc.?backed',
            r'venture.?backed',
            r'raised.*million',
            r'raised.*billion'
        ]
        
        for pattern in funding_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                startup_score += 1
        
        # Look for company size indicators (enterprise)
        size_patterns = [
            r'\d+,?\d*\s*employees',
            r'thousands?\s*of\s*employees',
            r'global\s*team',
            r'worldwide\s*presence'
        ]
        
        for pattern in size_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                enterprise_score += 1
        
        # Determine classification
        if enterprise_score > startup_score and enterprise_score >= 1:
            return 'enterprise'
        elif startup_score > enterprise_score and startup_score >= 1:
            return 'startup'
        else:
            return 'unknown'









