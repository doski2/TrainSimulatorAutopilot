# 🔧 Guía de Solución de Problemas - Train Simulator Autopilot

## 📋 Información General

Esta guía ayuda a diagnosticar y resolver los problemas más comunes del sistema
Train Simulator Autopilot.

## 🚨 Problemas Críticos

### 1. Sistema No Inicia

**Síntomas**:

- Error al ejecutar `python web_dashboard.py`
- "Module not found" o import errors
- Crash inmediato del sistema

**Diagnóstico**:

```bash
# Verificar Python
python --version

# Verificar dependencias
python -c "import flask, flask_socketio, numpy, pandas"

# Verificar archivos
ls -la *.py
```

**Soluciones**:

1. **Dependencias faltantes**:

```bash
pip install -r requirements.txt
```

1. **Python version incorrecta**:

```bash
# Instalar Python 3.8+
# O actualizar pip
python -m pip install --upgrade pip
```

1. **Archivos corruptos**:

```bash
git reset --hard HEAD
git pull origin main
```

### 2. Dashboard No Carga

**Síntomas**:

- Página en blanco en <http://localhost:5000>
- Error "Connection refused"
- Timeout al cargar

**Diagnóstico**:

```bash
# Verificar puerto
netstat -ano | findstr :5000

# Probar conexión
curl http://localhost:5000/api/status

# Verificar logs
tail -f logs/autopilot.log
```

**Soluciones**:

1. **Puerto ocupado**:

```bash
# Cambiar puerto en web_dashboard.py
# O matar proceso
taskkill /PID <PID> /F
```

1. **Firewall bloqueando**:

- Agregar excepción para Python en firewall
- Deshabilitar temporalmente antivirus

1. **Configuración incorrecta**:

```ini
# Verificar config.ini
[GENERAL]
debug_mode = true
```

### 3. Sin Datos de Telemetría

**Síntomas**:

- Valores en cero o sin actualizar
- "Integración TSC no disponible"
- Datos simulados no aparecen

**Diagnóstico**:

```bash
# Verificar TSC ejecutándose
tasklist | findstr RailWorks

# Verificar archivos de datos
ls -la "C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\"

# Probar integración
python -c "from tsc_integration import TSCIntegration; t = TSCIntegration(); print(t.get_telemetry())"
```

**Soluciones**:

1. **TSC no ejecutándose**:

- Iniciar Train Simulator Classic
- Verificar que esté en modo "Drive"

1. **Rutas incorrectas**:

```ini
[TSC_INTEGRATION]
data_file_path = C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt
command_file_path = C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt
```

1. **Permisos insuficientes**:

- Ejecutar como administrador
- Verificar permisos de escritura en carpeta plugins

## ⚠️ Problemas de Rendimiento

### 4. Actualizaciones Lentas

**Síntomas**:

- Dashboard se congela
- Latencia > 100ms
- CPU/Memoria alta

**Diagnóstico**:

```bash
# Verificar rendimiento
curl http://localhost:5000/api/performance

# Monitorear recursos
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%')"
```

**Soluciones**:

1. **Optimizaciones automáticas**:

```bash
# El sistema aplica optimizaciones automáticamente
# Verificar en logs
grep "optimizaciones" logs/autopilot.log
```

1. **Reducir frecuencia de actualización**:

```ini
[TSC_INTEGRATION]
update_frequency_hz = 5  # Reducir de 10
```

1. **Limpiar caché**:

```bash
# Reiniciar sistema
# Los datos se limpiarán automáticamente
```

### 5. Memoria Llena

**Síntomas**:

- Uso de RAM > 80%
- Sistema lento
- Crash por out of memory

**Diagnóstico**:

```bash
# Verificar uso de memoria
python -c "import psutil; print(f'Memory: {psutil.virtual_memory()}')"

# Verificar archivos de log grandes
ls -lah logs/
```

**Soluciones**:

1. **Limpiar logs antiguos**:

```bash
# Logs > 30 días
find logs -name "*.log" -mtime +30 -delete
```

1. **Reducir retención de datos**:

```ini
[VISUALIZATION]
max_data_points = 500  # Reducir de 1000
```

1. **Reiniciar servicios**:

```bash
# Cerrar y reiniciar
python web_dashboard.py
```

## 🔌 Problemas de Conectividad

### 6. WebSocket No Conecta

**Síntomas**:

