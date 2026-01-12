Título: Reemplazar placeholders en `template_telemetry_documentation.txt` por métodos/scripts reales

Descripción:
`docs/template_telemetry_documentation.txt` contiene placeholders (`[SCRIPT/MÉTODO_DE_CAPTURA]`) que deberían ser sustituidos por scripts y procedimientos reales (p. ej. `Railworks_GetData_Script.lua`, `debug_tsc.py`).

Problema:
La plantilla no es directamente usable hasta que no se especifiquen los scripts y métodos de captura de datos; esto dificulta reproducir y documentar telemetría.

Pasos sugeridos:
- Revisar scripts existentes (`Railworks_GetData_Script.lua`, `debug_fetch.py`, `debug_tsc.py`) y documentar cuál se usa para cada flujo.
- Reemplazar placeholders en la plantilla con ejemplos y comandos de captura.
- Añadir un ejemplo mínimo de archivo generado y un script para capturar telemetría de prueba.

Asignado sugerido: @doski2
Labels sugeridos: `documentation`, `telemetry`