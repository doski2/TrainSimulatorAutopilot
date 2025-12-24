Add-Content -Path '.\scripts\plugin_monitor.log' -Value "test write $(Get-Date -Format o)"
Get-Content -Path '.\scripts\plugin_monitor.log' -Tail 20