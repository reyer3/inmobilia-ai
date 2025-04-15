# Inmobilia AI

Agente conversacional basado en LangGraph para generación de leads inmobiliarios.

## Descripción

Inmobilia AI es un sistema de conversación inteligente diseñado para capturar y calificar leads en el sector inmobiliario, específicamente adaptado al mercado peruano. El sistema utiliza LangGraph para crear flujos de conversación naturales que obtienen la información necesaria mientras mantienen una experiencia fluida para el usuario.

## Características

- Conversación natural para captura de datos de lead
- Cumplimiento con la ley peruana de protección de datos (Ley 29733)
- Extracción inteligente de información de respuestas abiertas
- Flujos adaptativos según las necesidades del usuario
- Recomendación de proyectos inmobiliarios

## Estructura del Proyecto

El proyecto sigue una arquitectura modular con desarrollo incremental:

- **Fase 1:** MVP Conversacional
- **Fase 2:** Extracción Inteligente
- **Fase 3:** Flujo Adaptativo
- **Fase 4:** Match y Engagement
- **Fase 5:** Optimización de Conversión

## Metodología GitFlow

Este proyecto implementa GitFlow como metodología de control de versiones:

- `main`: Versión de producción estable
- `develop`: Rama de desarrollo principal
- `feature/*`: Nuevas funcionalidades
- `release/*`: Preparación para lanzamientos
- `hotfix/*`: Correcciones urgentes en producción

## Requisitos

- Python 3.10+
- LangGraph
- LangChain
- Base de datos (a definir)

## Estructura de Datos

El sistema captura información estructurada con diferentes niveles de prioridad:

- **Prioridad 10 (Obligatorio)**: Nombre, Tipo de inmueble, Consentimiento
- **Prioridad 9**: Celular, Distrito/Zona, ID Proyecto
- **Prioridad 8**: Email, Documento, Metraje, Habitaciones
- **Prioridad 7**: Presupuesto, Timeline de compra

## Contribución

Por favor, sigue las convenciones de GitFlow para contribuir a este proyecto.