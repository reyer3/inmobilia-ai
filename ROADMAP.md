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
- Nodos adicionales en el grafo de conversación
- Persistencia de datos con base de datos
- Implementación de CI/CD y herramientas de desarrollo ✅
- Documentación API con Swagger
- Sistema de logging y monitoreo

**Issues relacionados:** #4, #5, #6, #7, #8, #10 ✅, #11, #12

## Fase 2.5: Conversación Natural y Adaptativa 🆕

**Estado:** Planificado (Inicio Mayo 2025)

**Objetivo:** Reingeniar el agente para una interacción más natural, fluida y contextualmente relevante.

**Entregables:**
- Integración con LLM para extracción avanzada de entidades
- Personalización de respuestas usando el nombre y datos del usuario
- Implementación de memoria conversacional para referencias a información previa
- Transiciones condicionales en el grafo basadas en contexto
- Respuestas generadas dinámicamente según el perfil del usuario
- Detección básica de intenciones del usuario mediante NLP
- Reconocimiento de Entidades Nombradas (NER) para identificar nombres y ubicaciones

**Issues relacionados:** #9 (parcial)

## Fase 3: Flujo Conversacional Avanzado 🔜

**Estado:** Planificado

**Objetivo:** Implementar un flujo conversacional completamente adaptativo con comprensión avanzada.

**Entregables:**
- Detección de intenciones complejas del usuario
- Rutas totalmente dinámicas en el grafo conversacional
- Manejo sofisticado de respuestas incompletas y correcciones
- Sistema de aclaración automática ante ambigüedades
- Comprensión de lenguaje natural avanzada
- Detección de preferencias implícitas
- Manejo de interrupciones en el flujo (preguntas o cambios de tema)

## Fase 4: Match y Recomendación Inteligente 🔜

**Estado:** Planificado

**Objetivo:** Integrar sistema de recomendación de propiedades y mejorar engagement.

**Entregables:**
- Integración con API de proyectos inmobiliarios
- Algoritmo de matching basado en preferencias explícitas e implícitas
- Presentación conversacional de propiedades relevantes
- Sistema de feedback del usuario sobre recomendaciones
- Seguimiento de interacciones para aprendizaje continuo
- Integración con CRM para el seguimiento de leads
- Funcionalidad de búsqueda semántica de propiedades

## Fase 5: Optimización y Expansión 🔜

**Estado:** Planificado

**Objetivo:** Maximizar tasas de conversión y expandir capacidades del sistema.

**Entregables:**
- A/B testing de diferentes estrategias conversacionales
- Optimización basada en analítica de conversaciones
- Multimodalidad (integración de imágenes y enlaces interactivos)
- Expansión a múltiples canales (WhatsApp, Telegram, Web, etc.)
- Implementación de un dashboard para análisis de conversiones
- Personalización avanzada basada en perfiles de usuario
- Generación automática de propuestas de valor

---

*Este roadmap es un documento vivo y puede ser ajustado según las necesidades del proyecto y feedback recibido.*
*Última actualización: 16 de abril de 2025*