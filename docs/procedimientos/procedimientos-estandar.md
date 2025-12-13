# 📋 Procedimientos Estándar - Train Simulator Autopilot

## 📋 Procedimientos Estándar Modernos (2025-12-02)

### Procedimiento Estándar: Inicio del Sistema Multi-Dashboard

#### 1. Verificación de Prerrequisitos

```bash
# Verificar Python 3.9+
python --version

# Verificar Node.js 18+
node --version
npm --version

# Verificar entorno virtual activado
python -m venv .venv
.venv\Scripts\activate  # Windows
```

#### 2. Inicio Automático Completo (Recomendado)

```bash
# Inicio completo del sistema
start.bat

# Verificar servicios iniciados:
# - Dashboard TypeScript: http://localhost:3000
# - Dashboard Flask: http://localhost:5001
# - Aplicación Electron: Ventana nativa
```

#### 3. Inicio Manual por Componentes

```bash
# Dashboard Principal TypeScript
cd dashboard
npm install
npm run build
npm start

# Dashboard Flask Secundario
python web_dashboard.py

# Aplicación Electron
start.bat       # Automático
start_dev.bat   # Desarrollo con DevTools
```

### Procedimiento Estándar: Configuración de Desarrollo

#### 1. Configuración del Entorno de Desarrollo

```bash
# Clonar repositorio
git clone <repository-url>
cd train-simulator-autopilot

# Configurar Python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Configurar TypeScript
cd dashboard
npm install
npm run build
```

#### 2. Verificación de Calidad de Código

```bash
# Linting Python
python -m flake8 . --max-line-length=88
python -m black . --check

# Linting TypeScript
cd dashboard
npm run lint

# Tests completos
python -m pytest --cov=. --cov-report=html
```

#### 3. Configuración de CI/CD Local

```bash
# Ejecutar pipeline local
python -m pytest
python -m flake8 . --max-line-length=88
python -m black . --check
markdownlint "docs/**/*.md"
cd dashboard && npm run build
```

### Procedimiento Estándar: Desarrollo con TypeScript

#### 1. Estructura del Dashboard TypeScript

```log
dashboard/
├── src/
│   ├── server.ts          # Servidor principal
│   ├── routes/
│   │   └── api.ts        # Endpoints REST
│   └── services/
│       └── SignalingDataService.ts
├── public/
│   └── index.html        # Interfaz web
├── package.json
└── tsconfig.json
```

#### 2. Desarrollo y Compilación

```bash
cd dashboard

# Desarrollo con hot reload
npm run dev

# Compilación de producción
npm run build

# Verificación de tipos
npm run type-check
```

#### 3. Agregar Nuevos Endpoints

```typescript
// En src/routes/api.ts
app.get('/api/system/:name', (req, res) => {
  const { name } = req.params;
  // Lógica del endpoint
  res.json({ system: name, status: 'active' });
});
```

### Procedimiento Estándar: Cliente WebSocket

#### 1. Configuración del Cliente

```python
# ws_client_test.py - Cliente corregido
import socketio

def on_telemetry(data):
    print(f"Telemetría: {data}")

sio = socketio.Client()
sio.on('telemetry', on_telemetry)

try:
    sio.connect('http://localhost:3000')
    sio.wait()
except KeyboardInterrupt:
    sio.disconnect()
```

#### 2. Manejo de Eventos WebSocket

```python
@sio.on('connect')
def on_connect():
    print("Conectado al dashboard")

@sio.on('disconnect')
def on_disconnect():
    print("Desconectado del dashboard")

@sio.on('telemetry')
def on_telemetry(data):
    # Procesar datos de telemetría
    speed = data.get('speed', 0)
    throttle = data.get('throttle', 0)
    # Lógica de procesamiento
```

### Procedimiento Estándar: Testing y Validación

#### 1. Tests Unitarios

```python
# tests/test_dashboard.py
import pytest
from web_dashboard import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_dashboard_status(client):
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
```

#### 2. Tests de Integración

```python
# tests/integration/test_websocket.py
def test_websocket_connection():
    # Test de conexión WebSocket
    sio = socketio.Client()
    connected = False

    @sio.on('connect')
    def on_connect():
        nonlocal connected
        connected = True

    sio.connect('http://localhost:3000')
    time.sleep(1)
    assert connected
    sio.disconnect()
```

#### 3. Tests End-to-End

```python
# tests/e2e/test_full_system.py
def test_full_system_integration():
    # Iniciar servicios
    # Verificar dashboards
    # Probar WebSocket
    # Validar telemetría
    pass
```

### Procedimiento Estándar: Monitoreo y Logs

#### 1. Configuración de Logging

```python
# logging_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/autopilot.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. Monitoreo de Rendimiento

```python
# performance_monitor.py
import psutil
import time

def monitor_system():
    while True:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent

        if cpu > 80:
            logging.warning(f"CPU alto: {cpu}%")
        if memory > 85:
            logging.warning(f"Memoria alta: {memory}%")

        time.sleep(60)
```

### Procedimiento Estándar: Despliegue y Producción

#### 1. Preparación para Producción

```bash
# Configurar variables de entorno
cp .env.example .env
# Editar .env con valores de producción

# Construir assets
cd dashboard
npm run build

# Ejecutar tests finales
python -m pytest
```

#### 2. Inicio en Producción

```bash
# Usar scripts de producción
start.bat              # Inicio completo
# O componentes individuales
python web_dashboard.py --prod
cd dashboard && npm start
```

#### 3. Monitoreo en Producción

```bash
# Verificar servicios
curl http://localhost:3000/api/status
curl http://localhost:5001/api/status

# Revisar logs
tail -f logs/autopilot.log
tail -f dashboard/logs/server.log
```

### Checklist de Calidad de Código

#### ✅ Antes de Commit

- [ ] `python -m flake8 . --max-line-length=88` - Sin errores de linting
- [ ] `python -m black . --check` - Código formateado
- [ ] `python -m pytest` - Tests pasan
- [ ] `cd dashboard && npm run build` - TypeScript compila
- [ ] `markdownlint "docs/**/*.md"` - Documentación correcta

#### ✅ Antes de Merge

- [ ] Cobertura > 85%
- [ ] Sin errores de linting (flake8)
- [ ] Código formateado (black)
- [ ] Documentación actualizada
- [ ] Tests de integración pasan
- [ ] Performance validada

#### ✅ Antes de Release

- [ ] Version bump en package.json
- [ ] CHANGELOG.md actualizado
- [ ] Documentación de usuario actualizada
- [ ] Tests end-to-end pasan
- [ ] Validación cross-browser completada
