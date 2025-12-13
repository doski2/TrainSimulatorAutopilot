try {
    Remove-Item -Path 'web_server.log','web_server_error.log' -Force -ErrorAction SilentlyContinue
} catch { }

# Start Python web server; logs will be redirected
Start-Process -NoNewWindow -FilePath 'python' -ArgumentList 'web_dashboard.py' -RedirectStandardOutput 'web_server.log' -RedirectStandardError 'web_server_error.log'
Start-Sleep -Seconds 2

# Find the process ID for the launched web server
$p = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*web_dashboard.py*' } | Select-Object -First 1
if ($p) {
    Write-Host "Servidor web iniciado con PID $($p.ProcessId)"
    $watchArgs = ('-NoProfile -ExecutionPolicy Bypass -File "scripts\\wait_and_cleanup.ps1" -processid {0}' -f $p.ProcessId)
    Start-Process -NoNewWindow -FilePath 'powershell' -ArgumentList $watchArgs
} else {
    Write-Host "No se encontró proceso web_dashboard.py"
}