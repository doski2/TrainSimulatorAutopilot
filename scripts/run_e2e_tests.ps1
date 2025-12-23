param()

# Run end-to-end tests for Train Simulator Autopilot (PowerShell)
# Starts Prometheus, launches the dashboard, waits for /metrics and runs integration tests

Push-Location (Join-Path $PSScriptRoot '..')

Write-Host "Starting Prometheus (docker-compose)..."
docker-compose up -d prometheus | Out-Null

Write-Host "Starting web dashboard..."
$proc = Start-Process -FilePath (Get-Command python).Source -ArgumentList 'web_dashboard.py' -NoNewWindow -PassThru

Write-Host "Waiting for /metrics at http://127.0.0.1:5001/metrics ..."
$max = 30
for ($i = 0; $i -lt $max; $i++) {
    try {
        $r = Invoke-WebRequest -Uri http://127.0.0.1:5001/metrics -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { Write-Host "Dashboard /metrics available"; break }
    } catch { Start-Sleep -Seconds 1 }
}

Write-Host "Running integration tests with pytest..."
& (Get-Command python).Source -ArgumentList '-m', 'pytest', 'tests/integration', '-q'
$exit = $LASTEXITCODE

Write-Host "Stopping dashboard process (Id: $($proc.Id))"
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue

Pop-Location

exit $exit
