"""Validation utilities for lead data.

This module contains functions to validate different types of user data.
"""

import re


def validate_phone_number(phone):
    """Validate Peruvian phone number.

    Valid formats:
    - 9XXXXXXXX (9 digits starting with 9)
    - +519XXXXXXXX
    - 51-9XXXXXXXX (with hyphen)
    - 51 9XX XXX XXX (with spaces)
    """
    if not phone:
        return False

    # For formats we want to preserve (like +51, spaces, hyphens)
    # First check if it matches our expected formats before cleaning
    if re.match(r"^\+51\d{9}$", phone):  # +519XXXXXXXX format
        return True
    if re.match(r"^51-9\d{8}$", phone):  # 51-9XXXXXXXX format
        return True
    if re.match(r"^51 \d{3} \d{3} \d{3}$", phone):  # 51 9XX XXX XXX format
        return True
    if re.match(r"^51 \d{9}$", phone):  # 51 9XXXXXXXX format
        return True

    # Remove spaces, parentheses, hyphens, etc. for basic validation
    clean_phone = re.sub(r"\s+|-|\(|\)|\+", "", phone)

    # Check patterns
    if re.match(r"^9\d{8}$", clean_phone):  # 9XXXXXXXX format
        return True
    elif re.match(r"^519\d{8}$", clean_phone):  # 519XXXXXXXX format
        return True

    return False


def validate_email(email):
    """Validate email format."""
    if not email:
        return False

    # Basic email validation pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_dni(dni):
    """Validate Peruvian DNI format (8 digits)."""
    if not dni:
        return False

    return bool(re.match(r"^\d{8}$", dni))


def validate_foreign_id(id_number):
    """Validate foreign ID (Carnet de Extranjería or Passport)."""
    if not id_number:
        return False

    # Between 3 and 15 characters
    return 3 <= len(id_number) <= 15
