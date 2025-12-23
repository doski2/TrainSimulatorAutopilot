# Ejecutar pruebas End-to-End (E2E)

Este documento explica cómo ejecutar las pruebas de integración end-to-end localmente.

Requisitos:
- Docker y docker-compose instalados
- Entorno Python activado (virtualenv con dependencias instaladas)

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
- Levanta el servicio `prometheus` definido en `docker-compose.yml` para que las reglas puedan evaluarse si es necesario.
- Inicia el `web_dashboard` en segundo plano.
- Espera a que `/metrics` esté disponible y ejecuta las pruebas en `tests/integration`.
- Detiene el servidor del dashboard al finalizar (Prometheus queda en ejecución para facilitar la depuración).

Notas de diagnóstico:
- Si el script falla añadiendo `--maxfail=1 -x` a pytest puede ayudar a identificar el primer fallo.
- Para detener Prometheus: `docker-compose stop prometheus` o `docker-compose rm -f prometheus`.
