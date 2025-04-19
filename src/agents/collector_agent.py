"""Agente especializado en recolectar datos básicos del usuario.

Este agente se encarga de obtener información esencial como nombre,
teléfono, email y otros datos básicos del usuario de manera conversacional.
"""

import re
from typing import Any, Dict, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

COLLECTOR_PROMPT = """
Eres un agente especializado en recolectar información básica de clientes inmobiliarios en Perú.
Tu objetivo es obtener datos esenciales del usuario de manera natural y conversacional.

Datos prioritarios que debes obtener (en orden):
1. Nombre del cliente
2. Número de celular o email para contacto
3. Tipo de documento y número (DNI, CE, pasaporte)

Indicaciones importantes:
- Sé amable y conversacional, evita sonar robótico o como un formulario.
- Haz una pregunta a la vez, no bombardees al usuario con múltiples preguntas.
- Si el usuario ya proporcionó algún dato, no vuelvas a solicitarlo.
- Si el usuario se muestra reacio a compartir algún dato, no insistas y pasa al siguiente.
- Prioriza obtener al menos un medio de contacto (celular o email).

Historial de la conversación:
{chat_history}

Datos ya recolectados:
{collected_data}

Mensaje del usuario: {input}

Responde de manera natural, extraye cualquier información relevante, y pregunta por el siguiente dato faltante prioritario.
"""


class CollectorAgent:
    """Agente especializado en recolectar datos básicos del usuario."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-latest", temperature: float = 0.3):
        """Inicializa el agente recolector."""
        self.model = ChatAnthropic(model=model_name, temperature=temperature)
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

        # Extraer información del mensaje
        extracted_data = self._extract_data(user_input)
        for key, value in extracted_data.items():
            if value and (key not in user_data or not user_data[key]):
                user_data[key] = value

        # Formatear los datos recolectados para el prompt
        collected_data_str = self._format_collected_data(user_data)

        # Generar respuesta
        response = self.model.invoke(
            self.prompt.format(
                input=user_input,
                chat_history=self._format_history(),
                collected_data=collected_data_str,
            )
        )

        # Actualizar historial con la respuesta
        self.chat_history.append({"role": "assistant", "content": response.content})

        return response.content, user_data

    def _extract_data(self, text: str) -> Dict[str, Any]:
        """Extrae datos personales del texto del usuario."""
        extracted = {}

        # Extraer nombre (palabras que empiezan con mayúscula, precedidas por "me llamo", "soy", "mi nombre es")
        name_patterns = [
            r"(?:me llamo|soy|mi nombre es)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})",
            r"(?:^|\s)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})(?:\s+me llamo|\s+es mi nombre)",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                extracted["nombre"] = match.group(1).strip()
                break

        # Extraer email
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        if email_match:
            extracted["email"] = email_match.group(0)

        # Extraer número de celular (formato peruano)
        phone_match = re.search(r"(?:\+51|51|9)[0-9]{8,9}", text.replace(" ", ""))
        if phone_match:
            extracted["celular"] = phone_match.group(0)

        # Extraer DNI (8 dígitos)
        dni_match = re.search(r"(?:DNI|dni)\s*[:\-]?\s*([0-9]{8})", text)
        if dni_match:
            extracted["tipo_documento"] = "dni"
            extracted["numero_documento"] = dni_match.group(1)

        # Extraer Carnet de Extranjería
        ce_match = re.search(r"(?:CE|ce|carnet)\s*[:\-]?\s*([A-Z0-9]{9,12})", text)
        if ce_match:
            extracted["tipo_documento"] = "ce"
            extracted["numero_documento"] = ce_match.group(1)

        return extracted

    def _format_collected_data(self, data: Dict[str, Any]) -> str:
        """Formatea los datos recolectados para incluirlos en el prompt."""
        if not data:
            return "No se han recolectado datos todavía."

        # Mapeo de claves a nombres más amigables
        key_mapping = {
            "nombre": "Nombre",
            "email": "Email",
            "celular": "Celular",
            "tipo_documento": "Tipo de documento",
            "numero_documento": "Número de documento",
        }

        # Filtrar solo las claves que nos interesan
        relevant_keys = [k for k in key_mapping.keys() if k in data and data[k]]

        if not relevant_keys:
            return "No se han recolectado datos relevantes todavía."

        # Formatear los datos
        formatted = ""
        for key in relevant_keys:
            formatted += f"- {key_mapping[key]}: {data[key]}\n"

        return formatted

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

    # Métodos adicionales para integración con herramientas (alineado con LangGraph)

    def get_tools(self):
        """Retorna las herramientas que este agente puede utilizar.

        Permite la integración con create_react_agent de LangGraph.
        """
        from src.agents.extractors import ExtractorTools
        from src.agents.validators import ValidationTools

        extractors = ExtractorTools()
        validators = ValidationTools()

        return [
            extractors.extract_name,
            extractors.extract_contact,
            validators.validate_phone_number,
            validators.validate_email,
        ]

    def get_prompt(self):
        """Retorna el prompt base para este agente.

        Facilita la integración con create_react_agent.
        """
        return COLLECTOR_PROMPT
