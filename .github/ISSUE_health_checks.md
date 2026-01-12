Título: Implementar health checks automáticos para el dashboard y servicios

Descripción:
`docs/workflow-log.md` recomienda implementar health checks automáticos para el dashboard.

Problema:
Sin health checks no hay forma automática de detectar degradaciones del servicio o recuperar procesos.

Pasos sugeridos:
- Añadir endpoints de health (liveness/readiness) en el backend y en el servicio del dashboard.
- Añadir monitoreo y alertas (Prometheus + Alertmanager o similar).
- Integrar checks en CI (smoke tests) y en scripts de despliegue.

Asignado sugerido: @doski2
Labels sugeridos: `ops`, `monitoring`