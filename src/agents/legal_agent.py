"""Agente especializado en aspectos legales y cumplimiento normativo.

Este agente se encarga de gestionar el consentimiento de datos personales
de acuerdo con la Ley 29733 de Protección de Datos Personales de Perú.
"""

from datetime import datetime
from typing import Any, Dict, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

LEGAL_PROMPT = """
Eres un agente especializado en aspectos legales para un asistente inmobiliario en Perú.
Tu principal responsabilidad es asegurar el cumplimiento de la Ley 29733 de Protección de Datos Personales.

Prioridades:
1. Solicitar y confirmar consentimiento explícito para procesar datos personales.
2. Explicar de forma sencilla cómo se usarán los datos proporcionados.
3. Informar sobre derechos ARCO (Acceso, Rectificación, Cancelación y Oposición).

Importante:
- NO puedes recolectar datos personales sin antes obtener consentimiento explícito.
- Debes explicar que los datos serán usados para buscar propiedades que se ajusten a las necesidades del usuario.
- El tono debe ser profesional pero accesible y respetuoso.
- Las respuestas deben ser breves y naturales, sin tecnicismos excesivos.

Historial de la conversación:
{chat_history}

Mensaje del usuario: {input}

Recuerda: si el usuario no ha dado consentimiento, debes solicitarlo antes de continuar.
"""


class LegalAgent:
    """Agente especializado en aspectos legales y cumplimiento normativo."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-latest", temperature: float = 0.2):
        """Inicializa el agente legal.

        Args:
            model_name: Nombre del modelo de Claude a utilizar
            temperature: Temperatura para la generación de texto
        """
        self.model = ChatAnthropic(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", LEGAL_PROMPT), ("human", "{input}")]
        )
        self.chat_history = []
        self.consent_obtained = False

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
        messages.append({"role": "assistant", "content": response, "agent": "legal"})

        # Verificar si el objeto lead_obj ya existe
        lead_obj = state.get("lead_obj")
        if lead_obj:
            lead_obj.update_from_dict(updated_data)
        else:
            from src.models.lead_data import LeadData

            lead_obj = LeadData(**updated_data)

        # Crear comando para actualizar estado y volver al supervisor
        return Command(
            goto="supervisor",
            update={
                "lead_data": updated_data,
                "lead_obj": lead_obj,
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

        # Verificar si ya tenemos consentimiento
        if user_data.get("consentimiento") is True:
            self.consent_obtained = True

        # Generar respuesta
        response = self.model.invoke(
            self.prompt.format(input=user_input, chat_history=self._format_history())
        )

        # Actualizar historial con la respuesta
        self.chat_history.append({"role": "assistant", "content": response.content})

        # Analizar si la respuesta del usuario indica consentimiento
        if not self.consent_obtained:
            consent_words = ["si", "sí", "acepto", "autorizo", "de acuerdo", "ok", "claro"]
            if any(word in user_input.lower() for word in consent_words):
                self.consent_obtained = True
                user_data["consentimiento"] = True
                user_data["fecha_consentimiento"] = datetime.now().isoformat()

        return response.content, user_data

    def _format_history(self) -> str:
        """Formatea el historial de conversación para incluirlo en el prompt."""
        if not self.chat_history:
            return ""

        formatted_history = ""
        for msg in self.chat_history[-6:]:  # Limitamos a los últimos 6 mensajes
            role = "Usuario" if msg["role"] == "user" else "Asistente"
            formatted_history += f"{role}: {msg['content']}\n\n"

        return formatted_history

    def reset(self) -> None:
        """Reinicia el estado del agente."""
        self.chat_history = []
        self.consent_obtained = False

    # Métodos adicionales para integración con herramientas (alineado con LangGraph)

    def get_tools(self):
        """Retorna las herramientas que este agente puede utilizar."""
        from src.agents.validators import ValidationTools

        validators = ValidationTools()

        return [
            validators.check_consent,
            validators.validate_consent,
        ]

    def get_prompt(self):
        """Retorna el prompt base para este agente."""
        return LEGAL_PROMPT
