"""Agente supervisor que coordina la conversación inmobiliaria.

Este agente determina cuál de los agentes especializados debe manejar cada mensaje,
basándose en el contexto de la conversación y el estado del lead.
"""

from typing import Any, Dict, Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command


class RouterResponse(TypedDict):
    """Respuesta del supervisor para ruteo."""

    next: Literal["legal", "collector", "location", "preferences", "END"]
    reasoning: str


class SupervisorAgent:
    """Agente supervisor que coordina la conversación inmobiliaria."""

    def __init__(self, model_name: str = "claude-3-7-sonnet-latest"):
        """Inicializa el agente supervisor.

        Args:
            model_name: Nombre del modelo a utilizar
        """
        self.model = ChatAnthropic(model=model_name, temperature=0.2)
        self.prompt = SUPERVISOR_PROMPT  # Definir un prompt que guíe las decisiones

    async def router_node(self, state: Dict[str, Any], config: RunnableConfig) -> Command:
        """Nodo que determina qué agente debe manejar el mensaje actual.

        Args:
            state: Estado actual del grafo
            config: Configuración del runnable

        Returns:
            Comando indicando el siguiente agente
        """
        messages = [
            {"role": "system", "content": self.prompt},
        ] + state["messages"]

        # Añadir contexto sobre los datos ya recolectados
        lead_data_summary = self._format_lead_data(state.get("lead_data", {}))
        messages.append({"role": "system", "content": f"Datos del lead:\n{lead_data_summary}"})

        # Determinar el siguiente agente
        response = self.model.with_structured_output(RouterResponse).invoke(messages)
        next_agent = response["next"]

        if next_agent == "END":
            return Command(goto="__end__")

        return Command(goto=next_agent, update={"current_agent": next_agent})

    def decide_next_agent(self, state: Dict[str, Any]) -> str:
        """Función de decisión para el grafo condicional.

        Args:
            state: Estado actual del grafo

        Returns:
            Nombre del siguiente agente
        """
        return state.get("current_agent", "supervisor")

    def _format_lead_data(self, lead_data: Dict[str, Any]) -> str:
        """Formatea los datos del lead para incluirlos en el prompt."""
        if not lead_data:
            return "No se han recolectado datos todavía."

        formatted = ""
        for key, value in lead_data.items():
            if value is not None:
                formatted += f"- {key}: {value}\n"

        return formatted
