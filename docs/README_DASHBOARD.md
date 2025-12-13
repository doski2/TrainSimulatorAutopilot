# Train Simulator Autopilot - Dashboard Web

## 🚂 Sistema Completo de Piloto Automático para Train Simulator Classic

### 📋 Descripción General

El **Train Simulator Autopilot** es un sistema avanzado de piloto automático
para Train Simulator Classic que incluye:

- **Integración TSC**: Comunicación bidireccional con Train Simulator Classic
- **Sistema Predictivo**: Machine Learning para optimización de conducción
- **Multi-locomotiva**: Control simultáneo de múltiples locomotoras
- **Dashboard Web**: Interfaz web en tiempo real para monitoreo y control remoto

## 🎯 Jerarquía de Sistemas de Dashboard

### 🥇 **Sistema Principal: `dashboard/` (TypeScript + Socket.IO)**

**Estado:** ✅ **RECOMENDADO - Sistema Principal**

- **Tecnología:** TypeScript, Express.js, Socket.IO
- **Inicio:** `./iniciar_dashboard.bat` → <http://localhost:3000>
- **Características:**
  - ✅ Tiempo real con WebSockets
  - ✅ Interfaz moderna y responsive
  - ✅ Sistema de señales ferroviarias
  - ✅ Multi-locomotora con paneles individuales
  - ✅ Métricas avanzadas de rendimiento IA
  - ✅ TypeScript para mantenibilidad
- **Documentación:** `dashboard/README.md`

### 🥈 **Sistema Alternativo: `web/` (Flask + Bootstrap)**

**Estado:** ✅ **DISPONIBLE - Sistema Secundario**

- **Tecnología:** Python Flask, Bootstrap 5, Chart.js
- **Inicio:** `python web_dashboard.py` → <http://localhost:5000>
- **Características:**
  - ✅ Interfaz moderna con Bootstrap
  - ✅ Gráficos interactivos con Chart.js
  - ✅ APIs REST completas
  - ✅ Fácil personalización
- **Documentación:** Sección actual

### 🥉 **Sistema Básico: Eliminado**

**Estado:** ❌ **ELIMINADO - Redundante**

- **Nota:** Sistema básico eliminado por ser redundante con el sistema principal
- **Funcionalidad:** Migrada al sistema principal TypeScript

### 🌐 Dashboard Web - Características Principales

#### 📊 Monitoreo en Tiempo Real

- **Telemetría completa**: Velocidad, acelerador, frenos, pendiente, señales
- **Gráficos interactivos**: Visualización histórica con Chart.js
- **Estado del sistema**: Indicadores de salud y alertas
- **Múltiples locomotoras**: Panel individual para cada locomotora activa

#### 🎮 Control Remoto

- **Piloto automático**: Activación/desactivación remota
- **Sistema predictivo**: Control de optimización ML
- **Entrenamiento**: Reentrenamiento de modelos en tiempo real
- **APIs REST**: Integración con sistemas externos

#### 💻 Interfaz Moderna

- **Responsive Design**: Funciona en desktop, tablet y móvil
- **Tema Oscuro**: Interfaz moderna con gradientes y animaciones
- **WebSockets**: Actualizaciones en tiempo real sin refrescar
- **Bootstrap 5**: Framework CSS moderno y accesible

## 🚀 Instalación y Configuración

### 🥇 Sistema Principal (Recomendado)

```bash
# Desde el directorio raíz del proyecto
./iniciar_dashboard.bat
```

**Acceso:** <http://localhost:3000>

### 🥈 Sistema Alternativo (Flask)

#### Prerrequisitos

```bash
# Instalar dependencias Python
pip install flask flask-socketio python-socketio eventlet

# Instalar dependencias del sistema principal
pip install pandas scikit-learn tensorflow numpy psutil
```

#### Estructura del Proyecto

```text
TrainSimulatorAutopilot/
├── web_dashboard.py          # Servidor Flask principal
├── web/
│   ├── templates/
│   │   └── index.html       # Interfaz web principal
│   └── static/
│       ├── css/
│       │   └── dashboard.css # Estilos personalizados
│       ├── js/
│       │   └── dashboard.js  # Lógica frontend
│       └── demo_data.json    # Datos de demostración
├── scripts/
│   ├── test_web_dashboard.py # Script de pruebas
│   ├── integrator.py         # Integración TSC
│   ├── predictive.py         # Sistema ML
│   └── cleaner.py            # Limpieza de datos
├── data/
│   ├── raw/                  # Datos crudos TSC
│   ├── clean/                # Datos procesados
│   └── logs/                 # Registros del sistema
└── docs/                     # Documentación
```

#### Inicio del Sistema Flask

```bash
# Desde el directorio raíz del proyecto
python web_dashboard.py
```

**Acceso:** <http://localhost:5000>

