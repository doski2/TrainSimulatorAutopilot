# Configuración de Prometheus para Train Simulator Autopilot ✅

Esta carpeta contiene una configuración mínima de Prometheus para "scrapear"
el endpoint `/metrics` del proyecto y un conjunto reducido de reglas de alerta
útiles para desarrollo y pruebas locales.

Archivos:

- `prometheus.yml` - Configuración principal de Prometheus (raspa
  `localhost:5001/metrics` por defecto).
- `rules.yml` - Reglas de alerta de ejemplo (reintentos de lectura/escritura,
  latencia de IA, tasa de alertas).

Arranque rápido (Docker):

```bash
# Ejecutar Prometheus con la imagen oficial y montar esta carpeta
docker run --rm -p 9090:9090 \
  -v $(pwd)/prometheus:/etc/prometheus \
  prom/prometheus --config.file=/etc/prometheus/prometheus.yml
```

Arranque rápido con docker-compose (recomendado para dev local):

```bash
# Levantar el servicio Prometheus definido en docker-compose
docker-compose up -d prometheus
# Verificar que Prometheus esté listo
curl http://localhost:9090/-/ready
```

Notas:

- Ajusta la lista `targets` en `prometheus.yml` si el dashboard se ejecuta en
  otro host o puerto (p. ej., `host.docker.internal:5001`).
- Las reglas de alerta son intencionalmente conservadoras; ajústalas a tu
  entorno antes de activarlas en producción.
- Para probar alertas localmente puedes usar `promtool` o generar condiciones
  sintéticas invocando `/metrics` con valores simulados.

Siguientes pasos sugeridos:

- Añadir Grafana para visualización y evaluación de reglas.
- Considerar añadir un contenedor ligero de Prometheus en CI para validar
  las reglas (p. ej., usando `promtool`).
