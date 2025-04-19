"""Configuración centralizada para la aplicación Inmobilia AI.

Este módulo contiene todas las configuraciones y constantes utilizadas en la aplicación.
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de APIs
APIs = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4.1-nano-2025-04-14"),
        "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
        "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
    },
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"),
        "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0.3")),
        "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
    },
    "langsmith": {
        "api_key": os.getenv("LANGSMITH_API_KEY"),
        "project": os.getenv("LANGSMITH_PROJECT", "inmobilia"),
    },
}

# Configuración del sistema
SYSTEM = {
    "environment": os.getenv("ENVIRONMENT", "development"),
    "debug": os.getenv("DEBUG", "True").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "max_history_length": int(os.getenv("MAX_HISTORY_LENGTH", "10")),
    "user_data_expiry_days": int(os.getenv("USER_DATA_EXPIRY_DAYS", "30")),
}

# Configuración legal
LEGAL = {
    "consent_message": "Para ayudarte mejor, necesito tu autorización para procesar tus datos personales según la Ley 29733 de Protección de Datos Personales de Perú. ¿Me autorizas?",
    "privacy_policy_url": "https://inmobilia.pe/politica-de-privacidad",
    "terms_url": "https://inmobilia.pe/terminos-y-condiciones",
}

# Texto para uso de agentes
AGENT_PROMPTS = {
    "welcome": "Hola, soy el asistente inmobiliario de Inmobilia. Estoy aquí para ayudarte a encontrar tu propiedad ideal en Perú. ¿En qué puedo ayudarte?",
    "goodbye": "Gracias por contactarnos. Pronto un asesor inmobiliario se comunicará contigo. ¡Que tengas un excelente día!",
    "clarification": "No comprendí bien tu solicitud. ¿Podrías por favor ser más específico sobre el tipo de propiedad que estás buscando?",
}

# Nombres de agentes
AGENT_NAMES = {
    "LEGAL": "legal_agent",
    "COLLECTOR": "collector_agent",
    "LOCATION": "location_agent",
    "PREFERENCES": "preferences_agent",
}

# Prioridades de información de leads
LEAD_PRIORITIES = {
    "P10": ["nombre", "tipo_inmueble", "consentimiento"],  # Obligatorios
    "P9": ["celular", "email", "distrito", "metraje"],  # Muy importantes
    "P8": ["habitaciones", "presupuesto_min", "presupuesto_max"],  # Importantes
    "P7": ["timeline_compra", "tipo_documento", "numero_documento"],  # Opcionales
}


def get_settings() -> Dict[str, Any]:
    """Obtiene las configuraciones consolidadas en un solo diccionario.

    Returns:
        Diccionario con todas las configuraciones
    """
    return {
        "apis": APIs,
        "system": SYSTEM,
        "legal": LEGAL,
        "agent_prompts": AGENT_PROMPTS,
        "agent_names": AGENT_NAMES,
        "lead_priorities": LEAD_PRIORITIES,
    }


def validate_env() -> bool:
    """Valida que las variables de entorno necesarias estén configuradas.

    Returns:
        True si todas las configuraciones críticas están presentes, False en caso contrario
    """
    required_vars = ["ANTHROPIC_API_KEY"]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"ERROR: Faltan variables de entorno requeridas: {', '.join(missing_vars)}")
        return False

    return True
