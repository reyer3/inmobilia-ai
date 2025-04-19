# src/models/__init__.py
"""Modelos de datos para Inmobilia AI."""

# Exportar modelos de estado
from .agent_state import AgentState, get_initial_state

# Exportar modelos de API
from .api import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LeadDataResponse,
    SessionInfo,
    SessionListResponse,
)

# Exportar enumeraciones
from .enums import EstadoLead, TipoDocumento, TipoInmueble

# Exportar modelos de datos
from .lead_data import LeadData, LeadMetadata

# Exportar validadores
from .validators import (
    parse_habitaciones,
    parse_metraje,
    parse_presupuesto,
    validate_email,
    validate_phone_number,
)

__all__ = [
    # Enums
    "EstadoLead",
    "TipoInmueble",
    "TipoDocumento",
    # Modelos de datos
    "LeadData",
    "LeadMetadata",
    # Estado del agente
    "AgentState",
    "get_initial_state",
    # Modelos de API
    "ChatRequest",
    "ChatResponse",
    "LeadDataResponse",
    "HealthResponse",
    "SessionInfo",
    "SessionListResponse",
    # Validadores
    "parse_metraje",
    "parse_habitaciones",
    "parse_presupuesto",
    "validate_phone_number",
    "validate_email",
]
