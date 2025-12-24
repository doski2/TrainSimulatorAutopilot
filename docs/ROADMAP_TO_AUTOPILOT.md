# Roadmap: Cómo llegar a Piloto Automático (Autopilot)

Este documento describe los pasos prácticos, comandos y verificaciones para llevar el sistema desde código hasta un piloto automático operativo en Train Simulator Classic (TSC).

## 1) Pre-requisitos ✅
- Windows con Train Simulator Classic instalado (ruta típica: `C:\Program Files (x86)\Steam\steamapps\common\RailWorks`).
- Python 3.9+ (usar el virtualenv del repo si aplica). Instalar dependencias: `pip install -r requirements.txt` (algunas son opcionales para tests avanzados).
- Permisos de administrador para copiar scripts a la carpeta `plugins` del simulador si fuera necesario.

---

## 2) Instalar plugin Lua (si no está instalado) 🔧
1. Copia `complete_autopilot_lua.lua` a `RailWorks\plugins` (usa `scripts/install_lua_plugin.ps1` para automatizar):
   - PowerShell (ejecutar como admin):
     ```powershell
     .\scripts\install_lua_plugin.ps1
     ```
2. Verifica que el archivo `complete_autopilot_lua.lua` exista en `...\RailWorks\plugins`.
3. Si el juego está en ejecución, reinicíalo para cargar el plugin. El plugin escribe archivos de presencia:`autopilot_probe_loaded.txt` y `autopilot_plugin_loaded.txt`.

---

## 3) Verificar que el plugin se cargó ✅
- Arranca TSC y carga una escena donde tengas `engine key` (motor con llave puesta).
- En la carpeta `plugins` espera que aparezcan:
  - `autopilot_plugin_loaded.txt` (heartbeat/presencia)
  - `autopilot_debug.log` (logs del plugin)
- Puedes usar el script de polling: `.\	emplates\poll_for_plugin_output.ps1` o el script creado `scripts/poll_for_plugin_output.ps1`.

> Nota: si no aparece la presencia, revisa Event Viewer (Application) por crashes de `RailWorks64.exe` y revisa permisos/antivirus.

---

## 4) Flujo de comandos (archivo y API) 📨
- El backend escribe líneas a `plugins/autopilot_commands.txt` (ej: `start_autopilot`, `Regulator:0.500`).
- El plugin Lua lee ese archivo y procesa cada línea; para `start_autopilot` escribe `autopilot_state.txt` con `on`.
- Nuevo API disponible: `POST /api/control/set` con JSON `{ "control": "Regulator", "value": 0.5 }` que delega a `TSCIntegration.enviar_comandos`.

Comandos útiles desde Python:
- Test rápido (ejemplo):
```python
from tsc_integration import TSCIntegration
tsc = TSCIntegration()
tsci.enviar_comandos({"autopilot": True}) # escribe start_autopilot
```

---

## 5) Probar inicio del piloto (ACK) — pasos concretos ✅
1. Con el simulador corriendo y la escena cargada, en el servidor (o tests) ejecuta:
   - `POST /api/control/start_autopilot` (o usar `tsc_integration.enviar_comandos({'autopilot': True})`).
2. El plugin debería:
   - leer `autopilot_commands.txt` y escribir `autopilot_state.txt` con `on` (ACK).
3. Verifica con: `/api/status` o con `tsc_integration.wait_for_autopilot_state('on')`.
4. Si `wait_for_autopilot_state` expira → API responde 504 (configurable vía `AUTOPILOT_ACK_TIMEOUT`).

---

## 6) Tests & E2E incluidos 🧪
- Unit tests relevantes:
  - `tests/unit/test_api_set_control.py` (endpoint POST /api/control/set)
  - `tests/unit/test_tsc_integration_set_control.py` (verify writing numeric control to `autopilot_commands.txt`)
- E2E:
  - `tests/integration/test_e2e_autopilot_file_ack.py` — simula que plugin escribe ACK y verifica `wait_for_autopilot_state`.

Ejecutar tests:
```bash
python -m pytest -q
```

---

## 7) Troubleshooting (si no llega ACK) 🔍
- Verifica `autopilot_debug.log` y `autopilot_plugin_loaded.txt` en `plugins/`.
- Revisa permisos del directorio `plugins` y que el usuario del proceso tenga permisos de escritura.
- Si el juego crashea, ver Event Viewer (`Application` / `Windows Error Reporting`) para `RailWorks64.exe`.
- Verifica bloqueo de archivos (WinError 32) — el simulador puede mantener archivos abiertos; los reintentos/atomic writes se implementan en `tsc_integration._atomic_write_lines`.
- Si el plugin no escribe ACK, reinicia el simulador con la escena (algunos plugins se cargan solo en el inicio de la escena).

---

## 8) Seguridad y operativa ⚠️
- No expongas `plugins` path ni archivos internos en interfaces públicas.
- Mantén `AUTOPILOT_ACK_TIMEOUT` razonable en producción (p. ej. 3–5 s) y monitoriza métricas `autopilot_plugin_unacked_total`.

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

Si quieres, añado un script que automátice el flujo completo (instalar plugin, reiniciar TSC, run polling y validar ACK) — dime y lo implemento.
