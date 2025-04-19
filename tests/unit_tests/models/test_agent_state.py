from datetime import datetime

import pytest

from src.models.agent_state import AgentState, Message, get_initial_state


class TestAgentState:
    def test_message_type(self) -> None:
        message: Message = {
            "role": "user",
            "content": "Hola, estoy buscando un departamento",
            "name": None,
        }
        assert message["role"] == "user"
        assert message["content"] == "Hola, estoy buscando un departamento"
        assert message["name"] is None

    def test_get_initial_state(self) -> None:
        user_message = "Hola, busco un departamento"
        session_id = "test-session-123"
        user_id = "user-456"

        state = get_initial_state(user_message, session_id, user_id)

        # Verify basic structure
        assert isinstance(state, dict)
        assert state["lead_data"] == {}
        assert state["lead_obj"] is None
        assert state["last_agent"] == "none"
        assert state["session_id"] == session_id
        assert state["user_id"] == user_id
        assert state["error"] is None

        # Verify conversation history
        assert state["conversation_history"] == [{"role": "user", "content": user_message}]
        assert state["messages"] == [{"role": "user", "content": user_message}]
        assert state["current_message"] == user_message

        # Verify timestamps
        timestamp = state["conversation_start_time"]
        assert isinstance(timestamp, str)
        # Should not raise exception if properly formatted
        datetime.fromisoformat(timestamp)

    def test_get_initial_state_without_user_id(self) -> None:
        user_message = "Hola, busco un departamento"
        session_id = "test-session-123"

        state = get_initial_state(user_message, session_id)

        # User ID should default to session ID
        assert state["user_id"] == session_id
