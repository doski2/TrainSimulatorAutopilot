# 📖 Índice de Documentación - Train Simulator Autopilot

## 🎯 Visión General

Este índice proporciona una guía completa para navegar por la documentación
reorganizada del proyecto Train Simulator Autopilot. La documentación ha sido
estructurada en carpetas temáticas para facilitar el mantenimiento y la búsqueda
de información.

## 📁 Estructura de Documentación

### 📋 docs/procedimientos/

Guías prácticas y procedimientos estándar para el uso del sistema.

#### [`procedimientos-estandar.md`](procedimientos/procedimientos-estandar.md)

- **Integración IA con TSClassic Raildriver**: Guía paso a paso para configurar
la integración
- **Ejemplos concretos**: Personalización para SD70MAC (Academy)
- **Descripción de directorios**: FullEngineData/, InputMapper/, KeyMaps/
- **Checklist de validación**: Procedimientos para cada sesión de simulación

### 💻 docs/ejemplos/

Ejemplos de código, configuraciones y casos prácticos.

#### [`ejemplos-codigo.md`](ejemplos/ejemplos-codigo.md)

- **Scripts Lua**: Control de velocidad, frenado automático
- **Configuración Python**: Análisis predictivo, integración multi-locomotora
- **Configuración JSON**: Dashboard web, logging estructurado
- **Configuración INI**: Sistema principal, escenarios personalizados

### 📚 docs/historico/

Registro completo del desarrollo y evolución del proyecto.

#### [`historial-proyecto.md`](historico/historial-proyecto.md)

- **Registro histórico**: Desarrollo desde [01/11/2025] hasta [08/11/2025]
- **Cambios por versión**: 1.0.0, 1.5.0, 2.0.0
- **Métricas de desarrollo**: Estadísticas del proyecto, rendimiento, IA
- **Lecciones aprendidas**: Arquitectura, desarrollo IA, integración hardware

### 🔧 docs/desarrollo/

Logs técnicos, verificaciones y detalles de implementación.

#### [`logs-tecnicos.md`](desarrollo/logs-tecnicos.md)

- **Verificaciones de interfaces**: GUI, Rust/C++, multiplataforma
- **Métricas y rendimiento**: Estadísticas del proyecto, sistema, IA
- **Actualizaciones recientes**: Dashboard v2.0 con métricas del motor
- **Troubleshooting**: Soluciones rápidas, FAQ, métricas de evaluación

#### [`CORRECCIONES_DASHBOARD.md`](CORRECCIONES_DASHBOARD.md) ⭐ **NUEVO**

- **Problema del esfuerzo de tracción**: Corrección de visualización en N vs kN
- **Error "alerts no es un array"**: Solución para formato de datos de alertas
- **Unidades consistentes**: Mejoras en la presentación de datos
- **Verificación del sistema**: Comandos y estado actual

## 📄 Documentos Principales (Raíz docs/)

### [`GUIA_DESARROLLADOR.md`](GUIA_DESARROLLADOR.md) ⭐ **NUEVO**

**Guía rápida completa para desarrolladores** - Todo lo esencial en un solo
lugar.

- **🚀 Inicio rápido**: Configuración del entorno y primeros pasos
- **🏗️ Arquitectura**: Diagramas y flujo de datos del sistema
- **📁 Estructura**: Organización completa del proyecto
- **🔧 Desarrollo**: Testing, debugging y workflows
- **📚 Documentación**: Referencias importantes y navegación
- **🎯 Métricas**: Variables implementadas y endpoints API
- **🚨 Troubleshooting**: Soluciones rápidas a problemas comunes
- **🔄 Workflows**: Procesos de desarrollo y mantenimiento

### [`workflow-log.md`](workflow-log.md)

- **Resumen ejecutivo**: Estado actual del proyecto
- **Métricas clave**: Rendimiento, precisión, uptime
- **Próximos pasos**: Planificación inmediata y a largo plazo
- **Referencias rápidas**: Enlaces a documentación y scripts principales

### [`ia-spec.md`](ia-spec.md)

- **Especificaciones técnicas**: Algoritmos, reglas de conducción
- **Integración técnica**: Comunicación con simulador
- **Auditoría y métricas**: Validación y medición de rendimiento

### [`integration.md`](integration.md)

- **Arquitectura de integración**: Componentes y flujo de datos
- **Protocolos de comunicación**: Socket TCP/IP, parsing de datos
- **Manejo de errores**: Estrategias de recuperación

### [`API_REFERENCE.md`](API_REFERENCE.md) ⭐ **NUEVO**

- **Referencia completa de APIs:** Arquitectura, endpoints REST, WebSocket
- **Web Dashboard API:** Flask server, métricas, control del sistema
- **APIs de análisis estadístico:** Alertas, reportes, correlaciones, anomalías
- **Clientes programáticos:** Python y JavaScript
- **Seguridad y manejo de errores:** CORS, validación, logging

### [`flujo-ia-conduccion.md`](flujo-ia-conduccion.md)

- **Flujo completo de IA**: Desde telemetría hasta comandos
- **Algoritmos de decisión**: Lógica de control automático
- **Optimizaciones**: Procesamiento paralelo, sincronización

### [`testing-framework.md`](testing-framework.md)

- **Estrategia de testing**: Unitarios, integración, rendimiento
- **Herramientas**: pytest, coverage, benchmarking
- **Casos de prueba**: Edge cases, estrés, validación

## 🗂️ Documentos de Soporte

### Reportes de Rendimiento y Estado

