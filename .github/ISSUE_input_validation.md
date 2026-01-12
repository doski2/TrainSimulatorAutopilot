Título: Añadir validaciones más robustas para datos entrantes de telemetría

Descripción:
`docs/workflow-log.md` recomienda agregar más validaciones de datos de entrada.

Problema:
Entradas inválidas o malformadas pueden propagarse y causar errores en la IA o dashboards.

Pasos sugeridos:
- Definir un esquema de validación (pydantic/dataclass+validators) para la telemetría.
- Añadir tests unitarios que validen entradas edge-case (valores nulos, tipos incorrectos, límites).
- Integrar validación antes de procesar/emitir datos y añadir logs de error con métricas.

Asignado sugerido: @doski2
Labels sugeridos: `bug`, `testing`, `enhancement`