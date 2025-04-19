# Tests Unitarios

Este directorio contiene pruebas unitarias para los diferentes componentes del proyecto. La estructura se organiza por tipo de componente:

## Estructura

- `models/`: Pruebas para los modelos de datos
  - `test_enums.py`: Pruebas para las enumeraciones (EstadoLead, TipoInmueble, TipoDocumento)
  - `test_validators.py`: Pruebas para las funciones de validación
  - `test_lead_data.py`: Pruebas para el modelo LeadData y LeadMetadata
  - `test_agent_state.py`: Pruebas para el estado del agente
  - `test_api.py`: Pruebas para los modelos de API

- `test_configuration.py`: Pruebas para la configuración del agente

## Ejecución

Ejecutar todas las pruebas:
```bash
make test
```

Ejecutar un archivo específico:
```bash
make test TEST_FILE=tests/unit_tests/models/test_validators.py
```

Ejecutar pruebas en modo watch:
```bash
make test_watch
```

## Dependencias

Para ejecutar los tests es necesario tener instaladas todas las dependencias del proyecto. Asegúrate de instalar las dependencias de desarrollo:

```bash
uv pip install -e ".[dev]"
```