- Datos no se actualizan en tiempo real
- Error "WebSocket connection failed"
- Console errors en navegador

**Diagnóstico**:

```javascript
// En browser console (F12)
const socket = io('http://localhost:5000');
socket.on('connect', () => console.log('Connected'));
socket.on('connect_error', (err) => console.log('Error:', err));
```

**Soluciones**:

1. **CORS issues**:

```javascript
// Verificar configuración en web_dashboard.py
CORS(app, origins=["http://localhost:5000"])
```

1. **Proxy/Network issues**:

- Deshabilitar proxy del sistema
- Verificar configuración de red

1. **Browser cache**:

- Hard refresh (Ctrl+F5)
- Limpiar cache del navegador

### 7. APIs No Responden

**Síntomas**:

- 404/500 errors en endpoints
- Timeout en requests
- Datos vacíos

**Diagnóstico**:

```bash
# Test básico
curl -v http://localhost:5000/api/status

# Verificar endpoints
curl http://localhost:5000/api/alerts
curl http://localhost:5000/api/performance
```

**Soluciones**:

1. **Servidor no iniciado**:

```bash
python web_dashboard.py
```

1. **Rutas incorrectas**:

```python
# Verificar en web_dashboard.py
@app.route('/api/status')
def api_status():
    # código
```

1. **Errores de Python**:

```bash
# Verificar logs
tail -f logs/autopilot.log
```

## 🎮 Problemas de TSC Integration

### 8. Locomotora No Responde

**Síntomas**:

- Comandos no tienen efecto
- Telemetría no cambia
- "Command failed" messages

**Diagnóstico**:

```bash
# Verificar archivos de comando
ls -la "C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt"

# Probar escritura
echo "test" > "C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\SendCommand.txt"
```

**Soluciones**:

1. **Raildriver no configurado**:

- Instalar y configurar Raildriver Interface
- Verificar mapeo de controles

1. **Formato de comandos incorrecto**:

```python
# Verificar formato en tsc_integration.py
command_format = "throttle:{value}"
```

1. **TSC version incompatible**:

- Verificar compatibilidad con versión de TSC
- Actualizar scripts de TSC si necesario

### 9. Datos Inconsistentes

**Síntomas**:

- Valores erráticos
- Saltos en telemetría
- Alertas falsas

**Diagnóstico**:

```python
# Debug telemetría
from tsc_integration import TSCIntegration
tsc = TSCIntegration()
for i in range(10):
    data = tsc.get_telemetry()
    print(f"Sample {i}: {data}")
    time.sleep(0.1)
```

**Soluciones**:

1. **Frecuencia de muestreo alta**:

```ini
[TSC_INTEGRATION]
update_frequency_hz = 5
```

1. **Filtrado insuficiente**:

```python
# Aumentar smoothing en autopilot_system.py
acceleration_smoothing = 0.9  # Aumentar de 0.8
```

1. **Calibración necesaria**:

- Recalibrar sensores de TSC
- Verificar configuración de Raildriver

## 📊 Problemas de Visualización

### 10. Bokeh No Carga

**Síntomas**:

- Botón "Cargar Bokeh" no funciona
- Error 500 en /bokeh
- Gráficos no aparecen

**Diagnóstico**:

```bash
# Verificar puerto Bokeh
netstat -ano | findstr :5006

# Test Bokeh server
curl http://localhost:5006
```

**Soluciones**:

1. **Bokeh no iniciado**:

```python
# Verificar en web_dashboard.py
bokeh_server = BokehServer()
bokeh_server.start()
```

1. **Dependencias faltantes**:

```bash
pip install bokeh
```

1. **Puerto ocupado**:

```python
# Cambiar puerto en configuración
bokeh_port = 5007
```

### 11. Gráficos No Se Actualizan

**Síntomas**:

- Gráficos estáticos
- Datos no fluyen
- Error en console del navegador

**Diagnóstico**:

```javascript
// En browser console
console.log('Bokeh version:', Bokeh.version);
console.log('WebSocket readyState:', socket.readyState);
```

**Soluciones**:

1. **WebSocket issues**:

- Verificar conexión WebSocket
- Reiniciar navegador

1. **Bokeh callbacks**:

```python
# Verificar callbacks en bokeh_charts.py
source.stream(new_data, rollover=max_points)
```

1. **Data format issues**:

- Verificar formato de datos enviados
- Debug en browser developer tools

