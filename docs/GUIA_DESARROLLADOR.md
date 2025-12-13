# 🚀 Guía Rápida para Desarrolladores - Train Simulator Autopilot

## 📋 Inicio Rápido

### 1. Configuración del Entorno

```bash
# Clonar repositorio
git clone <repository-url>
cd TrainSimulatorAutopilot

# Instalar dependencias
pip install -r requirements.txt
npm install

# Configurar entorno
python configurator.py
```

### 2. Inicio del Sistema

```bash
# Opción 1: Inicio automático completo
./start.bat

# Opción 2: Modo desarrollo
./start_dev.bat

# Opción 3: Manual
python web_dashboard.py  # Terminal 1
npm start               # Terminal 2 (Electron)
```

## 🏗️ Arquitectura del Sistema

### 📊 Diagramas Disponibles

- **`architecture_diagram.png`** - Vista general (163KB)
- **`architecture_diagram_complete.png`** - Vista completa del proyecto (281KB)

Generados automáticamente con `python architecture_diagram.py`

### 🔄 Flujo de Datos Principal

Usuario → Electron App → Flask Server → Python Backend → Raildriver → Lua Script
→ TSC ↖️ WebSocket ↖️ REST API ↖️ Telemetría ↖️ Comandos ↖️

## 📁 Estructura del Proyecto

TrainSimulatorAutopilot/ ├── 🖥️ main.js # Aplicación Electron ├── 🌐
web_dashboard.py # Servidor Flask principal ├── 🐍 tsc_integration.py #
Integración con TSC ├── 🤖 autopilot_system.py # Lógica de IA ├── 📊 dashboard/ #
Componentes del dashboard ├── 🔧 scripts/ # Scripts de automatización ├── 🧪
tests/ # Suite de testing completa ├── 📚 docs/ # Documentación completa └── ⚙️
config.ini # Configuración del sistema

## 🔧 Desarrollo y Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/unit/test_tsc_integration.py
pytest tests/unit/test_dashboard.py

# Con cobertura
pytest --cov=.

# Tests de rendimiento
python -m pytest tests/ -k "performance"
```

### Debugging

```bash
# Modo desarrollo con logs detallados
./start_dev.bat

# Ver logs en tiempo real
tail -f logs/autopilot.log

# Debug de integración TSC
python -c "from tsc_integration import TSCIntegration; t = TSCIntegration(); print(t.leer_datos_archivo())"
```

## 📚 Documentación Importante

### 📖 Para Empezar

- **[README.md](README.md)** - Instalación y uso básico
- **[README_DESKTOP.md](README_DESKTOP.md)** - Aplicación desktop
- **[docs/indice-documentacion.md](indice-documentacion.md)** - Índice completo

### 🏛️ Arquitectura

- **[docs/ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura completa
- **[docs/DIAGRAMS.md](DIAGRAMS.md)** - Diagramas de arquitectura
- **[docs/RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** - Resumen ejecutivo

### 🔧 Desarrollo

- **[docs/procedimientos/procedimientos-
  estandar.md](procedimientos/procedimientos-estandar.md)** -
Guías prácticas
- **[docs/ejemplos/ejemplos-codigo.md](ejemplos/ejemplos-codigo.md)** - Ejemplos
de código
- **[docs/testing-framework.md](testing-framework.md)** - Framework de testing

### 🔗 Integración

- **[docs/integration.md](integration.md)** - Guía de integración
- **[docs/api-reference.md](api-reference.md)** - Referencia de APIs
- **[docs/flujo-ia-conduccion.md](flujo-ia-conduccion.md)** - Flujo de IA

## 🎯 Métricas y Telemetría

### Variables Principales Implementadas

| Variable                          | Mapeo IA                   | Dashboard
| Estado       | | --------------------------------- |
-------------------------- | --------------------- | ------------ | |
CurrentSpeed                      | velocidad_actual           | ✅ Velocidad
| Implementado | | Acceleration                      | aceleracion
| ✅ Aceleración        | Implementado | | TractiveEffort                    |
esfuerzo_traccion          | ✅ Tracción           | Implementado | | RPM
| rpm                        | ✅ RPM                | Implementado | | Ammeter
| amperaje                   | ✅ Corriente          | Implementado | | Wheelslip
| deslizamiento_ruedas       | ✅ Deslizamiento      | Implementado | |
AirBrakePipePressurePSI           | presion_tubo_freno         | ✅ Tubo de Freno
| Implementado | | MainReservoirPressurePSIDisplayed |
presion_deposito_principal | ✅ Depósito Principal | Implementado | |
AuxReservoirPressure              | presion_deposito_auxiliar  | ✅ Depósito
Auxiliar  | ⭐ Nuevo     |

### Endpoints API Principales

```bash
# Telemetría en tiempo real
GET  /api/telemetry
POST /api/telemetry/update

# Control del sistema
POST /api/control/throttle/{value}
POST /api/control/brake/{value}
POST /api/control/reverser/{value}

# Estado del sistema
GET  /api/status
GET  /api/metrics
```

## 🚨 Troubleshooting Rápido

### Problemas Comunes

#### 1. Dashboard no carga

```bash
# Verificar servidor Flask
netstat -ano | findstr :5001

# Reiniciar servicios
./start.bat
```

#### 2. No hay datos de TSC

```bash
# Verificar archivo GetData.txt
type "C:\Program Files (x86)\Steam\steamapps\common\RailWorks\plugins\GetData.txt"

# Verificar Raildriver ejecutándose
tasklist | findstr Raildriver
```

#### 3. Tests fallan

```bash
# Limpiar cache de tests
pytest --cache-clear

# Ejecutar tests específicos
pytest tests/unit/test_tsc_integration.py -v
```

### Logs Importantes

- **Aplicación**: `logs/autopilot.log`
- **Dashboard**: `logs/dashboard.log`
- **Tests**: `htmlcov/index.html`

## 🔄 Workflows de Desarrollo

### 1. Nueva Funcionalidad

1. Crear rama: `git checkout -b feature/nueva-funcionalidad`
2. Implementar código
3. Añadir tests: `pytest tests/unit/test_nueva_funcionalidad.py`
4. Actualizar documentación
5. Commit: `git commit -m "feat: nueva funcionalidad"`
6. PR y merge

### 2. Bug Fix

1. Crear rama: `git checkout -b fix/nombre-del-bug`
2. Reproducir bug
3. Implementar fix
4. Añadir test de regresión
5. Commit: `git commit -m "fix: descripción del fix"`
6. PR y merge

### 3. Actualizar Diagramas

```bash
# Después de cambios en arquitectura
python architecture_diagram.py
git add architecture_diagram*.png
git commit -m "docs: actualizar diagramas de arquitectura"
```

## 📞 Soporte

- **📖 Documentación**: [docs/indice-documentacion.md](indice-documentacion.md)
- **🐛 Issues**: Crear issue en GitHub con logs
- **💬 Comunidad**: [Discord/Slack del proyecto]
- **📧 Email**: [contacto@proyecto.com]

---

**🚀 Última actualización**: Diciembre 2025 **📊 Versión**: 2.0.0 **✅ Estado**:
Completado y documentado</content> parameter name="filePath">c:\Users\doski\Trai
nSimulatorAutopilot\docs\GUIA_DESARROLLADOR.md
