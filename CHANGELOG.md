# Train Simulator Autopilot - Registro de Cambios

## [Unreleased] - 13/01/2026

Este repositorio mantiene un historial completo de cambios en `archivado/CHANGELOG_2026-01-13.md`.

**Resumen (highlights):**

- Modernización del sistema y mejoras en CI / tests.
- Herramientas: auto-etiquetado de issues y utilidades de mantenimiento.
- Pendientes: optimizaciones de rendimiento y pruebas E2E en Windows.

#### Cambios recientes (pendiente de release)

- **CI / Tests:** Añadidos helpers para ejecutar tests en Windows (`scripts/run_tests.ps1`, `scripts/run_tests.bat`) y **nuevo workflow** Windows que ejecuta la suite y sube un JUnit report (PR #74). Se corrigieron problemas de invocación PowerShell, se instaló primero `requirements.txt` para evitar fallos en la colección, y se añadió cache de pip (`.pip-cache`) para acelerar runs.
- **Diagnóstico:** Captura automática de stdout/stderr de pytest (`pytest-output.txt`, `pytest-error.txt`) y subida de esos logs como artifact solo en caso de fallo para facilitar el diagnóstico de flakes.
- **Docs:** `CONTRIBUTING.md` actualizado para recomendar los nuevos atajos de test en Windows. 
- **Seguridad / Fiabilidad:** Asegurado que comandos críticos (p.ej. `emergency_brake`) no sean silenciados si la escritura al archivo de comandos falla: `enviar_comandos` ahora devuelve `False` cuando la escritura principal falla y se añaden pruebas unitarias que cubren este caso.
- **Seguridad:** Añadida autenticación por API key para endpoints sensibles (`/api/commands`, `/api/control/<action>`) y pruebas unitarias asociadas; configurable vía `API_KEYS` o `API_KEY` (env).

(Ver PR #74 y PR #76 para detalles y ejecuciones validadas.)
- **Docs:** Añadido un JSON Schema para `telemetry_update` en `docs/schemas/telemetry_update.schema.json` y pruebas que validan payloads contra el esquema (`tests/unit/test_telemetry_schema.py`).

Para ver el historial completo con todos los detalles y entradas antiguas, consulta:

`archivado/CHANGELOG_2026-01-13.md`

---

### Cómo añadir una entrada

- Abre un PR que añada una sección concisa en *Unreleased* siguiendo el formato "Keep a Changelog" (título, fecha y entradas breves).  
- Incluye una breve verificación o pruebas que aseguren que el cambio está probado.

---

(El historial completo fue movido a `archivado/CHANGELOG_2026-01-13.md`.)
