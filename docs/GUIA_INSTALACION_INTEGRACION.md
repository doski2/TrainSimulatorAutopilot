# 🚀 Guía de Instalación e Integración - Train Simulator Autopilot

## Parte 1: Instalación Rápida del Sistema

### Requisitos Previos

- **Python 3.8+** instalado
- **Train Simulator Classic** instalado
- **Git** (opcional, para clonar repositorio)

### ⚡ Instalación Automática (Recomendado)

#### Windows

```cmd
# 1. Clonar o descargar el repositorio
git clone https://github.com/tu-usuario/train-simulator-autopilot.git
cd train-simulator-autopilot

# 2. Ejecutar deployment automático
scripts\deploy.bat

# 3. Iniciar la aplicación
start_production.bat
```

#### Linux/Mac

```bash
# 1. Clonar o descargar el repositorio
git clone https://github.com/tu-usuario/train-simulator-autopilot.git
cd train-simulator-autopilot

# 2. Ejecutar deployment automático
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 3. Iniciar la aplicación
./start_production.sh
```

### 🔧 Instalación Manual

#### 1. Preparar Entorno

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

#### 2. Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

#### 3. Configurar Aplicación

```bash
# Copiar configuración de ejemplo
cp config.ini.example config.ini

# Editar configuración según necesidades
notepad config.ini  # Windows
nano config.ini     # Linux/Mac
```

#### 4. Verificar Instalación

```bash
# Ejecutar tests básicos
python -m pytest tests/unit/ -v

# Verificar que el dashboard inicia
python web_dashboard.py
```

### 🌐 Acceder a los Dashboards

Una vez iniciado, acceder a:

- **Dashboard Principal**: <http://localhost:5001/>
- **Dashboard Bokeh Interactivo**: <http://localhost:5001/bokeh>
- **Dashboard Seaborn Analytics**: <http://localhost:5001/analytics>

### ⚙️ Configuración Básica

#### Archivo `config.ini`

```ini
[GENERAL]
debug = false
log_level = INFO

[TSC_INTEGRATION]
host = localhost
port = 1435
timeout = 5.0

[WEB_DASHBOARD]
host = 0.0.0.0
port = 5001

[PERFORMANCE]
compression_enabled = true
cache_enabled = true
```

#### Variables de Entorno

```bash
# Para producción
export FLASK_ENV=production
export FLASK_DEBUG=false

# Para desarrollo
export FLASK_ENV=development
export FLASK_DEBUG=true
```

### 🔍 Verificación de Funcionamiento

#### 1. Verificar Conexión TSC

```bash
python -c "from tsc_integration import TSCIntegration; tsc = TSCIntegration(); print('Conexión OK' if tsc.conectar() else 'Error de conexión')"
```

#### 2. Verificar Dashboard Web

```bash
curl http://localhost:5001/api/status
```

#### 3. Verificar Optimizaciones

```bash
python cross_browser_validator.py
```

### 🚨 Solución de Problemas

#### Error: "Python no encontrado"

**Solución**: Instalar Python 3.8+ desde <https://python.org>

#### Error: "Puerto 5001 ocupado"

**Solución**: Cambiar puerto en `config.ini` o cerrar aplicación que usa el
puerto

#### Error: "No se puede conectar a TSC"

**Solución**:

1. Verificar que Train Simulator Classic esté ejecutándose
2. Revisar configuración de red en TSC
3. Verificar firewall/antivirus

#### Error: "Dependencias faltantes"

**Solución**:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 📊 Monitoreo Básico

#### Logs de Aplicación

```bash
# Ver logs en tiempo real
tail -f logs/train_simulator_autopilot.log
```

#### Métricas de Rendimiento

```bash
# Ver estadísticas de optimización
curl http://localhost:5001/api/optimize/stats
```

#### Estado del Sistema

```bash
# Ver estado general
curl http://localhost:5001/api/status
```

### 🔄 Actualización

```bash
# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Reiniciar aplicación
# Windows: start_production.bat
# Linux/Mac: ./start_production.sh
```

### ✅ Checklist Post-Instalación

