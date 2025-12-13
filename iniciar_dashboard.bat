@echo off
echo 🚂 Iniciando Train Simulator Autopilot Dashboard...
echo.

cd /d "%~dp0dashboard"

echo Instalando dependencias si es necesario...
if not exist node_modules (
    npm install
)

echo Compilando TypeScript...
npm run build

echo.
echo ✅ Dashboard compilado exitosamente!
echo.
echo Iniciando servidor en http://localhost:3000
echo Presiona Ctrl+C para detener el servidor
echo.

npm start