"""Tests for data extraction utilities."""

import pytest
from src.utils.extractors import extract_property_type, extract_consent

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