- [ ] Dashboard accesible en <http://localhost:5001>
- [ ] Conexión con Train Simulator Classic funcionando
- [ ] Gráficos Bokeh mostrándose correctamente
- [ ] Reportes automáticos generándose
- [ ] Optimizaciones activas (compresión, cache)
- [ ] Tests pasando exitosamente
- [ ] Logs sin errores críticos

## Parte 2: Integración de Nuevos Juegos al Sistema

### 📋 Paso 1: Análisis del Proyecto Actual

#### Estructura del Sistema Actual

El proyecto TrainSimulatorAutopilot tiene los siguientes componentes
principales:

##### 🗂️ **Documentación** (`docs/`)

- `data-received-from-railworks.md` - Documentación completa de variables TSC
- `template_telemetry_documentation.txt` - Plantilla genérica reutilizable
- `TELEMETRY_TEMPLATE_README.md` - Guía de uso de plantillas
- Ejemplos adaptados: `example_msfs_telemetry.txt`,
`example_victoria3_telemetry.txt`

##### 🔧 **Captura de Datos**

- **Script Lua**: `Railworks_GetData_Script.lua` (en carpeta plugins de
RailWorks)
- **Archivo de datos**: `GetData.txt` generado por el script Lua
- **Frecuencia**: Cada 100ms (configurable)

##### 🐍 **Backend Python**

- `tsc_integration.py` - Clase principal de integración
  - Lee datos del archivo `GetData.txt`
  - Mapea nombres TSC → nombres IA (`mapeo_controles`)
  - Procesa y valida datos
- `web_dashboard.py` - Servidor Flask con WebSockets
  - Envía datos en tiempo real al frontend
  - APIs REST para configuración

##### 🌐 **Frontend Web**

- **Templates HTML**: `web/templates/` (index.html, sd40.html)
- **JavaScript**: `web/static/js/` (dashboard.js, dashboard-sd40.js)
- **CSS**: `web/static/css/dashboard.css`
- **WebSockets**: Actualización en tiempo real

##### ⚙️ **Configuración**

- `config.ini` - Configuración principal
- `mapeo_controles` en `tsc_integration.py` - Diccionario de mapeo
- Estados de implementación en documentación

### 🎯 Paso 2: Evaluación del Nuevo Juego

#### Criterios de Compatibilidad

Antes de empezar, verifica:

##### ✅ **API/Interfaz Disponible**

- ¿El juego tiene API oficial? (SimConnect para MSFS, Lua para RailWorks)
- ¿Permite mods/scripts? (Victoria 3, otros Paradox games)
- ¿Se pueden leer variables en tiempo real?

##### ✅ **Tipo de Datos**

- **Simuladores Físicos**: Velocidad, RPM, presión, coordenadas
- **Juegos de Estrategia**: Economía, población, relaciones diplomáticas
- **Arcade**: Puntuación, vidas, power-ups, estadísticas de juego

##### ✅ **Frecuencia de Actualización**

- ¿Cada cuánto se actualizan los datos?
- ¿Es compatible con actualizaciones en tiempo real? (100ms ideal)

##### ✅ **Complejidad de Integración**

- Baja: Juegos con APIs simples (MSFS SimConnect)
- Media: Juegos con scripting limitado (RailWorks Lua)
- Alta: Juegos sin API oficial (requiere memory reading u otros hacks)

### 🚀 Paso 3: Planificación de la Integración

#### 3.1 Definir Alcance

**Preguntas clave:**

- ¿Qué tipo de autopilot quieres? (control automático, monitoreo, alertas)
- ¿Qué datos son críticos vs opcionales?
- ¿Frecuencia de actualización necesaria?

**Ejemplos por tipo de juego:**

| Tipo de Juego        | Autopilot Posible            | Datos Críticos
| | -------------------- | ---------------------------- |
------------------------------ | | **Simulador Vuelo**  | Control automático de
vuelo  | Altitud, rumbo, velocidad      | | **Simulador Tren**   | Control de
velocidad/frenos  | Velocidad, límites, presiones  | | **Juego Estrategia** |
Gestión automática económica | Economía, estabilidad política | | **Juego
Arcade**     | Mejora de rendimiento        | Puntuación, estadísticas       |

#### 3.2 Arquitectura de Integración

**Opciones de arquitectura:**

