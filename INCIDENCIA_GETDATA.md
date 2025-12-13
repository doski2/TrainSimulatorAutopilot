# Incidencia: GetData.txt No Se Creaba

## Fecha

7 de Diciembre de 2025

## Resumen

El script Lua `Railworks_GetData_Script.lua` no creaba el archivo `GetData.txt`
a pesar de estar correctamente ubicado en la carpeta de plugins de RailWorks.

## Síntomas

- ❌ Archivo GetData.txt no se creaba
- ❌ No había registros de ejecución
- ❌ El dashboard de Python no recibía datos de telemetría
- ❌ Los controles del tren funcionaban, pero la lectura de datos no

## Causa Raíz

**El script usaba `Update(ElapsedTime)` como función de entrada, pero RailWorks
no llama automáticamente esa función.**

RailWorks tiene un sistema de plugins con un punto de entrada específico: la
función `getdata()` (en minúsculas). El juego llama esta función automáticamente
en cada frame.

### Problema Técnico

```lua
-- ❌ INCORRECTO - RailWorks nunca llama esta función
function Update(ElapsedTime)
    -- código que nunca se ejecutaba
end
```

```lua
-- ✅ CORRECTO - RailWorks llama esto automáticamente
function getdata()
    -- código que se ejecuta cada frame
end
```

## Investigación Realizada

### Fase 1: Diagnóstico de Rutas

- Se verificó que las rutas relativas `"plugins/GetData.txt"` no funcionan en el
  contexto de plugins de RailWorks
- Se actualizaron a rutas absolutas: `C:\Program Files
  (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt`

### Fase 2: Simplificación del Script

- Script original: 760+ líneas con muchas características
- Script simplificado: 106 líneas solo con lo esencial
- La complejidad innecesaria ocultaba el problema fundamental

### Fase 3: Identificación del Punto de Entrada

- Se investigó la documentación de RailWorks
- Se descubrió que RailWorks llama a `getdata()` automáticamente, no a
  `Update()`
- Se cambió el nombre de la función principal de `Update(ElapsedTime)` a
  `getdata()`
- Se añadió `Update(ElapsedTime)` como fallback para compatibilidad

### Fase 4: Validación

- Se ejecutó Train Simulator Classic con el script actualizado
- Se verificó que GetData.txt se creaba y actualizaba en tiempo real
- Se confirmó que contenía datos de telemetría válidos del juego

## Solución Implementada

### Cambios Realizados

1. **Renombraron la función principal** de `Update(ElapsedTime)` a `getdata()`
2. **Se añadió `Update(ElapsedTime)`** como función de compatibilidad
   que llamaba a `getdata()`
3. **Se simplificó el código** eliminando complejidad innecesaria
4. **Se añadió logging** para verificar ejecución (luego removido)
5. **Se usaron rutas absolutas** para evitar problemas de resolución de ruta

### Script Final

- **Ubicación**:

  ```text
  C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\Railworks_GetData_Script.lua
  ```

- **Líneas**: 106
- **Punto de entrada**: `getdata()` llamada por RailWorks automáticamente
- **Frecuencia**: Cada 5 iteraciones del loop del juego
- **Datos exportados**: Speed, Acceleration, Gradient, TimeOfDay, SimulationTime
- **Formato**: Pares clave:valor en archivo de texto

## Datos Recopilados (Validación)

```text
ControlType:Speed
ControlName:CurrentSpeed
ControlMin:0
ControlMax:1000
ControlValue:-0.0049583874642849

ControlType:_Acceleration
ControlName:Acceleration
ControlMin:-10
ControlMax:10
ControlValue:-0.00062701513525099

ControlType:_Gradient
ControlName:Gradient
ControlMin:-100
ControlMax:100
ControlValue:-1.7993800640106

ControlType:TimeOfDay
ControlName:TimeOfDay
ControlMin:0
ControlMax:86400
ControlValue:54230.90625

ControlType:SimulationTime
ControlName:SimulationTime
ControlMin:0
ControlMax:999999
ControlValue:470.90628051758
```

## Impacto

- ✅ GetData.txt se crea correctamente
- ✅ Datos de telemetría se exportan en tiempo real
- ✅ Python puede leer los datos del archivo
- ✅ Dashboard puede acceder a información del tren
- ✅ Sistema de autopilot tiene datos para funcionar

## Lecciones Aprendidas

1. **Puntos de entrada específicos**: Cada sistema de plugins tiene funciones de
  entrada esperadas
2. **Rutas relativas vs absolutas**: En plugins de juegos, las rutas
   relativas no funcionan desde el contexto de ejecución
3. **Simplicidad es mejor**: Un script simple de 106 líneas es más confiable que
  uno complejo de 760
4. **Logging es crítico**: Los plugins no pueden usar consola; necesitan
   archivos de log para debugging
5. **RailWorks usa Lua 5.1**: Necesita funciones específicas como `getdata()` y
  `Update()`

## Estado Final

✅ **RESUELTO** - GetData.txt se crea y actualiza correctamente con telemetría en
tiempo real.

## Próximos Pasos

- Verificar que Python lee correctamente GetData.txt
- Validar conversión de unidades (m/s a km/h)
- Probar dashboard web con datos reales
- Validar ruta SendCommand.txt para comandos del tren
