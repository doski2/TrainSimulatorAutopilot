# Instalar el plugin Lua de Autopilot

Este documento explica cómo instalar el plugin Lua `complete_autopilot_lua.lua` en la carpeta `plugins` de Train Simulator en Windows.

Precauciones:
- Requiere permisos de administrador para escribir en `C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins`.
- Recomiendo cerrar Train Simulator antes de copiar para evitar problemas de archivo bloqueado. Si no puedes cerrar el juego, copia y luego reinícialo.

Pasos manuales (rápido):
1. Abre PowerShell como Administrador.
2. Desde la raíz del repo: `Copy-Item .\complete_autopilot_lua.lua "C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\complete_autopilot_lua.lua"` (haz backup si ya existe).
3. Inicia Train Simulator o reinícialo.
4. Verifica la creación de `autopilot_state.txt` y `autopilot_debug.log` dentro de la carpeta `plugins`.

Uso del script automatizado (recomendado):
- Ejecuta (como Administrador):
  `.\	ools\scripts\install_lua_plugin.ps1` (o desde la raíz `.\












Si quieres, puedo ejecutar el script por ti (necesitaré confirmación y que estés de acuerdo en que el script escriba en `Program Files`).- Los logs del dashboard (`tsc_autopilot.log`) también pueden indicar problemas de E/S o permisos.- Si no aparece `autopilot_state.txt`, consulta `autopilot_debug.log` para ver errores del script Lua.Diagnóstico adicional:- Espera hasta `TimeoutSeconds` por la creación de `autopilot_state.txt` y te alerta si no lo hizo (sugiere reiniciar el simulator)- Copia `complete_autopilot_lua.lua` a `plugins/`- Hace backup del plugin existente (si lo hay)Qué hace el script:ecipes\scripts\install_lua_plugin.ps1` según estructura)