1. **Script en el Juego** (como TSC)
   - Ventaja: Acceso directo a variables del juego
   - Desventaja: Requiere conocimientos del lenguaje del juego

2. **API Externa** (como MSFS)
   - Ventaja: Más estable y oficial
   - Desventaja: Limitado a lo que expone la API

3. **Memory Reading** (avanzado)
   - Ventaja: Acceso a todo
   - Desventaja: Inestable, requiere reversing

4. **Screen Capture + OCR** (último recurso)
   - Ventaja: Funciona con cualquier juego
   - Desventaja: Lento, inexacto

### 📝 Paso 4: Documentación Inicial

#### 4.1 Crear Archivo de Documentación

Usa la plantilla `template_telemetry_documentation.txt`:

```bash
cp docs/template_telemetry_documentation.txt docs/data_[NOMBRE_JUEGO].txt
```

**Estructura básica:**

```text
// =============================================================================
// DATOS DE TELEMETRÍA DE [NOMBRE_JUEGO]
// Archivo generado por [MÉTODO_CAPTURA]
// Actualizado: [FECHA]
// =============================================================================
```

#### 4.2 Identificar Variables Iniciales

**Método de identificación:**

1. **Documentación oficial** del juego
2. **Comunidades de modding** (forums, wikis)
3. **Herramientas de debugging** del juego
4. **Análisis de archivos** de configuración
5. **Pruebas manuales** y logging

**Ejemplo para un simulador de vuelo:**

```log
IndicatedAirSpeed: 120              // [IMPLEMENTADO] Velocidad indicada (nudos)
TrueAirSpeed: 125                   // [IMPLEMENTADO] Velocidad verdadera (nudos)
Altitude: 8500                      // [IMPLEMENTADO] Altitud (pies)
Heading: 275.5                      // [IMPLEMENTADO] Rumbo magnético (grados)
```

#### 4.3 Definir Estados de Implementación

- `[IMPLEMENTADO]` - Ya integrado y probado
- `[PENDIENTE]` - Identificado, pendiente de implementar
- `[EXPERIMENTAL]` - En desarrollo/pruebas
- `[NO RELEVANTE]` - No útil para autopilot
- `[OBSOLETO]` - Ya no disponible

### 🔧 Paso 5: Desarrollo del Sistema de Captura

#### 5.1 Elegir Método de Captura

**Para juegos con scripting (como RailWorks):**

- Crea script en el lenguaje del juego
- Escribe datos a archivo de texto
- Python lee el archivo periódicamente

**Para juegos con API (como MSFS):**

- Conecta directamente a la API
- Procesa datos en tiempo real
- Integra con el sistema Python

#### 5.2 Implementar Clase de Integración

Crea nueva clase basada en `tsc_integration.py`:

```python
class [NombreJuego]Integration:
    def __init__(self):
        # Configurar rutas, conexiones, etc.

    def leer_datos(self) -> Dict[str, Any]:
        # Leer datos del juego
        pass

    def convertir_datos_ia(self, datos_raw) -> Dict[str, Any]:
        # Mapear a nombres de IA
        pass
```

**Ejemplo de mapeo:**

```python
self.mapeo_controles = {
    "VelocidadActual": "velocidad_actual",
    "Altitud": "altitud",
    "Combustible": "combustible",
    # ... más mapeos
}
```

#### 5.3 Manejo de Errores y Validación

```python
def validar_datos(self, datos):
    """Validar que los datos sean razonables."""
    if datos.get('velocidad_actual', 0) < 0:
        logger.warning("Velocidad negativa detectada")
    # ... más validaciones
```

### 🌐 Paso 6: Integración con Dashboard

#### 6.1 Actualizar Backend

Modificar `web_dashboard.py`:

```python
# Importar nueva integración
from [nombre_juego]_integration import [NombreJuego]Integration

# Inicializar
[nombre_juego]_integration = [NombreJuego]Integration()

# En el loop de actualización
datos = [nombre_juego]_integration.leer_datos()
socketio.emit('telemetry_update', datos)
```

#### 6.2 Actualizar Frontend

**HTML Templates:**

- Agregar nuevas tarjetas de métricas
- Adaptar layout según necesidades del juego

**JavaScript:**

