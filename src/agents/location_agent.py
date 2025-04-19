"""Agente especializado en ubicaciones inmobiliarias en Perú.

Este agente maneja consultas relacionadas con distritos, zonas,
y ubicaciones específicas en Perú, con enfoque en Lima Metropolitana.
"""

from typing import Any, Dict, Optional, Tuple, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI  # Cambiado de ChatAnthropic
from langgraph.types import Command

from src.models.lead_data import LeadData


class LocationInfo(TypedDict):
    """Información de ubicación extraída del mensaje."""
    distrito: Optional[str]
    zona: Optional[str]


LOCATION_PROMPT = """
Eres un agente especializado en ubicaciones inmobiliarias en Perú, con énfasis en Lima Metropolitana.
Tu objetivo es ayudar al usuario a identificar zonas o distritos que se ajusten a sus necesidades.

Conocimientos que debes dominar:
1. Distritos de Lima y sus características (precio, seguridad, accesibilidad, etc.)
2. Principales ciudades de Perú y sus zonas residenciales
3. Tendencias inmobiliarias por ubicación
4. Conectividad y transporte entre zonas

Cuando interactúes con el usuario:
- Pregunta por sus preferencias en cuanto a ubicación
- Ayúdalo a definir el distrito o zona que mejor se ajuste a sus necesidades
- Ofrece información relevante sobre las zonas mencionadas (brevemente)
- Evita incluir datos precisos de precios, pero sí puedes mencionar si una zona es económica, media o exclusiva

Los principales distritos de Lima son:
- Lima Moderna: Miraflores, San Isidro, Barranco, San Borja, Surco, La Molina (zonas exclusivas y de alto valor)
- Lima Centro: Jesús María, Lince, Pueblo Libre, Magdalena, San Miguel (zonas de valor medio-alto)
- Lima Norte: Los Olivos, Independencia, San Martín de Porres (zonas de valor medio-bajo)
- Lima Sur: Villa El Salvador, San Juan de Miraflores, Villa María del Triunfo (zonas de valor medio-bajo)
- Lima Este: Ate, Santa Anita, La Molina (zonas mixtas, desde exclusivas hasta económicas)

Historial de la conversación:
{chat_history}

Preferencias conocidas del usuario:
{user_preferences}

Mensaje del usuario: {input}

Responde de manera concisa y natural, enfocándote en ayudar al usuario a definir la ubicación ideal para su búsqueda inmobiliaria.
"""


