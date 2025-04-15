# Roadmap de Inmobilia AI

Este documento describe el plan de desarrollo incremental para Inmobilia AI, dividido en fases con objetivos y entregables claros.

## Fase 1: MVP Conversacional ✅

**Estado:** Completado (Abril 2025)

**Objetivo:** Crear un agente conversacional básico que capture los datos obligatorios (prioridad 10).

**Entregables:**
- Grafo de conversación para capturar nombre, tipo de inmueble y consentimiento
- API básica con FastAPI
- Extractores simples de datos
- Validadores para información del lead
- Pruebas unitarias básicas

## Fase 2: Extracción Inteligente 🔄

**Estado:** En progreso

**Objetivo:** Mejorar la extracción de datos y expandir el grafo para capturar información adicional.

**Entregables:**
- Mejora de extractores (teléfono, email, ubicación)
- Integración con LLM para extracción avanzada
- Persistencia de datos con base de datos
- Nodos adicionales en el grafo de conversación
- CI/CD y documentación API
- Implementación de logging y monitoreo

**Issues relacionados:** #4, #5, #6, #7, #8, #9, #10, #11, #12, #13

## Fase 3: Flujo Adaptativo 🔜

**Estado:** Planificado

**Objetivo:** Implementar un flujo conversacional más natural y adaptativo.

**Entregables:**
- Detección de intenciones del usuario
- Rutas dinámicas en el grafo según contexto
- Personalización basada en preferencias detectadas
- Manejo de múltiples temas en la misma conversación
- Implementación de memoria para referencias previas

## Fase 4: Match y Engagement 🔜

**Estado:** Planificado

**Objetivo:** Integrar sistema de recomendación de propiedades y mejorar engagement.

**Entregables:**
- Integración con API de proyectos inmobiliarios
- Algoritmo de matching basado en preferencias
- Presentación visual de propiedades
- Sistema de feedback del usuario sobre recomendaciones
- Seguimiento de interacciones para mejora continua

## Fase 5: Optimización de Conversión 🔜

**Estado:** Planificado

**Objetivo:** Maximizar tasas de conversión y mejorar experiencia del usuario.

**Entregables:**
- A/B testing de diferentes estrategias conversacionales
- Optimización basada en analítica de conversaciones
- Hooks psicológicos (escasez, prueba social, etc.)
- Sistema de seguimiento post-conversación
- Integración con CRM para seguimiento de leads

---

*Este roadmap es un documento vivo y puede ser ajustado según las necesidades del proyecto y feedback recibido.*