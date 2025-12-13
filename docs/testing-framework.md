# 🧪 Framework de Testing - Train Simulator Autopilot

## Documentación completa del sistema de testing para el proyecto Train

Simulator Autopilot

## 📋 Resumen Ejecutivo

El framework de testing del Train Simulator Autopilot está diseñado para
garantizar la calidad, fiabilidad y robustez del sistema de piloto automático
inteligente. Utiliza **pytest** como framework principal con cobertura completa
de testing unitario, integración y end-to-end.

## 🏗️ Arquitectura del Framework

### Estructura de Tests

```text
tests/
├── unit/                    # Tests unitarios
│   ├── test_tsc_integration.py
│   └── test_predictive_telemetry.py
├── integration/            # Tests de integración
│   └── test_integration.py
├── e2e/                    # Tests end-to-end
│   └── test_e2e_scenarios.py
└── __init__.py
```

### Configuración pytest

**Archivo: `pytest.ini`**

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=.
    --cov-report=term-missing
    --cov-report=html:htmlcov
markers =
    unit: Tests unitarios (marcados automáticamente)
    integration: Tests de integración entre componentes
    e2e: Tests end-to-end completos
    slow: Tests que requieren tiempo prolongado
    skip_ci: Tests a omitir en CI/CD
norecursedirs = scripts backup_* .*
```

## 📊 Cobertura de Tests

### Resumen Ejecutivo

| Categoría       | Cantidad     | Estado             | Cobertura | |
--------------- | ------------ | ------------------ | --------- | |
**Unitarios**   | 14 tests     | ✅ Completo        | 85%+      | |
**Integración** | 5 tests      | ✅ Completo        | 90%+      | | **End-to-
End**  | 4 tests      | ✅ Completo        | 95%+      | | **Total**       | **23
tests** | **100% Funcional** | **87%**   |

### Tests Unitarios (`tests/unit/`)

#### `test_tsc_integration.py`

**Propósito**: Validar la integración individual con Train Simulator Classic

**Tests incluidos:**

- `test_initialization` - Inicialización correcta del sistema
- `test_data_reading` - Lectura de datos de telemetría
- `test_command_sending` - Envío de comandos al simulador
- `test_error_handling` - Manejo de errores de conexión
- `test_multi_locomotive_support` - Soporte multi-locomotora
- `test_connection_state_management` - Gestión de estados de conexión
- `test_data_validation` - Validación de datos entrantes

**Marcadores**: `unit`

#### `test_predictive_telemetry.py`

**Propósito**: Validar el análisis predictivo de telemetría

**Tests incluidos:**

- `test_model_initialization` - Inicialización del modelo predictivo
- `test_data_processing` - Procesamiento de datos de telemetría
- `test_prediction_accuracy` - Precisión de predicciones
- `test_anomaly_detection` - Detección de anomalías
- `test_performance_metrics` - Métricas de rendimiento
- `test_real_time_processing` - Procesamiento en tiempo real
- `test_model_persistence` - Persistencia del modelo

**Marcadores**: `unit`, `slow`

### Tests de Integración (`tests/integration/`)

#### `test_integration.py`

**Propósito**: Validar la interacción entre componentes del sistema

**Tests incluidos:**

1. **`test_tsc_data_flow`**
   - **Objetivo**: Verificar flujo completo de datos TSC
   - **Escenario**: Lectura → Procesamiento → Almacenamiento
   - **Validaciones**: Integridad de datos, timestamps, formato

2. **`test_command_execution_integration`**
   - **Objetivo**: Validar ejecución de comandos entre componentes
   - **Escenario**: Comando IA → TSC Integration → Simulador
   - **Validaciones**: Ejecución correcta, feedback, error handling

3. **`test_predictive_feedback_loop`**
   - **Objetivo**: Validar bucle de retroalimentación predictiva
   - **Escenario**: Datos → Predicción → Acción → Resultado
   - **Validaciones**: Consistencia, timing, accuracy

4. **`test_error_handling_integration`**
   - **Objetivo**: Probar manejo de errores entre componentes
   - **Escenario**: Error en un componente → Propagación → Recuperación
   - **Validaciones**: Logging, recovery, system stability

5. **`test_performance_integration`**
   - **Objetivo**: Validar rendimiento del sistema integrado
   - **Escenario**: Carga alta, múltiples locomotoras, predicciones continuas
   - **Validaciones**: Latencia, throughput, resource usage

**Marcadores**: `integration`, `slow`

### Tests End-to-End (`tests/e2e/`)

#### `test_e2e_scenarios.py`

**Propósito**: Validar escenarios completos de uso del sistema

**Tests incluidos:**

1. **`test_complete_driving_scenario`**
   - **Objetivo**: Simular conducción completa con piloto automático
   - **Escenario**: Inicio → Aceleración → Mantenimiento velocidad → Parada
   - **Validaciones**: Comandos correctos, timing, safety

2. **`test_emergency_stop_scenario`**
   - **Objetivo**: Validar respuesta a situaciones de emergencia
   - **Escenario**: Condición crítica → Stop inmediato → Recovery
   - **Validaciones**: Response time, safety protocols, logging

3. **`test_energy_efficiency_optimization`**
   - **Objetivo**: Optimizar eficiencia energética (sin gestión de combustible)
   - **Escenario**: Análisis predictivo → Ajustes → Mejora efficiency
   - **Validaciones**: Reducción consumo energía, mantenimiento performance

4. **`test_system_recovery_after_failure`**
   - **Objetivo**: Validar recuperación tras fallos del sistema
   - **Escenario**: Failure → Detection → Recovery → Normal operation
   - **Validaciones**: Downtime mínimo, data integrity, system state

**Marcadores**: `e2e`, `slow`, `skip_ci`

## 🚀 Ejecución de Tests

### Comandos Básicos

```bash
# Ejecutar todos los tests
python -m pytest

