"""Grafo principal para el asistente inmobiliario Inmobilia AI.

Este módulo define el grafo de conversación principal que coordina
los agentes especializados y el flujo de la conversación inmobiliaria.
"""

import os
from typing import Any, Dict

from langchain.globals import set_debug
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.agents.collector_agent import CollectorAgent
from src.agents.legal_agent import LegalAgent
from src.agents.location_agent import LocationAgent
from src.agents.preferences_agent import PreferencesAgent
from src.agents.supervisor_agent import SupervisorAgent
from src.config.settings import get_settings
from src.models.agent_state import AgentState
from src.services.lead_repository import save_lead_data

# Habilitar depuración si está especificado
if os.getenv("DEBUG", "False").lower() == "true":
    set_debug(True)

# Obtener configuración
settings = get_settings()

# Instanciar agentes
collector_agent = CollectorAgent(model_name=settings["apis"]["openai"]["model"])
legal_agent = LegalAgent(model_name=settings["apis"]["openai"]["model"])
location_agent = LocationAgent(model_name=settings["apis"]["openai"]["model"])
preferences_agent = PreferencesAgent(model_name=settings["apis"]["openai"]["model"])
supervisor_agent = SupervisorAgent(model_name=settings["apis"]["openai"]["model"])


# Definir herramientas para transferir entre agentes
def create_inmobilia_graph():
    """Crea el grafo de conversación para Inmobilia AI."""
    # Definir el grafo con el estado
    workflow = StateGraph(AgentState)

    # Añadir nodos para cada agente
    workflow.add_node("supervisor", supervisor_agent.router_node)
    workflow.add_node("legal", legal_agent.process_node)
    workflow.add_node("collector", collector_agent.process_node)
    workflow.add_node("location", location_agent.process_node)
    workflow.add_node("preferences", preferences_agent.process_node)

    # Configurar el punto de entrada - siempre empezamos con el supervisor
    workflow.set_entry_point("supervisor")

    # Añadir aristas condicionales desde el supervisor a cada agente
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_agent.decide_next_agent,
        {
            "legal": "legal",
            "collector": "collector",
            "location": "location",
            "preferences": "preferences",
            END: END,
        },
    )

    # Todos los agentes vuelven al supervisor después de procesar
    for node in ["legal", "collector", "location", "preferences"]:
        workflow.add_edge(node, "supervisor")

    return workflow


# Crear e instanciar el grafo
checkpointer = MemorySaver()
graph = create_inmobilia_graph().compile(checkpointer=checkpointer)


# Función para procesar mensajes
async def process_message(
    state: Dict[str, Any], message: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """Procesa un mensaje a través del grafo de conversación.

    Args:
        state: Estado actual de la conversación
        message: Mensaje del usuario
        config: Configuración del grafo (thread_id, etc.)

    Returns:
        Estado actualizado después de procesar el mensaje
    """
    # Actualizar estado con el mensaje actual
    state["current_message"] = message
    state["messages"] = state.get("messages", []) + [{"role": "user", "content": message}]

    try:
        # Procesar el mensaje a través del grafo
        result = await graph.ainvoke(state, {"configurable": config})

        # Guardar datos del lead si existen
        if "lead_obj" in result and result["lead_obj"]:
            thread_id = config.get("thread_id", "default")
            save_lead_data(thread_id, result["lead_obj"])

        return result
    except Exception as e:
        # Manejo de errores
        print(f"Error procesando mensaje: {str(e)}")
        state["error"] = "api_error"
        return state


# Función para inicializar la conversación
async def start_conversation() -> Dict[str, Any]:
    """Inicia una nueva conversación con un mensaje de bienvenida."""
    welcome_message = settings["agent_prompts"]["welcome"]

    # Estado inicial con mensaje de bienvenida
    initial_state = {
        "lead_data": {},
        "lead_obj": None,
        "messages": [{"role": "assistant", "content": welcome_message, "agent": "system"}],
        "last_agent_response": welcome_message,
        "current_agent": "supervisor",
    }

    return initial_state
