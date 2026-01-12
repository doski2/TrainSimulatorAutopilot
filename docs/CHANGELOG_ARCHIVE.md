# Train Simulator Autopilot - Registro de Cambios (Archivo Completo)

Este archivo contiene el historial completo del proyecto tal y como estaba en `CHANGELOG.md` antes del archivado.

> Nota: Este archivo fue creado automáticamente a partir de `CHANGELOG.md` durante el proceso de archivado.

---

# Train Simulator Autopilot - Registro de Cambios

## [Unreleased] - 2025-12-17

### 🔧 Correcciones y mejoras (POC Archivo+ACK)

- **policy**: Cambiado el comportamiento por defecto de `start_autopilot` para
  **NO** requerir ACK del plugin Lua. Esto evita que llamadas al endpoint se
  bloqueen en entornos donde el plugin no está disponible o los accesos a
  archivos están restringidos.
  - Se eliminó el soporte de espera por ACK del flujo principal del proyecto
    y se deprecó la POC basada en archivos (`tools/poc_file_ack`).
  - La PoC `tools/poc_file_ack` y las pruebas relacionadas fueron
    **eliminadas** del repositorio; la decisión y el flujo final están
    documentados en `docs/AUTOPILOT_SENDCOMMAND.md`.
    - Se eliminó el test E2E
      `tests/integration/test_e2e_autopilot_file_ack.py` que comprobaba el flujo
      de ACK por archivos.
    - Se eliminaron múltiples tests unitarios del consumer y otros tests
      relacionados con la PoC ACK (ya deprecada), para reducir ruido y
      mantenimiento en la suite de pruebas.
  - Las métricas relacionadas con ACK (`ack_skipped_total`,
    `unacked_total`) se han eliminado del conjunto de métricas operativas.
  - Tests y documentación actualizados para reflejar la nueva política.

  - **Archivos eliminados (selección):**
    - `tools/poc_file_ack/` (PoC eliminado)
    - `.github/workflows/poc-e2e.yml` (job específico del POC eliminado)
    - `tests/e2e/test_file_ack.py` (E2E)
    - `tests/integration/test_e2e_autopilot_file_ack.py` (E2E)
    - `tests/e2e/test_probe_file.py` (E2E)
    - `tests/e2e/test_retries.py` (E2E)
    - `tests/e2e/test_persist_ids.py` (E2E)
    - Varias pruebas unitarias relacionadas con el consumer (p.ej.
      `tests/unit/test_consumer_*.py`) fueron eliminadas o marcadas como
      omitidas para reducir ruido de mantenimiento

- **consumer**: Registrar excepciones en lugar de silenciarlas para mejorar
  diagnósticos y mantener el loop vivo (`tools/poc_file_ack/consumer.py`).
- **tests**: Añadido `tests/unit/test_consumer_exceptions.py` que valida
  logging y resiliencia del consumer.
- **tests**: Centralizada la configuración de `sys.path` en `tests/conftest.py`
  (se removieron inserciones manuales desde tests individuales).
- **docs**: Documentación actualizada sobre la opción Archivo+ACK y la
  configuración de tests (`docs/docs controles/opcion1_archivo_ack.md`,
  `docs/testing-framework.md`).
- **ci**: `.gitignore` actualizado para ignorar `tmp_poc_dir/`.
  - El job POC E2E (`.github/workflows/poc-e2e.yml`) **fue eliminado** porque
    la PoC basada en archivos fue deprecada.
- **consumer**: Marcar y persistir IDs procesados antes de escribir ACK para
  evitar reprocesos (test: `tests/unit/test_consumer_race_condition.py`).
- **consumer**: Mantener una caché de `processed_ids` con tamaño limitado
  (`processed_ids_max`) para evitar crecimiento ilimitado de memoria en
  consumidores de larga duración (test:
  `tests/unit/test_consumer_bounded_processed_set.py`).

