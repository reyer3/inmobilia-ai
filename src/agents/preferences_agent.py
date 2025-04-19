"""Agente especializado en capturar preferencias inmobiliarias.

Este agente se enfoca en obtener detalles específicos sobre el tipo
de inmueble que busca el usuario, sus características, presupuesto y otros requisitos.
"""

import re
from datetime import datetime
from typing import Any, Dict, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

PREFERENCES_PROMPT = """
Eres un agente especializado en capturar preferencias inmobiliarias en Perú.
Tu objetivo es obtener detalles específicos sobre el tipo de propiedad que el usuario está buscando.

Preferencias que debes capturar (en orden de prioridad):
1. Tipo de inmueble (departamento, casa, terreno, oficina, etc.)
2. Presupuesto aproximado (mínimo y/o máximo)
3. Metraje deseado
4. Número de habitaciones y baños
5. Características específicas (estacionamiento, áreas comunes, etc.)
6. Antigüedad de la propiedad (nuevo, de estreno, segunda mano, etc.)
7. Plazo para la compra/alquiler

Indicaciones importantes:
- Sé conversacional y natural, no interrogatorio.
- Haz una pregunta a la vez enfocándote en las más prioritarias primero.
- Si el usuario ya mencionó alguna preferencia, considérala y no la preguntes de nuevo.
- Ayuda al usuario a definir sus preferencias si están ambiguas (ej. si dice "barato", pregunta por un rango específico).
- Adapta las preguntas al contexto de Perú (moneda en soles, zonas peruanas, etc.).

Historial de la conversación:
{chat_history}

Preferencias ya conocidas:
{known_preferences}

Mensaje del usuario: {input}

Responde de manera natural y pregunta por la siguiente preferencia prioritaria que falte.
"""


