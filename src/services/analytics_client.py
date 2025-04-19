"""Cliente para enviar datos analíticos de la aplicación.

Este módulo proporciona funciones para enviar datos analíticos
a servicios externos para monitoreo y análisis.
"""

import json
import os
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

# Directorio para almacenar analíticas (para desarrollo)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
ANALYTICS_DIR = os.path.join(DATA_DIR, "analytics")

# Asegurar que los directorios existen
os.makedirs(ANALYTICS_DIR, exist_ok=True)


def track_conversation(thread_id: str, event_type: str, event_data: Dict[str, Any]) -> bool:
    """Registra un evento de conversación para analíticas.

    En un entorno de producción, esto enviaría datos a un sistema analítico como
    Google Analytics, Segment, o un data warehouse interno. Para desarrollo,
    guarda los eventos en archivos JSON locales.

    Args:
        thread_id: Identificador único de la conversación
        event_type: Tipo de evento (por ejemplo, "message_sent", "lead_created")
        event_data: Datos adicionales del evento

    Returns:
        Boolean indicando si la operación fue exitosa
    """
    try:
        # Estructura del evento
        event = {
            "thread_id": thread_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data,
        }

        # Crear archivo para el thread si no existe
        thread_analytics_file = os.path.join(ANALYTICS_DIR, f"{thread_id}_events.json")

        # Cargar eventos existentes o crear una lista nueva
        if os.path.exists(thread_analytics_file):
            with open(thread_analytics_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            if not isinstance(events, list):
                events = []
        else:
            events = []

        # Añadir nuevo evento
        events.append(event)

        # Guardar eventos actualizados
        with open(thread_analytics_file, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"Error al registrar evento analítico: {e}")
        traceback.print_exc()
        return False


def track_agent_assignment(thread_id: str, user_message: str, assigned_agent: str) -> bool:
    """Registra la asignación de un agente a un mensaje del usuario.

    Args:
        thread_id: Identificador único de la conversación
        user_message: Mensaje del usuario
        assigned_agent: Agente asignado (por ejemplo, "legal", "collector")

    Returns:
        Boolean indicando si la operación fue exitosa
    """
    return track_conversation(
        thread_id=thread_id,
        event_type="agent_assignment",
        event_data={
            "user_message": (
                user_message[:100] + "..." if len(user_message) > 100 else user_message
            ),
            "assigned_agent": assigned_agent,
        },
    )


def track_lead_update(thread_id: str, lead_data: Dict[str, Any], source: str) -> bool:
    """Registra una actualización en los datos de un lead.

    Args:
        thread_id: Identificador único de la conversación
        lead_data: Datos actualizados del lead
        source: Origen de la actualización (por ejemplo, "legal_agent", "collector_agent")

    Returns:
        Boolean indicando si la operación fue exitosa
    """
    # Filtrar datos sensibles para la analítica
    filtered_data = {}
    for key, value in lead_data.items():
        # Excluir ciertos campos sensibles
        if key in ["numero_documento", "celular", "email"]:
            if value:  # Solo registrar si existe, pero no su valor
                filtered_data[key] = "[REDACTED]"
        else:
            filtered_data[key] = value

    return track_conversation(
        thread_id=thread_id,
        event_type="lead_update",
        event_data={
            "lead_data": filtered_data,
            "source": source,
            "fields_updated": list(lead_data.keys()),
        },
    )


def get_conversation_events(thread_id: str) -> Optional[Dict[str, Any]]:
    """Recupera todos los eventos de una conversación.

    Args:
        thread_id: Identificador único de la conversación

    Returns:
        Diccionario con métricas y eventos, o None si no hay datos
    """
    try:
        thread_analytics_file = os.path.join(ANALYTICS_DIR, f"{thread_id}_events.json")

        if not os.path.exists(thread_analytics_file):
            return None

        with open(thread_analytics_file, "r", encoding="utf-8") as f:
            events = json.load(f)

        # Calcular algunas métricas básicas
        agent_assignments = {}
        lead_updates = 0

        for event in events:
            if event["event_type"] == "agent_assignment":
                agent = event["data"]["assigned_agent"]
                agent_assignments[agent] = agent_assignments.get(agent, 0) + 1
            elif event["event_type"] == "lead_update":
                lead_updates += 1

        return {
            "thread_id": thread_id,
            "total_events": len(events),
            "agent_assignments": agent_assignments,
            "lead_updates": lead_updates,
            "events": events,
        }
    except Exception as e:
        print(f"Error al recuperar eventos de conversación: {e}")
        return None
