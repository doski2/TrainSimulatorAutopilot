Hola @doski2,

Solicito tu revisión de este PR que actualiza las instrucciones del agente y añade un ejemplo de workflow Windows.

Instrucciones para ejecutar las pruebas de integración (Windows):

- En la UI: ve a la pestaña **Actions** → selecciona "CI (Windows example)" → "Run workflow" → elige la rama `docs/update-copilot-instructions` → fija `run_integration=true` y ejecuta.
- Desde CLI (opcional):

  gh workflow run windows-ci.yml --ref docs/update-copilot-instructions -f run_integration=true

Notas:

- Las pruebas de integración deben estar marcadas con `@pytest.mark.simulator` y requieren archivos de RailWorks (`GetData.txt`, `SendCommand.txt`).
- Si quieres, puedo lanzar la ejecución y reportar los resultados aquí.

Gracias!
