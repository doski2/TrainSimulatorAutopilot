Título: Soportar/verificar telemetría de alta frecuencia (100ms)

Descripción:
En `docs/workflow-log.md` se sugiere verificar el funcionamiento con datos de alta frecuencia (100ms). Necesitamos pruebas y posiblemente optimizaciones para manejar 10Hz.

Problema:
El pipeline de lectura/proceso/emitido puede no estar preparado para 100ms: latencias, colas, y CPU/rate-limits pueden provocar pérdida de datos o bloqueos.

Pasos sugeridos:
- Crear mocks y fixtures que emulen telemetría a 100ms.
- Ejecutar pruebas de carga localmente y en CI (Windows runner para tests que dependan de TSC).
- Medir latencias y pérdidas, identificar cuellos de botella (I/O, parsing, WebSocket).
- Proponer mejoras (batching, desacoplamiento con colas, worker pool).

Asignado sugerido: @doski2
Labels sugeridos: `performance`, `testing`, `needs-investigation`