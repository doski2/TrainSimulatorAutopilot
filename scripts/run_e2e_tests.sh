#!/usr/bin/env bash
set -euo pipefail

# Run end-to-end tests for Train Simulator Autopilot
# - Starts Prometheus (docker-compose service 'prometheus')
# - Starts the web dashboard in background
# - Waits until /metrics is reachable
# - Runs pytest on integration tests

# Ensure we're in project root
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Start Prometheus (best-effort)
echo "Starting Prometheus..."
docker-compose up -d prometheus || echo "Prometheus service may already be running"

# Start dashboard in background
echo "Starting web dashboard..."
python web_dashboard.py &
DASH_PID=$!

# Wait for /metrics readiness
echo "Waiting for dashboard /metrics to be available..."
for i in {1..30}; do
  if curl --silent --fail http://127.0.0.1:5001/metrics > /dev/null; then
    echo "Dashboard /metrics available"
    break
  fi
  sleep 1
done

# Run integration tests
echo "Running integration tests..."
pytest tests/integration -q
PYTEST_EXIT=$?

# Cleanup: stop dashboard
echo "Stopping web dashboard (pid=$DASH_PID)..."
kill $DASH_PID || true

# Optionally: stop prometheus? (left running for debugging)
# docker-compose stop prometheus || true

exit $PYTEST_EXIT
