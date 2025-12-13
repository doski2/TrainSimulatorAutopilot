# Plantilla de Documentación de Telemetría para Simuladores

Esta plantilla está diseñada para documentar de manera estructurada los datos de
telemetría disponibles en diferentes juegos y simuladores, facilitando la
implementación de sistemas de autopilot o dashboards.

## Estructura de la Plantilla

### 1. Encabezado

- **Título**: Identifica el juego/simulador
- **Fuente**: Cómo se obtienen los datos (script, API, etc.)
- **Fecha**: Última actualización

### 2. Secciones de Datos

Organiza las variables por categorías lógicas:

- Controles de motor/potencia
- Sistemas de frenado/control
- Sensores y displays
- Límites y navegación
- Sistema y audio

### 3. Formato de Variables

Cada línea sigue el patrón:

NombreVariable: ValorEjemplo // [ESTADO] Descripción breve

**Estados posibles:**

- `[IMPLEMENTADO]` - Ya integrado en el sistema
- `[NO RELEVANTE]` - No útil para el autopilot
- `[PENDIENTE]` - Identificado pero no implementado
- `[EXPERIMENTAL]` - En pruebas
- `[OBSOLETO]` - Ya no disponible

### 4. Notas de Implementación

- Detalles técnicos específicos del juego
- Unidades de medida
- Frecuencia de actualización
- Consideraciones especiales

## Cómo Usar la Plantilla

1. **Copia la plantilla** a un nuevo archivo con nombre descriptivo
2. **Reemplaza los placeholders**:
   - `[NOMBRE_DEL_JUEGO/SIMULADOR]`
   - `[SCRIPT/MÉTODO_DE_CAPTURA]`
   - `[FECHA]`
   - `[SECCIÓN_X]` con nombres apropiados
   - `[ESTADO]` con estados reales
   - `[SISTEMA/DASHBOARD]` con el nombre de tu sistema

3. **Adapta las secciones** según el juego:
   - Para simuladores de vuelo: Controles de vuelo, navegación, motores
   - Para juegos de carreras: Controles del vehículo, telemetría de pista
   - Para simuladores de tren: Sistemas de freno, potencia, señales

4. **Documenta todas las variables** encontradas, incluso las no implementadas
inicialmente

## Ejemplos de Adaptación

### Para Microsoft Flight Simulator

- Secciones: Controles de Vuelo, Motor/Propulsión, Navegación, Sensores
- Variables: IAS, GS, ALT, HDG, VS, RPM, FUEL, etc.

### Para Assetto Corsa (Simulador de Carreras)

- Secciones: Controles del Vehículo, Telemetría de Pista, Motor, Frenos
- Variables: Speed, RPM, Gear, Brake, Throttle, LapTime, etc.

### Para otros simuladores de tren

- Secciones similares a TSC pero adaptadas al motor específico
- Variables: Power, Brake, Speed, Signals, etc.
  - Signals: `SignalAspect`, `KVB_SignalAspect` and `senal_procesada`
(normalizada para la IA). Valores: -1=UNKNOWN, 0=RED, 1=YELLOW, 2=GREEN.

## Beneficios de Esta Estructura

- **Consistencia**: Formato uniforme entre diferentes juegos
- **Trazabilidad**: Fácil seguimiento de qué está implementado
- **Colaboración**: Otros desarrolladores pueden entender rápidamente
- **Mantenimiento**: Fácil actualizar y agregar nuevas variables
- **Documentación**: Sirve como referencia técnica completa

## Archivo Original

Esta plantilla se basa en la documentación de Train Simulator Classic (`data-
received-from-railworks.md`), que ha demostrado ser efectiva para organizar
datos complejos de telemetría.
