# 🚂 Train Simulator Autopilot - Dashboard Web

Dashboard web en tiempo real para monitoreo y control del sistema Train
Simulator Autopilot. Está desarrollado con TypeScript, Express y Socket.IO.

## Características

- **Monitoreo en tiempo real** de velocidad, sistemas de señalización y
  estado de seguridad
- **Interfaz moderna y responsive** con indicadores visuales claros
- **Conexión WebSocket** para actualizaciones en vivo
- **API REST** para integración con sistemas externos
- **Soporte completo** para sistemas de señalización norteamericanos
  (ACSES, PTC, ATC, CAB)
- **Panel de control** para envío de comandos al sistema
- **Configuración personalizable** (temas, animaciones, intervalos)
- **Gráficos interactivos** con Chart.js

## Arquitectura

```text
dashboard/
├── src/
│   ├── server.ts                    # Servidor Express principal
│   ├── routes/
│   │   └── api.ts                   # Rutas API REST
│   └── services/
│       └── SignalingDataService.ts  # Servicio de datos de señalización
├── public/
│   └── index.html                   # Interfaz web completa (HTML + CSS + JS embebido)
├── dist/                            # Archivos compilados TypeScript
├── package.json                     # Dependencias y scripts
└── tsconfig.json                    # Configuración TypeScript
```

## Instalación

1. **Instalar dependencias:**

   ```bash
   cd dashboard
   npm install
   ```

2. **Compilar TypeScript:**

   ```bash
   npm run build
   ```

3. **Iniciar el servidor:**

   ```bash
   npm start
   ```

   Para desarrollo con recarga automática:

   ```bash
   npm run dev
   ```

4. **Acceder al dashboard:**
   Abrir `http://localhost:3000` en el navegador (puerto por defecto)

## API REST

### Endpoints Disponibles

#### `GET /api/status`

Estado general del sistema de señalización.

**Respuesta (200):**

```json
{
    "connected": true,
    "timestamp": 1640995200.0,
    "estado_sistema": "activo",
    "sistemas_activos": {
        "acses": true,
        "ptc": false,
        "atc": true,
        "cab": false
    }
}
```

#### `GET /api/data`

Todos los datos de señalización disponibles.

**Respuesta (200):**

```json
{
    "timestamp": 1640995200.0,
    "estado_sistema": "activo",
    "sistemas_activos": {
        "acses": { "activo": true, "timestamp": 1640995200.0 },
        "ptc": { "activo": false, "timestamp": null },
        "atc": { "activo": true, "timestamp": 1640995200.0 },
        "cab": { "activo": false, "timestamp": null }
    }
}
```

#### `GET /api/system/:name`

Datos específicos de un sistema de señalización.

**Parámetros URL:**

- `name`: `acses`, `ptc`, `atc`, `cab`

**Respuesta (200):**

```json
{
    "activo": true,
    "timestamp": 1640995200.0,
    "datos_especificos": {
        // Datos específicos del sistema
    }
}
```

**Respuesta (404):**

```json
{
    "error": "Sistema acses no encontrado"
}
```

#### `POST /api/command`

Enviar comandos al sistema de señalización.

**Cuerpo de la solicitud:**

```json
{
    "type": "acses",
    "action": "set_signal",
    "value": "green",
    "timestamp": 1640995200.0
}
```

**Respuesta (200):**

```json
{
    "success": true,
    "message": "Comando enviado correctamente"
}
```

### Ejemplos de uso

```javascript
// Obtener estado del sistema
fetch('/api/status')
  .then(res => res.json())
  .then(data => console.log('Estado:', data));

// Obtener datos de un sistema específico
fetch('/api/system/acses')
  .then(res => res.json())
  .then(data => console.log('ACSES:', data));

// Enviar un comando
fetch('/api/command', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    type: 'acses',
    action: 'set_signal',
    value: 'green'
  })
})
.then(res => res.json())
.then(data => console.log('Comando enviado:', data));
```

## WebSocket Events

### Eventos del Servidor → Cliente

- `telemetry_update` - Actualización de datos de telemetría
- `system_message` - Mensajes del sistema (info, warning, error)
- `alert_triggered` - Nueva alerta activada
- `performance_update` - Actualización de métricas de rendimiento

### Eventos del Cliente → Servidor

- `request_telemetry` - Solicitar actualización inmediata de telemetría

### Ejemplo de conexión WebSocket

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:3000');

// Conectar
socket.on('connect', () => {
    console.log('Conectado al dashboard');
    socket.emit('request_telemetry');
});

