Título: Evaluar e implementar optimizaciones de WebSocket (perf + compresión)

Descripción:
`docs/workflow-log.md` recomienda evaluar optimizaciones de rendimiento para WebSocket; además, para alto volumen se sugiere considerar compresión.

Problema:
En situaciones de alto throughput (múltiples locomotoras, 100ms), los mensajes WebSocket pueden convertirse en cuello de botella.

Pasos sugeridos:
- Medir throughput y latencia actual en escenarios de carga.
- Probar opciones: comprimir payloads (gzip/snappy), usar frames binarios en lugar de JSON, o agrupar mensajes.
- Implementar tests que validen reducción de latencia y uso de CPU/NET.
- Documentar cambios en `docs/` y en la sección de operaciones.

Asignado sugerido: @doski2
Labels sugeridos: `performance`, `backend`, `enhancement`