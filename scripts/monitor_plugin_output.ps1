param(
    [string]$PluginsDir = 'C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins',
    [int]$IntervalSeconds = 5,
    [switch]$RunOnce
)

$logFile = Join-Path $PSScriptRoot 'plugin_monitor.log'
function Log { param($m) $line = "$(Get-Date -Format o) - $m"; Add-Content -Path $logFile -Value $line; Write-Output $line }

Log "Starting plugin monitor (PluginsDir=$PluginsDir, Interval=$IntervalSeconds, RunOnce=$RunOnce)"

while ($true) {
    try {
        $statePath = Join-Path $PluginsDir 'autopilot_state.txt'
        $debugPath = Join-Path $PluginsDir 'autopilot_debug.log'
        $loadedPath = Join-Path $PluginsDir 'autopilot_plugin_loaded.txt'

        $existsState = Test-Path $statePath
        $existsDebug = Test-Path $debugPath
        $existsLoaded = Test-Path $loadedPath

        if ($existsState -or $existsDebug -or $existsLoaded) {
            Log "FOUND plugin output: state=$existsState debug=$existsDebug loaded=$existsLoaded"

            if ($existsDebug) {
                Log "--- tail of autopilot_debug.log ---"
                try { Get-Content $debugPath -Tail 200 | ForEach-Object { Add-Content -Path $logFile -Value "DEBUG: $_"; Write-Output "DEBUG: $_" } } catch { Log "Error reading debug log: $_" }
            }

            # Touch a flag file to make detection easy for other scripts
            $flag = Join-Path $PSScriptRoot 'plugin_detected.flag'
            New-Item -Path $flag -ItemType File -Force | Out-Null

            if ($RunOnce) { Log "RunOnce specified, exiting after detection"; break }
            # If found, sleep longer to reduce noise
            Start-Sleep -Seconds ($IntervalSeconds * 6)
        } else {
            # Not found, write a short heartbeat to the local log every 12th iteration
            Add-Content -Path $logFile -Value "$(Get-Date -Format o) - heartbeat: no plugin output" -ErrorAction SilentlyContinue
        }
    } catch {
        Log "Exception in monitor loop: $_"
    }

    Start-Sleep -Seconds $IntervalSeconds
}

Log "Plugin monitor exiting"