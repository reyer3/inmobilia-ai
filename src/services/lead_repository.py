"""Repositorio para gestionar datos de leads inmobiliarios.

Este módulo proporciona funciones para guardar, recuperar y actualizar
datos de leads en una base de datos o almacenamiento persistente.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.models.lead_data import LeadData

# Directorio para almacenar datos (para desarrollo)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
LEADS_DIR = os.path.join(DATA_DIR, "leads")

# Asegurar que los directorios existen
os.makedirs(LEADS_DIR, exist_ok=True)


def save_lead_data(thread_id: str, lead_data: Union[LeadData, Dict[str, Any]]) -> bool:
    """Guarda los datos de un lead asociado a un thread_id específico.

    En un entorno de producción, esto se conectaría a una base de datos.
    Para desarrollo, guarda los datos en archivos JSON.

    Args:
        thread_id: Identificador único de la conversación
        lead_data: Datos del lead a guardar (objeto LeadData o diccionario)

    Returns:
        Boolean indicando si la operación fue exitosa
    """
    try:
        # Convertir a diccionario si es un objeto LeadData
        data_dict = lead_data.to_dict() if isinstance(lead_data, LeadData) else lead_data

        # Añadir timestamp de actualización
        data_dict["last_updated"] = datetime.now().isoformat()

        # Guardar en un archivo JSON
        file_path = os.path.join(LEADS_DIR, f"{thread_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"Error al guardar datos del lead: {e}")
        return False


def get_lead_data(thread_id: str) -> Optional[Dict[str, Any]]:
    """Recupera los datos de un lead asociado a un thread_id específico.

    Args:
        thread_id: Identificador único de la conversación

    Returns:
        Diccionario con los datos del lead, o None si no existe
    """
    try:
        file_path = os.path.join(LEADS_DIR, f"{thread_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al recuperar datos del lead: {e}")
        return None


def get_lead_object(thread_id: str) -> Optional[LeadData]:
    """Recupera el objeto LeadData asociado a un thread_id específico.

    Args:
        thread_id: Identificador único de la conversación

    Returns:
        Objeto LeadData, o None si no existe
    """
    data = get_lead_data(thread_id)
    if not data:
        return None

    try:
        return LeadData.model_validate(data)
    except Exception as e:
        print(f"Error al convertir datos a objeto LeadData: {e}")
        return None


def delete_lead_data(thread_id: str) -> bool:
    """Elimina los datos de un lead asociado a un thread_id específico.

    Args:
        thread_id: Identificador único de la conversación

    Returns:
        Boolean indicando si la operación fue exitosa
    """
    try:
        file_path = os.path.join(LEADS_DIR, f"{thread_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error al eliminar datos del lead: {e}")
        return False


def list_leads(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Lista todos los leads disponibles.

    Args:
        limit: Número máximo de leads a devolver
        offset: Número de leads a saltar

    Returns:
        Lista de diccionarios con los datos de los leads
    """
    try:
        # Obtener todos los archivos JSON en el directorio de leads
        lead_files = [f for f in os.listdir(LEADS_DIR) if f.endswith(".json")]
        lead_files.sort(key=lambda x: os.path.getmtime(os.path.join(LEADS_DIR, x)), reverse=True)

        # Aplicar paginación
        lead_files = lead_files[offset : offset + limit]

        # Cargar los datos de cada lead
        leads = []
        for file_name in lead_files:
            thread_id = file_name[:-5]  # Quitar la extensión .json
            lead_data = get_lead_data(thread_id)
            if lead_data:
                lead_data["thread_id"] = thread_id
                leads.append(lead_data)

        return leads
    except Exception as e:
        print(f"Error al listar leads: {e}")
        return []