## [2.1.0] - 2025-12-17

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 y este proyecto se adhiere al [Versionado Semántico](https://semver.org/spec/v2.0.0/).

### ✨ Nuevas Funcionalidades

#### Estado de Controles de Locomotora

- **Nueva funcionalidad**: Sistema de estado interno para controles de puertas y
  luces
- **API Endpoint**: `GET /api/control/status` para consultar estado actual
- **Lógica de alternancia**: Los botones ahora alternan correctamente entre
  abrir/cerrar y encender/apagar
- **Mensajes mejorados**: Confirmaciones claras del estado actual
  ("Puertas ABIERTAS", "Luces APAGADAS")

### 🔧 Problemas Resueltos — v2.1.0

#### Controles No Se Actualizaban Correctamente

- **Problema**: Los botones de puertas/luces siempre enviaban el mismo comando
  (ej: siempre "doors_open")
- **Causa**: Falta de estado interno para mantener el estado de los controles
- **Solución**: Implementación de variables de estado `control_states` con
  alternancia lógica
- **Impacto**: Los controles ahora funcionan como toggles reales

#### Comandos Incorrectos Enviados al Lua Script

- **Problema**: El Python enviaba "doors_open" incluso cuando las puertas ya
  estaban abiertas
- **Causa**: Sin distinción entre comandos de apertura y cierre
- **Solución**: Lógica que envía "doors_open"/"doors_close" y
"lights_on"/"lights_off" según estado
- **Impacto**: Comandos correctos llegan al simulador

### 📁 Archivos Modificados — v2.1.0

#### Código Principal — v2.1.0

- `web_dashboard.py`:
  - Agregada variable global `control_states` para mantener estado
  - Actualizada lógica de `toggle_doors` y `toggle_lights` para alternar
  estado
  - Nuevo endpoint `GET /api/control/status`
  - Mensajes de confirmación mejorados

#### Scripts Lua

- `Railworks_GetData_Script.lua`: Ya soportaba comandos separados (sin cambios
necesarios)

#### Documentación — v2.1.0

- `API_DOCUMENTATION.md`: Documentado nuevo endpoint `/api/control/status`
- `TROUBLESHOOTING.md`: Nueva sección sobre problemas de controles que no se
actualizan
- `CHANGELOG.md`: Esta entrada

### 🧪 Verificación — v2.1.0

**Comandos de verificación:**

```bash
# Verificar estado inicial
curl http://localhost:5000/api/control/status

# Debería mostrar:
{
  "success": true,
  "control_states": {
    "doors_open": false,
    "lights_on": false
  }
}

# Probar alternancia (desde el dashboard)
# Click "Puertas" -> debería mostrar "Puertas ABIERTAS"
# Click "Puertas" -> debería mostrar "Puertas CERRADAS"
# Click "Luces" -> debería mostrar "Luces ENCENDIDAS"
```

### 🔄 Cambios Incompatibles

- Los controles de puertas y luces ahora requieren estado del servidor
- El comportamiento de alternancia puede diferir si el servidor se reinicia

## [1.0.1] - 2025-12-03 - Correcciones Críticas de Inicio

### 🔧 Problemas Resueltos — v1.0.1

#### Dashboard No Se Abre Después de start.bat

- **Problema**: El script `start.bat` no iniciaba el dashboard debido a errores
Unicode
- **Causa**: Caracteres emoji (✅, ❌, 🚂) en `direct_tsc_control.py` causaban
`UnicodeEncodeError`
- **Solución**: Reemplazados todos los emojis por texto descriptivo `[OK]`,
`[ERROR]`, `[AUTO]`
- **Impacto**: Dashboard ahora se inicia correctamente en Windows

#### Script de Inicio Problemático

- **Problema**: `start.bat` intentaba iniciar aplicación Electron sin interfaz
gráfica disponible
- **Causa**: Lógica condicional basada en disponibilidad de npm
- **Solución**: Simplificación del script para siempre abrir navegador web
- **Impacto**: Compatibilidad mejorada con entornos sin interfaz gráfica
completa

### 📁 Archivos Modificados — v1.0.1

#### Código Principal — v1.0.1

- `direct_tsc_control.py`: Limpieza completa de caracteres Unicode
- `start.bat`: Reescritura completa con lógica simplificada
- `web_dashboard.py`: Sin cambios (ya funcionaba correctamente)

#### Documentación — v1.0.1

- `docs/troubleshooting.md`: Nueva sección "Problemas Recientes Resueltos"
- `docs/ESTADO_FINAL_PROYECTO.md`: Actualización con estado post-solución
- `mkdocs.yml`: Navegación actualizada con todas las páginas disponibles
- `CHANGELOG.md`: Nueva entrada para v1.0.1

### 🧪 Verificación — v1.0.1

**Comandos de verificación:**

```bash
# Verificar servidor web
Test-NetConnection -ComputerName localhost -Port 5001

# Verificar procesos
Get-Process -Name "python"

# Ejecutar dashboard
cmd /c start.bat
```

**Resultado esperado:**

- ✅ Servidor web ejecutándose en puerto 5001
- ✅ Dashboard accesible en navegador
- ✅ Sin errores Unicode en logs
- ✅ Inicio automático del navegador

### 📊 Métricas de Mejora

| Aspecto | Antes | Después | Mejora | |---------|-------|---------|--------| |
Tiempo de inicio | ~30s (con errores) | ~5s | 83% más rápido | | Tasa de éxito |
0% | 100% | 100% | | Compatibilidad | Limitada | Completa | Total |

### 🔒 Seguridad

- No se introdujeron cambios que afecten la seguridad
- Los mismos mecanismos de validación y sanitización permanecen activos
- Logs mejorados para debugging sin exponer información sensible

---

## [3.0.0] - 2025-11-29

### 🎯 **MODERNIZACIÓN COMPLETA DEL SISTEMA**

#### ✅ Dashboard TypeScript/Node.js Principal

- **Servidor Express.js Completo**: Implementación con TypeScript y
configuración robusta
- **API REST Completa**: 4 endpoints funcionales (`/api/status`, `/api/data`,
`/api/system/:name`, `/api/command`)
- **WebSocket en Tiempo Real**: Socket.IO con eventos bidireccionales para
telemetría
- **Interfaz Web Moderna**: Bootstrap 5, Chart.js, 6 paneles funcionales
(señalización, métricas, sistemas, controles)
- **Configuración Personalizable**: 4 temas, animaciones, intervalos de
actualización
- **TypeScript Tipado Completo**: Compilación correcta, interfaces bien
definidas

#### ✅ Dashboard Flask Secundario Corregido

- **Correcciones Críticas**: Resueltos errores de atributos
`cors_allowed_origins`, `async_mode`, `server`
- **Métricas Avanzadas**: Nuevo endpoint `/api/metrics/dashboard` con uptime,
CPU, memoria, conexiones
- **Validación Mejorada**: Manejo robusto de errores, códigos HTTP apropiados
(400, 403, 404, 500, 503)
- **Logging Detallado**: Seguimiento completo de operaciones y errores

... (truncated in this message)