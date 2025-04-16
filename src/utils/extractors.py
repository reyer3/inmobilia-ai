"""Data extraction utilities.

This module contains functions to extract structured data from natural language responses.
"""

import re

from src.utils.validators import validate_phone_number

# These are placeholder functions for Phase 1
# They will be enhanced with NLP capabilities in Phase 2

def extract_name(text):
    """Extract person name from text."""
    # Simple implementation for Phase 1
    # Later phases will use NER models
    return text.strip()

def extract_property_type(text):
    """Identify property type mentioned in text."""
    text = text.lower()
    
    # Simple keyword matching
    if any(word in text for word in ["departamento", "depa", "flat", "apartamento"]):
        return "departamento"
    elif any(word in text for word in ["casa", "vivienda", "hogar", "chalet"]):
        return "casa"
    elif any(word in text for word in ["oficina", "local", "comercial"]):
        return "oficina"
    elif any(word in text for word in ["terreno", "lote", "parcela", "tierra"]):
        return "terreno"
    else:
        return None

def extract_location(text):
    """Extract district or zone from text."""
    # This will be implemented in Phase 2
    # Will use a gazetteer of Lima districts
    return None

def extract_phone_number(text):
    """Extract phone number from text.
    
    Identifies and extracts Peruvian phone numbers in various formats:
    - 9XXXXXXXX (9 digits starting with 9)
    - +519XXXXXXXX (with country code)
    - 51-9XXXXXXXX (with country code and hyphen)
    - 51 9XX XXX XXX (with spaces)
    
    Args:
        text (str): Text containing potential phone numbers
        
    Returns:
        str or None: Extracted phone number if found, None otherwise
    """
    if not text:
        return None
    
    # Common patterns for Peruvian phone numbers
    patterns = [
        r'\b9\d{8}\b',                       # 9XXXXXXXX
        r'(?:\+51|51)[- ]?9[- ]?\d{8}\b',    # +519XXXXXXXX or 519XXXXXXXX with optional spaces/hyphens
        r'\b51[- ]?9[- ]?\d{2}[- ]?\d{3}[- ]?\d{3}\b'  # 51 9XX XXX XXX with various separators
    ]
    
    # Try each pattern
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Clean up the first match and validate
            candidate = matches[0]
            if validate_phone_number(candidate):
                return candidate
    
    return None

def extract_consent(text):
    """Check if text contains consent."""
    text = text.lower()
    
    # Simple keyword matching for consent
    affirmative = ["si", "sí", "acepto", "autorizo", "claro", "de acuerdo", 
                  "ok", "okay", "por supuesto"]
    
    return any(word in text for word in affirmative)