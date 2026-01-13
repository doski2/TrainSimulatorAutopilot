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

(Ver PR #74 para detalles y ejecución validada: run 20975308347 — 145 passed, 1 skipped.)

Para ver el historial completo con todos los detalles y entradas antiguas, consulta:

`archivado/CHANGELOG_2026-01-13.md`

---

### Cómo añadir una entrada

- Abre un PR que añada una sección concisa en *Unreleased* siguiendo el formato "Keep a Changelog" (título, fecha y entradas breves).  
- Incluye una breve verificación o pruebas que aseguren que el cambio está probado.

---

(El historial completo fue movido a `archivado/CHANGELOG_2026-01-13.md`.)
