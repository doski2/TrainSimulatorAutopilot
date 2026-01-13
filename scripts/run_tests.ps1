# Run the test suite using the project's virtual environment (Windows PowerShell)
# Usage: .\run_tests.ps1 [pytest-args]

$venvPython = Join-Path -Path $PSScriptRoot -ChildPath "..\.venv\Scripts\python.exe"
if (-Not (Test-Path $venvPython)) {
    Write-Host "Virtual environment python not found at $venvPython" -ForegroundColor Yellow
    Write-Host 'Create and activate one using: python -m venv .venv; .\.venv\Scripts\Activate.ps1'
    exit 1
}

$argsList = $args -join ' '
if ($argsList -eq '') { $argsList = '-q' }

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$outFile = Join-Path $repoRoot "pytest-output.txt"
$errFile = Join-Path $repoRoot "pytest-error.txt"

Write-Host "Running tests with: $venvPython -m pytest $argsList" -ForegroundColor Green

# Build argument list for Start-Process
$allArgs = @("-m","pytest") + $args

# Run pytest and capture stdout/stderr to files
$proc = Start-Process -FilePath $venvPython -ArgumentList $allArgs -RedirectStandardOutput $outFile -RedirectStandardError $errFile -NoNewWindow -Wait -PassThru
$rc = $proc.ExitCode

# If there is stderr content, append it to the main output file for easier diagnosis
if ((Test-Path $errFile) -and ((Get-Item $errFile).Length -gt 0)) {
    Add-Content -Path $outFile -Value "`n===== STDERR =====`n"
    Get-Content $errFile | Add-Content -Path $outFile
}

Write-Host "pytest exit code: $rc"
Write-Host "Logs written to: $outFile and $errFile"
exit $rc
