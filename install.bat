@echo off
echo 🚂 Train Simulator Autopilot - Instalación Mejorada
echo ====================================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo Ejecutando instalador avanzado...
python setup.py
if errorlevel 1 (
    echo ❌ Error en la instalación
    echo.
    echo Intenta ejecutar manualmente:
    echo pip install -r requirements.txt
    echo python web_dashboard.py
    pause
    exit /b 1
)

echo.
echo 🎉 ¡Instalación completada!
echo.
echo Para iniciar el sistema:
echo 1. Dashboard web: python web_dashboard.py
echo 2. Airflow: docker-compose up -d
echo 3. Ver documentación en docs/
echo.
pause
)

echo.
echo Verificando archivos críticos...
if not exist "tsc_integration.py" (
    echo ❌ Archivo tsc_integration.py no encontrado
    pause
    exit /b 1
)
if not exist "autopilot_system.py" (
    echo ❌ Archivo autopilot_system.py no encontrado
    pause
    exit /b 1
)
echo ✅ Archivos críticos verificados

echo.
echo Ejecutando prueba rápida...
python scripts/demo_completa_autopilot.py --test-only
if errorlevel 1 (
    echo ⚠️ Prueba rápida falló, pero la instalación básica está completa
    echo Revisa la configuración y ejecuta manualmente para diagnosticar
) else (
    echo ✅ Prueba rápida exitosa
)

echo.
echo ==================================================
echo ✅ INSTALACIÓN COMPLETADA
echo.
echo Para usar el sistema:
echo   1. Ejecuta: python autopilot_system.py
echo   2. O usa la demo: python scripts/demo_completa_autopilot.py
echo   3. Configura rutas en config.ini si es necesario
echo.
echo ¡Disfruta conduciendo trenes automáticamente!
echo ==================================================

pause