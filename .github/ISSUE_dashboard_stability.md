Título: Monitorizar estabilidad del dashboard con diferentes locomotoras

Descripción:
En `docs/workflow-log.md` aparece una tarea pendiente: "Monitorear estabilidad del dashboard con diferentes locomotoras".

Problema:
No hay tareas/PRs rastreando específicamente la verificación de estabilidad con distintos modelos de locomotoras y formaciones (multilocomotora). Esto puede ocultar errores específicos por tipo de motor/archivo de datos.

Pasos sugeridos:
- Diseñar y automatizar pruebas E2E que simulen diferentes locomotoras y formaciones (small/medium/large).
- Añadir datasets de test (mock) con muestras representativas para cada tipo.
- Ejecutar pruebas en CI (marcadas con `e2e` y `simulator` cuando requieran datos reales) y guardar logs.
- Reportar fallos y añadir clasificaciones por criticidad.

Asignado sugerido: @doski2
Labels sugeridos: `testing`, `e2e`, `needs-investigation`