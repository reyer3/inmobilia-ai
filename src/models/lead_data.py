"""Modelo de datos para leads inmobiliarios.

Este módulo define la estructura de datos para los leads inmobiliarios,
con validaciones y utilitarios para gestionar la información del cliente.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class LeadMetadata(BaseModel):
    """Metadatos adicionales para un lead."""

    fecha_creacion: str = Field(default_factory=lambda: datetime.now().isoformat())
    fecha_modificacion: str = Field(default_factory=lambda: datetime.now().isoformat())
    fecha_consentimiento: Optional[str] = None
    origen: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    dispositivo: Optional[str] = None
    agente_asignado: Optional[str] = None
    ultima_interaccion: Optional[str] = None


class LeadData(BaseModel):
    """Modelo para los datos de un lead inmobiliario."""

    # Datos básicos (Prioridad 10 - Obligatorios)
    nombre: Optional[str] = Field(None, description="Nombre del cliente")
    tipo_inmueble: Optional[str] = Field(None, description="Tipo de inmueble buscado")
    consentimiento: Optional[bool] = Field(
        None, description="Consentimiento para procesar datos personales"
    )

    # Datos de contacto (Prioridad 9)
    celular: Optional[str] = Field(None, description="Número de celular del cliente")
    email: Optional[str] = Field(None, description="Correo electrónico del cliente")

    # Datos de ubicación (Prioridad 9)
    distrito: Optional[str] = Field(None, description="Distrito o zona de interés")
    zona: Optional[str] = Field(None, description="Zona general (norte, sur, etc.)")
    metraje: Optional[int] = Field(None, description="Metraje deseado en metros cuadrados")

    # Datos adicionales (Prioridad 8)
    habitaciones: Optional[int] = Field(None, description="Número de habitaciones deseadas")
    presupuesto_min: Optional[float] = Field(None, description="Presupuesto mínimo en moneda local")
    presupuesto_max: Optional[float] = Field(None, description="Presupuesto máximo en moneda local")

    # Datos opcionales (Prioridad 7)
    tipo_documento: Optional[str] = Field(None, description="Tipo de documento de identidad")
    numero_documento: Optional[str] = Field(None, description="Número de documento de identidad")
    timeline_compra: Optional[str] = Field(None, description="Plazo estimado para la compra")

    # Estado y metadatos
    estado: str = Field("ConversacionIniciada", description="Estado actual del lead")
    metadata: Optional[LeadMetadata] = Field(default_factory=LeadMetadata)

    # Configuración del modelo
    model_config = {
        "validate_assignment": True,  # Validar al asignar atributos
        "extra": "ignore",  # Ignorar campos adicionales
    }

    # Validadores de campos
    @field_validator("metraje")
    @classmethod
    def validate_metraje(cls, value):
        """Valida y convierte el metraje a entero si es posible."""
        if isinstance(value, str):
            try:
                # Limpiar el string (quitar "m2", "metros", etc)
                clean_value = value.lower().replace("m2", "").replace("metros", "").strip()
                return int(clean_value)
            except (ValueError, TypeError):
                return None
        return value

    @field_validator("habitaciones")
    @classmethod
    def validate_habitaciones(cls, value):
        """Valida y convierte el número de habitaciones a entero si es posible."""
        if isinstance(value, str):
            try:
                # Extraer sólo dígitos
                import re

                digits = re.search(r"\d+", value)
                if digits:
                    return int(digits.group())
                return None
            except (ValueError, TypeError):
                return None
        return value

    @field_validator("presupuesto_min", "presupuesto_max")
    @classmethod
    def validate_presupuesto(cls, value):
        """Valida y convierte el presupuesto a float si es posible."""
        if isinstance(value, str):
            try:
                # Limpiar el string (quitar símbolos de moneda, comas, etc)
                clean_value = value.replace("$", "").replace("S/", "").replace(",", "").strip()
                return float(clean_value)
            except (ValueError, TypeError):
                return None
        return value

    @model_validator(mode="after")
    def check_presupuesto_range(self):
        """Verifica que el presupuesto máximo sea mayor al mínimo."""
        if (
            self.presupuesto_min is not None
            and self.presupuesto_max is not None
            and self.presupuesto_min > self.presupuesto_max
        ):
            self.presupuesto_min, self.presupuesto_max = (
                self.presupuesto_max,
                self.presupuesto_min,
            )
        return self

    # Métodos de utilidad
    def update_estado(self) -> None:
        """Actualiza el estado del lead basado en los datos completados."""
        # Campos obligatorios (P10)
        p10_fields = ["nombre", "tipo_inmueble", "consentimiento"]
        p10_missing = [field for field in p10_fields if getattr(self, field) is None]

        # Campos importantes (P9)
        p9_fields = ["celular", "email", "distrito", "metraje"]
        p9_completed = len([field for field in p9_fields if getattr(self, field) is not None])

        # Campos adicionales (P8)
        p8_fields = ["habitaciones", "presupuesto_min", "presupuesto_max"]
        p8_completed = len([field for field in p8_fields if getattr(self, field) is not None])

        if p10_missing:
            self.estado = "ConversacionIniciada"
        elif not p10_missing and p9_completed < 2:
            self.estado = "PreLead"
        elif p9_completed >= 2 and p8_completed < 2:
            self.estado = "Lead"
        else:
            self.estado = "LeadEnriquecido"

        # Actualizar fecha de modificación
        if self.metadata:
            self.metadata.fecha_modificacion = datetime.now().isoformat()

    def is_core_complete(self) -> bool:
        """Verifica si los datos obligatorios (P10) están completos."""
        return all(
            [
                self.nombre is not None,
                self.tipo_inmueble is not None,
                self.consentimiento is True,
            ]
        )

    def is_contact_complete(self) -> bool:
        """Verifica si al menos un dato de contacto está completo."""
        return any([self.celular is not None, self.email is not None])

    def get_missing_fields(self, priority: int = 10) -> List[str]:
        """Devuelve los campos faltantes según nivel de prioridad.

        Args:
            priority: Nivel de prioridad (10: obligatorios, 9: importantes, 8: adicionales, 7: opcionales)

        Returns:
            Lista de nombres de campos faltantes
        """
        missing = []

        if priority >= 10:  # Obligatorios
            p10_fields = ["nombre", "tipo_inmueble", "consentimiento"]
            missing.extend([f for f in p10_fields if getattr(self, f) is None])

        if priority >= 9:  # Importantes
            p9_fields = ["celular", "email", "distrito", "metraje"]
            missing.extend([f for f in p9_fields if getattr(self, f) is None])

        if priority >= 8:  # Adicionales
            p8_fields = ["habitaciones", "presupuesto_min", "presupuesto_max"]
            missing.extend([f for f in p8_fields if getattr(self, f) is None])

        if priority >= 7:  # Opcionales
            p7_fields = ["tipo_documento", "numero_documento", "timeline_compra"]
            missing.extend([f for f in p7_fields if getattr(self, f) is None])

        return missing

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario, excluyendo campos nulos."""
        return self.model_dump(exclude_none=True)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Actualiza los campos del lead desde un diccionario."""
        for key, value in data.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)

        # Actualizar estado y metadata
        self.update_estado()
