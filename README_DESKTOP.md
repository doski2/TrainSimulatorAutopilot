# Train Simulator Autopilot - Aplicación de Escritorio

Esta es la versión de aplicación de escritorio del Dashboard del Train Simulator
Autopilot, construida con Electron para una experiencia nativa.

## Características

- **Interfaz Nativa**: Aplicación de escritorio con apariencia nativa del
  sistema operativo
- **Sin Navegador**: No requiere abrir un navegador web
- **Actualizaciones en Tiempo Real**: Mantiene todas las funcionalidades del
  dashboard web
- **Temas Personalizables**: Soporte para temas Dark, Light, Blue Industrial y
  Green Train
- **Configuraciones Persistentes**: Guarda automáticamente las preferencias del
  usuario

## Requisitos

- Python 3.x con las dependencias instaladas
- Node.js y npm
- Windows (la aplicación está optimizada para Windows)

## Instalación

1. Asegúrate de tener Python y Node.js instalados
2. Instala las dependencias de Python:

   ```bash
   pip install -r requirements.txt
   ```

3. Instala las dependencias de Node.js:

   ```bash
   npm install
   ```

## Inicio de la Aplicación

### Opción 1: Inicio Automático (Recomendado)

Ejecuta el archivo `start.bat` que:

- Verifica si el servidor web está corriendo
- Inicia el servidor si es necesario
- Abre la aplicación Electron automáticamente

### Opción 2: Modo Desarrollo

Ejecuta `start_dev.bat` para:

- Iniciar con DevTools abiertas automáticamente
- Ver logs detallados en la consola
- Modo de desarrollo completo

### Opción 3: Inicio Manual

```bash
# Terminal 1: Iniciar servidor web
python web_dashboard.py

# Terminal 2: Iniciar Electron
npm start
```

### Opción 4: Modo Desarrollo Manual

```bash
# Iniciar Electron con DevTools
npm run dev
```

## Funcionalidades

- **Dashboard Principal**: Vista general con métricas en tiempo real
- **Dashboard SD 40-2**: Interfaz específica para la locomotora SD 40-2
- **Configuración**: Panel de configuración con temas y ajustes
- **Telemetría**: Datos en tiempo real del simulador
- **Gráficos**: Visualización de datos con Chart.js

## Desarrollo

Para desarrollo, puedes usar:

```bash
npm run dev
```

Esto iniciará tanto el servidor como la aplicación Electron.

## Estructura del Proyecto

```text
TrainSimulatorAutopilot/
├── main.js                 # Archivo principal de Electron
├── package.json           # Configuración de Node.js
├── start.bat             # Script de inicio automático
├── web/                  # Aplicación web
│   ├── static/
│   ├── templates/
│   └── dashboard.py
├── scripts/              # Scripts de procesamiento
└── docs/                 # Documentación
```

## Diagnóstico del Panel de Configuración

Si el panel de configuración no se abre, ejecuta el script de diagnóstico:

```bash
diagnostico_config.bat
```

Este script:

- Agrega logs detallados de depuración
- Reinicia la aplicación con modo diagnóstico
- Proporciona instrucciones para revisar la consola del navegador

### Logs de Depuración

Cuando ejecutes el diagnóstico, busca en la consola del navegador (F12) logs
como:

- 🔥 DOM Content Loaded
- 🔧 Setting up settings event listeners
- 🎯 Settings link clicked
- 🔄 Toggling settings panel

### Funciones de Debug

Desde la consola del navegador puedes ejecutar:

```javascript
debugSettings()  // Muestra estado del panel
testToggle()     // Prueba la función toggle
```

## Solución de Problemas

- Si la aplicación no se inicia, verifica que el puerto 5001 esté disponible
- Asegúrate de que todas las dependencias estén instaladas
- Para problemas con el simulador, revisa los logs en la consola
- Si el panel de configuración no funciona, usa el script
  `diagnostico_config.bat`

## Ventajas sobre la Versión Web

1. **Experiencia Nativa**: Se integra mejor con el sistema operativo
2. **Sin Navegador**: No requiere abrir un navegador web separado
3. **Mejor Rendimiento**: Optimizado para aplicaciones de escritorio
4. **Acceso Directo**: Se puede anclar a la barra de tareas
5. **Actualizaciones Automáticas**: Fácil de mantener y actualizar
