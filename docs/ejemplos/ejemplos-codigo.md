# 💻 Ejemplos de Código - Train Simulator Autopilot

## Ejemplos de Scripts Lua para Locomotoras

### Script Avanzado de Piloto Automático (Actualizado 02/12/2025)

```lua
-- complete_autopilot_lua.lua - Script completo de piloto automático
-- Sistema avanzado con IA predictiva, control multi-estado y telemetría completa

-- Variables globales optimizadas
gData = ""
autopilotActive = false
predictiveActive = false
doorsAutoMode = false  -- Disabled in examples: door control handled by AI in future
lastSpeed = 0
lastAcceleration = 0
speedHistory = {}
accelerationHistory = {}

-- Umbrales de seguridad mejorados
alertThresholds = {
    speed = 80,      -- km/h
    acceleration = 2.0,  -- m/s²
    brakePressure = 3.0,  -- bar
    wheelslip = 0.1,     -- deslizamiento
    fuel = 0.15,         -- 15% combustible
    rpm = 2000,          -- RPM alto
    current = 1000       -- corriente alta (amperios)
}

-- Mapeo de controles optimizado
controlMappings = {
    ["acelerador"] = "VirtualThrottle",
    ["freno_tren"] = "TrainBrakeControl",
    ["freno_motor"] = "EngineBrakeControl",
    ["freno_dinamico"] = "VirtualEngineBrakeControl",
    ["reverser"] = "VirtualReverser",
    -- Door control removed from examples: AI will manage doors in future
    ["luces"] = "LightSwitch",
    ["freno_emergencia"] = "BrakeControl"
}

-- Inicialización mejorada
function Initialise()
    -- Door initialization removed in examples
    SysCall("PlayerEngineSetControlValue", "LightSwitch", 0, 0)
    SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0, 0)
    SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0)

    -- Inicializar arrays de historia
    for i = 1, 10 do
        speedHistory[i] = 0
        accelerationHistory[i] = 0
    end

    SysCall("ScenarioManager:ShowMessage", "🚂 Train Simulator Autopilot v3.0 - Inicializado", 5, 1)
end

-- Loop principal optimizado
function Update(time)
    if Call("GetIsEngineWithKey") == 1 then
        updateTelemetry()
        getdata()  -- Escritura de telemetría para Python

        if autopilotActive then
            handleAutopilot()
        end

        if predictiveActive then
            handlePredictiveAnalysis()
        end

        -- Door automation disabled in examples

        checkAlerts()
    end
end

-- Control de piloto automático inteligente
function handleAutopilot()
    local currentSpeed = lastSpeed
    local targetSpeed = 60  -- km/h configurable
    local speedLimit = Call("GetCurrentSpeedLimit") * 3.6

    -- Lógica de control PID-like mejorada
    if currentSpeed < targetSpeed - 2 then
        local throttleValue = math.min((targetSpeed - currentSpeed) / 20, 1.0)
        SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0, throttleValue)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0)
    elseif currentSpeed > targetSpeed + 2 then
        local brakeValue = math.min((currentSpeed - targetSpeed) / 30, 1.0)
        SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0, 0)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, brakeValue)
    else
        -- Modo de crucero optimizado
        SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0, 0.1)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0)
    end

    -- Compensación de gradiente inteligente
    local gradient = Call("GetGradient")
    if gradient > 0.01 then  -- Subida
        local compensation = gradient * 0.5
        local currentThrottle = Call("GetControlValue", "VirtualThrottle", 0)
        SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0,
                math.min(currentThrottle + compensation, 1.0))
    elseif gradient < -0.01 then  -- Bajada
        local compensation = math.abs(gradient) * 0.3
        local currentBrake = Call("GetControlValue", "TrainBrakeControl", 0)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0,
                math.min(currentBrake + compensation, 1.0))
    end
end

-- Análisis predictivo avanzado
function handlePredictiveAnalysis()
    local currentSpeed = lastSpeed
    local nextLimit, nextDistance = Call("GetNextSpeedLimit", 0)

    if nextLimit and nextDistance then
        nextLimit = nextLimit * 3.6  -- Convertir a km/h
        nextDistance = nextDistance  -- metros

        -- Cálculo de distancia de frenado con física real
        local speedDiff = currentSpeed - nextLimit
        local stoppingDistance = (currentSpeed * currentSpeed) / (2 * 1.5)  -- v²/2a

        if nextDistance < stoppingDistance and speedDiff > 5 then
            local brakeIntensity = math.min(speedDiff / 20, 1.0)
            SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, brakeIntensity)
            SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0, 0)

            if brakeIntensity > 0.3 then
                SysCall("ScenarioManager:ShowMessage", "🛑 Frenado predictivo activado", 3, 2)
            end
        end
    end
end

-- Sistema de alertas inteligente
function checkAlerts()
    local currentSpeed = lastSpeed
    local currentAcceleration = lastAcceleration

    -- Alertas críticas con niveles de severidad
    if currentSpeed > alertThresholds.speed then
        SysCall("ScenarioManager:ShowMessage",
                string.format("🚨 ALERTA VELOCIDAD: %.1f km/h", currentSpeed), 5, 3)
    end

    if math.abs(currentAcceleration) > alertThresholds.acceleration then
        SysCall("ScenarioManager:ShowMessage",
                string.format("⚠️ ALERTA ACELERACIÓN: %.2f m/s²", currentAcceleration), 5, 3)
    end

    -- Monitoreo de sistemas de freno
    local brakePipePressure = Call("GetControlValue", "AirBrakePipePressurePSI", 0) or 0
    if brakePipePressure < alertThresholds.brakePressure then
        SysCall("ScenarioManager:ShowMessage",
                string.format("🔴 PRESIÓN BAJA TUBO FRENO: %.1f PSI", brakePipePressure), 5, 3)
    end

    -- Alertas de seguridad adicionales
    local wheelslip = Call("GetControlValue", "Wheelslip", 0) or 0
    if wheelslip > alertThresholds.wheelslip then
        SysCall("ScenarioManager:ShowMessage",
                string.format("⚠️ DESLIZAMIENTO RUEDAS: %.2f", wheelslip), 3, 2)
    end

    -- FuelLevel removed for TSC (infinite fuel). Example kept for reference only.
    -- local fuelLevel = Call("GetFuelLevel") or 1.0
    -- if fuelLevel < alertThresholds.fuel then
    --     SysCall("ScenarioManager:ShowMessage",
    --             string.format("⛽ COMBUSTIBLE BAJO: %.1f%%", fuelLevel * 100), 5, 3)
    -- end
end

-- Funciones de control externas (llamadas desde Python)
function SetAutopilotState(state)
    autopilotActive = state
    if state then
        SysCall("ScenarioManager:ShowMessage", "🤖 PILOTO AUTOMÁTICO ACTIVADO", 5, 1)
    else
        SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0, 0)
        SysCall("PlayerEngineSetControlValue", "TrainBrakeControl", 0, 0)
        SysCall("ScenarioManager:ShowMessage", "🛑 PILOTO AUTOMÁTICO DESACTIVADO", 5, 2)
    end
end

function SetPredictiveState(state)
    predictiveActive = state
    local msg = state and "ANÁLISIS PREDICTIVO ACTIVO" or "ANÁLISIS PREDICTIVO INACTIVO"
    SysCall("ScenarioManager:ShowMessage", msg, 5, 1)
end

function EmergencyBrake()
    SysCall("PlayerEngineSetControlValue", "BrakeControl", 0, 1)
    SysCall("PlayerEngineSetControlValue", "VirtualThrottle", 0, 0)
    autopilotActive = false
    predictiveActive = false
    SysCall("ScenarioManager:ShowMessage", "🚨 ¡FRENO DE EMERGENCIA!", 10, 3)
end

-- Función de telemetría completa para integración Python
function GetTelemetryData()
    return {
        speed = lastSpeed,
        acceleration = lastAcceleration,
        throttle = Call("GetControlValue", "VirtualThrottle", 0),
        brake = Call("GetControlValue", "TrainBrakeControl", 0),
        gradient = Call("GetGradient()),
        autopilot = autopilotActive,
        predictive = predictiveActive,
        doors = Call("GetControlValue", "DoorSwitch", 0),
        lights = Call("GetControlValue", "LightSwitch", 0),
        rpm = Call("GetControlValue", "RPM", 0) or 0,
        ammeter = Call("GetControlValue", "Ammeter", 0) or 0,
        tractiveEffort = Call("GetControlValue", "TractiveEffort", 0) or 0,
        -- fuelLevel = Call("GetFuelLevel") or 1.0, -- Removed for TSC (infinite fuel)
        brakePipePressure = Call("GetControlValue", "AirBrakePipePressurePSI", 0) or 0,
        locoBrakeCylinderPressure = Call("GetControlValue", "LocoBrakeCylinderPressurePSI", 0) or 0,
        trainBrakeCylinderPressure = Call("GetControlValue", "TrainBrakeCylinderPressurePSI", 0) or 0,
        wheelslip = Call("GetControlValue", "Wheelslip", 0) or 0,
        currentSpeedLimit = Call("GetCurrentSpeedLimit") or 0,
        nextSpeedLimit = Call("GetNextSpeedLimit") or 0,
        nextSpeedLimitDistance = Call("GetNextSpeedLimitDistance") or 0,
        signalAspect = Call("GetControlValue", "SignalAspect", 0) or 0,
        distanceTravelled = Call("GetControlValue", "DistanceTravelled", 0) or 0,
        simulationTime = Call("GetSimulationTime") or 0,
        systemHealthy = true,
        timestamp = os.time()
    }
end

-- Escritura de datos de telemetría para Python (formato RailDriver)
function getdata()
    gData = string.format(
        "ControlName:CurrentSpeed\nControlValue:%.2f\n" ..
        "ControlName:Acceleration\nControlValue:%.2f\n" ..
        "ControlName:VirtualThrottle\nControlValue:%.2f\n" ..
        "ControlName:TrainBrakeControl\nControlValue:%.2f\n" ..
        "ControlName:Gradient\nControlValue:%.2f\n" ..
        "ControlName:AutopilotActive\nControlValue:%d\n" ..
        "ControlName:PredictiveActive\nControlValue:%d\n" ..
        "ControlName:DistanceTravelled\nControlValue:%.2f\n" ..
        "ControlName:SimulationTime\nControlValue:%.2f\n" ..
        "ControlName:TractiveEffort\nControlValue:%.2f\n" ..
        "ControlName:RPM\nControlValue:%.2f\n" ..
        "ControlName:Ammeter\nControlValue:%.2f\n" ..
        "ControlName:Wheelslip\nControlValue:%.2f\n" ..
        "ControlName:AirBrakePipePressurePSI\nControlValue:%.2f\n" ..
        "ControlName:LocoBrakeCylinderPressurePSI\nControlValue:%.2f\n" ..
        "ControlName:TrainBrakeCylinderPressurePSI\nControlValue:%.2f\n" ..
        "ControlName:EqReservoirPressurePSIAdvanced\nControlValue:%.2f\n" ..
        "ControlName:MainReservoirPressurePSIDisplayed\nControlValue:%.2f\n" ..
        "ControlName:AuxReservoirPressure\nControlValue:%.2f\n" ..
        "ControlName:BrakePipePressureTailEnd\nControlValue:%.2f\n" ..
        "ControlName:LocoBrakeCylinderPressurePSIDisplayed\nControlValue:%.2f\n" ..
        "ControlName:FuelLevel\nControlValue:%.2f\n" ..
        "ControlName:CurrentSpeedLimit\nControlValue:%.2f\n" ..
        "ControlName:NextSpeedLimitSpeed\nControlValue:%.2f\n" ..
        "ControlName:NextSpeedLimitDistance\nControlValue:%.2f\n" ..
        "ControlName:SignalAspect\nControlValue:%.2f\n",
        lastSpeed / 3.6,  -- Convertir a m/s para RailDriver
        lastAcceleration,
        Call("GetControlValue", "VirtualThrottle", 0),
        Call("GetControlValue", "TrainBrakeControl", 0),
        Call("GetGradient()),
        autopilotActive and 1 or 0,
        predictiveActive and 1 or 0,
        Call("GetControlValue", "DistanceTravelled", 0) or 0,
        Call("GetSimulationTime") or 0,
        Call("GetControlValue", "TractiveEffort", 0) or 0,
        Call("GetControlValue", "RPM", 0) or 0,
        Call("GetControlValue", "Ammeter", 0) or 0,
        Call("GetControlValue", "Wheelslip", 0) or 0,
        Call("GetControlValue", "AirBrakePipePressurePSI", 0) or 0,
        Call("GetControlValue", "LocoBrakeCylinderPressurePSI", 0) or 0,
        Call("GetControlValue", "TrainBrakeCylinderPressurePSI", 0) or 0,
        Call("GetControlValue", "EqReservoirPressurePSIAdvanced", 0) or 0,
        Call("GetControlValue", "MainReservoirPressurePSIDisplayed", 0) or 0,
        Call("GetControlValue", "AuxReservoirPressure", 0) or 0,
        Call("GetControlValue", "BrakePipePressureTailEnd", 0) or 0,
        Call("GetControlValue", "LocoBrakeCylinderPressurePSIDisplayed", 0) or 0,
        -- Call("GetFuelLevel") or 0, -- Removed for TSC (infinite fuel)
        Call("GetCurrentSpeedLimit") or 0,
        Call("GetNextSpeedLimit") or 0,
        Call("GetNextSpeedLimitDistance") or 0,
        Call("GetControlValue", "SignalAspect", 0) or 0
    )

    local file = io.open("plugins/GetData.txt", "w")
    if file then
        file:write(gData)
        file:close()
    end
end
```

