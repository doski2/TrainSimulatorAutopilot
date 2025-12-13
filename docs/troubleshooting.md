# Guía de Troubleshooting - Train Simulator Autopilot

## Problemas Comunes y Soluciones

### 1. Problemas de Configuración

#### Configuración Inválida Rechazada

**Síntomas:**

- Mensaje de error al guardar configuración
- Configuración no se aplica
- Alertas de validación en el dashboard

**Solución:**

```javascript
// Verificar configuración actual en la consola del navegador
console.log(localStorage.getItem('dashboardConfig'));

// Resetear configuración a valores por defecto
localStorage.removeItem('dashboardConfig');
location.reload();
```

**Causas comunes:**

- Tema no válido (debe ser 'light' o 'dark')
- Intervalo de actualización fuera de rango (100-5000ms)
- Puntos de historial excesivos (>1000)
- Unidades de velocidad no válidas

#### Archivo config.ini Corrupto

**Síntomas:**

- Error al iniciar el sistema
- Configuración no se carga

**Solución:**

```batch
# Usar el archivo de ejemplo como base
copy config.ini.example config.ini
```

### 2. Problemas de Dashboard Web

#### Dashboard No Carga

**Síntomas:**

- Página en blanco
- Error 500 en el servidor
- JavaScript errors en consola

**Diagnóstico:**

```javascript
// Verificar conectividad del servidor
fetch('/api/status')
  .then((r) => r.json())
  .then((d) => console.log('Servidor OK:', d))
  .catch((e) => console.log('Error de servidor:', e));
```

**Soluciones:**

1. Verificar que Flask esté ejecutándose
2. Comprobar logs del servidor en `logs/autopilot.log`
3. Reiniciar el servicio web

#### Métricas No Se Actualizan

**Síntomas:**

- Valores estáticos en el dashboard
- No hay datos en tiempo real

**Causas posibles:**

- Conexión WebSocket perdida
- Throttling excesivo configurado
- Problemas con el sistema de telemetría

**Solución:**

```javascript
// Forzar reconexión WebSocket
location.reload();

// Verificar configuración de throttling
console.log('Throttling actual:', {
  metrics: window.metricsUpdateThrottle,
  charts: window.chartUpdateThrottle,
});
```

#### Gráficos No Se Renderizan

**Síntomas:**

- Área de gráficos vacía
- Errores de Chart.js en consola

**Solución:**

```javascript
// Limpiar caché de gráficos
if (window.speedChart) window.speedChart.destroy();
if (window.tempChart) window.tempChart.destroy();
location.reload();
```

### 3. Problemas de Rendimiento

#### Dashboard Lento o Congelado

**Síntomas:**

- Actualizaciones lentas
- Navegador no responde
- Alto uso de CPU

**Diagnóstico:**

```javascript
// Verificar configuración de rendimiento
console.log('Configuración de rendimiento:', {
  updateInterval: localStorage.getItem('updateInterval'),
  historyPoints: localStorage.getItem('historyPoints'),
  animations: localStorage.getItem('animations'),
});
```

**Optimizaciones:**

1. Aumentar intervalos de actualización (>1000ms)
2. Reducir puntos de historial (<100)
3. Desactivar animaciones
4. Usar throttling apropiado (métricas: 100ms, gráficos: 500ms)

#### Memoria Llena

**Síntomas:**

- Navegador se congela
- Errores de "out of memory"

**Solución:**

```javascript
// Limpiar historial de datos
if (window.metricsHistory) {
  window.metricsHistory = window.metricsHistory.slice(-50);
}
location.reload();
```

### 4. Problemas de Alertas

#### Alertas No Aparecen

**Síntomas:**

- No hay notificaciones visuales
- Condiciones críticas no se detectan

**Verificación:**

```javascript
// Verificar configuración de alertas
const config = JSON.parse(localStorage.getItem('dashboardConfig') || '{}');
console.log('Configuración de alertas:', config.alerts);

// Verificar datos actuales
console.log('Datos actuales:', window.currentMetrics);
```

#### Falsas Alertas

**Síntomas:**

- Alertas cuando no deberían aparecer
- Umbrales incorrectos

**Ajuste de umbrales:**

```javascript
// Umbrales recomendados
const recommendedThresholds = {
  engineTemp: { warning: 220, critical: 250 },
  oilPressure: { warning: 40, critical: 30 },
  fuelLevel: { warning: 20, critical: 10 }, // NO USADO - TSC tiene combustible infinito
  amps: { warning: 1500, critical: 1800 },
};
```

### 5. Problemas de Conectividad

#### Pérdida de Conexión WebSocket

**Síntomas:**

- Datos dejan de actualizarse
- Mensaje "Desconectado" en dashboard

**Solución automática:**

```javascript
// El dashboard tiene reconexión automática
// Forzar reconexión manual si es necesario
if (window.socket) {
  window.socket.disconnect();
  window.socket.connect();
}
```

#### Puerto Ocupado

**Síntomas:**

- Error al iniciar servidor: "Address already in use"

**Solución:**

