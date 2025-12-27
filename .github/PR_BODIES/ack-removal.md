PR: Eliminación y deprecación de PoC Archivo+ACK — Resumen de artefactos eliminados

Resumen breve

Este PR depreca y elimina el PoC de confirmación por archivo ("Archivo+ACK") y purga los artefactos dependientes. La decisión se tomó por motivos de robustez operativa (ACK poco fiable, problemas de I/O en Windows) y para simplificar el flujo: ahora el servidor encola comandos de forma atómica y no espera confirmación por archivo.

Evidencia de verificación local

- Suite de tests (local): 145 passed, 1 skipped
- Linter (ruff): sin errores locales

Artefactos eliminados (selección representativa)

- Código PoC:
  - `tools/poc_file_ack/` (package eliminado por completo)

- Tests E2E / integración relacionados con el PoC:
  - `tests/e2e/test_file_ack.py` (eliminado)
  - `tests/integration/test_e2e_autopilot_file_ack.py` (eliminado)
  - `tests/e2e/test_probe_file.py`, `tests/e2e/test_retries.py`, `tests/e2e/test_persist_ids.py` (eliminados)

- Tests unitarios dependientes del consumer / PoC (ejemplos):
  - Varias pruebas `tests/unit/test_consumer_*.py` relacionadas con la PoC fueron eliminadas o marcadas como omitidas para reducir ruido y mantenimiento.

- CI / Workflows:
  - `.github/workflows/poc-e2e.yml` (el job específico para la PoC fue retirado)

- Documentación / UI / Scripts:
  - `docs/docs controles/opcion1_archivo_ack.md` (eliminado)
  - `docs/docs controles/ack_implementation_steps.md` (eliminado)
  - POC UI block removido en `web/static/js/dashboard.js` (se eliminó solo el fragmento POC)
  - Limpieza en `docs/AUTOPILOT_SENDCOMMAND.md` para reflejar que la confirmación por archivo ya no es obligatoria

Notas de migración y rollback

- Si decidimos recuperar el PoC más adelante, podemos crear un branch con el snapshot histórico antes de este PR y mover `tools/poc_file_ack` a `tools/deprecated/poc_file_ack` en una PR separada.

Acción solicitada

- Propongo mergear esta rama (`feature/doc-autopilot-sendcommand`) una vez que CI remoto esté verde. La rama incluye la actualización de `CHANGELOG.md` y pruebas/linters locales ya pasan.

(Archivo generado automáticamente por el equipo de mantenimiento — incluye lista de artefactos eliminados para facilitar revisión humana y auditoría.)