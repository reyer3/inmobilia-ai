from datetime import datetime

import pytest

from src.models.api import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LeadDataResponse,
    SessionInfo,
    SessionListResponse,
)


class TestChatRequest:
    def test_required_fields(self) -> None:
        # message field is required
        with pytest.raises(Exception):
            ChatRequest()

        # Valid creation with just message
        request = ChatRequest(message="Hola")
        assert request.message == "Hola"
        assert request.session_id is None
        assert request.user_id is None
        assert request.metadata == {}

    def test_optional_fields(self) -> None:
        request = ChatRequest(
            message="Hola",
            session_id="session-123",
            user_id="user-456",
            metadata={"source": "web", "path": "/contacto"},
        )
        assert request.message == "Hola"
        assert request.session_id == "session-123"
        assert request.user_id == "user-456"
        assert request.metadata == {"source": "web", "path": "/contacto"}


class TestLeadDataResponse:
    def test_extended_fields(self) -> None:
        lead_response = LeadDataResponse(
            nombre="Juan Pérez",
            score=85.5,
            ultima_actualizacion=datetime.now().isoformat(),
            propiedades_sugeridas=["prop-1", "prop-2"],
        )
        assert lead_response.nombre == "Juan Pérez"
        assert lead_response.score == 85.5
        assert isinstance(lead_response.ultima_actualizacion, str)
        assert lead_response.propiedades_sugeridas == ["prop-1", "prop-2"]


class TestChatResponse:
    def test_required_fields(self) -> None:
        # These fields are required
        with pytest.raises(Exception):
            ChatResponse()

        with pytest.raises(Exception):
            ChatResponse(message="Respuesta")

        with pytest.raises(Exception):
            ChatResponse(message="Respuesta", session_id="session-123")

        # Valid creation with required fields
        response = ChatResponse(
            message="Respuesta", session_id="session-123", conversation_id="conv-456"
        )
        assert response.message == "Respuesta"
        assert response.session_id == "session-123"
        assert response.conversation_id == "conv-456"

        # Defaults for optional fields
        assert response.user_id is None
        assert isinstance(response.lead_data, LeadDataResponse)
        assert isinstance(response.timestamp, str)
        assert response.agent is None
        assert response.next_agent is None
        assert response.estado_lead is None

    def test_all_fields(self) -> None:
        response = ChatResponse(
            message="Respuesta",
            session_id="session-123",
            conversation_id="conv-456",
            user_id="user-789",
            lead_data=LeadDataResponse(nombre="Juan Pérez"),
            timestamp="2023-01-01T12:00:00",
            agent="extractor",
            next_agent="responder",
            estado_lead="Lead",
        )
        assert response.message == "Respuesta"
        assert response.session_id == "session-123"
        assert response.conversation_id == "conv-456"
        assert response.user_id == "user-789"
        assert response.lead_data.nombre == "Juan Pérez"
        assert response.timestamp == "2023-01-01T12:00:00"
        assert response.agent == "extractor"
        assert response.next_agent == "responder"
        assert response.estado_lead == "Lead"


class TestSessionInfo:
    def test_session_info(self) -> None:
        session = SessionInfo(
            session_id="session-123",
            user_id="user-456",
            created_at="2023-01-01T10:00:00",
            last_activity="2023-01-01T12:00:00",
            message_count=5,
            lead_status="Lead",
        )
        assert session.session_id == "session-123"
        assert session.user_id == "user-456"
        assert session.created_at == "2023-01-01T10:00:00"
        assert session.last_activity == "2023-01-01T12:00:00"
        assert session.message_count == 5
        assert session.lead_status == "Lead"


class TestSessionListResponse:
    def test_session_list(self) -> None:
        session1 = SessionInfo(
            session_id="session-123",
            created_at="2023-01-01T10:00:00",
            last_activity="2023-01-01T12:00:00",
            message_count=5,
        )
        session2 = SessionInfo(
            session_id="session-456",
            created_at="2023-01-01T11:00:00",
            last_activity="2023-01-01T12:30:00",
            message_count=3,
        )

        response = SessionListResponse(total=2, sessions=[session1, session2])

        assert response.total == 2
        assert len(response.sessions) == 2
        assert response.sessions[0].session_id == "session-123"
        assert response.sessions[1].session_id == "session-456"


class TestHealthResponse:
    def test_health_response(self) -> None:
        health = HealthResponse(
            status="OK",
            version="1.0.0",
            environment="production",
            uptime=3600.5,
            sessions_active=25,
        )

        assert health.status == "OK"
        assert health.version == "1.0.0"
        assert health.environment == "production"
        assert health.uptime == 3600.5
        assert health.sessions_active == 25
        assert isinstance(health.timestamp, str)

        # Should not raise exception if timestamp is properly formatted
        datetime.fromisoformat(health.timestamp)
