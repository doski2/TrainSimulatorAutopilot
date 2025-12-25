<#
Install Lua plugin for Train Simulator Autopilot
- Copies `complete_autopilot_lua.lua` from the repository to the Train Simulator `plugins` folder
- Creates a timestamped backup if a plugin with the same name exists
- Verifies that the copied file exists and prints next steps

Usage (PowerShell as Administrator recommended):
  .\scripts\install_lua_plugin.ps1 -Force -DryRun:$false

#>
param(
    [switch]$Force = $false,
    [int]$TimeoutSeconds = 30,
    [switch]$DryRun = $false
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent -Path $PSScriptRoot
$source = Join-Path $repoRoot 'complete_autopilot_lua.lua'
$pluginsDir = 'C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins'
$dest = Join-Path $pluginsDir 'complete_autopilot_lua.lua'

Write-Host "Source: $source"
Write-Host "Destination: $dest"

if (-not (Test-Path $source)) {
    Write-Error "Source Lua plugin not found at $source. Ensure you have the file in the repository root (complete_autopilot_lua.lua)."
    exit 2
}

if (-not (Test-Path $pluginsDir)) {
    Write-Error "Plugins directory not found: $pluginsDir. Is Train Simulator installed in the default location?"
    exit 3
}

if ($DryRun) {
    Write-Host "Dry run: would copy $source -> $dest"
    exit 0
}

# Backup existing plugin if present
if (Test-Path $dest) {
    $bak = "$dest.bak.$((Get-Date).ToString('yyyyMMddHHmmss'))"
    Write-Host "Backing up existing plugin to $bak"
    Copy-Item -Path $dest -Destination $bak -Force
}

# Copy plugin with elevated intent (requires appropriate privileges)
try {
    Copy-Item -Path $source -Destination $dest -Force
    Write-Host "Copied plugin to $dest"
} catch {
    Write-Error "Failed to copy plugin: $_. Exception: $($_.Exception.Message)"
    exit 4
}

# Check permissions - ensure current user can read/write
try {
    $acl = Get-Acl $pluginsDir
    Write-Host "Plugins dir owner: $($acl.Owner)"
} catch {
    # Use explicit format to avoid variable interpolation parsing issues
    Write-Warning ("Could not read ACL for {0}: {1}" -f $pluginsDir, $_.Exception.Message)
}

Write-Host "== Verification: waiting up to $TimeoutSeconds sec for plugin outputs =="
Write-Host "Please (re)start Train Simulator now to ensure the plugin is loaded."

$end = (Get-Date).AddSeconds($TimeoutSeconds)
$foundState = $false
while ((Get-Date) -lt $end) {
    if (Test-Path (Join-Path $pluginsDir 'autopilot_state.txt')) {
        Write-Host "Found autopilot_state.txt -> OK"
        $foundState = $true
        break
    }
    Start-Sleep -Seconds 1
}

if (-not $foundState) {
    Write-Warning "autopilot_state.txt was not created. If Train Simulator is running, try restarting it so the plugin loads."
    Write-Host "Check file: $(Join-Path $pluginsDir 'autopilot_debug.log') for plugin errors after the simulator starts."
    exit 0
}

Write-Host "Plugin appears to have created autopilot_state.txt. Installation complete."
exit 0
