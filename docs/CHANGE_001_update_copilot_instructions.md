Resumen: Adapté y amplié `.github/copilot-instructions.md` para reflejar reglas y prácticas específicas del proyecto TrainSimulatorAutopilot.

Qué se cambió:

- Añadidas secciones de auditoría y revisión continua ("Regla: revisar y auditar continuamente").
- Añadidas recomendaciones y comandos para pruebas locales y depuración (`debug_fetch.py`, `debug_tsc.py`, `start.bat`).
- Añadidas reglas explícitas de CI: pruebas que interactúan con archivos del simulador (`GetData.txt`, `SendCommand.txt`) deben ejecutarse en `windows-latest`.
- Añadidas convenciones para PRs grandes y documentación requerida (`docs/CHANGE_X.md`).

Por qué:

- La base de código depende de E/S de archivos del simulador y entornos Windows; la guía anterior era incompleta en reglas de CI y pruebas locales.
- Facilitar que agentes y contribuidores sigan prácticas consistentes y eviten duplicados.

Cómo probar los cambios localmente:

1. Abrir el archivo modificado: `.github/copilot-instructions.md`.
2. Verificar que las nuevas secciones aparecen y que los comandos referenciados (`python web_dashboard.py`, `cd dashboard && npm start`, `python -m pytest -v`) existen y funcionan en tu entorno.
3. Ejecutar pruebas unitarias: `python -m pytest tests/ -q`.
4. Probar el flujo de depuración con `debug_tsc.py` o `debug_fetch.py` para generar datos de telemetría de prueba.

Notas adicionales:

- Si prefieres que añada un ejemplo de job de GitHub Actions (Windows) para correr las suites de integración, puedo prepararlo en un commit separado.
- Si quieres que abra el PR con título y descripción listos, lo preparo y lo subo (necesito confirmación para crear la rama y el PR).
