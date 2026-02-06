"""
Input validators for TalentScout Hiring Assistant.
Provides validation utilities for candidate information.
"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email address is required"
    
    # Standard email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email.strip()):
        return True, ""
    else:
        return False, "Please provide a valid email address (e.g., example@email.com)"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number format.
    Accepts various international formats.
    
    Args:
        phone: Phone number to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove common formatting characters for validation
    cleaned = re.sub(r'[\s\-\.\(\)\+]', '', phone)
    
    # Check if remaining characters are digits and length is reasonable
    if cleaned.isdigit() and 10 <= len(cleaned) <= 15:
        return True, ""
    else:
        return False, "Please provide a valid phone number (10-15 digits)"


def validate_required_field(value: str, field_name: str) -> Tuple[bool, str]:
    """
    Validate that a required field is not empty.
    
    Args:
        value: Field value to validate
        field_name: Name of the field for error message
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"{field_name} is required"
    
    if len(value.strip()) < 2:
        return False, f"{field_name} seems too short. Please provide more details."
    
    return True, ""


def validate_years_of_experience(years: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate and parse years of experience.
    
    Args:
        years: Years of experience as string
    
    Returns:
        Tuple of (is_valid, parsed_value, error_message)
    """
    if not years:
        return False, None, "Years of experience is required"
    
    # Try to extract number from string
    try:
        # Handle common formats like "5 years", "5+", etc.
        cleaned = re.sub(r'[^\d]', '', years)
        if cleaned:
            parsed = int(cleaned)
            if 0 <= parsed <= 50:  # Reasonable range
                return True, parsed, ""
            else:
                return False, None, "Years of experience should be between 0 and 50"
        else:
            return False, None, "Please provide a numeric value for years of experience"
    except ValueError:
        return False, None, "Please provide a valid number for years of experience"


def validate_tech_stack(tech_stack: str) -> Tuple[bool, list, str]:
    """
    Validate and parse tech stack input.
    
    Args:
        tech_stack: Comma or space-separated list of technologies
    
    Returns:
        Tuple of (is_valid, parsed_list, error_message)
    """
    if not tech_stack:
        return False, [], "Tech stack is required"
    
    # Split by common delimiters
    technologies = re.split(r'[,;/\n]+', tech_stack)
    
    # Clean and filter
    cleaned = [tech.strip() for tech in technologies if tech.strip()]
    
    if not cleaned:
        return False, [], "Please list at least one technology you're proficient in"
    
    if len(cleaned) < 1:
        return False, [], "Please provide at least one technology"
    
    return True, cleaned, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input for safe storage.
    
    Args:
        text: Raw user input
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potential harmful characters while preserving most input
    # This is a basic sanitization - for production, use a proper library
    sanitized = text.strip()
    
    # Remove null bytes and control characters (except newlines and tabs)
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
    
    # Limit length to prevent abuse
    max_length = 5000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