### Script de Control de Puertas Inteligente

```lua
-- doors_control.lua - Control automático inteligente de puertas
local doorsState = 0  -- 0 = closed, 1 = open
local lastStationStop = 0
local boardingTime = 30  -- segundos para embarque/desembarque

function handleAutomaticDoors()
    local currentSpeed = Call("GetSpeed") * 3.6  -- km/h
    local currentTime = Call("GetSimulationTime")

    -- Lógica inteligente de puertas
    if currentSpeed > 10 then
        -- Tren en movimiento - asegurar puertas cerradas
        if doorsState ~= 0 then
            SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 0)
            doorsState = 0
            SysCall("ScenarioManager:ShowMessage", "🔒 Puertas cerradas (movimiento)", 3, 1)
        end
    elseif currentSpeed < 2 then
        -- Tren detenido - verificar si es parada de estación
        local distanceTravelled = Call("GetControlValue", "DistanceTravelled", 0) or 0

        if (currentTime - lastStationStop) > boardingTime then
            -- Tiempo suficiente desde última parada - abrir puertas
            if doorsState ~= 1 then
                SysCall("PlayerEngineSetControlValue", "DoorSwitch", 0, 1)
                doorsState = 1
                lastStationStop = currentTime
                SysCall("ScenarioManager:ShowMessage", "🚪 Puertas abiertas (embarque)", 3, 1)

                -- Programar cierre automático
                -- (En implementación real usaría timer)
            end
        end
    end
end
```

