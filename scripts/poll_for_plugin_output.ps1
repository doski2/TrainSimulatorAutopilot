$plugins = 'C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins'
$found = $false
for ($i = 0; $i -lt 60; $i++) {
    $statePath = Join-Path $plugins 'autopilot_state.txt'
    $debugPath = Join-Path $plugins 'autopilot_debug.log'
    $existsState = Test-Path $statePath
    $existsDebug = Test-Path $debugPath
    if ($existsState -or $existsDebug) {
        Write-Output "FOUND plugin output after $($i*2) seconds"
        $found = $true
        break
    }
    Start-Sleep -Seconds 2
}
if ($found) {
    Get-ChildItem $plugins | Where-Object { $_.Name -in @('autopilot_state.txt','autopilot_debug.log') } | Select-Object Name, LastWriteTime, Length | Format-Table -AutoSize
    if (Test-Path (Join-Path $plugins 'autopilot_state.txt')) {
        Write-Output 'autopilot_state.txt content:'
        Get-Content (Join-Path $plugins 'autopilot_state.txt') -ErrorAction SilentlyContinue
    }
} else {
    Write-Output "No plugin output detected within timeout. Please start Train Simulator and load a scenario, then re-run this script or notify me to poll again."
}
