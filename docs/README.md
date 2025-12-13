# Train Simulator Autopilot

## 🚂 Sistema de Piloto Automático Completo para Train Simulator Classic

Proyecto de integración completa de IA para conducción automática en Train
Simulator Classic, con comunicación bidireccional real y control inteligente de
trenes.

## ✅ Estado del Proyecto: COMPLETADO

El sistema incluye integración real con Train Simulator Classic, IA funcional, y
envío de comandos al juego. ¡Listo para usar!

## 🎯 Características Principales

### 🔗 Integración Real con TSC

- **Lectura de datos en tiempo real** desde el Raildriver Interface
- **Envío de comandos al juego** vía archivo SendCommand.txt
- **14 controles monitoreados** (velocidad, aceleración, pendiente, frenos,
etc.)
- **Frecuencia de actualización:** 10 Hz

### 🤖 IA Inteligente

- **Control automático de velocidad** según límites y señales
- **Ajustes por pendiente** (subidas/bajadas)
- **Frenado inteligente** en curvas y paradas
- **Historial de decisiones** completo

### 🚂 Características Avanzadas

- **Soporte Multi-Locomotora**: Detecta y controla múltiples locomotoras
simultáneamente
- **Selección Inteligente**: Elige qué locomotora controlar activamente
- **Monitoreo Independiente**: Cada locomotora tiene su propio estado y
telemetría
- **Gestión Automática**: Locomotoras inactivas se eliminan automáticamente
- **Análisis Predictivo**: Machine learning para anticipar comportamiento del
tren
- **Predicciones en Tiempo Real**: Predice velocidad, aceleración y condiciones
futuras
- **Control Inteligente**: Decisiones basadas en predicciones para mayor
seguridad

### 🎮 Demos Interactivas

- **`demo_multi_locomotive.py`** - Demostración completa del sistema
multi-locomotora
- **`demo_predictive_autopilot.py`** - Demo del análisis predictivo con machine
learning
- **`scripts/demo_completa_autopilot.py`** - Demo completa del piloto automático
- **`scripts/test_predictive_telemetry.py`** - Pruebas del sistema predictivo

## 🚀 Instalación Rápida

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd TrainSimulatorAutopilot

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar instalación
python scripts/demo_completa_autopilot.py
```

## 🎮 Uso del Piloto Automático

### Opción 1: Interface Interactiva (Recomendado)

```bash
python autopilot_system.py
```

Comandos disponibles:

- `start` - Iniciar sesión
- `auto` - Activar modo automático
- `status` - Ver estado del sistema
- `quit` - Salir

### Opción 2: Demo Completa

```bash
python scripts/demo_completa_autopilot.py
```

### Opción 3: Pruebas Individuales

```bash
# Probar lectura de datos
python scripts/test_datos_archivo.py

# Probar envío de comandos
python scripts/test_envio_comandos.py

# Probar IA
python scripts/test_datos_simulados.py
```

## 📊 Arquitectura del Sistema

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Train Simulator │    │ Raildriver       │    │   GetData.txt   │
│     Classic      │◄──►│  Interface       │◄──►│  (Lectura)      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ TSC Integration │    │   Sistema IA     │    │  SendCommand    │
│  (tsc_integration│───▶│  (Decisión)     │───▶│  .txt (Escritura)│
│     .py)        │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Comandos de     │    │   Control del    │    │   Retroaliment. │
│ Control         │───▶│   Tren          │───▶│   Visual        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📖 Requisitos del Sistema

### Software Requerido

- **Train Simulator Classic** instalado
- **TSClassic Raildriver Interface** v3.3.0.9
- **Python 3.8+**

### Hardware

- PC con Windows
- Conexión al Raildriver Interface

## 🧪 Verificación del Sistema

Ejecuta la demo completa para verificar que todo funciona:

```bash
python scripts/demo_completa_autopilot.py
```

Deberías ver:

- ✅ Lectura de datos reales del tren
- ✅ Procesamiento inteligente con IA
- ✅ Envío de comandos al juego

## 📚 Documentación

- **`docs/integration.md`** - Guía completa de integración
- **`docs/ESTADO_FINAL_PROYECTO.md`** - Estado final del proyecto
- **`docs/ia-spec.md`** - Especificaciones de la IA
- **`docs/workflow-log.md`** - Registro de desarrollo

## 🔧 Solución de Problemas

### El sistema no lee datos

- ✅ Verifica que TSC esté ejecutándose
- ✅ Verifica que el Raildriver Interface esté conectado
- ✅ Verifica que estés conduciendo un tren

### Los comandos no afectan al juego

- ✅ Verifica que el archivo SendCommand.txt se esté creando
- ✅ Verifica que TSC esté en modo "conducir"
- ✅ Reinicia el Raildriver Interface si es necesario

## 🎯 Próximas Mejoras (Opcionales)

- [x] **Dashboard web en tiempo real**
- [x] **Optimización de frecuencia de lectura** ✅ COMPLETADO
- [x] **Soporte para múltiples locomotoras** ✅ COMPLETADO
- [x] **Análisis predictivo de telemetría** ✅ COMPLETADO

## 📞 Soporte

**Estado:** ✅ **Proyecto Completado y Funcional**

Si encuentras problemas:

1. Ejecuta `python scripts/demo_completa_autopilot.py`
2. Revisa los logs en `tsc_integration.log`
3. Consulta `docs/integration.md`

---

**🚂 ¡Disfruta conduciendo trenes automáticamente!** 4. Actualiza docs y registra
en `workflow-log.md`.

## Comunidad

Comparte avances en foros como UKTrainSim, Railworks America o Discord de Train
Simulator. Incluye capturas de dashboards y logs de pruebas.

## Licencia

Proyecto personal - consulta términos de Train Simulator Classic.

---

Última actualización: Diciembre 2025
