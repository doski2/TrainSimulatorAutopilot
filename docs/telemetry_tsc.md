# Telemetría: Train Simulator Classic (TSC)

Documento generado a partir de `TELEMETRY_TEMPLATE_README.md` y adaptado a TSC.

## Fuente de datos
- Método de captura: `Railworks_GetData_Script.lua` (plugin que escribe `GetData.txt`) o scripts de depuración `debug_fetch.py` / `debug_tsc.py`.

## Variables principales (ejemplo)
- CurrentSpeed: 10.0 // [IMPLEMENTADO] - Velocidad actual (m/s)
- Acceleration: 0.5 // [IMPLEMENTADO] - Aceleración (m/s²)
- RPM: 400 // [IMPLEMENTADO] - Revoluciones por minuto del motor
- Ammeter: 250.5 // [IMPLEMENTADO] - Lectura del amperímetro
- AirBrakePipePressurePSI: 50.0 // [IMPLEMENTADO] - Presión del tubo de freno (PSI)
- LocoBrakeCylinderPressurePSI: 35.0 // [IMPLEMENTADO] - Presión en cilindro de loco (PSI)
- TrainBrakeCylinderPressurePSI: 30.0 // [IMPLEMENTADO] - Presión en cilindro de tren (PSI)
- BrakePipePressureTailEnd: 48.0 // [PENDIENTE] - Presión en extremo de cola (no siempre reportado)
- Regulator: 0.5 // [IMPLEMENTADO] - Posición del acelerador (0..1)
- Reverser: 1 // [IMPLEMENTADO] - Posición del reverser
- VirtualBrake: 0.0 // [IMPLEMENTADO] - Posición del freno virtual
- DynamicBrake: 0.2 // [IMPLEMENTADO] - Freno dinámico (si está disponible)
- SignalAspect: 2 // [IMPLEMENTADO] - Señal principal (0=RED,1=YELLOW,2=GREEN)
- KVB_SignalAspect: -1 // [PENDIENTE] - Sistema avanzado de señales (varía por mod)

## Notas de implementación
- Las variables marcadas como `[IMPLEMENTADO]` están disponibles en `tsc_integration.py` en `self.mapeo_controles`.
- Para variables que no siempre están presentes (p. ej. `BrakePipePressureTailEnd`), se recomienda validar su presencia antes de usarlas en la IA.

## Ejemplo de uso
- Para capturar telemetría de prueba en local:
  - `python debug_tsc.py --output sample_getdata.txt` (genera una salida de ejemplo)
  - `python debug_fetch.py --read sample_getdata.txt --format json`

## Checklist para completar
- [x] Crear documentación inicial basada en la plantilla
- [ ] Añadir ejemplos JSON reales
- [ ] Marcar variables adicionales detectadas por mods terceros
- [ ] Añadir tests que validen el mapeo y la presencia de campos críticos