## Ejemplos de Correcciones de Linting (2025-12-02)

### Corrección de Importaciones en Python

**❌ Código con errores de linting:**

```python
# test_autopilot.py - ANTES (con errores)
datos_simulados = {
    "CurrentSpeed": 15.5,
    "DistanceTravelled": 1250.75,
    "SignalAspect": 2,
    "RPM": 850.0,
    "CurrentSpeedLimit": 60
}

print("🚂 PRUEBA SISTEMA AUTOPILOT")
for k, v in datos_simulados.items():
    print(f"  {k}: {v}")

from autopilot_system import AutopilotSystem, IASistema  # ❌ Import después de código (E402)
from tsc_integration import TSCIntegration            # ❌ Import después de código (E402)

# Código que usa AutopilotSystem... ❌ Import no utilizado (F401)
```

**✅ Código corregido:**

```python
# test_autopilot.py - DESPUÉS (sin errores)
from autopilot_system import IASistema          # ✅ Import al inicio
from tsc_integration import TSCIntegration      # ✅ Import al inicio
# ❌ Eliminada importación no utilizada: AutopilotSystem

datos_simulados = {
    "CurrentSpeed": 15.5,
    "DistanceTravelled": 1250.75,
    "SignalAspect": 2,
    "RPM": 850.0,
    "CurrentSpeedLimit": 60
}

print("🚂 PRUEBA SISTEMA AUTOPILOT")
for k, v in datos_simulados.items():
    print(f"  {k}: {v}")

# ✅ Código limpio y sin errores de linting
```

