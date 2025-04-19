"""Definición del estado para el grafo del agente conversacional."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from typing_extensions import Annotated

from .lead_data import LeadData


class AgentNode(str, Enum):
    """Nodos principales del grafo conversacional."""

    WELCOME = "welcome"
    COLLECT_CONSENT = "collect_consent"
    EXTRACT_INFORMATION = "extract_information"
    ASK_MISSING_INFO = "ask_missing_info"
    ENRICH_LEAD = "enrich_lead"
    CLOSE_CONVERSATION = "close_conversation"
    FALLBACK = "fallback"


class Message(TypedDict):
    """Mensaje en la conversación."""

    role: Literal["user", "assistant", "system"]
    content: str
    name: Optional[str]


class AgentState(TypedDict, total=False):
    """Estado compartido a través del grafo de conversación."""

    # Información del lead
    lead_data: Dict[str, Any]
    lead_obj: Optional[LeadData]
    # Estado de la conversación
    conversation_history: List[Dict[str, str]]
    messages: List[Union[Message, Annotated[List[str], lambda x, y: x + y]]]
    current_message: str
    last_agent: str
    last_response: str
    current_node: AgentNode
    # Contexto y metadatos
    session_id: str
    user_id: str
    conversation_start_time: str
    routing_decisions: List[Dict[str, Any]]
    error: Optional[str]
    # Preferencias y propiedades
    property_matches: List[Dict[str, Any]]
    active_filters: Dict[str, Any]
    # Para el supervisor
    next: Optional[str]
    # Para el sumarizador
    context: Dict[str, Any]
    # Flag para terminar conversación
    should_end: bool


def get_initial_state(message: str, session_id: str, user_id: Optional[str] = None) -> AgentState:
    """Crea el estado inicial para el grafo de conversación."""
    timestamp = datetime.now().isoformat()
    return {
        "lead_data": {},
        "lead_obj": None,  # Inicializar como None para compatibilidad con tests
        "conversation_history": [{"role": "user", "content": message}],
        "messages": [{"role": "user", "content": message}],
        "current_message": message,
        "last_agent": "none",
        "last_response": "",
        "current_node": AgentNode.WELCOME,
        "session_id": session_id,
        "user_id": user_id or session_id,
        "conversation_start_time": timestamp,
        "routing_decisions": [],
        "error": None,
        "property_matches": [],
        "active_filters": {},
        "next": None,
        "context": {},
        "should_end": False,
    }
