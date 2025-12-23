#!/usr/bin/env bash
set -euo pipefail

# Script para arrancar Prometheus usando docker-compose
COMPOSE_FILE="docker-compose.yml"
SERVICE_NAME="prometheus"

echo "Starting Prometheus service via docker-compose..."
docker-compose -f "$COMPOSE_FILE" up -d $SERVICE_NAME

echo "Waiting for Prometheus to become available on http://localhost:9090 ..."
for i in {1..20}; do
  if curl --silent --fail http://localhost:9090/-/ready > /dev/null; then
    echo "Prometheus is ready."
    exit 0
  fi
  sleep 1
done

echo "Warning: Prometheus did not become ready in time. Check 'docker logs prometheus' for details." 
exit 1
