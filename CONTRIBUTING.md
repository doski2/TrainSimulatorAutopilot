# Contribuir al proyecto Train Simulator Autopilot

Gracias por contribuir. Por favor sigue estas pautas simples para mantener la consistencia del proyecto.

## Formato de fechas (estándar)
- **Formato para documentación legible:** usar **DD/MM/YYYY** (ej.: `13/01/2026`).
- **Excepción:** los **nombres de archivo** que contienen fechas (p. ej. `CHANGELOG_2026-01-13.md`) y los **timestamps de datos o registros** deben conservar el formato ISO (YYYY-MM-DD o ISO-8601) para compatibilidad y orden cronológico.

## Changelogs
- Añade una entrada concisa en `CHANGELOG.md` bajo *Unreleased* cuando tu cambio afecte la funcionalidad o la API.
- Usa la fecha en el encabezado en formato `DD/MM/YYYY`.

## Pull Requests
- Describe brevemente qué se hizo y por qué.
- Si la PR requiere una entrada en el changelog, marca la PR con la etiqueta `mejora` o `bug` y añade la entrada al `CHANGELOG.md` o indica que un mantenedor lo hará.

## Código y Estilo
- Python: PEP 8
- JavaScript: ESLint
- Usar `pytest` para tests y asegúrate de que pasen en CI antes de pedir revisión.

## Entorno de desarrollo y tests
Sigue estos pasos para preparar tu entorno de desarrollo y ejecutar tests localmente:

1. Crear y activar un entorno virtual:
   - Linux/macOS:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

2. Instalar dependencias de desarrollo:

```bash
pip install -r requirements-dev.txt
```

3. Ejecutar tests:

```bash
# Ejecutar toda la suite de tests unitarios
pytest -q

# Ejecutar un test específico
pytest tests/unit/test_tsc_integration.py::test_leer_datos_retries_on_permission_error -q

# Si un test es flaky localmente, puedes reintentar automáticamente
pytest --maxfail=1 --reruns 2
```

**Atajo para Windows (recomendado si tienes problemas de entorno):**
- Ejecuta `scripts\run_tests.ps1` (PowerShell) o `scripts\run_tests.bat` (CMD) desde la raíz del repo; los scripts usarán la Python del virtualenv `.venv` y aceptan los mismos argumentos que `pytest`.

4. Ejecutar tests de integración Windows (si necesitas pruebas que interactúen con RailWorks):

```bash
# Desde GitHub CLI: dispara la job Windows que ejecuta tests con marca 'simulator'
gh workflow run windows-ci.yml --ref master -f run_integration=true
```

Notas:
- Si faltan paquetes (por ejemplo `matplotlib`), instala `pip install -r requirements-dev.txt` o `pip install matplotlib`.
- La job de CI Windows ya aplica reintentos (`--reruns 2`) para mitigar flakes intermitentes.

## Preguntas
Para preguntas sobre estilo o convenciones, crea un issue y etiqueta `pregunta`.
