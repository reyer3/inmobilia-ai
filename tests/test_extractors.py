"""Tests for data extraction utilities."""

import pytest

from src.utils.extractors import extract_consent, extract_phone_number, extract_property_type


def test_extract_property_type():
    """Test extraction of property types."""
    # Test departamento extraction
    assert extract_property_type("Busco un departamento") == "departamento"
    assert extract_property_type("Necesito un depa") == "departamento"
    
    # Test casa extraction
    assert extract_property_type("Quiero una casa") == "casa"
    assert extract_property_type("Busco vivienda") == "casa"
    
    # Test oficina extraction
    assert extract_property_type("Necesito una oficina") == "oficina"
    assert extract_property_type("Busco local comercial") == "oficina"
    
    # Test terreno extraction
    assert extract_property_type("Quiero un terreno") == "terreno"
    assert extract_property_type("Busco un lote") == "terreno"
    
    # Test no match
    assert extract_property_type("Hola buenos días") is None

def test_extract_consent():
    """Test extraction of consent."""
    # Test affirmative responses
    assert extract_consent("Sí, acepto") == True
    assert extract_consent("Claro, por supuesto") == True
    assert extract_consent("Estoy de acuerdo") == True
    assert extract_consent("Ok, adelante") == True
    
    # Test negative or unclear responses
    assert extract_consent("No estoy seguro") == False
    assert extract_consent("¿Qué implica esto?") == False

def test_extract_phone_number():
    """Test extraction of Peruvian phone numbers."""
    # Test basic 9-digit format
    assert extract_phone_number("Mi número es 987654321") == "987654321"
    
    # Test with country code
    assert extract_phone_number("Me puedes llamar al +51987654321") == "+51987654321"
    assert extract_phone_number("Contacto: 51-987654321") == "51-987654321"
    
    # Test with spaces
    assert extract_phone_number("Mi cel es 51 987 654 321") == "51 987 654 321"
    
    # Test within a sentence
    assert extract_phone_number("Para coordinar llámame al 987654321 en cualquier momento") == "987654321"
    
    # Test multiple numbers (should return the first valid one)
    assert extract_phone_number("Tengo dos números: 987654321 y 987123456") == "987654321"
    
    # Test invalid formats
    assert extract_phone_number("Mi número fijo es 2137890") is None  # Not starting with 9
    assert extract_phone_number("12345678") is None  # Not starting with 9
    assert extract_phone_number("Texto sin número") is None  # No phone number
    
    # Test empty input
    assert extract_phone_number("") is None
    assert extract_phone_number(None) is None