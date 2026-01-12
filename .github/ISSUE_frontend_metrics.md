Título: Añadir métricas de rendimiento frontend para el dashboard

Descripción:
`docs/workflow-log.md` sugiere agregar métricas de rendimiento del frontend.

Problema:
Sin métricas frontend (RUM/telemetría de rendimiento) es difícil priorizar optimizaciones y detectar regresiones UX.

Pasos sugeridos:
- Instrumentar métricas como: tiempo de carga, time-to-interactive, FPS en gráficas y tiempos de renderización.
- Reportar a Prometheus (o endpoint) o usar herramientas RUM (Sentry/Datadog) si aplica.
- Añadir pruebas E2E que verifiquen limites de rendimiento en escenarios críticos.

Asignado sugerido: @doski2
Labels sugeridos: `frontend`, `monitoring`