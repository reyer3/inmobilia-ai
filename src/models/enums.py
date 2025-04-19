"""Definición de enumeraciones para Inmobilia AI."""

from enum import Enum


class EstadoLead(str, Enum):
    """Estados posibles de un lead en el proceso de conversación."""

    CONVERSACION_INICIADA = "ConversacionIniciada"
    PRE_LEAD = "PreLead"
    LEAD = "Lead"
    LEAD_ENRIQUECIDO = "LeadEnriquecido"


class TipoInmueble(str, Enum):
    """Tipos de inmuebles soportados."""

    DEPARTAMENTO = "departamento"
    CASA = "casa"
    OFICINA = "oficina"
    LOTE = "lote"
    TERRENO = "terreno"


class TipoDocumento(str, Enum):
    """Tipos de documento de identidad soportados."""

    DNI = "dni"
    CE = "ce"  # Carnet de Extranjería
    PASAPORTE = "pasaporte"
    RUC = "ruc"
