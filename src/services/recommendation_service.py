"""Servicio de recomendaciones inmobiliarias.

Este módulo proporciona funciones para recomendar propiedades inmobiliarias
basadas en las preferencias del usuario y propiedades disponibles.
"""

import json
import os
import random
from typing import Any, Dict, List, Optional

# Directorio para almacenar datos (para desarrollo)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
PROPERTIES_DIR = os.path.join(DATA_DIR, "properties")

# Asegurar que los directorios existen
os.makedirs(PROPERTIES_DIR, exist_ok=True)


# Para desarrollo, usamos una lista fija de propiedades simuladas
SAMPLE_PROPERTIES = [
    {
        "id": "prop001",
        "tipo": "departamento",
        "distrito": "Miraflores",
        "direccion": "Av. Pardo 1234",
        "precio": 250000,
        "moneda": "USD",
        "metraje": 85,
        "habitaciones": 2,
        "baños": 2,
        "estacionamientos": 1,
        "descripcion": "Moderno departamento con vista al mar, cerca a parques y centros comerciales",
        "caracteristicas": ["piscina", "terraza", "gimnasio", "seguridad 24/7"],
        "estado": "En venta",
        "url_imagen": "https://example.com/images/prop001.jpg",
    },
    {
        "id": "prop002",
        "tipo": "casa",
        "distrito": "La Molina",
        "direccion": "Calle Las Palmeras 567",
        "precio": 420000,
        "moneda": "USD",
        "metraje": 180,
        "habitaciones": 4,
        "baños": 3,
        "estacionamientos": 2,
        "descripcion": "Amplia casa familiar en zona residencial exclusiva con amplio jardín",
        "caracteristicas": [
            "jardín",
            "parrilla",
            "cuarto de servicio",
            "sala de estar",
        ],
        "estado": "En venta",
        "url_imagen": "https://example.com/images/prop002.jpg",
    },
    {
        "id": "prop003",
        "tipo": "departamento",
        "distrito": "San Isidro",
        "direccion": "Calle Los Cedros 789",
        "precio": 320000,
        "moneda": "USD",
        "metraje": 110,
        "habitaciones": 3,
        "baños": 2,
        "estacionamientos": 1,
        "descripcion": "Elegante departamento en el corazón financiero de San Isidro",
        "caracteristicas": ["ascensor", "terraza", "lobby", "seguridad 24/7"],
        "estado": "En venta",
        "url_imagen": "https://example.com/images/prop003.jpg",
    },
    {
        "id": "prop004",
        "tipo": "departamento",
        "distrito": "Barranco",
        "direccion": "Jr. Unión 456",
        "precio": 190000,
        "moneda": "USD",
        "metraje": 75,
        "habitaciones": 2,
        "baños": 1,
        "estacionamientos": 1,
        "descripcion": "Acogedor departamento en zona bohemia, cerca a restaurantes y galerías",
        "caracteristicas": [
            "vista a la calle",
            "área de lavandería",
            "closets empotrados",
        ],
        "estado": "En venta",
        "url_imagen": "https://example.com/images/prop004.jpg",
    },
    {
        "id": "prop005",
        "tipo": "casa",
        "distrito": "Surco",
        "direccion": "Calle Monte Bello 123",
        "precio": 380000,
        "moneda": "USD",
        "metraje": 160,
        "habitaciones": 3,
        "baños": 2,
        "estacionamientos": 2,
        "descripcion": "Casa moderna en condominio cerrado con áreas verdes y seguridad",
        "caracteristicas": ["jardín", "terraza", "estudio", "cuarto de servicio"],
        "estado": "En venta",
        "url_imagen": "https://example.com/images/prop005.jpg",
    },
]


def initialize_sample_data():
    """Inicializa datos de muestra si no existen."""
    for prop in SAMPLE_PROPERTIES:
        file_path = os.path.join(PROPERTIES_DIR, f"{prop['id']}.json")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(prop, f, ensure_ascii=False, indent=2)


# Inicializar datos de muestra
initialize_sample_data()


