# Documentación del Script Lua: Railworks_GetData_Script.lua

## Descripción General

El script `Railworks_GetData_Script.lua` es un plugin para Train Simulator Classic
(RailWorks).

Recopila datos de telemetría en tiempo real de la locomotora y los escribe en
`GetData.txt`.

Este archivo lo usan aplicaciones externas (por ejemplo el autopilot
de `TrainSimulatorAutopilot`) para monitorear y controlar el tren.

## Ubicación

- **Archivo principal**: `C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\Railworks_GetData_Script.lua`
- **Archivo de salida**: `C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt`
- **Archivos de debug**: `debug_getdata.log`, `GetData_Error.txt`

## Funcionalidad

El script se ejecuta automáticamente dentro del simulador cuando el jugador conduce
una locomotora.

Recopila datos como velocidad, RPM, esfuerzo de tracción y presiones de freno,
entre otros, y los formatea en un archivo de texto plano.

### Funciones Principales

1. **`getdata()`**: Función principal llamada periódicamente.
   Verifica si el jugador está conduciendo y recopila datos.
2. **`GetSpeedInfo()`**: Obtiene información de velocidad y tipo de velocímetro
   (MPH/KPH).
3. **`GetControlData()`**: Recopila datos de controles del motor y frenos.
4. **`GetSpeedLimits()`**: Obtiene límites de velocidad actuales y próximos.
5. **`WriteData()`**: Escribe los datos recopilados en `GetData.txt`.
6. **`SendData()`**: Lee comandos desde `SendCommand.txt` y los envía al simulador.

## Configuración

- **`delay`**: Número de iteraciones antes de actualizar datos.
  (por defecto: 1, para actualizaciones rápidas).
- **`BASE_DIR`**: Directorio base para archivos
  (plugins de RailWorks).
- **`delete_Files`**: Borra archivos antiguos en la primera ejecución.

## Formato de Salida (GetData.txt)

Cada entrada sigue el formato:

```text
ControlType:Tipo
ControlName:Nombre
ControlMin:Mínimo
ControlMax:Máximo
ControlValue:Valor
```

### Ejemplo de Contenido

```text
ControlType:Speed
ControlName:CurrentSpeed
ControlMin:0
ControlMax:0
ControlValue:25.5

ControlType:_RPM
ControlName:RPM
ControlMin:0
ControlMax:5000
ControlValue:1200.0
```

## Variables de Telemetría Principales

- **Velocidad**: `CurrentSpeed` (m/s convertido a MPH/KPH).
- **RPM**: Revoluciones del motor (reportado o inferido).
- **TractiveEffort**: Esfuerzo de tracción (Newtons).
- **Ammeter**: Corriente eléctrica (Amperes).
- **Wheelslip**: Deslizamiento de ruedas.
- **Presiones de freno**: Varias mediciones en PSI.
- **Límites de velocidad**: Actuales y próximos.

## Correcciones Aplicadas

- **Error de sintaxis**: Removido `end` suelto en `GetControlData()`.
- **Delay reducido**: Cambiado de 5 a 1 para actualizaciones más frecuentes.
- **Debug agregado**: Logs en `debug_getdata.log` para diagnóstico.

## Uso con TrainSimulatorAutopilot

El script alimenta datos al backend Python (`tsc_integration.py`), que parsea
`GetData.txt` y envía telemetría al dashboard web.

Asegúrate de que el simulador se ejecute con permisos de escritura
(ej. como administrador).

## Diagnóstico

- Si no genera `GetData.txt`, verifica logs de debug.
- Ejecuta el simulador y conduce una locomotora para activar el script.
- Errores se registran en `GetData_Error.txt`.

## Notas

- Basado en el script original de la comunidad RailWorks.
- Compatible con locomotoras diésel y eléctricas.
- No requiere modificaciones al simulador base.
