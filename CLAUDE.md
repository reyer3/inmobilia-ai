# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Inmobilia AI - Asistente Inmobiliario Peruano

### Comandos esenciales
```bash
# Ejecutar pruebas
make test                                       # Todas las pruebas unitarias
make test TEST_FILE=tests/unit_tests/test_X.py  # Test específico
make integration_tests                          # Pruebas de integración
make test_watch                                 # Ejecutar tests en modo watch

# Linting y formato
make lint                                       # Verificar estilo y tipos
make format                                     # Formatear código automáticamente

# Desarrollo
python -m agent                                 # Ejecutar agente directamente
```

### Estructura del proyecto
- `/src/models/`: Modelos de datos (LeadData, AgentState) y validadores
- `/src/agent/`: Componentes del grafo conversacional LangGraph
  - `configuration.py`: Configuración del agente
  - `graph.py`: Definición del flujo conversacional
  - `state.py`: Estructuras de estado del agente

### Convenciones de código
- **Estilo**: Google Style Guide con docstrings en formato Google
- **Formato**: Ruff para formateo automático (ejecutar `make format`)
- **Importaciones**: Organizadas con `isort` (via ruff)
- **Tipos**: Type hints estrictos validados con mypy (`--strict`)
- **Pruebas**: Pytest para tests unitarios y de integración
- **Errores**: Capturar excepciones específicas como `anthropic.APIError`
- **Paquetes**: Usa uv para manejar los paquetes

### Configuración del entorno
Variables requeridas en `.env`:
```
ANTHROPIC_API_KEY=sk-...   # API key de Anthropic para Claude
LANGSMITH_PROJECT=inmobilia # Para trazas y monitoreo (opcional)
```

### Arquitectura del sistema
Este proyecto implementa un asistente inmobiliario conversacional para el mercado peruano usando:
- **LangGraph**: Orquestación de agentes especializados
- **Claude**: Modelo LLM para procesamiento de lenguaje natural
- **Pydantic**: Validación y serialización de datos inmobiliarios
- **ChromaDB**: Almacenamiento para datos y contexto

La implementación debe cumplir con la Ley 29733 de Protección de Datos Personales de Perú, especialmente en la obtención y manejo del consentimiento explícito.