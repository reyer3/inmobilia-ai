"""Tests for data validation utilities."""

# Using pytest framework for testing

from src.utils.validators import validate_dni, validate_email, validate_phone_number


def test_validate_phone_number():
    """Test validation of Peruvian phone numbers."""
    # Valid formats
    assert validate_phone_number("987654321") is True
    assert validate_phone_number("+51987654321") is True
    assert validate_phone_number("51 987 654 321") is True

    # Invalid formats
    assert validate_phone_number("87654321") is False  # Missing 9 prefix
    assert validate_phone_number("9876543") is False  # Too short
    assert (
        validate_phone_number("51887654321") is False
    )  # Wrong prefix after country code
    assert validate_phone_number("") is False  # Empty
    assert validate_phone_number(None) is False  # None


def test_validate_email():
    """Test validation of email addresses."""
    # Valid emails
    assert validate_email("user@example.com") is True
    assert validate_email("user.name+tag@example.co.uk") is True

    # Invalid emails
    assert validate_email("user@example") is False  # Missing TLD
    assert validate_email("user@.com") is False  # Missing domain
    assert validate_email("@example.com") is False  # Missing username
    assert validate_email("") is False  # Empty
    assert validate_email(None) is False  # None


def test_validate_dni():
    """Test validation of Peruvian DNI numbers."""
    # Valid DNI
    assert validate_dni("12345678") is True

    # Invalid DNI
    assert validate_dni("1234567") is False  # Too short
    assert validate_dni("123456789") is False  # Too long
    assert validate_dni("1234567A") is False  # Contains letter
    assert validate_dni("") is False  # Empty
    assert validate_dni(None) is False  # None
