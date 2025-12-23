# Prometheus configuration for Train Simulator Autopilot ✅

This folder contains a minimal Prometheus configuration to scrape the project's `/metrics` endpoint and a small set of alerting rules useful for development and local testing.

Files:
- `prometheus.yml` - Prometheus main configuration (scrapes `localhost:5001/metrics` by default)
- `rules.yml` - Example alert rules (read/write retries, IA latency, alert rate)

Quick start (Docker):
```bash
# Run Prometheus using official image and mount this directory as /etc/prometheus
docker run --rm -p 9090:9090 -v $(pwd)/prometheus:/etc/prometheus prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yml
```

Quick start with docker-compose (recommended for local dev):
```bash
# Start Prometheus service defined in project docker-compose
docker-compose up -d prometheus
# Check readiness
curl http://localhost:9090/-/ready
```

Notes:
- Adjust the `targets` list in `prometheus.yml` if your dashboard runs on a different host or port (e.g., `host.docker.internal:5001`).
- The alert rules are intentionally conservative; tune thresholds for your environment before enabling them in production.
- To test alerts locally you can use `promtool` or trigger synthetic conditions by calling `/metrics` endpoints with mocked metric values.

Suggested next steps:
- Add Grafana for visualization and rule evaluation.
- Consider adding a lightweight Prometheus container to CI for rules validation (e.g., use promtool).
