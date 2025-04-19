"""Agente especializado en recolectar datos básicos del usuario.

Este agente se encarga de obtener información esencial como nombre,
teléfono, email y otros datos básicos del usuario de manera conversacional.
"""

from typing import Any, Dict, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command


class CollectorAgent:
    """Agente especializado en recolectar datos básicos del usuario."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-latest"):
        """Inicializa el agente recolector."""
        self.model = ChatAnthropic(model=model_name, temperature=0.3)
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", COLLECTOR_PROMPT), ("human", "{input}")]
        )
        self.chat_history = []

    async def process_node(self, state: Dict[str, Any], config: RunnableConfig) -> Command:
        """Procesa el estado actual y genera una respuesta.

        Este método es compatible con el grafo LangGraph.

        Args:
            state: Estado actual del grafo
            config: Configuración del runnable

        Returns:
            Comando para actualizar el estado y navegar al siguiente nodo
        """
        # Obtener el mensaje actual
        current_message = state.get("current_message", "")
        lead_data = state.get("lead_data", {})

        # Procesar el mensaje
        response, updated_data = self.process_message(current_message, lead_data)

        # Actualizar historial de mensajes
        messages = state.get("messages", []).copy()
        messages.append({"role": "assistant", "content": response, "agent": "collector"})

        # Crear comando para actualizar estado y volver al supervisor
        return Command(
            goto="supervisor",
            update={
                "lead_data": updated_data,
                "messages": messages,
                "last_agent_response": response,
            },
        )

    def process_message(
        self, user_input: str, user_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Procesa el mensaje del usuario y genera una respuesta.

        Args:
            user_input: Mensaje del usuario
            user_data: Datos del usuario recolectados hasta el momento

        Returns:
            Tuple con la respuesta y los datos actualizados del usuario
        """
        # Actualizar historial con el mensaje del usuario
        self.chat_history.append({"role": "user", "content": user_input})

        # (Resto del código original del método)
        # ...