// Recibir actualizaciones
socket.on('telemetry_update', (data) => {
    console.log('Datos actualizados:', data);
    updateDashboard(data);
});

// Recibir mensajes del sistema
socket.on('system_message', (msg) => {
    console.log('Mensaje:', msg);
    showNotification(msg);
});
```

## Paneles del Dashboard

### 1. **Panel de Señalización en Tiempo Real**

- Estado actual de señalización
- Timestamp de última actualización
- Estado general del sistema
- Número de sistemas activos

### 2. **Métricas Principales**

- Velocidad actual del tren
- Estado del sistema
- Número de sistemas activos
- Señal actual

### 3. **Sistemas de Señalización**

Panel individual para cada sistema:

- **ACSES** (Advanced Civil Speed Enforcement System)
- **PTC** (Positive Train Control)
- **ATC** (Automatic Train Control)
- **CAB** (Cab Signal System)

Cada panel muestra:

- Estado de actividad (Activo/Inactivo)
- Timestamp de última actualización
- Información específica del sistema

### 4. **Panel de Control**

- Envío de comandos al sistema
- Selección de tipo de sistema
- Parámetros JSON personalizables
- Confirmación de envío

### 5. **Configuración del Dashboard**

- **Tema visual**: Oscuro, Claro, Azul Industrial, Verde Tren
- **Animaciones**: Habilitar/deshabilitar
- **Intervalo de actualización**: 500ms - 5000ms
- **Puntos de historial**: 10 - 200 puntos
- **Notificaciones**: Alertas del sistema, señales, comandos

### 6. **Gráfico Histórico**

- Visualización de señales a lo largo del tiempo
- Chart.js interactivo
- Historial configurable
- Actualización en tiempo real

## Desarrollo

### Scripts Disponibles

```bash
npm run build      # Compilar TypeScript a JavaScript
npm start          # Iniciar servidor de producción
npm run dev        # Desarrollo con ts-node (sin compilación)
npm run watch      # Compilación continua con nodemon
```

### Estructura de Datos

```typescript
interface SignalingData {
  timestamp: number;
  estado_sistema: string;
  sistemas_activos: {
    acses: { activo: boolean; timestamp: number | null };
    ptc: { activo: boolean; timestamp: number | null };
    atc: { activo: boolean; timestamp: number | null };
    cab: { activo: boolean; timestamp: number | null };
  };
}

interface SystemData {
  activo: boolean;
  timestamp: number | null;
  // Datos específicos del sistema...
}

interface CommandData {
  type: 'acses' | 'ptc' | 'atc' | 'cab';
  action: string;
  value?: any;
  timestamp: number;
}
```

## Requisitos del Sistema

- **Node.js** >= 16.0
- **TypeScript** >= 5.0
- **Navegador moderno** con soporte WebSocket
- **Sistema operativo**: Windows, macOS, Linux

## Tecnologías Utilizadas

- **Backend**: Node.js, Express.js, Socket.IO
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Visualización**: Chart.js
- **Lenguaje**: TypeScript
- **Build**: npm scripts, TSC

## Solución de Problemas

### El dashboard no carga

1. Verificar que Node.js esté instalado: `node --version`
2. Instalar dependencias: `npm install`
3. Compilar proyecto: `npm run build`
4. Iniciar servidor: `npm start`
5. Acceder a `http://localhost:3000`

### Error de conexión WebSocket

1. Verificar que el puerto 3000 no esté ocupado
2. Comprobar firewall/antivirus
3. Revisar logs del servidor en consola

### Problemas de rendimiento

- Reducir intervalo de actualización en configuración
- Disminuir puntos de historial
- Deshabilitar animaciones si es necesario

## Configuración

### Variables de Entorno

```bash
PORT=3000                    # Puerto del servidor (opcional)
NODE_ENV=development         # Entorno de ejecución
CORS_ORIGIN=*               # Origen permitido para CORS
```

### Configuración TypeScript

El archivo `tsconfig.json` incluye configuración optimizada para:

- Compilación ES6+
- Source maps para debugging
- Strict type checking
- Output en carpeta `dist/`

## Contribución

1. Fork el proyecto
2. Crear rama para nueva funcionalidad: `git checkout -b feature/nueva-funcionalidad`
3. Realizar cambios y pruebas
4. Commit: `git commit -m "Agrega nueva funcionalidad"`
5. Push: `git push origin feature/nueva-funcionalidad`
6. Crear Pull Request

## Licencia

MIT License - ver archivo LICENSE para más detalles.

---

**🚂 Dashboard Web - Train Simulator Autopilot**
**Versión:** 1.0.0
**Fecha:** Noviembre 2025