def get_properties(
    filters: Optional[Dict[str, Any]] = None, limit: int = 10
) -> List[Dict[str, Any]]:
    """Obtiene propiedades que coinciden con los filtros especificados.

    En un entorno de producción, esto consultaría una base de datos.
    Para desarrollo, filtra las propiedades de muestra en memoria.

    Args:
        filters: Diccionario con criterios de filtrado
        limit: Número máximo de propiedades a devolver

    Returns:
        Lista de propiedades que coinciden con los filtros
    """
    # Cargar todas las propiedades
    properties = []
    for file_name in os.listdir(PROPERTIES_DIR):
        if file_name.endswith(".json"):
            with open(os.path.join(PROPERTIES_DIR, file_name), "r", encoding="utf-8") as f:
                properties.append(json.load(f))

    # Si no hay filtros, devolver todas las propiedades
    if not filters:
        return properties[:limit]

    # Filtrar propiedades según los criterios
    filtered_properties = []
    for prop in properties:
        match = True

        # Filtrar por tipo de inmueble
        if filters.get("tipo_inmueble") and prop["tipo"] != filters["tipo_inmueble"]:
            match = False

        # Filtrar por distrito
        if filters.get("distrito") and prop["distrito"] != filters["distrito"]:
            match = False

        # Filtrar por rango de precio
        if filters.get("presupuesto_min") and prop["precio"] < filters["presupuesto_min"]:
            match = False
        if filters.get("presupuesto_max") and prop["precio"] > filters["presupuesto_max"]:
            match = False

        # Filtrar por metraje mínimo
        if filters.get("metraje") and prop["metraje"] < filters["metraje"]:
            match = False

        # Filtrar por número de habitaciones
        if filters.get("habitaciones") and prop["habitaciones"] < filters["habitaciones"]:
            match = False

        if match:
            filtered_properties.append(prop)
            if len(filtered_properties) >= limit:
                break

    return filtered_properties


def get_recommended_properties(preferences: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
    """Recomienda propiedades basadas en las preferencias del usuario.

    Esta función aplica un algoritmo simplificado de recomendación basado en los
    filtros proporcionados en el objeto de preferencias.

    Args:
        preferences: Diccionario con las preferencias del usuario
        limit: Número máximo de propiedades a recomendar

    Returns:
        Lista de propiedades recomendadas
    """
    filters = {}

    # Aplicar filtros básicos
    if preferences.get("tipo_inmueble"):
        filters["tipo_inmueble"] = preferences["tipo_inmueble"]
    if preferences.get("distrito"):
        filters["distrito"] = preferences["distrito"]
    if preferences.get("habitaciones"):
        filters["habitaciones"] = preferences["habitaciones"]

    # Manejo de presupuesto (con margen de tolerancia)
    if preferences.get("presupuesto_max"):
        # Tolerancia del 10% por encima del presupuesto máximo
        filters["presupuesto_max"] = preferences["presupuesto_max"] * 1.1
    if preferences.get("presupuesto_min"):
        filters["presupuesto_min"] = preferences["presupuesto_min"]

    # Manejo de metraje
    if preferences.get("metraje"):
        # Tomamos el 90% del metraje deseado como mínimo
        filters["metraje"] = preferences["metraje"] * 0.9

    # Obtener propiedades que coinciden con los filtros
    matches = get_properties(filters, limit=limit * 2)

    # Si no hay suficientes coincidencias, relajar los filtros
    if len(matches) < limit:
        # Eliminar filtros menos prioritarios
        relaxed_filters = {}
        if "tipo_inmueble" in filters:
            relaxed_filters["tipo_inmueble"] = filters["tipo_inmueble"]
        if "distrito" in filters and len(matches) < 1:
            # Solo eliminar el filtro de distrito si no hay coincidencias
            pass
        else:
            if "distrito" in filters:
                relaxed_filters["distrito"] = filters["distrito"]

        # Relajar límites de presupuesto
        if "presupuesto_max" in filters:
            relaxed_filters["presupuesto_max"] = filters["presupuesto_max"] * 1.2

        matches = get_properties(relaxed_filters, limit=limit * 2)

    # Si tenemos más coincidencias que el límite, ordenar por relevancia
    # y seleccionar las mejores
    if len(matches) > limit:
        # En un sistema real, aquí aplicaríamos un algoritmo de ranking
        # Para simplificar, usamos un orden aleatorio
        random.shuffle(matches)
        matches = matches[:limit]

    return matches


def get_property_by_id(property_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene una propiedad por su ID.

    Args:
        property_id: Identificador único de la propiedad

    Returns:
        Datos de la propiedad, o None si no existe
    """
    try:
        file_path = os.path.join(PROPERTIES_DIR, f"{property_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al obtener propiedad: {e}")
        return None


def format_property_for_display(property_data: Dict[str, Any]) -> str:
    """Formatea los datos de una propiedad para mostrarlos al usuario.

    Args:
        property_data: Datos de la propiedad

    Returns:
        Texto formateado con información de la propiedad
    """
    # Formato de precio con separador de miles
    precio_formateado = f"{property_data['moneda']} {property_data['precio']:,}"

    # Construir texto
    text = f"""• *{property_data["tipo"].capitalize()} en {property_data["distrito"]}* (ID: {property_data["id"]})
• Precio: {precio_formateado}
• Área: {property_data["metraje"]} m² | {property_data["habitaciones"]} hab. | {property_data["baños"]} baños
• {property_data["descripcion"]}
• Características: {", ".join(property_data["caracteristicas"][:3])}"""

    return text
