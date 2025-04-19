"""Grafo principal del asistente inmobiliario con enfoque no secuencial.

Este módulo define un grafo de conversación que utiliza un supervisor para orquestar
múltiples agentes especializados, permitiendo una recolección no secuencial de datos.
"""

import os
from typing import Dict, Any, Optional

from langchain.globals import set_debug
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from src.agents.collector_agent import CollectorAgent
from src.agents.legal_agent import LegalAgent
from src.agents.location_agent import LocationAgent
from src.agents.preferences_agent import PreferencesAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.config.settings import get_settings
from src.models.agent_state import AgentState, get_initial_state
from src.services.lead_repository import save_lead_data
from src.services.analytics_client import track_agent_assignment, track_lead_update

# Habilitar depuración si está configurado
if os.getenv("DEBUG", "False").lower() == "true":
    set_debug(True)

# Obtener configuración
settings = get_settings()


def create_inmobilia_graph():
    """Crea el grafo de conversación no secuencial para Inmobilia AI.

    Este grafo implementa un enfoque dinámico donde el supervisor analiza
    cada mensaje y determina qué agente debe manejarlo, sin un flujo secuencial.

    Returns:
        Grafo compilado listo para ser ejecutado
    """
    # Instanciar agentes
    supervisor = SupervisorAgent(model_name=settings["apis"]["anthropic"]["model"])
    legal_agent = LegalAgent(model_name=settings["apis"]["anthropic"]["model"])
    collector_agent = CollectorAgent(model_name=settings["apis"]["anthropic"]["model"])
    location_agent = LocationAgent(model_name=settings["apis"]["anthropic"]["model"])
    preferences_agent = PreferencesAgent(model_name=settings["apis"]["anthropic"]["model"])

    # Definir el grafo con el estado
    workflow = StateGraph(AgentState)

    # Añadir nodos para cada agente
    workflow.add_node("supervisor", supervisor.router_node)
    workflow.add_node("legal", legal_agent.process_node)
    workflow.add_node("collector", collector_agent.process_node)
    workflow.add_node("location", location_agent.process_node)
    workflow.add_node("preferences", preferences_agent.process_node)

    # Establecer el punto de entrada
    workflow.add_edge(START, "supervisor")

    # Todas las decisiones de enrutamiento se toman en el supervisor
    workflow.add_conditional_edges(
        "supervisor",
        supervisor.decide_next_agent,
        {
            "legal": "legal",
            "collector": "collector",
            "location": "location",
            "preferences": "preferences",
            END: END,
        }
    )

    # Todos los agentes vuelven al supervisor después de procesar
    for agent_name in ["legal", "collector", "location", "preferences"]:
        workflow.add_edge(agent_name, "supervisor")

    return workflow.compile(checkpointer=MemorySaver())


# Instanciar el grafo
graph = create_inmobilia_graph()


async def process_message(
    state: Dict[str, Any],
    message: str,
    session_id: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Procesa un mensaje a través del grafo conversacional de manera no secuencial.

    Esta función es el punto de entrada para utilizar el grafo desde la API.

    Args:
        state: Estado actual de la conversación
        message: Mensaje del usuario
        session_id: ID de la sesión
        user_id: ID opcional del usuario

    Returns:
        Estado actualizado después de procesar el mensaje
    """
    # Inicializar estado si es la primera vez
    if not state:
        state = get_initial_state(message, session_id, user_id)
    else:
        # Actualizar estado con el mensaje actual
        state["current_message"] = message
        state["messages"].append({"role": "user", "content": message})

    try:
        # Configuración para el grafo
        config = {
            "thread_id": session_id,
            "user_id": user_id or session_id,
            "timestamp": state.get("conversation_start_time")
        }

        # Procesar el mensaje a través del grafo
        result = await graph.ainvoke(state, {"configurable": config})

        # Registrar qué agente manejó el mensaje para analíticas
        if "current_agent" in result and result["current_agent"] != state.get("last_agent"):
            track_agent_assignment(
                thread_id=session_id,
                user_message=message,
                assigned_agent=result["current_agent"]
            )

            # Actualizar último agente en el estado
            result["last_agent"] = result["current_agent"]

        # Guardar datos del lead si existen
        if "lead_obj" in result and result["lead_obj"]:
            save_lead_data(session_id, result["lead_obj"])

            # Registrar actualización del lead
            track_lead_update(
                thread_id=session_id,
                lead_data=result["lead_obj"].to_dict(),
                source=result.get("current_agent", "system")
            )

        return result
    except Exception as e:
        # Manejo de errores
        print(f"Error procesando mensaje: {str(e)}")
        state["error"] = str(e)
        return state


async def start_conversation(session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Inicia una nueva conversación con un mensaje de bienvenida.

    Args:
        session_id: ID de la sesión
        user_id: ID opcional del usuario

    Returns:
        Estado inicial de la conversación
    """
    welcome_message = settings["agent_prompts"]["welcome"]

    # Crear estado inicial
    initial_state = get_initial_state("", session_id, user_id)

    # Añadir mensaje de bienvenida
    initial_state["messages"].append({"role": "assistant", "content": welcome_message})
    initial_state["last_response"] = welcome_message
    
    return initial_state