### Corrección de Espacios en Blanco

**❌ Código con líneas en blanco con espacios (W293):**

```python
def test_conversion() -> Optional[Dict[str, Any]]:
    ruta_prueba = r"c:\Users\doski\TrainSimulatorAutopilot\test_data.txt"
    tsc = TSCIntegration(ruta_archivo=ruta_prueba)

    print("Probando conversión de datos TSC...")

    # ❌ Línea 24: contiene espacios en blanco
    if datos is None:
        # ❌ Línea 28: contiene espacios en blanco

    print("\nDatos convertidos para IA:")
```

**✅ Código corregido:**

```python
def test_conversion() -> Optional[Dict[str, Any]]:
    ruta_prueba = r"c:\Users\doski\TrainSimulatorAutopilot\test_data.txt"
    tsc = TSCIntegration(ruta_archivo=ruta_prueba)

    print("Probando conversión de datos TSC...")

    # ✅ Líneas completamente vacías (sin espacios)
    if datos is None:

    # ✅ Código limpio y sin espacios residuales
    print("\nDatos convertidos para IA:")
```

### Corrección de Importaciones No Utilizadas

**❌ Código con imports innecesarios:**

```python
# verificar_datos_reales.py - ANTES
import json      # ❌ No se utiliza en el código
import time      # ❌ No se utiliza en el código
import requests  # ✅ Se utiliza

def verificar_datos_frenos():
    response = requests.get('http://localhost:5000/status', timeout=5)
    # ... resto del código sin usar json ni time
```

