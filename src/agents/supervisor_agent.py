"""Agente supervisor que coordina la conversación de manera no secuencial.

Este agente analiza cada mensaje del usuario, extrae datos dinámicamente
y decide qué agente especializado debe manejar cada mensaje.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Literal, Optional, TypedDict, List, Union

# Corrigiendo la importación de Message
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage as Message
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.constants import END
from langgraph.types import Command
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.models.lead_data import LeadData
from src.services.analytics_client import track_agent_assignment

logger = logging.getLogger(__name__)


class RouterResponse(TypedDict):
    """Respuesta del supervisor para ruteo."""
    next: Literal["legal", "collector", "location", "preferences", "END"]
    reasoning: str


class ExtractedData(BaseModel):
    """Modelo para estructurar la información extraída del mensaje del usuario."""

    nombre: Optional[str] = Field(None, description="Nombre del cliente")
    email: Optional[str] = Field(None, description="Correo electrónico del cliente")
    celular: Optional[str] = Field(None, description="Número de celular del cliente")
    tipo_inmueble: Optional[str] = Field(None, description="Tipo de inmueble buscado")
    distrito: Optional[str] = Field(None, description="Distrito o zona de interés")
    zona: Optional[str] = Field(None, description="Zona general (norte, sur, etc.)")
    presupuesto_min: Optional[float] = Field(None, description="Presupuesto mínimo en moneda local")
    presupuesto_max: Optional[float] = Field(None, description="Presupuesto máximo en moneda local")
    metraje: Optional[int] = Field(None, description="Metraje deseado en metros cuadrados")
    habitaciones: Optional[int] = Field(None, description="Número de habitaciones deseadas")
    consentimiento: Optional[bool] = Field(None, description="Si el usuario ha dado consentimiento para procesar sus datos")
    timeline_compra: Optional[str] = Field(None, description="Plazo estimado para la compra")

    class Config:
        extra = "ignore"


class SupervisorAgent:
    """Agente supervisor que coordina la conversación de manera no secuencial."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-latest"):
        """Inicializa el agente supervisor.

        Args:
            model_name: Nombre del modelo a utilizar
        """
        self.model = ChatOpenAI(model=model_name, temperature=0.2)
        settings = get_settings()

        # Sistema de prioridades para datos
        self.priorities = settings["lead_priorities"]

        # Carga prompts configurados
        self.router_prompt = """
        Eres un supervisor de conversación para un asistente inmobiliario en Perú.
        Tu trabajo es analizar cada mensaje del usuario y determinar qué agente especializado 
        debe manejarlo, basándote en el contexto actual y el estado del lead.
        
        Agentes disponibles:
        1. legal: Maneja consentimiento y aspectos legales (debe activarse primero si no hay consentimiento)
        2. collector: Obtiene datos básicos del usuario (nombre, contacto, etc.)
        3. location: Maneja consultas sobre ubicaciones y distritos en Perú
        4. preferences: Captura preferencias específicas sobre el inmueble (presupuesto, metraje, etc.)
        5. END: Finaliza la conversación cuando el lead está completo o el usuario está satisfecho
        
        Prioridades:
        - Si falta consentimiento, siempre asigna "legal" primero
        - Si el mensaje contiene información sobre ubicaciones, asigna "location"
        - Si el mensaje contiene preferencias inmobiliarias, asigna "preferences"
        - Si necesitas datos personales básicos, asigna "collector"
        - Si el usuario indica que ha terminado o agradece, considera "END"
        
        Basándote en el contexto y los datos ya recolectados, determina el mejor agente
        para continuar la conversación de forma natural, sin seguir un orden secuencial rígido.
        """

        # Prompt para extracción estructurada
        self.extraction_prompt = """
        Extrae toda la información relevante del mensaje del usuario para un contexto inmobiliario.
        Solo incluye la información explícitamente mencionada en este mensaje.
        
        Mensaje del usuario: {text}
        
        Debes extraer:
        - nombre: Nombre del cliente si lo menciona
        - email: Correo electrónico si aparece en el mensaje
        - celular: Número de celular peruano si lo proporciona
        - tipo_inmueble: Tipo de propiedad mencionada (departamento, casa, etc.)
        - distrito: Distrito específico de Lima/Perú mencionado
        - zona: Zona general (Lima Norte, Lima Sur, etc.)
        - presupuesto_min: Cantidad mínima de presupuesto como número
        - presupuesto_max: Cantidad máxima de presupuesto como número
        - metraje: Tamaño del inmueble en metros cuadrados como número entero
        - habitaciones: Número de habitaciones como entero
        - consentimiento: Si el mensaje incluye aceptación explícita de consentimiento para procesar datos (true/false)
        - timeline_compra: Plazo estimado para la compra
        
        Responde solo con los campos que puedas identificar claramente en el mensaje.
        Para consentimiento, marca como true solo si hay una aceptación explícita para tratar sus datos personales.
        """

        self.extraction_prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.extraction_prompt),
            ("human", "{text}")
        ])

    async def extract_information(self, message: str) -> Dict[str, Any]:
        """Extrae toda la información posible de un mensaje en una sola pasada usando modelo estructurado.

        Args:
            message: Mensaje del usuario

        Returns:
            Diccionario con información extraída
        """
        try:
            # Usar el modelo para extraer datos estructurados
            extraction_result = self.model.with_structured_output(ExtractedData).invoke(
                self.extraction_prompt_template.format(text=message)
            )

            # Convertir a diccionario, excluyendo valores None
            extracted_data = extraction_result.model_dump(exclude_none=True)

            # Generar niveles de confianza (simulados ya que el modelo no proporciona confianza)
            confidence = {k: 85 for k in extracted_data.keys()}

            return {
                "extracted": extracted_data,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error en extracción estructurada: {str(e)}")
            # En caso de error, devolver diccionarios vacíos
            return {
                "extracted": {},
                "confidence": {}
            }

    async def router_node(self, state: Dict[str, Any], config: RunnableConfig) -> Command:
        """Nodo que determina qué agente debe manejar el mensaje actual.

        Este método procesa cada mensaje del usuario, extrae información en una sola pasada
        y decide qué agente especializado debe manejarlo, sin seguir un flujo secuencial.

        Args:
            state: Estado actual del grafo
            config: Configuración del runnable

        Returns:
            Comando indicando el siguiente agente
        """
        # Extraer mensaje actual
        current_message = state.get("current_message", "")

        # Verificar si hay mensaje para procesar
        if not current_message:
            return Command(goto="legal", update={"last_agent": "supervisor"})

        # Extraer automáticamente toda la información posible
        extraction_result = await self.extract_information(current_message)
        high_confidence_data = {k: v for k, v in extraction_result["extracted"].items()
                              if extraction_result["confidence"].get(k, 0) >= 70}

        # Actualizar datos del lead con información extraída
        lead_data = state.get("lead_data", {}).copy() if isinstance(state.get("lead_data"), dict) else {}
        lead_data.update(high_confidence_data)

        # Verificar si ya existe el objeto LeadData
        lead_obj = state.get("lead_obj")
        if lead_obj:
            lead_obj.update_from_dict(high_confidence_data)
        else:
            lead_obj = LeadData(**lead_data)

        # Actualizar fecha de última interacción
        if lead_obj and lead_obj.metadata:
            lead_obj.metadata.ultima_interaccion = datetime.now().isoformat()

        # Construir mensajes para el modelo
        messages = [
            {"role": "system", "content": self.router_prompt},
        ]

        # Añadir contexto sobre datos ya recolectados
        lead_data_summary = self._format_lead_data(lead_data)
        messages.append({"role": "system", "content": f"Datos ya recolectados:\n{lead_data_summary}"})

        # Añadir análisis de lo que falta
        missing_fields = lead_obj.get_missing_fields(10) if lead_obj else self.priorities["P10"]
        messages.append({"role": "system", "content": f"Campos obligatorios faltantes: {', '.join(missing_fields)}"})

        # Añadir historial reciente (últimos mensajes para dar contexto)
        recent_history = self._format_recent_history(state.get("messages", []))
        messages.extend(recent_history)

        # Añadir mensaje actual
        messages.append({"role": "user", "content": current_message})

        # Determinar el siguiente agente
        try:
            response = self.model.with_structured_output(RouterResponse).invoke(messages)
            next_agent = response["next"]
            reasoning = response.get("reasoning", "")

            # Registrar la decisión para analytics
            if isinstance(config, dict) and config.get("configurable") and config["configurable"].get("thread_id"):
                thread_id = config["configurable"]["thread_id"]
                track_agent_assignment(
                    thread_id=thread_id,
                    user_message=current_message[:100] + "..." if len(current_message) > 100 else current_message,
                    assigned_agent=next_agent
                )

            logger.info(f"Router decidió: {next_agent}, razón: {reasoning}")

        except (KeyError, ValueError, TypeError) as e:
            # En caso de error, usar la lógica de fallback
            logger.error(f"Error en router_node: {str(e)}")
            next_agent = self.decide_next_agent(state)
            reasoning = f"Fallback: error en LLM - {str(e)[:100]}"

        # Guardar la decisión de ruteo para análisis
        routing_decisions = state.get("routing_decisions", [])
        routing_decisions.append({
            "timestamp": datetime.now().isoformat(),
            "message": current_message[:50] + "..." if len(current_message) > 50 else current_message,
            "next_agent": next_agent,
            "reasoning": reasoning
        })

        # Actualizar estado
        updates = {
            "lead_data": lead_data,
            "lead_obj": lead_obj,
            "last_agent": "supervisor",
            "next": next_agent,
            "routing_decisions": routing_decisions
        }

        if next_agent == "END":
            return Command(goto=END, update=updates)

        return Command(goto=next_agent, update=updates)

    @staticmethod
    def _format_recent_history(messages: List[Union[Dict[str, Any], Message]]) -> List[Dict[str, Any]]:
        """Formatea los mensajes recientes para proporcionar contexto al LLM.

        Args:
            messages: Lista de mensajes del historial

        Returns:
            Lista de mensajes formateados para el LLM
        """
        recent_messages = []

        # Tomar los últimos 6 mensajes para no saturar el contexto
        message_slice = messages[-6:] if len(messages) > 6 else messages

        for msg in message_slice:
            if isinstance(msg, dict):
                recent_messages.append(msg)
            elif isinstance(msg, (HumanMessage, AIMessage)):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                content = msg.content
                name = getattr(msg, "name", None)

                message_dict = {"role": role, "content": content}
                if name:
                    message_dict["name"] = name

                recent_messages.append(message_dict)

        return recent_messages

    @staticmethod
    def decide_next_agent(state: Dict[str, Any]) -> str:
        """Determina el siguiente agente basado en el análisis del estado actual.

        Esta es la función clave para el enfoque no secuencial. En lugar de seguir
        un flujo predefinido, analiza los datos disponibles y decide dinámicamente.

        Args:
            state: Estado actual del grafo

        Returns:
            ID del siguiente agente o END para terminar
        """
        # Datos del lead actuales
        lead_data = state.get("lead_data", {})
        lead_obj = state.get("lead_obj")

        # Verificar si ya existe un siguiente agente decidido
        if state.get("next") and state["next"] != "supervisor":
            return state["next"]

        # Verificar palabras de despedida en el mensaje actual
        message = state.get("current_message", "").lower()
        farewell_words = ["gracias", "adios", "adiós", "chau", "hasta luego", "terminar", "finalizar"]
        if any(word in message for word in farewell_words) and lead_data.get("consentimiento"):
            return "END"

        # Priorizar consentimiento legal si no existe
        if not lead_data.get("consentimiento"):
            return "legal"

        # Si ya tenemos el consentimiento pero faltan datos básicos (nombre, contacto)
        if lead_data.get("consentimiento") and (
            not lead_data.get("nombre") or
            not (lead_data.get("celular") or lead_data.get("email"))
        ):
            return "collector"

        # Si necesitamos datos de ubicación y tipo de inmueble
        if lead_data.get("consentimiento") and (
            not lead_data.get("distrito") or
            not lead_data.get("tipo_inmueble")
        ):
            return "location"

        # Si necesitamos preferencias específicas
        if lead_data.get("consentimiento") and lead_data.get("tipo_inmueble") and (
            not lead_data.get("presupuesto_max") or
            not lead_data.get("habitaciones")
        ):
            return "preferences"

        # Verificar si el lead está enriquecido
        if lead_obj and lead_obj.estado == "LeadEnriquecido":
            return "END"

        # Si no hay una regla clara, volver al agente más adecuado según el contenido
        if any(word in message for word in ["precio", "costo", "presupuesto", "habitacion", "habitación", "cuarto"]):
            return "preferences"
        elif any(word in message for word in ["zona", "distrito", "ubicacion", "ubicación", "lugar", "donde"]):
            return "location"
        elif any(word in message for word in ["nombre", "llamo", "contacto", "celular", "teléfono", "email", "correo"]):
            return "collector"

        # Por defecto, si no hay pistas claras y ya tenemos consentimiento,
        # usamos preferences para seguir enriqueciendo el lead
        if lead_data.get("consentimiento"):
            return "preferences"

        # Si tampoco tenemos consentimiento, volvemos a legal
        return "legal"

    @staticmethod
    def _format_lead_data(lead_data: Dict[str, Any]) -> str:
        """Formatea los datos del lead para incluirlos en el prompt."""
        if not lead_data:
            return "No se han recolectado datos todavía."

        # Mapeo para nombres más amigables
        key_mapping = {
            "nombre": "Nombre",
            "tipo_inmueble": "Tipo de inmueble",
            "consentimiento": "Consentimiento otorgado",
            "celular": "Número de celular",
            "email": "Correo electrónico",
            "distrito": "Distrito de interés",
            "zona": "Zona",
            "metraje": "Metraje (m²)",
            "habitaciones": "Número de habitaciones",
            "presupuesto_min": "Presupuesto mínimo",
            "presupuesto_max": "Presupuesto máximo",
            "tipo_documento": "Tipo de documento",
            "numero_documento": "Número de documento",
            "timeline_compra": "Plazo para compra"
        }

        formatted = ""
        for key, value in lead_data.items():
            if value is not None:
                display_key = key_mapping.get(key, key)
                # Formatear valores especiales
                if key == "consentimiento" and value is True:
                    value = "Sí"
                elif key == "presupuesto_min" or key == "presupuesto_max":
                    try:
                        value = f"S/ {float(value):,.2f}"
                    except (ValueError, TypeError):
                        pass

                formatted += f"- {display_key}: {value}\n"

        return formatted

    async def generate_summary(self, state: Dict[str, Any]) -> Optional[str]:
        """Genera un resumen del estado actual del lead para transferencia al CRM.

        Args:
            state: Estado actual del grafo

        Returns:
            Resumen formateado del lead o None si ocurre un error
        """
        lead_obj = state.get("lead_obj")
        if not lead_obj:
            return None

        try:
            lead_data = lead_obj.to_dict()

            # Preparar un prompt para que el modelo genere un resumen
            prompt = f"""
            Genera un resumen conciso del lead inmobiliario con estos datos:
            
            {self._format_lead_data(lead_data)}
            
            El resumen debe incluir:
            1. Nombre e información de contacto
            2. Preferencias inmobiliarias principales
            3. Presupuesto (si está disponible)
            4. Siguientes pasos recomendados para el asesor inmobiliario
            
            Formato el resumen en máximo 4-5 líneas, de manera profesional y directa.
            """

            response = self.model.invoke([
                {"role": "system", "content": "Eres un asistente especializado en inmobiliaria que genera resúmenes concisos para el CRM."},
                {"role": "user", "content": prompt}
            ])

            return response.content

        except (KeyError, ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error generando resumen: {str(e)}")
            return None