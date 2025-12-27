Resumen

Este PR elimina el soporte de ACK basado en archivos para la activación del piloto automático y depreca la PoC 'file+ACK'. Incluye los siguientes cambios principales:

- Código:
  - Eliminada la espera/blocks por ACK en `POST /api/control/start_autopilot` y `/api/commands`.
  - `/api/commands` ahora encola atómicamente y devuelve 202 (queued) siempre; `wait_for_ack` queda ignorado.
  - `tools.poc_file_ack` ha sido eliminado del árbol de código y sus tests dependientes han sido borrados.
  - Métricas relacionadas con ACK eliminadas (`ack_skipped_total`, `unacked_total`).

- Tests:
  - Los tests E2E/Unit que verificaban los flujos ACK/PoC fueron marcados como omitidos (skipped) y los tests de API actualizados para reflejar la nueva semántica (202 queued).

- Docs y configuración:
  - `docs/AUTOPILOT_SENDCOMMAND.md`, `docs/CONTROLS.md`, `docs/ROADMAP_TO_AUTOPILOT.md` actualizados para documentar la eliminación del ACK y las razones (plugin inconsistente y problemas de I/O en Windows).
  - `config.ini.example` actualizado con nota indicando que el soporte de ACK fue eliminado.
  - `CHANGELOG.md` actualizado con la decisión y el rationale.

Evidencia y verificación

- Suite de tests local: `147 passed, 20 skipped` (ejecución completa).
- Pruebas manuales: `POST /api/control/start_autopilot` ahora devuelve 200 y escribe `start_autopilot` + fallback `Regulator:0.125` y `VirtualThrottle:0.125` cuando el plugin no está cargado.

Razonamiento

- Se observaron fallos en producción/entornos locales: el plugin no se cargaba en ocasiones y las escrituras a archivos en Windows fallaban por `Access denied` / `file locked`. Dado que el ACK era poco fiable y hacía la API frágil, decidimos eliminar la dependencia del ACK y optar por un comportamiento más robusto (siempre encolar y aplicar fallback).

Notas de migración y rollback

- La PoC queda deprecada en `tools/poc_file_ack/DEPRECATED.md` — si es necesario reactivar la PoC, se recomienda moverla a `tools/deprecated/` y restablecer pruebas/E2E en una rama separada.

Solicito revisión enfocada en:
- Validación de riesgos operativos y compatibilidad hacia atrás (se mantiene escritura en `autopilot_commands.txt` para compatibilidad).
- Revisión de la documentación y del texto de `CHANGELOG.md` para asegurarnos de que la justificación es clara para operadores.

Si se acepta, procederé a: (opcional) mover `tools/poc_file_ack` a `tools/deprecated/` y cerrar/omitir completamente los artefactos PoC en la rama principal.
