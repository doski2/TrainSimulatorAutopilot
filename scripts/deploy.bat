@echo off
REM deploy.bat - Script de deployment automatizado para Windows

echo 🚀 Iniciando deployment de Train Simulator Autopilot
echo ==================================================

REM Colores para output (limitado en Windows)
REM Usamos echo normal para compatibilidad

echo [INFO] Verificando prerrequisitos...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip no está instalado
    exit /b 1
)

echo [INFO] Configurando entorno virtual...

if not exist ".venv" (
    python -m venv .venv
    echo [INFO] Entorno virtual creado
) else (
    echo [INFO] Entorno virtual ya existe
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat
echo [INFO] Entorno virtual activado

echo [INFO] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [INFO] Dependencias instaladas

echo [INFO] Configurando aplicación...

REM Copiar configuración de ejemplo si no existe
if not exist "config.ini" (
    if exist "config.ini.example" (
        copy config.ini.example config.ini
        echo [INFO] Archivo config.ini creado desde ejemplo
    ) else (
        echo [WARNING] No se encontró config.ini.example
    )
)

REM Verificar configuración
if not exist "config.ini" (
    echo [ERROR] Archivo config.ini no encontrado
    exit /b 1
)
echo [INFO] Configuración verificada

echo [INFO] Ejecutando tests...
if exist "pytest.ini" (
    python -m pytest tests/ -v --tb=short
    echo [INFO] Tests ejecutados exitosamente
) else (
    echo [WARNING] Archivo pytest.ini no encontrado - omitiendo tests
)

echo [INFO] Aplicando optimizaciones...

REM Compilar archivos Python
python -m compileall .

REM Crear directorio de logs si no existe
if not exist "logs" mkdir logs

echo [INFO] Optimizaciones aplicadas

echo [INFO] Creando script de inicio...

echo @echo off > start_production.bat
echo REM start_production.bat - Script para iniciar la aplicación en producción >> start_production.bat
echo echo 🚀 Iniciando Train Simulator Autopilot ^(Producción^) >> start_production.bat
echo. >> start_production.bat
echo REM Activar entorno virtual >> start_production.bat
echo call .venv\Scripts\activate.bat >> start_production.bat
echo. >> start_production.bat
echo REM Variables de entorno para producción >> start_production.bat
echo set FLASK_ENV=production >> start_production.bat
echo set FLASK_DEBUG=false >> start_production.bat
echo. >> start_production.bat
echo REM Iniciar aplicación >> start_production.bat
echo python web_dashboard.py >> start_production.bat
echo. >> start_production.bat

echo [INFO] Script de inicio creado: start_production.bat

echo.
echo ✅ Deployment completado exitosamente!
echo.
echo Para iniciar la aplicación en producción:
echo   start_production.bat
echo.
echo O manualmente:
echo   .venv\Scripts\activate.bat
echo   python web_dashboard.py
echo.</content>
<parameter name="filePath">c:\Users\doski\TrainSimulatorAutopilot\scripts\deploy.bat