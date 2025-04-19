import pytest

from src.models.enums import EstadoLead, TipoDocumento, TipoInmueble


class TestEstadoLead:
    def test_enum_values(self) -> None:
        assert EstadoLead.CONVERSACION_INICIADA == "ConversacionIniciada"
        assert EstadoLead.PRE_LEAD == "PreLead"
        assert EstadoLead.LEAD == "Lead"
        assert EstadoLead.LEAD_ENRIQUECIDO == "LeadEnriquecido"

    def test_enum_members(self) -> None:
        assert set(EstadoLead.__members__.keys()) == {
            "CONVERSACION_INICIADA",
            "PRE_LEAD",
            "LEAD",
            "LEAD_ENRIQUECIDO",
        }


class TestTipoInmueble:
    def test_enum_values(self) -> None:
        assert TipoInmueble.DEPARTAMENTO == "departamento"
        assert TipoInmueble.CASA == "casa"
        assert TipoInmueble.OFICINA == "oficina"
        assert TipoInmueble.LOTE == "lote"
        assert TipoInmueble.TERRENO == "terreno"

    def test_enum_members(self) -> None:
        assert set(TipoInmueble.__members__.keys()) == {
            "DEPARTAMENTO",
            "CASA",
            "OFICINA",
            "LOTE",
            "TERRENO",
        }


class TestTipoDocumento:
    def test_enum_values(self) -> None:
        assert TipoDocumento.DNI == "dni"
        assert TipoDocumento.CE == "ce"
        assert TipoDocumento.PASAPORTE == "pasaporte"
        assert TipoDocumento.RUC == "ruc"

    def test_enum_members(self) -> None:
        assert set(TipoDocumento.__members__.keys()) == {
            "DNI",
            "CE",
            "PASAPORTE",
            "RUC",
        }