**✅ Código corregido:**

```python
# verificar_datos_reales.py - DESPUÉS
import requests  # ✅ Solo imports utilizados

def verificar_datos_frenos():
    response = requests.get('http://localhost:5000/status', timeout=5)
    # ✅ Código más eficiente y limpio
```

### Corrección de Modos Redundantes en open()

**❌ Código con modo redundante:**

```python
# verificar_datos_reales.py - ANTES
def verificar_archivo_getdata():
    try:
        with open('GetData.txt', 'r', encoding='utf-8') as f:  # ❌ 'r' es redundante
            contenido = f.read()
```

**✅ Código corregido:**

```python
# verificar_datos_reales.py - DESPUÉS
def verificar_archivo_getdata():
    try:
        with open('GetData.txt', encoding='utf-8') as f:  # ✅ Modo por defecto
            contenido = f.read()
```

## Ejemplos de Configuración Python

### Configuración de Entorno Virtual

**requirements.txt:**

```txt
# Dependencias principales
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=1.0.0
flask>=2.0.0
requests>=2.25.0

# Dependencias de desarrollo
pytest>=6.2.0
black>=21.0.0
flake8>=3.9.0
mypy>=0.910
bandit>=1.7.0

# Dependencias específicas del proyecto
bokeh>=2.4.0
psutil>=5.8.0
pyyaml>=5.4.0
```

