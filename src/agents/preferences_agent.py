"""Agente especializado en capturar preferencias inmobiliarias.

Este agente se enfoca en obtener detalles específicos sobre el tipo
de inmueble que busca el usuario, sus características, presupuesto y otros requisitos.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from pydantic import BaseModel, Field


# Modelos para estructurar la extracción
class PropertyPreference(BaseModel):
    """Modelo para estructurar las preferencias inmobiliarias extraídas."""

    tipo_inmueble: Optional[str] = Field(None, description="Tipo de inmueble buscado (departamento, casa, etc.)")
    presupuesto_min: Optional[float] = Field(None, description="Presupuesto mínimo en la moneda mencionada")
    presupuesto_max: Optional[float] = Field(None, description="Presupuesto máximo en la moneda mencionada")
    moneda: Optional[str] = Field(None, description="Moneda del presupuesto (soles, dólares)")
    metraje: Optional[int] = Field(None, description="Metraje deseado en metros cuadrados")
    habitaciones: Optional[int] = Field(None, description="Número de habitaciones deseadas")
    distrito: Optional[str] = Field(None, description="Distrito o zona preferida")
    timeline_compra: Optional[str] = Field(None, description="Plazo para la compra o alquiler")

    class Config:
        extra = "ignore"


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

# Prompt para extraer preferencias estructuradas
EXTRACTION_PROMPT = """
Extrae las preferencias inmobiliarias mencionadas en el mensaje del usuario y estructúralas 
según el formato solicitado. Solo incluye lo explícitamente mencionado en este mensaje, 
no información de mensajes anteriores.

Mensaje del usuario: {text}

Detecta las siguientes categorías si están presentes:
- tipo_inmueble: El tipo de propiedad mencionado (departamento, casa, terreno, etc.)
- presupuesto_min: El monto mínimo del presupuesto en números
- presupuesto_max: El monto máximo del presupuesto en números
- moneda: La moneda mencionada (soles, dólares, etc.)
- metraje: El tamaño en metros cuadrados como número entero
- habitaciones: La cantidad de habitaciones como número entero
- distrito: El distrito o zona mencionada de Lima/Perú
- timeline_compra: Plazo para comprar (inmediato, 1-3 meses, 3-6 meses, 6+ meses)

Responde solo con los datos encontrados, omitiendo los campos no mencionados.
"""


class PreferencesAgent:
    """Agente especializado en capturar preferencias inmobiliarias."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-latest", temperature: float = 0.3):
        """Inicializa el agente de preferencias.

        Args:
            model_name: Nombre del modelo de Claude a utilizar
            temperature: Temperatura para la generación de texto
        """
        self.model = ChatOpenAI(model=model_name, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", PREFERENCES_PROMPT), ("human", "{input}")]
        )
        self.extraction_prompt = ChatPromptTemplate.from_messages(
            [("system", EXTRACTION_PROMPT), ("human", "{text}")]
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

        # Extraer preferencias del mensaje usando modelo estructurado
        preferences = self._extract_structured_preferences(user_input)

        # Actualizar datos del usuario con nuevas preferencias
        updated_data = user_data.copy()
        for key, value in preferences.model_dump(exclude_none=True).items():
            if value is not None:
                updated_data[key] = value

        # Formatear las preferencias conocidas para el prompt
        preferences_str = self._format_preferences(updated_data)

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
        updated_data["ultima_interaccion"] = datetime.now().isoformat()

        return response.content, updated_data

    def _extract_structured_preferences(self, text: str) -> PropertyPreference:
        """Extrae preferencias inmobiliarias del texto usando modelo estructurado."""
        try:
            # Usar el modelo para extraer preferencias estructuradas
            extraction_result = self.model.with_structured_output(PropertyPreference).invoke(
                self.extraction_prompt.format(text=text)
            )
            return extraction_result
        except Exception as e:
            print(f"Error extrayendo preferencias estructuradas: {e}")
            # Fallback a un objeto de PropertyPreference con valores predeterminados
            return PropertyPreference(
                tipo_inmueble=None,
                presupuesto_min=None,
                presupuesto_max=None,
                moneda=None,
                metraje=None,
                habitaciones=None,
                distrito=None,
                timeline_compra=None
            )

    @staticmethod
    def _format_preferences(data: Dict[str, Any]) -> str:
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

    # Métodos adicionales para integración con LangGraph
    def get_prompt(self):
        """Retorna el prompt base para este agente."""
        return PREFERENCES_PROMPT