## 🎯 Uso del Dashboard

### 🥇 Sistema Principal (TypeScript)

#### Inicio del Sistema TypeScript

```bash
# Desde el directorio raíz del proyecto
./iniciar_dashboard.bat
```

#### Acceso al Dashboard Principal

Abrir navegador en: **<http://localhost:3000>**

### 🥈 Sistema Flask Alternativo

#### Inicio del Dashboard Flask

```bash
# Desde el directorio raíz del proyecto
python web_dashboard.py
```

#### Acceso al Dashboard Flask

Abrir navegador en: **<http://localhost:5000>**

### 3. Funcionalidades Disponibles

#### Panel de Telemetría

- **Velocidad actual**: En mph con indicador visual
- **Controles**: Acelerador, freno de tren, freno de motor
- **Condiciones**: Pendiente, límite de velocidad, radio de curva
- **Señales**: Estado de señales principal y avanzada

#### Gráficos Interactivos

- **Historial de velocidad**: Gráfico de línea con datos históricos
- **Tendencias**: Visualización de aceleración y frenado
- **Predicciones**: Comparación entre valores reales y predichos

#### Control del Sistema

- **Piloto Automático**: Botones para iniciar/detener
- **Sistema Predictivo**: Activación de optimización ML
- **Entrenamiento**: Reentrenamiento de modelos
- **Reinicio**: Reset completo del sistema

#### Panel Multi-locomotiva

- **Lista de locomotoras**: Todas las locomotoras detectadas
- **Estado individual**: Velocidad y controles por locomotora
- **Control selectivo**: Operaciones en locomotoras específicas

## 🔧 APIs REST

### Endpoints Disponibles

#### Estado del Sistema

```http
GET /api/status
```

Retorna estado completo del sistema incluyendo telemetría, predicciones y estado
de locomotoras.

#### Control del Piloto

```http
POST /api/control/start_autopilot
POST /api/control/stop_autopilot
```

Inicia o detiene el piloto automático.

#### Sistema Predictivo

```http
POST /api/control/start_predictive
POST /api/control/stop_predictive
POST /api/control/train_model
```

Control del sistema de machine learning.

### Ejemplos de Uso

```bash
# Obtener estado
curl http://localhost:5000/api/status

# Iniciar piloto
curl -X POST http://localhost:5000/api/control/start_autopilot

# Entrenar modelo
curl -X POST http://localhost:5000/api/control/train_model
```

## 📊 Métricas del Dashboard

### Métricas Principales

El dashboard muestra las siguientes métricas en tiempo real desde Train
Simulator Classic:

#### 🚂 **Métricas de Movimiento**

- **Velocidad Actual**: Velocidad del tren en km/h o mph
- **Aceleración**: Aceleración/deceleración en m/s² (+ = acelerando, - =
frenando)
- **Pendiente**: Gradiente de la vía en ‰ (por mil)
- **Límite de Velocidad**: Velocidad máxima permitida

#### ⚙️ **Métricas del Motor (NUEVO - v2.0)**

- **Esfuerzo de Tracción**: Fuerza de tracción en kN (kilonewtons)
- **RPM**: Revoluciones por minuto del motor
- **Corriente**: Amperaje del sistema eléctrico en A
- **Deslizamiento**: Indicador de pérdida de adherencia (0-2)

#### ⛽ **Métricas de Consumo**

- **Nivel de Combustible**: Cantidad de combustible restante
- **Presión de Frenos**: Presión en sistemas de freno

### Visualización de Métricas

#### Tarjetas de Métricas

- **Velocidad**: Tarjeta principal con indicador grande
- **Aceleración**: Muestra valores positivos/negativos con colores
- **Esfuerzo de Tracción**: Nueva tarjeta con icono de engranajes
- **Motor**: Tres tarjetas para RPM, Corriente y Deslizamiento

#### Gráfico de Velocidad

- **Historial**: Últimos 50 puntos de velocidad
- **Límite**: Línea roja indicando límite de velocidad
- **Tiempo real**: Actualización continua cada 100ms

### Estados y Alertas

#### Estados del Sistema

- **🟢 Activo**: Sistema funcionando normalmente
- **🟡 Advertencia**: Valores fuera de rango normal
- **🔴 Error**: Problemas de comunicación o datos inválidos

#### Alertas de Seguridad

- **Deslizamiento**: Alerta cuando > 1.0
- **Sobrecarga**: Alerta cuando corriente > 1000A
- **Sobrevelocidad**: Alerta cuando velocidad > límite + 10%

## 🧪 Pruebas

### Script de Pruebas Automatizado

```bash
python scripts/test_web_dashboard.py
```

### Pruebas Manuales

