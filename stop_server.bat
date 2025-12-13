@echo off
echo Deteniendo servidor web si está en ejecución...

powershell -Command "try { $procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*web_dashboard.py*' }; if ($procs) { foreach ($p in $procs) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue; Write-Host 'Detenido proceso PID' $p.ProcessId } } else { Write-Host 'No se encontraron procesos web_dashboard.py en ejecución.' }; Remove-Item -Path 'web_server.log','web_server_error.log' -Force -ErrorAction SilentlyContinue; Write-Host 'Logs eliminados.' } catch { Write-Host 'Error: ' $_ }"
echo Listo.
pause >nul
