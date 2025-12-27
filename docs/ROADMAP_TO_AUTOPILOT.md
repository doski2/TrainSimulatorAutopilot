# Roadmap: Cómo llegar a Piloto Automático (Autopilot)

Este documento describe los pasos prácticos, comandos y verificaciones para
llevar el sistema desde código hasta un piloto automático operativo en Train
Simulator Classic (TSC).

## 1) Pre-requisitos ✅

- Windows con Train Simulator Classic instalado.
  Ruta típica: `C:\Program Files (x86)\Steam\steamapps\common\RailWorks`.
- Python 3.9+ (usar el virtualenv del repo si aplica).
  Instala dependencias con `pip install -r requirements.txt`.
  Ten en cuenta que algunas dependencias son opcionales para tests avanzados.
- Permisos de administrador para copiar scripts a la carpeta `plugins` del
  simulador si fuera necesario.

---

## 2) Instalar plugin Lua (si no está instalado) 🔧

1. Copia `complete_autopilot_lua.lua` a `RailWorks\plugins`.
   (Puedes usar `scripts/install_lua_plugin.ps1` para automatizar este paso):
   - PowerShell (ejecutar como admin):

     ```powershell
     .\scripts\install_lua_plugin.ps1
     ```

2. Verifica que el archivo `complete_autopilot_lua.lua` exista en `...\RailWorks\plugins`.
3. Si el juego está en ejecución, reinícialo para cargar el plugin. El
   plugin escribe archivos de presencia:
   - `autopilot_probe_loaded.txt`
   - `autopilot_plugin_loaded.txt`.

---

## 3) Verificar que el plugin se cargó ✅

- Arranca TSC y carga una escena donde tengas `engine key` (motor con llave puesta).
- En la carpeta `plugins` espera que aparezcan:
  - `autopilot_plugin_loaded.txt` (heartbeat/presencia)
  - `autopilot_debug.log` (logs del plugin)
- Puedes usar el script de polling:
  `scripts/poll_for_plugin_output.ps1` (o el script equivalente en `templates/`).

> Nota: si no aparece la presencia, revisa el Event Viewer
  (Application) por crashes de `RailWorks64.exe`.
  También verifica permisos y antivirus.

---

## 4) Flujo de comandos (archivo y API) 📨

- El backend escribe líneas a `plugins/autopilot_commands.txt` (p. ej.,
  `start_autopilot`, `Regulator:0.500`).
- El plugin Lua lee ese archivo y procesa cada línea. Para el comando
  `start_autopilot` el plugin escribe `autopilot_state.txt` con el valor
  `on` (ACK).
- Nuevo endpoint API: `POST /api/control/set` con JSON
  `{ "control": "Regulator", "value": 0.5 }`, que delega en
  `TSCIntegration.enviar_comandos`.

Comandos útiles desde Python:

- Test rápido (ejemplo):

```python
from tsc_integration import TSCIntegration
tsc = TSCIntegration()
tsc.enviar_comandos({"autopilot": True})
# escribe start_autopilot
```

---

## 5) Probar inicio del piloto (ACK) — pasos concretos ✅

1. Con el simulador corriendo y la escena cargada, en el servidor (o tests)
   ejecuta:
   - `POST /api/control/start_autopilot`.
   - Alternativamente: `tsc_integration.enviar_comandos({'autopilot': True})`.
2. El plugin debería:
   - leer `autopilot_commands.txt`.
   - escribir `autopilot_state.txt` con el valor `on` para indicar ACK.
3. Verifica con: `/api/status`.
4. Nota: la comprobación por ACK (`wait_for_autopilot_state`) ha sido eliminada
   del flujo por defecto; el sistema no espera confirmaciones por archivo y
   siempre devuelve éxito en los endpoints de inicio de autopilot.

---

## 6) Tests & E2E incluidos 🧪

- Unit tests relevantes:
  - `tests/unit/test_api_set_control.py`
  (comprueba el endpoint POST `/api/control/set`)
- `tests/unit/test_tsc_integration_set_control.py`
  (verifica la escritura de controles numéricos en `autopilot_commands.txt`)
- E2E:
  - `tests/integration/test_e2e_autopilot_file_ack.py`
  — simula que el plugin escribe el ACK y verifica
  `wait_for_autopilot_state`.

Ejecutar tests:

```bash
python -m pytest -q
```

---

## 7) Troubleshooting (si no llega ACK) 🔍

- Verifica `autopilot_debug.log` y `autopilot_plugin_loaded.txt` en la carpeta
  `plugins/`.
- Revisa los permisos del directorio `plugins/` y que el usuario del proceso
  tenga permisos de escritura.
- Si el juego se bloquea, consulta el Event Viewer (`Application` /
  `Windows Error Reporting`) para entradas relacionadas con
  `RailWorks64.exe`.
- Verifica bloqueo de archivos (WinError 32). El simulador puede mantener
  archivos abiertos; el módulo implementa reintentos y escrituras atómicas
  en `tsc_integration._atomic_write_lines`.
- Si el plugin no escribe ACK, reinicia el simulador con la escena cargada
  (algunos plugins solo se cargan al inicio de la escena).

---

## 8) Seguridad y operativa ⚠️

- No expongas `plugins` path ni archivos internos en interfaces públicas.
- Mantén `AUTOPILOT_ACK_TIMEOUT` razonable en producción (p. ej. 3–5 s)
  y monitoriza métricas como `autopilot_plugin_unacked_total`.

---

## 9) Checklist de despliegue ✅

- [ ] Copia `complete_autopilot_lua.lua` al `plugins/` (o usar `scripts/install_lua_plugin.ps1`).
- [ ] Reinicia TSC y carga escenario.
- [ ] Verifica `autopilot_plugin_loaded.txt` y `autopilot_debug.log`.
- [ ] Ejecuta `POST /api/control/start_autopilot` y confirma ACK en `autopilot_state.txt`.
- [ ] Ejecuta tests unitarios y E2E locales.

---

## 10) Siguientes mejoras (opcional) ✨

- Emular HID (ViGEm/vJoy) para control sin depender de foco de ventana.
- Mejor logging en plugin Lua (más niveles, rotación de logs).
- Test de integración que arranque/termine RailWorks en CI (difícil por licencias/hardware/Windows).

---

Si quieres, puedo añadir un script que automatice el flujo completo: instalar
el plugin, reiniciar TSC, ejecutar el polling y validar el ACK. Dime si lo
implemento.