```javascript
// En dashboard.js
socket.on('telemetry_update', function (data) {
  // Actualizar displays
  updateVelocity(data.velocidad_actual);
  updateAltitude(data.altitud);
  // ... más actualizaciones
});
```

**CSS:**

- Agregar estilos para nuevas métricas
- Mantener consistencia visual

#### 6.3 Configuración

Actualizar `config.ini`:

```ini
[juego]
enabled = true
data_source = archivo  # o 'api', 'memory', etc.
update_interval = 100  # ms
```

### 🧪 Paso 7: Pruebas y Validación

#### 7.1 Pruebas Unitarias

```python
def test_[nombre_juego]_integration():
    integration = [NombreJuego]Integration()
    datos = integration.leer_datos()
    assert 'velocidad_actual' in datos
    assert datos['velocidad_actual'] >= 0
```

#### 7.2 Pruebas de Integración

- Verificar que datos fluyan correctamente
- Probar actualizaciones en tiempo real
- Validar mapeo de nombres
- Comprobar manejo de errores

#### 7.3 Pruebas de Rendimiento

- Medir latencia de captura de datos
- Verificar uso de CPU/memoria
- Probar con diferentes escenarios del juego

#### 7.4 Pruebas de Usuario

- Funcionalidad del dashboard
- Legibilidad de datos
- Utilidad para autopilot

### 📚 Paso 8: Documentación Final

#### 8.1 Actualizar README

Agregar sección en `README.md`:

```markdown
## Soporte para [Nombre Juego]

### Requisitos

- [Nombre Juego] versión X.X
- [Dependencias específicas]

### Configuración

1. [Pasos de instalación]
2. [Configuración específica]
3. [Cómo ejecutar]

### Variables Soportadas

- Lista de variables implementadas
- Estados de implementación
```

#### 8.2 Crear Guía de Troubleshooting

```markdown
## Solución de Problemas - [Nombre Juego]

### Problema: No se reciben datos

**Solución:**

1. Verificar que [Nombre Juego] esté ejecutándose
2. Comprobar permisos de archivos
3. Revisar logs del sistema

### Problema: Datos incorrectos

**Solución:**

1. Verificar versión del juego
2. Comprobar configuración regional
3. Validar script de captura
```

#### 8.3 Actualizar CHANGELOG

```markdown
## [Versión] - [Fecha]

### Agregado

- Soporte para [Nombre Juego]
- Nuevas variables: lista de variables
- Dashboard actualizado con métricas específicas
```

### 🔄 Paso 9: Mantenimiento

#### 9.1 Monitoreo Continuo

- Seguimiento de issues en GitHub
- Actualizaciones cuando cambie el juego
- Mejoras basadas en feedback de usuarios

#### 9.2 Actualizaciones

- Verificar compatibilidad con nuevas versiones del juego
- Actualizar scripts de captura si es necesario
- Mantener documentación al día

### 📋 Checklist Final

- [ ] Documentación inicial completa
- [ ] Sistema de captura implementado
- [ ] Integración backend funcionando
- [ ] Dashboard actualizado
- [ ] Pruebas unitarias e integración
- [ ] Documentación de usuario
- [ ] Guía de troubleshooting
- [ ] CHANGELOG actualizado

### 🎯 Ejemplos por Tipo de Juego

#### Simulador de Vuelo (MSFS)

- **Captura**: SimConnect API
- **Variables**: IAS, ALT, HDG, VS, RPM, FUEL
- **Autopilot**: Control automático de vuelo

#### Juego de Estrategia (Victoria 3)

- **Captura**: API de modding o archivos de save
- **Variables**: GDP, Población, Estabilidad, Ejército
- **Autopilot**: Gestión económica/diplomática automática

#### Juego Arcade (Retro Game)

- **Captura**: Memory reading o screen capture
- **Variables**: Score, Lives, Level, Power-ups
- **Autopilot**: Mejora automática de rendimiento

Esta guía proporciona un framework completo para integrar cualquier juego al
sistema de autopilot. El proceso puede adaptarse según las capacidades
específicas de cada juego.

## 📞 Soporte

- **Documentación completa**: `docs/` directory
- **Issues**: Crear issue en GitHub
- **Logs**: Revisar `logs/train_simulator_autopilot.log`

**Última actualización:** Diciembre 2025