```batch
# Encontrar proceso usando el puerto
netstat -ano | findstr :5000

# Matar proceso (reemplazar PID)
taskkill /PID <PID> /F

# O cambiar puerto en config.ini
# port = 5001
```

### 6. Problemas de Logs y Diagnóstico

#### Logs No Se Generan

**Verificación:**

```batch
# Verificar existencia de directorio logs
dir logs

# Verificar permisos
icacls logs

# Verificar configuración de logging
type logging_config.py
```

#### Logs Demasiado Grandes

**Solución:**

```batch
# Rotar logs semanalmente
# Configurar en logging_config.py:
# 'when': 'W0',  # Rotar semanalmente
# 'backupCount': 4  # Mantener 4 semanas
```

### 7. Problemas Específicos de Locomotora SD40

#### Métricas SD40 No Disponibles

**Síntomas:**

- Valores en cero o N/A
- Dashboard muestra "Sin datos"

**Diagnóstico:**

```javascript
// Verificar script Lua cargado
console.log('Script Lua detectado:', window.luaScriptLoaded);

// Verificar comunicación con simulador
fetch('/api/sd40/status')
  .then((r) => r.json())
  .then((d) => console.log('Estado SD40:', d));
```

#### Valores Irrealistas

**Síntomas:**

- Temperaturas imposibles (>500°F)
- Velocidades negativas
- Consumo energético irreal

**Solución:**

```javascript
// Resetear calibración en script Lua
// Buscar función resetCalibration() en engineScript.lua
```

### 8. Comandos de Diagnóstico Rápido

#### Verificar Estado General del Sistema

```batch
# Ejecutar diagnóstico completo
diagnostico_config.bat
```

#### Verificar Configuración

```batch
# Validar config.ini
python -c "import configparser; c=configparser.ConfigParser(); c.read('config.ini'); print('Configuración OK')"
```

#### Verificar Dependencias Python

```batch
# Listar paquetes instalados
pip list

# Verificar versiones críticas
pip show flask flask-socketio
```

#### Limpiar Caché del Navegador

```javascript
// Ejecutar en consola del navegador
localStorage.clear();
sessionStorage.clear();
location.reload();
```

### 9. Contacto y Soporte

Si los problemas persisten:

1. Recopilar información de diagnóstico
2. Revisar logs en `logs/autopilot.log`
3. Incluir configuración actual
4. Describir pasos para reproducir el problema

**Información útil para reportes:**

- Versión del sistema operativo
- Versión de Python
- Navegador y versión
- Configuración completa
- Logs de error relevantes

## 🔧 Problemas con las Métricas del Motor

### TractiveEffort (Esfuerzo de Tracción) no aparece

**Síntomas:**

- Tarjeta muestra "--" constantemente
- Valor nunca cambia de cero

**Causas posibles:**

1. **Locomotora parada**: El esfuerzo de tracción es 0 cuando no hay movimiento
2. **Script Lua no actualizado**: Verificar que `Railworks_GetData_Script.lua`
tenga el código nuevo
3. **Control no disponible**: Algunos modelos de locomotoras no exponen este
control

**Soluciones:**

```lua
-- Verificar en el script Lua que esté presente:
local TractiveEffort = Call("GetControlValue", "TractiveEffort", 0)
if not TractiveEffort then
    TractiveEffort = Call("*:GetControlValue", "TractiveEffort", 0)
end
```

**Prueba:** Acelerar la locomotora - el valor debería aparecer cuando aplique
potencia.

---

### RPM siempre muestra el mismo valor

**Síntomas:**

- RPM se mantiene constante (ej: 391 RPM)
- No cambia con la aceleración

**Causas posibles:**

1. **Motor al ralentí**: RPM normal al ralentí es ~300-400 RPM
2. **Modelo de locomotora**: Algunos modelos mantienen RPM constante
3. **Dato no disponible**: Verificar que el control RPM esté activo

**Solución:** Verificar en `debug.txt` que RPM cambie cuando acelera.

---

### Ammeter (Corriente) muestra valores erráticos

**Síntomas:**

- Valores negativos cuando debería ser positivo
- Cambios bruscos sin explicación

**Interpretación correcta:**

- **Positivo (+)**: Generando corriente (frenado regenerativo)
- **Negativo (-)**: Consumiendo corriente (tracción/aceleración)
- **Cero (0)**: Sin carga eléctrica

**Solución:** Los valores son correctos - es el comportamiento normal del
sistema eléctrico.

---

### Wheelslip (Deslizamiento) siempre en 1.0

**Síntomas:**

- Valor constante de 1.0
- No cambia en curvas o frenadas

**Causas posibles:**

1. **Valor base normal**: 1.0 puede ser el valor neutro
2. **Sin deslizamiento actual**: Solo cambia cuando hay pérdida de adherencia
3. **Configuración de locomotora**: Algunos modelos tienen diferente escala

**Interpretación:**

- **0.0-0.9**: Adherencia perfecta
- **1.0**: Adherencia normal
- **1.1-2.0**: Deslizamiento (requiere atención)

---

## 🔍 Diagnóstico General de Métricas

### Verificar que las métricas se lean correctamente

