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
Write-Host "Running tests with: $venvPython -m pytest $argsList" -ForegroundColor Green
& $venvPython -m pytest $args
exit $LASTEXITCODE
