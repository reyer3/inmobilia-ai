"""Agente especializado en recolectar datos básicos del usuario.

Este agente se encarga de obtener información esencial como nombre,
teléfono, email y otros datos básicos del usuario de manera conversacional.
"""

import re
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from src.models.lead_data import LeadData
from src.models.validators import validate_phone_number, validate_email


class CollectorAgent:
    """Agente especializado en recolectar datos básicos del usuario."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-latest"):
        """Inicializa el agente recolector."""
        self.model = ChatOpenAI(model=model_name, temperature=0.3)
        self.system_prompt = self._get_system_prompt()
        self.chat_history = []

    @staticmethod
    def _get_system_prompt() -> str:
        """Obtiene el prompt del sistema para el agente recolector."""
        return """
        Eres un agente especializado en recolectar información básica de clientes inmobiliarios en Perú.
        Tu objetivo es obtener datos esenciales del usuario de manera natural y conversacional.

        Datos prioritarios que debes obtener (si no los tiene ya):
        1. Nombre del cliente
        2. Número de celular o email para contacto

        Indicaciones importantes:
        - Sé amable y conversacional, evita sonar robótico o como un formulario.
        - Haz una pregunta a la vez, no bombardees al usuario con múltiples preguntas.
        - Si el usuario ya proporcionó algún dato, no vuelvas a solicitarlo.
        - Si el usuario se muestra reacio a compartir algún dato, no insistas y pasa al siguiente.
        - Prioriza obtener al menos un medio de contacto (celular o email).
        
        Analiza cuidadosamente los datos ya recolectados para evitar pedir información redundante.
        """

    async def process_node(self, state: Dict[str, Any], config: RunnableConfig) -> Command:
        """Procesa el estado actual y genera una respuesta.

        Este método es compatible con el grafo LangGraph.

        Args:
            state: Estado actual del grafo
            config: Configuración del runnable

        Returns:
            Comando para actualizar el estado y navegar al siguiente nodo
        """
        # Obtener el mensaje actual y datos existentes
        current_message = state.get("current_message", "")
        lead_data = state.get("lead_data", {})

        # Extraer nueva información del mensaje
        extracted_data = self._extract_data(current_message)

        # Actualizar datos
        updated_data = lead_data.copy()
        for key, value in extracted_data.items():
            if value and (key not in updated_data or not updated_data[key]):
                updated_data[key] = value

        # Generar una respuesta conversacional
        response = self._generate_response(current_message, updated_data)

        # Actualizar historial de mensajes
        messages = state.get("messages", []).copy()
        messages.append({"role": "assistant", "content": response, "agent": "collector"})

        # Actualizar el objeto lead si existe
        lead_obj = state.get("lead_obj")
        if lead_obj:
            lead_obj.update_from_dict(updated_data)
        else:
            lead_obj = LeadData(**updated_data)

        # Crear comando para actualizar estado y volver al supervisor
        return Command(
            goto="supervisor",
            update={
                "lead_data": updated_data,
                "lead_obj": lead_obj,
                "messages": messages,
                "last_agent_response": response,
                "last_agent": "collector"
            }
        )

    @staticmethod
    def _extract_data(text: str) -> Dict[str, Any]:
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
            email = email_match.group(0)
            if validate_email(email):
                extracted["email"] = email

        # Extraer número de celular (formato peruano)
        phone_pattern = r"(?:\+51|51|9)[0-9]{8,9}"
        phone_match = re.search(phone_pattern, text.replace(" ", ""))
        if phone_match:
            phone = phone_match.group(0)
            if validate_phone_number(phone):
                extracted["celular"] = phone

        return extracted

    def _generate_response(self, user_message: str, lead_data: Dict[str, Any]) -> str:
        """Genera una respuesta basada en el mensaje del usuario y los datos del lead.

        Args:
            user_message: Mensaje del usuario
            lead_data: Datos actuales del lead

        Returns:
            Respuesta generada
        """
        # Analizar qué datos faltan
        missing_data = self._get_missing_data(lead_data)

        # Construir mensajes para el LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Datos ya recolectados: {self._format_lead_data(lead_data)}"},
            {"role": "system", "content": f"Datos faltantes prioritarios: {', '.join(missing_data) if missing_data else 'Ninguno'}"},
            {"role": "user", "content": user_message}
        ]

        # Generar respuesta
        response = self.model.invoke(messages)
        return response.content

    @staticmethod
    def _get_missing_data(lead_data: Dict[str, Any]) -> List[str]:
        """Identifica qué datos prioritarios faltan.

        Args:
            lead_data: Datos actuales del lead

        Returns:
            Lista de nombres de campos faltantes
        """
        missing = []

        # Verificar datos prioritarios
        if not lead_data.get("nombre"):
            missing.append("nombre")

        # Verificar al menos un contacto
        if not lead_data.get("celular") and not lead_data.get("email"):
            missing.append("contacto (celular o email)")

        return missing

    @staticmethod
    def _format_lead_data(data: Dict[str, Any]) -> str:
        """Formatea los datos del lead para incluirlos en el prompt.

        Args:
            data: Datos del lead

        Returns:
            String con los datos formateados
        """
        if not data:
            return "No se han recolectado datos todavía."

        formatted = ""
        for key, value in data.items():
            if value is not None:
                formatted += f"- {key}: {value}\n"

        return formatted or "No hay datos relevantes aún."