1. **Ejecutar TSC** con el Raildriver Interface activo
2. **Verificar `GetData.txt`** en
`C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\`
3. **Buscar líneas como:**

ControlName:TractiveEffort ControlValue:650.000 ControlName:RPM
ControlValue:450.500

### Verificar el dashboard

1. **Abrir dashboard** en `http://localhost:5001`
2. **Acercar la locomotora** para generar valores
3. **Verificar que las tarjetas** se actualicen

### Logs de depuración

```python
# En tsc_integration.py, agregar logging:
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar que se lean los nuevos campos:
print(f"TractiveEffort: {datos.get('TractiveEffort')}")
print(f"RPM: {datos.get('RPM')}")
print(f"Ammeter: {datos.get('Ammeter')}")
print(f"Wheelslip: {datos.get('Wheelslip')}")
```

---

## ⚠️ Alertas y Límites Recomendados

### Umbrales de Seguridad

| Métrica            | Normal        | Advertencia | Crítico | |
------------------ | ------------- | ----------- | ------- | |
**TractiveEffort** | 0-800N        | 800-1000N   | >1000N  | | **RPM**
| 300-700       | 700-850     | >850    | | **Ammeter**        | -600 to +800A |
±800-1000A  | >±1000A | | **Wheelslip**      | 0.0-1.2       | 1.2-1.5     |
>1.5    |

### Acciones Automáticas Recomendadas

- **Wheelslip > 1.5**: Reducir potencia automáticamente
- **RPM > 850**: Alertar sobrecalentamiento
- **Ammeter > 1200A**: Proteger sistema eléctrico
- **TractiveEffort = 0**: Verificar estado de locomotora

---

## 📞 Soporte Adicional para Métricas

Si las métricas no funcionan:

1. **Verificar versión del script Lua**
2. **Confirmar que TSC está ejecutándose**
3. **Revisar logs del dashboard**
4. **Verificar archivo GetData.txt**

**Última actualización:** Diciembre 2025

---

## 🔧 Problemas Recientes Resueltos (Diciembre 2025)

### Dashboard No Se Abre Después de Ejecutar start.bat

**Síntomas:**

- El script `start.bat` se ejecuta sin errores aparentes
- El servidor web no se inicia
- No se abre ningún navegador o aplicación
- Mensajes de "UnicodeEncodeError" en logs

**Causa Raíz:**

- Caracteres emoji (✅, ❌, 🚂) en el código Python causaban errores de
codificación Unicode
- El script `start.bat` intentaba iniciar aplicación Electron en lugar del
navegador web
- Problemas con la verificación de npm en el script batch

**Solución Paso a Paso:**

#### 1. Limpiar Emojis del Código Python

**Archivos afectados:**

- `direct_tsc_control.py`
- Cualquier archivo Python con emojis en mensajes de impresión

**Solución:**

```python
# ANTES (causa errores Unicode)
print("✅ Conexión exitosa")

# DESPUÉS (compatible con Windows)
print("[OK] Conexión exitosa")
```

**Reemplazos realizados:**

- ✅ → [OK]
- ❌ → [ERROR]
- 🚂 → [AUTO]

#### 2. Simplificar Script start.bat

**Problema:** El script intentaba iniciar Electron cuando npm estaba disponible,
pero en entornos sin interfaz gráfica esto fallaba.

**Solución:** Modificar `start.bat` para siempre abrir navegador web:

```batch
@echo off
echo ========================================
echo TRAIN SIMULATOR AUTOPILOT - DESKTOP
echo ========================================

REM ... verificaciones básicas ...

echo Iniciando servidor web...

REM Iniciar servidor en background
powershell -Command "Start-Process -NoNewWindow -FilePath 'python' -ArgumentList 'web_dashboard.py' -RedirectStandardOutput 'web_server.log' -RedirectStandardError 'web_server_error.log'"

timeout /t 5 /nobreak >nul

REM Verificar servidor
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:5001' -TimeoutSec 5 | Out-Null; Write-Host 'Servidor web iniciado correctamente' } catch { Write-Host 'Error al conectar' }"

REM Abrir navegador
start http://localhost:5001
```

#### 3. Verificación Final

**Comandos para verificar:**

```batch
# Verificar puerto
Test-NetConnection -ComputerName localhost -Port 5001

# Verificar procesos
Get-Process -Name "python"

# Revisar logs
type web_server.log
```

**Resultado esperado:**

- Servidor web ejecutándose en `http://localhost:5001`
- Dashboard accesible desde navegador web
- Sin errores Unicode en la consola

### Prevención de Problemas Similares

1. **Evitar emojis en código Python** destinado a Windows
2. **Probar scripts batch** en cmd.exe, no solo PowerShell
3. **Usar navegador web** como fallback cuando Electron no esté disponible
4. **Implementar logging robusto** para debugging

**Archivos modificados:**

- `direct_tsc_control.py` - Limpieza de emojis
- `start.bat` - Simplificación y corrección de lógica
- `web_server.log` - Nuevo archivo de logs del servidor

**Estado:** ✅ Resuelto - Dashboard funciona correctamente