**Configuración de entorno virtual:**

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import numpy, pandas, bokeh; print('✅ Todas las dependencias instaladas')"
```

### Configuración de Pylance/VS Code

**settings.json (espacio de trabajo):**

```json
{
  "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.linting.banditEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.indexing": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### Ejemplo de Configuración de Logging

**logging_config.py:**

```python
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

class AutopilotLogger:
    """Configuración centralizada de logging para el sistema de autopilot."""

    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file or "autopilot.log"

        # Crear directorio de logs si no existe
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configurar logger raíz
        self._setup_logger()

    def _setup_logger(self):
        """Configura el logger con formato y handlers apropiados."""

        # Formato detallado para desarrollo
        detailed_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Formato simple para producción
        simple_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # Logger raíz
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # Limpiar handlers existentes
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(simple_format)
        logger.addHandler(console_handler)

        # Handler para archivo (con rotación)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_format)
        logger.addHandler(file_handler)

        # Logger específico para el autopilot
        autopilot_logger = logging.getLogger('autopilot')
        autopilot_logger.setLevel(logging.DEBUG)

# Uso del logger
logger = AutopilotLogger(log_level="DEBUG").logger

def ejemplo_uso_logger():
    """Ejemplo de uso del sistema de logging."""
    logger.info("🚂 Sistema de autopilot iniciado")
    logger.debug("Configuración cargada desde config.ini")
    logger.warning("⚠️  Velocidad límite excedida temporalmente")
    logger.error("❌ Error de comunicación con TSC")
    logger.critical("🚨 SISTEMA DETENIDO - Error crítico detectado")

if __name__ == "__main__":
    ejemplo_uso_logger()
```

## Ejemplos de Pruebas Unitarias

### Pruebas para el Sistema de Autopilot

**tests/test_autopilot_system.py:**

```python
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from autopilot_system import AutopilotSystem, IASistema
from tsc_integration import TSCIntegration


class TestAutopilotSystem:
    """Pruebas unitarias para el sistema de autopilot."""

    @pytest.fixture
    def sample_telemetry(self) -> Dict[str, Any]:
        """Datos de telemetría de ejemplo para pruebas."""
        return {
            "CurrentSpeed": 45.5,
            "DistanceTravelled": 1250.75,
            "SignalAspect": 2,
            "RPM": 1200.0,
            "CurrentSpeedLimit": 60,
            "Gradient": 0.002,
            "BrakePressure": 0.0,
            "Throttle": 0.8
        }

    @pytest.fixture
    def temp_config_file(self):
        """Crear archivo de configuración temporal para pruebas."""
        config_data = {
            "autopilot": {
                "max_speed": 80,
                "safety_margin": 5,
                "brake_distance_factor": 1.2
            },
            "system": {
                "update_interval": 0.1,
                "log_level": "INFO"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f, indent=2)
            return f.name

    def test_initialization(self, temp_config_file):
        """Prueba la inicialización correcta del sistema."""
        system = AutopilotSystem(config_file=temp_config_file)

        assert system.max_speed == 80
        assert system.safety_margin == 5
        assert system.brake_distance_factor == 1.2
        assert system.is_active is False

    def test_speed_control_logic(self, sample_telemetry):
        """Prueba la lógica de control de velocidad."""
        system = AutopilotSystem()
        system.is_active = True
        system.target_speed = 50

        # Simular velocidad por debajo del objetivo
        low_speed_data = sample_telemetry.copy()
        low_speed_data["CurrentSpeed"] = 40.0

        action = system._calculate_speed_control(low_speed_data)

        assert action["Throttle"] > 0.5  # Debería acelerar
        assert action["BrakePressure"] == 0.0  # No frenar

    def test_emergency_braking(self, sample_telemetry):
        """Prueba el sistema de frenado de emergencia."""
        system = AutopilotSystem()
        system.is_active = True

        # Simular obstáculo cercano
        emergency_data = sample_telemetry.copy()
        emergency_data["SignalAspect"] = 0  # Señal roja
        emergency_data["CurrentSpeed"] = 55.0  # Velocidad alta

        action = system._calculate_emergency_action(emergency_data)

        assert action["BrakePressure"] > 0.7  # Frenado fuerte
        assert action["Throttle"] == 0.0  # Sin aceleración

    @patch('tsc_integration.TSCIntegration.read_telemetry')
    def test_integration_with_tsc(self, mock_read, sample_telemetry):
        """Prueba la integración con el sistema TSC."""
        mock_read.return_value = sample_telemetry

        tsc = TSCIntegration()
        system = AutopilotSystem()
        system.is_active = True

        # Ejecutar ciclo de control
        system.update_control()

        # Verificar que se leyó la telemetría
        mock_read.assert_called_once()

        # Verificar que se generó una acción de control
        assert system.last_action is not None

    def test_safety_limits(self):
        """Prueba los límites de seguridad del sistema."""
        system = AutopilotSystem()

        # Velocidad máxima segura
        assert system._is_speed_safe(75, 80) is True
        assert system._is_speed_safe(85, 80) is False

        # Gradiente seguro
        assert system._is_gradient_safe(0.005) is True
        assert system._is_gradient_safe(0.05) is False  # Muy empinado

    @pytest.mark.parametrize("speed,limit,expected", [
        (50, 60, True),   # Velocidad normal
        (65, 60, False),  # Exceso de velocidad
        (0, 60, True),    # Detenido
        (59, 60, True),   # Límite inferior
    ])
    def test_speed_limit_compliance(self, speed, limit, expected):
        """Prueba parametrizada del cumplimiento de límites de velocidad."""
        system = AutopilotSystem()
        assert system._is_speed_safe(speed, limit) == expected


class TestIASistema:
    """Pruebas para el sistema de IA."""

    def test_predictive_analysis(self):
        """Prueba el análisis predictivo."""
        ia = IASistema()

        # Datos históricos de velocidad
        historical_data = [40, 45, 50, 48, 52, 55]

        prediction = ia.predict_next_speed(historical_data)

        # La predicción debería estar en un rango razonable
        assert 45 <= prediction <= 65

    def test_anomaly_detection(self):
        """Prueba la detección de anomalías."""
        ia = IASistema()

        # Datos normales
        normal_data = {
            "CurrentSpeed": 50,
            "RPM": 1000,
            "BrakePressure": 0.1
        }

        # Datos anómalos
        anomalous_data = {
            "CurrentSpeed": 50,
            "RPM": 3000,  # RPM anormalmente alto
            "BrakePressure": 0.1
        }

        assert ia.detect_anomaly(normal_data) is False
        assert ia.detect_anomaly(anomalous_data) is True


# Pruebas de integración
class TestSystemIntegration:
    """Pruebas de integración entre componentes."""

    def test_full_autopilot_cycle(self, tmp_path):
        """Prueba un ciclo completo del autopilot."""
        # Crear archivos temporales
        telemetry_file = tmp_path / "GetData.txt"
        config_file = tmp_path / "config.ini"

        # Configurar telemetría simulada
        telemetry_data = {
            "CurrentSpeed": 45.0,
            "SignalAspect": 2,
            "CurrentSpeedLimit": 60
        }

        telemetry_file.write_text(json.dumps(telemetry_data))

        # Configurar sistema
        system = AutopilotSystem()
        tsc = TSCIntegration(str(telemetry_file))

        # Ejecutar ciclo
        telemetry = tsc.read_telemetry()
        action = system.process_telemetry(telemetry)

        # Verificaciones
        assert isinstance(action, dict)
        assert "Throttle" in action
        assert "BrakePressure" in action
        assert system.is_active is True
```

### Configuración de Pytest

**pytest.ini:**

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=autopilot_system
    --cov=tsc_integration
    --cov-report=html:htmlcov
    --cov-report=term-missing
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**Ejecución de pruebas:**

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=.

# Ejecutar pruebas específicas
pytest tests/test_autopilot_system.py::TestAutopilotSystem::test_speed_control_logic

# Ejecutar solo pruebas unitarias
pytest -m "unit"

# Ejecutar pruebas de integración
pytest -m "integration"
```

## Conclusión

Estos ejemplos demuestran las mejores prácticas implementadas en el proyecto
Train Simulator Autopilot:

- ✅ **Código Lua avanzado** con control predictivo y sistemas de seguridad
- ✅ **Integración Python-Lua** para dashboards en tiempo real
- ✅ **Correcciones de linting** para código limpio y mantenible
- ✅ **Configuración robusta** de entornos de desarrollo
- ✅ **Pruebas unitarias** exhaustivas con pytest
- ✅ **Logging estructurado** para monitoreo y debugging
- ✅ **Documentación actualizada** que refleja la implementación real

Todos los ejemplos están basados en el código real del proyecto y siguen las
convenciones actuales de desarrollo.

### Configuración de Telemetría Predictiva

```python
# predictive_telemetry_analysis.py - Análisis predictivo de telemetría
import numpy as np
from sklearn.linear_model import LinearRegression

class PredictiveTelemetryAnalyzer:
    def __init__(self):
        self.speed_history = []
        self.brake_history = []
        self.model = LinearRegression()

    def analyze_telemetry(self, current_speed, current_brake):
        # Almacenar datos históricos
        self.speed_history.append(current_speed)
        self.brake_history.append(current_brake)

        # Mantener solo los últimos 100 puntos
        if len(self.speed_history) > 100:
            self.speed_history.pop(0)
            self.brake_history.pop(0)

        # Predecir próxima velocidad
        if len(self.speed_history) >= 10:
            X = np.array(range(len(self.speed_history))).reshape(-1, 1)
            y = np.array(self.speed_history)
            self.model.fit(X, y)

            # Predicción para el siguiente punto
            next_prediction = self.model.predict([[len(self.speed_history)]])
            return next_prediction[0]

        return current_speed

# Uso del analizador
analyzer = PredictiveTelemetryAnalyzer()
predicted_speed = analyzer.analyze_telemetry(45.5, 0.2)
print(f"Velocidad predicha: {predicted_speed:.1f} mph")
```

### Configuración Multi-Locomotora

```python
# multi_locomotive_integration.py - Integración de múltiples locomotoras
class MultiLocomotiveController:
    def __init__(self):
        self.locomotives = {}
        self.lead_locomotive = None

    def add_locomotive(self, loco_id, config):
        self.locomotives[loco_id] = {
            'config': config,
            'status': 'idle',
            'speed': 0,
            'throttle': 0
        }

    def set_lead_locomotive(self, loco_id):
        if loco_id in self.locomotives:
            self.lead_locomotive = loco_id
            print(f"Locomotora líder establecida: {loco_id}")

    def synchronize_throttle(self, throttle_value):
        if not self.lead_locomotive:
            return

        # Aplicar throttle a todas las locomotoras
        for loco_id, loco_data in self.locomotives.items():
            loco_data['throttle'] = throttle_value
            # Aquí iría la lógica para enviar comandos a cada locomotora
            print(f"Aplicando throttle {throttle_value} a {loco_id}")

# Configuración de ejemplo
controller = MultiLocomotiveController()
controller.add_locomotive("SD70MAC_01", {"max_power": 4000, "weight": 200000})
controller.add_locomotive("SD70MAC_02", {"max_power": 4000, "weight": 200000})
controller.set_lead_locomotive("SD70MAC_01")
controller.synchronize_throttle(0.75)
```

## Ejemplos de Configuración JSON

### Configuración de Dashboard Web

```json
{
  "dashboard": {
    "title": "Train Simulator Autopilot Dashboard",
    "refresh_rate": 1000,
    "theme": "dark",
    "panels": [
      {
        "type": "gauge",
        "title": "Velocidad Actual",
        "data_source": "telemetry.speed",
        "unit": "mph",
        "min": 0,
        "max": 150,
        "thresholds": {
          "warning": 100,
          "danger": 120
        }
      },
      {
        "type": "chart",
        "title": "Historial de Velocidad",
        "data_source": "telemetry.speed_history",
        "time_window": 300,
        "update_interval": 5000
      },
      {
        "type": "controls",
        "title": "Controles Manuales",
        "controls": [
          {
            "name": "throttle",
            "type": "slider",
            "min": 0,
            "max": 1,
            "step": 0.01
          },
          {
            "name": "brake",
            "type": "slider",
            "min": 0,
            "max": 1,
            "step": 0.01
          }
        ]
      }
    ]
  }
}
```

### Configuración de Logging

```json
{
  "logging": {
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
      "detailed": {
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
      },
      "telemetry": {
        "format": "%(asctime)s - TELEMETRY - %(message)s",
        "datefmt": "%H:%M:%S"
      }
    },
    "handlers": {
      "file": {
        "class": "logging.FileHandler",
        "filename": "logs/autopilot.log",
        "formatter": "detailed",
        "level": "INFO"
      },
      "telemetry_file": {
        "class": "logging.FileHandler",
        "filename": "logs/telemetry.log",
        "formatter": "telemetry",
        "level": "DEBUG"
      },
      "console": {
        "class": "logging.StreamHandler",
        "formatter": "detailed",
        "level": "WARNING"
      }
    },
    "loggers": {
      "autopilot": {
        "handlers": ["file", "console"],
        "level": "INFO",
        "propagate": false
      },
      "telemetry": {
        "handlers": ["telemetry_file"],
        "level": "DEBUG",
        "propagate": false
      }
    }
  }
}
```

## Ejemplos de Configuración INI

### Configuración Principal del Sistema

```ini
[GENERAL]
system_name = Train Simulator Autopilot v2.0
debug_mode = false
log_level = INFO
max_speed_limit = 120

[TELEMETRY]
update_interval = 100
speed_unit = mph
distance_unit = meters
data_retention_days = 30

[HARDWARE]
raildriver_enabled = true
joystick_enabled = true
calibration_file = config/calibration.json

[AI]
prediction_enabled = true
adaptive_learning = true
safety_override = true
max_correction_angle = 5

[MULTI_LOCOMOTIVE]
enabled = false
max_locomotives = 4
sync_throttle = true
sync_brake = true

[WEB_DASHBOARD]
enabled = true
port = 8080
host = 0.0.0.0
auth_required = false
```

### Configuración de Escenarios

```ini
[SCENARIO_DEFAULT]
name = Default Route
difficulty = normal
ai_assistance = medium
speed_limits = strict
weather_effects = enabled

[SCENARIO_CHALLENGE]
name = Expert Mode
difficulty = hard
ai_assistance = low
speed_limits = strict
weather_effects = enabled
realism_mode = true

[SCENARIO_SANDBOX]
name = Free Play
difficulty = easy
ai_assistance = high
speed_limits = relaxed
weather_effects = disabled
unlimited_fuel = true
```
