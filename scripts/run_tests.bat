@echo off
REM Run the test suite using the project's virtual environment (Windows CMD)
REM Usage: run_tests.bat [pytest-args]
setlocal
set VENV_PY=%~dp0..\.venv\Scripts\python.exe
if not exist "%VENV_PY%" (
  echo Virtual environment python not found at %VENV_PY%
  echo Create and activate one using: python -m venv .venv && .\.venv\Scripts\Activate.ps1
  exit /b 1
)
if "%*"=="" (
  %VENV_PY% -m pytest -q
) else (
  %VENV_PY% -m pytest %*
)
exit /b %ERRORLEVEL%
