# Web Dashboard API

Documentación específica para la API del dashboard web. Para la referencia
completa, consulte `API_REFERENCE.md`.

## Endpoints Principales

- `GET /api/status` - Estado del servidor
- `GET /api/telemetry` - Telemetría actual
  - Telemetría incluye claves: `velocidad_actual`, `aceleracion`, `rpm`,
`presion_tubo_freno`, `senal_principal`, `senal_avanzada`, `senal_procesada`.
- `POST /api/control/*` - Comandos de control del sistema
