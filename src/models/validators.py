"""Funciones de validación para modelos de datos."""

import re
from typing import Optional, Union


def parse_metraje(value: Optional[Union[int, float, str]]) -> Optional[int]:
    """Valida y convierte el metraje a entero si es posible."""
    if value is None:
        return None
    try:
        # Si es un número, convertir directamente
        if isinstance(value, (int, float)):
            return int(value)
        # Si es un string, extraer dígitos y convertir
        if isinstance(value, str):
            # Extraer números del string (puede incluir "50m2" o "50 metros cuadrados")
            digits = re.search(r"(\d+)", value)
            if digits:
                return int(digits.group(1))
        return None
    except (ValueError, TypeError):
        return None


def parse_habitaciones(value: Optional[Union[int, str]]) -> Optional[int]:
    """Valida y convierte el número de habitaciones a entero si es posible."""
    if value is None:
        return None
    try:
        # Si es un número, convertir directamente
        if isinstance(value, (int, float)):
            return int(value)
        # Si es un string, extraer dígitos y convertir
        if isinstance(value, str):
            digits = re.search(r"(\d+)", value)
            if digits:
                return int(digits.group(1))
        return None
    except (ValueError, TypeError):
        return None


def parse_presupuesto(value: Optional[Union[int, float, str]]) -> Optional[float]:
    """Valida y convierte el presupuesto a float si es posible."""
    if value is None:
        return None
    try:
        # Si es un número, convertir directamente
        if isinstance(value, (int, float)):
            return float(value)
        # Si es un string, limpiar y convertir
        if isinstance(value, str):
            # Eliminar símbolos de moneda, comas y espacios
            cleaned = re.sub(r"[^\d.]", "", value.replace(",", "."))
            if cleaned:
                return float(cleaned)
        return None
    except (ValueError, TypeError):
        return None


def validate_phone_number(phone: Optional[str]) -> bool:
    """Valida formato de teléfono peruano."""
    if not phone:
        return False
    # Eliminar espacios, guiones, paréntesis, etc.
    clean_phone = "".join(c for c in phone if c.isdigit() or c == "+")
    # Formato peruano: 9XXXXXXXX o +519XXXXXXXX
    if re.match(r"^9\d{8}$", clean_phone):
        return True
    elif re.match(r"^(?:\+51|51)9\d{8}$", clean_phone):
        return True
    return False


def validate_email(email: Optional[str]) -> bool:
    """Valida formato de correo electrónico."""
    if not email:
        return False
    # Patrón básico para validar emails
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
