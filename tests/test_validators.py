"""Tests for data validation utilities."""

import pytest

from src.utils.validators import validate_dni, validate_email, validate_phone_number


def test_validate_phone_number():
    """Test validation of Peruvian phone numbers."""
    # Valid formats
    assert validate_phone_number("987654321") == True
    assert validate_phone_number("+51987654321") == True
    assert validate_phone_number("51 987 654 321") == True
    
    # Invalid formats
    assert validate_phone_number("87654321") == False  # Missing 9 prefix
    assert validate_phone_number("9876543") == False  # Too short
    assert validate_phone_number("51887654321") == False  # Wrong prefix after country code
    assert validate_phone_number("") == False  # Empty
    assert validate_phone_number(None) == False  # None

def test_validate_email():
    """Test validation of email addresses."""
    # Valid emails
    assert validate_email("user@example.com") == True
    assert validate_email("user.name+tag@example.co.uk") == True
    
    # Invalid emails
    assert validate_email("user@example") == False  # Missing TLD
    assert validate_email("user@.com") == False  # Missing domain
    assert validate_email("@example.com") == False  # Missing username
    assert validate_email("") == False  # Empty
    assert validate_email(None) == False  # None

def test_validate_dni():
    """Test validation of Peruvian DNI numbers."""
    # Valid DNI
    assert validate_dni("12345678") == True
    
    # Invalid DNI
    assert validate_dni("1234567") == False  # Too short
    assert validate_dni("123456789") == False  # Too long
    assert validate_dni("1234567A") == False  # Contains letter
    assert validate_dni("") == False  # Empty
    assert validate_dni(None) == False  # None