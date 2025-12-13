@echo off
echo ========================================
echo 🔧 MODO DESARROLLO - TRAIN SIMULATOR AUTOPILOT
echo ========================================
echo.
echo Iniciando en modo desarrollo con DevTools...
echo.

REM Verificar si el servidor web esta corriendo
echo 🔍 Verificando servidor web...
curl -s http://localhost:5001 > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Servidor web no detectado. Iniciando servidor...
    start "WebServer" cmd /c "cd /d %~dp0 && python web_dashboard.py"
    echo ⏳ Esperando que el servidor inicie...
    timeout /t 5 /nobreak > nul
) else (
    echo ✅ Servidor web ya esta ejecutandose
)

echo.
echo 🚀 Iniciando aplicacion Electron en modo desarrollo...
echo.
echo INSTRUCCIONES PARA DIAGNOSTICO:
echo 1. La ventana de la aplicacion se abrira
echo 2. PRESIONA F12 si no ves las DevTools
echo 3. Ve a la pestaña Console en DevTools
echo 4. Haz clic en "Configuracion" en la barra de navegacion
echo 5. Copia TODOS los logs que aparezcan en la consola
echo 6. Cierra la aplicacion cuando termines
echo.
echo ========================================
echo.

REM Iniciar Electron en modo desarrollo
npm run dev

echo.
echo ✅ Modo desarrollo finalizado.
echo.
echo ¿Viste los logs en la consola cuando hiciste clic en Configuracion?
echo Copialos aqui para diagnosticar el problema.
echo.
pause