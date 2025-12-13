@echo off
echo ========================================
echo TRAIN SIMULATOR AUTOPILOT - DESKTOP
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist ".venv" (
    echo ERROR: Virtual environment no encontrado
    echo Ejecuta primero: install.bat
    pause
    exit /b 1
)

if not exist "web_dashboard.py" (
    echo ERROR: Archivo web_dashboard.py no encontrado
    pause
    exit /b 1
)

REM Activar virtual environment
echo Activando virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el virtual environment
    pause
    exit /b 1
)
echo Virtual environment activado

REM Verificar que Python funciona
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está disponible en el virtual environment
    pause
    exit /b 1
)
echo Python disponible

echo.
echo Iniciando servidor web...
echo.

REM Limpiar logs anteriores y luego iniciar servidor web en background usando PowerShell
powershell -Command "try { Remove-Item -Path 'web_server.log','web_server_error.log' -Force -ErrorAction SilentlyContinue } catch { }"
REM Iniciar el servidor usando el script PowerShell 'scripts/start_server.ps1'
powershell -ExecutionPolicy Bypass -File "scripts\start_server.ps1"
REM Esperar un tiempo corto y verificar arranque
timeout /t 5 /nobreak >nul

REM Verificar que el servidor se inició (compatibilidad PS 5.1 y PS 6+)
echo Verificando que el servidor web esté ejecutándose...
powershell -Command "try { $v = $PSVersionTable.PSVersion.Major; if ($v -ge 6) { Invoke-RestMethod -Uri 'http://localhost:5001' -TimeoutSec 5 | Out-Null } else { Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5001' -TimeoutSec 5 | Out-Null }; Write-Host 'Servidor web iniciado correctamente' } catch { Write-Host 'No se pudo conectar al servidor web' }" 2>nul

if errorlevel 1 (
    echo ERROR: El servidor web no se pudo iniciar
    echo Revisa los archivos web_server.log y web_server_error.log para más detalles
    pause
    exit /b 1
)

echo.
echo Servidor web ejecutándose en: http://localhost:5001
echo.

echo Abriendo navegador web...
echo.
echo INSTRUCCIONES:
echo - El dashboard se abrirá en tu navegador web
echo - Si no se abre automáticamente, ve a: http://localhost:5001
echo - Presiona F12 para abrir la consola de desarrollo
echo - Para salir, cierra la pestaña del navegador
echo.
echo ========================================
echo.

REM Abrir navegador web
start http://localhost:5001

echo.
echo Navegador abierto. Presiona cualquier tecla para continuar...
pause >nul