1. **Interfaz Web**: Verificar carga correcta en navegador
2. **WebSockets**: Comprobar actualizaciones en tiempo real
3. **Controles**: Probar botones de control
4. **Gráficos**: Verificar visualización de datos
5. **APIs**: Probar endpoints REST

### Pruebas con TSC

1. Iniciar Train Simulator Classic
2. Cargar escenario con locomotoras
3. Ejecutar `python web_dashboard.py`
4. Abrir dashboard en navegador
5. Verificar datos en tiempo real

## 📊 Arquitectura Técnica

### Backend (Flask)

- **Servidor web**: Flask con SocketIO para WebSockets
- **Hilos**: Procesamiento en background para telemetría
- **Integración**: Comunicación con sistemas TSC existentes
- **APIs**: Endpoints REST para control remoto

### Frontend (HTML/CSS/JS)

- **Framework**: Bootstrap 5 para responsive design
- **Gráficos**: Chart.js para visualización de datos
- **WebSockets**: Socket.IO para comunicación bidireccional
- **Tema**: CSS personalizado con gradientes y animaciones

### Comunicación

- **WebSockets**: Actualizaciones en tiempo real (< 100ms latencia)
- **REST APIs**: Control remoto y integración externa
- **Event-driven**: Arquitectura basada en eventos

## 🔒 Seguridad y Rendimiento

### Seguridad

- **CORS**: Configurado para desarrollo local
- **Validación**: Entradas sanitizadas en APIs
- **Rate limiting**: Protección contra abuso de APIs

### Rendimiento

- **Optimización**: Actualizaciones eficientes de UI
- **Compresión**: Archivos estáticos comprimidos
- **Caching**: Headers apropiados para navegador

## 🐛 Solución de Problemas

### Problemas Comunes

#### Dashboard no carga

```bash
# Verificar puerto 5000 disponible
netstat -ano | findstr :5000

# Verificar dependencias instaladas
pip list | findstr flask
```

#### Sin datos en tiempo real

- Verificar que TSC esté ejecutándose
- Comprobar conexión de integración TSC
- Revisar logs del sistema

#### WebSockets no conectan

- Verificar firewall/antivirus
- Comprobar configuración de red
- Revisar consola del navegador (F12)

### Logs y Debug

```bash
# Ver logs del dashboard
python web_dashboard.py  # Los logs se muestran en consola

# Ver logs de integración TSC
# Revisar archivos en data/logs/
```

## 🛠️ Solución de Problemas y Actualizaciones (2025-11-09)

### Problemas recientes

- Error de puerto ocupado (WinError 10048): Solucionado cambiando el puerto del
dashboard a 5001.
- Advertencia de incompatibilidad de modelos scikit-learn: Si se actualiza
scikit-learn, reentrenar y guardar los modelos nuevamente.
- Recomendación: Si el dashboard no inicia, verificar con
`netstat -ano | findstr :5000` y liberar el puerto con `taskkill /PID <PID> /F`.

### Actualización de dependencias

- Instalar dependencias en el entorno virtual:

  ```bash
  pip install flask flask-socketio python-socketio eventlet \
    joblib scikit-learn tensorflow pandas numpy psutil
  ```

- Si hay problemas de compatibilidad, revisar las versiones y reentrenar modelos
ML.

### Cambio de puerto

- Editar `web_dashboard.py` y modificar la línea:

  ```python
  def start_dashboard(host='0.0.0.0', port=5001):
  ```

- Reiniciar el dashboard y acceder a `http://localhost:5001`.

---

## 📈 Métricas y Monitoreo

### Métricas Disponibles

- **Rendimiento**: Latencia de respuesta, uso de CPU/memoria
- **Telemetría**: Datos de conducción en tiempo real
- **Sistema**: Estado de componentes y servicios
- **Predicciones**: Precisión del modelo ML

### Monitoreo

- **Dashboard web**: Visualización en tiempo real
- **Logs**: Registros detallados de operaciones
- **Alertas**: Notificaciones de eventos importantes

## 🚀 Próximos Pasos

### Mejoras Planificadas

- [ ] Autenticación y autorización
- [ ] Configuración remota de parámetros
- [ ] Exportación de datos históricos
- [ ] Notificaciones push
- [ ] Modo offline con datos simulados

### Contribuciones

El proyecto está abierto a contribuciones. Áreas de interés:

- Optimización de rendimiento
- Nuevas funcionalidades de UI
- Mejoras en algoritmos ML
- Documentación adicional

## 📄 Licencia

Este proyecto es software libre bajo licencia MIT.

## 👥 Soporte

Para soporte técnico o preguntas:

- Revisar documentación en `docs/`
- Ejecutar pruebas con `scripts/test_web_dashboard.py`
- Verificar logs del sistema

---

**Versión**: 1.1.0 **Última actualización**: Diciembre 2025 **Estado**:
Producción listo    
