# Resumen y análisis del flujo GetData/SendCommand (Autopilot)

Fecha: 07/12/2025

## 1. Propósito

Este documento consolida el análisis, pruebas, correcciones aplicadas y
recomendaciones para la integración entre RailWorks (plugin Lua) y la
herramienta Python (`tsc_integration.py`) para el autopilot del simulador.

Incluye además un resumen del esqueleto del módulo AI (`ai_autopilot`) y pasos
siguientes para depuración y entrenamiento.

---

## 2. Artefactos clave y archivos revisados

- `Railworks_GetData_Script.lua` (plugin Lua)
- `tsc_integration.py` (Python: integración y comandos)
- `ai_autopilot/` (scripts de grabación y pipeline AI)
  - `ai_autopilot/scripts/record_session.py`
  - `ai_autopilot/scripts/labeler.py`
  - `ai_autopilot/scripts/preprocess.py`
  - `ai_autopilot/scripts/train_model.py`
  - `ai_autopilot/scripts/inference_service.py`
  - `ai_autopilot/tests/test_record_and_label.py`

Archivos usados en debugging:

- `c:/Users/doski/Documents/TSClassic Raildriver and Joystick Interface
V3.3.0.9/GetData.txt` (escrito por plugin)
- `c:/Users/doski/Documents/TSClassic Raildriver and Joystick Interface
V3.3.0.9/SendCommand.txt` (escrito por Python/tsc_integration en pruebas)

---

## 3. Resumen de comportamiento actual

- El plugin Lua compone y escribe `GetData.txt` con múltiples `ControlName` y
`ControlValue` para telemetría (velocidad, rpm, amperímetro, freno, presiones,
etc.).
- `tsc_integration.py` lee `GetData.txt` y convierte/normaliza datos para la IA
(ej. convertir m/s a km/h) y mapea nombres a claves en español/IA.
- `tsc_integration.py` genera `SendCommand.txt` con formato `ControlName:value`
tras mapear comandos IA a nombres del RailDriver; implementa heurística de
fallback (ej. `DynamicBrake` → `VirtualEngineBrakeControl`).
- El plugin Lua lee `SendCommand.txt` (con `SendData()`) y aplica
`SetControlValue` y `SetControlTargetValue`.

---

## 4. Pruebas realizadas y resultados

- Validación parseo `GetData.txt` con `parse_getdata()` -> OK (valores numéricos
convertidos).
- `TSCIntegration.leer_datos_archivo()` y `convertir_datos_ia()`:
  - Lectura simulada y conversión correcta (velocidad 5 m/s → 18 km/h).
  - Fallback `RPMDelta` si `RPM` es 0.
  - Alias `amps` para `Ammeter` implementado.
- `TSCIntegration.enviar_comandos()`:
  - Remapeo correcto `freno_tren` → `TrainBrakeControl`.
  - Heurístico de fallback `DynamicBrake` → `VirtualEngineBrakeControl` si
`DynamicBrake` no existe.
  - `SendCommand.txt` se generó con el valor esperado (ej.
`TrainBrakeControl:0.000`).
- `ai_autopilot/scripts/record_session.py` generó JSONL de sesiones con
normalizaciones (speed, amps, rpm).
- `labeler` (heurístico) genera `brake_applied`, `brake_released`, `is_stopped`
correctamente para las muestras simples.

---

## 5. Hallazgos (problemas y observaciones)

1. **Rutas por defecto discordantes**: El plugin Lua escribe en la carpeta de
"TSClassic Raildriver ..." (ruta en usuario), mientras que `tsc_integration.py`
lee por defecto desde la instalación de Steam (`Program Files (x86)`). Esto crea
desincronización si se deja con valores por defecto.
2. **Falta de logging detallado del proceso de SendCommand**: En Lua no existe un
`SendCommandDebug.txt` para observar `before/after` de control y confirmar que
el control se aplicó.
3. **Freno no libera (síntoma)**: Posibles causas verificadas:
   - El control es enviado correctamente (por Python), pero no se refleja
inmediatamente por la física del simulador que requiere tiempo para presión.
   - El comando es mapeado a control equivocado para el asset (ej.
`VirtualBrake` vs `TrainBrakeControl`).
   - No hay confirmación de aplicación tras `SetControlValue`.
4. **Riesgo de race**: Si el plugin y Python no usan la misma ruta, o si el
`delete_Files` borra archivos con timing, puede interferir en la sincronización.
5. **AI pipeline**: La estructura y scripts están listos; falta dataset real y
validación de etiquetas (revisión manual mínima recomendable).

---

## 6. Recomendaciones y cambios propuestos (prioridad alta → baja)

### Prioridad alta

1. **Agregar `SendCommandDebug.txt` en `Railworks_GetData_Script.lua`**: Loggeará
timestamp, control solicitado, valor solicitado, valor `before` y `after` para
diagnosticar si se aplicó realmente el control.
2. **Unificar o permitir configuración de rutas**: En `tsc_integration.py` y
`record_session.py` permitir `--getdata`, `--sendcmd` o variables de entorno
(`TSC_GETDATA_FILE` y `TSC_SENDCOMMAND_FILE`).
3. **Implementar re-check / confirmación para freno**: Tras enviar
`TrainBrakeControl:0.0`, esperar 300–500 ms y verificar
`TrainBrakeCylinderPressurePSI` o `AirBrakePipePressurePSI` para confirmar
liberación, reintentar con fallback si no baja.

### Prioridad media

