"""MVP Graph for basic lead generation.

This is the simplest graph implementation for Phase 1, focusing on
capturing the mandatory (P10) fields through a conversational interface.
"""

from typing import Dict, List, Any, Tuple
from langgraph.graph import StateGraph

# Type definitions for better readability
State = Dict[str, Any]
Message = str

# Define handlers for each node
def welcome_handler(state: State, message: Message) -> Tuple[State, Message]:
    """Initial greeting and explanation of the service."""
    # Initialize state if needed
    if not state.get("initialized"):
        state["initialized"] = True
        state["lead_data"] = {
            "nombre": None,
            "tipo_inmueble": None,
            "consentimiento": None,
        }
        state["conversation"] = {
            "history": [],
            "current_flow": "welcome"
        }
    
    # Add user message to history
    if message and message.strip():
        state["conversation"]["history"].append({"role": "user", "content": message})
    
    # Generate welcome message
    response = (
        "¡Hola! Soy el asistente virtual de Inmobilia. Estoy aquí para ayudarte "
        "a encontrar el inmueble perfecto para ti. ¿Te gustaría que te ayude a "
        "buscar un departamento, casa, oficina o terreno?"
    )
    
    # Update state
    state["conversation"]["history"].append({"role": "assistant", "content": response})
    state["conversation"]["current_flow"] = "legal"
    
    return state, response

def legal_handler(state: State, message: Message) -> Tuple[State, Message]:
    """Handle legal consent required by Peruvian law."""
    # Add user message to history
    state["conversation"]["history"].append({"role": "user", "content": message})
    
    # Check if this is first time in legal or a retry
    if state["conversation"]["current_flow"] == "legal" and state["lead_data"]["consentimiento"] is None:
        # Try to extract property type from previous message
        property_type = extract_property_type(message)
        if property_type:
            state["lead_data"]["tipo_inmueble"] = property_type
        
        # Present legal consent
        response = (
            "Antes de continuar, necesito tu consentimiento para procesar tus datos "
            "según la Ley 29733 de Protección de Datos Personales. ¿Me autorizas a "
            "utilizar tus datos para encontrar opciones inmobiliarias que se ajusten "
            "a tus necesidades?"
        )
    else:
        # Check for consent in the message
        consent_given = check_consent(message)
        
        if consent_given:
            state["lead_data"]["consentimiento"] = True
            response = (
                "Gracias por tu consentimiento. Ahora cuéntame, ¿cómo te llamas?"
            )
            state["conversation"]["current_flow"] = "core_data"
        else:
            response = (
                "Para poder asistirte, necesito que me autorices a utilizar tus "
                "datos según la ley peruana. Por favor, responde 'Sí' o 'Acepto' "
                "para continuar."
            )
    
    # Update conversation history
    state["conversation"]["history"].append({"role": "assistant", "content": response})
    
    return state, response

def core_data_handler(state: State, message: Message) -> Tuple[State, Message]:
    """Collect core data: name and property type confirmation."""
    # Add user message to history
    state["conversation"]["history"].append({"role": "user", "content": message})
    
    # Check if we need to get name or property type
    if state["lead_data"]["nombre"] is None:
        # Extract name from message
        name = extract_name(message)
        state["lead_data"]["nombre"] = name
        
        # If we already have property type, ask for contact, otherwise confirm property type
        if state["lead_data"]["tipo_inmueble"]:
            response = (
                f"Gracias, {name}. Para mostrarte opciones de {state['lead_data']['tipo_inmueble']} "
                f"que podrían interesarte, ¿me podrías compartir tu número de celular?"
            )
            state["conversation"]["current_flow"] = "contact"
        else:
            response = (
                f"Gracias, {name}. ¿Qué tipo de inmueble estás buscando? ¿Un departamento, "
                f"casa, oficina o terreno?"
            )
    else:
        # We have the name, now confirm property type if needed
        if state["lead_data"]["tipo_inmueble"] is None:
            property_type = extract_property_type(message)
            state["lead_data"]["tipo_inmueble"] = property_type
            
            response = (
                f"Entendido, {state['lead_data']['nombre']}. Para mostrarte opciones de {property_type} "
                f"que podrían interesarte, ¿me podrías compartir tu número de celular?"
            )
            state["conversation"]["current_flow"] = "contact"
        else:
            # Unexpected state - should not reach here in MVP
            response = (
                f"Gracias por la información, {state['lead_data']['nombre']}. "
                f"¿Hay algo más que quieras contarme sobre lo que buscas?"
            )
    
    # Update conversation history
    state["conversation"]["history"].append({"role": "assistant", "content": response})
    
    return state, response

# Helper functions (placeholders for Phase 1)
def extract_property_type(message: str) -> str:
    """Extract property type from message."""
    message = message.lower()
    if any(term in message for term in ["departamento", "depa", "flat", "apartamento"]):
        return "departamento"
    elif any(term in message for term in ["casa", "vivienda", "chalet"]):
        return "casa"
    elif any(term in message for term in ["oficina", "local", "comercial"]):
        return "oficina"
    elif any(term in message for term in ["terreno", "lote", "parcela", "terr"]):
        return "terreno"
    else:
        return None

def check_consent(message: str) -> bool:
    """Check if the message contains consent."""
    message = message.lower()
    affirmative_terms = ["si", "sí", "acepto", "autorizo", "de acuerdo", "ok", 
                        "claro", "por supuesto", "adelante"]
    
    return any(term in message for term in affirmative_terms)

def extract_name(message: str) -> str:
    """Extract name from message."""
    # In a real implementation, this would be more sophisticated
    # For Phase 1, we'll just return the message as the name
    # In later phases, we'll use NLP to extract names properly
    return message.strip()

# Build the graph
def build_mvp_graph():
    """Build the MVP graph for Phase 1."""
    graph = StateGraph()
    
    # Add nodes
    graph.add_node("welcome", welcome_handler)
    graph.add_node("legal", legal_handler)
    graph.add_node("core_data", core_data_handler)
    
    # Add edges
    graph.add_edge("welcome", "legal")
    graph.add_conditional_edges(
        "legal",
        lambda state: "core_data" if state["lead_data"]["consentimiento"] == True else "legal"
    )
    
    # Set entry point
    graph.set_entry_point("welcome")
    
    return graph.compile()