class PreferencesAgent:
    """Agente especializado en capturar preferencias inmobiliarias."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-latest", temperature: float = 0.3):
        """Inicializa el agente de preferencias.

        Args:
            model_name: Nombre del modelo de Claude a utilizar
            temperature: Temperatura para la generación de texto
        """
        self.model = ChatAnthropic(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", PREFERENCES_PROMPT), ("human", "{input}")]
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
        messages.append({"role": "assistant", "content": response, "agent": "preferences"})

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

        # Extraer preferencias del mensaje
        preferences = self._extract_preferences(user_input)
        for key, value in preferences.items():
            if value and (key not in user_data or not user_data[key]):
                user_data[key] = value

        # Formatear las preferencias conocidas para el prompt
        preferences_str = self._format_preferences(user_data)

        # Generar respuesta
        response = self.model.invoke(
            self.prompt.format(
                input=user_input,
                chat_history=self._format_history(),
                known_preferences=preferences_str,
            )
        )

        # Actualizar historial con la respuesta
        self.chat_history.append({"role": "assistant", "content": response.content})

        # Actualizar la fecha de última interacción
        user_data["ultima_interaccion"] = datetime.now().isoformat()

        return response.content, user_data

    def _extract_preferences(self, text: str) -> Dict[str, Any]:
        """Extrae preferencias inmobiliarias del texto del usuario."""
        preferences = {}

        # Extraer tipo de inmueble
        property_types = {
            "departamento": ["departamento", "depa", "flat", "apartamento"],
            "casa": ["casa", "chalet", "vivienda"],
            "terreno": ["terreno", "lote", "parcela"],
            "oficina": ["oficina", "local comercial", "espacio comercial"],
            "casa de playa": ["casa de playa", "casa en la playa"],
        }

        for prop_type, keywords in property_types.items():
            if any(keyword in text.lower() for keyword in keywords):
                preferences["tipo_inmueble"] = prop_type
                break

        # Extraer metraje
        metraje_patterns = [
            r"([0-9]+)\s*m2",
            r"([0-9]+)\s*metros cuadrados",
            r"([0-9]+)\s*metros",
        ]

        for pattern in metraje_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    preferences["metraje"] = int(match.group(1))
                    break
                except ValueError:
                    pass

        # Extraer número de habitaciones
        habitaciones_patterns = [
            r"([0-9]+)\s*habitaci[oó]n",
            r"([0-9]+)\s*habitaciones",
            r"([0-9]+)\s*cuartos",
            r"([0-9]+)\s*dormitorios",
            r"([0-9]+)\s*dorm",
        ]

        for pattern in habitaciones_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    preferences["habitaciones"] = int(match.group(1))
                    break
                except ValueError:
                    pass

        # Extraer presupuesto
        # Patrones para capturar presupuesto en diferentes formatos (soles o dólares)
        precio_patterns = [
            # Formato $X,XXX o $X.XXX
            r"\$\s*([0-9]{1,3}(?:[,.][0-9]{3})*(?:\.[0-9]+)?)",
            # Formato S/X,XXX o S/.X,XXX
            r"S/\.?\s*([0-9]{1,3}(?:[,.][0-9]{3})*(?:\.[0-9]+)?)",
            # Formato X,XXX soles
            r"([0-9]{1,3}(?:[,.][0-9]{3})*(?:\.[0-9]+)?)\s*(?:soles|sol)",
            # Formato X,XXX dólares/USD
            r"([0-9]{1,3}(?:[,.][0-9]{3})*(?:\.[0-9]+)?)\s*(?:d[oó]lares|usd)",
        ]

        for pattern in precio_patterns:
            matches = re.finditer(pattern, text.lower())
            prices = []

            for match in matches:
                try:
                    # Limpiar el número (quitar comas y convertir a float)
                    price_str = match.group(1).replace(",", "")
                    price = float(price_str)
                    prices.append(price)
                except (ValueError, IndexError):
                    continue

            if len(prices) == 1:
                # Si solo hay un precio, asumimos que es el máximo
                preferences["presupuesto_max"] = prices[0]
            elif len(prices) >= 2:
                # Si hay dos o más, asumimos min y max
                preferences["presupuesto_min"] = min(prices)
                preferences["presupuesto_max"] = max(prices)

            if prices:  # Si encontramos al menos un precio, salimos del bucle
                break

        # Detectar si menciona plazos
        timeline_patterns = {
            "inmediato": ["inmediato", "urgente", "ya mismo", "cuanto antes"],
            "1-3 meses": ["próximo mes", "siguiente mes", "pronto", "en unas semanas"],
            "3-6 meses": ["en unos meses", "mediano plazo"],
            "6+ meses": ["largo plazo", "fin de año", "próximo año"],
        }

        for timeline, keywords in timeline_patterns.items():
            if any(keyword in text.lower() for keyword in keywords):
                preferences["timeline_compra"] = timeline
                break

        return preferences

    def _format_preferences(self, data: Dict[str, Any]) -> str:
        """Formatea las preferencias conocidas para incluirlas en el prompt."""
        if not data:
            return "No se conocen preferencias del usuario todavía."

        relevant_keys = [
            "tipo_inmueble",
            "presupuesto_min",
            "presupuesto_max",
            "metraje",
            "habitaciones",
            "distrito",
            "timeline_compra",
        ]

        # Mapeo de claves a nombres más amigables
        key_mapping = {
            "tipo_inmueble": "Tipo de inmueble",
            "presupuesto_min": "Presupuesto mínimo",
            "presupuesto_max": "Presupuesto máximo",
            "metraje": "Metraje aproximado",
            "habitaciones": "Número de habitaciones",
            "distrito": "Distrito de interés",
            "timeline_compra": "Plazo para la compra",
        }

        # Filtrar solo las claves relevantes que existen en los datos
        existing_keys = [k for k in relevant_keys if k in data and data[k]]

        if not existing_keys:
            return "No se conocen preferencias inmobiliarias del usuario todavía."

        # Formatear los datos
        formatted = ""
        for key in existing_keys:
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
        """Retorna las herramientas que este agente puede utilizar."""
        from src.agents.extractors import ExtractorTools

        extractors = ExtractorTools()

        return [
            extractors.extract_property_type,
            extractors.extract_habitaciones,
            extractors.extract_presupuesto,
            extractors.extract_timeline,
        ]

    def get_prompt(self):
        """Retorna el prompt base para este agente."""
        return PREFERENCES_PROMPT