# Tests unitarios únicamente
python -m pytest tests/unit/

# Tests de integración
python -m pytest tests/integration/

# Tests end-to-end
python -m pytest tests/e2e/

# Con reporte de cobertura detallado
python -m pytest --cov=. --cov-report=html
```

### Ejecución Selectiva

```bash
# Tests por marcador
python -m pytest -m "unit and not slow"    # Unitarios rápidos
python -m pytest -m integration           # Solo integración
python -m pytest -m e2e                   # Solo end-to-end

# Tests específicos
python -m pytest tests/unit/test_tsc_integration.py::TestTSCIntegration::test_initialization
python -m pytest tests/integration/test_integration.py -v

# Tests con salida verbosa
python -m pytest -v --tb=short
```

### Configuración de Entorno

```bash
# Instalar dependencias de testing
pip install pytest pytest-cov pytest-mock

# Limpiar cache de tests
python -m pytest --cache-clear

# Ver configuración
python -m pytest --collect-only --quiet
```

## 📈 Reportes de Cobertura

### Generación de Reportes

```bash
# Reporte en terminal
python -m pytest --cov=. --cov-report=term

# Reporte HTML
python -m pytest --cov=. --cov-report=html

# Reporte XML (para CI/CD)
python -m pytest --cov=. --cov-report=xml
```

### Interpretación de Cobertura

- **Líneas ejecutadas**: Código efectivamente probado
- **Ramas (branches)**: Caminos condicionales probados
- **Funciones**: Funciones con al menos una ejecución
- **Clases**: Clases instanciadas durante tests

### Umbrales de Calidad

- **Cobertura total**: ≥ 80%
- **Cobertura de funciones críticas**: ≥ 90%
- **Cobertura de nuevos features**: ≥ 85%
- **Ramas condicionales**: ≥ 75%

## 🛠️ Herramientas y Utilidades

### Mocks y Fixtures

```python
import pytest
from unittest.mock import Mock, patch
from tests.fixtures import mock_tsc_data, mock_telemetry_stream

@pytest.fixture
def tsc_integration_mock():
    """Fixture para mock de TSC Integration"""
    with patch('tsc_integration.TSCIntegration') as mock:
        mock.return_value.obtener_datos_telemetria.return_value = mock_tsc_data()
        yield mock

@pytest.fixture
def telemetry_analyzer_mock():
    """Fixture para mock de Predictive Telemetry Analyzer"""
    with patch('predictive_telemetry_analysis.PredictiveTelemetryAnalyzer') as mock:
        yield mock
```

### Helpers de Testing

```python
def assert_telemetry_data_valid(data):
    """Valida estructura de datos de telemetría"""
    required_fields = ['speed', 'acceleration', 'brake_pressure', 'throttle']
    for field in required_fields:
        assert field in data, f"Campo requerido faltante: {field}"
        assert isinstance(data[field], (int, float)), f"Tipo incorrecto para {field}"

def simulate_tsc_response(delay=0.1):
    """Simula respuesta del TSC con delay configurable"""
    import time
    time.sleep(delay)
    return {"status": "success", "data": mock_tsc_data()}
```

## 🔧 Configuración Avanzada

### pytest.ini - Configuración Completa

```ini
[tool:pytest]
# Rutas de búsqueda
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Opciones por defecto
addopts =
    --strict-markers
    --strict-config
    --disable-warnings
    --tb=short
    -ra

# Marcadores personalizados
markers =
    unit: Tests unitarios básicos
    integration: Tests de integración entre componentes
    e2e: Tests end-to-end completos
    slow: Tests que requieren tiempo prolongado (>30s)
    skip_ci: Tests a omitir en entorno CI/CD
    smoke: Tests de humo para validación rápida