class LocationAgent:
    """Agente especializado en ubicaciones inmobiliarias en Perú."""

    def __init__(self, model_name: str = "gpt-4-1106-preview", temperature: float = 0.3):
        """Inicializa el agente de ubicaciones.

        Args:
            model_name: Nombre del modelo a utilizar
            temperature: Temperatura para la generación de texto
        """
        self.model = ChatOpenAI(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", LOCATION_PROMPT), ("human", "{input}")]
        )
        self.chat_history = []

        # Definir distritos para uso en extracción estructurada
        self.distritos = [
            "Miraflores", "San Isidro", "Barranco", "San Borja", "Surco", "La Molina",
            "Jesús María", "Lince", "Pueblo Libre", "Magdalena", "San Miguel",
            "Los Olivos", "Independencia", "San Martín de Porres",
            "Villa El Salvador", "San Juan de Miraflores", "Villa María del Triunfo",
            "Ate", "Santa Anita", "Chorrillos", "Breña", "Rímac", "Cercado de Lima",
            "La Victoria", "San Juan de Lurigancho", "Comas", "Carabayllo",
            "San Luis", "El Agustino", "Santa Rosa", "Ancón", "Puente Piedra",
            "Lurigancho", "Pachacámac", "San Bartolo", "Punta Hermosa",
            "Punta Negra", "Santa María del Mar", "Pucusana", "Lurín", "Cieneguilla",
        ]

        # Definir zonas para uso en extracción estructurada
        self.lima_zonas = {
            "lima moderna": [
                "Miraflores", "San Isidro", "Barranco", "San Borja", "Surco", "La Molina",
            ],
            "lima centro": ["Jesús María", "Lince", "Pueblo Libre", "Magdalena", "San Miguel"],
            "lima norte": [
                "Los Olivos", "Independencia", "San Martín de Porres", "Comas", "Carabayllo",
            ],
            "lima sur": [
                "Villa El Salvador", "San Juan de Miraflores", "Villa María del Triunfo", "Chorrillos",
            ],
            "lima este": ["Ate", "Santa Anita", "La Molina", "San Juan de Lurigancho"],
        }

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
        messages.append({"role": "assistant", "content": response, "agent": "location"})

        # Verificar si el objeto lead_obj ya existe
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

        # Extraer información sobre ubicación
        location_info = self._extract_location_structured(user_input)
        for key, value in location_info.items():
            if value and (key not in user_data or not user_data[key]):
                user_data[key] = value

        # Formatear las preferencias del usuario para el prompt
        preferences_str = self._format_preferences(user_data)

        # Generar respuesta
        response = self.model.invoke(
            self.prompt.format(
                input=user_input,
                chat_history=self._format_history(),
                user_preferences=preferences_str,
            )
        )

        # Actualizar historial con la respuesta
        self.chat_history.append({"role": "assistant", "content": response.content})

        return response.content, user_data

    def _extract_location_structured(self, text: str) -> Dict[str, Any]:
        """Extrae información sobre ubicación del texto del usuario usando un enfoque estructurado."""
        # Definir la estructura de salida esperada
        structured_output_prompt = f"""
        Analiza este texto y extrae información sobre ubicaciones en Lima, Perú.
        
        Texto: "{text}"
        
        Responde SOLO con un JSON que contenga estos campos:
        - distrito: El distrito de Lima mencionado, o null si no se menciona
        - zona: La zona de Lima mencionada (lima moderna, lima centro, lima norte, lima sur, lima este), o null si no se menciona
        
        Distritos válidos: {", ".join(self.distritos)}
        Zonas válidas: {", ".join(self.lima_zonas.keys())}
        """

        try:
            # Usar el modelo para extraer la información estructurada
            extraction_response = self.model.with_structured_output(LocationInfo).invoke(
                [{"role": "user", "content": structured_output_prompt}]
            )

            # Validar la extracción
            location_info = {}
            if extraction_response.get("distrito") and extraction_response["distrito"] in self.distritos:
                location_info["distrito"] = extraction_response["distrito"]

            if extraction_response.get("zona") and extraction_response["zona"] in self.lima_zonas.keys():
                location_info["zona"] = extraction_response["zona"]

            return location_info
        except (ValueError, KeyError, AttributeError):
            # Si hay un error, utilizar el método de extracción basado en reglas como fallback
            return self._extract_location_fallback(text)

    def _extract_location_fallback(self, text: str) -> Dict[str, Any]:
        """Método de respaldo para extraer información sobre ubicación basado en reglas."""
        location_info = {}
        text_lower = text.lower()

        # Verificar si menciona algún distrito específico
        for distrito in self.distritos:
            if distrito.lower() in text_lower:
                location_info["distrito"] = distrito
                break

        # Verificar si menciona alguna zona genérica
        for zona in self.lima_zonas.keys():
            if zona in text_lower:
                location_info["zona"] = zona
                break

        return location_info

    def _format_preferences(self, data: Dict[str, Any]) -> str:
        """Formatea las preferencias del usuario para incluirlas en el prompt."""
        if not data:
            return "No se conocen preferencias del usuario todavía."

        relevant_keys = [
            "tipo_inmueble",
            "distrito",
            "zona",
            "presupuesto_min",
            "presupuesto_max",
            "habitaciones",
            "metraje",
        ]

        # Mapeo de claves a nombres más amigables
        key_mapping = {
            "tipo_inmueble": "Tipo de inmueble",
            "distrito": "Distrito de interés",
            "zona": "Zona de interés",
            "presupuesto_min": "Presupuesto mínimo",
            "presupuesto_max": "Presupuesto máximo",
            "habitaciones": "Número de habitaciones",
            "metraje": "Metraje aproximado",
        }

        # Filtrar solo las claves relevantes que existen en los datos
        existing_keys = [k for k in relevant_keys if k in data and data[k]]

        if not existing_keys:
            return "No se conocen preferencias de ubicación del usuario todavía."

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

    def get_prompt(self) -> str:
        """Retorna el prompt base para este agente."""
        return LOCATION_PROMPT