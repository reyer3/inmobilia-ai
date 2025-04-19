"""Aplicación principal para Inmobilia AI.

Este módulo proporciona un punto de entrada simple para ejecutar
el asistente inmobiliario y probar su funcionamiento.
"""

import asyncio
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv

from src.config.settings import get_settings, validate_env
from src.graphs.inmobilia_graph import process_message, start_conversation
from src.services.analytics_client import track_conversation

# Cargar variables de entorno
load_dotenv()

# Validar configuración
if not validate_env():
    print("ERROR: Faltan variables de entorno críticas. Por favor verifica el archivo .env.")
    exit(1)


async def chat_loop():
    """Ejecuta un bucle de chat interactivo para probar el agente."""
    print("\n🏠 Inmobilia AI - Asistente Inmobiliario")
    print("----------------------------------------")
    print("(Escribe 'salir' para terminar)")
    print()

    # Inicializar sesión
    thread_id = str(uuid.uuid4())
    config = {"thread_id": thread_id, "user_id": "usuario_test", "context": {}}

    # Obtener mensaje de bienvenida
    state = await start_conversation()

    # Mostrar mensaje de bienvenida
    welcome_message = state["last_agent_response"]
    print(f"🤖 Asistente: {welcome_message}")

    # Registrar inicio de conversación
    track_conversation(
        thread_id=thread_id,
        event_type="conversation_started",
        event_data={
            "timestamp": datetime.now().isoformat(),
            "config": {k: v for k, v in config.items() if k != "context"},
        },
    )

    # Comenzar loop de conversación
    while True:
        # Entrada del usuario
        user_input = input("\n👤 Tú: ")

        # Verificar comando de salida
        if user_input.lower() in ["salir", "exit", "quit"]:
            # Registrar fin de conversación
            track_conversation(
                thread_id=thread_id,
                event_type="conversation_ended",
                event_data={
                    "reason": "user_exit",
                    "timestamp": datetime.now().isoformat(),
                },
            )
            print("\n¡Gracias por usar Inmobilia AI! Hasta pronto.")
            break

        # Registrar mensaje del usuario
        track_conversation(
            thread_id=thread_id,
            event_type="user_message",
            event_data={"message": user_input},
        )

        # Procesar mensaje
        try:
            result = await process_message(state, user_input, config)
            state = result
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            continue

        # Mostrar respuesta
        if "last_agent_response" in result and result["last_agent_response"]:
            agent_response = result["last_agent_response"]
            current_agent = result.get("current_agent", "unknown")
            print(f"\n🤖 Asistente [{current_agent}]: {agent_response}")

            # Registrar respuesta del agente
            track_conversation(
                thread_id=thread_id,
                event_type="assistant_response",
                event_data={
                    "agent": current_agent,
                    "message": (
                        agent_response[:100] + "..."
                        if len(agent_response) > 100
                        else agent_response
                    ),
                },
            )

        # Verificar si debemos terminar
        if result.get("should_end", False):
            # Registrar fin de conversación
            track_conversation(
                thread_id=thread_id,
                event_type="conversation_ended",
                event_data={
                    "reason": "completion",
                    "timestamp": datetime.now().isoformat(),
                },
            )
            print("\n💬 Conversación finalizada. ¡Gracias por usar Inmobilia AI!")
            break


if __name__ == "__main__":
    asyncio.run(chat_loop())