# Exclusiones
norecursedirs =
    .git
    __pycache__
    .pytest_cache
    scripts
    backup_*
    .*

# Cobertura
[coverage:run]
source = .
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    setup.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

### Configuración CI/CD

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: python -m pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## 📊 Métricas y KPIs

### Métricas de Calidad

- **Tasa de éxito de tests**: ≥ 99%
- **Tiempo de ejecución**: < 5 minutos para suite completa
- **Cobertura de código**: ≥ 85%
- **Densidad de defects**: < 0.1 por 1000 líneas

### Métricas de Rendimiento

- **Tests unitarios**: < 30 segundos
- **Tests integración**: < 2 minutos
- **Tests E2E**: < 3 minutos
- **Memoria máxima**: < 500MB durante ejecución

### Alertas y Monitoreo

- **Fallas consecutivas**: > 3 → Alerta inmediata
- **Cobertura decreciente**: > 5% → Revisión requerida
- **Tiempo ejecución**: > 150% baseline → Investigación

## 🐛 Debugging y Troubleshooting

### Problemas Comunes

#### Tests que fallan intermitentemente

```bash
# Ejecutar con más verbosidad
python -m pytest -v -s --tb=long

# Ejecutar múltiples veces para verificar flake
python -m pytest --count=5 --maxfail=1
```

#### Problemas de cobertura

```bash
# Ver líneas no cubiertas
python -m pytest --cov=. --cov-report=term-missing

# Excluir archivos específicos
python -m pytest --cov=. --cov-report=html --cov-config=.coveragerc
```

#### Tests lentos

```bash
# Identificar tests lentos
python -m pytest --durations=10

# Ejecutar solo tests rápidos
python -m pytest -m "not slow"
```

### Logs y Debugging

```python
import logging

# Configurar logging para tests
@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='test_debug.log'
    )
```

## 📚 Mejores Prácticas

### Estructura Recomendada de Tests

```python
class TestFeature:
    """Tests para feature específica"""

    def setup_method(self):
        """Setup antes de cada test"""
        self.system = SystemUnderTest()

    def teardown_method(self):
        """Cleanup después de cada test"""
        self.system.cleanup()

    def test_feature_normal_case(self):
        """Test caso normal"""
        # Given
        input_data = valid_input()

        # When
        result = self.system.process(input_data)

        # Then
        assert result.is_success()
        assert_telemetry_data_valid(result.data)

    def test_feature_edge_case(self):
        """Test caso borde"""
        # Given
        edge_input = edge_case_input()

        # When/Then
        with pytest.raises(ExpectedException):
            self.system.process(edge_input)
```

### Mocks y Stubs

```python
from unittest.mock import Mock, MagicMock

def test_with_mocks():
    """Ejemplo de test con mocks"""
    # Crear mocks
    tsc_mock = Mock()
    tsc_mock.obtener_datos_telemetria.return_value = mock_data()

    analyzer_mock = MagicMock()
    analyzer_mock.get_predictions.return_value = mock_predictions()

    # Inyectar mocks
    system = AutopilotSystem(tsc_mock, analyzer_mock)

    # Ejecutar test
    result = system.make_decision()

    # Verificar interacciones
    tsc_mock.obtener_datos_telemetria.assert_called_once()
    analyzer_mock.get_predictions.assert_called_once()

    # Verificar resultado
    assert result.action == "accelerate"
```

## 🔄 Mantenimiento del Framework

### Actualización de Tests

1. **Revisar cobertura** después de cambios en código
2. **Actualizar mocks** cuando cambie la API
3. **Agregar tests** para nueva funcionalidad
4. **Refactorizar tests** cuando el código cambie significativamente

### Limpieza Periódica

```bash
# Limpiar cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -rf .pytest_cache/
rm -rf htmlcov/

# Verificar estructura
python -m pytest --collect-only
```

### Actualización de Dependencias

```bash
# Actualizar pytest y plugins
pip install --upgrade pytest pytest-cov pytest-mock

# Verificar compatibilidad
python -m pytest --version
```

## 📞 Soporte y Contacto

### Reportar Issues

- **Tests que fallan**: Crear issue con logs completos
- **Cobertura insuficiente**: Revisar y agregar tests faltantes
- **Performance issues**: Profile y optimizar tests lentos

### Documentación Relacionada

- `docs/integration.md` - Guía de integración del sistema
- `docs/ia-spec.md` - Especificaciones de IA
- `README.md` - Documentación general del proyecto

---

🧪 Framework de testing completo y validado para garantizar la calidad del Train
Simulator Autopilot
