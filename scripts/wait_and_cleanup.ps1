param([int]$processid)
try {
    if ($processid -ne $null) {
        Write-Host "Esperando proceso con PID $processid..."
        Wait-Process -Id $processid -ErrorAction SilentlyContinue
    }
} catch {
    Write-Host "Error esperando proceso: $_"
}
try {
    Remove-Item -Path "web_server.log","web_server_error.log" -Force -ErrorAction SilentlyContinue
    Write-Host "Logs eliminados por wait_and_cleanup.ps1"
} catch {
    Write-Host "Error eliminando logs: $_"
}
