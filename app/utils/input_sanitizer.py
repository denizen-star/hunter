#!/usr/bin/env python3
"""
Input sanitization utilities for trimming spaces and removing dangerous characters.

This module provides functions to sanitize user input by:
1. Trimming leading and trailing whitespace (primary concern)
2. Removing dangerous/problematic characters while preserving common ones
   (e.g., hyphens, apostrophes, ampersands for names like O'Brien, Mary-Jane, AT&T)
"""

import re
from typing import Optional


def sanitize_text(text: Optional[str]) -> str:
    """
    Sanitize general text input by trimming spaces and removing dangerous characters.
    
    Preserves common characters needed for names and company names:
    - Hyphens (-) for names like Mary-Jane
    - Apostrophes (') for names like O'Brien
    - Ampersands (&) for companies like AT&T
    - Letters, numbers, and spaces
    
    Removes dangerous/problematic characters:
    - Control characters
    - Path separators (/ \)
    - Wildcards (* ?)
    - Quotes that could break things (" ')
    - Other problematic characters
    
    Args:
        text: Input string to sanitize, can be None
        
    Returns:
        Sanitized string with trimmed spaces and dangerous chars removed
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Trim leading and trailing whitespace (primary concern)
    text = text.strip()
    
    # Remove dangerous/problematic characters while preserving common ones
    # Keep: letters, numbers, spaces, hyphens, apostrophes, ampersands, periods
    # Remove: control chars, path separators, wildcards, quotes, etc.
    dangerous_chars_pattern = r'[<>:"|?*\\/\x00-\x1f\x7f-\x9f]'
    text = re.sub(dangerous_chars_pattern, '', text)
    
    # Remove quotes that could break things (but keep apostrophes in the middle)
    # Only remove quotes at the start/end or standalone quotes
    text = re.sub(r'^["\']+|["\']+$', '', text)
    
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def sanitize_email(text: Optional[str]) -> str:
    """
    Sanitize email input by trimming spaces and removing dangerous characters.
    
    Preserves @ and . characters required for valid email addresses.
    
    Args:
        text: Email string to sanitize, can be None
        
    Returns:
        Sanitized email string
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Trim leading and trailing whitespace (primary concern)
    text = text.strip()
    
    # Remove dangerous characters but preserve @ and . for email
    dangerous_chars_pattern = r'[<>:"|?*\\/\x00-\x1f\x7f-\x9f]'
    text = re.sub(dangerous_chars_pattern, '', text)
    
    # Remove quotes
    text = re.sub(r'^["\']+|["\']+$', '', text)
    
    return text.strip()


def sanitize_phone(text: Optional[str]) -> str:
    """
    Sanitize phone input by trimming spaces and removing dangerous characters.
    
    Preserves +, -, (, ), and spaces for phone number formatting.
    
    Args:
        text: Phone string to sanitize, can be None
        
    Returns:
        Sanitized phone string
    """
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Trim leading and trailing whitespace (primary concern)
    text = text.strip()
    
    # Remove dangerous characters but preserve +, -, (, ), and spaces for phone format
    dangerous_chars_pattern = r'[<>:"|?*\\/\x00-\x1f\x7f-\x9f]'
    text = re.sub(dangerous_chars_pattern, '', text)
    
    # Remove quotes
    text = re.sub(r'^["\']+|["\']+$', '', text)
    
    return text.strip()


def sanitize_optional(text: Optional[str]) -> Optional[str]:
    """
    Sanitize optional text input. Returns None if input is None or empty after sanitization.
    
    Args:
        text: Input string to sanitize, can be None
        
    Returns:
        Sanitized string or None if input was None/empty
    """
    if text is None:
        return None
    
    sanitized = sanitize_text(text)
    return sanitized if sanitized else None
