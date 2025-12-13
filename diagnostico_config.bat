@echo off
echo ========================================
echo 🔧 DIAGNOSTICO PANEL DE CONFIGURACION
echo ========================================
echo.
echo La aplicacion se esta ejecutando con logs de depuracion.
echo.
echo INSTRUCCIONES PARA DIAGNOSTICO:
echo.
echo 1. Abre la aplicacion Electron
echo 2. Presiona F12 para abrir la consola del navegador
echo 3. Busca los logs que empiezan con emojis (🔥, 🔧, etc.)
echo 4. Haz clic en "Configuracion" en la barra de navegacion
echo 5. Copia y pega todos los logs de la consola aqui
echo.
echo FUNCIONES DE DEBUG DISPONIBLES:
echo - debugSettings() - Muestra estado del panel
echo - testToggle() - Prueba la funcion toggle
echo.
echo Presiona cualquier tecla para continuar...
pause > nul

echo.
echo Reiniciando aplicacion con diagnostico...
echo.

REM Detener procesos anteriores
taskkill /f /im electron.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1

REM Iniciar servidor web
start "WebServer" cmd /c "cd /d %~dp0 && python web_dashboard.py"

REM Esperar a que el servidor inicie
timeout /t 3 /nobreak > nul

REM Iniciar Electron
start "ElectronApp" cmd /c "cd /d %~dp0 && npm start"

echo.
echo ✅ Aplicacion iniciada con diagnostico activado
echo.
echo Recuerda revisar la consola del navegador (F12)
echo y reportar los logs cuando hagas clic en Configuracion.
echo.