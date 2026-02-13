"""Input validation utilities."""
from datetime import datetime
from typing import Optional
from dateutil import parser as date_parser
from .constants import VALID_CLASSES, VALID_ROLES, VALID_STATUSES


def validate_date(date_string: str) -> Optional[str]:
    """Validate and normalize a date string.
    
    Args:
        date_string: Date string in various formats
        
    Returns:
        Normalized date string (YYYY-MM-DD) or None if invalid
    """
    try:
        # Try to parse the date using dateutil with dayfirst=True for DD/MM/YYYY format
        # This prevents ambiguous dates like "01/02/2024" from being misinterpreted
        parsed_date = date_parser.parse(date_string, fuzzy=True, dayfirst=True)
        # Return in standardized format
        return parsed_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def validate_class(class_name: str) -> Optional[str]:
    """Validate a WoW class name.
    
    Args:
        class_name: Class name to validate
        
    Returns:
        Validated class name or None if invalid
    """
    # Case-insensitive matching
    for valid_class in VALID_CLASSES:
        if class_name.lower() == valid_class.lower():
            return valid_class
    return None


def validate_role(role: str) -> Optional[str]:
    """Validate a role name.
    
    Args:
        role: Role name to validate
        
    Returns:
        Validated role name or None if invalid
    """
    # Case-insensitive matching
    for valid_role in VALID_ROLES:
        if role.lower() == valid_role.lower():
            return valid_role
    return None


def validate_status(status: str) -> Optional[str]:
    """Validate a roster status.
    
    Args:
        status: Status to validate
        
    Returns:
        Validated status or None if invalid
    """
    # Case-insensitive matching
    for valid_status in VALID_STATUSES:
        if status.lower() == valid_status.lower():
            return valid_status
    return None


def validate_player_name(name: str) -> bool:
    """Validate a player name.
    
    Args:
        name: Player name to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation: not empty, reasonable length
    return bool(name and len(name) >= 2 and len(name) <= 50)


def validate_character_name(name: str) -> bool:
    """Validate a character name.
    
    Args:
        name: Character name to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation: not empty, reasonable length, alphanumeric
    return bool(name and len(name) >= 2 and len(name) <= 20)
