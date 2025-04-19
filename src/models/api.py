"""Modelos de datos para la API de Inmobilia AI."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .lead_data import LeadData


class ChatRequest(BaseModel):
    """Solicitud de chat."""

    message: str = Field(..., description="Mensaje del usuario")
    session_id: Optional[str] = Field(
        None, description="ID de sesión existente, si continúa una conversación"
    )
    user_id: Optional[str] = Field(
        None, description="ID de usuario para identificación consistente"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Metadatos adicionales"
    )


class LeadDataResponse(LeadData):
    """Versión de LeadData para respuestas API con campos adicionales."""

    score: Optional[float] = Field(None, description="Puntuación de calidad del lead (0-100)")
    ultima_actualizacion: Optional[str] = Field(
        None, description="Timestamp de última actualización"
    )
    propiedades_sugeridas: Optional[List[str]] = Field(
        None, description="IDs de propiedades sugeridas"
    )


class ChatResponse(BaseModel):
    """Respuesta de chat."""

    message: str = Field(..., description="Respuesta del asistente")
    session_id: str = Field(..., description="ID de la sesión")
    user_id: Optional[str] = Field(None, description="ID del usuario")
    lead_data: LeadDataResponse = Field(
        default_factory=LeadDataResponse, description="Datos del lead extraídos"
    )
    conversation_id: str = Field(..., description="ID único de la conversación")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp de la respuesta",
    )
    agent: Optional[str] = Field(None, description="Agente que generó la respuesta")
    next_agent: Optional[str] = Field(None, description="Próximo agente sugerido")
    estado_lead: Optional[str] = Field(None, description="Estado del lead")


class SessionInfo(BaseModel):
    """Información de una sesión."""

    session_id: str
    user_id: Optional[str] = None
    created_at: str
    last_activity: str
    message_count: int
    lead_status: Optional[str] = None


class SessionListResponse(BaseModel):
    """Respuesta con lista de sesiones activas."""

    total: int
    sessions: List[SessionInfo]


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""

    status: str
    version: str
    environment: str
    uptime: float
    sessions_active: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
