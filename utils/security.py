#!/usr/bin/env python3
"""
Security utilities for ARCHIRAPID
Input sanitization, validation, and XSS prevention
"""

import html
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks
    Escapes HTML special characters
    """
    if not text:
        return ""
    return html.escape(str(text))


def sanitize_url(url: str, allowed_schemes: List[str] = None) -> Optional[str]:
    """
    Validate and sanitize URLs to prevent injection attacks
    
    Args:
        url: URL to sanitize
        allowed_schemes: List of allowed URL schemes (default: http, https, data)
    
    Returns:
        Sanitized URL or None if invalid
    """
    if not url:
        return None
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https', 'data']
    
    try:
        # Handle data URLs separately (for base64 images)
        if url.startswith('data:image/'):
            # Validate data URL format with proper base64 validation
            # Base64 must be padded correctly and only contain valid characters
            pattern = r'^data:image/(png|jpeg|jpg|gif|webp);base64,(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'
            if re.match(pattern, url):
                return url
            return None
        
        parsed = urlparse(url)
        
        # Check if scheme is allowed
        if parsed.scheme not in allowed_schemes:
            return None
        
        # Return sanitized URL
        return url
    except Exception:
        return None


def validate_email(email: str) -> bool:
    """
    Validate email format according to RFC standards
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format
    """
    if not email:
        return False
    
    # More strict email regex validation
    # - No consecutive dots
    # - No dots at start/end of local part
    # - Valid characters only
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}$'
    
    # Additional check for consecutive dots
    if '..' in email:
        return False
    
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (Spanish format)
    
    Args:
        phone: Phone number to validate
    
    Returns:
        True if valid phone format
    """
    if not phone:
        return False
    
    # Remove spaces and common separators
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Spanish phone format: +34 followed by 9 digits or just 9 digits
    pattern = r'^(\+34)?[6-9]\d{8}$'
    return bool(re.match(pattern, clean_phone))


def validate_numeric_range(value: Any, min_val: float = None, max_val: float = None) -> bool:
    """
    Validate that a numeric value is within acceptable range
    
    Args:
        value: Value to validate
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value
    
    Returns:
        True if value is valid
    """
    try:
        num_value = float(value)
        
        if min_val is not None and num_value < min_val:
            return False
        
        if max_val is not None and num_value > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks
    
    Args:
        filename: Filename to sanitize
    
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove path separators and dangerous characters
    safe_name = re.sub(r'[/\\:*?"<>|]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')
    
    # Limit length
    if len(safe_name) > 255:
        safe_name = safe_name[:255]
    
    return safe_name or "unnamed"


def validate_coordinate(lat: float, lng: float) -> bool:
    """
    Validate geographic coordinates
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        True if coordinates are valid
    """
    try:
        lat_val = float(lat)
        lng_val = float(lng)
        
        # Valid latitude: -90 to 90
        # Valid longitude: -180 to 180
        return -90 <= lat_val <= 90 and -180 <= lng_val <= 180
    except (ValueError, TypeError):
        return False


def sanitize_form_data(data: Dict) -> Dict:
    """
    Sanitize all string fields in a form data dictionary
    
    Args:
        data: Dictionary with form data
    
    Returns:
        Dictionary with sanitized data
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_form_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_html(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def validate_catastral_reference(ref: str) -> bool:
    """
    Validate Spanish cadastral reference format
    
    Args:
        ref: Cadastral reference
    
    Returns:
        True if format is valid
    """
    if not ref:
        return False
    
    # Spanish cadastral reference: 20 characters
    # Format: 7 digits + 4 letters + 7 digits + 2 letters
    pattern = r'^\d{7}[A-Z]{4}\d{7}[A-Z]{2}$'
    return bool(re.match(pattern, ref.upper().replace(' ', '')))


# Input validation rules for different field types
VALIDATION_RULES = {
    'email': validate_email,
    'phone': validate_phone,
    'catastral_ref': validate_catastral_reference,
}


def validate_field(field_type: str, value: Any) -> bool:
    """
    Validate a field based on its type
    
    Args:
        field_type: Type of field to validate
        value: Value to validate
    
    Returns:
        True if validation passes
    """
    validator = VALIDATION_RULES.get(field_type)
    if validator:
        return validator(value)
    return True  # No specific validation rule, assume valid
