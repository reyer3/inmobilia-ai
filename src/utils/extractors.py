"""Data extraction utilities.

This module contains functions to extract structured data from natural language responses.
"""

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
    """Extract phone number from text."""
    # This will be implemented in Phase 2
    # Will use regex patterns for Peruvian phone numbers
    return None

def extract_consent(text):
    """Check if text contains consent."""
    text = text.lower()
    
    # Simple keyword matching for consent
    affirmative = ["si", "sí", "acepto", "autorizo", "claro", "de acuerdo", 
                  "ok", "okay", "por supuesto"]
    
    return any(word in text for word in affirmative)