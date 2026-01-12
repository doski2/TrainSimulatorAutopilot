# Ejecutar pruebas End-to-End (E2E)

**Revisado:** 13/01/2026 — Revisado por @doski2 ✅

Este documento explica cómo ejecutar las pruebas de integración end-to-end localmente.

Requisitos:

- Docker instalado y disponible (compatible con Docker Compose v1 o v2; tener `docker-compose` o `docker compose` en PATH)
- Entorno Python activado **(Python 3.9+ recomendado, virtualenv con dependencias instaladas)**
- `pytest` y dependencias de `requirements.txt` instaladas en el entorno
- (Windows) PowerShell 5.1 o PowerShell Core para ejecutar los scripts `.ps1`

Pasos rápidos (Linux/macOS):

1. Asegúrate de tener dependencias instaladas:

   ```bash
   pip install -r requirements.txt
   ```

2. Arranca Prometheus y el dashboard y ejecuta las pruebas E2E:

   ```bash
   ./scripts/run_e2e_tests.sh
   ```

Pasos en Windows (PowerShell):

1. Instala dependencias si no lo hiciste:

   ```powershell
   pip install -r requirements.txt
   ```

2. Ejecuta el script de pruebas E2E:

   ```powershell
   .\scripts\run_e2e_tests.ps1
   ```

Qué hace el script:

- Levanta el servicio `prometheus` definido en `docker-compose.yml` para que
  las reglas puedan evaluarse si es necesario (puerto Prometheus: 9090).
- Inicia el `web_dashboard` en segundo plano (puerto por defecto: 5001).
- Espera a que `/metrics` esté disponible (`http://127.0.0.1:5001/metrics`) y ejecuta las pruebas en `tests/integration`.
- Detiene el servidor del dashboard al finalizar; **Prometheus se deja en ejecución** por defecto para facilitar la depuración.

Notas y troubleshooting:

- Si tu instalación usa Docker Compose v2 (`docker compose`), asegúrate de que el comando sea accesible en tu PATH o crea un alias `docker-compose` para compatibilidad.
- Si `/metrics` no se vuelve disponible: verifica que el dashboard esté arrancado en el puerto correcto (`FLASK_PORT` / 5001), revisa logs con `python web_dashboard.py` y asegúrate de que no haya firewall bloqueando el puerto.
- Para detener Prometheus después de la ejecución:
  - con Docker Compose v1: `docker-compose stop prometheus`
  - con Docker Compose v2: `docker compose stop prometheus`
- Si el script falla, ejecutar `pytest` con `--maxfail=1 -x` puede ayudar a identificar el primer fallo.

Notas de diagnóstico:

- Si el script falla, añadir `--maxfail=1 -x` a pytest puede ayudar a
  identificar el primer fallo.
- Para detener Prometheus: `docker-compose stop prometheus` o `docker-compose rm -f prometheus` (o `docker compose stop prometheus` si usas Docker Compose v2).

Mejoras recomendadas (se han creado issues si procede):

- Añadir soporte en los scripts para detectar y usar `docker compose` cuando `docker-compose` no exista, y documentar este comportamiento. (Issue creado)
- Añadir opción `--cleanup` para detener/remover Prometheus al finalizar la ejecución (Issue creado)
- Considerar una job opcional de CI que ejecute una versión reducida del E2E (smoke test) en runners Linux para detectar regresiones (Issue creado)