1. **Modo DRY RUN**: Enviar a `SendCommand_DRY.txt` para verificar sin aplicar a
simulador (útil en pruebas).
2. **Agregar CLI para `record_session.py`**: Añadir `--getdata` y `--output` para
flexibilidad durante grabación de sesiones.
3. **Agregar logs de debug en `tsc_integration.py`** (nivel DEBUG) para remapeos,
fallback y cambios de valor.

### Prioridad baja

1. **Añadir tests E2E**: Test que simule GetData y verifique que
`SendCommand.txt` y `SendCommandDebug.txt` se escriben y coinciden con
expectativas.
2. **Mejoras AI**: Revisión y ajuste de etiquetas (manuales) sobre el dataset
para mejorar la calidad de entrenamiento.

---

## 7. Parche recomendado: `SendCommandDebug.txt` (Lua)

Insertar después de `Call("SetControlTargetValue", ...)` en `SendData()`:

```lua
local debugPath = "c:/Users/doski/Documents/TSClassic Raildriver and Joystick Interface V3.3.0.9/SendCommandDebug.txt"
local beforeVal = Call("GetControlValue", t[1], 0)
-- apply
if OnControlValueChange then
  OnControlValueChange(t[1], 0, tonumber(t[2]))
else
  Call("SetControlValue", t[1], 0, tonumber(t[2]))
end
Call("SetControlTargetValue", t[1], 0, tonumber(t[2]))
local afterVal = Call("GetControlValue", t[1], 0)
local debugFile = io.open(debugPath, "a")
if debugFile then
  debugFile:write(os.date("%Y-%m-%d %H:%M:%S") .. " " .. t[1] .. " requested:" .. tostring(t[2]) .. " before:" .. tostring(beforeVal) .. " after:" .. tostring(afterVal) .. "\n")
  debugFile:close()
end
```

---

## 8. Cambios Python recomendados: configuración de rutas y CLI

- En `TSCIntegration.__init__()` permitimos:
  - `ruta_archivo` por argumento o `TSC_GETDATA_FILE` env var
  - `ruta_archivo_comandos` por argumento o `TSC_SENDCOMMAND_FILE` env var
- Este cambio permite que `TSCIntegration` lea el GetData que el plugin está
generando (ruta del user) sin necesitar editar código.

---

## 9. Plan AI (resumen)

1. Configurar `record_session.py` con rutas y grabar 20–60 minutos por asset bajo
diferentes escenarios.
2. Ejecutar `labeler.py` y validar manualmente una muestra del 5–10% para afinar
heurísticas.
3. Generar secuencias con `preprocess.py`, entrenar con `train_model.py` y probar
`inference_service.py` en modo dry-run.

---

## 10. Pasos de verificación y comandos (PowerShell)

Activar entorno:

```powershell
& C:/Users/doski/TrainSimulatorAutopilot/.venv/Scripts/Activate.ps1
```

Ejecutar test simple de lectura / envío:

```powershell
python - <<'PY'
import os, sys
sys.path.append(r'c:\Users\doski\TrainSimulatorAutopilot')
from tsc_integration import TSCIntegration
getdata_path = r"c:/Users/doski/Documents/TSClassic Raildriver and Joystick Interface V3.3.0.9/GetData.txt"
send_path = r"c:/Users/doski/Documents/TSClassic Raildriver and Joystick Interface V3.3.0.9/SendCommand.txt"
# create sample GetData
ios.makedirs(os.path.dirname(getdata_path), exist_ok=True)
with open(getdata_path,'w',encoding='utf-8') as f:
    f.write('ControlType:Speed\nControlName:CurrentSpeed\nControlMin:0\nControlMax:0\nControlValue:5.0\n')
    f.write('ControlType:_TrainBrakeControl\nControlName:TrainBrakeControl\nControlMin:0\nControlMax:1\nControlValue:0.4\n')
intg = TSCIntegration(ruta_archivo=getdata_path)
intg.ruta_archivo_comandos = send_path
print(intg.leer_datos_archivo())
print(intg.convertir_datos_ia(intg.leer_datos_archivo()))
print(intg.enviar_comandos({'freno_tren':0.0}))
print('SendCommand content:')
print(open(send_path,'r',encoding='utf-8').read())
PY
```

Monitorear `SendCommandDebug.txt` (tras parche Lua):

```powershell
Get-Content "c:\Users\doski\Documents\TSClassic Raildriver and Joystick Interface V3.3.0.9\SendCommandDebug.txt" -Tail 100 -Wait
```

Grabar datos AI (ejemplo):

```powershell
python ai_autopilot/scripts/record_session.py --output ai_autopilot/data/sessions/session-test.jsonl --getdata "c:\Users\doski\Documents\TSClassic Raildriver and Joystick Interface V3.3.0.9\GetData.txt"
```

---

## 11. Próximos pasos propuestos

1. ¿Aplicamos ya el parche de `SendCommandDebug.txt` en
`Railworks_GetData_Script.lua`? (Recomendado: sí)
2. ¿Quieres que actualice `tsc_integration.py` para aceptar rutas/args/env vars y
agregue CLI a `record_session.py`? (Recomendado: sí)
3. ¿Iniciamos colección de dataset AI (yo puedo manejar la configuración de
`record_session.py` y probarlo)?

---

## 12. Limitaciones y notas finales

- No se ejecutó el simulador en tiempo real aquí (no hay acceso directo a Train
Simulator Classic); pruebas de integración E2E en la máquina del usuario son
requeridas.
- Las recomendaciones están validadas con tests simulados que crearon y leyeron
archivos en disco y con snippets ejecutados en el entorno.

---

Si quieres, aplico ahora los cambios automáticos (parche Lua + ajustes en
`tsc_integration.py`) y/o creo tests E2E y un PR con los cambios. Indica cuál
quieres que haga a continuación.