- [`REPORTES_PERFORMANCE.md`](REPORTES_PERFORMANCE.md) ⭐ **NUEVO** - Reportes
consolidados de rendimiento, estado del proyecto y métricas

### Notas Personales

- [`notas personales.txt`](notas%20personales.txt) - Notas organizadas del
desarrollador

## 🔗 Navegación Temática

### 👨‍💻 Para Desarrolladores

1. **[`GUIA_DESARROLLADOR.md`](GUIA_DESARROLLADOR.md)** ⭐ **NUEVO** - Guía
rápida completa
2. **[`WEB_DASHBOARD_API.md`](WEB_DASHBOARD_API.md)** ⭐ **NUEVO** - API del
servidor web
3. **[`ia-spec.md`](ia-spec.md)** - Especificaciones técnicas
4. **[`flujo-ia-conduccion.md`](flujo-ia-conduccion.md)** - Lógica de IA
5. **[`api-reference.md`](api-reference.md)** - Referencia de APIs
6. **[`testing-framework.md`](testing-framework.md)** - Testing
7. **[`ejemplos-codigo.md`](ejemplos/ejemplos-codigo.md)** - Ejemplos prácticos

### 👤 Para Usuarios

1. **[`README.md`](README.md)** - Guía de instalación y uso
2. **[`procedimientos-estandar.md`](procedimientos/procedimientos-estandar.md)**

-

Procedimientos de uso
3. **[`workflow-log.md`](workflow-log.md)** - Estado del proyecto
4. **[`README_DASHBOARD.md`](README_DASHBOARD.md)** - Uso del dashboard web
5. **[`signals.md`](signals.md)** - Guía completa sobre `SignalAspect` y
`KVB_SignalAspect`

### 🔧 Para Administradores

1. **[`workflow-log.md`](workflow-log.md)** - Estado y métricas
2. **[`logs-tecnicos.md`](desarrollo/logs-tecnicos.md)** - Verificaciones
técnicas
3. **[`historial-proyecto.md`](historico/historial-proyecto.md)** - Historial de
desarrollo
4. **[`REPORTES_PERFORMANCE.md`](REPORTES_PERFORMANCE.md)** ⭐ **NUEVO** -
Reportes de rendimiento y estado

## 📊 Métricas del Proyecto

| Aspecto                | Valor                | Archivo de Referencia
| | ---------------------- | -------------------- |
---------------------------------------------------------- | | **Líneas de
Código**   | ~20,000+             | [`historial-
proyecto.md`](historico/historial-proyecto.md) | | **Archivos**           | 55+
| [`historial-proyecto.md`](historico/historial-proyecto.md) | | **Dashboards
Activos** | 3 sistemas completos | [`logs-tecnicos.md`](desarrollo/logs-
tecnicos.md)          | | **APIs REST**          | 15+ endpoints        |
[`WEB_DASHBOARD_API.md`](WEB_DASHBOARD_API.md)             | | **WebSocket
Events**   | 8+ eventos           |
[`WEB_DASHBOARD_API.md`](WEB_DASHBOARD_API.md)             | | **Tests**
| 200+                 | [`testing-framework.md`](testing-framework.md)
| | **Cobertura**          | 85%                  | [`testing-
framework.md`](testing-framework.md)             | | **Precisión IA**       |
92%                  | [`logs-tecnicos.md`](desarrollo/logs-tecnicos.md)
| | **Latencia**           | <50ms                | [`logs-
tecnicos.md`](desarrollo/logs-tecnicos.md)          | | **Calidad Código**     |
0 errores linting    | [`logs-tecnicos.md`](desarrollo/logs-tecnicos.md)
|

## 🚀 Estado Actual

### ✅ Componentes Operativos

- Sistema IA predictiva con control automático
- Dashboard web con métricas en tiempo real
- Integración completa con Train Simulator Classic
- Soporte multiplataforma (Python, Node.js, C++)
- Sistema de seguridad y backups automatizados

### 🔄 Próximos Pasos

- Pruebas de integración real con TSC
- Calibración de parámetros IA
- Recopilación de feedback de comunidad
- Desarrollo de nuevas características

## 🎨 Diagramas de Arquitectura ⭐ **NUEVO**

### [`DIAGRAMS.md`](DIAGRAMS.md)

Documentación completa sobre los diagramas de arquitectura generados
automáticamente.

#### 📊 Diagramas Disponibles

- **`architecture_diagram.png`** (163KB) - Vista general del sistema
  - Componentes principales y flujo básico
  - Ideal para presentaciones y documentación de alto nivel

- **`architecture_diagram_complete.png`** (281KB) - Vista completa del proyecto
  - Todos los archivos y componentes detallados
  - Estructura completa organizada en clusters
  - Dependencias específicas entre módulos

#### 🛠️ Generación y Mantenimiento

- **Generación automática** usando librería `diagrams` de Python
- **Graphviz** como motor de renderizado
- **Actualización automática** cuando cambia la arquitectura
- **Convenciones de estilo** documentadas

## 📞 Contacto y Soporte

Para preguntas específicas sobre la documentación:

- **Desarrolladores**: Consulte
[`logs-tecnicos.md`](desarrollo/logs-tecnicos.md)
- **Usuarios**: Revise
[`procedimientos-estandar.md`](procedimientos/procedimientos-estandar.md)
- **Administradores**: Vea [`workflow-log.md`](workflow-log.md)

---

**📖 Última actualización:** Diciembre 2025 **🏆 Proyecto:** Train Simulator
Autopilot v2.0.0
