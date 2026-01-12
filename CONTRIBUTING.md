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

## Preguntas
Para preguntas sobre estilo o convenciones, crea un issue y etiqueta `pregunta`.
