Título: CI: fallo en Windows — test_leer_datos_retries_on_permission_error (metrics read latency = 0.0)

Descripción:
Durante la ejecución del workflow `CI (Windows example)` en la rama `docs/update-copilot-instructions` hubo un fallo del test unitario `tests/unit/test_tsc_integration.py::test_leer_datos_retries_on_permission_error`.

Detalles del run:

- Run ID: 20921148757
- Workflow: CI (Windows example)
- Estado: completado (exit code 1)
- Resultado: 1 failed, 144 passed, 1 skipped
- Enlace al run: <https://github.com/doski2/TrainSimulatorAutopilot/actions/runs/20921148757>
- PR relacionado: <https://github.com/doski2/TrainSimulatorAutopilot/pull/23>

Fallo observado (extracto):

- Test: tests/unit/test_tsc_integration.py::test_leer_datos_retries_on_permission_error
- Aserción que falla: `assert metrics["read_last_latency_ms"] > 0.0`
- Mensaje: E   assert 0.0 > 0.0  (metrics["read_last_latency_ms"] fue 0.0)
- Línea aproximada del test: 240

Pasos para reproducir localmente:

1. Ejecutar unitario específico:

   ```bash
   python -m pytest tests/unit/test_tsc_integration.py::test_leer_datos_retries_on_permission_error -q
   ```

2. O bien disparar el workflow con integración Windows (ejemplo):

   ```bash
   gh workflow run windows-ci.yml --ref docs/update-copilot-instructions -f run_integration=true
   ```

Hipótesis iniciales / puntos a investigar:

- El test espera que, tras un error de permiso y reintentos, la métrica `read_last_latency_ms` se registre con un valor > 0.0; en este run quedó en 0.0.
- Posible causa: el código que mide/guarda `read_last_latency_ms` no se ejecutó en la ruta de error, o el mocking de tiempo/latencia en el test no se aplicó en Windows, o la conversión de unidades produjo 0.

Siguientes pasos sugeridos:

- Reproducir localmente el test en Windows (o en runner windows-latest) para inspeccionar logs y variables intermedias.
- Revisar `tsc_integration.py` en la zona que calcula `read_last_latency_ms` y el test que simula el PermissionError para asegurar que la métrica se registra incluso en casos de fallo y reintento.
- Añadir un log temporal o ajustar el test para capturar la cadena de llamadas en fallo.

Etiquetas sugeridas: `ci-failure`, `bug`, `needs-investigation`

Asignado sugerido: @doski2

Si quieres, hago la investigación inicial y propongo un PR de corrección.
