# Instalar el plugin Lua de Autopilot

Este documento explica cómo instalar el plugin Lua `complete_autopilot_lua.lua`
en la carpeta `plugins` de Train Simulator en Windows.

Precauciones:

- Requiere permisos de administrador para escribir en `C:\Program Files
  (x86)\Steam\steamapps\common\RailWorks\plugins`.
- Recomiendo cerrar Train Simulator antes de copiar para evitar
  problemas de archivo bloqueado.
  Si no puedes cerrar el juego, copia los archivos y reinícialo.

Pasos manuales (rápido):

1. Abre PowerShell como Administrador.
2. Desde la raíz del repo, ejecuta el siguiente comando (haz backup si ya
   existe):

```powershell
Copy-Item .\complete_autopilot_lua.lua "C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\complete_autopilot_lua.lua"
```

1. Inicia Train Simulator o reinícialo.
2. Verifica la creación de `autopilot_state.txt` y `autopilot_debug.log`
   dentro de la carpeta `plugins`.

Uso del script automatizado (recomendado):

- Ejecuta el instalador (como Administrador) desde la raíz del repo:

```powershell
.\tools\scripts\install_lua_plugin.ps1
```

- Si prefieres, puedo ejecutar el script por ti; necesitaré tu
  confirmación y permiso para escribir en `Program Files`.

- Notas de diagnóstico:
  - Los logs del dashboard (`tsc_autopilot.log`) pueden indicar
    problemas de E/S o permisos.
  - Si no aparece `autopilot_state.txt`, revisa
    `autopilot_debug.log` para ver errores del plugin.

Diagnóstico adicional:

- El instalador espera hasta `TimeoutSeconds` por la creación de
  `autopilot_state.txt` y alerta si no lo hace (sugiere reiniciar el
  simulador).
- El script copia `complete_autopilot_lua.lua` a `plugins/` y hace
  backup del plugin existente si ya existía.