### 12. Controles No Se Actualizan (Puertas/Luces)

**Síntomas**:

- Botones de puertas/luces no cambian estado visual
- Comandos siempre hacen lo mismo (ej: siempre abren puertas)
- Estado de controles no se mantiene entre clics

**Diagnóstico**:

```bash
# Verificar estado de controles
curl http://localhost:5000/api/control/status

# Debería mostrar:
{
  "success": true,
  "control_states": {
    "doors_open": false,
    "lights_on": true
  }
}
```

**Soluciones**:

1. **Reiniciar servidor**:

```bash
# El estado se reinicia al iniciar
python web_dashboard.py
```

1. **Verificar implementación de estado**:

- Los controles ahora mantienen estado interno
- Cada clic alterna entre abrir/cerrar, encender/apagar
- El estado se puede consultar vía API

1. **Problema resuelto en v2.1.0**:

- Sistema ahora mantiene estado de puertas y luces
- Comandos correctos se envían según estado actual
- Mensajes de confirmación muestran acción realizada

## 🔧 Herramientas de Diagnóstico

### Script de Diagnóstico Completo

```python
#!/usr/bin/env python3
# diagnostic_script.py

import requests
import socket
import psutil
import os
from pathlib import Path

def run_diagnostics():
    print("🔍 Diagnóstico del Sistema Train Simulator Autopilot")
    print("=" * 60)

    # 1. Verificar servicios
    print("\n1. Verificando servicios...")
    try:
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        print(f"✅ API Status: {response.status_code}")
    except:
        print("❌ API Status: No disponible")

    # 2. Verificar archivos
    print("\n2. Verificando archivos...")
    config_path = Path('config.ini')
    if config_path.exists():
        print("✅ config.ini: Presente")
    else:
        print("❌ config.ini: Faltante")

    # 3. Verificar recursos
    print("\n3. Verificando recursos...")
    print(f"CPU: {psutil.cpu_percent()}%")
    print(f"RAM: {psutil.virtual_memory().percent}%")

    # 4. Verificar TSC
    print("\n4. Verificando TSC...")
    tsc_path = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RailWorks")
    if tsc_path.exists():
        print("✅ TSC instalado")
    else:
        print("❌ TSC no encontrado")

    print("\n🏁 Diagnóstico completado")

if __name__ == "__main__":
    run_diagnostics()
```

### Logs Importantes

- `logs/autopilot.log`: Logs principales del sistema
- `logs/performance.log`: Métricas de rendimiento
- `logs/tsc_integration.log`: Problemas de integración TSC
- `reports/performance_report_*.json`: Reportes de rendimiento

### Comandos Útiles

```bash
# Ver procesos Python
ps aux | grep python

# Ver conexiones de red
netstat -tlnp | grep :5000

# Ver uso de disco
df -h

# Ver logs en tiempo real
tail -f logs/autopilot.log
```

## 📞 Obtener Ayuda

Si los problemas persisten:

1. **Recopilar información**:
   - Logs completos
   - Configuración actual
   - Versión del sistema
   - Pasos para reproducir

2. **Crear issue en GitHub**:
   - Usar template de bug report
   - Incluir logs y configuración
   - Describir pasos exactos

3. **Comunidad**:
   - Discord: [Train Simulator Autopilot](https://discord.gg/train-simulator)
   - Foro: [Discussions][gh_discussions]

---

<!-- markdownlint-disable MD013 -->
[gh_discussions]: https://github.com/tu-usuario/train-simulator-autopilot/discussions
<!-- markdownlint-enable MD013 -->

## 🚀 Recuperación de Emergencia

### Reset Completo del Sistema

```bash
# 1. Detener todos los procesos
pkill -f python
pkill -f RailWorks

# 2. Limpiar archivos temporales
rm -rf __pycache__
rm -rf *.pyc

# 3. Reset configuración
cp config.ini.example config.ini

# 4. Limpiar logs
rm -rf logs/*
rm -rf reports/*

# 5. Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# 6. Reiniciar
python web_dashboard.py
```

### Backup y Restore

```bash
# Backup
tar -czf backup_$(date +%Y%m%d).tar.gz config.ini logs/ reports/

# Restore
tar -xzf backup_20251129.tar.gz
```

---

*Última actualización: Noviembre 2025*</content> parameter
name="filePath">c:\Users\doski\TrainSimulatorAutopilot\TROUBLESHOOTING.md
