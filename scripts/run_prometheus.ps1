param()

Write-Host "Starting Prometheus service using docker-compose..."
docker-compose -f "docker-compose.yml" up -d prometheus

Write-Host "Waiting for Prometheus to be ready at http://localhost:9090"
$max = 30
for ($i = 0; $i -lt $max; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri http://localhost:9090/-/ready -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            Write-Host "Prometheus is ready."
            exit 0
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}
Write-Warning "Prometheus was not ready within the expected time. Check container logs: docker logs prometheus"
exit 1
