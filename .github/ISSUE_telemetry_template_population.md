Título: Completar / poblar plantillas de telemetría (TSC y otros)

Descripción:
`docs/TELEMETRY_TEMPLATE_README.md` y `docs/template_telemetry_documentation.txt` contienen placeholders y estados `[PENDIENTE]` que requieren ser completados para TSC y otros simuladores.

Problema:
Falta documentación completa de las variables telemétricas implementadas vs pendientes, y las capturas (scripts/métodos) asociadas.

Pasos sugeridos:
- Crear/actualizar archivos de telemetría concretos (ej.: `docs/telemetry_tsc.md`) usando la plantilla.
- Reemplazar `[SCRIPT/MÉTODO_DE_CAPTURA]` por el script real (`Railworks_GetData_Script.lua` o `debug_tsc.py`) y documentar la ruta.
- Marcar variables con `[IMPLEMENTADO]/[PENDIENTE]` y añadir ejemplos JSON de salida.
- Añadir checklist y tests que validen la presencia de campos clave.

Asignado sugerido: @doski2
Labels sugeridos: `documentation`, `telemetry`